# Knowledge Base Template

Output file: `<project_root>/.tony/knowledge-base.md` — the curated synthesis layer generated from the wiki (`.tony/wiki/`). This is the file `/tony create-epic` and `/tony create-user-story` read.

```markdown
# Knowledge Base

## Cache
- **Generated:** <ISO timestamp>
- **Sources:** <count> — <file1>, <file2>, …
- **Wiki:** .tony/wiki/index.md
- **Indexes:** TF-IDF <available|unavailable> · Vector <available|unavailable>

## Summary
- <3-5 bullet synthesis of what the baseline says overall>

## Business & Strategy
- [claim] -> .tony/md-documents/<file>.md:<line>

## Users & Research
- [claim] -> .tony/md-documents/<file>.md:<line>

## Metrics & Baselines
- [claim] -> .tony/md-documents/<file>.md:<line>

## Constraints & Decisions
- [claim] -> .tony/md-documents/<file>.md:<line>

## Risks & Open Items
- [claim] -> .tony/md-documents/<file>.md:<line>

## Conflicts
- [claim A] (<source-a>) contradicts [claim B] (<source-b>)
```

## Rules

- Every claim carries a citation — a claim without `path:line` does not get written.
- Keep claims short (one line each); the wiki and converted documents hold the detail.
- An empty category is omitted, not filled with filler.
- Merging replaces only claims citing re-converted sources; everything else is kept.
- When a claim cannot be distilled from the wiki, leave it out — never invent facts.
