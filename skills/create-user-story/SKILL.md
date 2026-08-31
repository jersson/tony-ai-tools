---
name: create-user-story
persona: po
description: Understand an idea (or an existing epic) and draft user stories that pass INVEST + 3C validation, grounded in the loaded project knowledge base. Each story is self-checked against the checklist and correctness criteria before being written to docs/user-stories/<epic-name>/.
---

# Create User Story Skill

When this skill is loaded, you help the PO turn an idea (or an epic) into **user stories**. Every generated story must pass the INVEST + 3C validation rules before it is written to disk — a story that would fail `/tony` review does not leave this skill.

> **Command syntax:** examples below use `/tony <name>`. OpenCode runs them as written; Claude Code namespaces them with a colon (`/tony:create-epic`). Quote whichever form matches the PO's environment.

## Pre-condition

### 1. Load Global Guidelines

Read `../globals/INDEX.md` and load every principle file it lists into session context. Nothing else in this skill runs until that is done.

### 2. Load the PO personality

Apply the PO personality following `../globals/personality.md`:

- If `<project_root>/.tony/personality.json` exists → load and **validate it against the strict schema** (allowed keys: `archetype`, `tone`, `working_rule`, `updated_at`). If it has an unmapped key, a missing required field, or an invalid archetype, **throw a processing error** naming the problem and stop — never proceed with an unparseable config.
- If it is missing → run the capture flow (one compact pass), save to `<project_root>/.tony/personality.json`, then continue.

### 3. Verify the evidence dependency (hard gate)

`build-knowledge` is a hard prerequisite — this skill cannot produce grounded stories without it.

- If `<project_root>/.tony/knowledge-base.md` exists → proceed.
- If it is missing → do not run this skill, and do not offer any way to continue without the baseline. There is no "no-baseline" path — never propose to register the idea as unverified, proceed anyway, or mark every claim unverified. Tell the PO: *"Shaping requires a knowledge base. Run `/tony build-knowledge` first — drop source documents in `.tony/raw-documents/`."* Stop.

## Workflow

### 1. Determine intent

If the PO wants to shape a broad idea into epics first, do not proceed here. Tell them to use `/tony create-epic` for that and stop.

If the request is not about breaking an idea (or epic) into stories (coding, debugging, general Q&A, or anything else) it is outside tony's scope — refuse per the safety protocol and stop.

If they want user stories from an idea or an epic, proceed.

### 2. Determine the input source

| Input | Action |
|-------|--------|
| A path to an epic in `docs/epics/` | Read it fully; derive stories within its scope, honoring its out-of-scope list |
| An epic name without a path | Search `docs/epics/` for a match; if not found, ask |
| A raw idea (pasted or described) | Treat it as the idea source; check `docs/epics/` for a related epic to link against |

If neither an idea nor an epic is provided, ask for one and stop until answered.

### 3. Understand the idea

Extract during analysis:

- **Actors** — every distinct role that interacts with the capability
- **Capabilities** — the distinct things each actor needs to do
- **Benefits** — why each action matters to the actor or business
- **Flows** — happy path AND unhappy paths (errors, edge cases, empty states)
- **Data & integrations** — entities touched, external systems involved
- **Open questions** — anything undefined that affects testability

If essential context is missing, ask **one** focused clarifying question at a time.

### 4. Use the knowledge base

The gate in the pre-conditions guarantees `.tony/knowledge-base.md` exists. Read it and use it two ways:

- **Support:** ground story details in cited claims — personas for the roles, baselines and targets for acceptance-criteria thresholds (e.g., a documented "links valid 12 months" decision becomes a testable criterion). Copy citations into the story's Notes / Context. Any claim that cannot be traced to the knowledge base must be listed under the story's **Assumptions** section and labeled as an assumption — never presented as fact (checklist: every claim is cited or an assumption).
- **Push back:** when a drafted story contradicts the baseline — a constraint it violates, a metric it undermines, a conflict already recorded — flag it with both citations before writing. The PO decides whether to adjust the story or override the baseline; never silently write a story that contradicts the knowledge base.

