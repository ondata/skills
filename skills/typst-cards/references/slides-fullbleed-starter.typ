// ─── slides-fullbleed-starter.typ ─────────────────────────────────────────
// Instagram/LinkedIn 1:1 carousel template (1080×1080px), FULL-BLEED variant.
// Copy to <project>/carousel/slides.typ and adapt the content.
// Requires theme.typ in the same folder: copy references/theme-starter.typ to
// <project>/carousel/theme.typ, as Phase 3 of SKILL.md prescribes.
//
// Difference from slides-1x1-starter.typ: the page has NO margin, so
// backgrounds, colour bands and images reach every edge. The padding is added
// back inside the `slide` helper, and the repeated furniture (accent rail,
// page counter, URL) is drawn with `place`, out of the content flow.
//
// Use this variant when the design needs edge-to-edge colour or imagery.
// Use slides-1x1-starter.typ when a classic margined page with a footer rule
// is enough — see "Two layout patterns" in SKILL.md.

#import "theme.typ": *

// ── document metadata (ends up in the PDF) ────────────────────────────────
#set document(title: "Carousel title", author: "Author or organisation")

// ── language: drives hyphenation — set "it" for Italian decks ─────────────
#set text(lang: "en")

// ── format: Square 1:1 → 7.5in × 144ppi = exactly 1080×1080px ─────────────
// margin: 0in is the whole point. Do not add a page margin back here.
#set page(width: 7.5in, height: 7.5in, margin: 0in)
#set text(font: SANS, size: 15pt, fill: FG-LIGHT)

// Footer URL — edit once for the whole deck.
#let URL = "github.com/<org>/<repo>"

// ── the slide helper ──────────────────────────────────────────────────────
// One call = one card. Draws the accent rail, the page counter and the URL,
// then lays out `body` in the padded area. Move it to theme.typ if you reuse
// it across several decks.
//
// `inset.left` must clear the rail (rail 0.16in + breathing room → 0.9in).
//
// `bleed` takes content drawn BEFORE the padded block, so it measures against
// the page and can reach the edges. Anything placed inside `body` is measured
// against the padded block instead and will stop at the inset — that is the
// most common mistake with this pattern.
#let slide(fill: BG-WHITE, dark: false, bleed: none, body) = page(fill: fill, {
  set text(fill: if dark { FG-DARK } else { FG-LIGHT })

  // edge-to-edge decoration, if any
  bleed

  // full-height accent rail on the left edge
  place(left + top, rect(width: 0.16in, height: 100%, fill: ACC))

  // page counter, top right — native counter, robust to adding/removing cards
  place(top + right, dx: -0.55in, dy: 0.55in, context text(
    font: MONO,
    size: 9pt,
    fill: if dark { MUTED-D } else { MUTED-L },
    [#counter(page).display() / #counter(page).final().first()],
  ))

  // source URL, bottom left
  place(bottom + left, dx: 0.9in, dy: -0.5in, text(
    font: MONO,
    size: 9pt,
    fill: if dark { MUTED-D } else { MUTED-L },
    URL,
  ))

  // content area — `place` above is out of flow, so only this block matters.
  // WARNING: with `height: 100%` an overfull card is CLIPPED SILENTLY.
  // To check, temporarily drop `height: 100%`: extra pages = overfull card.
  block(
    width: 100%,
    height: 100%,
    inset: (left: 0.9in, right: 0.55in, top: 0.55in, bottom: 0.85in),
    body,
  )
})

// Compilation:
//   typst compile slides.typ "output/slide-{p}.png" --ppi 144
//   typst compile slides.typ output/deck.pdf

// ══════════════════════════════════════════════════════════════════════════
// CARD 1 · Cover (dark background)
// ══════════════════════════════════════════════════════════════════════════
#slide(fill: BG-DARK, dark: true, {
  v(1fr)
  lbl(dark: true)[category · topic]
  v(0.15in)
  text(font: DISPLAY, size: 44pt, weight: 900)[
    Main title\
    of the card
  ]
  v(0.2in)
  text(size: 14pt, fill: MUTED-D)[
    Short descriptive subtitle,\
    one or two lines.
  ]
  v(1fr)
})

// ══════════════════════════════════════════════════════════════════════════
// CARD 2 · Content section — full-bleed accent band at the top
// The band goes through `bleed`, not through the body: only there does
// `width: 100%` mean the page width instead of the padded column.
// ══════════════════════════════════════════════════════════════════════════
#slide(bleed: place(top + left, rect(width: 100%, height: 1.4in, fill: BG-LIGHT)), {
  v(1.05in)
  lbl[01 · first section]
  v(0.18in)
  text(size: 31pt, weight: 900)[
    Section title\
    on two lines
  ]
  v(0.22in)
  text(size: 14pt, fill: MUTED-L)[
    Card body text. Three or four\
    lines max. Leave white space\
    around the text.
  ]
})

// ══════════════════════════════════════════════════════════════════════════
// CARD 3 · Numbered list (inverted background — one per deck)
// ══════════════════════════════════════════════════════════════════════════
#slide(fill: BG-DARK, dark: true, {
  lbl(dark: true)[02 · key points]
  v(0.2in)
  text(size: 26pt, weight: 900)[What to know]
  v(0.3in)

  // List pattern with accent number — safe, avoids grid overflow
  let item(num, title, desc) = {
    grid(
      columns: (0.45in, 1fr),
      column-gutter: 0.12in,
      align(top + left, text(size: 10pt, weight: "bold", fill: ACC)[#num]),
      stack(
        dir: ttb,
        spacing: 3pt,
        text(size: 15pt, weight: "bold")[#title],
        text(size: 12pt, fill: MUTED-D)[#desc],
      ),
    )
    v(0.16in)
  }

  item("01", "First point", "Short description of the first item")
  item("02", "Second point", "Short description of the second item")
  item("03", "Third point", "Short description of the third item")
})

// ══════════════════════════════════════════════════════════════════════════
// CARD 4 · Data or code
// ══════════════════════════════════════════════════════════════════════════
#slide({
  lbl[03 · detail]
  v(0.18in)
  text(size: 31pt, weight: 900)[Section title]
  v(0.22in)
  text(size: 14pt, fill: MUTED-L)[Short introduction to the block below.]
  v(0.25in)
  codebox[
    example code or relevant data\
    line two of the code
  ]
})

// ══════════════════════════════════════════════════════════════════════════
// CARD 5 · Outro / Call to action
// ══════════════════════════════════════════════════════════════════════════
#slide({
  lbl[conclusion]
  v(1fr)
  text(font: DISPLAY, size: 36pt, weight: 900)[
    Closing line\
    or call to action.
  ]
  v(0.3in)
  text(size: 16pt, fill: MUTED-L)[Final note, link or invitation to act.]
  v(1fr)
})
