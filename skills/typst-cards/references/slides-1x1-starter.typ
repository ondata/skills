// ─── slides-1x1-starter.typ ───────────────────────────────────────────────
// Instagram 1:1 carousel template (1080×1080px).
// Copy to <project>/carousel/slides.typ and adapt the content.
// Requires theme-starter.typ in the same folder (or rename it to theme.typ).

#import "theme-starter.typ": *

// ── format: Square 1:1 → 1080×1080px ──────────────────────────────────────
// Keep `bottom` margin >= 0.62in so the footer line + 9pt text fit fully.
#set page(
  width: 7.5in, height: 7.5in,
  margin: (x: 0.55in, top: 0.5in, bottom: 0.7in),
  footer-descent: 18pt,
)
#set text(font: SANS, size: 15pt, fill: FG-LIGHT)

// Footer URL — edit once for the whole deck. Counter is auto-numbered.
#let URL = "github.com/<org>/<repo>"

// Compilation:
//   typst compile slides.typ "output/slide-{p}.png" --ppi 144

// ══════════════════════════════════════════════════════════════════════════
// SLIDE 1 · Cover (dark background)
// ══════════════════════════════════════════════════════════════════════════
#set page(fill: BG-DARK, footer: footer-block(URL, dark: true))

#v(1fr)
#lbl(dark: true)[category · topic]
#v(0.15in)
#text(
  font: DISPLAY,
  size: 44pt,
  weight: 900,
  fill: FG-DARK,
)[
  Main title\
  of the card
]
#v(0.2in)
#text(size: 14pt, fill: MUTED-D)[
  Short descriptive subtitle,\
  one or two lines.
]
#v(1fr)

// ══════════════════════════════════════════════════════════════════════════
// SLIDE 2 · Content section (light background)
// Change of fill creates a new page automatically.
// ══════════════════════════════════════════════════════════════════════════
#set page(fill: BG-WHITE, footer: footer-block(URL, dark: false))
#set text(fill: FG-LIGHT)

#lbl[01 · first section]
#v(0.18in)
#text(size: 31pt, weight: 900)[
  Section title\
  on two lines
]
#v(0.22in)
#text(size: 14pt, fill: MUTED-L)[
  Slide body text. Three or four\
  lines max. Leave white space\
  around the text.
]
#v(0.2in)
#codebox[
  example code or relevant data\
  line two of the code
]

// ══════════════════════════════════════════════════════════════════════════
// SLIDE 3 · Second section (same background → explicit pagebreak)
// ══════════════════════════════════════════════════════════════════════════
#pagebreak()

#lbl[02 · second section]
#v(0.18in)
#text(size: 31pt, weight: 900)[Section title]
#v(0.22in)
#text(size: 14pt, fill: MUTED-L)[
  Section content.
]

// ══════════════════════════════════════════════════════════════════════════
// SLIDE 4 · List or data (alternated dark background)
// ══════════════════════════════════════════════════════════════════════════
#set page(fill: BG-DARK, footer: footer-block(URL, dark: true))
#set text(fill: FG-DARK)

#lbl(dark: true)[03 · key points]
#v(0.2in)
#text(size: 26pt, weight: 900, fill: FG-DARK)[What to know]
#v(0.3in)

// List pattern with accent number — safe, avoids grid overflow
#let item(num, title, desc) = {
  grid(
    columns: (0.45in, 1fr),
    column-gutter: 0.12in,
    align(top + left)[
      #text(size: 10pt, weight: "bold", fill: ACC)[#num]
    ],
    stack(dir: ttb, spacing: 3pt,
      text(size: 15pt, weight: "bold", fill: FG-DARK)[#title],
      text(size: 12pt, fill: MUTED-D)[#desc],
    ),
  )
  v(0.16in)
}

#item("01", "First point", "Short description of the first item")
#item("02", "Second point", "Short description of the second item")
#item("03", "Third point", "Short description of the third item")

// ══════════════════════════════════════════════════════════════════════════
// SLIDE 5 · Outro / Call to action
// ══════════════════════════════════════════════════════════════════════════
#set page(fill: BG-WHITE, footer: footer-block(URL, dark: false))
#set text(fill: FG-LIGHT)

#lbl[conclusion]
#v(1fr)
#text(size: 36pt, weight: 900)[
  Closing line\
  or call to action.
]
#v(0.3in)
#text(size: 16pt, fill: MUTED-L)[
  Final note, link or invitation to act.
]
#v(1fr)
