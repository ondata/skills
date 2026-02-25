# Common Open Data Anti-patterns

Documented patterns observed in real datasets published on open data portals worldwide.
Each entry includes: problem description, how to detect it, severity, and how to fix it.

Anti-patterns are organized in two sections:
- **Universal** — observed in datasets from any country
- **Locale-specific** — tied to a particular language or administrative system

---

## Universal Anti-patterns

### 1. Date field present as empty string

**Severity**: Major

**What happens**: Metadata field `issued` or `modified` exists as a key but holds `""`.
Many parsers treat an empty string differently from a missing/null value, causing silent failures.
Observed in: IT, ES, PL portals — but the root cause (CKAN export behavior) is universal.

**Detection**:
```bash
for KEY in issued modified; do
  VAL=$(jq -r ".extras[] | select(.key==\"$KEY\") | .value" metadata.json 2>/dev/null)
  [ -z "$VAL" ] && echo "⚠️ $KEY is missing or empty string"
done
```

**Fix (publisher)**: Set the field to an actual ISO 8601 date:
```
issued: "2024-03-15"   ✅
issued: ""              ❌
```

---

### 2. Cloud storage or short URL as resource link

**Severity**: Major

**What happens**: Resource URL points to Google Sheets, Dropbox, OneDrive, or a link shortener.
Problems: link may expire, file may be overwritten without versioning, no stable checksum,
potential auth issues, URL changes if the document is recreated.

**Detection**:
```bash
jq -r '.resources[].url' metadata.json \
  | grep -iE "bit\.ly|tinyurl|goo\.gl|t\.co|google\.com/spreadsheets|dropbox\.com|drive\.google|onedrive\.live"
```

**Fix (publisher)**:
1. Export the file to a static format (CSV, JSON)
2. Upload to your institution's own server or CKAN file store
3. Register the stable URL with `dcat:downloadURL`
4. Add `dcat:byteSize` and optionally `spdx:checksum`

---

### 3. `size: 0` on resources

**Severity**: Minor

**What happens**: Resource metadata shows `"size": 0` — the file exists but size was not
captured at harvest/upload time. Reduces trust and complicates download planning.

**Detection**:
```bash
jq -r '.resources[] | "\(.name): \(.size // "null")"' metadata.json
```

**Fix**: Ensure the CKAN harvester or upload pipeline records `dcat:byteSize`.
For existing resources, update the metadata manually.

---

### 4. License on dataset but missing on distributions

**Severity**: Major (DCAT-AP compliance, all profiles)

**What happens**: Dataset has `license_id` set, but individual resources do not.
DCAT-AP requires `dct:license` on **each distribution**, not only at dataset level.

**Detection**:
```bash
echo "Dataset license: $(jq -r '.license_id // "❌ MISSING"' metadata.json)"
jq -r '.resources[] | "Resource \(.name): \(.license_id // .license // "❌ MISSING")"' metadata.json
```

**Fix**: Add `dct:license` to each resource/distribution record in CKAN.

---

### 5. Description equals title (no real content explanation)

**Severity**: Major

**What happens**: The `notes` / `description` field is the same as the title, or a minor
variation of it. Provides no useful information for discovery or reuse.

**Detection**:
```bash
TITLE=$(jq -r '.title' metadata.json)
NOTES=$(jq -r '.notes // ""' metadata.json)
[ ${#NOTES} -lt 80 ] && echo "⚠️ Description too short (${#NOTES} chars)"
[ "$TITLE" = "$NOTES" ] && echo "⚠️ Description is identical to title"
```

**Fix — a good description should answer**:
- What data is in this dataset? What does each row represent?
- What is the time coverage?
- Who collected it, how, and for what purpose?
- What does each key column mean?
- What units and formats are used?
- Are there known caveats or limitations?

---

### 6. Non-ISO date format in data cells

**Severity**: Major

**What happens**: Date values in the CSV use a locale-specific format rather than ISO 8601.
Common patterns (all problematic):

| Pattern | Common in |
|---------|-----------|
| `DD/MM/YYYY` | Most of Europe (IT, FR, DE, ES, PT, NL, ...) |
| `MM/DD/YYYY` | USA |
| `DD.MM.YYYY` | DE, CH, AT, Scandinavia, RU |
| `YYYY/MM/DD` | Some East Asian datasets |
| `D-MMM-YY` | Older Excel exports everywhere |

