---
name: cup-cig
description: Guide users monitoring Italian public procurement to extract detailed information from lists of CUP (Codice Unico di Progetto) and CIG (Codice Identificativo Gara). Use when the user wants to look up project metadata, financial status, or tender details for Italian public contracts.
compatibility: Requires curl, jq, bash, internet access. Bulk sources also need duckdb, unzip and iconv; resolving territorial codes at a date needs the opensituas CLI; querying published notices needs the anac-pl CLI; scripts/cig-fetch.sh needs agent-browser and timeout (GNU coreutils; macOS: brew install coreutils). OpenCUP API requires OPENCUP_API_CLIENT_ID and OPENCUP_API_CLIENT_SECRET environment variables.
license: CC BY-SA 4.0 (Creative Commons Attribution-ShareAlike 4.0 International)
metadata:
  version: "0.13"
  updated: "2026-08-17"
  author: "Andrea Borruso <aborruso@gmail.com>"
  tags: [api, open-data, procurement, cup, cig, italy, public-works]
---

# CUP-CIG

Use this skill to retrieve detailed information on Italian public projects and tenders
from CUP and CIG codes using open data sources.

> **IMPORTANT:** Always write `curl` commands on a **single line**. Multi-line `\`
> continuation breaks argument parsing in agent environments and will cause errors.

---

## Decision Tree — Which Source for Which Question?

```
User has a CUP
  │
  ├─ START HERE, ALWAYS: OpenCUP  (`references/opencup.md`)
  │    The registry: neutral, source-agnostic, answers for virtually
  │    every CUP. Gives the anagraphics AND tells you which monitoring
  │    system to try next — see below.
  │    If it does NOT resolve, the code may be a SUPERSEDED one: projects
  │    get merged and re-registered, documents record it as "già <CUP>",
  │    and the old code stops being published while its tenders stay in ANAC.
  │
  ├─ Financial monitoring / execution status?
  │    The three systems split BY FUNDING SOURCE, and you usually do not
  │    know the funding source in advance. Read it off OpenCUP first:
  │      DESC_TIPO_COPERTURA = COMUNITARIA + DESC_STRUMENTO naming a
  │        "MISSIONE … COMPONENTE …"        → PNRR      → ReGiS  (regis-italiadomani.md)
  │      DESC_TIPO_COPERTURA = COMUNITARIA, no PNRR mission
  │                                          → cohesion → OpenCoesione (opencoesione.md)
  │      DESC_TIPO_COPERTURA = STATALE / REGIONALE / ALTRA PUBBLICA,
  │        DESC_STRUMENTO naming an ordinanza or a piano OO.PP.
  │                                          → national → MOP `prg` (bdap-mop.md)
  │    Then CONFIRM by querying: the hint narrows the search, it does not
  │    replace it. A project financed from several sources sits in several
  │    systems, and coverage is partial everywhere.
  ├─ How much was actually PAID, per year?
  │    └─ BDAP MOP `sal` (SIOPE cannot answer: the CUP is in the OPI payment
  │       orders, but siope.it publishes only entity × spending-code aggregates)
  ├─ Where does the work fall?
  │    └─ BDAP MOP `loc` (also the resolver for the regional partitions)
  └─ Associated tenders (CIG)?
       ├─ ANAC dataset `cup`      (widest coverage, all sectors)
       ├─ BDAP MOP Gare via OData (public works only, adds bidder + amounts)
       └─ ReGiS `PNRR_Gare`       (PNRR only — and says WHY a CIG is missing)
       ⚠ the three do not fully agree: use the union when completeness matters

