---
name: typst-cards
description: Generate PNG images and PDF carousels for online communication — social media, carousels, infographics, posts — using Typst. Use this skill whenever the user wants to create slides, cards, visual posts or any digital graphic content, even if they don't explicitly mention Typst. The skill drives an interview about brand materials (logo, palette, fonts, DESIGN.md), proposes the formats best suited to the context (Instagram 1:1, Stories 9:16, LinkedIn 16:9, etc.) and produces ready-to-use PNGs, plus a single PDF for LinkedIn document posts.
---

# Typst Cards

## Purpose

Turn a textual context and optional brand materials into professional PNG images for online communication, using Typst as the rendering engine. The skill manages the full flow: interview → theme → generation → review.

## Prerequisites — verify Typst

Before any other step, check that Typst is installed:

```bash
typst --version
```

If not available, install it like this (Linux/WSL x86_64):

```bash
curl -fsSL https://github.com/typst/typst/releases/latest/download/typst-x86_64-unknown-linux-musl.tar.xz -o /tmp/typst.tar.xz && tar -xf /tmp/typst.tar.xz -C /tmp/ && mkdir -p ~/.local/bin && mv /tmp/typst-x86_64-unknown-linux-musl/typst ~/.local/bin/
```

> **Note**: `~/.local/bin` must be in your `PATH` for `typst` to be found. Add `export PATH="$HOME/.local/bin:$PATH"` to your shell profile if needed.

---

## Phase 1 — Interview (single message, mandatory)

Before creating any file, ask these questions to the user **in a single message**:

**Visual materials available?**
- Do you have a logo? If yes, where is the file? (PNG, SVG, or other)
- Do you have a `DESIGN.md` or brand guidelines to share?
- Do you have color preferences? (specific palette, or a mood description: "dark and technical", "colorful and lively", "institutional", etc.)
- Do you have specific fonts to use?

**Desired output:**
- What is the topic or content of the cards?
- How many slides or cards? (a single image or a carousel?)
- Which formats do you need? (propose those best suited to the context, see table below)
- Where will it be published? (this decides the deliverable: PNGs for Instagram and most feeds, a single PDF for a LinkedIn document post — see "Compilation")
- Should the design reach the edges of the card (full-bleed colour bands, photos) or sit inside a margin? (see "Two layout patterns")

If the user has no brand materials, propose a palette consistent with the context and ask for a quick confirmation before proceeding.

---

## Supported formats

| Name | Typical use | Pixels | width | height | PPI |
|------|-------------|--------|-------|--------|-----|
| Square 1:1 | Instagram post, carousels | 1080×1080 | 7.5in | 7.5in | 144 |
| Portrait 4:5 | Instagram portrait | 1080×1350 | 7.5in | 9.375in | 144 |
| Story 9:16 | Instagram/TikTok Stories, Reels | 1080×1920 | 7.5in | 13.33in | 144 |
| Landscape 16:9 | Twitter/X, YouTube thumb, LinkedIn header | 1920×1080 | 13.33in | 7.5in | 144 |
| LinkedIn/OG 1.91:1 | LinkedIn post, Open Graph meta | 1200×628 | 8.33in | 4.36in | 144 |

**Math**: `pixels = inches × PPI` → e.g. 7.5in × 144ppi = 1080px.

For carousels, always use the same format for every slide.

---

## Phase 2 — Material analysis

**With DESIGN.md**: read it and extract — and **apply in theme.typ**:
- **Colors**: every token (primary, secondary, accent, surface, neutral…)
- **Fonts**: if the DESIGN.md specifies different fonts for different roles (e.g. display vs body), use them all in theme.typ as separate variables (`DISPLAY`, `SANS`, `MONO`). For example: a serif display face for headlines, a sans-serif for body.
- **Visual style**: restrained? bold? editorial? Steer the layout accordingly.
- **Explicit rules**: if the DESIGN.md says "do not use X on Y", honor it.

Do not collapse everything into a single font — the display/body distinction is part of the brand.

**Font availability — two tiers.** Only four faces are embedded in the Typst binary and are therefore identical on every machine, in a clean container and in CI:

