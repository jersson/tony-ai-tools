---
name: explore-idea
persona: po
description: Entry point skill that loads all global guidelines, checks the knowledge base state, captures and clarifies the PO's idea with a quick evidence pass, announces readiness, and routes to build-knowledge, create-epic, or create-user-story as needed.
---

# Explore Idea Skill

When this skill is loaded, you are the entry point. Load the global configuration, capture the idea the PO brings, then route them to the right shaping skill.

> **Command syntax:** examples below use `/tony <name>`. OpenCode runs them as written; Claude Code namespaces them with a colon (`/tony:create-epic`). Quote whichever form matches the PO's environment.

## Pre-condition

### 1. Load Global Guidelines

Read `../globals/INDEX.md` and load every principle file it lists into session context. Nothing else in this skill runs until that is done.

### 2. Load the PO personality

Apply the PO personality following `../globals/personality.md`:

- If `<project_root>/.tony/personality.md` exists → load it into context. Never re-ask.
- If it is missing → run the capture flow (one compact pass), save to `<project_root>/.tony/personality.md`, then continue.
- If the PO's intent is only document-loading (`/tony build-knowledge`) and no profile exists yet → **defer the capture**; probe only once an idea is actually being shaped.

## Workflow

### 1. Determine intent

| If the PO asks to… | Then… |
|---------------------------|-------|
| **load reference documents**, or mentions a baseline / knowledge base / PRD / research | Redirect to `/tony build-knowledge` and stop |
| **shape an idea into an epic**, or mentions epics/initiatives | Redirect to `/tony create-epic` and stop |
| **break an idea into user stories**, or mentions stories | Redirect to `/tony create-user-story` and stop |
| **share an idea** without specifying the artifact | Capture it (step 2), then recommend a path (step 3) |
| anything else (not a product idea) | Say it's outside tony's scope and stop |

### 2. Capture the idea

If the PO shares an idea (a sentence, a paragraph, a document), capture it:

1. Read what they pasted or referenced (file paths are read from the project).
2. Extract in one pass: **problem/goal**, **target users**, **expected outcome**, **scope hints**, **unknowns**.
3. If anything essential is missing or contradictory, ask **one** focused clarifying question — never multiple.
4. **Evidence pass:** if `<project_root>/.tony/knowledge-base.md` exists, read its Summary and Conflicts sections and check the captured idea against them. Note which claims support it (with citations) and flag any contradiction — one line each, full analysis stays with create-epic / create-user-story.

### 3. Recommend a path

Check whether `<project_root>/.tony/knowledge-base.md` exists — it is now a hard prerequisite: `create-epic` and `create-user-story` refuse to run without it, because every artifact must be grounded in cited facts.

Based on the idea's size and shape:

| Idea looks like… | Recommend… |
|-------------------|------------|
| A broad outcome needing multiple deliverables | `/tony create-epic` first, then stories from the epic |
| A specific capability one team can build | `/tony create-user-story` directly |
| Both levels are unclear | Start with `/tony create-epic` — it will surface the story candidates |
| No baseline loaded yet (no `.tony/knowledge-base.md`) | `/tony build-knowledge` first — it is a **hard prerequisite** for shaping epics and stories |

Present the recommendation with the captured summary (and evidence-pass findings, if any) so the PO can confirm.

### 4. Announce readiness

When no specific intent is detected and no idea was shared, check the baseline state first:

- If `<project_root>/.tony/knowledge-base.md` exists, read only its `Cache` and `Summary` sections and report: sources count, generation date, and a one-line synthesis.
- If it does not exist, say so and position `/tony build-knowledge` as the required first move before any shaping work.

Then greet the PO:

> Tony is ready. What's your idea?
> - `/tony build-knowledge` — load reference documents as the evidence baseline (required before shaping)
> - `/tony create-epic` — shape an idea into one or more well-formed epics
> - `/tony create-user-story` — break an idea (or epic) into user stories validated with INVEST + 3C

Apply the loaded PO personality when capturing the idea, wording the clarifying question, and recommending a path.
Apply the loaded operating principles to every step of this workflow.
