# User Story Validation Checklist

Every generated story must pass all of the following before it is written to disk.

## INVEST

| Criterion | Check | Generation guidance |
|-----------|-------|---------------------|
| **I**ndependent | Can it be delivered standalone? No hard external blockers? | Slice vertically; move shared prerequisites into their own stories |
| **N**egotiable | Is there room for refinement and discussion? | Describe the outcome, not the implementation; leave UI/UX details open |
| **V**aluable | Does it deliver clear end-user or business value? | Tie the "so that" to a real user or business benefit |
| **E**stimable | Is it defined well enough to estimate effort? | Keep scope concrete; park unknowns in open questions, not inside the story |
| **S**mall | Can it fit within a single sprint? | If not, split by workflow step, data variation, or rule |
| **T**estable | Are acceptance criteria explicit and verifiable? | Every criterion must be objectively pass/fail |

## 3Cs

| Element | Check | Generation guidance |
|---------|-------|---------------------|
| **C**ard | Is the narrative written clearly? (As a… I want… so that…) | One role, one action, one benefit per card |
| **C**onversation | Are collaborators, context, and open questions documented? | Include constraints, dependencies, and unresolved points in Notes / Context |
| **C**onfirmation | Are the acceptance tests / conditions of satisfaction defined? | Cover happy path AND key unhappy paths |

## Consistency Checks

- [ ] The "who" (role) is a real user of the system
- [ ] The "what" (action) is a single, focused capability
- [ ] The "why" (benefit) justifies the effort
- [ ] All acceptance criteria are objectively pass/fail
- [ ] Every claim is either cited to the knowledge base or listed under **Assumptions** and labeled as such
- [ ] Citations in Notes / Context map to real knowledge-base entries
- [ ] Dependencies are identified and externalized

## Decision rule

| If the story is… | Then… |
|------------------|--------|
| Passing all checks | Write it to `docs/user-stories/<epic-name>/` |
| Failing 1–2 checks but fixable | Refine and re-validate before writing |
| Structurally invalid (not independent, not small, no clear value) | Exclude it; report why and suggest a split or an epic |
