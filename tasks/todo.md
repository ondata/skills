# onData Skills Project - Planning

## New skill: writing for Italian PA (Designers Italia writing toolkit) — 2026-07-28

Source: https://docs.italia.it/italia/designers-italia/writing-toolkit/it/bozza/index.html (CC-BY 4.0, repo `italia/writing-toolkit`)

### Plan

- [x] Confirm skill name and scope with user (`scrivi-chiaro-pa`, full scope incl. social/newsletter/images/editorial)
- [x] Create branch `add/scrivi-chiaro-pa`
- [x] Write `skills/scrivi-chiaro-pa/SKILL.md` (English instructions, Italian output/examples)
- [x] Write `references/stile-di-scrittura.md` (style + punctuation/grammar + numbers and dates + formatting)
- [x] Write `references/struttura-e-leggibilita.md` (structure, usability, SEO, accessibility)
- [x] Write `references/tono-di-voce.md` (9 scenarios: user mood → PA response approach)
- [x] Write `references/canali-e-redazione.md` (social, newsletter, images/video, content management)
- [x] Write `references/glossario-parole-pa.md` (single file, two tables: bureaucratese + spelling/capitalization)
- [x] Add attribution note (CC-BY 4.0, Designers Italia) in SKILL.md
- [x] Update LOG.md, open PR
- [ ] Evals battery in `evals/scrivi-chiaro-pa/` (follow-up PR)

### Source map (published "bozza" build)

1. Le parole della PA — A–Z glossary, RST sources on GitHub (only section present in the repo)
2. Suggerimenti di scrittura — 11 sub-pages: stile-di-scrittura, numeri-e-date, scrivere-per-i-motori-di-ricerca, accessibilita-e-inclusione, come-strutturare-il-contenuto, regole-di-formattazione, punteggiatura-e-grammatica, usabilita, immagini-video, social-e-newsletter, gestione-dei-contenuti
3. Tono di voce — intro + 9 scenarios: registrarsi, primo-accesso, recupero-password, pagamento-online, conferma-pagamento, promemoria-pagamenti, riepilogo-pagamenti, risultati-di-ricerca, blog

Note: suggerimenti + tono di voce exist only in the published build, not in repo master → harvest from docs.italia.it pages.

### Open questions

- Skill name: `scrivi-chiaro-pa`? alternatives: `linguaggio-pa`, `pa-scrivi-semplice`
- Include social/newsletter + immagini/video + gestione contenuti in v1, or keep it lean (web/letters/notices only)?
- Evals in the same PR or follow-up?

## Phase 1: Document & PRD
- [x] Create PRD.md (English) with:
  - Project vision & goals
  - Scope & constraints
  - Skill categories (data, transformation, visualization, etc.)
  - Installation & discovery workflow
  - Catalog structure & metadata requirements
  - Success criteria

## Phase 2: Foundation
- [ ] Create README.md (installation guide)
- [ ] Create CATALOG.md template (skill discovery format)
- [ ] Create CONTRIBUTING.md (skill submission guidelines)
- [ ] Setup project structure (docs/, skills/, examples/)

## Phase 3: Skill Template & Standards
- [ ] Define skill metadata schema (name, description, category, usage, etc.)
- [ ] Create skill template/example
- [ ] Document best practices for skill creation

## Unresolved Questions
- Should there be version control for individual skills?
- Who manages the catalog and skill submissions (curation process)?
- Are there tier/maturity levels (alpha, beta, stable) for skills?
- Should there be tests/validation for contributed skills?
- Where will skills actually be stored/deployed?
