# LOG

## 2026-02-24

- `openalex` SKILL.md v0.2: added filter syntax (OR/NOT/ranges), batch pipe lookup, two-step entity lookup, `group_by`/`sample`/`seed` params, `per-page=200` default, error handling with backoff, endpoint costs table

## 2026-02-15

- Saved reference documents in `docs/`: [testing-agent-skills-with-evals.md](docs/testing-agent-skills-with-evals.md) and [agent-skills-specification.md](docs/agent-skills-specification.md)
- Added "Core Idea" section to `PRD.md` (skill creation as an inclusive, non-technical activity)
- Created `docs/prd.md` with Alessio Cimarelli's eval proposal
- Created `evals/` structure with `_template/` and first eval for `openalex`
- First complete eval run on `openalex`: score 78/100 (7/9 checks), 7 improvements to the skill
  - single-line curl required (warning at top of SKILL.md)
  - `title.search` inside `filter=`, not standalone
  - `display_name` as title (Output Format section)
  - `api_key` explicitly documented as pitfall
  - Europe PMC fallback documented as recipe #6
  - Definition of Done added to SKILL.md
- Updated `README.md`: catalog with Eval column, Evals section, fix skill data-quality-csv → openalex
- Created project `CLAUDE.md`
