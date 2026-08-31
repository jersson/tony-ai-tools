# AGENTS.md

Guidance for AI coding agents working in this repo.

## Consistency audits

When asked to run a consistency check (or to fix inconsistencies), follow this order:

1. Run `tools/check_consistency.py` — mechanical checks; must exit 0 before anything else.
2. Follow `tools/CONSISTENCY.md` — the semantic LLM audit catalog. Sweep all skills/docs
   against its rules, fix every instance, sweep the sibling skills for the same defect.
3. When you discover a NEW inconsistency pattern, add a rule to `tools/CONSISTENCY.md`
   so it does not recur, then re-run the mechanical checks.

## Conventions

- Skills under `skills/` are shipped operating constraints for the LLM, not aspirational docs.
- Package version lives in `package.json` and `.claude-plugin/plugin.json` and must stay in
  sync with any version-pinned README install command. `.claude-plugin/marketplace.json` is a
  catalog entry, not a version source — keep its plugin `name` aligned with `plugin.json`.
- Product nouns are "epic", "user story", "story", "knowledge base"; the consumer is the "PO".
- After any approved modification, update the documentation that names what changed (tools,
  paths, versions, commands, sections, constants) in the SAME change. A stale doc is the same
  defect as broken code.