# OpenCUP: Project Metadata

**Base URL:** `https://api.sogei.it/rgs/opencup/o/extServiceApi/v1/opendataes/cup/{CUP}`
**Auth:** IBM API headers (`x-ibm-client-id`, `x-ibm-client-secret`)

### Look up a single CUP

```bash
curl -sS -X GET "https://api.sogei.it/rgs/opencup/o/extServiceApi/v1/opendataes/cup/J87G22000360002" -H "x-ibm-client-id: ${OPENCUP_API_CLIENT_ID}" -H "x-ibm-client-secret: ${OPENCUP_API_CLIENT_SECRET}" -H "Accept: application/json" | jq '.results[0]|{cup:.CUP, anno:.ANNO_DECISIONE, stato:.COD_STATO_PROGETTO, soggetto:.DESC_SOGGETTO, settore:.DESC_SETTORE_INTERVENTO, area:.DESC_AREA_INTERVENTO, importo:.IMPORTO_COSTO_PROGETTO, regione:.LOC_REGIONI}'
```

### Look up a list of CUPs

Given a file `cups.txt` (one CUP per line):

An unknown CUP returns an **empty body**, which makes `jq` fail — so a list loop must
guard against it, or one bad code kills the run:

```bash
while IFS= read -r cup; do echo "=== $cup ==="; curl -sS -o /tmp/cup.json -X GET "https://api.sogei.it/rgs/opencup/o/extServiceApi/v1/opendataes/cup/$cup" -H "x-ibm-client-id: ${OPENCUP_API_CLIENT_ID}" -H "x-ibm-client-secret: ${OPENCUP_API_CLIENT_SECRET}" -H "Accept: application/json"; [[ -s /tmp/cup.json ]] && jq '.results[0]|{cup:.CUP, stato:.COD_STATO_PROGETTO, soggetto:.DESC_SOGGETTO, settore:.DESC_SETTORE_INTERVENTO, importo:.IMPORTO_COSTO_PROGETTO}' /tmp/cup.json || echo "not found"; done < cups.txt
```

### Look up by owner entity — the second key, capped at 10 records

The API's entire query surface is **two keys** — a CUP and a titolare's PIVA; no other field can be a predicate. The titolare key returns that entity's CUPs.

```bash
curl -sS -X GET "https://api.sogei.it/rgs/opencup/o/extServiceApi/v1/opendataes/soggettotitolare/00269510624" -H "x-ibm-client-id: ${OPENCUP_API_CLIENT_ID}" -H "x-ibm-client-secret: ${OPENCUP_API_CLIENT_SECRET}" -H "Accept: application/json" | jq '{totcount, CurrentPage, numpages, results: (.results|length)}'
```

Response: `{totcount, CurrentPage, numpages, results[]}` — the same full per-CUP records, in a
pagination envelope of **10 records per page**. All of it measured on 2026-08-15:

| Behaviour | Evidence |
|---|---|
| `totcount` is trustworthy below 10.000 | COMUNE DI TORRECUSO (`00269510624`, 31 CUPs in the mirror) → `totcount: 31` |
| **Only the first 10 records are retrievable** | 12 pagination params tested and **all ignored** (`CurrentPage`, `page`, `pagina`, `p`, `pageNum`, `pageSize`, `offset`, `start`, `skip`, `limit`, `size`, `rpp`): every call answers `CurrentPage: 1` with the same 10 CUPs (set-identical, verified comparing sorted lists). `numpages` is also arithmetically wrong: 31 CUPs → `numpages: 3`, which covers 30 |
| **`totcount` appears capped at 10.000** | AGEA (1.557.932 CUPs in the mirror) and MIMIT (1.016.757) both answer exactly `totcount: 10000` |
| Result order is not stable | repeated identical calls returned the same 10 CUPs in a different array order — deduplicate by `CUP`, never by position |
| Unknown PIVA → HTTP 200 with an empty body | same guard as for CUPs; the **documentation's own example** PIVA `01206740324` behaves this way |

