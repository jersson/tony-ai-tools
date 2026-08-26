# Safety Protocol

**Verify first** · **Announce changes** · **Ask before damage**

---

## Verify first

- **Nothing is assumed to exist** — check with `ls`/glob before touching it.
- **Cite everything:** any claim about the product, domain, or codebase carries a source: `[Claim] -> file_path:line_number`.
- **Read before write:** editing a file requires reading it first.
- **No invented facts:** never fabricate metrics, users, or market data for an epic — record them as assumptions or open questions.

## Announce changes

- **Multi-file edits:** show a `<dry_run>` block with the intended changes first.
- **Failures:** report the actual error and analysis — never invent a fix.
- **Ambiguity:** missing context or unclear intent → stop and ask.

## Ask before damage

- **Overwrites:** replacing an existing epic or story needs explicit confirmation.
- **Destructive commands:** `rm -rf`, `git reset --hard`, force push → one-time explicit confirmation.
- **Git:** no force-push to main/master, no hook skipping, no commits unless asked; no interactive git (`rebase -i`, `add -i`).
- **Secrets:** `.env`, credentials, API keys, and tokens never get committed.
- **Dependencies:** nothing new gets installed without approval.
- **External URLs:** fetch only URLs that are clearly safe and relevant.
