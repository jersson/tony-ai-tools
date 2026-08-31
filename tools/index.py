#!/usr/bin/env python3
"""
Retrieval index tool for tony-ai-tools.

Creates a searchable index from wiki pages for semantic search.
Supports full rebuild and incremental update modes.

Usage:
    python index.py build <wiki_dir> <index_dir>      # Build index
    python index.py search <index_dir> <query> [k]  # Search index
    python index.py update <wiki_dir> <index_dir>     # Update index
"""

import sys
import os
import json
import re
from pathlib import Path
from datetime import datetime
from collections import Counter
import numpy as np


def tokenize(text: str) -> list:
    """Simple tokenization for English and Spanish text."""
    # Convert to lowercase
    text = text.lower()
    
    # Remove punctuation
    text = re.sub(r'[^\w\s]', ' ', text)
    
    # Split into words
    tokens = text.split()
    
    # Remove stopwords (English + Spanish)
    stopwords = {
        'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'any',
        'can', 'had', 'her', 'was', 'one', 'our', 'out', 'day', 'get',
        'has', 'him', 'his', 'how', 'its', 'new', 'now', 'old', 'see',
        'two', 'way', 'who', 'did', 'yes', 'this', 'that', 'with', 'from',
        'they', 'have', 'will', 'been', 'were', 'when', 'what', 'your',
        'which', 'their', 'there', 'would', 'about', 'into', 'than',
        'them', 'then', 'these', 'those', 'upon', 'also', 'such', 'each',
        'de', 'la', 'el', 'en', 'y', 'a', 'los', 'del', 'las', 'un', 'por',
        'con', 'no', 'una', 'su', 'para', 'es', 'al', 'lo', 'como', 'más',
        'pero', 'sus', 'le', 'ya', 'o', 'este', 'sí', 'porque', 'esta',
        'entre', 'cuando', 'muy', 'sin', 'sobre', 'también', 'me', 'hasta',
        'hay', 'donde', 'quien', 'desde', 'todo', 'nos', 'durante', 'todos',
        'uno', 'les', 'ni', 'contra', 'otros', 'ese', 'eso', 'ante', 'ellos',
        'e', 'esto', 'mí', 'antes', 'algunos', 'qué', 'unos', 'yo', 'otro',
        'otras', 'otra', 'él', 'tanto', 'esa', 'estos', 'mucho', 'quienes',
        'nada', 'muchos', 'cual', 'poco', 'ella', 'estar', 'estas', 'algunas',
        'algo', 'nosotros', 'mi', 'mis', 'tú', 'te', 'ti', 'tu', 'tus',
        'ellas', 'nosotras', 'vosotros', 'vosotras', 'os', 'mío', 'mía',
        'míos', 'mías', 'tuyo', 'tuya', 'tuyos', 'tuyas', 'suyo', 'suya',
        'suyos', 'suyas', 'nuestro', 'nuestra', 'nuestros', 'nuestras',
        'vuestro', 'vuestra', 'vuestros', 'vuestras', 'esos', 'esas',
        'estoy', 'estás', 'está', 'estamos', 'estáis', 'están', 'esté',
        'estés', 'estemos', 'estéis', 'estén', 'estaré', 'estarás', 'estará',
        'estaremos', 'estaréis', 'estarán', 'estaría', 'estarías', 'estaríamos',
        'estaríais', 'estarían', 'estaba', 'estabas', 'estábamos', 'estabais',
        'estaban', 'estuve', 'estuviste', 'estuvo', 'estuvimos', 'estuvisteis',
        'estuvieron', 'estuviera', 'estuvieras', 'estuviéramos', 'estuvierais',
        'estuvieran', 'estuviese', 'estuvieses', 'estuviésemos', 'estuvieseis',
        'estuviesen', 'estando', 'estado', 'estada', 'estados', 'estadas',
        'estado', 'estada', 'estados', 'estadas', 'he', 'has', 'ha', 'hemos',
        'habéis', 'han', 'haya', 'hayas', 'hayamos', 'hayáis', 'hayan',
        'habré', 'habrás', 'habrá', 'habremos', 'habréis', 'habrán',
        'habría', 'habrías', 'habríamos', 'habríais', 'habrían', 'había',
        'habías', 'habíamos', 'habíais', 'habían', 'hube', 'hubiste', 'hubo',
        'hubimos', 'hubisteis', 'hubieron', 'hubiera', 'hubieras', 'hubiéramos',
        'hubierais', 'hubieran', 'hubiese', 'hubieses', 'hubiésemos', 'hubieseis',
        'hubiesen', 'habiendo', 'habido', 'habida', 'habidos', 'habidas',
        'soy', 'eres', 'es', 'somos', 'sois', 'son', 'sea', 'seas', 'seamos',
        'seáis', 'sean', 'seré', 'serás', 'será', 'seremos', 'seréis', 'serán',
        'sería', 'serías', 'seríamos', 'seríais', 'serían', 'era', 'eras',
        'éramos', 'erais', 'eran', 'fui', 'fuiste', 'fue', 'fuimos', 'fuisteis',
        'fueron', 'fuera', 'fueras', 'fuéramos', 'fuerais', 'fueran', 'fuese',
        'fueses', 'fuésemos', 'fueseis', 'fuesen', 'siendo', 'sido',
        'tengo', 'tienes', 'tiene', 'tenemos', 'tenéis', 'tienen', 'tenga',
        'tengas', 'tengamos', 'tengáis', 'tengan', 'tendré', 'tendrás',
        'tendrá', 'tendremos', 'tendréis', 'tendrán', 'tendría', 'tendrías',
        'tendríamos', 'tendríais', 'tendrían', 'tenía', 'tenías', 'teníamos',
        'teníais', 'tenían', 'tuve', 'tuviste', 'tuvo', 'tuvimos', 'tuvisteis',
        'tuvieron', 'tuviera', 'tuvieras', 'tuviéramos', 'tuvierais', 'tuvieran',
        'tuviese', 'tuvieses', 'tuviésemos', 'tuvieseis', 'tuviesen', 'teniendo',
        'tenido', 'tenida', 'tenidos', 'tenidas', 'tened'
    }
    
    return [token for token in tokens if token not in stopwords and len(token) > 2]


