# PRD — ondata_skills

## Idea: test battery to validate skills

**Proposed by:** Alessio Cimarelli

### Problem

Skills are instructions for LLM agents: it is hard to tell whether a change actually improves them or just alters their behavior in unexpected ways. Without systematic tests, regressions — skills that fail to trigger, skip required steps, or produce wrong output — go unnoticed.

### Proposal

Build a **test battery for each skill** in the project, inspired by the eval pattern described by OpenAI, to validate effectiveness on practical cases.

This approach is especially useful for skills that deal with **data quality**: success criteria are concrete and verifiable (file produced, correct format, errors detected).

### Test structure per skill

For each skill, prepare:

1. **`evals/<skill-name>.prompts.csv`** — prompts with `id`, `should_trigger`, `prompt`.
   Covers explicit invocation, implicit invocation, contextual invocation, and negative controls.

2. **Deterministic checks** — verify commands executed, files created, output produced.

3. **Rubric-based grading** — JSON schema for qualitative evaluation (style, completeness, adherence to requirements).

### Phases

**Phase 1 — Base framework**
- Define the `evals/` structure in the project
- Write the battery for the `openalex` skill (already present) as a pilot
- Document the reusable pattern

**Phase 2 — Data quality skills**
- Develop specific data quality skills (e.g. CSV validation, metadata checks)
- Write the test battery alongside skill development

**Phase 3 — Automation**
- Integrate tests into CI or a manually runnable script
- Produce a summary report (pass/fail + score per skill)

### Reference reading

- [Testing Agent Skills Systematically with Evals](https://developers.openai.com/blog/eval-skills/) — OpenAI blog
- [testing-agent-skills-with-evals.md](testing-agent-skills-with-evals.md) — local copy of the article
- [agent-skills-specification.md](agent-skills-specification.md) — Agent Skills format specification ([online](https://agentskills.io/specification))

### Open questions

- Which agent should run the tests? Claude Code, Codex, or another?
- Should tests run in an isolated sandbox or can they make real API calls?
- For data quality: which checks are highest priority (encoding, separator, dates, etc.)?
