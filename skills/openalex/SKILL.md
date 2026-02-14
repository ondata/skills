---
name: openalex
description: Query OpenAlex API from the command line with curl and jq for publication discovery, filtering, sorting, pagination, and PDF availability checks. Use when searching scholarly works/authors/sources, building or debugging OpenAlex queries, extracting results, or downloading available PDFs using OPENALEX_API_KEY.
---

# OpenAlex

Use this skill to run reliable OpenAlex API workflows from shell.

## Quick Start

1. Export API key from environment:

```bash
export OPENALEX_API_KEY='...'
```

2. Check quota and auth:

```bash
curl -sS "https://api.openalex.org/rate-limit?api_key=$OPENALEX_API_KEY" | jq
```

3. Run list query (works):

```bash
curl -sS --get 'https://api.openalex.org/works' \
  --data-urlencode 'search="data quality" AND "open government data"' \
  --data-urlencode 'filter=type:article,from_publication_date:2023-01-01' \
  --data-urlencode 'sort=relevance_score:desc' \
  --data-urlencode 'per-page=20' \
  --data-urlencode 'select=id,display_name,publication_year,cited_by_count,doi' \
  --data-urlencode "api_key=$OPENALEX_API_KEY" \
| jq '.results[] | {title:.display_name, year:.publication_year, cited_by:.cited_by_count, doi}'
```

## Workflow

1. Define entity endpoint (`works`, `authors`, `sources`, etc.).
2. Build a `search` block with boolean logic (`AND`, `OR`, `NOT`, quotes, parentheses).
3. Add structured `filter` constraints (type/date/language/OA/citation fields).
4. Restrict output with `select` (root-level fields only).
5. Page results with `page` or `cursor=*`.
6. Extract fields via `jq` and save/transform as needed.

## Query Blocks

- `search=`: full-text relevance search.
- `filter=`: exact/structured constraints; comma means AND.
- `sort=`: `relevance_score:desc`, `cited_by_count:desc`, `publication_date:desc`, etc.
- `per-page=`: 1..200.
- `cursor=*`: deep pagination beyond first 10k records.
- `select=`: reduce payload; nested paths are not allowed in `select`.

## PDF Retrieval

For a work ID:

1. Fetch work metadata.
2. Resolve PDF URL in this order:
   - `.content_urls.pdf`
   - `.best_oa_location.pdf_url`
   - `.primary_location.pdf_url`
   - first non-null `.locations[].pdf_url`
3. Download with `api_key` query parameter when source is `content.openalex.org`.

## Common Pitfalls

- Do not sort by `relevance_score` without a search query.
- Do not use nested fields in `select` (example: use `open_access`, then parse `.open_access.is_oa` with `jq`).
- Expect some records to have no downloadable PDF.

## Resources

- Query recipes and jq snippets: `references/query-recipes.md`
- Generic query helper: `scripts/openalex_query.sh`
- PDF downloader for work IDs: `scripts/openalex_download_pdf.sh`
