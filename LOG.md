# LOG

## 2026-08-10

- `typst-cards`: new full-bleed layout pattern — `margin: 0` + a `slide()` helper that adds the padding back via `inset`, with rail, page counter and URL drawn through `place` (out of flow, so content cannot push them). Enables backgrounds, colour bands and images reaching every edge, which the margined pattern cannot do. New `references/slides-fullbleed-starter.typ` (5 cards, 1:1); the two existing starters are unchanged. New "Two layout patterns" section with the rule for choosing. Adapted from Mickaël Canouil's post on Typst LinkedIn carousels (credited in SKILL.md); geometry kept in inches — `7.5in × 144ppi` = exactly 1080px, while his 21cm square gives 1191px
- `typst-cards`: PDF output alongside PNG — a LinkedIn carousel is uploaded as a single PDF document post, so `typst compile slides.typ output/deck.pdf` is now part of the flow; frontmatter `description` updated accordingly; optional ImageMagick one-liner for an animated GIF preview
- `typst-cards`: new pitfall — `block(width: 100%, height: 100%, inset: ...)` **clips silently** on overflow (one page, text cut at the edge, no warning, exit 0); the same content without `height: 100%` spills into 6 real pages. Diagnostic recipe + page-count check added to Phase 4. Verified on typst 0.14.2
- `typst-cards`: new pitfall — inside `body`, `width: 100%` is the padded column, not the page, so "full-bleed" decoration drawn there comes out framed; the `slide()` helper takes a `bleed` argument for content that must be measured against the page
- `typst-cards`: font availability documented as two tiers — only `Libertinus Serif`, `New Computer Modern` (+ Math) and `DejaVu Sans Mono` are embedded in the binary (`typst fonts --ignore-system-fonts`); `DejaVu Sans`, previously the skill's primary body font, is system-only and can silently fall back elsewhere. Stated plainly: there is no embedded sans-serif
- `typst-cards`: new pitfall sub-case — smart quotes never reach string values, so `#helper("l'x")` keeps a straight apostrophe while `#helper[l'x]` and plain markup get `’`; interpolating the string into content does not rescue it. Silent, no error, and a deck mixing prose with helper calls ends up with two kinds of apostrophe. Surfaced by the first real deck built with the new pattern; mechanism isolated with a 5-case compile
- `typst-cards`: fix broken `cp` recipe — all three slide starters imported `theme-starter.typ` while Phase 3 tells you to copy the theme to `theme.typ`, so following the documented recipe failed with "file not found". Imports now point at `theme.typ`; verified end-to-end on all three starters (5 / 3 / 5 pages + PDF). Reported by the Copilot review on PR #27
- `typst-cards`: `#set document(title:, author:)` for PDF metadata, `#set text(lang: "it")` for Italian hyphenation, and deck-level guidance (5–7 cards, cover → content → CTA, one inverted card, one visual idea per deck)

## 2026-07-28

- `scrivi-chiaro-pa`: new skill — write, rewrite, or review Italian PA content in plain language, based on the Designers Italia *Guida al linguaggio della Pubblica Amministrazione* (CC-BY 4.0). Three modes (draft / rewrite / review), tone-of-voice scenarios, final glossary pass + checklist. References: style/grammar/numbers, structure/usability/SEO/accessibility, tone of voice (9 scenarios), social/newsletter/images/editorial management, A–Z glossary (~90 terms in two tables). Content harvested from the published "bozza" on docs.italia.it (suggerimenti + tono di voce sections exist only there) and from the `italia/writing-toolkit` repo (glossary RST sources)

## 2026-06-14

- `datawrapper`: document arrow markers in locator maps (new Datawrapper feature). Tested end-to-end via pure API: arrows are writable (line + flow types, triangle/lines heads, bidirectional, gradient, taper, curve). Full JSON schema + per-field table added to `references/locator-map.md`
- `datawrapper`: fix wrong marker storage in `references/locator-map.md` — there is NO `/markers` endpoint (404); points, areas and arrows are all stored in the chart data via `PUT /v3/charts/<ID>/data` as `{"markers":[...]}` (full replace each PUT). Corrected point (needs `icon` block) and area (colors in top-level `properties`, GeoJSON-style keys) examples
- `datawrapper`: document counterintuitive `curve.angle` behaviour — values near 0 produce huge looping arcs; gentle curves need larger magnitudes that scale with arrow length (`|angle| ≈ km/2.5`); recommend tuning in GUI then reading back via API (verified by hand-edit round-trip)

## 2026-04-26

- `typst-cards`: refactor starter templates to native page-level footer — `#set page(footer: footer-block(URL, dark: ...))` with Typst's `counter(page).display()` / `.final().first()`; replaces fragile `#v(1fr) + #ctr(n,total)` last-row pattern that produced silent ghost slides on dense content; new `footer-block` helper in theme; new pitfall entry; sub-case on literal helper params under special-chars table; smoke-tested both starters (5+3 PNGs, footer fully visible)
- `typst-cards`: add "Footer/edge content never clips" design rule — footer, counter, source URL must be fully visible; fix via larger page bottom margin or smaller footer font; must-check in Phase 4
- `typst-cards`: expand "Special characters in content mode" pitfall — table covering `$`, `//`, `_`, `*`, `@`, `<`, `~` (replaces the previous single bullet on `<`); typical contexts where these characters break compilation with "unclosed delimiter" errors
- `typst-cards`: tighten Phase 4 — explicit read → evaluate → report+propose → wait flow; AI must look at PNGs (not just check existence), evaluate against design principles, propose concrete fixes, wait for user decision before iterating
- `typst-cards`: new skill — generates PNG images for online communication (social posts, carousels, infographics) using Typst; brand-materials interview, supported formats (1:1, 4:5, 9:16, 16:9, 1.91:1), three reference starters (`theme-starter.typ`, `slides-1x1-starter.typ`, `slides-16x9-starter.typ`), known pitfalls

## 2026-04-24

- `openalex`: strengthen API key security — added prominent SECURITY callout at top of SKILL.md; expanded Common Pitfalls rule to cover all output contexts (text responses, echoed commands, logs), not just verification

## 2026-03-03

- `evals/openalex`: add `run_evals.sh` — runs prompts via `claude -p`, saves outputs to `runs/YYYY-MM-DD/`, auto-checks 4 pitfall patterns (relevance_sort, title.search scope, multi-line curl, API key printed)
- `openalex`: never print API key to verify presence — use `[[ -n "${OPENALEX_API_KEY:-}" ]]`; added to Quick Start and Common Pitfalls in SKILL.md
- `evals/openalex`: add 20 synthetic test prompts (test-09–test-28) targeting 11 known pitfall zones (relevance_sort_no_search, title_search_standalone, entity_name_filter, sequential_batch, nested_select, missing_api_key, default_per_page, multi_line_curl, null_csv_field, pdf_fallback_chain, wrong_search_scope); add corresponding pitfall checks to `checks.md`

## 2026-03-01

- `open-data-quality`: ZIP-wrapped CSV support — if resource declared as CSV is actually a ZIP, extract largest CSV to /tmp and proceed with full analysis; report MINOR `zip_wrapped_csv` instead of BLOCKER; uses Python `zipfile` (no DuckDB/Polars ZIP support); score 40→86 on Liguria air quality dataset

- `open-data-quality`: fix `_extras_value` — also check top-level package fields; some harvesters (dati.gov.it from regional portals) promote holder_name/identifier to top-level instead of extras; fixes false-positive MAJORs; score 83→97 on test dataset
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
