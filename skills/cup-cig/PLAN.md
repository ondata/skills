# Editorial Plan — `cup-cig` skill

## Goal

A skill that guides users in extracting detailed information from lists of CUP and CIG codes,
to support monitoring of Italian public procurement and project design.

---

## Demo dataset

`source_test_cup` lists which portals return data for that CUP (confirmed by testing).

```csv
"CIG";"CUP";"source_test_cup"
"Z063947806";"J87G22000360002";"OpenCUP"
"ZEE0718779";"B31B95000000003";"OpenCUP,OpenCoesione"
"Z5A0F93AC5";"J81J11001630007";"OpenCUP"
"8874674CA7";"H87H21003670005";"OpenCUP"
"Z723A99410";"G74I19000540002";"OpenCUP"
"Z3B3885F48";"E66C18001040006";"OpenCUP"
"Z7F1B53749";"B54H16000780004";"OpenCUP"
"48886723C1";"B23B12000070003";"OpenCUP"
"Z222B001C9";"E62I15000790001";"OpenCUP"
"Z3438FFE7D";"C19J21045150001";"OpenCUP"
"X160258A9A";"B41J10000310008";"OpenCUP"
"";"D27H12001840009";"OpenCUP,OpenCoesione"
"";"G48E18000200004";"OpenCUP,OpenCoesione"
"";"E78C11000150009";"OpenCUP,OpenCoesione"
```

Rows without CIG are added specifically to test the OpenCoesione API path.

**Legend:** OpenCUP = universal (all valid CUPs). OpenBDAP = TBD (requires per-CUP verification).
SCP = only non-Z CIGs (above threshold). OpenCoesione = only cohesion-funded projects.

---

## Data sources

### 1. OpenCUP — project metadata from CUP

**What it provides:** project description, sector, nature, typology, contracting authority,
financial amounts, geographic scope. The page also aggregates linked data from BDNCP-ANAC,
BDAP-MOP, OpenCoesione, SILOS (Camera) and SCP-MIT — each downloadable as CSV.

**Web page (no auth, free):**

```
https://opencup.gov.it/portale/progetto/-/cup/{CUP}
```

Confirmed working. Returns HTML with full project card including:
`anno decisione`, `stato`, `soggetto titolare`, `CF/P.IVA`, `classificazione`,
`area d'intervento`, `settore`, `sottosettore`, `categoria`, `copertura finanziaria`,
`totale costo previsto`, `totale finanziamento pubblico previsto`, `localizzazione`
(stato, area geografica, regione, provincia, comune).

**Sogei REST API (requires credentials — NOT free):**

```
https://api.sogei.it/rgs/opencup/o/extServiceApi/v1/opendataes/cup/{CUP}
```

Returns `401 Unauthorized` without credentials. Registration via:
`https://www.opencup.gov.it/portale/web/opencup/contattaci`

Authentication: **HTTP Basic Auth** — `client_id:client_secret`

```bash
curl -s "https://api.sogei.it/rgs/opencup/o/extServiceApi/v1/opendataes/cup/{CUP}" \
  -u "$OPENCUP_API_CLIENT_ID:$OPENCUP_API_CLIENT_SECRET"
```

> Note: passing credentials as `x-ibm-client-id`/`x-ibm-client-secret` headers returns 401.
> IBM API Connect gateway requires Basic Auth here.

Supports also query by VAT: `/soggettotitolare/{VAT}`

Response format: JSON (default). Wrap with `| python3 -m json.tool` or `| jq`.

**Fields confirmed in response (CUP J87G22000360002):**