**Detection**:
```bash
grep -m5 -oE '[0-9]{1,2}[/\.][0-9]{1,2}[/\.][0-9]{4}' data.csv \
  && echo "⚠️ Non-ISO date format found"
```

**Fix (ETL)**:
```bash
# DuckDB — example for DD/MM/YYYY
duckdb :memory: "
  CREATE TABLE t AS SELECT * FROM read_csv_auto('data.csv');
  SELECT strptime(date_col, '%d/%m/%Y')::DATE as date_iso FROM t;"

# Python
df['date'] = pd.to_datetime(df['date'], dayfirst=True).dt.strftime('%Y-%m-%d')
```

---

### 7. Non-dot decimal separator in numeric columns

**Severity**: Major

**What happens**: Numeric values use a comma as decimal separator (`25,50`, `1.234,56`).
Standard everywhere outside English-speaking countries, but breaks all tools using dot as
default: Python, R, SQL, JavaScript, Excel in non-European locales.

Common locales: IT, DE, FR, ES, PT, PL, RU, most of EU.

**Detection**:
```bash
grep -m5 -oE '[0-9]+,[0-9]+' data.csv && echo "⚠️ Comma decimal separator found"
```

**Fix (ETL)**:
```bash
# Miller (safe: only replaces decimal comma, not thousands separator)
mlr --csv put '
  for (k, v in $*) {
    if (typeof(v) == "string" && v =~ "^[0-9]+,[0-9]+$") {
      $[k] = sub(v, ",", ".")
    }
  }' data.csv

# For thousands+decimal pattern (e.g. "1.234,56" → "1234.56")
sed 's/\([0-9]\)\.\([0-9][0-9][0-9]\),/\1\2./g' data.csv
```

---

### 8. Units embedded in numeric cell values

**Severity**: Major

**What happens**: Values like `"25 kg"`, `"3 km²"`, `"100 EUR"`, `"45%"`.
The column becomes a string instead of a number, making aggregation impossible.

**Detection**:
```bash
grep -m5 -oE '[0-9]+ ?(kg|km|m²|km²|EUR|€|%|\$|£|GBP|ha|MW|GWh|tCO2|tn|t )' data.csv
```

**Fix**: Split into two columns: `value` (numeric) and `unit` (string).
Or: document the unit in the column name or metadata, remove from cell values.

---

### 9. Wide format — time periods as column names

**Severity**: Major (for analysis)

**What happens**: Each year/month/quarter becomes a column instead of a value:
```
region, 2020, 2021, 2022, 2023
Tuscany, 100, 110, 115, 120
```

Should be tidy (long) format:
```
region, year, value
Tuscany, 2020, 100
Tuscany, 2021, 110
```

**Detection**:
```bash
duckdb :memory: "
  SELECT column_name FROM (DESCRIBE SELECT * FROM read_csv_auto('data.csv'))
  WHERE column_name ~ '^(19|20)[0-9]{2}$';"
```

**Fix (ETL)**:
```bash
# DuckDB UNPIVOT
duckdb :memory: "
  CREATE TABLE wide AS SELECT * FROM read_csv_auto('data.csv');
  UNPIVOT wide ON COLUMNS(* EXCLUDE (region)) INTO NAME year VALUE value;"

# Miller
mlr --csv reshape -r '^(19|20)[0-9]{2}$' -o year,value data.csv
```

---

### 10. Aggregate/total rows mixed with observations

**Severity**: Major

**What happens**: Summary rows at the bottom of the file:
```
Palermo, 1234
Catania, 567
TOTAL, 1801    ← aggregate row
```

Breaks `COUNT`, `SUM`, type inference. The word for "total" varies by language.

**Detection**:
```bash
tail -10 data.csv | grep -i \
  "total\|totale\|subtotal\|subtotale\|sum\|somma\|gesamt\|insgesamt\|suma\|total général\|媒体\|合計"
```

**Fix**: Remove aggregate rows before publishing.
```bash
# Remove any row containing the word "total" in any column
mlr --csv filter '!($* =~ "(?i)totale?|subtotale?|gesamt|insgesamt|suma total|grand total")' data.csv
```

---

### 11. Footnote markers in data values

**Severity**: Minor

