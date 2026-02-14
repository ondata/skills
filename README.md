# onData Skills

A curated collection of AI skills maintained by [onData](https://www.ondata.it/). Skills are tool-agnostic instructions that help AI assistants handle specific tasks consistently — without re-explaining your workflows every time.

The project follows an open source model: public repo, open contributions, organic growth.

---

## Install

Skills follow the [Agent Skills](https://agentskills.io) open standard and can be installed with:

```bash
# Install all skills
npx skills add aborruso/ondata_skills

# Install a single skill
npx skills add aborruso/ondata_skills --skill openalex
```

Or install manually:

1. Clone the repo: `git clone https://github.com/aborruso/ondata_skills`
2. Copy the skill folder (e.g. `skills/data-quality-csv/`) into your AI tool's skills directory
3. Enable the skill in your tool's settings

---

## Catalog

| Skill | Description | Category | Eval |
|---|---|---|---|
| [openalex](skills/openalex/) | Query OpenAlex API for scholarly works, authors, and PDF retrieval | Research | [🟡 78/100](evals/openalex/) |

---

## Evals

Each skill has a test battery in [`evals/`](evals/) to verify trigger behavior, process correctness, and output quality.

See [`evals/README.md`](evals/README.md) for the full dashboard and instructions on how to run or contribute evals.

---

## Skill structure

Each skill is a folder inside `skills/` with the following layout:

```
skills/
└── your-skill-name/          ← kebab-case, matches the skill name
    ├── SKILL.md              ← required — instructions + YAML frontmatter
    ├── scripts/              ← optional — executable scripts (Python, Bash…)
    ├── references/           ← optional — supporting documentation
    └── assets/               ← optional — templates, fonts, icons
```

### SKILL.md format

Every skill starts with a YAML frontmatter block:

```markdown
---
name: your-skill-name
description: What it does and when to use it. Use when the user says "[trigger phrase]".
---

# Your Skill Name

## Instructions
…
```

**Rules:**

- `name`: kebab-case only, no spaces, no capitals — must match the folder name
- `description`: required — include both what the skill does and when to trigger it; max 1024 characters
- No `README.md` inside the skill folder — all documentation goes in `SKILL.md` or `references/`
- File must be named exactly `SKILL.md` (case-sensitive)

---

## Contribute

Have a skill you find useful? Open a pull request.

1. Fork the repo
2. Create your skill folder under `skills/` following the structure above
3. Make sure `SKILL.md` has valid YAML frontmatter with `name` and `description`
4. Add your skill to the catalog table in this README
5. Open a PR with a short description of what the skill does

No formal review process yet — we'll figure it out as we grow.
