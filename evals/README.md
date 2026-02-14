# Evals — onData Skills

Evaluation results for each skill in the collection.

## Dashboard

| Skill | Prompts | Last run | Score | Status |
|---|---|---|---|---|
| [openalex](openalex/) | 8 | 2026-02-14 | 78/100 | 🟡 |

## How to add evals for a skill

1. Copy `_template/` into a new folder named after the skill: `evals/<skill-name>/`
2. Fill `prompts.csv` — write 8–10 prompts covering explicit, implicit, contextual invocations and at least 2 negative controls
3. Fill `checks.md` — list the deterministic checks (commands run, files created, output format)
4. Adjust `rubric.schema.json` — add or remove check IDs to match what matters for this skill
5. Run at least 2–3 prompt cases manually and save results in `results/YYYY-MM-DD.json`
6. Update the dashboard table above

No code required for steps 1–4. Domain knowledge matters more than technical skills.

## Result format

Each file in `results/` follows the rubric schema:

```json
{
  "overall_pass": true,
  "score": 85,
  "checks": [
    { "id": "trigger", "pass": true, "notes": "Skill activated on all expected prompts." },
    { "id": "workflow", "pass": true, "notes": "All 6 steps followed." },
    { "id": "pitfalls", "pass": false, "notes": "Once sorted by relevance_score without search." }
  ]
}
```
