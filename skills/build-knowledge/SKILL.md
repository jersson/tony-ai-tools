---
name: build-knowledge
description: Full document pipeline that builds a vectorized second brain — converts raw sources (pdf, docx, xlsx, pptx, html, URLs) to markdown, quality-gates them, generates an Obsidian-compatible wiki with TF-IDF + vector indexes, and synthesizes a cited knowledge base (.tony/knowledge-base.md) used to support or push back on ideas.
---

# Build Knowledge Skill

When this skill is loaded, you run tony's **knowledge pipeline**: raw documents in, a searchable second brain out. The pipeline produces two artifacts downstream skills rely on:

- `.tony/` — converted documents, wiki, and retrieval indexes (TF-IDF + vector)
- `.tony/knowledge-base.md` — the curated claims layer (citations + conflicts) used to support or challenge ideas

> **Command syntax:** examples below use `/tony <name>`. OpenCode runs them as written; Claude Code namespaces them with a colon (`/tony:create-epic`). Quote whichever form matches the developer's environment.

## Pre-condition

### 1. Load Global Guidelines

Read `../globals/INDEX.md` and load every principle file it lists into session context. Nothing else in this skill runs until that is done.

### 2. Locate the tools

The Python tools are vendored in the tony package under `tools/` — two directory levels up from this SKILL.md file (`<package_root>/tools/`). Resolve that path once and reuse it for every command below.

Check whether Python 3.10+ is available (`python3 --version`). If `python3` is missing or older than 3.10 (e.g. macOS system Python 3.9), look for a newer interpreter (`python3.13`, `python3.12`, Homebrew python) and use it for every tool call below. If none exists, tell the developer to install Python 3.10+ and **stop** — the pipeline cannot run without it (markitdown requires ≥3.10; the other tools need ≥3.9).

## Workflow

### 1. Determine intent

If the developer wants to **use** an existing knowledge base to shape an idea, do not proceed here. Redirect to `/tony create-epic` or `/tony create-user-story` and stop.

If they want to **load documents** into the baseline, proceed.

### 2. Gather sources

Resolve sources in this order:

1. If `<project_root>/.tony/raw-documents/` exists and has files → use it.
2. Otherwise accept file paths, folder paths, or URLs given by the developer; copy/move loose files into `.tony/raw-documents/` first.
3. If nothing is available, create `.tony/raw-documents/` if missing and stop until answered.

**First-time announcement:** whenever you create `.tony/raw-documents/`, say so explicitly: *"Created `.tony/raw-documents/` — that is tony's canonical drop point. Put source documents there and re-run `/tony build-knowledge`."*

Supported inputs: `.pdf`, `.doc`, `.docx`, `.xls`, `.xlsx`, `.pptx`, `.txt`, `.html`, `.htm`, and HTTP/HTTPS URLs.

### 3. Convert to markdown

```bash
python3 <package_root>/tools/convert.py <sources> <project_root>/.tony/md-documents/ --incremental
```

The tool prints JSON: `success_rate`, `files[]`, `total`, `success`, `failed`. It writes YAML frontmatter (source, format, checksum) into each converted file and maintains `manifest.json`.

**Dependency check:** if markitdown is missing, the tool exits with an install hint. Offer to run `pip install -r <package_root>/tools/requirements.txt` — never install without approval.

### 4. Quality gate (load)

```bash
python3 <package_root>/tools/quality_gate.py load <project_root>/.tony/md-documents/
```

| Result | Action |
|--------|--------|
| `passed: true` | Continue |
| `passed: false` | Report each entry from `issues[]`, fix what's fixable (re-export, replace file), re-run. Do not continue past a failing gate |

### 5. Build the wiki

Read the converted markdown files in `.tony/md-documents/` and generate an Obsidian-compatible wiki in `.tony/wiki/` following `./guidelines/wiki-format.md`:

1. Extract entities per document — people, projects, dates, themes, key concepts.
2. Cluster documents into a natural topic hierarchy.
3. Cross-link pages with `[[wiki-links]]` where entities/topics recur.
4. Write `index.md` (Map of Content) plus one page per category, each with YAML frontmatter (`tags`, `aliases`, `source`) and source citations.

Then gate it:

```bash
python3 <package_root>/tools/quality_gate.py build <project_root>/.tony/
```

Stop on failure the same way as step 4.

### 6. Build retrieval indexes

```bash
python3 <package_root>/tools/index.py build <project_root>/.tony/wiki/ <project_root>/.tony/index/
python3 <package_root>/tools/vector_index.py build <project_root>/.tony/wiki/ <project_root>/.tony/index/kb.db
```

- TF-IDF builds fast and needs no model download — it always works.
- The vector index needs `fastembed` + `sqlite-vec`; on first build it downloads the embedding model. If either dependency is missing, report it, keep the TF-IDF index, and continue — semantic search degrades gracefully.
- On later runs use `update` instead of `build` for incremental refresh.

### 7. Synthesize the knowledge base

Distill the wiki into `<project_root>/.tony/knowledge-base.md` following `./guidelines/template.md`. This curated layer is what `/tony create-epic` and `/tony create-user-story` read:

- One-line claims per category, each citing `<source-file>:<line>` inside `.tony/md-documents/`.
- A **Conflicts** section listing contradictions between sources (or against existing epics/stories) with both citations.
- Merge on reload: replace claims citing re-converted sources, keep the rest.

### 8. Report

Structure your response following the loaded operating principles:

**Status:** ✅ Loaded / ⚠️ Loaded with conflicts / ❌ Pipeline failed

**Pipeline:** conversions (n success / n failed), wiki pages written, indexes built (TF-IDF ✅ / vector ✅ or ⚠️).

**Knowledge base:** claims extracted per category (count), conflicts found.

Then proactively ask: *"Baseline ready. Do you want to shape an idea against it? Use `/tony create-epic` or `/tony create-user-story`."*

Apply the loaded operating principles to every step of this workflow.