What survives is one question — «how many CUPs does this titolare own?» (up to 10.000) — plus a
10-record sample, in ~1,4 s: per single call this route is actually **faster** than the mirror.
The whole set is what it cannot serve: on Torrecuso the mirror's
`WHERE PIVA_CODFISCALE_SOG_TITOLARE = '00269510624'` returned 31/31 in 4,9 s — one query; the API
would need the pages it does not serve (4 pages × 1,4 s ≈ 5,6 s if paging worked). Note `PIVA` is
not the sort key, so the mirror filters by scan (~5 s) instead of row-group pruning (~2 s).

### What the response actually contains

**69 fields per project**, of which the example above shows eight. The ones worth knowing:

| Field | Why it matters |
|---|---|
| `CF_PIVA_SOGGETTO` | fiscal code of the owning entity — the join key to every other source |
| `COMUNI`, `PROVINCE`, `REGIONI` | territorial codes (**see the vintage warning below**) |
| `LOC_COMUNI`, `LOC_PROVINCE`, `LOC_REGIONI` | the same, as names |
| `IMPORTO_COSTO_PROGETTO` / `IMPORTO_FINANZIAMENTO` | total cost vs funding — not always equal |
| `NUMERO_CUP_COLLEGATI` | linked projects: a CUP↔CUP graph |
| `DESC_NATURA`, `DESC_TIPOLOGIA_INTERVENTO`, `DESC_SETTORE_INTERVENTO`, `DESC_SOTTO_SETTORE_INTERVENTO`, `DESC_CATEGORIA_INTERVENTO` | the CUP classification already decoded — no need to parse the code |
| `DATA_GENERAZIONE` | when the CUP was issued (`YYYYMMDDhhmmss`) |
| `CF_BENEFICIARIO` | masked (`****`) when it is a natural person |

There is **no CIG here**: OpenCUP describes the project, not its tenders.

> **OpenCUP's territorial codes lag behind ANAC's.** For CUP `J87G22000360002` the field
> `COMUNI` is `111067` — Sanluri's code from 28/04/2016 to 01/01/2026 — while its current
> code is `117015`. Do not compare these codes with ANAC's without resolving both at a
> date, or the same municipality will look like two.

### Error behaviour

- **Unknown CUP → HTTP 200 with an empty body** (0 bytes), not a 404 and not an empty
  result set. `jq` fails on it. Check the body length before parsing:

```bash
[[ -s /tmp/out.json ]] && jq '.results[0]' /tmp/out.json || echo "CUP not found (empty body)"
```

- **Missing or wrong credentials → HTTP 401** with `"Invalid client id or secret."`

### OpenCUP as the dispatcher

Because it is the **registry** and not a monitoring system, OpenCUP is the one neutral entry
point: it answers regardless of how the project is financed, and two of its fields tell you
where the monitoring data will be. Measured across three samples:

| `DESC_TIPO_COPERTURA` | `DESC_STRUMENTO` | Monitored in |
|---|---|---|
| `COMUNITARIA` (alone or combined) | names a PNRR mission/component, e.g. «MISSIONE 4 ISTRUZIONE E RICERCA COMPONENTE 1» | **ReGiS** |
| `COMUNITARIA` | no PNRR mission | **cohesion** → OpenCoesione |
| `STATALE`, `REGIONALE`, `ALTRA PUBBLICA` | an ordinanza, a «PIANO TRIENNALE OO.PP.», a «PIANO OPERE PUBBLICHE», or `ASSENTE-` | **MOP**, if monitored at all |

Evidence: 10 reconstruction CUPs, all `STATALE`/`REGIONALE`/`ALTRA PUBBLICA` with ordinanze
or piani as instrument, scored **0/10 in ReGiS, 0/10 in OpenCoesione, 5/10 in MOP, 10/10 in
ANAC `cup`**. Four CUPs taken from `PNRR_Gare` all came back `COMUNITARIA` with a PNRR
mission in `DESC_STRUMENTO`.

**Treat it as a hint that orders your queries, not as a verdict.** Half of the reconstruction
CUPs were in no monitoring system at all while still having tenders in ANAC — so when the
question is "which tenders", go to ANAC `cup` directly and skip the dispatch.

### Coverage: is every CUP here?

Almost. Measured on a **full** reconstruction dataset — every one of its 3.481 CUPs queried:
**3.457 resolved (99,3%)**, 24 did not. Two random samples of 100 and 10 had come back
100% earlier, which is why a small sample will tell you "always".

