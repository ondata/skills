// ─── theme-starter.typ ────────────────────────────────────────────────────
// Starter template. Adjust values to the context or DESIGN.md.
// Copy or rename this file to `theme.typ` in the same folder, then import it
// in slides.typ with: #import "theme.typ": *

// ── palette ────────────────────────────────────────────────────────────────
// Edit these values based on user palette or DESIGN.md.
// If DESIGN.md has named tokens (primary, secondary...), map them here.

#let BG-DARK  = rgb("#0d1117")   // primary dark background
#let BG-LIGHT = rgb("#f6f8fa")   // light background
#let BG-WHITE = rgb("#ffffff")   // pure white

#let ACC      = rgb("#58a6ff")   // accent on dark background  ← change first
#let ACC-L    = rgb("#0969da")   // accent on light background ← change second

#let FG-DARK  = rgb("#e6edf3")   // text on dark
#let FG-LIGHT = rgb("#1c2128")   // text on light
#let MUTED-D  = rgb("#8b949e")   // secondary on dark
#let MUTED-L  = rgb("#656d76")   // secondary on light

#let CODE-BG  = rgb("#161b22")   // code block background
#let CODE-BR  = rgb("#30363d")   // code block border

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

// ── helper: slide counter (carousels) ─────────────────────────────────────
// Usage: #ctr(2, 6) → "2 / 6" at bottom right
#let ctr(n, total, dark: false) = align(right)[
  #text(size: 9pt, fill: if dark { MUTED-D } else { MUTED-L }, font: SANS)[#n / #total]
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
