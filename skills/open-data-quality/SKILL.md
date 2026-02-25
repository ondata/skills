---
name: open-data-quality
description: >
  Comprehensive open data quality validator for two audiences: data analysts who need to assess
  whether a dataset is ready to use, and public administrations who want to self-evaluate their
  published data. Automatically adapts based on input type: (A) local CSV file only — performs
  file-level structural and content checks; (B) CKAN/open data portal dataset — adds metadata
  completeness, resource accessibility, URL reachability, and DCAT-AP compliance (supports all
  national profiles: DCAT-AP 2.x baseline, IT, BE, NL, DE, FR, UK, ES, and others).
  Always use this skill when the user mentions: data quality, validate dataset, check CSV, open
  data compliance, metadata audit, CKAN dataset review, "is this data usable?", or whenever
  a CSV file or CKAN dataset ID/URL is provided for quality assessment. Produces severity-ranked
  reports (blocker / major / minor) with concrete fixes, quality score, and a plain-language
  summary for non-technical stakeholders.
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

The skill produces a structured report with severity-ranked issues and a quality score (/100).

---

## Input Detection

**Before running any checks**, identify what you have:

```
LOCAL CSV only → run Phases 0–4 only (skip portal phases)
CKAN/portal   → run all phases (0–6)
```

Signs of a CKAN dataset: user provides a dataset ID, a CKAN URL (`/dataset/...`), or asks
to retrieve a dataset from a portal. If uncertain, ask: *"Do you have the file locally, or
should I retrieve it from an open data portal?"*

---

## Available Tools

| Tool | Purpose |
|------|---------|
| CKAN MCP Server | Retrieve metadata, resources, org info from CKAN portals |
| DuckDB CLI | SQL-based structural and content analysis |
| Miller (`mlr`) | CSV inspection, statistics, type inference |
| `file`, `iconv`, `xxd` | Encoding detection and binary checks |
| `curl` | URL reachability, HTTP status, download |
| `jq` | Parse and filter portal JSON metadata |
| `head`, `wc`, `grep` | Quick file inspection |

---

## Validation Modes

| Mode | Time | Goal | Phases |
|------|------|------|--------|
| **Quick Triage** | 5–10 min | Is this usable at all? | 0–1 (+ 5 if portal) |
| **Standard Check** | 15–25 min | Analyst assessment | 0–4 (+ 5–6 if portal) |
| **Full Audit** | 30–60 min | PA self-evaluation / certification | All phases |

Default to Standard Check unless the user asks otherwise.

---

## Phase 0: Blocker Detection ⛔ (Always first — exit immediately on failure)

### 0a. File-level blockers (always)

```bash
[ -f "$CSV" ] && [ -s "$CSV" ] \
  || { echo "❌ BLOCKER: File missing or empty"; exit 1; }

file -bi "$CSV" | grep -q "text/" \
  || { echo "❌ BLOCKER: Not a text file (binary/PDF/ZIP mislabeled as CSV)"; exit 1; }

duckdb :memory: "SELECT COUNT(*) FROM read_csv_auto('$CSV')" 2>/dev/null \
  || { echo "❌ BLOCKER: Cannot parse as CSV (corrupted or invalid format)"; exit 1; }

ROWS=$(duckdb :memory: "SELECT COUNT(*) FROM read_csv_auto('$CSV')")
COLS=$(duckdb :memory: "CREATE TABLE t AS SELECT * FROM read_csv_auto('$CSV'); \
  SELECT COUNT(*) FROM information_schema.columns WHERE table_name='t'")
[ "$ROWS" -gt 1 ] && [ "$COLS" -gt 1 ] \
  || { echo "❌ BLOCKER: Trivial data ($ROWS rows, $COLS columns)"; exit 1; }
```

### 0b. URL reachability blockers (portal datasets only)

```bash
HTTP_CODE=$(curl -sIL -o /dev/null -w "%{http_code}" --max-time 15 "$RESOURCE_URL")
[ "$HTTP_CODE" -eq 200 ] \
  || { echo "❌ BLOCKER: Resource not accessible (HTTP $HTTP_CODE)"; exit 1; }

# Unstable URL patterns — universal, not country-specific
echo "$RESOURCE_URL" | grep -qiE \
  "bit\.ly|tinyurl|goo\.gl|t\.co|google\.com/spreadsheets|dropbox\.com|drive\.google|onedrive\.live" \
  && echo "⚠️ WARNING: Unstable URL (cloud storage / short link) — use permanent institutional hosting"

[ "${RESOURCE_SIZE:-}" = "0" ] || [ -z "${RESOURCE_SIZE:-}" ] \
  && echo "⚠️ WARNING: Resource size missing or zero in metadata"
```