OpenCUP is the **registry**, while MOP, ReGiS and OpenCoesione are *monitoring* systems each
holding only their own share: absence from those says nothing, absence from OpenCUP is rare
and worth investigating rather than accepting.

### A CUP can be replaced — look for the code it superseded

This is the first thing to check when a well-formed CUP does not resolve. Projects get
merged or re-registered, and the **new code supersedes the old ones**, which stop being
published while surviving in documents and datasets. Publication decrees state it plainly:

> «SISMA 2016 – Ordinanza Speciale … **CUP: B48E21000140001 (già B17H21003520001 –
> B47H21004700001)**»

Verified: `B48E21000140001` is in OpenCUP (Consorzio di Bonifica delle Marche, 13,9 M€),
both superseded codes are not — **although ANAC still holds 13 CIG each** for them, because
the tenders were run under the old codes.

Practical consequences:

- a "missing" CUP may be a **predecessor**: search the source documents for `già <CUP>`
  before concluding anything;
- source files often keep both, sometimes in the **same cell** (`X – Y – Z`), so splitting a
  multi-code cell by pattern can turn one project into three;
- historical CUPs remain the right key for the tenders of their own era.

Of the 24 unresolved CUPs above, 4 are exactly this case. For the remaining 20 — 10 of which
do have tenders in ANAC — no explanation was found; some have suspicious shapes
(`G27B18000000000`) and may be transcription errors that still pass a format check. For one
of them the OpenCUP **web page also answers «non disponibile»**, so it is not an API-only
gap.

One documented caveat from the source itself: not all project natures are said to be
published as open data — some PNRR service-acquisition projects supposedly have no CUP here.
**This appears superseded**: 8 of 8 CUPs from PNRR submeasure M1C1 «Infrastrutture digitali»
resolved, all with nature «ACQUISTO O REALIZZAZIONE DI SERVIZI».

### Without API credentials (web page fallback)

The project page at `https://opencup.gov.it/portale/progetto/-/cup/{CUP}` is publicly
accessible but returns HTML. Use a browser or a headless fetch tool for scraping.

---

## Parquet mirror on Source Cooperative — query it without downloading

**This is now the fastest way to ask anything set-wide**, and it needs neither credentials nor a
download. onData publishes a faithful Parquet conversion of the bulk archive; DuckDB reads it over
HTTP with range requests, pulling only the row groups it needs.

Base: `https://data.source.coop/ondata/opencup/`

The base URL is the HTTPS face of an **S3 bucket**: cloud URI `s3://eu-central-1.opendata.source.coop/ondata/opencup/`, endpoint `data.source.coop`. The HTTPS form used throughout this file is the verified recipe here; the `s3://` URI is the documented cloud address for tools speaking the S3 protocol. The mirror's own [README](https://source.coop/ondata/opencup/README.md) documents layout, examples and provenance — read it before trusting an aggregation.

Two structural facts worth knowing: `CUP` is a **true primary key** in `progetti` — 11.942.784 rows, as many distinct values — and all four files cover the same 11.942.784 projects, none a subset of another. Each file is sorted on its own access key, so one lookup in `progetti` touches **one row group out of 120** (one of 228 in `fonti-copertura`) — this is why 1.000 random CUPs cost barely more than 10.


| File | Rows | Size | Sorted by | Content |
|---|---:|---:|---|---|
| `progetti.parquet` | 11.942.784 | 703 MB | `CUP` | the 62 columns of the projects archive |
| `localizzazione.parquet` | 13.595.165 | 38 MB | territory | CUP × territory |
| `fonti-copertura.parquet` | 22.806.427 | 29 MB | `CUP` | CUP × funding source |
| `soggetti.parquet` | 54.323 | 2 MB | name | titolare × richiedente pairs |

