---
name: difensore-civico-ti-scrivo
description: >
  Guides users step by step in drafting a formal complaint (segnalazione) to Italy's Digital
  Civic Defender (Difensore Civico per il Digitale, DCD) at AGID for violations of the CAD
  (Codice dell'Amministrazione Digitale) or other digitalization norms by public
  administrations. Use this skill whenever someone wants to: report an Italian PA to AGID;
  write to the Difensore Civico per il Digitale; complain about open data violations,
  non-machine-readable public data, inaccessible PA portals, missing or restrictive licenses
  on public data, captchas blocking automated access, unanswered data reuse requests (D.Lgs.
  36/2006 art. 5), failure to publish mandatory High Value Datasets (HVD, Reg. (UE) 2023/138),
  or a prior DCD complaint that got no response. Trigger even if the user does not name the
  skill — any Italian digital-rights complaint targeting a PA is a candidate.
---

# difensore-civico-ti-scrivo

Produces a ready-to-send formal *segnalazione* to Italy's Difensore Civico per il Digitale
(DCD) at AGID, under art. 17, comma 1-quater of the CAD (D.Lgs. 82/2005).

## Scope and constraints

**Funzione A only.** This skill covers violations of the CAD and other digitalization norms —
the DCD's main function. If the user describes an accessibility complaint (reclamo su
dichiarazione di accessibilità, L. 4/2004 — Funzione B), redirect them: the correct channel
is *exclusively* the link on the reported entity's own website, not AGID. Do not draft a
Funzione B complaint through this skill.

**Covered norms.** In addition to the CAD, this skill covers D.Lgs. 36/2006 (open data and
reuse) and EU regulations directly applicable in Italy — in particular **Reg. (UE) 2023/138**
(High Value Datasets — HVD), which requires publication of six dataset categories via
machine-readable API; obligations have been enforceable since 9 June 2024.

**One complaint per PA.** If multiple administrations are involved, produce one *segnalazione*
per administration.

## Common failure modes

These are the most frequent reasons a *segnalazione* fails or is dismissed. Check each before
drafting.

**Inadmissibility — complaint is not processed at all (art. 4 co. 3 Regolamento DCD)**
- Missing sender identity (full name + email/PEC): without these the complaint is inadmissible
  regardless of its merit. Remedy: always collect Group A in full before drafting.
- Missing DPR 445/2000 declaration: the statutory self-certification is a formal requirement.
  Remedy: always include the standard block; never omit it even if the user objects.

**Wrong channel — complaint reaches the wrong office**
- Accessibility complaints (L. 4/2004, Funzione B) sent here are not processed by the DCD;
  the user loses time and may miss the correct channel. Remedy: redirect immediately (see
  *Scope and constraints*).

**Premature complaint — DCD unlikely to proceed**
- Art. 5 D.Lgs. 36/2006 (unanswered reuse request): the DCD expects evidence that the user
  already sent a formal reuse request to the PA and received no response or a refusal. Without
  this prior step the complaint will likely be archived as premature. Remedy: ask Group C before
  drafting; if no prior request exists, advise the user to send it first.
- Prior DCD *segnalazione* unresolved: if the user already filed for the same PA and received a
  protocol number but no outcome, the new complaint must reference that number explicitly;
  otherwise the DCD may treat it as a duplicate and archive it.

**Weak evidence — complaint cannot be acted on**
- Vague description without URLs, dates, or observable facts: the DCD cannot invite the PA to
  remedy what it cannot identify. Remedy: insist on at least one URL and one specific date in
  Group B; if the user cannot provide them, note the limitation explicitly in the complaint text.

**Delivery failure — no legal proof of submission**
- Sending via ordinary email (not PEC and not the AGID web form) produces no legal proof of
  delivery; the DCD may never acknowledge receipt. Remedy: Step 4 covers the two valid channels;
  always remind the user before they send.

## Step 1 — Interview

