// ─── theme-starter.typ ────────────────────────────────────────────────────
// Starter template. Adjust values to the context or DESIGN.md.
// Copy or rename this file to `theme.typ` in the same folder, then import it
// in slides.typ with: #import "theme.typ": *

// ── palette ────────────────────────────────────────────────────────────────
// PLACEHOLDER PALETTE — neutral on purpose, so it does not look like a design
// decision that was already made. Replace it with the user's palette or the
// tokens in their DESIGN.md. If DESIGN.md has named tokens (primary,
// secondary...), map them onto the names below rather than renaming these.
//
// Surfaces and text are neutral greys, with no colour cast. All the pairings
// below clear 4.5:1, so every token is usable for body text, not just for
// decoration — keep that true after swapping in the brand colours.

#let BG-DARK  = rgb("#17191c")   // dark surface       — 15.9:1 with FG-DARK
#let BG-LIGHT = rgb("#f0efed")   // light surface, bands, boxes
#let BG-WHITE = rgb("#fbfbfa")   // lightest surface   — 16.5:1 with FG-LIGHT

// The accent is the ONE colour in the deck, and the first value to replace.
// ACC and ACC-L are the SAME colour at two lightnesses, one per background —
// not two brand colours. A DESIGN.md "primary" maps onto both.
#let ACC-L    = rgb("#2f5d8a")   // accent on light bg — 6.6:1  ← replace first
#let ACC      = rgb("#8fb8dd")   // accent on dark bg  — 8.4:1  ← same hue, lighter

#let FG-DARK  = rgb("#f2f3f4")   // text on dark
#let FG-LIGHT = rgb("#1a1c1e")   // text on light
#let MUTED-D  = rgb("#a0a4a8")   // secondary on dark  — 7.0:1
#let MUTED-L  = rgb("#5f6368")   // secondary on light — 5.8:1

#let CODE-BG  = rgb("#202225")   // code block background
#let CODE-BR  = rgb("#34373b")   // code block border
#let RULE-L   = rgb("#d6d4d1")   // separator line on light bg (decorative)

// ── fonts ──────────────────────────────────────────────────────────────────
// If DESIGN.md specifies separate fonts for display vs body, define both
// (e.g. DISPLAY for big titles, SANS for body).
//
// Safe fonts on Linux/WSL (verify with: fc-list | grep -i "name"):
//   DejaVu Sans, DejaVu Sans Mono
//   Liberation Sans, Liberation Mono
//   Arial, Courier New (from Windows Fonts on WSL)
//
// Always list fallbacks: ("Preferred Font", "DejaVu Sans", "Arial")

#let DISPLAY = ("Georgia", "DejaVu Serif", "Times New Roman")  // display titles
#let SANS    = ("DejaVu Sans", "Liberation Sans", "Arial")     // body/UI
#let MONO    = ("DejaVu Sans Mono", "Liberation Mono", "Courier New")  // code

// ── helper: section label (eyebrow) ───────────────────────────────────────
#let lbl(body, dark: false) = text(
  size: 9pt,
  weight: "bold",
  tracking: 2pt,
  font: SANS,
  fill: if dark { ACC } else { ACC-L },
)[#upper(body)]

// ── helper: page footer (URL on the left, slide counter on the right) ─────
// Uses Typst's NATIVE page counter — no manual N/total, robust to add/remove
// slides. Apply via `#set page(footer: footer-block("github.com/me/repo"))`.
// For mixed light/dark slides, re-apply per slide with `dark: true|false`.
#let footer-block(url, dark: false) = context [
  #line(
    length: 100%,
    stroke: 0.5pt + if dark { CODE-BR } else { RULE-L },
  )
  #v(0.06in)
  #grid(
    columns: (1fr, auto),
    text(font: MONO, size: 9pt, fill: if dark { MUTED-D } else { MUTED-L })[#url],
    text(font: MONO, size: 9pt, fill: if dark { MUTED-D } else { MUTED-L })[
      \# #counter(page).display() / #counter(page).final().first()
    ],
  )
]

// ── helper: code block ────────────────────────────────────────────────────
#let codebox(body) = block(
  fill: CODE-BG,
  stroke: 0.5pt + CODE-BR,
  radius: 4pt,
  inset: (x: 14pt, y: 11pt),
  width: 100%,
)[
  #set text(font: MONO, size: 10.5pt, fill: FG-DARK)
  #body
]

// ── helper: accent divider line ───────────────────────────────────────────
#let divider(dark: false) = line(
  length: 100%,
  stroke: 1.5pt + if dark { ACC } else { ACC-L },
)