| Field | Example |
|---|---|
| `CUP` | `J87G22000360002` |
| `DESCRIZIONE_CUP` | full project title |
| `DESC_CUP` | short description (often "DATO NON PRESENTE") |
| `COD_STATO_PROGETTO` | `A` (Attivo) |
| `ANNO_DECISIONE` | `2022` |
| `DATA_GENERAZIONE` | `20220819000000` |
| `DESC_SOGGETTO` | contracting authority name |
| `CF_PIVA_SOGGETTO` | authority fiscal code |
| `DESC_AREA_SOGGETTO` | e.g. `AMMINISTRAZIONI LOCALI` |
| `DESC_CATEGORIA_SOGGETTO` | e.g. `ENTI TERRITORIALI...` |
| `DESC_SOTTO_CATEGORIA_SOGGETTO` | e.g. `AMMINISTRAZIONI COMUNALI` |
| `DESC_AREA_INTERVENTO` | e.g. `AMBIENTE ED ENERGIA` |
| `DESC_SETTORE_INTERVENTO` | e.g. `INFRASTRUTTURE AMBIENTALI...` |
| `DESC_SOTTO_SETTORE_INTERVENTO` | e.g. `DIFESA DEL SUOLO` |
| `DESC_CATEGORIA_INTERVENTO` | e.g. `BONIFICA DI SITI` |
| `DESC_TIPOLOGIA_INTERVENTO` | e.g. `LAVORI SOCIALMENTE UTILI` |
| `DESC_NATURA` | e.g. `ACQUISTO O REALIZZAZIONE DI SERVIZI` |
| `IMPORTO_COSTO_PROGETTO` | `20000.0` |
| `IMPORTO_FINANZIAMENTO` | `20000.0` |
| `DESC_TIPO_COPERTURA` | e.g. `REGIONALE` |
| `LOC_REGIONI` | `SARDEGNA` |
| `LOC_PROVINCE` | `SUD SARDEGNA` |
| `LOC_COMUNI` | `SANLURI` |
| `INDIRIZZO` | location description |
| `NUMERO_CUP_COLLEGATI` | `0` |
| `COD_CUP_MASTER_COLLEGATO` | master CUP if any |
| `DESC_STRUMENTO` | programming instrument |
| `DESC_STRUTTURA_INFRASTRUTTURA` | infrastructure object |

**Known gaps:** PNRR service-delivery projects (PA Digitale 2026) are absent.

**Practical path:** scrape the web page (HTML) or use the Sogei API if credentials available.

---

### 2. OpenBDAP — financial monitoring from CUP

**What it provides:** public works financial monitoring (MOP), CIG codes linked to a CUP,
project phases, timeline, expenditure and financing data.

**OData endpoint (no auth, confirmed working):**

```bash
curl -s "https://bdap-opendata.rgs.mef.gov.it/ODataProxy/MdData('bda1676b-62ab-44b7-8f9a-ca93b8534488@rgs')/DataRows?$filter=Cccodice_cup_1267962549%20eq%20'{CUP}'&$top=10&$inlinecount=allpages" -H "Accept: application/json"
```

- Base: `https://bdap-opendata.rgs.mef.gov.it/ODataProxy/`
- Dataset ID: `bda1676b-62ab-44b7-8f9a-ca93b8534488@rgs` ("Progetti Opere Pubbliche MOP - Totale")
- CUP field: `Cccodice_cup_1267962549`
- Response wrapped in `d.results[]`
- **Add `$inlinecount=allpages`** to get a reliable record count in `d.__count`

> Note: `$filter` value must be URL-encoded (`%20` for spaces).
> The previous dataset ID `6c0df564...` was the Valle d'Aosta regional dataset — wrong.
> The correct "Totale" covers all regions and was confirmed with demo CUPs.

**Key fields confirmed (from reference CUP I77H11000120009):**

| Field | Description |
|---|---|
| `Cccodice_cup_1267962549` | CUP code |
| `Ccdescrizione_cu902475141` | Project description |
| `Cccodice_stato_1426672593` | Status code (`A`=active) |
| `Ccdescrizione_s1176782119` | Status description |
| `Ccdescrizione_ti177583083` | Contracting authority |
| `Cccodice_fiscal1934873127` | Authority fiscal code |
| `Ccnatura_interve446219799` | Nature of intervention |
| `Cctipologia_inte917995560` | Type of intervention |
| `Ccsettore_inter1475973826` | Sector |
| `Ccsottosettore_i327509803` | Sub-sector |
| `Cccategoria_inte847681723` | Category |
| `Ccinizio_progetta77930296` | Design start date |
| `Ccfine_progetta1599384906` | Design end date |
| `Cccosto_lavori_1978461874` | Works cost |
| `Ccfinanziamenti_756114873` | Total financing |

**Caveat:** field names are obfuscated (auto-generated IDs). No official field docs exist.

**Coverage gap:** not all CUPs appear — MOP covers public works (opere pubbliche). Service/supply projects and very small projects may return 0 results. Of the 11 demo CUPs, at least 2 confirmed present.

**Other confirmed filterable fields:**
- `Cccodice_fiscal1934873127` — fiscal code of contracting authority (find all projects by entity)
- `Cccodice_stato_1426672593` — status (`A`=active, `C`=closed)
- `Ccsettore_inter1475973826` — sector (e.g. `STRADALI`)
- OData standard `and`/`or` operators work for compound filters

