# Contributing

## Git workflow

This project uses **GitHub Flow**: `main` is always stable; all work happens on branches and merges via pull request.

### Rules

- Commit directly to `main` only for single-line typo/fact fixes. Everything else goes through a PR.
- One branch per contribution (skill, fix, eval, doc).
- Open a pull request for every change; merge only after review.
- Delete the branch after merge (locally and on remote).

After a PR is merged, delete the branch:

```bash
git checkout main
git branch -d <branch-name>
git push origin --delete <branch-name>
```

### Branch naming

| Prefix | Use |
|--------|-----|
| `add/` | new skill or file |
| `fix/` | bug fix or correction |
| `eval/` | eval work |
| `docs/` | documentation only |

Examples:

```
add/skill-openalex
fix/openalex-frontmatter
eval/openalex-prompts
docs/contributing-guide
```

### Commit messages

Short and imperative, in English:

```
add frontmatter fields to openalex skill
fix broken curl example in query-recipes
```

## Adding a skill

1. Create `skills/<skill-name>/SKILL.md` with required frontmatter (`name`, `description`, `compatibility`, `license`, `metadata`).
2. Add optional `scripts/`, `references/`, `assets/` as needed.
3. Copy evals template: `cp -r evals/_template/ evals/<skill-name>/` and fill in the three files.
4. Open a PR.

### Writing good skill content

Use the [`skill-creator`](https://github.com/anthropics/skills/tree/main/skills/skill-creator)
skill to draft, test, and iterate on new skills. It covers the full loop: draft → run test
prompts → review outputs → improve → optimize the `description` field for triggering accuracy.

When writing the skill body, prioritize these three content dimensions — empirically validated
as the strongest predictors of downstream skill utility (Huang et al. 2026,
[arXiv:2605.23899](https://arxiv.org/abs/2605.23899)):

| Dimension | What it means |
|---|---|
| **Failure Mechanism Encoding** | Name specific failure modes with executable remedies, not generic warnings |
| **Actionable Specificity** | Concrete, executable instructions — not process-level advice like "be careful" |
| **High-Risk Action Blacklist** | Explicit list of actions the agent must never do in this domain |

Note: skill *format* (ordered list, bullets, prose) has no measurable effect on utility —
only the content matters. Optimizing for clarity or completeness without grounding in these
three dimensions does not improve performance and may hurt it.

## Developer notes

### Local development with open-data-quality scripts

When editing Python sources under `skills/open-data-quality/scripts/` from WSL, do **not** use `uvx` from the Windows side — it builds a cached wheel and does not detect WSL source changes.

Use WSL's own `uv` instead:

```bash
wsl -e bash -c "~/.local/bin/uv run --project ./skills/open-data-quality/scripts odq-csv /tmp/data.csv"
wsl -e bash -c "~/.local/bin/uv run --project ./skills/open-data-quality/scripts odq-ckan https://dati.gov.it/opendata DATASET-ID"
```

### Windows encoding (cp1252 terminals)

On Windows terminals that use cp1252, `uvx` may raise `UnicodeEncodeError` if the output contains characters outside ASCII.
Set `PYTHONUTF8=1` before running:

```powershell
# PowerShell
$env:PYTHONUTF8=1; uvx --from git+https://github.com/ondata/open-data-quality odq-csv data.csv

# Command Prompt
set PYTHONUTF8=1 && uvx --from git+https://github.com/ondata/open-data-quality odq-csv data.csv
```

### DuckDB lenient parsing (`strict_mode=false`)

Some valid CSVs (e.g., with quoted newlines in headers, as per RFC 4180) fail DuckDB's default `read_csv_auto`. The validator retries with `strict_mode=false` before declaring a BLOCKER, and propagates the flag to all subsequent queries via the `_lenient` / `_rcsv()` pattern in `csv_validator.py`.

---

## Frontmatter fields

Required:

```yaml
name: skill-name
description: One-sentence description used for agent trigger matching.
compatibility: Lists runtime dependencies (tools, env vars, internet).
license: CC BY-SA 4.0 (Creative Commons Attribution-ShareAlike 4.0 International)
metadata:
  version: "0.1"
  author: "Name Surname <email@example.com>"
  tags: [tag1, tag2]
```