---

## Phase 1: File Structure Validation

```bash
ENCODING=$(file -bi "$CSV" | sed 's/.*charset=//')
[ "$ENCODING" = "utf-8" ] || [ "$ENCODING" = "us-ascii" ] \
  || echo "⚠️ MAJOR: Encoding is $ENCODING, expected UTF-8"

head -c 3 "$CSV" | xxd | grep -q "efbbbf" \
  && echo "⚠️ MAJOR: UTF-8 BOM present (causes parsing errors in many tools)"

duckdb :memory: "
  CREATE TABLE data AS SELECT * FROM read_csv_auto('$CSV');
  DESCRIBE data;
  SELECT COUNT(*) as total_rows FROM data;"

file "$CSV" | grep -q "CRLF" && echo "⚠️ MINOR: Windows line endings (CRLF) — prefer LF"
```

---

## Phase 2: Column & Structure Quality

```bash
duckdb :memory: "
  CREATE TABLE data AS SELECT * FROM read_csv_auto('$CSV');

  -- Problematic column names
  SELECT column_name FROM information_schema.columns
  WHERE table_name='data'
    AND (column_name LIKE '% %'
      OR column_name ~ '[^a-zA-Z0-9_]'
      OR column_name ~ '^[0-9]');

  -- Duplicate column names
  SELECT column_name, COUNT(*) n FROM information_schema.columns
  WHERE table_name='data' GROUP BY column_name HAVING COUNT(*) > 1;

  -- Wide format: time periods as column names (year numbers or month names in any language)
  SELECT column_name FROM information_schema.columns
  WHERE table_name='data'
    AND (column_name ~ '^(19|20)[0-9]{2}$'
      OR column_name ~* '^(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)'
      OR column_name ~* '^(gen|fev|mar|avr|mai|jui|aou|sep|okt|nov|dez)'
      OR column_name ~* '^(ene|feb|mar|abr|may|jun|jul|ago|sep|oct|nov|dic)');"

# Aggregate rows (multilingual keywords)
tail -5 "$CSV" | grep -i \
  "totale\|total\|subtotal\|subtotale\|somma\|sum\|media\|average\|gesamt\|insgesamt\|suma\|total général"
```

---

## Phase 3: Data Type & Content Quality

```bash
duckdb :memory: "CREATE TABLE data AS SELECT * FROM read_csv_auto('$CSV'); SUMMARIZE data;"

# Non-dot decimal separator (common across European locales: IT, DE, FR, ES, PT, PL...)
grep -m5 -oE '[0-9]+,[0-9]+' "$CSV" \
  && echo "⚠️ MAJOR: Comma decimal separator detected — standardize to dot"

# Non-ISO date format (any of the common patterns)
# DD/MM/YYYY → most of Europe | MM/DD/YYYY → US | DD.MM.YYYY → DE/CH/AT
grep -m5 -oE '[0-9]{1,2}[/\.][0-9]{1,2}[/\.][0-9]{4}' "$CSV" \
  && echo "⚠️ MAJOR: Non-ISO date format — convert to YYYY-MM-DD"

# Units embedded in numeric cells
grep -m5 -oE '[0-9]+ ?(kg|km|m²|km²|EUR|€|%|\$|£|GBP|ha|MW|GWh|tCO2)' "$CSV" \
  && echo "⚠️ MAJOR: Units mixed with numeric values — separate into a units column"

# Placeholder values (multilingual — extend list for your locale)
duckdb :memory: "
  CREATE TABLE data AS SELECT * FROM read_csv_auto('$CSV', all_varchar=true);
  SELECT column_name, COUNT(*) as n
  FROM (SELECT column_name, val FROM (UNPIVOT data ON COLUMNS(*) INTO NAME column_name VALUE val))
  WHERE LOWER(TRIM(val)) IN (
    'n/a','na','null','none','-','--','/',
    'not available','not applicable','unknown','missing',
    'n.d.','nd','assente','non disponibile',
    'n.r.','nr','inconnu','non disponible',
    'k.a.','ka','unbekannt','nicht verfügbar',
    'n.a.','desconocido','no disponible','não disponível',
    'onbekend','niet beschikbaar'
  )
  GROUP BY column_name HAVING COUNT(*) > 0 ORDER BY n DESC;"
```

---

## Phase 4: Administrative Code Integrity

Apply checks based on the dataset's country/scope.

```bash
# Find candidate code columns
duckdb :memory: "
  SELECT column_name FROM (DESCRIBE SELECT * FROM read_csv_auto('$CSV'))
  WHERE column_name ~* '(code|cod_|_code|_cod|nuts|lau|iso|zip|postal|id$|_id)';"
```

**Reference code formats by country/scope**:

