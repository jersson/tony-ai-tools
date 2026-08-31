# Operating Principles Index

Read and cache every principle file listed below before running any workflow step:

- `efficiency.md` — context and token discipline
- `formatting.md` — response structure, identity header, scannability, and language match (answer in the PO's language)
- `safety.md` — verification, confirmation, and secrets handling
- `precision.md` — scope matching and question protocol

**Note:** `personality.md` (the instruction doc in this directory) is **not** a principle (it ranks below them). PO-mode skills load it on demand through their own pre-condition; utility-mode skills never load it. Do not treat it as part of the global load. The *saved projection* of the PO personality is a separate, validated config file written to `<project_root>/.tony/personality.json` (not markdown).

The **project root** is the directory where opencode was launched (the workspace root). All `docs/` paths in skills are relative to this root.

## Precedence

When two principles collide, the lower number wins:

1. `safety.md` — never trade safety for anything
2. `precision.md` — answer exactly what was asked
3. `formatting.md` — structure responses unless safety or precision says otherwise
4. `efficiency.md` — save tokens last; relax it whenever the above demand it
