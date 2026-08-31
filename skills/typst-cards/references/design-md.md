# Reading a DESIGN.md

[DESIGN.md](https://github.com/google-labs-code/design.md) is an open format for handing a visual identity to an agent: YAML front matter carrying machine-readable design tokens, then Markdown prose explaining how to apply them. When the user has one, it replaces the palette guesswork in Phase 2 — the tokens *are* the theme.

Two version numbers exist and they are not the same thing: the **format** is at `version: alpha` (the value written in the front matter), while the **tooling** — the `@google/design.md` CLI, linter and exporters — has its own release line. A file declaring `alpha` is current, not stale. Read the [spec](https://github.com/google-labs-code/design.md/blob/main/docs/spec.md) when a file uses something not covered here; it is short.

## Tokens are normative, prose is binding

The front matter gives values; the prose gives the rules for using them, often naming the same colour poetically ("a warm limestone") next to its systematic token (`neutral`). Take the numbers from the tokens and the *constraints* from the prose. The **Do's and Don'ts** section is the part most likely to be violated by an otherwise correct deck: "the accent is never a background fill", "the ground is the warm neutral, not pure white", "no more than two font weights per view". Those are hard limits on the card design, not suggestions — check the finished cards against that list before showing them.

A section listed under `omitted` is deliberately absent. Do not invent a replacement for it; fall back to the skill's own defaults and say so.

## What maps onto a card, and what doesn't

| Section | On a social card |
|---|---|
| `colors` | directly — background, text, accent, muted |
| `typography` | directly — but rescaled, see below |
| `spacing` | directly — `v()` steps and block insets |
| `rounded` | directly — `radius:` on blocks |
| Overview, Do's and Don'ts | as constraints on layout and tone |
| `components` | mostly not — buttons, chips, inputs, tooltips and their hover/pressed variants have no meaning in a static PNG. Borrow only a card-like component's `padding`/`rounded`/`backgroundColor`. |
| Elevation & Depth | rarely — shadows read poorly at 1080px; the section's *intent* (tonal layers vs shadows) is the usable part |

## Resolve references before writing `theme.typ`

Token values may be references: `backgroundColor: "{colors.surface}"`, `rounded: "{rounded.md}"`. Typst knows nothing about them — `rgb("{colors.surface}")` fails with *"color string contains non-hexadecimal letters"*. Walk the YAML tree and substitute every `{path.to.token}` with its primitive value first. The failure is loud, so an unresolved reference cannot reach a rendered card silently.

## Colours

Hex is the recommended default in the spec and the only form Typst's `rgb()` takes: named CSS colours (`cornflowerblue`) raise the same non-hexadecimal error. The spec also admits `rgb()`, `hsl()`, `oklch()`, `lab()` and `color-mix()`. Typst 0.14.2 has native `oklch()` and `rgb()` constructors, so those pass through; anything else — named colours, `color-mix()` — must be converted to hex before it lands in `theme.typ`.

## Typography: convert the units, then rescale

Three conversions, each with a trap.

**`fontSize`: px → pt is ×0.75, but do not stop there.** A DESIGN.md sizes type for a screen, where a 48px headline sits in a viewport over a thousand pixels wide. A card is 1080px seen small in a feed, and the same headline translated literally comes out timid while the 16px body drops to 12pt and stops being readable on a phone. **Keep the ratios between the levels, raise the absolute values** to the card scale the skill already documents (cover 42–50pt, section 28–34pt, body 14–16pt). The identity lives in the proportions and the families, not in the absolute pixel counts.

**`lineHeight` → `leading` is not a subtraction of 1.** CSS `lineHeight` is the whole line box; Typst's `leading` is the gap *added on top of* the glyph box, so translating `lineHeight: 1.1` as `leading: 0.1em` makes lines collide — and in Italian it shows first on the accents, which touch the line below. Subtract roughly 0.75 instead:

```typst
// lineHeight: 1.1 → leading: 0.35em     lineHeight: 1.6 → leading: 0.85em
#block[
  #set par(leading: 0.35em)
  #text(size: 48pt, weight: 600)[Two lines \ that do not collide]
]
```

Measured on a 40pt headline at 144ppi, `leading: 0.35em` gives an 87px line pitch against the 88px that `lineHeight: 1.1` prescribes. Close enough to trust, not close enough to skip looking: the exact figure depends on the font's cap-height, so read the render.

**`letterSpacing` → `tracking`, resolved against the size.** Typst wants an absolute length: `-0.02em` on a 48pt headline is `tracking: -0.96pt`. `fontWeight` maps straight across — `weight: 600` works as a number.

## Fonts are the step that fails quietly

A DESIGN.md names the brand's families, and those are exactly the ones a machine tends not to have: the spec's own example calls for Public Sans and Space Grotesk, and on a stock Linux box neither is installed. Typst emits `warning: unknown font family` and renders with a fallback — a warning, not an error, so the deck compiles and simply looks wrong. Check every `fontFamily` in the front matter with `fc-list | grep -i "<family>"` before generating, always declare a fallback chain, and tell the user which families were substituted. See "Font availability — two tiers" in SKILL.md for what is portable.

## Spacing and shapes

`spacing` and `rounded` convert with the same ×0.75 and are worth keeping as a named scale rather than scattering literals, so the deck inherits the brand's rhythm:

```typst
#let SP = (xs: 3pt, sm: 6pt, md: 12pt, lg: 24pt, xl: 48pt)   // 4/8/16/32/64px
#let ROUND = (sm: 3pt, md: 6pt)                              // 4px / 8px
```

The one judgement call: a 32px page margin is right for a web page and thin for a card, where the skill's own 0.5–0.7in margins do the breathing. Use the DESIGN.md scale for the *internal* rhythm — gaps between blocks, padding inside a surface — and the card geometry for the outer frame.
