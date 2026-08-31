# ReGiS / ItaliaDomani: the PNRR monitoring system

The third bridge between CUP and CIG, and the one that explains absences. Bulk CSV, no API,
no authentication. Base path:

```
https://www.italiadomani.gov.it/content/dam/sogei-ng/opendata/{FILE}.csv
```

Verified live on 2026-08-12 — **check before trusting any published list of these files**,
three of the seven names documented elsewhere returned 404:

| File | Size | Content |
|---|---|---|
| `PNRR_Progetti` | 317 MB | projects: title, financing by source, implementing body, mission/component |
| `PNRR_Gare` | 111 MB | **CUP + CIG per tender** — the third CIG↔CUP bridge, PNRR only |
| `PNRR_Localizzazione` | 66 MB | **CUP → territory with a share percentage** |
| `PNRR_Soggetti` | 674 MB | project subjects |

Official field dictionaries (`.ods`, `.xlsx`, `.pdf` in one zip) sit next to the data:

```
https://www.italiadomani.gov.it/content/dam/sogei-ng/opendata/PNRR_Gare_Metadati.zip
https://www.italiadomani.gov.it/content/dam/sogei-ng/opendata/PNRR_Soggetti_Metadati.zip
```

The catalogue pages (`/it/it/catalogo-open-data/{slug}.html`) do **not** expose the CSV link
in their HTML — only the metadata zip — so build the CSV URL from the pattern above.

> **`HEAD` lies here, and it does not even lie consistently.** It returns **404 on files
> that exist and download fine with GET** — and repeating the identical request flips the
> answer: five consecutive `HEAD` on `PNRR_Progetti` returned 404, 200, 404, 404, 404,
> and `PNRR_Localizzazione` behaves the same way, while `PNRR_Gare` and `PNRR_Soggetti`
> answered 200 every time. The edge nodes are not configured alike, so **which node serves
> you decides the answer**. Never probe these URLs with `curl -I`, and never conclude a file
> is missing from a 404 on `HEAD`.
>
> The corollary is about method, not about this server: a single probe per file is not a
> measurement here. Whichever answer you get first will look like the rule, and it is not.
>
> The server also **ignores `Range`**: asking for the first bytes downloads the whole file,
> and the response is `200`, not `206`. To inspect the head of a file, pipe a plain `GET`
> through `head -c` and let the pipe close the connection.

> **Akamai blocks these CSVs from some networks — and the rule is about the caller, not
> the request.** From ordinary consumer networks a plain `GET` works with no headers at
> all. From datacenter egress it does not, and there the fix is to send a browser
> `User-Agent` **and** a `Range` header together: either alone gets a 403, and so does
> neither.
>
> But headers are not always enough, which is the part that costs time: from a GitHub
> Actions runner (Azure) even the correct pair returns 403, an `AkamaiGHost` "Access
> Denied" page. And the allow-list is finer than "cloud provider" — on Scaleway the same
> request passes from a Serverless Function and fails from a Serverless Job.
>
> Practical consequence: **do not conclude anything about this source from a single
> network.** Working from a laptop proves nothing about CI, and a 403 in CI proves nothing
> about the file.
>
> `Range: bytes=0-` requests the whole file while keeping the header present, which is
> what makes a full download work despite the quirk above.
>
> Working setup in `ondata/liberiamoli-tutti`: a Node function on `fr-par` fetches both
> CSVs with those headers and streams them to a public Scaleway bucket
> (`@aws-sdk/lib-storage` `Upload`, `ACL: public-read` — bucket ACL does not propagate to
> objects); the GitHub workflow calls the function, then reads the CSVs from the bucket.
> Function and bucket URLs live in repository secrets, never in the code.

### `PNRR_Localizzazione` — the only source that splits a project across territories

Fields: submeasure, `CUP`, `Codice Locale Progetto`, region / province / municipality (both
code and name), address, postcode, and — the one that matters — **`Percentuale di
Localizzazione`**.

