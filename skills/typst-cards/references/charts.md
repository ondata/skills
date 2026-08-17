# Charts on cards — gribouille

Data charts inside a card, drawn by [gribouille](https://m.canouil.dev/gribouille/), a grammar-of-graphics library for Typst (same author as the full-bleed pattern this skill credits). Everything below was compiled and looked at on **gribouille 0.6.0 + typst 0.14.2**; the version pair matters, the API is young.

## Prerequisite: one network fetch

The first compile downloads `gribouille`, plus `cetz` and `oxifmt`, from Typst Universe into Typst's package cache (`~/.cache/typst/packages` on Linux; the location differs on macOS and Windows). It needs network once; after that it is offline. Whenever a deck has charts, check it alongside the binary in "Prerequisites — verify Typst".

```typst
#import "@preview/gribouille:0.6.0": *
```

## The API surface lives upstream, not here

The library ships ~50 geoms and the docs are regenerated on every release with an [`llms.txt`](https://m.canouil.dev/gribouille/llms.txt) index plus a `.llms.md` companion for each page (e.g. `reference/geoms/geom-point.llms.md`). **Read those for anything beyond the recipe below** instead of guessing function names — a frozen list in this file would rot within a release. This document only pins what is specific to putting a chart on a social card.

## Call shape

`plot()` takes everything as named arguments; layers are a **tuple**, so a single layer needs a trailing comma. Data is a **list of row dicts**, not columns.

```typst
#let data = (
  (cat: "Open", n: 62, lab: "62%"),
  (cat: "Restricted", n: 24, lab: "24%"),
  (cat: "Closed", n: 14, lab: "14%"),
)

#plot(
  data: data,
  mapping: aes(x: "cat", y: "n"),
  layers: (
    geom-col(fill: ACC),
    geom-text(mapping: aes(label: "lab"), size: 13pt, colour: BG, anchor: "east"),
  ),
  scales: scales(x: scale-discrete(limits: ("Closed", "Restricted", "Open"))),
  coord: coord-flip(),
  labels: labels(x: none, y: none),
  theme: theme-minimal(ink: FG, paper: BG, text: element-text(size: 13pt)),
  width: 6.4in, height: 3.2in,
)
```

Passing `aes(...)` positionally — `plot(data, aes(...))`, the ggplot2 habit — fails with `unexpected argument`. It goes through `mapping:`.

## Sizing: absolute lengths only, and the plot is rigid

`width` and `height` reject ratios: `width: 100%` errors with *"width/height must be resolved to concrete lengths before rendering"*. So the usable width has to be computed from the layout pattern:

| Pattern | Page 1:1 | Minus | Usable width |
|---|---|---|---|
| Margined | 7.5in | 2 × 0.55in margin | **6.4in** |
| Full-bleed | 7.5in | 0.9in left inset + 0.55in right | **6.05in** |

The plot is one unbreakable block, and the two patterns fail differently when it does not fit — the same split the skill already documents:

- **Margined**: the overflow spills onto a real extra page. A card whose caption vanished onto page 2 looks *fine* on page 1; only the page count betrays it.
- **Full-bleed**: `block(height: 100%)` clips silently, no warning, exit 0.

So after every compile: the PNG count must equal the number of cards, **and** Phase 4 must actually read the images. Delete stale PNGs before recompiling, otherwise leftovers from a previous run inflate the count and fake an overflow that is not there.

## Brand mapping

`theme-minimal()` takes `ink` (all text and rules) and `paper` (the background). Wire them to the deck tokens and the chart stops looking like a foreign object:

```typst
theme-minimal(ink: FG-DARK, paper: BG-DARK)              // chart on a dark card
theme-minimal(ink: FG-LIGHT, paper: rgb(0, 0, 0, 0))     // transparent: sits on a full-bleed colour band
```

Inside the full-bleed `slide()` helper the chart is just another element of the body — only the width changes:

```typst
#slide(fill: BG-DARK, dark: true, {
  text(size: 31pt, weight: 900)[Datasets published]
  v(0.25in)
  plot(
    data: data, mapping: aes(x: "year", y: "n"),
    layers: (geom-col(fill: ACC),),
    labels: labels(x: none, y: none),
    theme: theme-minimal(ink: FG-DARK, paper: BG-DARK, text: element-text(size: 13pt)),
    width: 6.05in, height: 3.6in,
  )
  v(1fr)
})
```

Two more things follow the deck rather than the theme:

- **Fonts are inherited** from the page's `#set text(font: ...)`. Omit it and axis labels come out in Typst's default serif while the card is sans — the same two-tier portability caveat in SKILL.md applies to plot text.
- **Colours stay inside the 2–3 the deck already uses.** For a categorical scale pass the brand accent plus neutrals explicitly, `scale-discrete(palette: (...))`; the built-in default is not your palette.

## Card-specific settings

**Raise the theme text size.** The default tick labels are sized for a document page and read small on a 1080px card seen on a phone. `theme-minimal(..., text: element-text(size: 13pt))` cascades to every label; sizes can also be ratios (`80%`) relative to the parent.

**Drop the axis titles.** `labels(x: none, y: none)` — on a card the headline already says what the axis is, and the space is better spent on the plot.

**Label directly, don't legend.** A legend eats card width and forces a colour-to-category round trip. Put the value on the mark instead, via `geom-text`. Two things about it:

- the `label` aesthetic must map to a **string** column. Point it at a number and the layer draws nothing — no error, no warning. Precompute a formatted string (`"62%"`) in the data.
- `anchor: "east"` with the background colour puts the label *inside* the bar. With `anchor: "west"` the label sits outside and the longest one is clipped by the panel edge unless you widen the scale limits.

**Horizontal bars need `coord-flip()`**, not swapped aesthetics. Mapping `x: "n", y: "cat"` renders axes with no bars at all — again silently.

**Category order is alphabetical, not data order.** To sort bars by value, state the order explicitly in the `scales:` argument of `plot()`: `scales: scales(x: scale-discrete(limits: ("Closed", "Restricted", "Open")))` — smallest first puts the longest bar at the bottom under `coord-flip()`.

## When not to use a chart

A card is not a dashboard. One chart per card, one message per chart. Three big numbers set in the deck's display font usually beat a three-bar chart — reach for gribouille when the *shape* of the data is the point (a trend, a distribution, a gap), not when it is three values that could just be typed.
