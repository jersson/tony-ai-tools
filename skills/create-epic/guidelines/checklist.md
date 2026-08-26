# Epic Quality Checklist

## Core Criteria

| Criterion | Check |
|-----------|-------|
| **V**aluable | Does it deliver a clear business or end-user outcome? |
| **C**oherent | Do all in-scope items belong to the same outcome? |
| **S**coped | Are boundaries explicit (in scope AND out of scope)? |
| **S**ized | Is it deliverable within a release/quarter and breakable into stories? |
| **O**utcome-oriented | Does it define WHAT and WHY, not HOW (no solution design)? |
| **T**estable at high level | Are success metrics defined and verifiable? |

## Consistency Checks

- [ ] The problem statement explains why this matters now
- [ ] The goal is measurable or verifiable — not a vague aspiration
- [ ] Every in-scope item maps directly to the stated goal
- [ ] Out-of-scope lists real, likely temptations (not filler)
- [ ] Target users are specific roles/personas, not "everyone"
- [ ] Assumptions are labeled as assumptions — not presented as facts
- [ ] No solution-level detail (UI specs, architecture, story-level criteria)
- [ ] Candidate stories are hints, not fully specified stories
- [ ] Minimal overlap with other epics in `docs/epics/`

## Red Flags

- ❌ Goal like "improve UX" with no verifiable signal
- ❌ In-scope items that could each be their own epic
- ❌ Solution design hiding inside the summary ("add a dropdown that…")
- ❌ Success metrics the team cannot actually measure