```bash
typst fonts --ignore-system-fonts
# Libertinus Serif · New Computer Modern · New Computer Modern Math · DejaVu Sans Mono
```

Everything else — including `DejaVu Sans`, `Liberation Sans`, `Arial` — is a **system** font: present on the machine you are working on, possibly missing elsewhere, with the fallback kicking in silently and changing the look. Note the gap: **there is no embedded sans-serif**, so a fully portable body font is not available. Two consequences:

- If the deck must rebuild identically anywhere (CI, another contributor, a container), the only safe pairing is `Libertinus Serif` (or `New Computer Modern`) for display and body, `DejaVu Sans Mono` for code.
- Otherwise use the brand fonts, always with a fallback chain, and check with `fc-list | grep -i "name"` on the machine that will do the rendering.

**With logo**: note the path. You'll include it in Typst with:
```typst
#image("path/to/logo.png", height: 0.5in)   // fixed height
#image("path/to/logo.svg", width: 2in)       // fixed width
```

**Without materials**: pick a palette based on context:
- Tech/data topic → dark background `#0d1117`, accent blue `#58a6ff`
- Consumer/lifestyle topic → white background, vivid colors
- Institutional/PA topic → sober palette, neutral tones with a measured accent
- Editorial/journalism topic → strong typography, high contrast

---

## Phase 3 — File structure

Always create this structure in the project directory:

```
<project>/carousel/
├── theme.typ       # design tokens and helper functions
├── slides.typ      # content (imports theme.typ)
└── output/         # generated files
    ├── slide-1.png
    ├── slide-2.png
    ├── ...
    └── deck.pdf    # whole deck in one file (LinkedIn document post)
```

### Recommended starting point

Instead of writing from scratch, **copy one of the reference templates** from the skill folder and adapt it:

- `references/theme-starter.typ` → palette, fonts, helpers (`lbl`, `footer-block`, `codebox`, `divider`)
- `references/slides-1x1-starter.typ` → 5 Instagram 1:1 slides (cover + 3 content + outro), **margined** pattern
- `references/slides-16x9-starter.typ` → 3 LinkedIn 16:9 slides (cover + two-column + 3 stat), **margined** pattern
- `references/slides-fullbleed-starter.typ` → 5 1:1 cards, **full-bleed** pattern (`slide()` helper, no page margin)

The templates are **already tested and compile cleanly**. They give you a proven structure; you change colors, fonts, content.

```bash
# example:
cp <SKILL_DIR>/references/theme-starter.typ <project>/carousel/theme.typ
cp <SKILL_DIR>/references/slides-1x1-starter.typ <project>/carousel/slides.typ
# then edit content in slides.typ and tokens in theme.typ
```

### Two layout patterns

Pick one **before** writing any content — they are not mixable inside the same deck.

| | **Margined** (default) | **Full-bleed** |
|---|---|---|
| Page | `margin: (x: 0.55in, top: 0.5in, bottom: 0.7in)` | `margin: 0in` |
| Padding | from the page margin | from a `slide()` helper's `inset` |
| Furniture (URL, counter) | native page `footer`, in the bottom margin | `place()`, out of the content flow |
| Background reaches the edges | no — always a white frame | yes |
| Starter | `slides-1x1-starter.typ`, `slides-16x9-starter.typ` | `slides-fullbleed-starter.typ` |

**Choose full-bleed** when the design needs colour, photos or bands touching the edges — a coloured cover, a full-card image, a top band. **Choose margined** for text-first cards with a footer rule and a source URL: it is simpler and it is what the two long-standing starters implement.

The full-bleed pattern is one helper. Each call is one card:

