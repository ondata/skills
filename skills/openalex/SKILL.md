---
name: openalex
description: Query OpenAlex API from the command line with curl and jq for publication discovery, filtering, sorting, pagination, and PDF availability checks. Use when searching scholarly works/authors/sources, building or debugging OpenAlex queries, extracting results, or downloading available PDFs using OPENALEX_API_KEY.
---

# OpenAlex

Use this skill to run reliable OpenAlex API workflows from shell.

> **IMPORTANT:** Always write `curl` commands on a **single line**. Multi-line `\` continuation breaks argument parsing in agent environments and will cause errors.

## Definition of Done

A task is complete when:

**Results**
- The API returns at least one result (or a clear "no results found" message)
- Each result shows: title (`display_name`), year, citation count
- Output is readable — not a raw JSON blob

**Process**
- `curl` written on a single line
- `api_key` included in every request
- `select=` used to limit returned fields
- `jq` used to format output

**PDF download** (when requested)
- If PDF is available: file saved locally, path printed
- If PDF is not available: clear message, exit code 2, no crash

## Quick Start

1. Export API key:

```bash
export OPENALEX_API_KEY='...'
```

2. Run list query (works):

```bash
curl -sS --get 'https://api.openalex.org/works' --data-urlencode 'search="data quality" AND "open government data"' --data-urlencode 'filter=type:article,from_publication_date:2023-01-01' --data-urlencode 'sort=relevance_score:desc' --data-urlencode 'per-page=20' --data-urlencode 'select=id,display_name,publication_year,cited_by_count,doi' --data-urlencode "api_key=$OPENALEX_API_KEY" | jq '.results[] | {title:.display_name, year:.publication_year, cited_by:.cited_by_count, doi}'
```

## Workflow

1. Define entity endpoint (`works`, `authors`, `sources`, etc.).
2. Build a `search` block with boolean logic (`AND`, `OR`, `NOT`, quotes, parentheses).
3. Add structured `filter` constraints (type/date/language/OA/citation fields).
4. Restrict output with `select` (root-level fields only).
5. Page results with `page` or `cursor=*`.
6. Extract fields via `jq` and save/transform as needed.

## Query Blocks

- `title.search=`: searches only in the title — use this by default for focused results. Must be passed inside `filter=`, not as a standalone parameter: `filter=title.search:"your query"`.
- `search=`: full-text search across the entire document — use only when title-only matching is too restrictive.
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

## Output Format

When displaying results, always show `display_name` as the title — never use `doi` or `id` in its place.

Minimal jq for a results table:

```bash
| jq -r '.results[] | [.display_name, .publication_year, .cited_by_count, .doi] | @tsv'
```

Or as structured objects:

```bash
| jq '.results[] | {title: .display_name, year: .publication_year, cited_by: .cited_by_count, doi}'
```

## CSV Export

To save results as a CSV file, use `jq` with `@csv` and include a header row:

```bash
curl -sS --get 'https://api.openalex.org/works' ... --data-urlencode "api_key=$OPENALEX_API_KEY" | jq -r '["title","year","cited_by","doi"], (.results[] | [.display_name, .publication_year, .cited_by_count, (.doi // "")]) | @csv' > results.csv
```

Rules:
- Use `// ""` for fields that may be null (e.g. `doi`) — `@csv` fails on null values.
- The header array and data array must have the same number of columns.
- Use `-r` (raw output) so `@csv` produces plain text, not JSON strings.

## Common Pitfalls

- Do not sort by `relevance_score` without a search query.
- Do not use nested fields in `select` (example: use `open_access`, then parse `.open_access.is_oa` with `jq`).
- Expect some records to have no downloadable PDF.
- `search=` searches full text and can return loosely related results. Use `title.search=` when the topic must appear in the title.
- Always write `curl` commands on a single line — multi-line `\` continuation breaks argument parsing in agent environments.
- `title.search` is NOT a valid standalone parameter — always pass it inside `filter=`: `filter=title.search:"your query"`.
- Always include `api_key=$OPENALEX_API_KEY` in every request.

## Resources

- Query recipes and jq snippets: `references/query-recipes.md`
- Generic query helper: `scripts/openalex_query.sh`
- PDF downloader for work IDs: `scripts/openalex_download_pdf.sh`
