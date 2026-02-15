# Contributing

## Git workflow

This project uses **GitHub Flow**: `main` is always stable; all work happens on branches and merges via pull request.

### Rules

- Never commit directly to `main`.
- One branch per contribution (skill, fix, eval, doc).
- Open a pull request for every change; merge only after review.

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

1. Create `skills/<skill-name>/SKILL.md` with required frontmatter (`name`, `description`).
2. Add optional `scripts/`, `references/`, `assets/` as needed.
3. Copy evals template: `cp -r evals/_template/ evals/<skill-name>/` and fill in the three files.
4. Open a PR.

## Frontmatter fields

Required:

```yaml
name: skill-name
description: One-sentence description used for agent trigger matching.
```

Optional:

```yaml
compatibility: Lists runtime dependencies (tools, env vars, internet).
license: CC BY-SA 4.0 (Creative Commons Attribution-ShareAlike 4.0 International)
metadata:
  version: "0.1"
  author: "Name Surname <email@example.com>"
  tags: [tag1, tag2]
```
