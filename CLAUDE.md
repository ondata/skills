# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

A curated collection of AI skills maintained by the [onData](https://www.ondata.it/) association. Skills are tool-agnostic instructions for AI agents, following the [Agent Skills](https://agentskills.io) open standard.

All content must be in **English** — skills, docs, comments, commit messages, and `LOG.md` entries.

## Skill structure

Each skill lives in `skills/<skill-name>/` and must contain:

- `SKILL.md` — required. YAML frontmatter (`name`, `description`) followed by Markdown instructions.
- `scripts/` — optional. Executable scripts (Bash, Python).
- `references/` — optional. Supporting documentation loaded on demand.
- `assets/` — optional. Static resources.

`name` in frontmatter must match the folder name exactly (kebab-case, lowercase, no spaces).

## Evals

Each skill has a test battery in `evals/<skill-name>/`:

- `prompts.csv` — prompt cases with `id`, `should_trigger`, `prompt`
- `checks.md` — deterministic checks to verify after each run (tick `[x]` as you go)
- `rubric.schema.json` — JSON schema for structured results
- `results/YYYY-MM-DD.json` — one file per eval run

Score = passed checks / total checks × 100. Dashboard is in `evals/README.md`.

To add evals for a new skill: copy `evals/_template/` into `evals/<skill-name>/` and fill in the three files.

## Installing a skill locally

**Do NOT install skills unless explicitly asked.**

When asked, use the `skills` CLI (from [vercel-labs/skills](https://github.com/vercel-labs/skills)):

```bash
# Install one skill for Claude Code + Codex, globally, no prompts
npx skills add ./skills/<skill-name> --agent claude-code --agent codex --global --yes

# Install all skills at once
npx skills add ./skills/ --skill '*' --agent claude-code --agent codex --global --yes
```

This copies the skill to `~/.agents/skills/<skill-name>/` (canonical) and symlinks it into `~/.claude/skills/<skill-name>/` for Claude Code.

## Key documents

- `PRD.md` — project vision and phases
- `docs/prd.md` — eval framework proposal (proposed by Alessio Cimarelli)
- `docs/agent-skills-specification.md` — Agent Skills format spec ([online](https://agentskills.io/specification))
- `docs/testing-agent-skills-with-evals.md` — eval methodology reference ([online](https://developers.openai.com/blog/eval-skills/))
- `evals/README.md` — eval dashboard and contributor guide

## Git workflow

Use **GitHub Flow**: `main` is always stable; all work happens on branches.

- Never commit directly to `main`.
- Branch naming: `add/`, `fix/`, `eval/`, `docs/` prefix + short description.
- Open a PR for every change; merge only after review.
- Delete the branch after merge: `git switch main && git branch -d <branch> && git push origin --delete <branch>`.

See `CONTRIBUTING.md` for full details.

## Bash commands in skills

When writing or generating shell commands inside skill instructions or recipes:

- Always use **single-line** `curl` commands — multi-line `\` continuation breaks argument parsing in agent environments.
- Test any new script with `bash -n <script>` to check syntax before committing.