**Search by multiple CUPs (web UI):** up to 300 CUPs separated by `;`, results in Excel
with three sheets: CUP Details, CIG Details, Indicators.

---

### 3. Servizio Contratti Pubblici — tender data from CIG

**What it provides:** tender notices (bandi), outcomes (esiti), awards (aggiudicazioni),
CIG → CUP cross-reference, RUP, amounts, contracting authority.

**Base URL:** `https://www.serviziocontrattipubblici.it/WSConsultBandi/rest/`

**Key endpoints (all POST):**

| Endpoint | Query param | Returns |
|---|---|---|
| `Bandi/Lista` | `cig=` | List of notices for a CIG |
| `Bandi/Dettaglio` | body = `{id}` | Full notice detail |
| `Esiti/Lista` | `cig=` | List of outcomes for a CIG |
| `Esiti/Dettaglio` | `numeroPubblicazione=` + body `{idGara}` | Full outcome detail |
| `Avvisi/Lista` | — | List of award notices |
| `Avvisi/Dettaglio` | `codiceSistema=` `codiceSA=` + body `{id}` | Full award with CIG+CUP |

**Example — bandi per CIG (confirmed working):**

```bash
curl -sk -X POST "https://www.serviziocontrattipubblici.it/WSConsultBandi/rest/Bandi/Lista?page_limit=5&offset=0&stato=3&cig={CIG}" -H "Content-Type: application/x-www-form-urlencoded"
```

**Note:** `-k` required — SCP has an invalid TLS certificate (local CA issuer not found).

**`stato` values:** `stato=3` = published/archived notices. Required; omitting returns `error: state-invalid-value`.

**Coverage:** SCP covers public tenders above threshold. CIGs starting with `Z` (affidamenti diretti sotto soglia) return 0 results — they are not published on SCP.

---

### 4. ANAC BDNCP — CUP↔CIG join table

**What it provides:** the authoritative mapping between CUP and CIG for all ordinary public
contracts. One row per CIG, with its associated CUP. This is the **missing join** between
project identity (CUP) and procurement events (CIG).

**Access:** bulk ZIP download — no live query API.

- Portal: `https://dati.anticorruzione.it/opendata/dataset/cup`
- Format: CSV inside ZIP (large file — use DuckDB CLI to query without full decompression)

```bash
# Query CUP-CIG pairs with DuckDB
duckdb -c "SELECT * FROM read_csv_auto('cup.csv') WHERE cup = 'J87G22000360002' LIMIT 10"
```

**Practical path:** download once, query locally with DuckDB. The file is large but DuckDB
handles it efficiently without loading it all into memory.

---

### 5. ANAC BDNCP — bulk open data for all CIGs (including Z-codes)

**What it provides:** incremental delta updates for all published contracts including
direct awards (affidamenti diretti, CIG prefix `Z`). The only machine-readable source
for under-threshold CIGs.

**Access:** bulk download only — no live query API (WAF blocks programmatic requests).

- Portal: `https://dati.anticorruzione.it/opendata/dataset/cig`
- Formats: CSV, JSON, TTL
- Update cadence: delta files by period (e.g. `20240401-cig_csv`)

**OCDS dataset** (`dati.anticorruzione.it/opendata/ocds`) covers only contracts >40k€ —
excludes most Z-prefix CIGs.

**Practical path for Z-CIGs:** download the BDNCP delta/full CSV and filter locally.

---

### 6. OpenCoesione — cohesion policy projects from CUP

**What it provides:** EU/national cohesion-funded projects: title, description, status, financing
breakdown (EU/state/region/private), payments, advancement %, programming cycle, theme, nature,
subjects (programmers, implementers, beneficiaries), territories.

**REST API (no auth, confirmed working):**

Base: `https://opencoesione.gov.it/it/api/`

Rate limits: 12 req/min (anonymous), 60 req/min (registered via `info@opencoesione.gov.it`).

**Main endpoints:**

| Endpoint | Description |
|---|---|
| `progetti/` | Project list (paginated, filterable by tema/natura/territorio) |
| `progetti/{cod_locale_progetto}/` | Full project detail |
| `soggetti/` | Subject list (1.2M+ entities, filterable by tema/ruolo) |
| `soggetti/{slug}/` | Subject detail |
| `aggregati/` | Aggregated data (mirrors site pages) |

