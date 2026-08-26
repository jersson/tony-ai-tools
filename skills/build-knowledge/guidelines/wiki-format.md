# Wiki Format

Output directory: `<project_root>/.tony/wiki/`

```
wiki/
├── index.md              → MOC (Map of Content)
├── <category-1>.md       → category page
├── <category-2>.md       → category page
└── ...
```

## Page structure

```markdown
---
tags: [<tag1>, <tag2>]
aliases: [<alternate-name>]
source: <original document filename>
---

# <Category Title>

<synthesis of what this category covers>

## Key Points
- [point] -> <source-file>:<line>

## Related
- [[other-category]]
```

## Rules

- `index.md` links to every category page — it is the entry point for humans (Obsidian) and the agent.
- Every page carries frontmatter with at least `tags` and `source`; the build quality gate rejects pages without them.
- Use `[[wiki-links]]` wherever an entity or topic appears across categories.
- Keep each page under ~200 lines; split a category rather than bloating one page.
- Citations point into the converted documents (`.tony/md-documents/<file>.md:<line>`), never into the wiki itself.
