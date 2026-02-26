---
name: open-data-quality
description: "Comprehensive open data quality validator for two audiences: data analysts who need to assess whether a dataset is ready to use, and public administrations who want to self-evaluate their published data. Automatically adapts based on input type: (A) local CSV file only — performs file-level structural and content checks; (B) CKAN/open data portal dataset — adds metadata completeness, resource accessibility, URL reachability, and DCAT-AP compliance (supports all national profiles: DCAT-AP 2.x baseline, IT, BE, NL, DE, FR, UK, ES, and others). Always use this skill when the user mentions: data quality, validate dataset, check CSV, open data compliance, metadata audit, CKAN dataset review, \"is this data usable?\", or whenever a CSV file or CKAN dataset ID/URL is provided for quality assessment. Produces severity-ranked reports (blocker / major / minor) with concrete fixes, quality score, and a plain-language summary for non-technical stakeholders."
---

# Open Data Quality Validator

## Overview

This skill validates open data quality for two contexts and two audiences:

**Input contexts** (auto-detected):
- **Local CSV** — file on disk, no portal metadata available
- **CKAN / open data portal dataset** — dataset ID or URL

**Target audiences**:
- **Data analysts** — "Can I trust and use this data?"
- **Public administrations** — "Does our publication meet open data standards?"

---

## Input Detection

**Before running any checks**, identify what you have:

```
LOCAL CSV only → run odq-csv (phases 0–4)
CKAN/portal   → run odq-ckan (phases 0–6, optionally --download for CSV too)
```

Signs of a CKAN dataset: user provides a dataset ID, a CKAN URL (`/dataset/...`), or asks
to retrieve a dataset from a portal. If uncertain, ask: *"Do you have the file locally, or
should I retrieve it from an open data portal?"*

---

## Installation

The tool runs on any OS (Windows, macOS, Linux) via `uvx` — no permanent install needed.
If `uv` is not available, install it first:

```bash
# Install uv (once)
curl -LsSf https://astral.sh/uv/install.sh | sh        # macOS / Linux
winget install --id=astral-sh.uv -e                    # Windows
```

**Windows note**: set `PYTHONUTF8=1` to avoid encoding errors on cp1252 terminals:

```powershell
# PowerShell
$env:PYTHONUTF8=1; uvx --from git+https://github.com/ondata/open-data-quality odq-csv data.csv

# Command Prompt
set PYTHONUTF8=1 && uvx --from git+https://github.com/ondata/open-data-quality odq-csv data.csv
```

---

## Usage

### Local CSV (phases 0–4)

```bash
# Run directly — no install needed
uvx --from git+https://github.com/ondata/open-data-quality odq-csv data.csv

# With JSON and Markdown output
uvx --from git+https://github.com/ondata/open-data-quality odq-csv data.csv --output-json report.json --output-md report.md
```

### CKAN portal dataset (phases 0–6)

```bash
# Metadata + accessibility only (fast)
uvx --from git+https://github.com/ondata/open-data-quality odq-ckan PORTAL_URL DATASET_ID

# Metadata + accessibility + CSV validation
uvx --from git+https://github.com/ondata/open-data-quality odq-ckan PORTAL_URL DATASET_ID --download

# With output files
uvx --from git+https://github.com/ondata/open-data-quality odq-ckan PORTAL_URL DATASET_ID --download --output-json report.json --output-md report.md
```

---

## Validation Modes

| Mode | Goal | Command hint |
|------|------|-------------|
| **Quick Triage** | Is this usable at all? | Default run, check exit code |
| **Standard Check** | Analyst assessment | Default run, read full output |
| **Full Audit** | PA self-evaluation | Add `--show-ok` to see passed checks too |

Default to Standard Check unless the user asks otherwise.

---

## What Gets Checked

For a full breakdown of all checks per phase, see `scripts/README.md`.

**Local CSV** (phases 0–4): file validity, encoding, BOM, column names, wide format,
aggregate rows, decimal separators, date formats, units in cells, placeholders, reference codes.

**CKAN portal** (phases 0–6): all CSV checks (with `--download`) plus DCAT-AP profile
detection, metadata completeness, per-resource format/license/URL, HTTP accessibility,
declared vs actual encoding, update frequency consistency.

---

## Report Template

```markdown
# Open Data Quality Report
**Dataset**: [title or filename]
**Source**: [Local CSV | Portal: URL]
**DCAT-AP profile**: [baseline 2.x | IT | DE | FR | BE | NL | UK | ES | unknown]
**Validated**: [YYYY-MM-DD]
**Mode**: [Quick Triage | Standard Check | Full Audit]

## Summary
[2–3 plain-language sentences: who published this, is it usable, main problems.]

## Quality Score: XX/100

## Blocker Issues ⛔
## Major Issues ⚠️
## Minor Issues ℹ️

## Score Breakdown
| Dimension | Score | Notes |
|-----------|-------|-------|
| Accessibility | /20 | Portal only |
| Metadata completeness | /20 | Portal only |
| File format compliance | /15 | |
| Data structure quality | /20 | |
| Data content quality | /25 | |

## Recommended Actions
[Numbered, by severity, with code examples]

## What This Means for You
**As a data analyst**: [Can I use this? What to fix before analysis?]
**As a publisher**: [What must be fixed before republishing?]
```

---

## Severity Levels

| Level | Definition | Example |
|-------|------------|---------|
| **⛔ Blocker** | Cannot use the data at all | File empty, HTTP 404, cannot parse |
| **⚠️ Major** | Usable with effort or risk of errors | Comma decimals, non-ISO dates, missing license |
| **ℹ️ Minor** | Convention issue, low impact | Spaces in column names, quoted newlines in header |

---

## Exit Codes

| Code | Meaning |
|------|---------|
| `0` | No issues (or minor only) |
| `1` | At least one MAJOR — usable with caution |
| `2` | At least one BLOCKER — unusable |

---

## References

- [DCAT-AP 2.x](https://joinup.ec.europa.eu/collection/semantic-interoperability-community-semic/solution/dcat-application-profile-data-portals-europe)
- [RFC 4180 — CSV](https://tools.ietf.org/html/rfc4180) · [ISO 8601](https://en.wikipedia.org/wiki/ISO_8601)
- [Tidy Data](https://vita.had.co.nz/papers/tidy-data.pdf) · [Frictionless Table Schema](https://specs.frictionlessdata.io/table-schema/)
- IT: [DCAT-AP_IT](https://www.dati.gov.it/content/dcat-ap-it-v10-profilo-italiano-dcat-ap-0) · [AgID](https://www.agid.gov.it/it/dati/open-data)
- DE: [DCAT-AP.de](https://www.dcat-ap.de/) · FR: [schema.data.gouv.fr](https://schema.data.gouv.fr/)
- BE: [DCAT-AP_BE](https://www.health.belgium.be/en/dcat-ap-be) · NL: [DCAT-AP_DONL](https://docs.dataportal.nl/)
- UK: [data.gov.uk profile](https://guidance.data.gov.uk/) · ES: [datos.gob.es](https://datos.gob.es/es/doc-developer)

## Extended References

- `references/dcat-ap-profiles.md` — Field-by-field comparison across all national profiles
- `references/common-antipatterns.md` — Universal + locale-specific patterns with fixes
- `references/dcat-ap-it-fields.md` — Detailed DCAT-AP_IT field list (Italian PA)
- `scripts/README.md` — Full tool documentation, all options and examples
