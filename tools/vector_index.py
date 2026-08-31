#!/usr/bin/env python3
"""
Vector retrieval index tool for tony-ai-tools.

Creates a semantic search index using SQLite + sqlite-vec + local embeddings.
Supports full rebuild and incremental update modes.

Usage:
    python vector_index.py build <wiki_dir> <db_path>     # Build vector index
    python vector_index.py search <db_path> <query> [k]   # Semantic search
    python vector_index.py update <wiki_dir> <db_path>    # Incremental update
"""

import sys
import os
import json
import sqlite3
from pathlib import Path
from datetime import datetime

try:
    import sqlite_vec
except ImportError:
    print("Error: sqlite-vec not installed. Run: pip install sqlite-vec", file=sys.stderr)
    sys.exit(1)

try:
    from fastembed import TextEmbedding
except ImportError:
    print("Error: fastembed not installed. Run: pip install fastembed", file=sys.stderr)
    sys.exit(1)

MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
EMBEDDING_DIM = 384

_embedding_model = None


def get_model():
    """Lazily load the embedding model."""
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = TextEmbedding(model_name=MODEL_NAME)
    return _embedding_model


def get_db(path: str) -> sqlite3.Connection:
    """Open a database connection with sqlite-vec loaded."""
    db = sqlite3.connect(path)
    db.enable_load_extension(True)
    sqlite_vec.load(db)
    return db


