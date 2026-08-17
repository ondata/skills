# OpenBDAP: Financial Monitoring

**Portal:** `https://bdap-opendata.rgs.mef.gov.it`
**Auth:** None
**Field name for CUP:** `Cccodice_cup_1267962549`
**Full dataset map:** `references/bdap-mop-datasets.md`

### Two ids per dataset — not interchangeable

BDAP exposes each dataset through two different identifiers. Using one on the wrong
channel fails, and in one direction it fails **silently**:

| Goal | Endpoint | Id to use |
|---|---|---|
| Point query | `/ODataProxy/MdData('{ID}@rgs')/DataRows` | **XML resource id** |
| Full CSV dump | `/SpodCkanApi/api/3/datastore/dump/{ID}.csv` | **package id** |

For «Progetti Opere Pubbliche MOP - Totale» (the dataset used in the examples below):

```
package id      c76e90f7-eea5-4f32-8767-6b60e3505a1d   → CSV dump
XML resource id bda1676b-62ab-44b7-8f9a-ca93b8534488   → OData queries
```

Resolve both ids for any MOP dataset — `prg` projects, `gar` tenders (CUP **and** CIG),
`sal` payments, `pga` bidders, `pdc` cost plan, `sog` owners, `loc` geolocation:

```bash
curl -sS "https://bdap-opendata.rgs.mef.gov.it/SpodCkanApi/api/3/action/package_search?q=opere+pubbliche&rows=200" | jq -r '.result.results[] | select(.name|test("^spd_mop_")) | . as $p | (.resources[]? | select(.format=="XML") | "\($p.name) | \($p.title) | pkg=\($p.id) | odata=\(.id)")'
```

**BDAP is not a CKAN**: it is a Java application (`/SpodCkanApi/`) exposing a *partial*
CKAN-compatible API, so several habits from real CKAN portals do not carry over:

- `package_show?id={dataset_name}` returns `success: false` and a null result — it only
  accepts the **package UUID**. Use `package_search` to go from name to UUID.
- `package_list` works and returns 3.849 dataset names.
- `resource_show`, `site_read` and `status_show` are **not implemented** (Tomcat 404).
- in `package_search`, `q=opere+pubbliche` works while longer multi-word queries return
  no results.

Real CKAN endpoints, where the usual idioms do apply, are ANAC (`ckan_version` 2.6.8)
and IPA (2.9.8).

**Base URL (OData, Progetti MOP - Totale):**
`https://bdap-opendata.rgs.mef.gov.it/ODataProxy/MdData('bda1676b-62ab-44b7-8f9a-ca93b8534488@rgs')/DataRows`

### Seven families, all keyed on the CUP

Projects are only one of them. See `references/bdap-mop-datasets.md` for the full id map
and the OData field names.

| Family | Answers | Carries CIG? |
|---|---|---|
| `prg` | status, sector, planned vs actual cost, funding sources | no |
| `gar` | **tenders: CUP + CIG + winner + awarded amount** | **yes, 100% filled** |
| `sal` | **payments per CUP and year — money actually disbursed** | no |
| `pga` | who bid, with RTI role | yes |
| `pdc` | cost plan per year, planned vs realised | no |
| `sog` | project owner: fiscal code, legal form, address | no |
| `loc` | CUP → region / province / municipality | no |

`sal` is the only source that answers *«how much was actually paid for this project»* at CUP
level. **SIOPE cannot — but not for the reason usually given.**

