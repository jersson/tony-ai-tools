# Tony Knowledge Tools

Python tools that power the `build-knowledge` skill: they convert raw documents to
markdown, gate quality, and build retrieval indexes (TF-IDF + vector) over the
generated wiki.

Requires **Python 3.10+** (`markitdown` does not publish wheels for older versions;
on macOS the system `python3` is often 3.9 — use Homebrew's Python instead).

## Install

```bash
pip install -r tools/requirements.txt
```

| Package | Used by | Purpose |
|---------|---------|---------|
| `markitdown[all]` | convert.py | pdf/docx/xlsx/pptx/html → markdown |
| `numpy` | index.py | TF-IDF math |
| `fastembed` | vector_index.py | local embeddings (no API keys) |
| `sqlite-vec` | vector_index.py | vector search inside SQLite |

The vector index downloads its embedding model on first build
(`sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`, ~120MB, cached locally).

## Commands

```bash
# Convert raw sources (dir, file, or URL) into markdown
python3 tools/convert.py <input> <output_dir> [--incremental]

# Quality gates (exit 1 when below threshold, default 75)
python3 tools/quality_gate.py load <md_dir> [threshold]
python3 tools/quality_gate.py build <kb_dir> [threshold]

# TF-IDF retrieval (no model download — lightweight fallback)
python3 tools/index.py build <wiki_dir> <index_dir>
python3 tools/index.py search <index_dir> "<query>" [k]

# Vector retrieval (semantic)
python3 tools/vector_index.py build <wiki_dir> <db_path>
python3 tools/vector_index.py update <wiki_dir> <db_path>
python3 tools/vector_index.py search <db_path> "<query>" [k]
```

All tools print JSON on stdout; errors go to stderr with a non-zero exit code.

## Layout produced by the pipeline

```
<project_root>/
└── .tony/
    ├── raw-documents/         # developer drops source files here
    ├── md-documents/          # converted .md + manifest.json
    ├── wiki/                  # Obsidian-compatible wiki (MOC + category pages)
    ├── index/                 # TF-IDF store + kb.db (vector store)
    └── reports/               # load-report.md, build-report.md
```

Vendored and adapted from xavier-toolkit's tooling.
