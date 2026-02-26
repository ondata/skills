# open-data-quality

Quality validator for open data: local CSV files and datasets from CKAN/DCAT-AP portals.

Runnable directly with **`uvx`** — no installation required.

---

## Installation / usage with uvx

```bash
# Directly from GitHub (no install needed)
uvx --from git+https://github.com/yourorg/open-data-quality odq-csv data.csv
uvx --from git+https://github.com/yourorg/open-data-quality odq-ckan https://dati.gov.it/opendata DATASET-ID

# Or install globally with uv
uv tool install git+https://github.com/yourorg/open-data-quality
odq-csv data.csv
odq-ckan https://dati.gov.it/opendata DATASET-ID
```

---

## `odq-csv` — local CSV file validation

```
Usage: odq-csv [OPTIONS] CSV_FILE

Arguments:
  CSV_FILE  Path to the CSV file to validate

Options:
  --show-ok              Show passed checks too
  --output-json PATH     Save the report in JSON format
  --output-md   PATH     Save the report in Markdown format
  --sample-rows INT      Rows to sample for content checks [50000]
  --quiet / -q           Suppress terminal output
```

### What it checks

| Phase | Checks |
|-------|--------|
| **0 — Blockers** | File exists, not empty, not binary; DuckDB can parse it; minimum size |
| **1 — Structure** | Encoding (UTF-8 required), BOM, separator, header present |
| **2 — Columns** | Duplicate names, non-SQL names (spaces, special characters, leading digit), wide format (years/months as columns), total/aggregate rows, footnote markers |
| **3 — Content** | Comma decimal separator, non-ISO dates (DD/MM/YYYY, DD.MM.YYYY...), units in numeric values, multilingual placeholders (n/a, n.d., k.a., n.r....), null %, numeric columns typed as VARCHAR, near-duplicate category values (Jaro-Winkler fuzzy typo detection) |
| **4 — Codes** | EU NUTS codes, ISTAT municipality codes (6 digits, leading zeros), ISO 3166-1 country |

### Output

```
╭─────────────────────────────────────╮
│ Open Data Quality Report            │
│ Source:   bilancio_2023.csv         │
│ Profile:  unknown                   │
│ Date:     2026-02-25                │
│ Score:    57/100 (34/60 pts)        │
╰─────────────────────────────────────╯

⚠️  MAJOR (5)
  •  [phase2_columns] 1 aggregate/total row(s) at end of file
     Detail: TOTALE,1156788,1161000,1169000,"2049,06"
     Fix: Remove total rows; publish separate summary if needed
  •  [phase3_content] Comma decimal separator in 1 column(s): ['Reddito medio']
     Fix: mlr --csv put 'for(k,v in $*)...' data.csv
  ...

Score breakdown
  File format compliance    15/15
  Data structure quality    12/20
  Data content quality       7/25
```

### Exit codes

| Code | Meaning |
|------|---------|
| `0` | No issues (or minor only) |
| `1` | At least one MAJOR — usable with caution |
| `2` | At least one BLOCKER — unusable |

Useful in CI/CD pipelines:

```bash
odq-csv data.csv -q || { echo "Data quality check failed"; exit 1; }
```

---

## `odq-ckan` — CKAN portal dataset validation

```
Usage: odq-ckan [OPTIONS] PORTAL_URL DATASET_ID

Arguments:
  PORTAL_URL   Base URL of the CKAN portal (e.g. https://dati.gov.it/opendata)
  DATASET_ID   Dataset ID or slug (e.g. anpr-comuni-aggiornamento)

Options:
  --download             Download the first CSV and validate it with odq-csv
  --check-urls / --no-check-urls  Check HTTP accessibility of resources [default: on]
  --show-ok              Show passed checks too
  --output-json PATH     Save JSON report
  --output-md   PATH     Save Markdown report
  --sample-rows INT      Rows to sample for CSV checks [50000]
  --quiet / -q           Suppress terminal output
```

### What it checks

| Phase | Checks |
|-------|--------|
| **5a — Profile** | Auto-detect DCAT-AP profile (IT, DE, FR, BE, NL, UK, ES, baseline 2.x) |
| **5b — Baseline metadata** | Title, description (>=80 chars, different from title), publisher, license, tags (>=3), `issued`/`modified` (presence + ISO 8601), update frequency, temporal/geographic coverage, language, identifier |
| **5c — Profile-specific** | Required fields for DCAT-AP_IT (`holder_name`, `identifier`, `theme`), DE, BE, NL, ES |
| **Per resource** | Format, MIME type, license on each distribution, stable URL (no Google Sheets / bit.ly / Dropbox), non-zero size |
| **Accessibility** | HTTP HEAD on each resource URL; blocker if 404 |
| **6 — Consistency** | Declared vs detected encoding; data freshness (declared frequency vs `modified` date) |

### Examples

```bash
# Metadata only (fast, no download)
odq-ckan https://dati.gov.it/opendata anpr-comuni-aggiornamento

# Metadata + accessibility + CSV validation
odq-ckan https://dati.gov.it/opendata anpr-comuni-aggiornamento --download

# Skip URL check (offline or slow network)
odq-ckan https://portal.example.org my-dataset --no-check-urls

# Output for pipelines
odq-ckan https://dati.gov.it/opendata DATASET-ID --download --output-json report.json --output-md report.md --quiet
echo "Score: $(jq '.score' report.json)/100"
```

### Supported portals and detected DCAT-AP profiles

| Portal | Detected profile |
|--------|-----------------|
| `dati.gov.it` | DCAT-AP_IT |
| `govdata.de` | DCAT-AP_DE |
| `data.gouv.fr` | DCAT-AP_FR |
| `data.gov.be` | DCAT-AP_BE |
| `data.overheid.nl` | DCAT-AP_DONL |
| `data.gov.uk` | DCAT-AP_UK |
| `datos.gob.es` | DCAT-AP_ES |
| All others | DCAT-AP 2.x baseline |

---

## Scoring

| Dimension | Max | Notes |
|-----------|-----|-------|
| Accessibility | 20 | Portal only |
| Metadata completeness | 20 | Portal only |
| File format compliance | 15 | |
| Data structure quality | 20 | |
| Data content quality | 25 | |

With local CSV file only: score out of 60, normalized to /100.

---

## Severity levels

| Level | Meaning | Examples |
|-------|---------|----------|
| BLOCKER | Unusable data | Empty file, HTTP 404, DuckDB cannot parse |
| MAJOR | Usable with effort or error risk | Comma decimal, non-ISO dates, missing license |
| MINOR | Convention, low impact | CRLF, column names with spaces |

---

## Requirements

- Python >= 3.11
- `duckdb`, `charset-normalizer`, `httpx`, `rich`, `typer`

Installed automatically by `uvx` or `uv tool install`.