```bash
# one CUP, from a 703 MB remote file, in ~2,4 s
duckdb -c "SELECT * FROM 'https://data.source.coop/ondata/opencup/progetti.parquet' WHERE CUP = 'J87G22000360002';"

# set-wide question the API cannot answer: projects in a municipality (~1 s)
duckdb -c "SELECT count(*) FROM 'https://data.source.coop/ondata/opencup/localizzazione.parquet' WHERE CODICE_COMUNE = '082053';"

# join two remote files: cost quartile in Rome, 223.788 projects (~4 s)
duckdb -c "SELECT quantile_cont(p.COSTO_PROGETTO, 0.75) FROM 'https://data.source.coop/ondata/opencup/localizzazione.parquet' l JOIN 'https://data.source.coop/ondata/opencup/progetti.parquet' p USING (CUP) WHERE l.CODICE_COMUNE = '058091';"
```

Every file carries provenance and caveats in its own Parquet metadata — read them before trusting an
aggregation:

```bash
duckdb -c "SELECT key::VARCHAR, value::VARCHAR FROM parquet_kv_metadata('https://data.source.coop/ondata/opencup/localizzazione.parquet');"
```

**What it is and is not.** A faithful conversion — no column renamed, no value altered, no row
dropped — of the **2026-08-06 snapshot**. It is therefore *older than the API*: a CUP registered
after that date is in the API and not here. Use it for set-wide work, use the API for freshness.

**Five traps, all measured, all preserved from the source:**

- `localizzazione` is **1:N and carries no percentage shares**: 960.107 CUP (8%) span several
  territories, so summing project costs by municipality counts them more than once;
- when a project is supra-municipal the territorial codes are **`-1`** and the labels become
  `TUTTI` (comune) / **`TUTTE`** (provincia, regione) — note the gender, a filter on
  `PROVINCIA = 'TUTTI'` returns nothing while 467.094 rows match `'TUTTE'`. Only 95,35% of rows
  reach an actual municipality, and `-1` survives a cast to integer;
- **all codes are strings**: 92% of province and municipality codes start with a zero, `021108` is
  not `21108`; same for the ATECO hierarchy, where `47.8` is a level and not a decimal;
- **not every project is in Italy**: `STATO` has 195 distinct values and 33.904 rows (0,25%) are abroad (Spain, Germany, UK, France…) — filter by country too, or a per-region sum silently drops them;
- `soggetti` is **not one row per body**: 54.323 rows for 28.851 distinct titolari, because it pairs
  titolare with richiedente. Joining on `SOGGETTO_TITOLARE` multiplies rows by 1,88.

### Measured — same question, API vs mirror (2026-08-15)

Compare **equal work**, not equal calls:

| Question | API | Parquet mirror |
|---|---|---|
| one CUP | ~2,0 s | ~2,4 s |
| 10 CUPs | 18,0 s sequential; **17,9 s with 10 parallel calls — zero gain, the gateway serializes per credential** | 2,0 s, one query |
| 1.000 CUPs | ~30 min at the measured 1,8 s/CUP | 3,1 s, one query (1000/1000 found) |
| all 31 CUPs of a titolare (Torrecuso) | **unreachable**: pagination ignored, one call yields 10 of 31 in 1,4 s; had paging worked, 4 calls ≈ 5,6 s | 4,9 s, 31 of 31, one query |
| aggregate the whole set | not expressible — no filters, no listing | 8,9 s, `GROUP BY` region over 13,6 M rows |

At small N the API is not slower — for a single titolare call it is faster. The asymmetry is
capability and marginal cost: the per-CUP route pays ~1,8 s **per CUP, always**, and the titolare
route stops at 10 records; one SQL query goes 2,0 s → 3,1 s between 10 and 1.000 CUPs, because the
file is sorted by `CUP` and DuckDB prunes row groups from the Parquet statistics. Break-even sits
at N≈10 and the gap only widens. Rule: **one CUP and freshness → API; any set → mirror.**

## Bulk open data — the whole archive, no credentials

The API answers one CUP at a time. The **Parquet mirror above** answers set-wide questions without a
download and should be tried first; reach for the raw archive when you need the source files
themselves, a snapshot fresher than the mirror, or the XML variant. No authentication, no rate limit,
plain HTTP.

**Index page:** `https://www.opencup.gov.it/portale/web/opencup/accesso-agli-open-data`

