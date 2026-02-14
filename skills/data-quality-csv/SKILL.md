---
name: data-quality-csv
description: Analyzes a CSV file for common data quality issues: encoding, separators, date formats, data types, missing values, and structural problems. Use when the user asks to "check data quality", "validate a CSV", "inspect this file", or "what's wrong with this dataset".
---

# Data Quality CSV

## Instructions

When the user provides a CSV file or path, perform a systematic data quality analysis.

### Step 1: Structural check

- Detect encoding (UTF-8, UTF-8 BOM, Latin-1, etc.)
- Detect separator (comma, semicolon, tab, pipe)
- Count rows and columns
- Check for consistent column count across rows
- Flag empty files or files with only a header

### Step 2: Header check

- Verify header row exists
- Flag headers with special characters, leading/trailing spaces, or duplicates
- Flag non-descriptive headers (e.g. `col1`, `field2`)

### Step 3: Content check

For each column:
- Infer data type (text, integer, decimal, date, boolean, mixed)
- Count null/empty values and report percentage
- Flag columns with more than 20% missing values
- Detect common Italian anti-patterns:
  - Dates in DD/MM/YYYY format (should be ISO 8601: YYYY-MM-DD)
  - Decimal comma instead of decimal point (e.g. `1.234,56`)
  - Units embedded in cells (e.g. `100 kg`, `€ 50`)

### Step 4: Report

Produce a structured report with:
- Summary: file size, rows, columns, encoding, separator
- Issues found, grouped by severity:
  - **Blocker** — file cannot be parsed or used
  - **Warning** — data is usable but problematic
  - **Info** — minor issues or suggestions
- Recommended fixes for each issue

## Common Issues

### File cannot be parsed
**Cause:** Wrong encoding or malformed structure.
**Solution:** Try re-opening with UTF-8 or Latin-1 encoding. Check for unclosed quotes.

### Mixed data types in column
**Cause:** Inconsistent data entry.
**Solution:** Identify rows causing the mix and decide on a canonical type.

### Date format not ISO 8601
**Cause:** Dates entered as DD/MM/YYYY.
**Solution:** Convert to YYYY-MM-DD using `datefmt` or equivalent tool.