def init_schema(db: sqlite3.Connection):
    """Create tables if they don't exist."""
    db.execute("""
        CREATE TABLE IF NOT EXISTS pages (
            id INTEGER PRIMARY KEY,
            file TEXT NOT NULL,
            path TEXT NOT NULL,
            frontmatter TEXT,
            content TEXT NOT NULL,
            checksum TEXT,
            updated_at TEXT
        )
    """)
    db.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS vec_embeddings
        USING vec0(
            page_id INTEGER PRIMARY KEY,
            embedding FLOAT[%d]
        )
    """ % EMBEDDING_DIM)
    db.commit()


def extract_frontmatter(content: str) -> dict:
    """Extract YAML frontmatter from markdown content."""
    frontmatter = {}
    if content.startswith('---'):
        end_idx = content.find('---', 3)
        if end_idx != -1:
            fm_text = content[3:end_idx].strip()
            for line in fm_text.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    frontmatter[key.strip()] = value.strip()
    return frontmatter


def extract_text_content(content: str) -> str:
    """Extract text content without frontmatter."""
    if '---' in content:
        parts = content.split('---')
        if len(parts) >= 3:
            return '---'.join(parts[2:])
    return content


def calculate_checksum(file_path: str) -> str:
    """Calculate MD5 checksum of a file."""
    import hashlib
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return f"md5:{hash_md5.hexdigest()}"


def embed_texts(texts: list) -> list:
    """Embed a list of texts, returning list of float lists."""
    model = get_model()
    # fastembed returns generator of numpy arrays
    embeddings = list(model.embed(texts))
    return [e.tolist() for e in embeddings]


def vector_to_blob(vector: list) -> bytes:
    """Convert float list to compact little-endian float32 bytes."""
    import struct
    return struct.pack(f'<{len(vector)}f', *vector)


def blob_to_vector(blob: bytes) -> list:
    """Convert float32 bytes back to float list."""
    import struct
    n = len(blob) // 4
    return list(struct.unpack(f'<{n}f', blob))


def build_index(wiki_dir: str, db_path: str) -> dict:
    """
    Build a vector index from wiki pages.
    
    Returns:
        dict with index build results
    """
    wiki_path = Path(wiki_dir)
    
    if not wiki_path.exists():
        return {'error': f'Wiki directory not found: {wiki_dir}'}
    
    wiki_files = sorted(wiki_path.glob('*.md'))
    
    if not wiki_files:
        return {'error': 'No wiki pages found'}
    
    # Read all pages
    pages = []
    for wiki_file in wiki_files:
        content = wiki_file.read_text(encoding='utf-8')
        pages.append({
            'file': wiki_file.name,
            'path': str(wiki_file),
            'frontmatter': extract_frontmatter(content),
            'content': extract_text_content(content),
            'checksum': calculate_checksum(str(wiki_file)),
            'updated_at': datetime.now().isoformat(),
        })
    
    # Embed in batches
    batch_size = 16
    all_embeddings = []
    
    for i in range(0, len(pages), batch_size):
        batch = pages[i:i + batch_size]
        # Use title + content for better embeddings (multilingual-e5 needs 'query:'/'passage:' prefix)
        texts = [f"passage: {p['file']}\n{p['content'][:2000]}" for p in batch]
        embeddings = embed_texts(texts)
        all_embeddings.extend(embeddings)
    
    # Write to SQLite
    db = get_db(db_path)
    init_schema(db)
    
    # Clear existing data
    db.execute("DELETE FROM vec_embeddings")
    db.execute("DELETE FROM pages")
    
    for page, embedding in zip(pages, all_embeddings):
        cursor = db.execute(
            "INSERT INTO pages (file, path, frontmatter, content, checksum, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
            (page['file'], page['path'], json.dumps(page['frontmatter'], ensure_ascii=False),
             page['content'], page['checksum'], page['updated_at'])
        )
        page_id = cursor.lastrowid
        db.execute(
            "INSERT INTO vec_embeddings (page_id, embedding) VALUES (?, ?)",
            (page_id, vector_to_blob(embedding))
        )
    
    db.commit()
    db.close()
    
    return {
        'status': 'success',
        'mode': 'full',
        'num_documents': len(pages),
        'model': MODEL_NAME,
        'dimensions': EMBEDDING_DIM,
        'db_path': db_path,
    }


def search_index(db_path: str, query: str, top_k: int = 5) -> list:
    """
    Search the vector index with a query.
    
    Returns:
        list of matching documents with scores
    """
    if not Path(db_path).exists():
        return [{'error': f'Index not found: {db_path}'}]
    
    db = get_db(db_path)
    
    # Check if tables exist
    tables = [r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type IN ('table','virtual')").fetchall()]
    if 'pages' not in tables or 'vec_embeddings' not in tables:
        db.close()
        return [{'error': 'Index is empty. Run build first.'}]
    
    # Embed query (multilingual-e5 needs 'query:' prefix)
    query_text = f"query: {query}"
    embeddings = embed_texts([query_text])
    query_embedding = embeddings[0]
    
    # Search
    blob = vector_to_blob(query_embedding)
    rows = db.execute(
        """
        SELECT page_id, distance
        FROM vec_embeddings
        WHERE embedding MATCH ?
        ORDER BY distance
        LIMIT ?
        """,
        (blob, top_k)
    ).fetchall()
    
    results = []
    for page_id, distance in rows:
        page = db.execute(
            "SELECT file, path, frontmatter FROM pages WHERE id = ?",
            (page_id,)
        ).fetchone()
        if page:
            results.append({
                'file': page[0],
                'path': page[1],
                'frontmatter': json.loads(page[2]) if page[2] else {},
                'score': float(1.0 / (1.0 + distance)) if distance is not None else 0.0,
                'distance': float(distance) if distance is not None else 0.0,
            })
    
    db.close()
    return results


def update_index(wiki_dir: str, db_path: str) -> dict:
    """
    Update the index with new/changed wiki pages (incremental).
    
    Returns:
        dict with update results
    """
    wiki_path = Path(wiki_dir)
    
    if not wiki_path.exists():
        return {'error': f'Wiki directory not found: {wiki_dir}'}
    
    db = get_db(db_path)
    init_schema(db)
    
    # Get existing checksums
    existing = {}
    for row in db.execute("SELECT file, checksum FROM pages").fetchall():
        existing[row[0]] = row[1]
    
    wiki_files = sorted(wiki_path.glob('*.md'))
    changed = []
    
    for wiki_file in wiki_files:
        checksum = calculate_checksum(str(wiki_file))
        if wiki_file.name not in existing or existing[wiki_file.name] != checksum:
            changed.append(wiki_file)
    
    if not changed:
        db.close()
        return {
            'status': 'up_to_date',
            'mode': 'incremental',
            'num_documents': len(existing),
            'changed': 0,
        }
    
    # Process changed files
    pages = []
    for wiki_file in changed:
        content = wiki_file.read_text(encoding='utf-8')
        pages.append({
            'file': wiki_file.name,
            'path': str(wiki_file),
            'frontmatter': extract_frontmatter(content),
            'content': extract_text_content(content),
            'checksum': calculate_checksum(str(wiki_file)),
            'updated_at': datetime.now().isoformat(),
        })
    
    texts = [f"passage: {p['file']}\n{p['content'][:2000]}" for p in pages]
    embeddings = embed_texts(texts)
    
    for page, embedding in zip(pages, embeddings):
        # Check if page exists
        row = db.execute("SELECT id FROM pages WHERE file = ?", (page['file'],)).fetchone()
        
        if row:
            # Update existing
            page_id = row[0]
            db.execute(
                "UPDATE pages SET path = ?, frontmatter = ?, content = ?, checksum = ?, updated_at = ? WHERE id = ?",
                (page['path'], json.dumps(page['frontmatter'], ensure_ascii=False),
                 page['content'], page['checksum'], page['updated_at'], page_id)
            )
            db.execute(
                "UPDATE vec_embeddings SET embedding = ? WHERE page_id = ?",
                (vector_to_blob(embedding), page_id)
            )
        else:
            # Insert new
            cursor = db.execute(
                "INSERT INTO pages (file, path, frontmatter, content, checksum, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                (page['file'], page['path'], json.dumps(page['frontmatter'], ensure_ascii=False),
                 page['content'], page['checksum'], page['updated_at'])
            )
            page_id = cursor.lastrowid
            db.execute(
                "INSERT INTO vec_embeddings (page_id, embedding) VALUES (?, ?)",
                (page_id, vector_to_blob(embedding))
            )
    
    db.commit()
    
    # Count total
    total = db.execute("SELECT COUNT(*) FROM pages").fetchone()[0]
    db.close()
    
    return {
        'status': 'success',
        'mode': 'incremental',
        'num_documents': total,
        'changed': len(changed),
    }


def main():
    if len(sys.argv) < 3:
        print("Usage: python vector_index.py <command> <args>")
        print("Commands:")
        print("  build <wiki_dir> <db_path>   - Build vector index")
        print("  search <db_path> <query> [k] - Semantic search")
        print("  update <wiki_dir> <db_path>  - Incremental update")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'build':
        if len(sys.argv) < 4:
            print("Usage: python vector_index.py build <wiki_dir> <db_path>", file=sys.stderr)
            sys.exit(1)
        result = build_index(sys.argv[2], sys.argv[3])
        print(json.dumps(result, indent=2))
        if 'error' in result:
            sys.exit(1)
    
    elif command == 'search':
        if len(sys.argv) < 4:
            print("Usage: python vector_index.py search <db_path> <query> [k]", file=sys.stderr)
            sys.exit(1)
        top_k = int(sys.argv[4]) if len(sys.argv) > 4 else 5
        query = ' '.join(sys.argv[3:4]) if len(sys.argv) > 4 else ' '.join(sys.argv[3:])
        results = search_index(sys.argv[2], query, top_k)
        if len(results) == 1 and 'error' in results[0]:
            print(json.dumps(results, indent=2), file=sys.stderr)
            sys.exit(1)
        print(json.dumps(results, indent=2))    
    elif command == 'update':
        if len(sys.argv) < 4:
            print("Usage: python vector_index.py update <wiki_dir> <db_path>", file=sys.stderr)
            sys.exit(1)
        result = update_index(sys.argv[2], sys.argv[3])
        print(json.dumps(result, indent=2))
        if 'error' in result:
            sys.exit(1)
    
    else:
        print(f"Error: Unknown command '{command}'", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
