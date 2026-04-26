---
name: typst-cards
description: Generate PNG images for online communication — social media, carousels, infographics, posts — using Typst. Use this skill whenever the user wants to create slides, cards, visual posts or any digital graphic content, even if they don't explicitly mention Typst. The skill drives an interview about brand materials (logo, palette, fonts, DESIGN.md), proposes the formats best suited to the context (Instagram 1:1, Stories 9:16, LinkedIn 16:9, etc.) and produces ready-to-use PNGs.
---

## Purpose

Turn a textual context and optional brand materials into professional PNG images for online communication, using Typst as the rendering engine. The skill manages the full flow: interview → theme → generation → review.

## Prerequisites — verify Typst

Before any other step, check that Typst is installed:

```bash
typst --version
```

If not available, install it like this (Linux/WSL x86_64):

```bash
curl -fsSL https://github.com/typst/typst/releases/latest/download/typst-x86_64-unknown-linux-musl.tar.xz -o /tmp/typst.tar.xz && tar -xf /tmp/typst.tar.xz -C /tmp/ && mv /tmp/typst-x86_64-unknown-linux-musl/typst ~/.local/bin/
```

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
└── output/         # generated PNGs
    ├── slide-1.png
    ├── slide-2.png
    └── ...
```

### Recommended starting point

Instead of writing from scratch, **copy one of the reference templates** from the skill folder and adapt it:

- `references/theme-starter.typ` → palette, fonts, helpers (`lbl`, `ctr`, `codebox`, `divider`)
- `references/slides-1x1-starter.typ` → 5 Instagram 1:1 slides (cover + 3 content + outro)
- `references/slides-16x9-starter.typ` → 3 LinkedIn 16:9 slides (cover + two-column + 3 stat)

The templates are **already tested and compile cleanly**. They give you a proven structure; you change colors, fonts, content.

```bash
# example:
cp <SKILL_DIR>/references/theme-starter.typ <project>/carousel/theme.typ
cp <SKILL_DIR>/references/slides-1x1-starter.typ <project>/carousel/slides.typ
# then edit content in slides.typ and tokens in theme.typ
```

### theme.typ — design tokens

Adapt colors to the materials gathered. This is a starting point:

```typst
// — palette —
#let BG-DARK  = rgb("#0d1117")
#let BG-LIGHT = rgb("#ffffff")
#let ACC-DARK  = rgb("#58a6ff")   // accent on dark background
#let ACC-LIGHT = rgb("#0969da")   // accent on light background
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
  fill: if dark { ACC-DARK } else { ACC-LIGHT },
)[#upper(body)]

// — helper: slide counter (for carousels) —
#let ctr(n, total, dark: false) = align(right)[
  #text(size: 9pt, fill: if dark { MUTED-D } else { MUTED-L })[#n / #total]
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

// Pick the format (only one active line):
#set page(width: 7.5in,   height: 7.5in,   margin: (x: 0.62in, y: 0.58in))  // 1:1
// #set page(width: 7.5in, height: 9.375in, margin: (x: 0.62in, y: 0.58in)) // 4:5
// #set page(width: 7.5in, height: 13.33in, margin: (x: 0.62in, y: 0.70in)) // 9:16
// #set page(width: 13.33in, height: 7.5in, margin: (x: 0.80in, y: 0.58in)) // 16:9
// #set page(width: 8.33in, height: 4.36in, margin: (x: 0.62in, y: 0.45in)) // 1.91:1

#set text(font: SANS, size: 15pt, fill: FG-LIGHT)

// — SLIDE 1 (dark background) —
#set page(fill: BG-DARK)
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
#ctr(1, 6, dark: true)

// — SLIDE 2 (light background) — different settings → automatic page break
#set page(fill: BG-LIGHT)
#lbl[02 · section]
#v(0.2in)
#text(size: 31pt, weight: 900)[Section title]
#v(0.2in)
#text(size: 14pt, fill: MUTED-L)[Slide body text.]
#v(1fr)
#ctr(2, 6)

// — SLIDE 3 (same background as slide 2 → explicit pagebreak) —
#pagebreak()
// ... content ...
```

### Compilation

```bash
cd <project>/carousel
typst compile slides.typ "output/slide-{p}.png" --ppi 144
```

The `{p}` is replaced by the page number → one PNG per slide.

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

**Story 9:16**: center the content vertically, use larger fonts, avoid corners.

---

## Known pitfalls

**Grid with wide numbers/text**: `columns: (1fr, 1fr, 1fr)` causes overflow if values are wide. Use a vertical layout or `columns: (auto, 1fr)` with a generous gutter.

**Unavailable fonts**: always specify fallbacks (`("Chosen Font", "DejaVu Sans", "Arial")`). Check with `fc-list | grep -i "name"`. A warning is not an error: Typst uses the fallback.

**`#set page(fill: X)` does not create a new page if X doesn't change**: between slides with the same fill, use an explicit `#pagebreak()`.

**`v(1fr)` works at page level**: it splits the leftover space. If you place two of them, the space is split evenly between the two points.

**Logo with transparent background**: prefer SVG when possible. PNG with alpha works but requires that the slide background does not contrast badly with it.

**The `<` symbol in Typst content**: it is interpreted as a label opening and causes an error. Replace with words ("less than", "lower than") or use `$lt$` in math mode.

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

1. Compile with `typst compile` and read the resulting PNGs with the Read tool
2. Show the generated slides to the user
3. Ask for feedback: colors, text sizes, layout, content
4. Typst recompiles in <1s: iterate quickly until satisfied
