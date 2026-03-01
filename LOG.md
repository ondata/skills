# LOG

## 2026-03-01

- `open-data-quality`: add qualitative assessment section to SKILL.md — 9 LLM-only checks (title discoverability, title↔description, description↔content, content↔update frequency, dataset usefulness); runs after scripts, requires data content; Good/Acceptable/Poor rating; added to report template
- `open-data-quality`: add `outlier_values` check (phase3_content) — IQR method on numeric columns (≥100 rows); severity MINOR, -2 pts; no fix suggestion (signal only); new fixture `outlier_values.csv`; 36/36 tests pass
- `open-data-quality`: add `duplicate_rows` check (phase3_content) — detects exact duplicate rows via DuckDB `SELECT DISTINCT *`; severity MAJOR, -3 pts on data content quality; new fixture `duplicate_rows.csv`; 35/35 tests pass

## 2026-02-26

- `open-data-quality`: fix IT holder label — `dcatapit:datasetHolder` → `dct:rightsHolder` in code and all reference docs (confirmed from real dati.gov.it data)
- `open-data-quality`: remove deprecated `dcatapit:datasetHolder` row from profiles table; `dct:rightsHolder` now marked M for IT
- `open-data-quality`: add `portal_field_aliases.json` — JSON vocabulary mapping standard DCAT-AP field names to portal-specific CKAN extras keys; UK profile maps `issued`/`modified` → `dcat_issued`/`dcat_modified`
- `open-data-quality`: fix UK date detection — `metadata_validator.py` now uses `FIELD_ALIASES` fallback for date fields per profile
- `open-data-quality`: add 3 new tests — `test_it_holder_present_ok`, `test_it_holder_missing_flagged`, `test_uk_dcat_prefixed_dates_accepted`; 34/34 pass

- `open-data-quality`: added pytest test suite — 25 tests across phase0–3 + CLI integration; fixtures in `scripts/tests/fixtures/`; `pytest` added as dev dependency in `pyproject.toml`
- `open-data-quality`: fix fuzzy check — skip datetime/timestamp columns stored as VARCHAR (e.g. `2025-03-14T00:00:00` was triggering false positive near-duplicate alert)

- `open-data-quality`: file type detection in phase 0 — detect ZIP, HTML/XML, JSON, PDF, OLE2/Excel, UTF-16 via magic bytes/content sniffing; report specific type (e.g. "File is a ZIP archive") instead of generic binary/separator error
- `open-data-quality`: fuzzy false positive fix — add `levenshtein/max_len < 10%` ratio filter + raise JW threshold to 0.95 + minimum length > 5; eliminates NORD-EST~NORD-OVEST, MINISTERO DELLA DIFESA~SALUTE type false positives while preserving real typos (D'INTERESSE~DI INTERESSE caught at 4% ratio)

- `open-data-quality`: fix encoding false positive — normalize `utf_8` → `utf-8` before comparison; was marking valid UTF-8 files as MAJOR issue
- `open-data-quality`: split fuzzy check — trailing/leading whitespace now reported separately; fuzzy comparison works on trimmed values to avoid spurious matches
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