User has a CIG — branch on WHAT YOU NEED, not on the code shape
  ├─ A HANDFUL of CIGs and you want EVERYTHING about them?
  │    └─ `scripts/cig-fetch.sh` — one canonical JSON per CIG, ~10s each,
  │       no bulk download. Covers in one shot most of the branches below
  │       (CUP, metadata, award, lifecycle). Does NOT scale to set-wide
  │       questions: for those use the bulk datasets.
  ├─ Which CUP does it belong to?
  │    ├─ ANAC dataset `cup`      (widest coverage, SmartCIG included, N:N)
  │    ├─ BDAP MOP Gare via OData (public works only, adds bidder + amounts)
  │    └─ ReGiS `PNRR_Gare`       (PNRR only)
  ├─ Tender metadata, amount, CPV, outcome, place of execution?
  │    ├─ below-threshold → ANAC dataset `smartcig` (far fewer fields)
  │    └─ ordinary        → ANAC dataset `cig`      (the full record)
  ├─ Who won it, at what price?
  │    ├─ ANAC `aggiudicazioni` + `aggiudicatari` (all sectors, adds discount)
  │    └─ BDAP MOP Gare via OData (public works only, no download needed)
  ├─ What happened AFTER the award — SAL, payments, subcontracts,
  │  variants, suspensions, completion, sign-off?
  │    └─ ANAC lifecycle datasets → anac-lifecycle.md
  ├─ Full procedure: lots, parties, roles, contracts? → ANAC OCDS bulk
  └─ The published NOTICE itself — deadlines, tender documents, corrections?
       ├─ from 2024 on → ANAC PVL via `anac-pl` (live, searchable by CIG)
       └─ up to 2023   → SCP-MIT API (empty from 2024 on)
