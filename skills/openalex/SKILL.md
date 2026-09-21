---
name: openalex
description: Query OpenAlex API from the command line with curl and jq for publication discovery, filtering, sorting, pagination, and PDF availability checks. Use when searching scholarly works/authors/sources, building or debugging OpenAlex queries, extracting results, or downloading available PDFs using OPENALEX_API_KEY.
compatibility: Requires curl, jq, bash, OPENALEX_API_KEY environment variable, and internet access.
license: CC BY-SA 4.0 (Creative Commons Attribution-ShareAlike 4.0 International)
metadata:
  version: "0.2"
  author: "Andrea Borruso <aborruso@gmail.com>"
  tags: [api, research, scholarly, bibliometrics, open-access, curl, jq, pdf]
---

# OpenAlex

Use this skill to run reliable OpenAlex API workflows from shell.

> **IMPORTANT:** Always write `curl` commands on a **single line**. Multi-line `\` continuation breaks argument parsing in agent environments and will cause errors.

> **SECURITY:** Never expose the actual value of `OPENALEX_API_KEY` anywhere — not in text responses, not in echoed commands, not in logs. Always reference it as `$OPENALEX_API_KEY`. If the key appears in any output, stop immediately and do not repeat it.

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

   To verify it is set **without printing the value**:

```bash
[[ -n "${OPENALEX_API_KEY:-}" ]] && echo "key is set" || echo "ERROR: OPENALEX_API_KEY not set"
```

2. Run list query (works):

```bash
curl -sS --get 'https://api.openalex.org/works' --data-urlencode 'search="data quality" AND "open government data"' --data-urlencode 'filter=type:article,from_publication_date:2023-01-01' --data-urlencode 'sort=relevance_score:desc' --data-urlencode 'per-page=200' --data-urlencode 'select=display_name,publication_year,cited_by_count,doi' --data-urlencode "api_key=$OPENALEX_API_KEY" | jq '.results[] | {title:.display_name, year:.publication_year, cited_by:.cited_by_count, doi}'
```

## Workflow

1. Define entity endpoint (`works`, `authors`, `sources`, etc.).
2. Build a `search` block with boolean logic (`AND`, `OR`, `NOT`, quotes, parentheses).
3. Add structured `filter` constraints (type/date/language/OA/citation fields).
4. Restrict output with `select` (root-level fields only).
5. Page results with `page` or `cursor=*`.
6. Extract fields via `jq` and save/transform as needed.

## Iterative Validation Workflow

Use this when building or debugging non-trivial queries.

1. Start with a toy query (`per-page=5` or `per-page=10`) and minimal `select=`.
2. Manually inspect 5-10 records for relevance and field quality (`display_name`, year, DOI).
3. Compare a baseline and a variant before scaling:
   - baseline: `filter=title.search:"..."`
   - variant: `search=...` with same filters
4. Tune one parameter at a time (`search`, `filter`, `sort`, `per-page`, pagination mode).
5. Scale only after validation (`per-page=200`, then `cursor=*` for deep pagination).
6. Log each run: command, key parameters, result count, and quick notes.
7. **Known-item recall test.** Before trusting a survey, take one work you already know belongs in the answer, look it up by DOI to get its OpenAlex ID, then check whether your query returns it and at what rank:

```bash
curl -sS --get 'https://api.openalex.org/works' --data-urlencode 'search=...' --data-urlencode 'filter=...' --data-urlencode 'per-page=200' --data-urlencode 'select=display_name,doi' --data-urlencode "api_key=$OPENALEX_API_KEY" > r.json; jq -r '.results | to_entries[] | select(.value.doi=="https://doi.org/10.XXXX/YYY") | "rank \(.key+1)"' r.json
```

Rank far down a long result list is the failure this catches: the query did return the work, but no human reading the top of the list would have seen it. That is a triage problem, not a query problem, and the fix is a narrower filter that makes the whole set readable - not a different search string.

Avoid jumping directly from a paper/spec to a full extraction script without this short validation loop.

## Query Blocks

- `title.search=`: searches only in the title — use this by default for focused results. Must be passed inside `filter=`, not as a standalone parameter: `filter=title.search:"your query"`.
- `search=`: full-text search across the entire document — use only when title-only matching is too restrictive.
- `search.exact=`: like `search=` but without stemming.
- `search.semantic=`: semantic/conceptual search ($0.001/request; requires API key). See "Semantic search".
- `corpus=`: `core` (default, curated ~300M works) or `all` (adds datasets and repository records). Measured on `publication_year:2024`: 10.8M works with `core`, 28.0M with `all`. Never compare counts taken under different `corpus` values.
- `filter=`: exact/structured constraints; comma means AND.
- `sort=`: `relevance_score:desc`, `cited_by_count:desc`, `publication_date:desc`, etc.
- `per-page=`: 1..200. **Default is 25 — always set `per-page=200` for bulk queries (8× fewer API calls).**
- `page=`: page number for standard pagination.
- `cursor=*`: deep pagination beyond first 10k records.
- `select=`: reduce payload; nested paths are not allowed in `select`.
- `group_by=`: aggregate results by a field (e.g. `group_by=publication_year`, `group_by=topics.id`).
- `sample=`: random sample of N results (e.g. `sample=20`). Add `seed=42` for reproducibility.

## Field-Scoped Search

`search=` covers title, abstract and fulltext together. To search one field, append `.search` to the field name **inside `filter=`** — these are not standalone parameters:

| Filter | Searches | Hits for `heatwave`, 2025 |
|---|---|---|
| `title.search` | title only | 1.901 |
| `title_and_abstract.search` | title and abstract | 5.102 |
| `abstract.search` | abstract only | - |
| `fulltext.search` | title, abstract and fulltext (same as `search=`) | 17.192 |
| `raw_author_name.search` | the byline as published | - |

Title-only is the narrowest and misses any work whose subject is not in the title; `fulltext.search` and `search=` are the noisiest. `title_and_abstract.search` (or `abstract.search`) is usually the useful middle, especially combined with a structured filter such as `authorships.institutions.country_code` to scope by country without relying on the country name appearing in the text.

**Deprecation:** OpenAlex marks the whole `filter=field.search:` syntax as deprecated and recommends the `search` parameter instead. All of these still work (counts above measured 19 September 2026), and there is no `search` parameter equivalent for scoping to a single field, so they remain the tool for field-scoped queries - just expect them to change. `default.search` is a deprecated alias of `fulltext.search`. `raw_author_name.search` is the one the docs state has no replacement.

## Search Syntax

Applies to the `search=` parameter:

- Boolean `AND`, `OR`, `NOT` in uppercase, with parentheses; words with no operator are treated as `AND`.
- Double quotes for phrases: `search="fierce creatures"`.
- Proximity: `search="climate change"~5` matches the two words within 5 positions.
- Wildcards: `machin*`, `wom?n`. At least 3 characters before the wildcard; leading wildcards are not supported.
- Fuzzy: `machin~1` allows up to N character edits (N is 0, 1 or 2); at least 3 characters before the `~`.
- Stemming and stop-word removal are on by default (`possums` matches `possum`). Use `search.exact=` to turn stemming off.
- Only one search parameter per request: `search`, `search.exact` or `search.semantic`.

**URL length limit.** The whole request URL is capped at about 4 KB, which a long Boolean `OR` list can exceed - the API answers `400` with `"error": "Request URL too long"`. Split the `OR` list into chunks, request each, and take the union of the IDs client-side: `(X AND (a OR b OR c))` equals `(X AND (a OR b)) union (X AND (c))`. Each chunk is billed separately; splitting does not reduce cost and does not lose results.

## Semantic Search

Use `search.semantic=` to match by meaning, and above all when the input is long - an abstract, a grant aim, a paragraph. It embeds title and abstract of every work and ranks by cosine similarity.

| Constraint | Value |
|---|---|
| Max input length | 2.000 characters (longer is truncated) |
| Max results | 50 per query |
| Rate limit | 1 request per second |

Filters behave differently here. The docs say most filters work and name only `last_known_institutions.country_code` and `cited_by_count` as unsupported, but the API refuses more than that: `from_publication_date` is rejected with a message listing the whitelist it does accept - `author.id`, `authorships.author.id`, `authorships.institutions.id`, `authorships.institutions.lineage`, `funders.id`, `has_abstract`, `has_fulltext`, `institution.id`, `institutions.id`, `is_oa`, `is_retracted`, `language`, `open_access.is_oa`, `primary_location.license`, `primary_location.source.id`, `publication_year`, `type`. Read the error message rather than the docs: it is the live list. Use `publication_year` to bound the period.

Long queries can also return `"reason": "query_timeout"` - the response says you were not charged. Shorten the query and retry.

**What semantic search does not do.** It will not rescue a recall gap on its own. Tested against a known target - a paper on urban tree cover and heatwave mortality in Italian cities - `search.semantic=heatwave mortality Italy municipal data` did not return it in the top 25, with or without a year filter; it surfaced only when the query itself named "urban trees", which means already knowing the answer. Treat it as a way to find neighbours of a concept you can already phrase, not as a safety net.

## Filter Syntax

Filters are comma-separated AND conditions. Within a single attribute:

| Logic | Syntax | Example |
|-------|--------|---------|
| AND (comma) | `filter=a:x,b:y` | `filter=type:article,is_oa:true` |
| OR (pipe) | `filter=type:article\|book` | multiple values for same field |
| NOT (exclamation) | `filter=type:!journal-article` | negation |
| Greater than | `filter=cited_by_count:>100` | comparison |
| Less than | `filter=publication_year:<2020` | comparison |
| Range | `filter=publication_year:2020-2023` | inclusive range |

## Batch Lookup

Combine up to **50 IDs in one request** using the pipe operator — avoid sequential calls:

```bash
# Batch DOI lookup (up to 50 per request)
curl -sS --get 'https://api.openalex.org/works' --data-urlencode 'filter=doi:https://doi.org/10.1/abc|https://doi.org/10.2/def' --data-urlencode 'per-page=50' --data-urlencode "api_key=$OPENALEX_API_KEY" | jq '.results[] | {title:.display_name, doi}'
```

## Two-Step Entity Lookup

Names are ambiguous; always resolve to an OpenAlex ID first, then filter.

**Step 1 — find the entity ID:**

```bash
curl -sS --get 'https://api.openalex.org/authors' --data-urlencode 'search=Heather Piwowar' --data-urlencode 'per-page=5' --data-urlencode "api_key=$OPENALEX_API_KEY" | jq '.results[] | {id, display_name}'
```

**Step 2 — use the ID in a filter:**

```bash
curl -sS --get 'https://api.openalex.org/works' --data-urlencode 'filter=authorships.author.id:A5023888391' --data-urlencode 'per-page=200' --data-urlencode 'select=id,display_name,publication_year,cited_by_count' --data-urlencode "api_key=$OPENALEX_API_KEY" | jq '.results[] | {title:.display_name, year:.publication_year}'
```

Applies to: authors (`authorships.author.id`), institutions (`authorships.institutions.id`), sources/journals (`primary_location.source.id`). External IDs are also accepted: ORCID, ROR, ISSN, DOI.

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

## Error Handling

Implement exponential backoff on 403 (rate limit) and 500 (server error):

```
attempt 1 → wait 1s → attempt 2 → wait 2s → attempt 3 → wait 4s → attempt 4 → wait 8s
```

HTTP codes:
- `200` — success
- `400` — invalid parameter or filter syntax; fix the query. The `message` field is the most reliable reference in this API: it lists the valid parameters, or the filters a given mode accepts. Read it before consulting the docs. Two specific cases: `"Request URL too long"` (split the Boolean query) and `"reason": "query_timeout"` on semantic search (not charged; shorten and retry)
- `403` — rate limit exceeded; back off and retry
- `404` — entity not found
- `500` — temporary server error; retry with backoff

## Endpoint Costs

With the free $1/day budget:

| Request type | Cost | Daily limit |
|---|---|---|
| Singleton (`/works/W123`) | free | unlimited |
| List / filter | $0.0001 | ~10,000 requests |
| Search (full-text or semantic) | $0.001 | ~1,000 requests |
| PDF download (`content.openalex.org`) | $0.01 | ~100 downloads |

A `.search` filter is billed as a search, not as a list+filter: `filter=title_and_abstract.search:...` returns `cost_usd` 0.001, the same as `search=`. Only the plain structured filters cost 0.0001.

Every list response carries `meta.cost_usd`, what that single call actually cost. Use it instead of estimating: `jq '.meta.cost_usd'`.

Use `select=` and `per-page=200` to minimize request count.

## Common Pitfalls

- Do not use `.id` or `.doi` as the title field in jq output — `.id` is an OpenAlex URL, `.doi` is a DOI URL; always use `.display_name` for human-readable titles.
- Do not include `id` in `select=` unless you need the OpenAlex URL for follow-up lookups — it is a URL, not a title, and confuses output.
- Do not sort by `relevance_score` without a search query.
- Do not use nested fields in `select` (example: use `open_access`, then parse `.open_access.is_oa` with `jq`).
- Do not filter by entity names directly — use the two-step entity lookup to get the ID first.
- Do not use sequential calls for batch ID lookups — batch up to 50 with the pipe operator.
- Do not use `per-page=25` (default) for bulk extraction — always set `per-page=200`.
- Expect some records to have no downloadable PDF.
- `search=` searches full text and can return loosely related results. Use `title.search=` when the topic must appear in the title.
- Always write `curl` commands on a single line — multi-line `\` continuation breaks argument parsing in agent environments.
- `title.search` is NOT a valid standalone parameter — always pass it inside `filter=`: `filter=title.search:"your query"`. Same for `abstract.search`, `title_and_abstract.search` and `fulltext.search`. Passing one standalone returns a `400` whose message lists every valid parameter: `apc_sum, api-key, api_key, cited_by_count_sum, corpus, cursor, data-version, data_version, filter, format, group-by, group-bys, group_by, group_bys, include-xpac, include_xpac, mailto, page, per-page, per_page, q, sample, search, seed, select, sort, warm` (`search.exact` and `search.semantic` are absent from that list but work).
- Do not trust the docs on page size: the reference table says `per_page` maxes at 100, but the API accepts 200 and its own `400` message says "per-page parameter must be between 1 and 200". `per-page` and `per_page` are both accepted.
- Do not search only the title when the work might be about your subject without naming it — a paper can use Italian mortality data with neither "Italy" nor "mortality" in the title. Widen to `title_and_abstract.search` or add a structured filter.
- Always include `api_key=$OPENALEX_API_KEY` in every request.
- **Never expose the actual key value** — not in text output, not in echoed commands, not in logs, and not in any other form. Always use the variable reference `$OPENALEX_API_KEY`.
  - To verify it is set: `[[ -n "${OPENALEX_API_KEY:-}" ]] && echo "key is set" || echo "ERROR: OPENALEX_API_KEY not set"`.

## Resources

- Query recipes and jq snippets: `references/query-recipes.md`
- Generic query helper: `scripts/openalex_query.sh`
- PDF downloader for work IDs: `scripts/openalex_download_pdf.sh`