```typst
#set page(width: 7.5in, height: 7.5in, margin: 0in)   // 1:1 → 1080×1080 at 144ppi

#let slide(fill: BG-WHITE, dark: false, bleed: none, body) = page(fill: fill, {
  set text(fill: if dark { FG-DARK } else { FG-LIGHT })
  bleed                                                // edge-to-edge decoration
  place(left + top, rect(width: 0.16in, height: 100%, fill: ACC))   // accent rail
  place(top + right, dx: -0.55in, dy: 0.55in, context text(
    font: MONO, size: 9pt, fill: if dark { MUTED-D } else { MUTED-L },
    [#counter(page).display() / #counter(page).final().first()],
  ))
  place(bottom + left, dx: 0.9in, dy: -0.5in, text(                  // source URL
    font: MONO, size: 9pt, fill: if dark { MUTED-D } else { MUTED-L }, URL,
  ))
  // bottom inset larger than top: it must clear the URL placed above
  block(
    width: 100%, height: 100%,
    inset: (left: 0.9in, right: 0.55in, top: 0.55in, bottom: 0.85in),
    body,
  )
})

#slide(fill: BG-DARK, dark: true, { ... })   // one call = one card
```

Three things to keep straight:

- **Keep the geometry in inches**, not centimetres: `7.5in × 144ppi` is exactly 1080px, while a 21cm square at 144ppi gives 1191px.
- `inset.left` must clear the rail, otherwise the text runs over it.
- The counter goes through `place`, which is **out of flow** — content cannot push it onto a following page. This is the same guarantee the margined pattern gets from the native page footer, so the "fragile footer pattern" pitfall below does not apply here. What *does* apply is the silent clipping of the padded block: see the pitfall of the same name.

### theme.typ — design tokens

Adapt colors to the materials gathered. This is a starting point:

```typst
// — palette —
#let BG-DARK  = rgb("#0d1117")
#let BG-LIGHT = rgb("#f6f8fa")   // light background
#let BG-WHITE = rgb("#ffffff")   // pure white
#let ACC      = rgb("#58a6ff")   // accent on dark background
#let ACC-L    = rgb("#0969da")   // accent on light background
#let FG-DARK  = rgb("#e6edf3")    // text on dark
#let FG-LIGHT = rgb("#1c2128")    // text on light
#let MUTED-D  = rgb("#8b949e")    // secondary on dark
#let MUTED-L  = rgb("#656d76")    // secondary on light
#let CODE-BG  = rgb("#161b22")
#let CODE-BR  = rgb("#30363d")

// — fonts —
// Safe fonts on Linux/WSL: DejaVu Sans, DejaVu Sans Mono
// Check availability: fc-list | grep -i "Font Name"
#let SANS = ("DejaVu Sans", "Liberation Sans", "Arial")
#let MONO = ("DejaVu Sans Mono", "Liberation Mono", "Courier New")

// — helper: section label —
#let lbl(body, dark: false) = text(
  size: 9pt, weight: "bold", tracking: 2pt,
  fill: if dark { ACC } else { ACC-L },
)[#upper(body)]

// — helper: page footer (URL + native page counter) —
// Apply via #set page(footer: footer-block("github.com/me/repo"))
#let footer-block(url, dark: false) = context [
  #line(length: 100%, stroke: 0.5pt + if dark { CODE-BR } else { rgb("#d0d7de") })
  #v(0.06in)
  #grid(columns: (1fr, auto),
    text(font: MONO, size: 9pt, fill: if dark { MUTED-D } else { MUTED-L })[#url],
    text(font: MONO, size: 9pt, fill: if dark { MUTED-D } else { MUTED-L })[
      \# #counter(page).display() / #counter(page).final().first()
    ],
  )
]

// — helper: code block —
#let codebox(body) = block(
  fill: CODE-BG, stroke: 0.5pt + CODE-BR,
  radius: 4pt, inset: (x: 14pt, y: 11pt), width: 100%,
)[
  #set text(font: MONO, size: 10.5pt, fill: FG-DARK)
  #body
]
```

### slides.typ — base structure