| Scope | Code type | Format | Example |
|-------|-----------|--------|---------|
| EU | NUTS regions | `[A-Z]{2}[0-9A-Z]{1,3}` | `ITG12`, `DEA23` |
| All | ISO 3166-1 | `[A-Z]{2}` | `IT`, `DE`, `FR` |
| All | ISO 3166-2 | `[A-Z]{2}-[A-Z0-9]+` | `IT-PA`, `DE-BY` |
| All | ISO 4217 currency | `[A-Z]{3}` | `EUR`, `USD` |
| IT | ISTAT municipality | `[0-9]{6}` | `082053` |
| IT | Province (ISTAT) | `[0-9]{3}` | `082` |
| IT | CIG procurement | 10-char alphanumeric | `ABC1234567` |
| DE | AGS Gemeindeschlüssel | `[0-9]{8}` | `09162000` |
| FR | INSEE commune | `[0-9AB]{5}` | `75056` |
| NL | CBS gemeente | `[0-9]{4}` | `0363` |
| ES | INE municipality | `[0-9]{5}` | `28079` |
| UK | ONS GSS | `[A-Z][0-9]{8}` | `E09000001` |

---

## Phase 5: Portal Metadata Quality *(portal datasets only)*

### 5a. Detect the active DCAT-AP profile

```bash
IDENTIFIER=$(jq -r '.extras[]? | select(.key=="identifier") | .value' metadata.json 2>/dev/null)

# Italian profile: identifier follows istat_code:slug, holder_name field present
echo "$IDENTIFIER" | grep -qE '^[a-z]_[a-z0-9]+:' && echo "Profile: DCAT-AP_IT"
jq -e '.extras[]? | select(.key=="holder_name")' metadata.json >/dev/null 2>&1 \
  && echo "Profile: DCAT-AP_IT (holder_name present)"

# Other national portals
echo "$SERVER_URL" | grep -qiE 'govdata\.de'          && echo "Profile: DCAT-AP_DE"
echo "$SERVER_URL" | grep -qiE 'data\.gouv\.fr'       && echo "Profile: DCAT-AP_FR"
echo "$SERVER_URL" | grep -qiE 'data\.gov\.be'        && echo "Profile: DCAT-AP_BE"
echo "$SERVER_URL" | grep -qiE 'data\.overheid\.nl'   && echo "Profile: DCAT-AP_DONL"
echo "$SERVER_URL" | grep -qiE 'data\.gov\.uk'        && echo "Profile: DCAT-AP_UK"
echo "$SERVER_URL" | grep -qiE 'datos\.gob\.es'       && echo "Profile: DCAT-AP_ES"
# Fallback → DCAT-AP 2.x baseline (see references/dcat-ap-profiles.md)
```

### 5b. Universal baseline checks (all profiles)

```bash
jq -r '
  "Title:       \(.title // "❌ MISSING")",
  "Description: \(if (.notes // "" | length) > 80 then "✅ (\(.notes|length) chars)" else "⚠️ Too short" end)",
  "License:     \(.license_id // .license_title // "❌ MISSING")",
  "Publisher:   \(.organization.title // "❌ MISSING")",
  "Tags:        \(if (.tags | length) >= 3 then "✅ \([.tags[].name] | join(", "))" else "⚠️ Too few" end)"
' metadata.json

# Date fields — check both top-level and extras (varies by CKAN version and profile)
for DATE_KEY in issued modified; do
  VAL=$(jq -r "
    .${DATE_KEY} //
    (.extras[]? | select(.key==\"${DATE_KEY}\") | .value) //
    empty" metadata.json 2>/dev/null)
  if [ -z "$VAL" ]; then
    echo "⚠️ MAJOR: $DATE_KEY is missing or empty string"
  elif ! echo "$VAL" | grep -qE '^[0-9]{4}-[0-9]{2}-[0-9]{2}'; then
    echo "⚠️ MAJOR: $DATE_KEY='$VAL' is not ISO 8601 (expected YYYY-MM-DD)"
  else
    echo "✅ $DATE_KEY: $VAL"
  fi
done

# Per-resource
jq -r '.resources[] |
  "--- \(.name) ---",
  "  Format:  \(.format // "❌ MISSING")",
  "  MIME:    \(.mimetype // "⚠️ missing")",
  "  Size:    \(if ((.size // "0") | tonumber) > 0 then "\(.size) bytes ✅" else "⚠️ missing or 0" end)",
  "  License: \(.license_id // .license // "⚠️ missing — required on each distribution")",
  "  URL:     \(.url // "❌ MISSING")"
' metadata.json

# Unstable URLs
jq -r '.resources[].url' metadata.json \
  | grep -iE "bit\.ly|tinyurl|goo\.gl|google\.com/spreadsheets|dropbox|drive\.google|onedrive" \
  && echo "⚠️ MAJOR: Unstable resource URL — use permanent institutional hosting"
```

