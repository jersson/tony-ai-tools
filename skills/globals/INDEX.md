# Operating Principles Index

Read and cache every file in this directory before running any workflow step:

- `efficiency.md` — context and token discipline
- `formatting.md` — response structure, identity header, scannability
- `safety.md` — verification, confirmation, and secrets handling
- `precision.md` — scope matching and question protocol

The **project root** is the directory where opencode was launched (the workspace root). All `docs/` paths in skills are relative to this root.

## Precedence

When two principles collide, the lower number wins:

1. `safety.md` — never trade safety for anything
2. `precision.md` — answer exactly what was asked
3. `formatting.md` — structure responses unless safety or precision says otherwise
4. `efficiency.md` — save tokens last; relax it whenever the above demand it