```typst
#import "theme.typ": *

// Metadata — ends up in the PDF (title of the document post, author credit)
#set document(title: "Carousel title", author: "Author or organisation")

// Language — drives hyphenation. Set "it" for Italian decks, "en" for English.
#set text(lang: "it")

// Pick the format (only one active line). Keep `bottom` margin generous
// (~0.7in) so the footer line + 9pt text fit fully without clipping.
#set page(width: 7.5in,   height: 7.5in,   margin: (x: 0.55in, top: 0.5in, bottom: 0.7in), footer-descent: 18pt)  // 1:1
// #set page(width: 7.5in, height: 9.375in, margin: (x: 0.55in, top: 0.5in, bottom: 0.7in), footer-descent: 18pt) // 4:5
// #set page(width: 7.5in, height: 13.33in, margin: (x: 0.55in, top: 0.6in, bottom: 0.75in), footer-descent: 20pt) // 9:16
// #set page(width: 13.33in, height: 7.5in, margin: (x: 0.85in, top: 0.55in, bottom: 0.72in), footer-descent: 20pt) // 16:9
// #set page(width: 8.33in, height: 4.36in, margin: (x: 0.55in, top: 0.4in, bottom: 0.6in), footer-descent: 16pt) // 1.91:1

#set text(font: SANS, size: 15pt, fill: FG-LIGHT)

// Footer URL — edit once for the deck. Counter is auto-numbered.
#let URL = "github.com/<org>/<repo>"

// — SLIDE 1 (dark) — set fill + matching dark footer together
#set page(fill: BG-DARK, footer: footer-block(URL, dark: true))
#v(1fr)
#lbl(dark: true)[tag · topic]
#v(0.15in)
#text(size: 44pt, weight: 900, fill: FG-DARK)[
  Main title\
  of the slide
]
#v(0.2in)
#text(size: 14pt, fill: MUTED-D)[Short subtitle or description]
#v(1fr)

// — SLIDE 2 (light) — switch fill → new page automatically
#set page(fill: BG-LIGHT, footer: footer-block(URL, dark: false))
#lbl[02 · section]
#v(0.2in)
#text(size: 31pt, weight: 900)[Section title]
#v(0.2in)
#text(size: 14pt, fill: MUTED-L)[Slide body text.]

// — SLIDE 3 (same background as slide 2 → explicit pagebreak) —
#pagebreak()
// ... content ...
```

**Why the footer goes through `#set page(footer: ...)` and not a manual `#ctr` at the end of each slide**: the page-level footer uses Typst's native page counter, so adding/removing slides requires no renumbering. It also lives in the `bottom` margin, so it cannot be pushed to the next page by dense content (see "fragile footer pattern" in pitfalls).

### Compilation

```bash
cd <project>/carousel

# one PNG per card — for Instagram, X, previews, review
typst compile slides.typ "output/slide-{p}.png" --ppi 144

# one PDF for the whole deck — this is what you upload to LinkedIn
typst compile slides.typ output/deck.pdf
```

The `{p}` is replaced by the page number → one PNG per slide.

**A LinkedIn carousel is a PDF, not a set of images**: it is uploaded as a single *document post* and the feed turns the pages into swipeable cards. Produce both — the PDF to publish, the PNGs to review in Phase 4 and to reuse on other platforms. Neither export needs an extra tool.

Optional, only if the user asks for an animated preview (requires ImageMagick, an external dependency):

```bash
magick -delay 250 -loop 0 output/slide-*.png output/deck.gif
```

---

## Design principles for social cards

**Text hierarchy**: large title → subtitle → body. Max 3 levels. Don't crowd.

**White space**: generous margins (0.5–0.7in). Let the content breathe.

**Colors**: 2–3 max. A vivid accent on a neutral background always works.

**Font sizes on a 1080px canvas** (1pt Typst ≈ 2px output):
- Cover title: 42–50pt
- Section title: 28–34pt
- Body: 14–16pt
- Label/tag: 9–10pt bold uppercase with tracking

**Carousels**: counter at bottom right of every slide (`1 / 6`, `2 / 6`, ...).

**Deck arc** — decide the sequence before writing any card:
- Five to seven cards. Fewer says too little, more loses the reader mid-swipe.
- Cover → content → closing call to action. The cover carries one claim, not a summary.
- One card with an inverted background (dark among light, or the accent colour) to break the rhythm — one, not three.
- One visual idea per deck: a palette, a font pairing, a single recurring motif. Do not restate the same idea on every card.
- Do not clone the previous deck's layout. Consistency lives in the palette and typography, not in repeating the composition.

**Story 9:16**: center the content vertically, use larger fonts, avoid corners.

