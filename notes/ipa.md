# ipa

## Context

### Why this skill exists

In Italy, legal notifications sent via certified email (PEC) to public administrations are only valid if the PEC address is drawn from an officially recognised public register. An AI assistant that answers "the PEC of municipality X is Y" based on its training knowledge is legally unreliable: addresses change, registers are updated, and a lawyer acting on stale data may have a notification declared void.

The `ipa` skill solves this by performing a **live lookup** against the IPA catalogue (IndicePA, managed by AgID) at query time. It never relies on knowledge baked into the model — it returns the current address together with a verification URL, so the user can independently confirm the result.

### The legal framework

The obligation to use public registers for valid PEC notifications is anchored in **art. 16-ter, D.L. 179/2012** (converted by L. 221/2012, the so-called "Decreto Crescita 2.0"). This article defines which registers carry legal weight for electronic notifications. The three main ones are:

| Register | Establishing norm | Subjects |
|---|---|---|
| **ReGIndE** (General Register of Electronic Addresses) | Art. 16, D.L. 179/2012 | Public administrations (for judicial acts) |
| **IPA / IndicePA** | Art. 6-ter, CAD (D.Lgs. 82/2005) | Public administrations (fallback if not in ReGIndE) |
| **INI-PEC** | Art. 6-bis, CAD | Companies and professionals |

Key provisions:

- **Art. 16, D.L. 179/2012** — PAs are *required* (not merely allowed) to register their PEC address with the Ministry of Justice to enable electronic notifications.
- **Art. 28, D.L. 76/2020** — if a PA is not listed in ReGIndE, a notification sent to the PEC address published in IPA (art. 6-ter CAD) is still legally valid; where multiple addresses exist, the primary PEC indicated in the AgID guidelines applies.
- **Art. 3-ter, L. 53/1994** (introduced by D.Lgs. 149/2022, the "Riforma Cartabia", in force from 1 March 2023) — lawyers must use PEC when notifying parties that are legally required to have a digital domicile in public registers. PAs fall squarely into this category.

The Council of State (ruling 7170/2019) has held that a notification is valid only when the address is drawn from the register maintained by the Ministry of Justice, explicitly excluding any equivalence with other sources.

### Practical implication

A lawyer notifying a PA via PEC must use an address from a legally recognised register, and must be able to prove it at the time of the notification. Trusting an AI's memory for this is not acceptable practice. The skill fills the gap by querying the live IPA API and returning a citable, verifiable result.

## Why a skill — not just the website

The IPA web portal (`indicepa.gov.it`) has two critical limitations that make a skill necessary:

1. **The visual search cannot find sub-hierarchy entities.** Prefetture, questure, and similar bodies are registered in IPA as Aree Organizzative Omogenee (AOO) under a parent ministry (`m_it`), not as top-level entities. The website's search — by name, tax code, or IPA code — returns no results for "Prefettura di Palermo". The only way to retrieve the address is through the APIs.

2. **LLMs cannot generate correct deep-link URLs.** Even if a model knows the PEC address from training data, it cannot reliably construct the verification URL for a secondary-hierarchy entity (e.g. `.../elenco-aree-organizzative-omogenee/20608/scheda-area-organizzativa-omogenea/AC78FC0`). The `idEnte` and `Codice_uni_aoo` values must be retrieved live.

The skill uses both the official IPA web services (WS endpoints) and CKAN datastore queries on the IPA open data portal to retrieve information that the visual interface does not expose.

### Example output

Query: *"Qual è la PEC della Prefettura di Palermo?"*

```
La PEC della Prefettura - UTG di Palermo è:

  protocollo.prefpa@pec.interno.it

  Verifica su IPA: https://www.indicepa.gov.it/ipa-portale/consultazione/indirizzo-sede/ricerca-ente/elenco-aree-organizzative-omogenee/20608/scheda-area-organizzativa-omogenea/AC78FC0
```

This answer — including the live PEC and the exact verification URL — cannot be produced by a model relying on training knowledge alone.

## Links

- IPA official portal: [https://www.indicepa.gov.it](https://www.indicepa.gov.it)
- IPA open API (WS endpoints): referenced in `skills/ipa/references/`
- Art. 16, D.L. 179/2012 (PEC registration obligation for PAs) — [Normattiva](https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:decreto.legge:2012-10-18;179~art16)
- Art. 16-ter, D.L. 179/2012 (public registers valid for notifications) — [Normattiva](https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:decreto.legge:2012-10-18;179=) *(deep-link to this article not supported by Normattiva)*
- Art. 28, D.L. 76/2020 (IPA as fallback register) — [Normattiva](https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:decreto.legge:2020-07-16;76~art28)
- Art. 3-ter, L. 53/1994 (lawyers must use PEC for parties with digital domicile) — [Normattiva](https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:legge:1994-01-21;53=) *(deep-link to this article not supported by Normattiva)*
- Art. 6-bis, CAD — D.Lgs. 82/2005 (INI-PEC) — [Normattiva](https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:decreto.legislativo:2005-03-07;82~art6bis)
- Art. 6-ter, CAD — D.Lgs. 82/2005 (IPA / IndicePA) — [Normattiva](https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:decreto.legislativo:2005-03-07;82~art6ter)
- D.Lgs. 149/2022 — Riforma Cartabia (introduced art. 3-ter into L. 53/1994) — [Normattiva](https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:decreto.legislativo:2022-10-10;149=)