```

> **The `Z` prefix no longer identifies below-threshold CIGs.** It was the convention
> **until 31/12/2023 only**: in the `smartcig` monthly files it is the norm up to December
> 2023 and appears on **no record at all from January 2024 onwards**.
>
> Cause: ANAC decommissioned the SmartCIG service on 31/12/2023; since 01/01/2024 every
> CIG is issued through the certified digital procurement platforms (PCP) interoperating
> with BDNCP, so below-threshold codes are now indistinguishable in shape from ordinary
> ones (`B227609E1B`). Reference: ANAC-MIT delibera n. 582 of 13/12/2023.
>
> **Never infer the regime from the code shape** for anything issued from 2024 on — look
> the code up in the datasets instead. The old `Z` codes remain valid for historical
> records and stay searchable.

---

## Territorial attribution — never interchangeable

"Where is this CUP/CIG" has three different meanings — where the work is executed, where
the project falls, where the awarding entity sits — spread across four fields. Mixing them
attributes spending to the wrong municipality, silently. Always state which one you used.

| Question | Field | Source | Caveat |
|---|---|---|---|
| Where is it **executed**? | `luogo_istat` (6 digits) / `istat_comune` (9 digits) | ANAC `cig` / `smartcig` | declared per tender, and sometimes empty |
| Where does the **work fall**? | `Codice Regione`+`Provincia`+`Comune` | BDAP MOP `loc` | **one CUP can span many municipalities** — a minority, but some span dozens — and MOP gives **no share** |
| Where does the **work fall**, with a share? | region/province/municipality + **`Percentuale di Localizzazione`** | ReGiS `PNRR_Localizzazione` | PNRR only, but the **only source that lets you split an amount** across territories |
| Where does the **project** say it is? | `COMUNI`, `PROVINCE`, `REGIONI` | OpenCUP | single municipality only, and on an **older code vintage** than ANAC |
| Who **awards** it? | `cf_amministrazione_appaltante` → IPA | ANAC + IPA | the entity's seat, not the works' location |

`luogo_istat` does track execution rather than the entity's seat: a stazione appaltante with
several tenders often shows several distinct values. But for most of them it collapses to a
single municipality, which is exactly what makes it easy to mistake for the seat — and the
mistake is invisible until you aggregate.

### Four formats for the same thing

```
ANAC cig       luogo_istat      = 015146      6 digits, ready to use
ANAC smartcig  istat_comune     = 004021046   9 digits → take the LAST 6 (021046)
BDAP MOP loc   provincia+comune = 038 + 005   concatenate → 038005
OpenCUP        COMUNI           = 111067      6 digits, but often an older vintage
```

### Codes have a vintage — resolve them at a date

**Sources do not share the same version of the territorial registry** — and this includes
two sources of the same filière: for the same municipality **OpenCUP still returns the
2016-2026 code while ANAC returns the current one** (Sanluri: `111067` vs `117015`).

The clearest case:
**Sardinian municipalities changed ISTAT code en masse on 01/01/2026**, when the new
provinces instituted in 2025 took effect. ANAC publishes the **new** codes (`118002` Assemini,
`112064` Valledoria, `114006` Bitti), while ISTAT's own `Elenco-comuni-italiani.csv` still
carries the **old** ones (`092003`, `090079`, `091009`) and knows no `112`-`119` prefix.

So a code that looks invalid against that list may simply be **newer than the list**. Do
not discard it and do not call it a source error — resolve it at a date. The `opensituas`
CLI queries ISTAT SITUAS, which does carry them:

```bash
opensituas -o json cerca-codice comune Assemini | jq -r '.[] | "\(.["Codice Istat"]) [\(.["Data inizio"]) → \(.["Data fine"])]"'
# 092009 [17/03/1861 → 20/08/1974]
# 092003 [20/08/1974 → 01/01/2026]
# 118002 [01/01/2026 →  ]        ← current
```

The full old→new conversion table is one command away — report 105, columns `PRO_COM_T`
(before) and `PRO_COM_T_REL` (after):

```bash
opensituas -o json get 105 --from 01/01/2026 --to 31/12/2026 | jq -r '.[] | "\(.PRO_COM_T) \(.COMUNE) → \(.PRO_COM_T_REL)"'
```

> This is a general rule, not a Sardinian curiosity: municipalities merge and get
> renumbered every year. Before concluding that a source publishes broken codes, check
> whether your reference list is simply older than the source.

---

## Environment Variables

```bash
export OPENCUP_API_CLIENT_ID='...'
export OPENCUP_API_CLIENT_SECRET='...'
```

To verify without printing the values:

```bash
[[ -n "${OPENCUP_API_CLIENT_ID:-}" ]] && echo "ID is set" || echo "ERROR: OPENCUP_API_CLIENT_ID not set"
[[ -n "${OPENCUP_API_CLIENT_SECRET:-}" ]] && echo "SECRET is set" || echo "ERROR: OPENCUP_API_CLIENT_SECRET not set"
```

---

## The nine sources — index

Each source has its own reference file with endpoints, fields, verified quirks and working
commands. **Open the file for the source you are about to use**: the details below are
deliberately not repeated here, and guessing them is how the silent failures in *Common
Errors* happen.

| # | Source | Answers | Reference |
|---|---|---|---|
| 1 | **OpenCUP** | project registry: the full anagraphics of a CUP, and the dispatch hint telling you which monitoring system to query. API keys: a CUP, or a titolare PIVA (10-record cap). For anything set-wide use the **Parquet mirror on Source Cooperative** — queryable over HTTP, no credentials, no download — or the raw bulk archive | `references/opencup.md` |
| 2 | **BDAP / OpenBDAP (MOP)** | seven families keyed on CUP: projects, **tenders with CIG**, **payments per year**, bidders, cost plan, owners, geolocation | `references/bdap-mop.md` |
| 3 | **SCP-MIT** | published tenders and awards **up to 2023 only** — historical archive | `references/scp-mit.md` |
| 4 | **ANAC BDNCP** | the `cup` bridge — the widest CIG↔CUP mapping there is — plus `cig` and `smartcig` tender metadata | `references/anac-datasets.md` |
| 5 | **ANAC OCDS bulk** | the whole procedure as one object: lots, parties, roles, awards, contracts | `references/anac-ocds.md` |
| 6 | **ANAC lifecycle** | what happened after the award: SAL and certified payments, subcontracts, variants, suspensions, sign-off | `references/anac-lifecycle.md` |
| 7 | **ANAC PVL** | the published notice itself, from 2024 — the only live per-CIG lookup, with links to the tender documents | `references/anac-pvl.md` |
| 8 | **ReGiS / ItaliaDomani** | PNRR monitoring: third CUP↔CIG bridge, **why a CIG is missing**, and territorial **shares** | `references/regis-italiadomani.md` |
| 9 | **OpenCoesione / BDU** | cohesion-policy projects, 2021-2027 included — REST API without authentication, and the only source publishing **Parquet** for bulk membership tests | `references/opencoesione.md` |

Rules of thumb that hold across all nine: **OpenCUP always answers**, the monitoring systems
answer only for what they cover, and ANAC is where the tenders are regardless of funding.

---

## `scripts/cig-fetch.sh` — everything about a few CIGs, without bulk

The nine sources above are built for set-wide questions and mostly require downloading
monthly bulk files. When the question is about **a handful of specific CIGs**, this script
is the shorter path: it drives ANAC's public *dettaglio-cig* page through `agent-browser`,
clears the mosparo anti-spam control and saves the page's own JSON export.

```bash
scripts/cig-fetch.sh A0059785CC                      # one CIG → ./A0059785CC.json
scripts/cig-fetch.sh -o out/ -f cigs.txt             # batch from a list, one CIG per line
scripts/cig-fetch.sh --stdout A0059785CC | jq .      # single CIG straight into a pipe
```

What comes back is one object with the whole tender in it — `bando`, `aggiudicazione`,
`partecipanti`, `stazioneAppaltante`, `fontiFinanziamento`, `quadroEconomico`,
`statiAvanzamentoLavori`, `subappalti`, `varianti`, `sospensioni`, `collaudo` and more — so a
single call answers what would otherwise take four or five different bulk datasets. It
includes `bando.CUP`, which makes it a **CIG→CUP resolver** too.

Behaviour worth knowing:

- **Idempotent.** A `<CIG>.json` already on disk whose `.bando.CIG` matches is reported
  `SKIP` and not re-fetched. Use `--force` to override.
- **Validated.** The download is accepted only if `.bando.CIG` equals the requested code, so
  a wrong or truncated file is never left behind.
- **Batch-friendly.** The browser session is reused: 3 CIGs take about as long as 1 (~10s
  total). Failures do not stop the batch; the exit code is 1 if any CIG failed.
- **SmartCIG return less.** A pre-2024 `Z...` code leaves several sections empty that an
  ordinary CIG fills. That is the source, not a fetch failure.
- **A non-existent CIG costs ~56s** (two attempts) and reports `starting the search` — a
  misleading message: nothing is wrong with the click, the code simply has no page.
- Only accepts 10-character alphanumeric codes: passing a CUP exits 64 straight away.

Requires `agent-browser`, `jq` and `timeout`. Tune with `CIG_FETCH_STEP_TIMEOUT` (default 8s)
and `CIG_FETCH_ATTEMPT_TIMEOUT` (default 20s) on slow connections.

`scripts/test-cig-fetch.sh` checks the CLI contracts offline against a fake browser — no
network, about a second. Run it after touching the script.

⚠ It depends on the page's DOM (`#mosparo-box`, `button.export-json-btn`): if ANAC restyles
the page, the script breaks and the bulk datasets remain the stable route.