**Footer/edge content never clips**: any text near the page borders — footer, slide counter (`ctr`), source URL, page number — must be fully visible, no half-cut letters. If clipping occurs, increase the page bottom margin (`#set page(margin: (x: ..., y: ...))`) or reduce the footer font size. This is a must-check in Phase 4.

---

## Known pitfalls

**Grid with wide numbers/text**: `columns: (1fr, 1fr, 1fr)` causes overflow if values are wide. Use a vertical layout or `columns: (auto, 1fr)` with a generous gutter.

**Unavailable fonts**: always specify fallbacks (`("Chosen Font", "DejaVu Sans", "Arial")`). Check with `fc-list | grep -i "name"`. A warning is not an error: Typst uses the fallback.

**`#set page(fill: X)` does not create a new page if X doesn't change**: between slides with the same fill, use an explicit `#pagebreak()`.

**Fragile footer pattern — `#v(1fr)` + `#ctr(n, total)` as the last row of each slide**: when content saturates the page, the `1fr` space collapses to 0 and the counter slides onto the next page — you get a "ghost slide" with only the counter visible, no error. Prefer Typst's native page-level footer:
```typst
#set page(footer: footer-block(URL, dark: true))
// content of the slide — no v(1fr)+ctr at the end
```
The counter lives in the `bottom` margin and cannot be pushed by content. Overflow now manifests as a real extra page (immediately diagnosable) instead of a silent ghost slide.

This pitfall is about the **margined** pattern. In the full-bleed pattern there is no bottom margin to put a footer in, and the equivalent guarantee comes from `place`: placed content is out of the layout flow, so no amount of body text can move it. Either mechanism is fine; a manual `#v(1fr)` + counter as the last row of the body is not.

**Full-bleed: `height: 100%` clips silently on overflow.** Verified on typst 0.14.2 — a `block(width: 100%, height: 100%, inset: ...)` whose content does not fit produces **one page with the text cut off at the edge**: no warning, no extra page, exit code 0. Remove `height: 100%` and the same content spills into six real pages. The fixed height is not optional (it is what makes `v(1fr)` centre anything), so treat this as a diagnostic step rather than something to design around:

```bash
# suspect a card is overfull? temporarily drop `height: 100%` from the helper
# and recompile: if the deck grows extra pages, that card is over capacity
typst compile slides.typ "output/slide-{p}.png" --ppi 144 && ls output/*.png | wc -l
```

The page count must equal the number of `#slide(...)` calls, and Phase 4 must actually look at the images — this failure mode is invisible to any check that only counts files.

**Full-bleed: `width: 100%` inside the body is the padded column, not the page.** A rectangle placed inside `body` is measured against the inset block, so it stops short of the edges and the "full-bleed" band comes out framed. Edge-to-edge decoration must be a sibling of the padded block, which is what the `bleed` parameter is for:

```typst
// WRONG — the band inherits the block's inset
#slide({ place(top + left, rect(width: 100%, height: 1.4in, fill: BG-LIGHT)) ... })

// CORRECT — drawn before the padded block, measured against the page
#slide(bleed: place(top + left, rect(width: 100%, height: 1.4in, fill: BG-LIGHT)), { ... })
```

**`v(1fr)` works at page level**: it splits the leftover space. If you place two of them, the space is split evenly between the two points.

**Logo with transparent background**: prefer SVG when possible. PNG with alpha works but requires that the slide background does not contrast badly with it.

**Special characters in content mode**: several characters open syntactic constructs in Typst content mode and cause "unclosed delimiter" errors when used literally. Escape with a backslash or rephrase:

| Char | What it opens in content | How to escape |
|------|---------------------------|----------------|
| `$` | math mode | `\$` |
| `//` | line comment | `\/\/` or split with a space `/ /` |
| `_` (adjacent to a word) | emphasis (italic) | `\_` |
| `*` (before a word) | strong (bold) | `\*` |
| `@` | reference | `\@` |
| `<` | label | use words ("less than") or `$lt$` in math mode |
| `~` | non-breaking space (silent, rarely a problem) | `\~` if you need it as literal output |