### 5c. Profile-specific additional fields

After baseline, apply profile-specific checks. See `references/dcat-ap-profiles.md`.

**Fields that differ across profiles**:

| Field | DCAT-AP 2.x | IT | DE | FR | BE | NL |
|-------|:-----------:|:--:|:--:|:--:|:--:|:--:|
| `dct:identifier` | R | **M** | **M** | R | **M** | **M** |
| `dcatapit:datasetHolder` | — | **M** | — | — | — | — |
| `dct:rightsHolder` | O | — | R | — | R | — |
| `dct:spatial` | R | R | R | R | R | **M** |
| `dct:conformsTo` | O | R | O | O | O | R |
| `dct:provenance` | O | — | — | — | O | R |
| Multilingual | — | it+en | de | fr+en | nl+fr+de | nl+en |

---

## Phase 6: Consistency & Cross-Validation *(portal datasets only)*

```bash
# Declared encoding vs actual
DECLARED_ENC=$(jq -r '.extras[]? | select(.key=="encoding") | .value' metadata.json 2>/dev/null)
ACTUAL_ENC=$(file -bi "$CSV" | sed 's/.*charset=//')
[ -n "$DECLARED_ENC" ] && [ "$DECLARED_ENC" != "$ACTUAL_ENC" ] \
  && echo "⚠️ MAJOR: Declared encoding ($DECLARED_ENC) ≠ actual ($ACTUAL_ENC)"

# Temporal coverage vs actual data
TC=$(jq -r '.extras[]? | select(.key=="temporal_coverage") | .value' metadata.json 2>/dev/null)
[ -n "$TC" ] && echo "Declared temporal coverage: $TC — verify against MIN/MAX of date column"

# Update frequency vs last modification
FREQ=$(jq -r '.extras[]? | select(.key=="frequency" or .key=="accrualPeriodicity") | .value' \
  metadata.json 2>/dev/null)
MOD=$(jq -r '.extras[]? | select(.key=="modified") | .value' metadata.json 2>/dev/null)
echo "Frequency: ${FREQ:-?} | Last modified: ${MOD:-?} — verify consistency"

# Resource accessibility count
TOTAL=$(jq '.resources | length' metadata.json)
OK=0
for URL in $(jq -r '.resources[].url' metadata.json); do
  CODE=$(curl -sIL -o /dev/null -w "%{http_code}" --max-time 10 "$URL")
  [ "$CODE" -eq 200 ] && OK=$((OK+1)) || echo "⚠️ Not accessible (HTTP $CODE): $URL"
done
echo "Resources accessible: $OK/$TOTAL"
```

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

## Scoring Guide

| Dimension | Max | Deductions |
|-----------|-----|------------|
| **Accessibility** | 20 | −20 any 404; −5 broken URL; −5 unstable URL (cloud/shortlink) |
| **Metadata completeness** | 20 | −4 per missing mandatory field; −2 per missing recommended field |
| **File format** | 15 | −10 non-UTF-8; −5 BOM; −3 CRLF; −3 non-standard separator |
| **Data structure** | 20 | −5 wide format; −5 duplicate headers; −5 aggregate rows mixed; −3 bad column names |
| **Content quality** | 25 | −5 non-dot decimal; −5 non-ISO dates; −5 >5% nulls in key cols; −3 units in cells; −3 placeholder values; −4 missing/invalid reference codes |

**Local CSV only**: score on 60 (accessibility + metadata excluded), normalize to /100.

---

## Severity Levels

| Level | Definition | Example |
|-------|------------|---------|
| **⛔ Blocker** | Cannot use the data at all | File empty, HTTP 404, cannot parse |
| **⚠️ Major** | Usable with effort or risk of errors | Comma decimals, non-ISO dates, missing license |
| **ℹ️ Minor** | Convention issue, low impact | CRLF endings, spaces in column names |

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

## Automated Scripts

Installable Python package in `scripts/` — runs all mechanical checks via DuckDB:

```bash
# Install (once)
uv tool install ./scripts
# or: uvx --from git+https://github.com/... odq-csv ...

# CSV file (phases 0–4)
odq-csv data.csv
odq-csv data.csv --output-json report.json --output-md report.md

# CKAN portal dataset (phases 5–6 + optional CSV)
odq-ckan https://dati.gov.it/opendata DATASET-ID
odq-ckan https://dati.gov.it/opendata DATASET-ID --download

# Exit codes: 0=OK, 1=major issues, 2=blocker
```

See `scripts/README.md` for full documentation.