**Auxiliary endpoints (lookup lists):**

| Endpoint | Description |
|---|---|
| `nature/` | List of project natures |
| `temi/` | List of thematic areas |
| `territori/` | List of territories |
| `programmi/` | List of programmes (EU and national) |

Data available as HTML (browsable docs) or JSON (append `.json` or use `Accept: application/json`).

**Query by CUP (confirmed working):**

```bash
curl -s -H "Accept: application/json" "https://opencoesione.gov.it/it/api/progetti/?cup={CUP}"
```

**Filters (from official OPTIONS docs, confirmed working):**

Progetti can be filtered via query-string. Filters use slugs; multiple can be combined.

| Parameter | Example | Slug list endpoint |
|---|---|---|
| `cup` | `B31B95000000003` | — (exact CUP code) |
| `tema` | `energia`, `occupazione` | `/api/temi/` |
| `natura` | `infrastrutture`, `acquisto-beni-e-servizi` | `/api/nature/` |
| `territorio` | `sardegna-regione`, `roma-comune` | `/api/territori/` |
| `programma` | slug from programmi list | `/api/programmi/` |
| `soggetto` | `miur` | `/api/soggetti/` |

**Additional facet filters (confirmed working, not in official docs):**

| Parameter | Example |
|---|---|
| `stato` | `concluso`, `in_corso`, `liquidato`, `non_avviato` |
| `fonte` | `FS2127`, `FSC1420`, `FSC0713` |
| `ciclo_programmazione` | `2021_2027`, `2014_2020` |
| `focus` | `covid`, `clima`, `sisma` |

**Sorting (official):** `order_by` parameter. Values: `-costo` (default, desc), `costo`, `-data_inizio`, `data_inizio`.

**Pagination:** default 25 items/page, max `page_size=500`. Navigate via `next`/`previous` links.

**Response includes facet counts** for `ciclo_programmazione`, `natura`, `tema`, `fonte`, `stato`, `focus`.

**Key fields in list response:**

`cup`, `oc_titolo_progetto`, `oc_stato_progetto`, `oc_tema_sintetico`, `oc_finanz_tot_pub_netto`,
`tot_pagamenti`, `percentuale_avanzamento`, `soggetti` (array with role), `territori`.

**Key fields in detail response (additional):**

| Field | Description |
|---|---|
| `oc_sintesi_progetto` | Project summary |
| `oc_data_inizio_progetto` | Start date |
| `oc_data_fine_progetto_prevista` | Expected end date |
| `finanz_ue` | EU financing |
| `finanz_stato_fsc` | FSC state financing |
| `finanz_regione` | Regional financing |
| `finanz_privato` | Private financing |
| `impegni` | Commitments |
| `cup_descr_settore` | CUP sector description |
| `cup_descr_categoria` | CUP category description |
| `programmi` | Array of linked programmes with codes, axes, priorities |

**Coverage gap:** only cohesion-funded projects (EU structural funds, FSC, PAC). Ordinary
national/regional procurement not covered. ~1.8M projects across 2000-2027 cycles.

**Practical path:** direct API query by CUP — no scraping needed. Well-structured JSON,
clean field names, rich faceting. Best free API among all sources.

---

## Institutional landscape — why so many sources?

### CUP vs. CIG: the two identifiers

- **CUP** — identifies the *project* (investment decision). Upstream. One CUP covers the entire lifecycle of a public investment regardless of funding source or contracting activity.
- **CIG** — identifies the *procurement event* (tender/contract). Downstream. One CUP may generate multiple CIGs (one per lot, phase, or contract type).

Not all CUPs generate CIGs (grants, research), and not all CIGs are linked to a CUP.

### Portal classification: generalist vs. specialized

**Generalist portals** — cover all (or most) public investment projects regardless of funding source:

| Portal | Owner | Scope | API |
|---|---|---|---|
| **OpenCUP** | DIPE/PCM | All CUPs (universal registry) | Web scraping or Sogei API (auth required) |
| **ANAC BDNCP** | ANAC | All CIGs (universal procurement registry) | Bulk CSV download only |
| **ANAC CUP dataset** | ANAC | CUP↔CIG join table (all ordinary contracts) | Bulk CSV download only |

**Specialized portals** — cover subsets filtered by funding source, sector, or institutional domain:

