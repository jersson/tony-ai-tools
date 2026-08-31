# Tony Knowledge Tools

Python tools that power the `build-knowledge` skill: they convert raw documents to
markdown, gate quality, and build retrieval indexes (TF-IDF + vector) over the
generated wiki.

There are two kinds of tools here:

- **Pipeline (product) tools** — `convert.py`, `quality_gate.py`, `index.py`, `vector_index.py`.
  Run on the project's data (`.tony/…`) as part of `/tony build-knowledge`; the PO's
  documents pass through them at runtime.
- **QA harness** — `check_consistency.py`. Run by the maintainer or in CI; it verifies the
  pipeline tools behave as documented (exit codes, arg parsing, query integrity,
  gate behavior, doc↔code contracts). It runs against this repo, not against project
  data, and is not part of the pipeline. Mechanical checks only — the semantic
  narrative audit is an LLM pass and follows `CONSISTENCY.md` in this directory.

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
(`sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`, 384-dim embeddings, ~120MB, cached locally).

## Commands

### Pipeline (product) tools

```bash
# Convert raw sources (dir, file, or URL) into markdown
# Exits 1 when a batch's success rate drops below 75%
python3 tools/convert.py <input> <output_dir> [--incremental]

# Quality gate: validates converted docs (load) and wiki pages (build)
# Rejects invalid files; exit 1 when success rate drops below threshold (default 75)
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

### QA harness (maintainer / CI, not part of the pipeline)

```bash
# Verifies the pipeline tools and the docs stay consistent (stdlib only — no deps)
python3 tools/check_consistency.py   # mechanical checks only

# Semantic/narrative audit — an LLM pass following the rules in CONSISTENCY.md
# Run both: mechanical first (exit 0), then the semantic sweep per CONSISTENCY.md
```

Pipeline tools print JSON on stdout; errors go to stderr with a non-zero exit code. `check_consistency.py` prints a human-readable PASS/FAIL report and exits 0 only when every check passes. Because it validates the tools themselves, it is safe to reach into their internals at any time — it does not touch `.tony/` data.

The `load` gate rejects converted files that lack the frontmatter keys `convert.py` writes (`source_file`, `original_format`, `date_loaded`, `checksum`); the `build` gate enforces `tags` and `source` on wiki pages.

## Layout produced by the pipeline

```
<project_root>/
└── .tony/
    ├── raw-documents/         # the PO drops source files here
    ├── md-documents/          # converted .md + manifest.json
    ├── wiki/                  # Obsidian-compatible wiki (MOC + category pages)
    └── index/                 # TF-IDF store + kb.db (vector store)
```

Vendored and adapted from xavier-toolkit's tooling.