def compute_tf(tokens: list) -> dict:
    """Compute term frequency."""
    tf = Counter(tokens)
    total = len(tokens)
    return {term: count / total for term, count in tf.items()}


def compute_idf(documents: list) -> dict:
    """Compute inverse document frequency."""
    num_docs = len(documents)
    idf = {}
    
    # Collect all terms
    all_terms = set()
    for doc in documents:
        all_terms.update(set(doc))
    
    # Compute IDF for each term
    for term in all_terms:
        doc_count = sum(1 for doc in documents if term in doc)
        idf[term] = np.log((num_docs + 1) / (doc_count + 1)) + 1
    
    return idf


def build_index(wiki_dir: str, index_dir: str) -> dict:
    """
    Build a TF-IDF index from wiki pages.
    
    Returns:
        dict with index build results
    """
    wiki_path = Path(wiki_dir)
    index_path = Path(index_dir)
    
    # Create index directory
    index_path.mkdir(parents=True, exist_ok=True)
    
    # Find all wiki pages
    wiki_files = list(wiki_path.glob('*.md'))
    
    if not wiki_files:
        return {'error': 'No wiki pages found'}
    
    # Process each wiki page
    documents = []
    doc_info = []
    
    for wiki_file in wiki_files:
        content = wiki_file.read_text(encoding='utf-8')
        
        # Extract frontmatter
        frontmatter = {}
        if content.startswith('---'):
            end_idx = content.find('---', 3)
            if end_idx != -1:
                frontmatter_text = content[3:end_idx].strip()
                for line in frontmatter_text.split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        frontmatter[key.strip()] = value.strip()
        
        # Extract text content (without frontmatter)
        text_content = content
        if '---' in content:
            parts = content.split('---')
            if len(parts) >= 3:
                text_content = '---'.join(parts[2:])
        
        # Tokenize
        tokens = tokenize(text_content)
        
        documents.append(tokens)
        doc_info.append({
            'file': wiki_file.name,
            'path': str(wiki_file),
            'frontmatter': frontmatter,
            'token_count': len(tokens)
        })
    
    # Compute IDF
    idf = compute_idf(documents)
    
    # Build TF-IDF index
    index = {
        'created': datetime.now().isoformat(),
        'num_documents': len(documents),
        'vocab_size': len(idf),
        'idf': idf,
        'documents': []
    }
    
    for i, (tokens, info) in enumerate(zip(documents, doc_info)):
        tf = compute_tf(tokens)
        
        # Compute TF-IDF vector (sparse representation)
        tfidf = {}
        for term, tf_val in tf.items():
            if term in idf:
                tfidf[term] = tf_val * idf[term]
        
        # Sort by TF-IDF score
        sorted_tfidf = dict(sorted(tfidf.items(), key=lambda x: x[1], reverse=True)[:50])
        
        index['documents'].append({
            'id': i,
            'file': info['file'],
            'path': info['path'],
            'frontmatter': info['frontmatter'],
            'top_terms': sorted_tfidf
        })
    
    # Save index
    index_file = index_path / 'tfidf_index.json'
    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2, ensure_ascii=False)
    
    return {
        'status': 'success',
        'num_documents': len(documents),
        'vocab_size': len(idf),
        'index_file': str(index_file)
    }


