# OpenAlex Query Recipes

All examples assume:

```bash
export OPENALEX_API_KEY='...'
```

## 1) Title search (focused)

Use `title.search` instead of `search=` when the topic must appear in the title.
`search=` does full-text matching and often returns loosely related results.
Note: `.search` filters go inside `filter=`, never as standalone parameters.

```bash
curl -sS --get 'https://api.openalex.org/works' --data-urlencode 'filter=title.search:"open government data",type:article,from_publication_date:2023-01-01' --data-urlencode 'sort=cited_by_count:desc' --data-urlencode 'per-page=10' --data-urlencode 'select=display_name,publication_year,cited_by_count,doi' --data-urlencode "api_key=$OPENALEX_API_KEY" | jq '.results[] | {title:.display_name, year:.publication_year, cited:.cited_by_count}'
```

## 2) Topic search + structured filter

```bash
curl -sS --get 'https://api.openalex.org/works' --data-urlencode 'search=("data quality assessment" OR "data quality metrics") AND "open government data"' --data-urlencode 'filter=type:article,from_publication_date:2023-01-01,to_publication_date:2026-02-14' --data-urlencode 'sort=relevance_score:desc' --data-urlencode 'per-page=20' --data-urlencode 'select=id,display_name,publication_year,relevance_score,cited_by_count,doi' --data-urlencode "api_key=$OPENALEX_API_KEY"
```

## 2) Titles only

```bash
... | jq -r '.results[] | "\(.publication_year) - \(.display_name)"'
```

## 3) Most cited in range

```bash
curl -sS --get 'https://api.openalex.org/works' --data-urlencode 'search="open government data"' --data-urlencode 'filter=type:article,from_publication_date:2023-01-01' --data-urlencode 'sort=cited_by_count:desc' --data-urlencode 'per-page=10' --data-urlencode 'select=id,display_name,publication_year,cited_by_count,doi' --data-urlencode "api_key=$OPENALEX_API_KEY" | jq '.results[] | {title:.display_name, cited_by:.cited_by_count, doi}'
```

## 4) Cursor pagination

```bash
FIRST=$(curl -sS --get 'https://api.openalex.org/works' --data-urlencode 'filter=publication_year:2024' --data-urlencode 'per-page=100' --data-urlencode 'cursor=*' --data-urlencode "api_key=$OPENALEX_API_KEY")

CURSOR=$(echo "$FIRST" | jq -r '.meta.next_cursor')
echo "$FIRST" | jq '.meta'

curl -sS --get 'https://api.openalex.org/works' --data-urlencode 'filter=publication_year:2024' --data-urlencode 'per-page=100' --data-urlencode "cursor=$CURSOR" --data-urlencode "api_key=$OPENALEX_API_KEY"
```

## 5) Availability of PDF

```bash
WID='W4386028661'
curl -sS "https://api.openalex.org/works/$WID?api_key=$OPENALEX_API_KEY" | jq '{id, has_content, content_urls, best_pdf:.best_oa_location.pdf_url}'
```

## 6) Export results to CSV

Use `jq` with `@csv` to write a header + data rows in one pass:

```bash
curl -sS --get 'https://api.openalex.org/works' --data-urlencode 'filter=title.search:"open government data",from_publication_date:2023-01-01' --data-urlencode 'sort=cited_by_count:desc' --data-urlencode 'per-page=20' --data-urlencode 'select=display_name,publication_year,cited_by_count,doi' --data-urlencode "api_key=$OPENALEX_API_KEY" | jq -r '["title","year","cited_by","doi"], (.results[] | [.display_name, .publication_year, .cited_by_count, (.doi // "")]) | @csv' > results.csv
```

Add `open_access` to `select=` and include the OA flag in the CSV:

```bash
curl -sS --get 'https://api.openalex.org/works' --data-urlencode 'filter=title.search:"open government data",from_publication_date:2023-01-01' --data-urlencode 'sort=cited_by_count:desc' --data-urlencode 'per-page=20' --data-urlencode 'select=display_name,publication_year,cited_by_count,doi,open_access,best_oa_location' --data-urlencode "api_key=$OPENALEX_API_KEY" | jq -r '["title","year","cited_by","doi","is_oa","pdf_url"], (.results[] | [.display_name, .publication_year, .cited_by_count, (.doi // ""), .open_access.is_oa, (.best_oa_location.pdf_url // "")]) | @csv' > results.csv
```

