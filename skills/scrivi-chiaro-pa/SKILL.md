---
name: scrivi-chiaro-pa
description: >
  Write, rewrite, or review Italian public administration content in plain language
  (linguaggio chiaro), applying the Designers Italia language guide. Use this skill whenever
  someone needs to: draft or simplify a PA text (avviso, lettera al cittadino, pagina web
  istituzionale, email, comunicato, post social, newsletter, modulo, messaggio di errore o di
  conferma); remove bureaucratese (burocratese) from a text; check a PA text for clarity,
  accessibility, inclusiveness, or tone; choose the right tone of voice for a citizen-facing
  digital service (registration, payments, password recovery, search results, blog). Triggers
  include "scrivi in linguaggio chiaro", "semplifica questo avviso", "riscrivi per i
  cittadini", "questo testo è troppo burocratico", "scrivi un post per il Comune", even if
  the user does not name the skill — any request to produce or improve citizen-facing Italian
  PA communication is a candidate.
---

# scrivi-chiaro-pa

Helps Italian public administrations (and anyone writing on their behalf) communicate clearly with people, applying the *Guida al linguaggio della Pubblica Amministrazione* by Designers Italia.

All output is in **Italian** (unless the user asks for another language). These instructions are in English; the rules and examples in `references/` preserve the original Italian wording where it matters.

## Source and attribution

Rules are adapted from the [Guida al linguaggio della Pubblica Amministrazione](https://docs.italia.it/italia/designers-italia/writing-toolkit/it/bozza/index.html) (Designers Italia — Team per la Trasformazione Digitale / AgID), published as a draft ("bozza") and licensed [CC-BY 4.0](https://github.com/italia/writing-toolkit/blob/master/LICENSE). When the user asks where a rule comes from, cite this guide.

## Modes

Pick the mode from the user's request; if ambiguous, ask.

1. **Draft** — write a new text from scratch, given topic, audience, and channel.
2. **Rewrite** — take an existing PA text and rewrite it in plain language, preserving its legal and factual meaning.
3. **Review** — audit a text and report problems without rewriting it (unless the user then asks for the fix).

## Core principles (always apply)

- **Answer the citizen's question first.** Before writing, identify what the reader needs to know or do, and lead with it. Answer: chi, cosa, dove, come, quando.
- **Short and simple.** Short sentences, short paragraphs. Most readers are on a phone. Do not repeat the same information in different places — link instead.
- **Active, direct verbs.** *"Registrati sul sito"*, not *"La registrazione può essere effettuata sul sito"*. Avoid impersonal forms (*"È possibile iscriversi…"*).
- **No bureaucratese.** Avoid nominalizations in "-zione"/"-mento", archaic formulas (*"ad uopo"*, *"nelle more di"*), and jargon. Prefer everyday words: the glossary lists the most common offenders and their plain alternatives.
- **Concrete examples.** An example explains more than a long abstract explanation.
- **Norms in footnotes, not in the flow.** Summarize what a law means for the reader; put the exact reference in a note with a link (e.g. Normattiva permalink). Never write like *"ex art. 20 comma 2 e 3 della legge n. 247/2012"* in body text.
- **Inclusive language.** Feminine forms for office holders who are women (*la sindaca*, *la ministra*), "persone con disabilità", no stereotypes or generalizations by origin, religion, gender.
- **Tone follows context.** A payment confirmation, a password recovery, and a blog post need different tones. Match the reader's state of mind.

## Workflow

### Step 1 — Frame the job

Establish (ask only for what is missing and material):

- mode (draft / rewrite / review);
- content type and channel: web page, avviso/lettera, email or PEC, social post, newsletter, form or UI microcopy (buttons, errors, confirmations), blog post, attached document;
- audience (all citizens, businesses, professionals, a specific group);
- for rewrites/reviews: the original text.

### Step 2 — Load the relevant references

| Content type | Read |
|---|---|
| Any text, always | `references/stile-di-scrittura.md` + final glossary pass (`references/glossario-parole-pa.md`) |
| Web page, avviso, lettera, document | `references/struttura-e-leggibilita.md` |
| Form, UI microcopy, service touchpoint (registration, payment, recovery, search, area personale) | `references/tono-di-voce.md` + usability section of `references/struttura-e-leggibilita.md` |
| Social post, newsletter, images/video, editorial planning | `references/canali-e-redazione.md` |
| Blog post | `references/tono-di-voce.md` (blog scenario) + `references/stile-di-scrittura.md` |

### Step 3 — Choose the tone of voice

For citizen-facing service texts, match the situation to one of the nine scenarios in `references/tono-di-voce.md` (or interpolate between the closest ones): identify the reader's likely state of mind, then adopt the corresponding response approach.

### Step 4 — Write or rewrite

Apply the style, structure, and tone rules. When rewriting:

- preserve legal and factual meaning exactly — simplify the language, never the obligations, deadlines, or conditions;
- keep every normative reference, but move it to a note with the full name of the norm and a link;
- keep proper names, dates, amounts, and protocol numbers verbatim;
- match the output format to the channel (e.g. plain text for a letter or PEC, markdown-free; short lines and a strong first sentence for social).

### Step 5 — Final pass

1. Scan the text against `references/glossario-parole-pa.md` and replace or fix every term it flags.
2. Run the checklist below; fix what fails.

## Final checklist

- [ ] The first sentence answers the reader's main question or states the required action
- [ ] Sentences and paragraphs are short; no information is duplicated
- [ ] Verbs are active and direct; no impersonal or passive bureaucratic forms
- [ ] No unexplained acronyms: full name first, acronym after (only first letter capitalized, with exceptions: PA, UE, IVA, SPID, GU, MEPA, IRPEF, PM)
- [ ] Numbers, dates, times, percentages follow the rules in `references/stile-di-scrittura.md`
- [ ] Normative references are summarized in the text and cited precisely in notes with links
- [ ] Language is inclusive (feminine forms, "persone con disabilità", no stereotypes)
- [ ] Links have a clear destination ("Leggi la scheda X", never "clicca qui")
- [ ] Tone matches the scenario and the reader's state of mind
- [ ] Titles ≤ 65 characters, summary ≤ 150 characters (web content)

## Review mode output

Report findings as a list, most severe first. For each: quote the passage, name the problem, cite the rule area (style / structure / tone / glossary / accessibility), and propose the fixed wording in Italian. Close with an overall assessment and the three highest-impact fixes.
