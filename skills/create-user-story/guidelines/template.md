# User Story Template

```markdown
# <Story title>

As a [role],
I want [action],
so that [benefit].

## Acceptance Criteria
1. [condition 1]
2. [condition 2]
3. [condition 3]

## Notes / Context
- Epic: <epic file path or null>
- [technical constraints, dependencies, links]

## Assumptions
- <claim without a knowledge-base citation — labeled as an assumption; or "None — all claims cited">

## Open Questions
- [question blocking estimation or testability, if any]
```

## Rules

- Narrative: exactly one role, one action, one benefit.
- Acceptance criteria: Given/When/Then or plain pass/fail statements — never subjective.
- Assumptions: every claim not cited to the knowledge base appears under Assumptions, labeled as an assumption.
- File name: kebab-case of the story title (e.g., `referral-share-link.md`).
- Location: `<project_root>/docs/user-stories/<epic-name>/` — one folder per epic, named after the epic file's kebab name.

## Example

See a complete, filled-in example at `./example.md` (same folder).
