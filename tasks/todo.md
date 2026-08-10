# onData Skills Project - Planning

## typst-cards: full-bleed slide pattern + PDF output — 2026-08-10

Source: https://mickael.canouil.fr/posts/2026-05-28-typst-linkedin-carousels/ (Mickaël Canouil, CC BY-NC-SA 4.0) — ideas only, no verbatim reuse of his palette/typography.

### What was verified locally (typst 0.14.2)

- `typst fonts --ignore-system-fonts` → only `Libertinus Serif`, `New Computer Modern`, `New Computer Modern Math`, `DejaVu Sans Mono` are embedded. The skill's current primary body font `DejaVu Sans` is **system-only** → can vanish in a clean container/CI. There is **no embedded sans-serif**.
- `margin: 0` + `slide()` helper + `place()` for rail/counter compiles and renders full-bleed; native `counter(page)` works inside `place` under `context`.
- 21cm × 21cm @144ppi = **1191px, not 1080** → keep the skill's `in` + PPI geometry (7.5in × 144 = exactly 1080), take only the `margin: 0` mechanism.
- `block(width: 100%, height: 100%, inset: ...)` **clips silently** on overflow (1 page, no warning, exit 0). Without `height: 100%` the same content spills into 6 real pages. New pitfall, and it partly reopens the "ghost slide" problem the current footer pattern was designed to kill.

### Phase 1 — SKILL.md

- [x] New section "Two layout patterns": margined (current, footer in the bottom margin) vs full-bleed (`margin: 0` + `slide()` + `place()`), with a rule for choosing
- [x] Reconcile the "fragile footer pattern" pitfall (SKILL.md:217, 260-265) with the full-bleed pattern — `place()` is out of flow, so the counter cannot be pushed; state this explicitly instead of leaving two contradictory prescriptions
- [x] New pitfall: silent clipping of `height: 100%` blocks + how to detect it (temporarily drop `height: 100%`; extra pages = overfull slide)
- [x] Font tiers: embedded/CI-safe set vs system fonts needing `fc-list`; state plainly there is no embedded sans
- [x] `#set document(title:, author:)` (PDF metadata) and `#set text(lang: "it")` (Italian hyphenation)
- [x] Deck-level guidance: 5–7 cards, cover → content → CTA, one inverted-background card, one visual idea per deck
- [x] PDF output alongside PNG: `typst compile slides.typ deck.pdf` — LinkedIn carousels are uploaded as a PDF document post
- [x] Optional one-liner GIF via ImageMagick (marked optional, external dependency)

### Phase 2 — references

- [x] New `references/slides-fullbleed-starter.typ` (margin: 0, `slide()` helper, placed counter, neutral palette, 1:1 at 7.5in/144ppi)
- [x] Leave `slides-1x1-starter.typ` / `slides-16x9-starter.typ` untouched (they carry a "tested, compiles cleanly" promise; a geometry change would invalidate them and half the pitfalls section)
- [x] Smoke-test the new starter: PNG + PDF, read the images, verify page count

### Phase 3 — housekeeping

- [x] Branch `add/typst-cards-fullbleed`, keep the three modified `difensore-civico-ti-scrivo` files out of the commit
- [x] Update `LOG.md`, open PR

### Open questions

- PDF output changes what the skill delivers — update the frontmatter `description` (now PNG-only)? Affects triggering.
- Full-bleed as a third option, or refactor both existing starters to `margin: 0`? The refactor is breaking.
- Add `evals/typst-cards/`? None exists today.

---

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