## 7) Europe PMC fallback when OpenAlex has no pdf_url

Some OA works have no `pdf_url` in any OpenAlex location record (script exits with code 2).
If the work is indexed in Europe PMC, the PDF is still reachable directly:

```bash
WID='W2741809807'
META=$(curl -sS "https://api.openalex.org/works/$WID?api_key=$OPENALEX_API_KEY")

# Extract Europe PMC ID from external_ids
PMCID=$(echo "$META" | jq -r '.ids.pmcid // empty' | sed 's|https://www.ncbi.nlm.nih.gov/pmc/articles/||;s|/||')

if [ -n "$PMCID" ]; then
  PDF_URL="https://europepmc.org/backend/ptpmcrender.fcgi?accid=$PMCID&blobtype=pdf"
  echo "Fallback PDF: $PDF_URL"
  curl -sS -L -o "${PMCID}.pdf" "$PDF_URL"
fi
```

**When to use:** after `openalex_download_pdf.sh` returns exit code 2 and the work is Open Access.
Check `open_access.is_oa` and `ids.pmcid` in the metadata before attempting this fallback.

## 8) Field-scoped search plus a structured filter

The narrow-but-readable recipe: search the abstract instead of the title, and scope by the
country of the authors' institutions instead of hoping the country is named in the text.
Produces a result set small enough to read in full, so nothing depends on ranking.

```bash
curl -sS --get 'https://api.openalex.org/works' --data-urlencode 'filter=title_and_abstract.search:<terms>,authorships.institutions.country_code:it,from_publication_date:2024-09-01,type:article' --data-urlencode 'per-page=200' --data-urlencode 'select=display_name,publication_year,doi' --data-urlencode "api_key=$OPENALEX_API_KEY" | jq -r '.results[] | "\(.publication_year) - \(.display_name)"'
```

`institutions.country_code` and `authorships.institutions.country_code` are the same filter
(identical counts). Run the recipe several times with complementary terms rather than once
with a long `OR` list: each pass stays readable, and no single phrasing has to be exhaustive.

## 9) Known-item recall test

Before trusting a survey, check that a work you already know is in the answer set, and where
it ranks. A low rank in a long list means the triage will miss it.

```bash
DOI='https://doi.org/10.XXXX/YYY'
curl -sS --get 'https://api.openalex.org/works' --data-urlencode 'search=<your query>' --data-urlencode 'filter=type:article,from_publication_date:2024-09-01' --data-urlencode 'per-page=200' --data-urlencode 'select=display_name,doi' --data-urlencode "api_key=$OPENALEX_API_KEY" > r.json
jq -r --arg d "$DOI" '(.results | map(.doi) | index($d)) as $i | if $i then "found at rank \($i+1) of \(.results|length) (total \(.meta.count))" else "NOT in the first \(.results|length) of \(.meta.count)" end' r.json
```

Check the topics too when a query underperforms: OpenAlex may file two works on the same
research question under unrelated topics, so filtering by the topic of one known paper
silently excludes the other.

```bash
curl -sS "https://api.openalex.org/works/$DOI?select=id,topics&api_key=$OPENALEX_API_KEY" | jq -r '.topics[] | "\(.id) \(.display_name) | \(.field.display_name)"'
```

## 10) Semantic search, with its filter whitelist

```bash
curl -sS --get 'https://api.openalex.org/works' --data-urlencode 'search.semantic=<a sentence, an abstract, a grant aim>' --data-urlencode 'filter=publication_year:2025,type:article' --data-urlencode 'per-page=50' --data-urlencode 'select=display_name,publication_year,doi' --data-urlencode "api_key=$OPENALEX_API_KEY" | jq -r '.results[] | "\(.publication_year) - \(.display_name)"'
```

Use `publication_year`, not `from_publication_date`: the latter is rejected, and the error
message lists the filters semantic search does accept. Max 50 results, max 2.000 characters
of input, 1 request per second. Long queries can return `query_timeout` (not charged).
