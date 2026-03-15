# onData Skills

A curated collection of AI skills maintained by onData. Skills are tool-agnostic instructions that help AI assistants handle specific tasks consistently — without re-explaining your workflows every time.

A **skill** is a set of instructions that tells an AI assistant how to handle a specific task: which tools to use, in what order, and how to format the output. Once installed, it activates automatically when relevant.

For example, install the `openalex` skill and ask `$openalex: Find recent papers on urban heat islands with open access PDFs` — you'll get a structured list of works with titles, authors, DOIs, and direct download links.

The project follows an open source model: public repo, open contributions, organic growth.

---

## Install

Skills follow the [Agent Skills](https://agentskills.io) open standard. If you're new to skills, start with a single one to get familiar with how they work:

```bash
npx skills add ondata/skills --skill openalex
```

Once installed, open your AI tool and try it: `use $openalex skill to find recent papers on urban heat islands with open access PDFs` — you'll get a list of works with titles, authors, DOIs, and direct PDF links.

Once comfortable, you can install the full collection:

```bash
npx skills add ondata/skills
```

Or install manually:

1. Clone the repo: `git clone https://github.com/ondata/skills`
2. Copy the skill folder (e.g. `skills/openalex/`) into your AI tool's skills directory
3. Enable the skill in your tool's settings

### Claude Desktop

If you use Claude Desktop, you can install some skills directly from the UI using `.skill` files. Not all skills are available this way — we publish `.skill` packages only for skills that have been tested and confirmed to work on Claude Desktop. Check the [latest release](https://github.com/ondata/skills/releases/latest) to see which ones are available.

1. Download the `.skill` file for the skill you want from the release assets (e.g. `openalex.skill`).
2. In Claude Desktop, open the skill installation wizard and load the file.
3. After installation, open the skill settings and add any required domains to the **Domain allowlist** (see the skill's page for details).

### About the install tool

The `npx skills add` commands above use [skills.sh](https://skills.sh/docs), a shell tool and currently the most convenient way to install and manage Agent Skills across AI tools.

Skills work best with CLI-based AI tools (Claude Code, Gemini CLI, OpenAI Codex, etc.) — the command-line context gives the agent full access to your environment and makes skill workflows faster and richer.

During installation you'll be asked:

- **Which AI tools** to make the skill available in (e.g. Claude code, OpenAI Codex, Gemini cli, Cursor, Windsurf, ecc.).
- **User or project scope** — user skills are available in every project on your machine; project skills are installed into the current repository and shared with anyone who clones it.
- **Installation method** — **Symlink** (recommended) creates a single canonical copy that all your agents share; run `npx skills update` to update. **Copy** creates independent copies per agent and is useful only when symlinks are not supported on your system.

---

## Catalog

| Skill | Description | Category | Eval |
|---|---|---|---|
| [ipa](skills/ipa/) | Look up PEC addresses and contacts for Italian public administrations via the IPA registry | Italy / PA | — |
| [open-data-quality](skills/open-data-quality/) | Validate open data quality for CSV files and CKAN datasets; produces severity-ranked reports with a quality score | Open Data | — |
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