---

## Format traps across sources

| Source | Trap | Fix |
|---|---|---|
| BDAP CSV dumps | **latin-1**, delimiter `;`, no `charset` in the HTTP header | `iconv -f latin1 -t utf8 in.csv > out.csv` before DuckDB |
| BDAP `prg` | decimals with a **comma** | `REPLACE(col, ',', '.')` before casting |
| BDAP `gar`, `sal` | decimals with a **dot** — same system, different convention | no conversion; do not reuse the `prg` pipeline blindly |
| ISTAT comuni, POSAS | latin-1 | same `iconv` step |
| ISTAT comuni | column names change between yearly editions | detect columns heuristically, never hardcode |
| ANAC `cig` | text with **double-encoded UTF-8** (`÷` stored as `C3 83 C2 B7`, reads as `Ã·`) | decode twice where it appears |
| ANAC bulk, BDAP dumps | files from hundreds of MB to 3 GB | `Range` requests to inspect before pulling |
| ItaliaDomani (ReGiS) | **`HEAD` returns 404 on files that exist**; `Range` is ignored | probe with GET, inspect via `curl … \| head -c` |
| ItaliaDomani (ReGiS) | UTF-8-**SIG**: the BOM ends up in the first column name | strip the BOM, or let the CSV reader handle `utf-8-sig` |