def search_index(index_dir: str, query: str, top_k: int = 5) -> list:
    """
    Search the index with a query.
    
    Returns:
        list of matching documents with scores
    """
    index_path = Path(index_dir)
    index_file = index_path / 'tfidf_index.json'
    
    if not index_file.exists():
        return [{'error': 'Index not found'}]
    
    # Load index
    with open(index_file, 'r', encoding='utf-8') as f:
        index = json.load(f)
    
    # Tokenize query
    query_tokens = tokenize(query)
    
    # Compute query TF-IDF
    query_tf = compute_tf(query_tokens)
    query_tfidf = {}
    
    for term, tf_val in query_tf.items():
        if term in index['idf']:
            query_tfidf[term] = tf_val * index['idf'][term]
    
    # Compute cosine similarity with each document
    scores = []
    
    for doc in index['documents']:
        doc_tfidf = doc['top_terms']
        
        # Compute dot product
        dot_product = 0
        for term, query_score in query_tfidf.items():
            if term in doc_tfidf:
                dot_product += query_score * doc_tfidf[term]
        
        # Compute norms
        query_norm = np.sqrt(sum(score ** 2 for score in query_tfidf.values()))
        doc_norm = np.sqrt(sum(score ** 2 for score in doc_tfidf.values()))
        
        # Compute cosine similarity
        if query_norm > 0 and doc_norm > 0:
            similarity = dot_product / (query_norm * doc_norm)
        else:
            similarity = 0
        
        scores.append({
            'file': doc['file'],
            'path': doc['path'],
            'frontmatter': doc['frontmatter'],
            'score': float(similarity)
        })
    
    # Sort by score
    scores.sort(key=lambda x: x['score'], reverse=True)
    
    return scores[:top_k]


def update_index(wiki_dir: str, index_dir: str) -> dict:
    """
    Update the index with new/changed wiki pages.
    
    Returns:
        dict with update results
    """
    index_path = Path(index_dir)
    index_file = index_path / 'tfidf_index.json'
    
    # If index doesn't exist, build from scratch
    if not index_file.exists():
        return build_index(wiki_dir, index_dir)
    
    # Load existing index
    with open(index_file, 'r', encoding='utf-8') as f:
        old_index = json.load(f)
    
    # Build new index
    new_index_result = build_index(wiki_dir, index_dir)
    
    if 'error' in new_index_result:
        return new_index_result
    
    # Load new index
    with open(index_file, 'r', encoding='utf-8') as f:
        new_index = json.load(f)
    
    return {
        'status': 'updated',
        'old_num_documents': old_index['num_documents'],
        'new_num_documents': new_index['num_documents'],
        'vocab_size': new_index['vocab_size']
    }


def main():
    if len(sys.argv) < 3:
        print("Usage: python index.py <command> <args>")
        print("Commands:")
        print("  build <wiki_dir> <index_dir>  - Build index")
        print("  search <index_dir> <query> [k] - Search index")
        print("  update <wiki_dir> <index_dir> - Update index")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'build':
        if len(sys.argv) < 4:
            print("Usage: python index.py build <wiki_dir> <index_dir>", file=sys.stderr)
            sys.exit(1)
        
        wiki_dir = sys.argv[2]
        index_dir = sys.argv[3]
        
        result = build_index(wiki_dir, index_dir)
        print(json.dumps(result, indent=2))
        if 'error' in result:
            sys.exit(1)
    
    elif command == 'search':
        if len(sys.argv) < 4:
            print("Usage: python index.py search <index_dir> <query> [k]", file=sys.stderr)
            sys.exit(1)
        
        index_dir = sys.argv[2]
        top_k = int(sys.argv[4]) if len(sys.argv) > 4 else 5
        query = ' '.join(sys.argv[3:4]) if len(sys.argv) > 4 else ' '.join(sys.argv[3:])

        results = search_index(index_dir, query, top_k)
        if len(results) == 1 and 'error' in results[0]:
            print(json.dumps(results, indent=2), file=sys.stderr)
            sys.exit(1)
        print(json.dumps(results, indent=2))
    
    elif command == 'update':
        if len(sys.argv) < 4:
            print("Usage: python index.py update <wiki_dir> <index_dir>", file=sys.stderr)
            sys.exit(1)
        
        wiki_dir = sys.argv[2]
        index_dir = sys.argv[3]
        
        result = update_index(wiki_dir, index_dir)
        print(json.dumps(result, indent=2))
        if 'error' in result:
            sys.exit(1)
    
    else:
        print(f"Error: Unknown command '{command}'", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
