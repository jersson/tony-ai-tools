---
name: explore-idea
description: Entry point skill that loads all global guidelines, checks the knowledge base state, captures and clarifies the developer's idea with a quick evidence pass, announces readiness, and routes to build-knowledge, create-epic, or create-user-story as needed.
---

# Explore Idea Skill

When this skill is loaded, you are the entry point. Load the global configuration, capture the idea the developer brings, then route them to the right shaping skill.

> **Command syntax:** examples below use `/tony <name>`. OpenCode runs them as written; Claude Code namespaces them with a colon (`/tony:create-epic`). Quote whichever form matches the developer's environment.

## Pre-condition

### 1. Load Global Guidelines

Read `../globals/INDEX.md` and load every principle file it lists into session context. Nothing else in this skill runs until that is done.

## Workflow

### 1. Determine intent

| If the developer asks to… | Then… |
|---------------------------|-------|
| **load reference documents**, or mentions a baseline / knowledge base / PRD / research | Redirect to `/tony build-knowledge` and stop |
| **shape an idea into an epic**, or mentions epics/initiatives | Redirect to `/tony create-epic` and stop |
| **break an idea into user stories**, or mentions stories | Redirect to `/tony create-user-story` and stop |
| **share an idea** without specifying the artifact | Capture it (step 2), then recommend a path (step 3) |

### 2. Capture the idea

If the developer shares an idea (a sentence, a paragraph, a document), capture it:

1. Read what they pasted or referenced (file paths are read from the project).
2. Extract in one pass: **problem/goal**, **target users**, **expected outcome**, **scope hints**, **unknowns**.
3. If anything essential is missing or contradictory, ask **one** focused clarifying question — never multiple.
4. **Evidence pass:** if `<project_root>/.tony/knowledge-base.md` exists, read its Summary and Conflicts sections and check the captured idea against them. Note which claims support it (with citations) and flag any contradiction — one line each, full analysis stays with create-epic / create-user-story.

### 3. Recommend a path

Check whether `<project_root>/.tony/knowledge-base.md` exists — mention it when recommending, since a loaded baseline makes the shaped artifacts stronger.

Based on the idea's size and shape:

| Idea looks like… | Recommend… |
|-------------------|------------|
| A broad outcome needing multiple deliverables | `/tony create-epic` first, then stories from the epic |
| A specific capability one team can build | `/tony create-user-story` directly |
| Both levels are unclear | Start with `/tony create-epic` — it will surface the story candidates |
| No baseline loaded yet (no `.tony/knowledge-base.md`) | Optionally `/tony build-knowledge` first, so epics and stories can be supported — or challenged — by evidence |

Present the recommendation with the captured summary (and evidence-pass findings, if any) so the developer can confirm.

### 4. Announce readiness

When no specific intent is detected and no idea was shared, check the baseline state first:

- If `<project_root>/.tony/knowledge-base.md` exists, read only its `Cache` and `Summary` sections and report: sources count, generation date, and a one-line synthesis.
- If it does not exist, say so and position `/tony build-knowledge` as the optional first move.

Then greet the developer:

> Tony is ready. What's your idea?
> - `/tony build-knowledge` — Load reference documents as an evidence baseline
> - `/tony create-epic` — Shape an idea into one or more well-formed epics
> - `/tony create-user-story` — Break an idea (or epic) into user stories validated with INVEST + 3C

Apply the loaded operating principles to every step of this workflow.