Files live in Liferay's document library, so URLs carry a UUID:
`https://www.opencup.gov.it/portale/documents/{groupId}/{folderId}/{Name}.zip/{uuid}`.
The `?t=…` query string on the page links is a cache-buster — **drop it**, the URL works
without it. Verified with `HEAD` on 2026-08-15 (sizes are the `Content-Length` of the zip):

### By entity — the four that matter

| File | Size | Last-Modified | URL (append to `https://www.opencup.gov.it/portale/documents/21195/299152/`) |
|---|---|---|---|
| `OpendataProgetti.zip` | 2,20 GB | 2026-08-06 | `OpendataProgetti.zip/7384382b-679a-0380-c750-ce40779b59d7` |
| `OpendataLocalizzazione.zip` | 249 MB | 2026-08-06 | `OpendataLocalizzazione.zip/ac230d13-23a0-5929-8778-d34c21c9a7a4` |
| `OpendataFontiCopertura.zip` | 162 MB | 2026-08-06 | `OpendataFontiCopertura.zip/229bb5a8-cb28-cb64-dfd8-44ebac4b3693` |
| `OpendataSoggetti.zip` | 3,2 MB | 2026-08-06 | `OpendataSoggetti.zip/411e1e80-bce0-d085-bb96-b8036deb590f` |

`Progetti` is the anagraphics — the bulk equivalent of what the API returns per CUP.
`Localizzazione`, `FontiCopertura` and `Soggetti` are the 1:N satellites, and they are the
answer to questions the API cannot serve set-wide (which CUPs are in municipality X, which
are funded by instrument Y). Note the asymmetry: `Soggetti` is three orders of magnitude
smaller than `Progetti` — it is the entity registry, not one row per project.

### Everything in one file, and the regional splits

| File | Size | URL |
|---|---|---|
| `OpendataComplessivo.zip` | **3,37 GB** | `documents/21195/299152/OpendataComplessivo.zip/e2ed40f1-54ef-9a36-6d49-a1349175e500` |

Also published per macro-area, in **two formats** — `OpendataCsv{Area}.zip` and
`OpendataXml{Area}.zip`, with `{Area}` ∈ `Centro`, `Isole`, `NordEst`, `NordOvest`, `Sud`.
Their UUIDs are on the `dettaglio-opendata-{centro|isole|nord-est|nord-ovest|sud}` pages;
scrape the `href` rather than hardcoding, they change when the file is republished.

### Companion files you will need

| File | What for | URL (under `.../documents/21195/0/`) |
|---|---|---|
| `Tabelle+decodifica+classificazioni+opencup.zip` | decode the classification codes (settore, sottosettore, categoria, natura) | `Tabelle+decodifica+classificazioni+opencup.zip/ab457d6b-ae2c-8aef-697c-9abfd2e5a914` |
| `Metadati.xlsx` | field-by-field record layout | `Metadati.xlsx/379fbe11-e297-c7a9-ebe9-567d911e12a5` |
| `Opendata+xsd.zip` | XSD schema of the XML variant | `Opendata+xsd.zip/5c72365b-3949-4716-82cb-3c4d74eec8ae` |

Plus thematic extracts, all one-off snapshots — not kept in step with the main archive:
`File+CUP+opencup+pnrr_PNRR+febbraio+2024_1.zip` (PNRR, Feb 2024),
`Dataset-progetti-emergenza-covid-al-30.04.2021.zip`, `Incentivi+ad+unità+produttive.zip`,
`Zone+franche+urbane+-+OpenCUP.rar`.

### Practical notes

- **Update cadence**: the four entity files and `Complessivo` all carry the same
  `Last-Modified` day (2026-08-06), so they are republished as one batch. Check
  `Last-Modified` with `HEAD` before re-downloading — it is the only freshness signal, there
  is no changelog and no version in the filename.
- `HEAD` works and `Content-Length` is honest, so you can size a download before starting it.
- A browser `User-Agent` is safer than curl's default on this portal, as with ANAC.
- **Not verified here**: the contents of the archives — encoding, delimiter, column names,
  whether one zip holds one CSV or many. Inspect before writing a loader, and expect the
  Italian-portal defaults (latin-1, `;`, comma decimals) until proven otherwise.
- The bulk archive is a **different vintage from the API**: it is a periodic snapshot, so a
  CUP registered after the last publication date is in the API and not in the zip.

