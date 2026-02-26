# LOG

## 2026-02-26

- `open-data-quality`: fix #11 — placeholder message now shows actual values found (e.g. `NA`) instead of full catalog `n/a, n.d., -…`; SQL uses `list_distinct(list(...))` to collect found values per column

- `open-data-quality`: non-UTF8 encoding no longer a BLOCKER — `charset_normalizer` detects encoding, file converted to UTF-8 temp copy, full analysis runs; MAJOR finding reported (tested on Comune di Palermo CP1250 dataset: 33→73/100)
- `open-data-quality`: added fuzzy near-duplicate category check via `jaro_winkler_similarity > 0.92` (DuckDB built-in) — found real issues in Palermo dataset
- `open-data-quality`: CRLF line endings no longer flagged (RFC 4180 prescribes CRLF)
- `open-data-quality`: replaced `chardet` with `charset_normalizer` for more accurate encoding detection
- `open-data-quality`: added developer notes to `CONTRIBUTING.md` (WSL/uvx cache, PYTHONUTF8, DuckDB lenient parsing)
- `evals/open-data-quality/fixtures/palermo-edifici-pubblici-cp1250.csv`: archived as encoding test fixture
- `open-data-quality`: fixed false BLOCKER on valid CSVs with quoted newlines in headers — retry with `strict_mode=false`; added `_lenient` flag + `_rcsv()` helper across all DuckDB queries (score 29→86 on Copertino dataset)
- `open-data-quality`: SKILL.md rewritten — `uvx odq-csv`/`odq-ckan` is now the single primary path; all bash inline phases removed (no double maintenance)
- SKILL.md reduced from ~450 to ~130 lines
- `evals/checks.md` updated to validate `uvx` + package usage

## 2026-02-25

- Added `open-data-quality` skill: CSV validator (`odq-csv`) and CKAN/DCAT-AP metadata validator (`odq-ckan`)
- Created missing `__init__.py` for package discovery
- Translated `scripts/README.md` from Italian to English
- Tested end-to-end on real dati.gov.it datasets (bilancio, popolazione)
- Created eval suite: `evals/open-data-quality/` (8 prompts, 15 checks)

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
