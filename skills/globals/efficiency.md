# Context & Token Discipline

Keep sessions fast and cheap: discover before reading, read only what matters, and never repeat work.

---

## 1. Discover, then read

- Map structure with `ls` or `tree` before opening files.
- For files over 300 lines, pull only the relevant blocks (`grep`, targeted reads) — never the whole file.
- Cap terminal output at ~50 lines unless chasing a stack trace or test failure at the end of a log.

## 2. Load the minimum

- Skip anything not needed for the current step.
- Prefer one precise `grep` over a directory-wide scan.

## 3. Batch

- Fire independent reads/writes in parallel.
- Group related git operations into single commits.

## 4. Never repeat yourself

- A file already in context does not get re-read unless it changed.
- Do not rely on state left by a previous skill — carry the context forward explicitly.

## 5. Parallelize by default

- Before doing anything sequentially, check whether it can run alongside something else.

## 6. Stay brief

- Default to short answers; go long only when asked.