**Deep evidence lookup (optional):** if `.tony/index/kb.db` exists and acceptance criteria need thresholds or details not in the distilled claims, run a semantic search over the full corpus:

```bash
python3 <package_root>/tools/vector_index.py search .tony/index/kb.db "<query>" 5
```

Cite what it returns; fall back to TF-IDF (`<package_root>/tools/index.py search`) when the vector index is unavailable.

### 5. Identify candidate stories

Slice the idea into **vertical slices** — each story delivers a usable outcome end-to-end, not a layer ("build the API" is not a story). Cover:

- One core happy-path story per capability
- Unhappy paths as separate stories when they carry independent value
- Never merge two actors or two capabilities into one story

If a candidate is too big for one sprint, split it further (by workflow step, by data variation, by rule). If a candidate is really an epic, say so and suggest `/tony create-epic`.

### 6. Draft each story

Write each draft following `./guidelines/template.md`:

- **Card** — `As a [role], I want [action], so that [benefit].`
- **Conversation** — notes, constraints, dependencies, open questions
- **Confirmation** — acceptance criteria that are objectively pass/fail

### 7. Self-validate every story (mandatory)

For EACH drafted story, run the full validation:

1. Read `./guidelines/checklist.md` and assess every INVEST criterion, every 3C element, and all consistency checks.
2. Read `./guidelines/correctness-check.md` and analyze logical consistency.
3. Fix what fails and re-validate. Iterate until the story passes all checks.

**Code cross-check (only if a codebase exists):** If `<project_root>/.git` exists, `grep` the source for the roles, entities, actions, and UI elements each story references. Confirm they exist or flag domain mismatches (e.g., "As an admin" when no admin module exists).

A story may only be written when its status is **consistent & doable**. If a story cannot pass after refinement, exclude it and report why.

### 8. Write the story files

Stories are grouped in one folder per epic — the epic used as the base names the folder:

| Base | Target folder |
|------|---------------|
| An epic (path or matched name) | `<project_root>/docs/user-stories/<epic-name>/` — `<epic-name>` is the epic file's kebab name (`docs/epics/referral-program.md` → `referral-program`) |
| A raw idea with a related epic found in `docs/epics/` | Same rule, using that epic's name |
| A raw idea with no related epic | `<project_root>/docs/user-stories/<idea-kebab-name>/`; note in the report that stories are grouped by idea until linked to an epic |

Write each validated story to `<target-folder>/<story-kebab-name>.md` (e.g., `docs/user-stories/referral-program/referral-share-link.md`). Create folders as needed. Never overwrite an existing file without explicit confirmation.

### 9. Persist generation result

Write the outcome to `<project_root>/.tony/.story-registry.json` so downstream skills can trace which stories were generated and their validation status.

1. Read `<project_root>/.tony/.story-registry.json`; if it is missing or unparseable, treat it as `{"stories": []}`.
2. Upsert by `path`: replace the entry with the same path, or append a new one.
3. Each entry must include:
   - `path`: the story file path relative to project root
   - `type`: `"user-story"`
   - `epic`: epic file path relative to project root, or `null`
   - `status`: `"consistent-doable"` — only validated stories are registered
   - `timestamp`: current UTC ISO 8601 timestamp (e.g., `2026-08-20T14:30:00.000Z`)
4. Save the file with the `write` tool.

### 10. Report

Structure your response following the loaded global guidelines:

**Status:** ✅ Stories created / ⚠️ Created with open questions / ❌ Could not produce valid stories

**Stories created:** table of file → narrative one-liner → status.

**Validation summary:** per story, any INVEST/3C weaknesses that were fixed during iteration.

**Baseline:** how the knowledge base grounded the stories (cited claims), and any pushback raised and its resolution — the evidence gate guarantees a loaded baseline.

**Excluded candidates:** candidates that failed validation and why (if any).

**Open questions:** unresolved items from the Conversation element.

Apply the loaded PO personality when framing stories (conversation detail, acceptance-criteria emphasis), phrasing pushback against the knowledge base, and reporting the outcome — use the archetype's fingerprint in `../globals/personality.md` (Artifact fingerprints).
Apply the loaded operating principles to every step of this workflow.
