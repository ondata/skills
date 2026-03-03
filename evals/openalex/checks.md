# Deterministic Checks — openalex

## Trigger checks

- [x] Skill activates on all `should_trigger=true` prompts — test-01 through test-05 verified
- [x] Skill does NOT activate on `should_trigger=false` prompts — test-06, test-07, test-08 verified

## Process checks

- [x] Uses `curl` with `--data-urlencode` for all query parameters (not manual URL concatenation)
- [x] Includes `api_key` as a query parameter
- [x] Uses `jq` to parse and format the API response
- [x] Defines an entity endpoint (`works`, `authors`, `sources`, etc.) before building the query
- [x] Uses `select=` to restrict the payload to needed fields — root-level fields only confirmed

## Output checks

- [x] Results are printed in a readable format (not raw JSON blob)
- [x] Output includes at least title and year for each result — fixed after adding Output Format section to SKILL.md; re-verified with `display_name` shown correctly
- [x] For PDF download: file is saved locally with a meaningful name

## Pitfall checks

- [x] Does NOT use `sort=relevance_score` without a `search=` parameter — used `sort=cited_by_count:desc`
- [x] Does NOT use nested field paths in `select=` — confirmed: `open_access` in select, `.open_access.is_oa` only in jq
- [x] For PDF download: follows the fallback chain in order (`.content_urls.pdf` → `.best_oa_location.pdf_url` → `.primary_location.pdf_url` → first non-null `.locations[].pdf_url`)
- [x] Handles missing PDF gracefully — exit code 2 returned, no crash

## Synthetic-data pitfall checks (test-09 – test-28)

- [ ] test-09/test-27: does NOT use `sort=relevance_score:desc` without a `search=` parameter
- [ ] test-10/test-24: uses `filter=title.search:"..."` (not `search=`) when user asks for title-level match
- [ ] test-11: `title.search` placed inside `filter=`, not as a standalone parameter
- [ ] test-12/test-23: resolves author name to OpenAlex ID before filtering (two-step lookup)
- [ ] test-13: resolves both author names in one batch, not two sequential calls
- [ ] test-14: uses `open_access` in `select=`, extracts `.open_access.is_oa` only in `jq`
- [ ] test-16: includes `api_key` when downloading from `content.openalex.org`
- [ ] test-17/test-28: uses pipe-separated filter for batch ID lookup (not sequential calls)
- [ ] test-18: uses `per-page=200` (not default 25) when user asks for the full list
- [ ] test-19: uses `group_by=publication_year` correctly; no nested field in `select=`
- [ ] test-20: uses `// ""` null guard for `doi` field in `@csv` export
- [ ] test-21: resolves journal name to source ID before filtering
- [ ] test-22: writes `curl` on a single line (no multi-line `\` continuation)
- [ ] test-25: completes full multi-step flow — search → pick one result → download PDF
- [ ] test-26: uses `group_by=publication_year` with `per-page=200`

## Notes

- `search=` (full-text) used instead of `title.search=` in some runs — results were relevant, acceptable behavior
- `@tsv` output format followed from Output Format section — confirmed working