Collect the required information before drafting. Ask in conversational turns — not all at
once. Start with the first two groups; add the rest once you understand the case.

**Group A — Sender identity** (required for admissibility, art. 4 co. 3 Regolamento DCD)
- Full name
- Capacity: *privato cittadino* / *rappresentante di associazione* (name + role) / *professionista* (name + profession)
- Email or PEC address for replies

**Group B — The problem**
- Which PA? (name, and the URL of the page or service at issue)
- What happened? Be specific: what did the user observe, what did they try, when?

**Group C — Prior requests** (ask if categories E or F seem relevant)
- Has the user already sent a reuse request (art. 5 D.Lgs. 36/2006) or FOIA to this PA?
  If yes: date sent, delivery proof available?
- Was there a previous DCD *segnalazione* about this PA? If yes: date, protocol number.

**Group D — Optional details**
- Attachments to mention (files the user has: PEC receipts, screenshots, prior
  correspondence — list names only)
- Confidentiality: does the user want their identity withheld from the reported PA?

## Step 2 — Identify the violation category

Read `references/categorie-violazioni.md`. Match the user's description to one or more of
the categories listed there. Each category maps to specific articles and provides adaptable
Italian legal language. Confirm the match with the user before drafting.

If the case spans multiple categories, include arguments for all of them in a single complaint.

## Step 3 — Draft the complaint

Produce the complaint in Italian, formal administrative register. Pull exact article text
and URLs from `references/normativa.md`. Use the adaptable language from
`references/categorie-violazioni.md` for the legal-argument section.

Every complaint must include (admissibility elements, art. 4 co. 3 Regolamento DCD):
- Identifying data of the sender
- Exact identification of the reported entity
- Declaration of responsibility under DPR 445/2000 (standard template below)

---

## Complaint structure

```
A: protocollo@pec.agid.gov.it
Oggetto: Segnalazione al Difensore Civico per il Digitale (art. 17, co. 1-quater CAD) –
         [brief violation description] – [PA name]
```

**Body:**

```
Spett.le Difensore Civico per il Digitale
Agenzia per l'Italia Digitale

[SENDER BLOCK]
Il/La sottoscritto/a [NOME], [QUALITÀ E ORGANIZZAZIONE], con la presente formula
segnalazione ai sensi dell'art. 17, comma 1-quater, del decreto legislativo 7 marzo 2005,
n. 82 (Codice dell'Amministrazione Digitale – CAD) per presunta violazione
[VIOLATION SUMMARY] da parte di [ENTE SEGNALATO].

[CONTEXT — 2–4 sentences: what the PA is, what service/page is concerned, why it matters]

[FACTS — specific, dated, verifiable: what the user observed, what they tried, what the
outcome was. Include URLs. Be concrete.]

[PRIOR REQUESTS — only if applicable: date of request, type, channel, deadline, outcome]

[LEGAL ARGUMENTS — drawn from references/categorie-violazioni.md for this category.
Cite each article with its Normattiva URL from references/normativa.md.]

[REQUESTS TO THE DCD]
Alla luce di quanto sopra, si chiede al Difensore Civico per il Digitale di:
1. valutare la presente segnalazione ai sensi dell'art. 17, co. 1-quater CAD;
2. ove ritenuta non manifestamente infondata, invitare [ENTE] a [SPECIFIC REMEDY];
3. comunicare gli esiti del procedimento al recapito sopra indicato;
4. assegnare un numero di protocollo per il seguito della procedura.

[CONFIDENTIALITY — only if requested]
Per motivate esigenze di riservatezza ai sensi dell'art. 4, co. 5, del Regolamento AgID
(D.T. n. 270/2022), chiedo che il mio nominativo non sia riportato nelle comunicazioni
verso il soggetto segnalato. Qualora ciò non fosse proceduralmente possibile, chiedo di
essere preventivamente informato/a prima dell'inoltro.

[ATTACHMENTS — only if any]
Si allegano: [list filenames].

[DPR 445/2000 DECLARATION — always include]
Il/La sottoscritto/a dichiara, ai sensi del D.P.R. 28 dicembre 2000, n. 445, di essere a
conoscenza delle sanzioni penali previste in caso di falsità in atti e dichiarazioni mendaci
e attesta che le informazioni fornite nella presente segnalazione sono veritiere.

Distinti saluti,

[NOME]
[QUALITÀ / ORGANIZZAZIONE]
[EMAIL / PEC]
```