| Portal | Owner | Subset | API |
|---|---|---|---|
| **OpenCoesione** | DIPE/PCM | Cohesion-funded projects (EU structural funds, FSC, PAC) | REST API, free, no auth |
| **OpenBDAP/MOP** | RGS/MEF | Public works (opere pubbliche) — financial monitoring | OData API, free, no auth |
| **SCP/MIT** | MIT | MIT-domain tenders (above threshold) | REST API, free, no auth |
| **SILOS** | Camera dei Deputati | Strategic infrastructure (~hundreds of major projects) | No API |

### Per-portal summary

| Portal | Owner | Unique data | Gap |
|---|---|---|---|
| **OpenCUP** | DIPE/PCM | CUP registry, project classification, lifecycle status | No financial or procurement data |
| **OpenBDAP/MOP** | RGS/MEF | Financial execution per CUP: commitments, payments, CIGs linked, works phases | Works only (lavori pubblici); excludes grants and services |
| **OpenCoesione** | DIPE/PCM | EU fund classification, co-financing rate, beneficiaries, payments, advancement %, NUTS geography | Cohesion-funded projects only; no procurement data |
| **ANAC BDNCP** | ANAC | CIG registry (authoritative), tender notice, award details, financial traceability | No execution/payment data; CUP linkage not always enforced |
| **ANAC CUP dataset** | ANAC | **Authoritative CUP↔CIG join table** — all ordinary contracts with CUP+CIG pairs | Bulk ZIP only; no live API; large file (use DuckDB CLI) |
| **SCP/MIT** | MIT | MIT institutional procurement, legal opinions, contracting authority qualification | Not a comprehensive national dataset; declining scope since 2024 reform |
| **SILOS** | Camera dei Deputati | Strategic infrastructure classification, commissariat status, parliamentary monitoring | Only ~hundreds of major projects; no open API |

### Data flow

```
[Decision to invest]
  → CUP generated (Sistema CUPweb / DIPE)
      → OpenCUP (project metadata)
      → OpenCoesione (if EU/cohesion funded, via SNM/IGRUE/RGS)
      → BDAP/MOP (if public works, mandatory reporting via RGS)
          → OpenBDAP (analytics and open data)
          → ReGiS (PNRR projects, bidirectional feed)
  → Procurement triggered → CIG requested from ANAC
      → ANAC BDNCP (tender, award, contract)
          → SCP/MIT (MIT-domain works)
          → SILOS (strategic infrastructure)
  → Contract execution → payments tracked in BDAP/MOP
```

### Systemic gaps (across all sources)

1. No single source links CUP → CIG → payment: joining OpenCUP + BDAP/MOP + ANAC is required.
2. Sub-threshold procurement (<€40k) is underrepresented in ANAC BDNCP.
3. Non-works investments (grants, services) have CUPs but don't appear in BDAP/MOP.
4. No physical outcome data (beneficiaries reached, infrastructure utilization).
5. PNRR creates a parallel tracking layer (ReGiS/ItaliaDomani) that partially overlaps BDAP and OpenCoesione.
6. ~~No real-time API for any source — all rely on periodic bulk exports.~~ **Partially resolved: OpenCoesione has a proper REST API (12 req/min free).**

---

## Skill workflow (draft)

Given a list of CUP+CIG pairs, the skill guides the user to:

1. **Query OpenCUP** by CUP → get project metadata (description, sector, authority)
2. **Query OpenCoesione** by CUP → get cohesion funding details, payments, advancement
3. **Query OpenBDAP** by CUP → get public works financial monitoring
4. **Query Servizio Contratti Pubblici** by CIG → get tender notices and outcomes
5. **Combine results** into a structured output (CSV, JSON, or markdown table)

---

## Phases

### Phase 0 — Test APIs with demo codes
- [ ] Test OpenCUP web page for 3 sample CUPs
- [ ] Test Sogei API for 3 sample CUPs (check if auth is needed)
- [ ] Test OpenBDAP OData for 3 sample CUPs (find exact URL + dataset ID)
- [ ] Test Servizio Contratti Pubblici endpoints for 3 sample CIGs
- [x] Test OpenCoesione API for demo CUPs (1/11 found: B31B95000000003; added 3 cohesion-specific CUPs)
- [ ] Document actual response fields for each source

### Phase 1 — Write skill instructions
- [ ] Write "When to use" section
- [ ] Write "Data sources" reference section
- [ ] Write step-by-step workflow with `curl` + `jq` commands
- [ ] Add output format recommendations
- [ ] Create `references/` folder with per-source API reference files (one per portal)

