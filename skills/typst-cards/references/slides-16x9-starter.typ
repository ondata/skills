// ─── slides-16x9-starter.typ ──────────────────────────────────────────────
// LinkedIn / Twitter / YouTube 16:9 slide template (1920×1080px).
// Copy to <project>/carousel/slides.typ and adapt the content.
// Requires theme.typ in the same folder: copy references/theme-starter.typ to
// <project>/carousel/theme.typ, as Phase 3 of SKILL.md prescribes.

#import "theme.typ": *

// ── format: Landscape 16:9 → 1920×1080px ──────────────────────────────────
// Keep `bottom` margin >= 0.65in so the footer line + 9pt text fit fully.
#set page(
  width: 13.33in, height: 7.5in,
  margin: (x: 0.85in, top: 0.55in, bottom: 0.72in),
  footer-descent: 20pt,
)
#set text(font: SANS, size: 16pt, fill: FG-LIGHT)

// Footer URL — edit once for the whole deck. Counter is auto-numbered.
#let URL = "github.com/<org>/<repo>"

// Compilation:
//   typst compile slides.typ "output/slide-{p}.png" --ppi 144

// Text size notes for 16:9 (wide canvas):
//   - cover title:    46–56pt
//   - section title:  32–38pt
//   - body:           15–17pt
//   - label/eyebrow:  10–11pt

// ══════════════════════════════════════════════════════════════════════════
// SLIDE 1 · Cover (dark background, editorial layout)
// ══════════════════════════════════════════════════════════════════════════
#set page(fill: BG-DARK, footer: footer-block(URL, dark: true))

#v(1fr)
#lbl(dark: true)[category · section]
#v(0.15in)
#divider(dark: true)
#v(0.25in)
#text(
  font: DISPLAY,
  size: 52pt,
  weight: 400,
  fill: FG-DARK,
)[
  Main title\
  on two or three lines.
]
#v(0.2in)
#text(size: 16pt, fill: MUTED-D)[
  Descriptive subtitle —\
  explain the context in two lines.
]
#v(1fr)

// ══════════════════════════════════════════════════════════════════════════
// SLIDE 2 · Structured content (light background, two columns)
// ══════════════════════════════════════════════════════════════════════════
#set page(fill: BG-LIGHT, footer: footer-block(URL, dark: false))
#set text(fill: FG-LIGHT)

#lbl[01 · details]
#v(0.18in)
#text(font: SANS, size: 36pt, weight: 700)[
  Section title\
  main content
]
#v(0.3in)

// Two-column pattern — safe for 16:9 layouts
#grid(
  columns: (1fr, 1fr),
  column-gutter: 0.5in,
  // left column
  stack(dir: ttb, spacing: 10pt,
    text(size: 12pt, weight: "bold", fill: ACC-L)[CATEGORY A],
    text(size: 16pt)[First meaningful content,\
                     described concisely.],
    v(0.15in),
    text(size: 12pt, weight: "bold", fill: ACC-L)[CATEGORY B],
    text(size: 16pt)[Second content, positioned\
                     consistently with the first.],
  ),
  // right column
  stack(dir: ttb, spacing: 10pt,
    text(size: 12pt, weight: "bold", fill: ACC-L)[CATEGORY C],
    text(size: 16pt)[Third point, complementary\
                     to the previous.],
    v(0.15in),
    text(size: 12pt, weight: "bold", fill: ACC-L)[CATEGORY D],
    text(size: 16pt)[Fourth point closing\
                     the section.],
  ),
)

// ══════════════════════════════════════════════════════════════════════════
// SLIDE 3 · Numbers / impact (dark background, 3 horizontal stats)
// ══════════════════════════════════════════════════════════════════════════
#set page(fill: BG-DARK, footer: footer-block(URL, dark: true))
#set text(fill: FG-DARK)

#v(0.3in)
#lbl(dark: true)[02 · impact]
#v(0.18in)
#divider(dark: true)
#v(0.4in)

// 3-stat pattern — number stacked vertically to avoid 1fr overflow
#grid(
  columns: (1fr, 1fr, 1fr),
  column-gutter: 0.3in,
  stack(dir: ttb, spacing: 8pt,
    text(size: 48pt, weight: 900, fill: ACC)[N°],
    text(size: 14pt, fill: MUTED-D)[short \
    description],
  ),
  stack(dir: ttb, spacing: 8pt,
    text(size: 48pt, weight: 900, fill: ACC)[N°],
    text(size: 14pt, fill: MUTED-D)[short \
    description],
  ),
  stack(dir: ttb, spacing: 8pt,
    text(size: 48pt, weight: 900, fill: ACC)[N°],
    text(size: 14pt, fill: MUTED-D)[short \
    description],
  ),
)
#v(0.4in)
#text(size: 16pt, fill: MUTED-D)[
  Closing line — call to action or final link.
]