## Output format rules

The complaint is sent via PEC or web form to a PA. PEC clients are often basic and do not
render Markdown. Apply these rules strictly:

- **Plain text only.** No Markdown: no `**bold**`, no `### headers`, no `- bullet` lists
  with hyphens rendered as markup. Use plain prose and simple numbered lists (1. 2. 3.).
- **No horizontal rules.** Do not use `---` or `***` to separate sections. Leave a blank
  line between sections instead.
- **Subject line: max 100 characters.** Keep it to: "Segnalazione al Difensore Civico per
  il Digitale – [violation in 5–8 words] – [PA name]". Cut ruthlessly.
- **Links as numbered footnotes.** Never embed URLs in the text. Instead, write `[1]`, `[2]`
  etc. at each citation point, and collect all URLs at the very end under a plain-text
  "Riferimenti" section, one per line:

  ```
  Riferimenti
  [1] https://www.normattiva.it/...
  [2] https://www.agid.gov.it/...
  ```

- **Gender agreement.** Match "Il sottoscritto / La sottoscritta" to the sender's gender.
- **Italian accented characters.** Always use proper Unicode accented letters: à, è, é, ì,
  ò, ù. Never substitute with apostrophe (a', e', i', o', u'). This applies throughout the
  entire complaint, including legal article citations.

## Step 4 — Sending instructions

After the draft, tell the user:

- **Recommended channel — PEC:** send to `protocollo@pec.agid.gov.it`. Keep both the
  *ricevuta di accettazione* and *ricevuta di avvenuta consegna* as legally valid delivery
  proof. PEC is preferred over the form because it leaves a traceable paper trail in the
  sender's hands.
- **Alternative — AGID web form:** <https://www.agid.gov.it/it/form/difensore-civico-digitale>
  (requires SPID or CIE login). The form collects the same information but provides no
  receipt to the sender.
- The DCD has **90 days** to conclude the procedure (Regolamento art. 8). No response within
  90 days = automatic archiving (no further notification). The clock is suspended: up to 20
  days if AgID consults internal structures; during **10–20 August** and **25 December–1
  January**.
- One *segnalazione* per PA. If multiple PAs are involved, send separately.

## What to expect after submission

Tell the user what happens next, to set realistic expectations:

1. **Pre-istruttoria (art. 5 Regolamento):** The DCD reviews admissibility. If the complaint
   is inadmissible or irricevibile (too vague, wrong channel, duplicate), it is archived
   silently with no notification.

2. **Istruttoria (art. 6):** If the complaint passes, the DCD may request information from
   both the sender and the PA, with a 15-day peremptory deadline. Cooperate promptly.

3. **Transmission to Direttore Generale (art. 18-bis CAD):** If the DCD finds the complaint
   "non manifestamente infondata", it forwards the file to AgID's Direttore Generale, who can:
   - assign a peremptory deadline to the PA to comply;
   - report the violation to the PA's disciplinary office and performance evaluation body;
   - impose a fine of **€10,000–€100,000** (art. 18-bis co. 5).

4. **Realistic outcome:** In most cases the PA receives a formal invitation to comply and
   does so within the assigned deadline. Monetary sanctions are the exception, not the rule.
   The procedure does not give the user an enforceable right to the data — it is an
   administrative oversight channel, not a court order.

5. **No news = archived:** If 90 days pass with no communication, the complaint was archived.
   The user can file a new complaint (Category F) if the violation persists.
