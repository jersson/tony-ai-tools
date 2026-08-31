---
name: create-epic
persona: po
description: Understand an idea and shape it into one or more well-formed epics, grounded in the loaded project knowledge base. Reads a pasted idea or referenced material, analyzes problem/actors/outcome, validates against the epic checklist, and writes the epic file(s) to docs/epics/.
---

# Create Epic Skill

When this skill is loaded, you help the PO turn an idea into one or more **epics** — outcome-oriented bodies of work that will later be broken into user stories.

> **Command syntax:** tony commands are written here as `/tony <name>`. In OpenCode use them as-is (e.g., `/tony create-user-story`); in Claude Code they are namespaced with a colon (e.g., `/tony:create-user-story`). Always show the PO the syntax that matches the current environment.

## Pre-condition

### 1. Load Global Guidelines

Read `../globals/INDEX.md` and load every principle file it lists into session context. Nothing else in this skill runs until that is done.

### 2. Load the PO personality

Apply the PO personality following `../globals/personality.md`:

- If `<project_root>/.tony/personality.md` exists → load it into context. Never re-ask.
- If it is missing → run the capture flow (one compact pass), save to `<project_root>/.tony/personality.md`, then continue.

### 3. Verify the evidence dependency (hard gate)

`build-knowledge` is a hard prerequisite — this skill cannot shape a grounded epic without it.

- If `<project_root>/.tony/knowledge-base.md` exists → proceed.
- If it is missing → do not run this skill. Tell the PO: *"Shaping requires a knowledge base. Run `/tony build-knowledge` first — drop source documents in `.tony/raw-documents/`."* Stop.

## Workflow

### 1. Determine intent

If the PO already has an epic and wants to break it down, do not proceed here. Tell them to use `/tony create-user-story` for that and stop.

If the request is not about shaping an idea (coding, debugging, general Q&A, or anything else) it is outside tony's scope — refuse per the safety protocol and stop.

If they want to shape an idea into an epic (or several), proceed.

### 2. Gather the idea

Accept any of: pasted text, a spoken description, or referenced files/documents in the project. Read what is referenced.

Extract during analysis:

- **Problem / opportunity** — what pain or opportunity exists, and why now
- **Target users** — who benefits, which personas/roles
- **Desired outcome** — what changes when this succeeds (measurable if possible)
- **Scope hints** — what is clearly included, what is clearly excluded
- **Constraints & dependencies** — technical, business, regulatory
- **Unknowns** — open questions that need answers before stories are written

If the idea is too vague to extract at least problem + users + outcome, ask **one** focused clarifying question. Repeat only if the answer opens a new essential gap.

### 3. Use the knowledge base

The gate in the pre-conditions guarantees `.tony/knowledge-base.md` exists. Read it and use it two ways:

- **Support:** anchor the epic's problem, users, and goals to cited claims (e.g., a success metric that matches a documented baseline). Copy the citations into the epic's Assumptions or Success Metrics.
- **Push back:** when the idea contradicts the baseline — a constraint it ignores, a metric it conflicts with, a decision already taken — say so explicitly with both citations before writing anything. The PO decides whether to adjust the idea or override the baseline; never silently write an epic that contradicts the knowledge base.

**Deep evidence lookup (optional):** if `.tony/index/kb.db` exists and the distilled claims don't cover something, run a semantic search over the full corpus:

```bash
python3 <package_root>/tools/vector_index.py search .tony/index/kb.db "<query>" 5
```

Cite what it returns; fall back to TF-IDF (`<package_root>/tools/index.py search`) when the vector index is unavailable.

### 4. Check existing context

Look in `<project_root>/docs/epics/` (use `glob`):

- If related epics exist, read them (first 60 lines each) to avoid duplication and keep naming consistent.
- If the idea overlaps an existing epic, tell the PO and ask whether to extend that epic or create a new one.
- If the folder doesn't exist, create it when writing.

### 5. Shape the epic(s)

Decide granularity:

| If the idea… | Then… |
|--------------|-------|
| Has **one coherent outcome** | Produce **one epic** |
| Contains **multiple distinct outcomes** (e.g., different user types or product areas) | Propose **one epic per outcome** — confirm the split with the PO before writing |

For each epic, fill `./guidelines/template.md`. Keep it at the WHAT/WHY level — no solution design, no UI specs, no story-level detail. Candidate user stories are listed as hints only.

### 6. Validate against the checklist

Read `./guidelines/checklist.md` and assess the draft against every criterion. Be honest — flag weak spots and fix them before writing.

### 7. Write the epic file(s)

Write each epic to `<project_root>/docs/epics/<kebab-name>.md` (e.g., `referral-program.md`). Never overwrite an existing file without explicit confirmation.

### 8. Report

Structure your response following the loaded global guidelines:

**Status:** ✅ Created / ⚠️ Created with open questions / ❌ Needs more input

**Epics created:** file path + one-line goal each.

**Baseline:** how the knowledge base supported the epic (cited claims), and any pushback raised and its resolution — the evidence gate guarantees a loaded baseline.

**Open questions:** anything the PO should resolve before story breakdown.

Then proactively ask: *"Do you want to break this epic into user stories? Use `/tony create-user-story` with this epic."*

Apply the loaded PO personality when framing epics (success metrics, scope, story hints), phrasing pushback against the knowledge base, and reporting the outcome — use the archetype's fingerprint in `../globals/personality.md` (Artifact fingerprints).
Apply the loaded operating principles to every step of this workflow.
