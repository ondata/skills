# OpenAlex Query Recipes

All examples assume:

```bash
export OPENALEX_API_KEY='...'
```

## 1) Topic search + structured filter

```bash
curl -sS --get 'https://api.openalex.org/works' \
  --data-urlencode 'search=("data quality assessment" OR "data quality metrics") AND "open government data"' \
  --data-urlencode 'filter=type:article,from_publication_date:2023-01-01,to_publication_date:2026-02-14' \
  --data-urlencode 'sort=relevance_score:desc' \
  --data-urlencode 'per-page=20' \
  --data-urlencode 'select=id,display_name,publication_year,relevance_score,cited_by_count,doi' \
  --data-urlencode "api_key=$OPENALEX_API_KEY"
```

## 2) Titles only

```bash
... | jq -r '.results[] | "\(.publication_year) - \(.display_name)"'
```

## 3) Most cited in range

```bash
curl -sS --get 'https://api.openalex.org/works' \
  --data-urlencode 'search="open government data"' \
  --data-urlencode 'filter=type:article,from_publication_date:2023-01-01' \
  --data-urlencode 'sort=cited_by_count:desc' \
  --data-urlencode 'per-page=10' \
  --data-urlencode 'select=id,display_name,publication_year,cited_by_count,doi' \
  --data-urlencode "api_key=$OPENALEX_API_KEY" \
| jq '.results[] | {title:.display_name, cited_by:.cited_by_count, doi}'
```

## 4) Cursor pagination

```bash
FIRST=$(curl -sS --get 'https://api.openalex.org/works' \
  --data-urlencode 'filter=publication_year:2024' \
  --data-urlencode 'per-page=100' \
  --data-urlencode 'cursor=*' \
  --data-urlencode "api_key=$OPENALEX_API_KEY")

CURSOR=$(echo "$FIRST" | jq -r '.meta.next_cursor')
echo "$FIRST" | jq '.meta'

curl -sS --get 'https://api.openalex.org/works' \
  --data-urlencode 'filter=publication_year:2024' \
  --data-urlencode 'per-page=100' \
  --data-urlencode "cursor=$CURSOR" \
  --data-urlencode "api_key=$OPENALEX_API_KEY"
```

## 5) Availability of PDF

```bash
WID='W4386028661'
curl -sS "https://api.openalex.org/works/$WID?api_key=$OPENALEX_API_KEY" \
| jq '{id, has_content, content_urls, best_pdf:.best_oa_location.pdf_url}'
```