Typical contexts where you trip on this: terminal-style strings (`$ command`, `~$`, `exit_`), paths like `MIT // license`, identifiers with `_`. Typst usually reports the error far from the actual cause, so when you see "unclosed delimiter" scan for these characters first.

> **Sub-case — strings passed as helper parameters are literal**: when you call something like `#item("$ command", "...")` or `#text(...)[#param]` with a string variable, the string is treated literally — backslash escapes are NOT resolved. So `"\$ command"` outputs `\$ command` (with the visible backslash), while `"$ command"` outputs `$ command` correctly. The escape rule applies only inside content/markup, not inside string-typed parameter values.

> **Sub-case — smart quotes do not reach string values**: the same split hits apostrophes, and this one is silent. Typst turns `'` into a typographic `’` in markup only. A string keeps the straight `'`, and interpolating it into content does not rescue it:
>
> ```typst
> A contenuto diretto: l'investimento          // → l’investimento
> B #text("l'investimento")                    // → l'investimento
> C #helper("l'investimento")                  // → l'investimento
> D #helper[l'investimento]                    // → l’investimento
> E #{let s = "l'investimento"; [#s]}          // → l'investimento
> ```
>
> A deck that mixes prose and helper calls therefore comes out with two different apostrophes and no error anywhere. It bites hardest in Italian and French. Fix: pass content `[...]` instead of `"..."`, or type `’` directly in the string. Worth a grep for `'` in string arguments before the final compile.

**`leading` is not a parameter of `text()`**: it belongs to `par()`. To control line height of a text block:
```typst
// WRONG — error "unexpected argument: leading"
#text(size: 14pt, leading: 1.4em)[...]

// CORRECT — use par leading inside a block
#block[
  #set par(leading: 0.7em)
  #text(size: 14pt)[...]
]
```

**`align(center + horizon)` with long text causes incorrect wordwrap**: words can fuse. Prefer to handle vertical and horizontal alignment separately, or use `block(width: 100%)` to contain the text.

**Editorial pattern (kicker + huge title + footer)**:
```typst
// magazine/newspaper style — battle-tested on 1:1
#text(size: 9pt, weight: "bold", tracking: 3pt, fill: ACC)[#upper("category · section")]
#v(0.08in)
#line(length: 100%, stroke: 1pt + ACC)
#v(0.25in)
#text(size: 14pt, fill: DIM)[Eyebrow]
#v(0.05in)
#text(size: 60pt, weight: 900)[Big title]
#v(0.05in)
#text(size: 18pt, weight: "bold", fill: ACC)[Accent subtitle]
#v(1fr)
#line(length: 100%, stroke: 0.5pt + rgb("#333333"))
#v(0.1in)
#grid(columns: (1fr, 1fr, 1fr),
  text(size: 11pt)[Date],
  align(center, text(size: 11pt)[Place]),
  align(right, text(size: 11pt, fill: ACC)[CTA]),
)
```

---

## Phase 4 — Review and iteration

After every compile:

1. **Count** the generated PNGs — the total must equal the number of cards you wrote. More pages means overflow; the same number is not by itself proof that nothing was cut (see the silent-clipping pitfall)
2. **Read** the PNGs with the Read tool — look at each slide, don't just confirm the file exists
3. **Evaluate** against the design principles above: hierarchy, white space, contrast, text overflow/clipping, counter visibility, image quality
4. **Report and propose**: list what works, what doesn't, and propose concrete fixes (e.g. "slide 3 title clips on the right — reduce from 44pt to 38pt", "increase top margin from 0.58in to 0.75in")
5. **Wait** for user feedback before applying any change — do not auto-iterate

Typst recompiles in <1s, so iteration is cheap; each round must still be driven by an explicit user decision.

---

## Credits

The full-bleed pattern (`margin: 0` plus a `slide()` helper that adds the padding back, with the repeated furniture drawn via `place`) is adapted from [Build LinkedIn Carousels with Typst: the `slide` Layout](https://mickael.canouil.fr/posts/2026-05-28-typst-linkedin-carousels/) by Mickaël Canouil. The mechanism is reused here; the palette, typography and card compositions are not.