The OPI standard behind SIOPE+ *does* define `codice_cup` and `codice_cig_siope` (AgID
*Regole tecniche OPI*), so the CUP travels inside the payment orders. What is missing is in
the **published** data: [siope.it](https://www.siope.it) exposes payments and receipts
aggregated **by entity and spending code**, never by project. Do not write "SIOPE holds no
CUP" — write that SIOPE does not publish at project granularity.

Access, verified 2026-08: open to anyone, no registration (DM MEF 47989 of 30/05/2014, under
art. 8 c. 3 of DL 66/2014). Per-entity statements, aggregates, comparisons, historical series
and a bulk **Download** section by year or entity group. It is a session-based Struts web app
driven by JavaScript form posts — **no REST API**, and the `developers.italia.it` SIOPE entry
now redirects to a generic page. Institutions needing a different cut can request it in
writing from RGS-IGEPA Ufficio 4.

A civic re-publication exists — [dataciviclab/open-siope](https://github.com/dataciviclab/open-siope),
~18.000 entities 2021-2026 as public Parquet on GCS, queryable in DuckDB — but it inherits
the same granularity: entity and accounting code, no CUP.

> **MOP does not cover every CUP — because monitoring is split by funding source, not by
> type of work.** Italy runs **three** monitoring systems (d.lgs. 229/2011, l. 178/2020):
> **ReGiS** for PNRR projects (published on ItaliaDomani), **BDU** for cohesion policy **up
> to 2014-2020** (published on OpenCoesione), and **MOP** for national investments covered
> by neither (published on OpenBDAP). Two moving parts to keep in mind: MOP was **extended**
> beyond nationally-funded public works and now also carries PNC projects and others under
> various decrees, not necessarily public works; and **cohesion 2021-2027 goes to ReGiS**,
> not to BDU. A project financed from several sources lands in several systems at once. All
> three feed the Banca Dati delle PA (art. 13 l. 196/2009), but that flow is internal to
> RGS. A single monitoring system is being built and is not ready.
>
> Measured: of 100 random CUPs from a post-earthquake reconstruction dataset, **49 appear in
> MOP**. Progress stage shifts the odds — 39,7% for projects still in design (phases 1-6),
> 69,7% once works have started (phases 7-9) — but does not explain the rest. **Absence from
> MOP is not absence of the project**: check ReGiS and OpenCoesione, and fall back to OpenCUP
> for the anagraphics and to ANAC `cup` for the tenders.

### Finding the right regional file for a CUP

Every family except `loc` is split into 21 partitions, so a CUP lookup seems to need 21
queries. It does not: **Localizzazione is national and unpartitioned**, so it works as a
resolver.

```bash
# step 1 — CUP → region code(s), one query on the national Localizzazione
curl -sS "https://bdap-opendata.rgs.mef.gov.it/ODataProxy/MdData('c4cce647-cec4-4b60-a8ab-d308ecfba743@rgs')/DataRows?\$filter=Cccodice_cup_1267962549%20eq%20'B24B13000160001'&\$top=1000&\$format=json" | jq -r '[.d.results[].Cccodice_region1532212456] | unique[]'
# → 02  → the Valle d'Aosta partition (regNN follows ISTAT region codes)

# step 2 — query that region's `gar` / `sal` resource id, from the reference file
```

Three cases to handle explicitly:

- **multi-region CUP** — 1.976 of 541.329 (0,365%), up to 20 regions: repeat step 2 for
  each region returned;
- **CUP not in Localizzazione** — 210 of 541.539 (0,04%): these are works with no
  municipal localisation, look them up in the **`reg00` «Territorio Nazionale»** partition;
- **`reg00` is not the national total** — a total exists only for `prg`, and it carries no
  territorial column at all.

> A CUP spread over several municipalities is common — 27.982 CUP (5,17%), up to 93
> municipalities. **No dataset splits the amount between them**: attributing a project's
> cost to one municipality, or summing per municipality, double-counts.

### Query by CUP

```bash
curl -sS "https://bdap-opendata.rgs.mef.gov.it/ODataProxy/MdData('bda1676b-62ab-44b7-8f9a-ca93b8534488@rgs')/DataRows?\$filter=Cccodice_cup_1267962549%20eq%20'H87H21003670005'&\$top=100&\$format=json" | jq '[.d.results[]|{cup:.Cccodice_cup_1267962549, descrizione:.Ccdescrizione_cu902475141, stato:.Ccdescrizione_s1176782119, ente:.Ccdescrizione_ti177583083, settore:.Ccsettore_inter1475973826, costo:.Cccosto_lavori_e582037416}]'
```

### Query by entity fiscal code (without knowing CUPs)

```bash
curl -sS "https://bdap-opendata.rgs.mef.gov.it/ODataProxy/MdData('bda1676b-62ab-44b7-8f9a-ca93b8534488@rgs')/DataRows?\$filter=Cccodice_fiscal1934873127%20eq%20'02246660985'&\$top=100&\$format=json" | jq '[.d.results[]|{cup:.Cccodice_cup_1267962549, ente:.Ccdescrizione_ti177583083, stato:.Ccdescrizione_s1176782119}]'
```

### Common OData filters

| What | Filter |
|---|---|
| By CUP | `$filter=Cccodice_cup_1267962549 eq '{CUP}'` |
| By fiscal code | `$filter=Cccodice_fiscal1934873127 eq '{CF}'` |
| Active projects | `$filter=Cccodice_stato_1426672593 eq 'A'` |
| Closed projects | `$filter=Cccodice_stato_1426672593 eq 'C'` |
| By sector | `$filter=Ccsettore_inter1475973826 eq 'STRADALI'` |

Combine filters with `and`/`or`.

### Counting rows — and the silent 50-row truncation

**Always pass `$top` explicitly.** Without it the proxy truncates the response to
**50 rows** with no warning and no flag: an incomplete result looks exactly like a
complete one.

Neither counting mechanism of the OData protocol works on this proxy:
`$inlinecount=allpages` returns `__count: "0"` even when rows are returned, and
`/DataRows/$count` returns HTTP 500. Get the count by asking for more rows than you
expect and counting client-side — this is exact, not an estimate:

```bash
curl -sS "https://bdap-opendata.rgs.mef.gov.it/ODataProxy/MdData('bda1676b-62ab-44b7-8f9a-ca93b8534488@rgs')/DataRows?\$filter=Cccodice_stato_1426672593%20eq%20'A'&\$top=100000&\$format=json" | jq '.d.results|length'
```

Paginate large datasets with `$skip` + `$top`. Note that `row_id` restarts from 0 in
every response: it is a page index, not a stable record identifier.

### Looking up many CUPs at once

Do not loop one HTTP call per code. `$filter` accepts `or`, so a whole batch fits in a
single request — faster, and it survives being interrupted:

```bash
F=$(awk '{printf "%sCccodice_cup_1267962549 eq %s%s%s", (NR>1?" or ":""), "\047", $0, "\047"}' cups.txt)
enc=$(python3 -c "import urllib.parse,sys; print(urllib.parse.quote(sys.argv[1]))" "$F")
curl -sS "https://bdap-opendata.rgs.mef.gov.it/ODataProxy/MdData('bda1676b-62ab-44b7-8f9a-ca93b8534488@rgs')/DataRows?\$filter=$enc&\$top=5000&\$format=json" | jq -r '.d.results[] | [.Cccodice_cup_1267962549, .Ccdescrizione_s1176782119] | @tsv'
```

### Field names: read them, never guess them

The mangled suffix is stable per column name across datasets and regions, but it cannot be
derived from the column name. **Guessing produces empty values, not an error**: the query
returns rows and every projected field is blank, which reads exactly like "no data". Before
querying a family you have not used, list the keys of one row:

```bash
curl -sS "https://bdap-opendata.rgs.mef.gov.it/ODataProxy/MdData('{RESOURCE_ID}@rgs')/DataRows?\$top=1&\$format=json" | jq -r '.d.results[0] | keys[]'
```

---

## Dataset map and OData field names

## BDAP MOP — dataset map and OData field names

Companion to the BDAP section of the skill. The Monitoraggio Opere Pubbliche (MEF-RGS)
publishes **seven families** of datasets, all keyed on the **CUP**. Every family except
Localizzazione is split into 21 territorial partitions.

All facts below were verified live on 2026-08-11.

## How to reach a dataset

Each dataset has **two non-interchangeable ids** (see the warning in SKILL.md):

```bash
## full CSV dump  → package id
https://bdap-opendata.rgs.mef.gov.it/SpodCkanApi/api/3/datastore/dump/{PACKAGE_ID}.csv

## point queries  → OData resource id, with the @rgs suffix
https://bdap-opendata.rgs.mef.gov.it/ODataProxy/MdData('{RESOURCE_ID}@rgs')/DataRows?$filter=…&$top=1000&$format=json
```

Regenerate this whole map with:

```bash
curl -sS "https://bdap-opendata.rgs.mef.gov.it/SpodCkanApi/api/3/action/package_search?q=opere+pubbliche&rows=200" | jq -r '.result.results[] | select(.name|test("^spd_mop_")) | . as $p | (.resources[]? | select(.format=="XML") | "\($p.name) | \($p.title) | pkg=\($p.id) | odata=\(.id)")'
```

## The seven families

| Family | Content | Carries CIG? |
|---|---|---|
| `prg` | Projects: owner, status, sector, planned/actual cost, funding sources | no |
| `gar` | **Tenders: CUP + CIG + winner + base and awarded amounts** | **yes, 100% filled** |
| `sal` | **Payments per CUP and year** — money actually disbursed | no |
| `pga` | Tender participants, with RTI role | yes |
| `pdc` | Cost plan per year: planned vs realised | no |
| `sog` | Project owners: fiscal code, legal form, address | no |
| `loc` | **Geolocation: CUP → region / province / municipality** | no |

## Territorial partitioning — and the one national resolver

`reg01`…`reg20` follow the **ISTAT region codes** (`reg08` = Emilia-Romagna). Two
exceptions matter:

- **`reg00` is not the national total.** It holds works with no municipal localisation —
  large infrastructure. Measured on the `gar` family: 44.796 tender rows but only **165
  distinct CUP**, of which 152 are absent from Localizzazione.
- **A national «Totale» dataset exists only for `prg`** (`spd_mop_prg_mon_opere_01_9999`),
  and it carries **no territorial column** — 48 columns, none for region, province or
  municipality.

**Localizzazione is the only unpartitioned dataset**, and this makes it the resolver:
given a CUP you get its region in one query, and the region tells you which regional
dataset to hit next. Coverage measured against the national `prg` dump: 541.539 CUP in
projects, 541.329 in Localizzazione — only **210 CUP (0,04%) unresolvable**, and those
are the `reg00` cases.

Cardinality measured on the full Localizzazione dump (666.153 rows, 541.329 CUP):

| Case | Count | Share | Max |
|---|---|---|---|
| CUP over several municipalities | 27.982 | 5,17% | 93 municipalities |
| CUP over several regions | 1.976 | 0,365% | 20 regions |

A multi-region CUP means step 2 must be repeated for each region. **No dataset carries a
split of the amount between territories**: never divide, never sum blindly.

## OData field names

The proxy mangles column names with a numeric suffix, but the suffix derives from the
**column name**, not from the dataset: `Cccodice_cup_1267962549` is the same in Projects,
Tenders and Localizzazione, across all regions. Parametric queries over the 21 partitions
are therefore possible.

| Column | OData field | Where |
|---|---|---|
| Codice CUP | `Cccodice_cup_1267962549` | all families |
| Codice CIG | `Cccodice_cig_1267962168` | `gar`, `pga` |
| Codice Locale Progetto | `Cccodice_locale1983787008` | all families |
| Codice Fiscale Titolare | `Cccodice_fiscal1934873127` | `prg`, `sog` |
| Codice/Descrizione Stato CUP | `Cccodice_stato_1426672593` / `Ccdescrizione_s1176782119` | `prg` |
| Settore Intervento | `Ccsettore_inter1475973826` | `prg` |
| Costo Lavori Effettivo | `Cccosto_lavori_e582037416` | `prg` |
| Importo Aggiudicazione | `Ccimporto_aggiudi23568545` | `gar` |
| Importo Base d'Asta | `Ccimporto_base_d762806864` | `gar` |
| Descrizione Soggetto (winner) | `Ccdescrizione_so914929799` | `gar` |
| Tipo Scelta Contraente | `Cctipo_scelta_co554630002` | `gar`, `pga` |
| Codice Regione / Provincia / Comune | `Cccodice_region1532212456` / `Cccodice_provin1339238684` / `Cccodice_comune_370585612` | `loc` |
| Descrizione Regione / Provincia / Comune | `Ccdescrizione_r1013517246` / `Ccdescrizione_p1589129158` / `Ccdescrizione_c1275250270` | `loc` |
| Anno Pagamenti | `Ccanno_pagament2071337486` | `sal` |
| Importo Pagamenti | `Ccimporto_pagam2083996808` | `sal` |

> **Never guess a mangled name.** The suffix is stable per column name, but it is not
> derivable: guessing `Ccanno_pagamenti…`/`Ccimporto_pagam1734266467` for `sal` returns
> **empty strings, not an error** — the query succeeds and every value comes back blank.
> Always read one row first and list its keys (command below) before writing a filter or
> a projection against a family you have not used yet.

To discover the fields of any other dataset, ask for one row and list the keys:

```bash
curl -sS "https://bdap-opendata.rgs.mef.gov.it/ODataProxy/MdData('{RESOURCE_ID}@rgs')/DataRows?\$top=1&\$format=json" | jq -r '.d.results[0] | keys[]'
```

## Column layout of the less obvious families

**`sal` — Payments**: `Codice Locale Progetto`, `Codice CUP`, `Anno Pagamenti`,
`Importo Pagamenti`. One row per project-year; decimals use a dot here.

**`pdc` — Cost plan**: project code, CUP, `Anno Piano dei Costi`, `Importo da Realizzare`,
`Importo Realizzato`.

**`pga` — Participants**: project code, CUP, CIG, tender number and object, selection
procedure, fiscal code and name of the participant (two pairs: entity and its RTI
member), plus `Tipo Partecipazione` (e.g. `RTI`).

**`sog` — Owners**: project code, CUP, fiscal code, name, entity code, legal form
(`Descrizione Forma Giuridica`), municipality and postcode.

## Format traps

- CSV dumps are **latin-1**, delimiter `;`. Convert before feeding DuckDB:
  `iconv -f latin1 -t utf8 in.csv > out.csv`.
- Decimals: **comma** in `prg` (needs `REPLACE(col, ',', '.')` before casting), **dot** in
  `gar` and `sal`.
- Sizes: Localizzazione ~69 MB, Projects (national total) ~428 MB, a mid-size regional
  `gar` ~16 MB.

## Dataset map


### Progetti (`prg`)

| Ambito | Package id (dump CSV) | Resource id (OData) |
|---|---|---|
| Piemonte | `a0ab0d42-2ec0-45c3-970c-6609b8f2c1fc` | `8332a9c9-196b-4cc3-b842-fb1dd3e31c57` |
| Valle d'Aosta | `32838eab-4cdf-4759-ad75-1a090ed0a02e` | `6c0df564-f95d-4d48-9a39-b70146131722` |
| Lombardia | `c2b4f565-8502-4182-804d-53cfb6fd2659` | `e73db0ff-9e61-4da9-9166-ab61e9bf8352` |
| Trentino-Alto Adige | `7165532b-a5b7-4fd6-b7a5-9e47fd9c8e4a` | `a58f116c-dcd0-47c7-b112-bf87a1d44447` |
| Veneto | `213f9fd6-1e98-4feb-a68a-94cf9346fa92` | `bd3718fb-b04c-4beb-a482-34f6a838c523` |
| Friuli-Venezia Giulia | `357feec0-b81b-4f91-a1f3-b132aa667a85` | `ab6fa5ed-9aab-4b3f-ba3c-ab560f6d7d83` |
| Liguria | `6b4f8364-74ae-4286-a096-823d096f607f` | `f7fd3487-ac2b-46b9-8c05-a7362ce6bf0d` |
| Emilia-Romagna | `4f26f066-87e5-43a9-ab83-48d40253f7c4` | `33a4e97d-d906-447e-9ed7-c920c3e14849` |
| Toscana | `5a969166-6766-4188-940d-416a73f2a7fb` | `3d866aa2-9abe-434e-8375-6815242b2885` |
| Umbria | `5740a207-3437-4943-88fa-7caa8ff1a934` | `0e31510a-5352-403f-8c91-ee4c5f3aa93e` |
| Marche | `20ad5fce-30bb-4a3a-aec2-89f850cff6cc` | `f757bb44-3334-454c-b110-11bc7e5b1d92` |
| Lazio | `e99de221-4ec4-4800-8c49-518e9dbb9432` | `0a83cd4f-7a14-44b8-a742-7ffbd98d6efa` |
| Abruzzo | `b3c13736-9ff1-47e3-b2b4-4aedf1b765bc` | `84f44432-5beb-4f54-9485-7bdbc1879a2b` |
| Molise | `8a6e1b18-f1a4-410d-b8e9-38aab6821ce9` | `de9ef0b3-c9bc-4a86-a175-f89f40d514a5` |
| Campania | `b54a5bcb-da1c-4f3b-9015-e675704e3ce0` | `ae265345-1324-40af-be65-c3c1d0f19fd0` |
| Puglia | `17b7abdc-fda1-4c48-8a86-0b31659c07e8` | `27f8f3f2-d6b8-4e1a-a3f2-855097cfcecf` |
| Basilicata | `b5728959-823d-4081-962d-f8f7a7b0eeb8` | `86e4f18f-3daa-418d-936a-703b9c6ef332` |
| Calabria | `b0d27f31-3a84-4e76-8b01-e58503bad22c` | `55a5db4a-21e5-43c0-aa3c-9f884518ddab` |
| Sicilia | `9ffc0c78-36e6-45a9-8f7e-1082a35a8329` | `68bbcaaf-cc1e-4ddb-8482-81ff81a9bfd7` |
| Sardegna | `cef7d438-e999-4fce-b26f-dda4d7d9bf0c` | `d904d26b-94b2-4fe3-aa8b-944d6906cdb0` |
| Totale | `c76e90f7-eea5-4f32-8767-6b60e3505a1d` | `bda1676b-62ab-44b7-8f9a-ca93b8534488` |

### Gare (`gar`)

| Ambito | Package id (dump CSV) | Resource id (OData) |
|---|---|---|
| Territorio Nazionale | `b0603af6-f0c9-48a1-9e34-ece73a608aad` | `3ddefe62-ae2e-48c3-b0bc-0e25dbc7c66a` |
| Piemonte | `874296f7-93dd-41a7-b860-4ae1c59c2e93` | `4fcf85ae-fa0e-4dd1-8173-5820dfcef64d` |
| Valle d'Aosta | `473eb03c-846e-49b2-84d7-389260da4acb` | `9c05a8b8-d333-4156-b23a-b025a83bcc9f` |
| Lombardia | `228df76d-de44-454e-9bdf-bcc782815b9d` | `25828d46-7a94-4e7b-8135-2aa116103223` |
| Trentino-Alto Adige | `c9b036f7-06a0-4ee8-bd8e-39b4dc08318b` | `bddfab47-5581-43cb-8340-8eb2ac076c3c` |
| Veneto | `acae7f65-9e7a-4e1f-b15b-f590533d5cd6` | `311213d2-c447-4eab-91c5-003cdd68e897` |
| Friuli-Venezia Giulia | `5220238c-44f2-461f-a1ac-c905b504b26e` | `a737252b-7d63-41d2-9995-538e5f217d24` |
| Liguria | `8c2a99b1-62ea-44a3-b8a8-a66289a4cc7a` | `f9e2bc35-d28c-46bd-89df-f12dce583654` |
| Emilia-Romagna | `c2210ecf-52c5-4db2-a90b-a43b7a3fbde9` | `d7c52d8b-9486-421a-92ec-52dde25c55ae` |
| Toscana | `73905b2f-9bfd-4518-9b26-32f40f48c73c` | `c9994a0e-9b21-4475-ba16-11c0f5939930` |
| Umbria | `f3d54366-a91f-4675-88bf-dec13baabff1` | `1a10101b-cbfc-40a8-9953-4ce581aa9e76` |
| Marche | `16e8ae35-1c89-43f2-a891-4ae3e96bfd8d` | `fc7565a5-2277-4a96-9134-90f5e5c564b7` |
| Lazio | `372f630c-d7fb-47ba-9173-4bde3d9d1f96` | `74849025-3789-474d-b422-7b47d98d4784` |
| Abruzzo | `cac73cc4-7eb9-4219-a4ff-2ba6614e5205` | `de927263-4a92-4070-b8bf-5e94118df4cc` |
| Molise | `cc2eded1-2cc5-4669-b7fc-d5921fff82e9` | `2e854191-6949-4529-8cea-19cbb788178c` |
| Campania | `a7cc0311-2197-41c9-8bb8-6b37c439ad32` | `6139f999-74b6-4ea2-8afb-63883305dffd` |
| Puglia | `7cfa12af-a764-4224-98d1-922b82392fb9` | `d114f68b-65ef-4543-8f5d-1acec19ccf34` |
| Basilicata | `b21cb4dc-32cf-4dd8-9836-68a8b97d4d7b` | `4d2f25f9-9953-4a93-ace1-8fce2d9c9fa2` |
| Calabria | `4628d028-66d2-4b7a-9a30-d148c3f7bd89` | `07f114b3-a63a-437e-a67a-abc635e4c632` |
| Sicilia | `f1b05fea-4b28-4010-b8ef-f4049056c6dd` | `49a5930b-d46b-446b-907c-c14988f9c676` |
| Sardegna | `4644ba01-49bb-42bc-af01-7bcec01aac4a` | `dac376ec-d32f-49b5-8c17-321003b36594` |

### Pagamenti (`sal`)

| Ambito | Package id (dump CSV) | Resource id (OData) |
|---|---|---|
| Territorio Nazionale | `bcaca701-28d8-455b-aa9a-c840c5e12b75` | `375829db-8f54-4e1f-bdc5-ec168f900702` |
| Piemonte | `370a089d-cce8-4fb0-81dd-91fdcbb4f7a9` | `781e6e55-b0ce-41d9-8268-9038f40d8b63` |
| Valle d'Aosta | `75f3d316-bfbf-4bc7-8dc1-c27a7893618b` | `dfb05259-83d8-4ea8-8649-d56a892f5c9b` |
| Lombardia | `30d9dcb6-eab0-4dbd-8e37-698a3cb2ffc5` | `82db7262-a387-43e6-806f-00f9a30b3710` |
| Trentino-Alto Adige | `edbe8a01-ea86-4f04-9b40-d357dc9e9be6` | `ec76b1be-1c06-4c66-8fef-01024d509299` |
| Veneto | `21360010-c160-4699-8e55-844364a2ad74` | `c5e264d7-34b6-46e2-99e0-38eb7528c6fd` |
| Friuli-Venezia Giulia | `c3d0700f-2be7-420c-93be-06b5dea19eec` | `78a566ea-ede6-47f2-a23b-24c108f9dad4` |
| Liguria | `c483220f-907a-49a2-bc72-9c66eeb46134` | `a4146059-197a-479e-9a0a-7a55c2d80ca2` |
| Emilia-Romagna | `94961149-efbb-4799-909e-410c21853aaa` | `3843d361-3663-4132-a16f-38ea4e3d2e29` |
| Toscana | `8238bfce-dc5b-4764-ac06-db426b314a1e` | `6520633d-58ba-4776-85f9-557958d855ef` |
| Umbria | `5527b971-7a53-420f-9e31-1c953eca8190` | `1cf70168-2fb3-4ce5-bf66-5ac43a713f9b` |
| Marche | `886c05c2-bd41-4c2b-a8d4-f000f51c8836` | `51753405-a82c-4271-a311-9ee8853fbbba` |
| Lazio | `59017a93-b264-4ed3-bf31-698c74d99c2d` | `aa5b5e71-3798-44e3-be9a-c9c7409d10b3` |
| Abruzzo | `3b9ef833-5fa2-42dd-9a78-4c53bc122625` | `9fd6e470-d412-49fe-8204-28015ebef6be` |
| Molise | `84d2f904-209a-4f02-ac19-531030640920` | `260ee7f6-b739-4652-9db5-88572f251f3a` |
| Campania | `ee901078-f660-4693-9e2d-401c2eb8a4a4` | `1cd788f0-d492-42ed-90b6-ad3c7b2d3fde` |
| Puglia | `51879bb1-7625-40bf-9e0d-93eb5b45eff9` | `1f1e1f8e-3f20-4b36-8f8e-a6d9de0c17fb` |
| Basilicata | `e0e68b8c-c9c6-474b-abbb-6fc87bf7ac11` | `ee4935bd-35f7-4637-b9c2-0d3b66e6378c` |
| Calabria | `f0acdbfb-19f0-4135-bbdc-97d344c0cf29` | `86678724-f166-4391-9fb2-c7e1b5ca36ec` |
| Sicilia | `b04ad0b8-2982-4dd2-83a3-4638ae82064d` | `68f65608-4c70-4227-8308-b28b7f00f506` |
| Sardegna | `7ab11e9d-8651-4d74-944e-9905a8f651bb` | `5dd52505-5ef3-4aa4-b02c-8d2af102d932` |

### Partecipanti gare (`pga`)

| Ambito | Package id (dump CSV) | Resource id (OData) |
|---|---|---|
| Territorio Nazionale | `4bd4850f-2ff1-4334-a0ee-2d685542b997` | `198c9d7c-9845-40bf-9b70-feb14af22b84` |
| Piemonte | `9e792797-cde1-42d9-b0fe-f8a94861246a` | `59e4cf29-279e-475f-bea7-3b7d0c047551` |
| Valle d'Aosta | `3c615ade-6155-4b35-8ddf-8d03daaa9ae6` | `e84a7c86-651f-4d31-904d-ce21339a4518` |
| Lombardia | `b21d86b9-351a-4e4f-93b8-ef8650ff9b66` | `16acacc5-b16b-4452-8845-17c4ba3ce4c3` |
| Trentino-Alto Adige | `f2847404-02eb-4e51-9828-84a0b1d94540` | `d2c56f24-672c-4e5c-b518-ed00d9f48fde` |
| Veneto | `d800cd4e-39c8-4614-acb9-521cd60a6aa8` | `2783c437-83ab-45b7-88e5-14889e2b1290` |
| Friuli-Venezia Giulia | `63153ed2-cffc-4d7b-b545-c7ff3d8e2491` | `e8a0e88d-9415-4241-b070-0c12984fdb61` |
| Liguria | `7a5dac24-0cd4-47f2-a9ca-ad086852f401` | `286ba202-9520-4082-8d0e-47a1693efb76` |
| Emilia-Romagna | `a37b0318-228d-468a-af5f-186fe8e2390a` | `30f49e9a-8202-412a-bedb-f540b1220033` |
| Toscana | `09ce6485-bde9-4041-a856-63a93629f0c5` | `31ce7434-6279-4e25-bc73-922d27ca8d87` |
| Umbria | `d3fe6b05-b9e8-4ad0-9e4e-b57400a978c5` | `e04a6535-265b-4e72-8adb-b2e39c54eb81` |
| Marche | `fbbb4575-ff8e-4f13-89a0-d27c81801951` | `c864c469-8caa-4c5f-80f3-30fd64644805` |
| Lazio | `d2f793d9-9f8c-420a-b043-1ba66d337ecd` | `b145b86d-2ecf-4819-a399-e6709b53666e` |
| Abruzzo | `a410de4f-0c8b-4bb2-a3c2-a0a1a43c1ccd` | `ca7752e4-21a9-45f9-8180-d1b4808e52e7` |
| Molise | `353971bd-ed9e-4064-98c2-2b7fb7116f82` | `28569753-7fb8-420a-8193-05ade8bcb564` |
| Campania | `3517a68f-8bc6-495f-a0f3-e93e33d93cd8` | `58dde6ac-4e90-4f35-b01f-55848ab9989b` |
| Puglia | `2f4ee0e4-e560-47e3-85fa-681f6449d314` | `fefec21e-ca49-44b2-96e8-9bb2c487a908` |
| Basilicata | `eaf5580e-1f21-4e57-a6c3-8e1a6cbc1415` | `a552ef2d-d2f5-4899-a97b-0dd0bedf2ab4` |
| Calabria | `c15df728-3f29-4b51-9a39-d5eefa380d6d` | `5002ae3a-6a30-4466-9975-3f49b7570c8e` |
| Sicilia | `e0c63653-8353-430a-8457-34fb51e74423` | `45855c47-6ad7-4dfd-8135-525c4eaeb97f` |
| Sardegna | `cfbd9943-fe91-41e7-b0fb-3f6c2803d9a9` | `d0490a77-a00e-49b8-bb60-f28a33acb02d` |

### Piano dei costi (`pdc`)

| Ambito | Package id (dump CSV) | Resource id (OData) |
|---|---|---|
| Territorio Nazionale | `a8cab680-aebe-4c8f-b761-8a465964c739` | `b5351e5a-f2ed-4336-a140-e718c8f101c2` |
| Piemonte | `7a3a2d0e-b911-4830-9350-3ee61272bee6` | `7e11918e-f315-4d69-a445-7a81b6525ffa` |
| Valle d'Aosta | `7b983818-080c-4ff7-85fa-7cf3aa971349` | `14393bb2-ae02-454e-b7bd-abacf101e637` |
| Lombardia | `40969c2b-12f6-49dd-9824-47a3218ec4e6` | `a6ea81c2-8a3c-4002-9b96-10039c572574` |
| Trentino-Alto Adige | `a6181253-e2f2-4638-8862-fbee87d6bcf6` | `1afb7c2a-eac0-4bb3-b578-14e1685370af` |
| Veneto | `96d01011-5ba9-49d6-ba3a-3514bf7ea85e` | `4e05c791-b344-45ed-955b-7215ce356800` |
| Friuli-Venezia Giulia | `4d3c105e-d72b-46cf-9ed1-92de509e09ef` | `c90d2f57-a6a6-42de-8c0b-59afd596243e` |
| Liguria | `4e99e9f8-0d72-4712-b693-55695c10ff14` | `87535540-7382-4b46-ac00-db85cd881f81` |
| Emilia-Romagna | `f4089ce6-f500-4283-ab21-2aeaeb97cc20` | `27b27a99-9f21-4d7d-bfea-9f05e3660349` |
| Toscana | `967ba775-cf79-4f9d-9095-4ea90a838ae2` | `42b58c13-c2e9-4489-97f6-ac4b8fa6bb0d` |
| Umbria | `3b8564c1-94ea-450b-8850-ab402a4cf41f` | `ae9512f2-e50c-42fa-8133-1850ad1894e5` |
| Marche | `3b1dbb8e-0626-4cfd-88a5-3ca29a08e9b1` | `4ad7493c-14e9-44c2-a0a0-5ea6892fe4f4` |
| Lazio | `fc5df8d2-07ad-48aa-8c0e-e15fa96cc217` | `b04f84e5-9b05-463c-9afc-8e7729cb95ab` |
| Abruzzo | `eb2fd84f-ab5f-4c8c-998a-876878a35bf1` | `a66d2cec-df3a-4d31-8b2c-22cdf236d385` |
| Molise | `8b919172-2aa5-4a8e-818b-0faf1f5382bf` | `5e144228-45bb-475f-8484-acf82a8e9a13` |
| Campania | `affc1a08-1053-4960-943c-8b42d50d308a` | `17892064-26fa-4b28-b130-d05ad3026d0c` |
| Puglia | `71e36966-871a-4789-8730-7f7a6aa9c86d` | `54936936-c099-49f5-b337-16af6618348b` |
| Basilicata | `f04eb4a6-5393-4358-8b8c-e659c082f6b4` | `02e0842d-d550-4732-a70a-199cdcfa167f` |
| Calabria | `caf420bb-5752-495a-8704-cfe673bbd219` | `f01ad700-09d6-40e8-8dee-0e89a16768da` |
| Sicilia | `2572cada-6bb7-43fc-a253-d3864a66b612` | `e7460c34-2bcf-4405-8e01-861b260b92b1` |
| Sardegna | `dcbe70d9-c60f-45fc-9826-3bb097228424` | `3e357dc4-1a73-4817-ac08-bb5bce165c3d` |

### Soggetti titolari (`sog`)

| Ambito | Package id (dump CSV) | Resource id (OData) |
|---|---|---|
| Territorio Nazionale | `4c3ae347-3f3f-4cd4-80b8-e6b6bf83f091` | `29d214ba-dc3c-492c-8721-7704ce68a92c` |
| Piemonte | `3b220472-5636-4060-86a1-199edcd21e9e` | `479358d6-7c80-485f-a1d0-052f1297d6f4` |
| Valle d'Aosta | `9c717a0b-3193-4c0b-8cd3-165cf87d0a4a` | `e5e66f85-0dcc-424f-88f8-d53e4afe97b1` |
| Lombardia | `5c700932-2667-48d8-bf5d-f5b9eed941bc` | `eecfca9c-c787-4fc3-b400-b9216b1eb886` |
| Trentino-Alto Adige | `720fe7f1-d76e-40ae-8d0c-f3dd8ff0f566` | `90cb1ae7-40dc-42ac-8367-700bcd29cbaa` |
| Veneto | `b6e0b8aa-a2a3-410c-93be-e533adaabf93` | `57d2b58f-11d6-40a1-ae08-89be9a1a758e` |
| Friuli-Venezia Giulia | `cefe9fc9-bf9b-400c-8c6c-eacce62a6045` | `c2609d82-80d2-4105-94e0-48b3b06eee89` |
| Liguria | `162a1004-e62f-4640-b5e3-bae35d4f5361` | `17499b16-3563-4081-b6de-061984b21591` |
| Emilia-Romagna | `ef8910ce-8bac-4591-b936-2ac2fbbc2e15` | `15939aba-788b-4b57-adac-f68171c9a0fa` |
| Toscana | `b9efacb5-59e0-4756-9a52-dacac22b497d` | `6d9295b8-76c3-45b7-b160-ce155010550f` |
| Umbria | `2a705e33-3fc5-433f-bec8-e346d5c4cdbf` | `de21272a-c375-4450-a488-0dd83c921976` |
| Marche | `e521b32b-7f46-4ff9-beed-7466a57e7e57` | `ca471a3c-c069-429e-90a5-86fc229e6ae1` |
| Lazio | `b8181f7c-b5e9-4c6d-806d-4f70cabf3490` | `38830ae7-96f4-43b2-9275-04c37b473c83` |
| Abruzzo | `ff0de0b4-73a5-44a8-aef8-2d596b5f1937` | `d525b7dd-6571-4874-b2a7-c149a3386bc4` |
| Molise | `f1d56024-e757-4f4b-9266-985abf691203` | `54a4a586-a2e6-4b2e-9b8c-eb48df31e07b` |
| Campania | `04ccb4aa-e5a5-4201-8117-cb639f40071c` | `12746190-f1ca-4af7-b054-91154ad76485` |
| Puglia | `03a57b53-2329-4e07-8156-23bb70d4d00b` | `4f487ac1-241a-48f3-ba95-bdd199c45469` |
| Basilicata | `7c86c872-6c7f-4bb9-a0e2-c579e562695f` | `878d1ff7-5115-44b9-a8bb-8b7a36b58948` |
| Calabria | `71216f65-cc71-49e6-b4cf-1d9b805ed2ac` | `d7dcccab-e414-44ff-bb9a-3a7981c96605` |
| Sicilia | `8c8b84f6-9360-40c8-9fa7-d0473f132fb4` | `3ed15057-9c21-4f2a-b3b5-731f21be073f` |
| Sardegna | `12874542-87db-45c0-bead-8e8505ccf5fd` | `5b361132-db6f-4b53-b2d5-105c3baffab8` |

### Localizzazione (`loc`)

| Ambito | Package id (dump CSV) | Resource id (OData) |
|---|---|---|
| Nazionale | `31b40a28-9d84-49f4-905e-f4bf471aae8b` | `c4cce647-cec4-4b60-a8ab-d308ecfba743` |
