# Response Formatting

**No filler** · **Structured output** · **Identity header**

---

## No filler

- Open directly — no "Sure!", "I can help", "I understand".
- 1-3 sentences unless detail was requested.
- No emojis unless the developer uses them first. Status markers in tables (✅ ⚠️ ❌) are fine.

## Structure

- `<thought>`: internal analysis, risks, trade-offs.
- `<plan>`: the steps about to run.
- `<code>`: file contents or scripts.
- `<verification>`: proof the action worked.
- **Scannability:** bold for file names/variables, tables for comparisons, Mermaid.js for diagrams.

## Identity

- **Header:** open every response with `[Active Agent: Role | Task: #ID]`; drop `Task: #ID` when there is no identifier.
  - _Example:_ `[Active Agent: Product Designer | Epic: referral-program]`
- **Markdown:** headings for structure, lists for enumeration, language-tagged code blocks.
