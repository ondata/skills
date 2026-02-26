# Deterministic Checks — open-data-quality

List the concrete, verifiable behaviors to check after each run.
These do not require code — they describe what to look for.

## Trigger checks

- [ ] Skill activates on all `should_trigger=true` prompts
- [ ] Skill does NOT activate on `should_trigger=false` prompts

## Process checks

- [ ] Agent runs `odq-csv` for local CSV validation
- [ ] Agent runs `odq-ckan` when a portal URL and dataset ID are provided
- [ ] Agent uses `uvx --from git+...` (no install step needed)
- [ ] Agent adds `--download` to `odq-ckan` when CSV validation is also requested
- [ ] Agent skips `odq-ckan` when only a local CSV is provided

## Output checks

- [ ] Terminal output includes the score box with Source, Profile, Date, Score
- [ ] Score breakdown shows 3 dimensions for CSV-only (format, structure, content) summing to /60, normalized to /100
- [ ] Score breakdown shows 5 dimensions for CKAN mode (accessibility, metadata, format, structure, content) summing to /100
- [ ] JSON report contains keys: source, profile, mode, score, score_raw, findings, dimensions
- [ ] Exit code is 0 (no issues), 1 (major), or 2 (blocker) matching the findings

## Pitfall checks

- [ ] Agent does not confuse `odq-csv` (local file) with `odq-ckan` (portal metadata)
- [ ] Agent does not fabricate quality scores without actually running the tool
- [ ] Agent interprets severity levels correctly: BLOCKER > MAJOR > MINOR
- [ ] Agent does not attempt to fix the data — only reports findings