**What happens**: Excel footnotes leak into exported CSV:
```
Paris, 5000*
Berlin, (1)3200
Madrid, 4100 (*)
```

**Detection**:
```bash
grep -m5 -E '\([0-9]+\)|\(\*\)|[0-9]+\s*\*' data.csv
```

**Fix**: Remove markers programmatically. Document footnote meanings in description or
as a separate `notes` column.

---

### 12. Encoding mismatch (legacy encodings mislabeled as UTF-8)

**Severity**: Blocker or Major

**What happens**: File saved in Windows-1252, ISO-8859-1, or a regional encoding,
but declared or assumed to be UTF-8. Affects any language with accented characters
or non-ASCII scripts: ä, ö, ü (DE), à, è, é (FR/IT), ñ (ES), ç (PT/FR), ø (DK/NO), etc.

**Detection**:
```bash
file -bi data.csv
iconv -f UTF-8 -t UTF-8 data.csv > /dev/null 2>&1 || echo "Not valid UTF-8"
python3 -c "open('data.csv', encoding='utf-8').read()" 2>&1
```

**Fix**:
```bash
# If source encoding is known
iconv -f windows-1252 -t UTF-8 data.csv > data_utf8.csv
iconv -f iso-8859-1  -t UTF-8 data.csv > data_utf8.csv
iconv -f latin9      -t UTF-8 data.csv > data_utf8.csv  # ISO-8859-15, common in FR

# If source encoding is unknown — detect first
python3 -c "
import chardet
with open('data.csv', 'rb') as f:
    print(chardet.detect(f.read(100000)))
"
```

---

## Locale-specific Anti-patterns

### IT — Italian

**IT-1. `modified` in extras with DD-MM-YYYY format**

CKAN portals in Italy sometimes store `modified` as `"25-02-2026"` (not ISO 8601).
This is different from the cell-level date issue above — it's a metadata field.

```bash
jq -r '.extras[] | select(.key=="modified") | .value' metadata.json \
  | grep -E '^[0-9]{2}-[0-9]{2}-[0-9]{4}$' && echo "⚠️ modified not ISO 8601"
```

Fix: always store as `YYYY-MM-DD`.

**IT-2. Province abbreviations without ISTAT numeric codes**

Data uses 2-letter codes (`PA`, `MI`) without the 3-digit ISTAT numeric code.
Creates join ambiguity when merging datasets.

Fix: add `cod_istat_provincia` (`082`, `015`) alongside the abbreviation.
Reference: https://www.istat.it/it/archivio/6789

**IT-3. Municipality codes without leading zeros**

ISTAT codes are 6-digit, but Excel often strips leading zeros: `82053` instead of `082053`.

```bash
duckdb :memory: "
  SELECT cod_comune, LENGTH(cod_comune) as len FROM (SELECT * FROM read_csv_auto('data.csv'))
  WHERE LENGTH(cod_comune::VARCHAR) < 6 LIMIT 5;"
```

Fix: `LPAD(cod_comune::VARCHAR, 6, '0')` in DuckDB / `str.zfill(6)` in Python.

---

### DE — German

**DE-1. Period-thousands + comma-decimal: `1.234,56`**

Both separators used together. Requires two-step conversion:
```bash
# Step 1: remove thousands dots, Step 2: replace decimal comma
sed 's/\([0-9]\)\.\([0-9][0-9][0-9]\),/\1\2./g' data.csv
```

**DE-2. AGS code without leading zeros**

8-digit Gemeindeschlüssel, Excel strips zeros. Fix with `LPAD(..., 8, '0')`.

---

### FR — French

**FR-1. `n.r.` (non renseigné) as placeholder**
Added to the universal placeholder list above, but verify the exact form used.

**FR-2. Accented characters in column names from Excel**
Columns like `Région`, `Âge`, `Données` — problematic in SQL identifiers.
Fix: normalize column names to ASCII before publishing.

---

### General EU

**EU-1. NUTS codes without LAU (municipality) codes**

Regional datasets often provide NUTS2/NUTS3 but omit the finer LAU level.
Flag if the dataset claims municipal granularity but only has NUTS codes.

**EU-2. Administrative boundaries without reference year**

NUTS classifications change (NUTS 2016, NUTS 2021). Always document the reference year.
```
nuts_code_year: "2021"  ✅
```