This closes a gap left open everywhere else: BDAP MOP `loc` tells you a CUP spans several
municipalities but **never how to split the amount**, so any per-municipality sum
double-counts. ReGiS publishes the share. When you need spending by territory for PNRR
projects, this is the only defensible way to compute it.

Two things to handle: the `Regione` code includes **`000`**, the national scope used when a
project has no territorial detail; and the `CUP` column contains junk values (`N/A2` among
them), so filter on the CUP pattern before joining.

### Why the three CUP↔CIG bridges disagree — the documented reason

This is not a data glitch, it is how the system was designed. Per the ItaliaDomani open
data FAQ, and confirmed in exchanges with MEF, a procedure enters ReGiS in **two** ways:

- **retrieved from ANAC through interoperability** — it carries a `CIG`;
- **entered directly by the Soggetto Attuatore / RUP**, when the law allows skipping the
  CIG — it carries a `Codice Procedura Utente` instead.

Either way the CUP-CLP-procedure link is identified by `Codice Interno PDA`.

Crucially, **the association is not automatic**: the proposal to let ANAC↔ReGiS
interoperability carry the CUP-CIG link without the operator having to confirm it was
considered and **not adopted** — partly over ANAC data-quality concerns, partly because
some tenders may relate to accessory services whose spending sits outside the project.

Three consequences you will meet in the data:

- a CIG that ANAC associates to a PNRR CUP may be **absent from ReGiS** — either awaiting
  association, or deliberately excluded by the RUP as outside the project;
- a procedure may exist in ReGiS **with no CIG at all**, legitimately;
- several PNRR measures involve **no tender whatsoever** — staff hiring, financial
  instruments, research, training, tax credits, grants to firms or individuals.

So when the bridges diverge, do not assume one is wrong. Report which source you used, and
prefer the union when you need completeness.

### Why `PNRR_Gare` is worth knowing

19 columns, including `CUP`, `CIG`, `CIG Accordo Quadro`, `Codice Locale Progetto`,
`Importo Complessivo Gara`, `Importo Aggiudicazione`, `Data Aggiudicazione Definitiva`,
`Descrizione Procedura di Aggiudicazione` and the submeasure classification.

**The two channels are visible in the data, and mutually exclusive** — which is what lets you
tell them apart row by row:

| Origin | How to recognise it |
|---|---|
| **from ANAC via interoperability** — the large majority | `CIG` filled, no `Codice Procedura Utente` |
| **entered by the Soggetto Attuatore** — a small but significant minority | `Codice Procedura Utente` filled, no `CIG` |

No row carries both, so the test is unambiguous. Per the official dictionary, `Codice Procedura Utente` is "un codice
inserito manualmente dal soggetto attuatore … non richiamato in automatico attraverso i
servizi di interoperabilità con ANAC", and `Codice interno PDA` is assigned by ReGiS to
identify the award procedure — it is **the key to the subcontractors dataset when there is
no CIG**.

The field no other source has is **`Descrizione Motivo Assenza CIG`**: when a tender carries
no CIG, ReGiS says **why**, with an explicit reason per row. The two commonest are worth
knowing because they mean opposite things: «temporaneo mancato recupero del CIG da ANAC» is a
**synchronisation gap** between the two systems — the CIG exists, ReGiS just has not pulled it
yet — while grants under art. 12 l. 241/1990 have **no CIG by law**. The rest are employment
contracts and other exclusions under d.lgs. 50/2016 and 36/2023.

This turns "the CUP has no CIG" from a dead end into an answerable question.

> **`CIG Accordo Quadro` is the "CIG padre"** — the code identifying a whole framework
> agreement or convention, issued to the central purchasing body, whose awarded amount is
> the global value of the agreement. Do not sum it together with the child CIGs.

> Encoding is **UTF-8-SIG** (BOM `EF BB BF`), delimiter `;`, licence CC-BY 4.0.