### Phase 2 — Scripts
- [ ] `query_cup.sh` — query OpenCUP + OpenBDAP by CUP list
- [ ] `query_cig.sh` — query Servizio Contratti Pubblici by CIG list
- [ ] `merge_results.sh` — combine outputs

### Phase 3 — Evals
- [ ] Create `evals/cup-cig/prompts.csv`
- [ ] Create `evals/cup-cig/checks.md`
- [ ] Create `evals/cup-cig/rubric.schema.json`

### Phase 4 — MCP server

Wrap the tested APIs into an MCP server so any MCP client can query Italian public
procurement data directly, without generating curl commands.

**Tools:**

| Tool | Source | Input | Auth |
|---|---|---|---|
| `query_opencup` | OpenCUP HTML scrape | `cup` | none |
| `query_opencup_api` | Sogei REST | `cup` | Basic Auth (env vars) |
| `query_opencoesione_projects` | OpenCoesione REST | `cup`, `tema`, `natura`, `territorio`, `programma`, `soggetto`, `stato`, `fonte`, `ciclo_programmazione`, `focus` | none (12 req/min) |
| `query_opencoesione_subjects` | OpenCoesione REST | `tema`, `ruolo` | none |
| `query_openbdap` | OpenBDAP OData | `cup`, `codice_fiscale`, `stato`, `settore` | none |
| `query_scp_bandi` | SCP REST | `cig` | none (invalid TLS) |
| `query_scp_esiti` | SCP REST | `cig` | none |
| `lookup_opencoesione_temi` | OpenCoesione REST | — | none |
| `lookup_opencoesione_nature` | OpenCoesione REST | — | none |
| `lookup_opencoesione_territori` | OpenCoesione REST | — | none |

**Design notes:**

- Server-side rate limiting queue (especially OpenCoesione 12 req/min)
- Centralized TLS handling (SCP requires `-k` / skip verify)
- Normalize response fields across sources into a common schema where possible
- Batch input support: accept list of CUPs/CIGs, return aggregated results
- The skill `references/` docs become the MCP server's internal documentation
- Stack: Python (httpx + mcp SDK) or TypeScript (fetch + @modelcontextprotocol/sdk)

---

## References folder structure (planned)

`skills/cup-cig/references/` — one file per data source, loaded on demand by the skill.

| File | Content |
|---|---|
| `opencup.md` | OpenCUP web page structure, Sogei API auth, field mapping |
| `opencoesione.md` | REST API endpoints, filters, slug lists, field reference |
| `openbdap.md` | OData endpoint, dataset ID, obfuscated field names mapping |
| `scp.md` | Servizio Contratti Pubblici POST endpoints, stato values, TLS notes |
| `anac-bdncp.md` | Bulk download URLs, CUP↔CIG join table, field schema |
| `portal-landscape.md` | Generalist vs. specialized classification, data flow, systemic gaps |

---

## Open questions (priority)

1. ~~Does Sogei API work without registration?~~ **Confirmed: requires client ID/secret (401). Use Basic Auth.**
2. ~~What is the exact OpenBDAP OData base URL and dataset identifier?~~ **Confirmed: `bdap-opendata.rgs.mef.gov.it/ODataProxy/`, dataset `bda1676b-62ab-44b7-8f9a-ca93b8534488@rgs` (Totale). Previous ID was Valle d'Aosta only.**
3. ~~What does `stato=3` mean in SCP?~~ **Confirmed: published/archived notices. Required param.**
4. ~~Are Z-prefix CIGs treated differently?~~ **Confirmed: not in SCP. Only in ANAC BDNCP bulk download.**
5. Can the OpenCUP web page CSV downloads (BDNCP-ANAC, SILOS) be triggered programmatically?
6. What is the ANAC BDNCP full dataset URL (not just delta)? What fields does it contain?
7. ~~OpenBDAP returns 0 results for all 11 demo CUPs~~ **Confirmed: correct dataset ID is `bda1676b...`; at least 2 demo CUPs present. `$inlinecount=allpages` required for accurate count.**
8. BDAP/MOP "CIG linked to CUP" claim: the main MOP dataset (`bda1676b...`) has NO CIG fields. CIG data must be in a separate BDAP dataset — not yet identified via OData/CKAN. Needs further investigation (the web UI Excel export has a "CIG Details" sheet — that data comes from somewhere).