---

## Definition of Done

A task is complete when:

- The correct source is selected based on the decision tree above.
- API call returns data (or a clear "no results" message).
- Output is readable (not a raw JSON blob) — use `jq` to format.
- For bulk sources: DuckDB query returns and formats results.

And none of these silent failure modes is left unchecked:

- every BDAP OData query carries an explicit `$top` — a bare 50 rows is a truncation, not a result;
- any total is counted client-side, never read from `__count`;
- when a territorial code is reported, **which** attribution it is — execution, project location, or awarding entity's seat — is stated;
- a code absent from the ISTAT list is resolved at a date before being called invalid;
- an empty OpenCUP body is reported as "CUP not found", not swallowed as a `jq` error;
- amounts aggregated across the CIG↔CUP join are de-duplicated, and amounts per municipality account for multi-municipality CUP.

---

## Common Errors

| Error | Cause | Fix |
|---|---|---|
| `401 Unauthorized` on OpenCUP | Wrong credentials or not set | Check `OPENCUP_API_CLIENT_ID`/`SECRET` |
| OpenCUP returns **HTTP 200 with an empty body**, `jq` errors out | The CUP is not published — the API does not 404 | Test `[[ -s file ]]` before parsing |
| A well-formed CUP does not resolve in OpenCUP | It may be a **superseded code** — projects get merged and re-registered | Search the documents for `già <CUP>`; the tenders stay in ANAC under the old code |
| `soggettotitolare/{PIVA}` keeps returning the same 10 records | 12 pagination params tested, all ignored server-side; result order unstable | Mirror: `WHERE PIVA_CODFISCALE_SOG_TITOLARE = '…'` |
| `soggettotitolare` answers `totcount: 10000` for a huge entity | `totcount` appears capped at 10.000, and the biggest titolari hold orders of magnitude more | Read it as «≥ 10.000»; count in the mirror |
| Empty results on OpenBDAP | CUP not in MOP dataset | Project may not have financial monitoring data |
| Exactly 50 rows returned | No `$top` passed — silent truncation | Always set `$top` explicitly |
| An ANAC dataset looks implausibly small | You pulled a monthly increment, not the full dump | Get `{dataset}_csv.zip` (no date prefix), then apply increments |
| Row counts in `*_logCsv.csv` look inflated | The log mixes CSV, JSON and TTL rows | Filter on the format column before reading counts |
| CSV dump returns **HTTP 200** and a tiny body `{"error": … "Attachment not found"}` | Used the OData resource id on the dump endpoint | Use the **package id** for `/datastore/dump/`; checking the status code is not enough, check `success` |
| OData returns HTTP 500 with an empty body | Used the package id on the OData endpoint | Use the **XML resource id** + `@rgs` |
| `__count` is `"0"` but rows exist | Known BDAP OData proxy defect | Count `.d.results` length, ignore `__count` |
| BDAP OData returns rows but **all projected fields are empty** | A guessed mangled field name — no error is raised | List the keys of one row and use the real names |
| A CUP is missing from BDAP MOP | MOP coverage is substantially incomplete — a miss is expected, not an anomaly | Use OpenCUP for anagraphics, ANAC `cup` for tenders |
| No results on SCP-MIT for a recent CIG | The archive stops at 2023 | Use the ANAC datasets; SCP-MIT is historical only |
| No results on SCP-MIT even for an old CIG | `stato` not passed — it is mandatory | Add `stato=3` to the form body |
| SCP-MIT Bandi have no CIG field | Only Esiti expose `cig` (with a trailing dash) | Query Esiti when you need the CIG |
| A 2024+ CIG has no `Z` but behaves as below-threshold | The `Z` convention ended on 31/12/2023 | Do not classify by code shape; look it up in `cig` vs `smartcig` |
| SSL error on SCP-MIT | Formerly a self-signed certificate; it validates as of 2026-08 | Retry without `-k` first; add it only if your CA bundle is outdated |
