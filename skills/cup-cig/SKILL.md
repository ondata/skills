---
name: cup-cig
description: Guide users monitoring Italian public procurement to extract detailed information from lists of CUP (Codice Unico di Progetto) and CIG (Codice Identificativo Gara). Use when the user wants to look up project metadata, financial status, or tender details for Italian public contracts.
compatibility: Requires curl, jq, bash, internet access. OpenCUP API requires OPENCUP_API_CLIENT_ID and OPENCUP_API_CLIENT_SECRET environment variables. scripts/cig-fetch.sh requires agent-browser.
license: CC BY-SA 4.0 (Creative Commons Attribution-ShareAlike 4.0 International)
metadata:
  version: "0.1"
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
  ├─ Project metadata (name, sector, entity, amounts)?
  │    └─ OpenCUP API (or web page if no API key)
  ├─ Financial monitoring / execution status?
  │    └─ OpenBDAP OData
  └─ Associated tenders (CIG)?
       └─ ANAC BDNCP bulk (authoritative CUP↔CIG join)

User has a CIG
  ├─ Starts with Z (e.g. Z063947806)?
  │    └─ Below-threshold direct award → ANAC BDNCP bulk only
  └─ Alphanumeric (e.g. 8874674CA7)?
       ├─ Basic tender list / award outcomes?
       │    └─ SCP-MIT API
       └─ Full detail (participants, awards, subcontracts, financials)?
            └─ ANAC dettaglio-cig → scripts/cig-fetch.sh (requires agent-browser)
```

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

## Source 1 — OpenCUP: Project Metadata

**Base URL:** `https://api.sogei.it/rgs/opencup/o/extServiceApi/v1/opendataes/cup/{CUP}`
**Auth:** IBM API headers (`x-ibm-client-id`, `x-ibm-client-secret`)

### Look up a single CUP

```bash
curl -sS -X GET "https://api.sogei.it/rgs/opencup/o/extServiceApi/v1/opendataes/cup/J87G22000360002" -H "x-ibm-client-id: ${OPENCUP_API_CLIENT_ID}" -H "x-ibm-client-secret: ${OPENCUP_API_CLIENT_SECRET}" -H "Accept: application/json" | jq '.results[0]|{cup:.CUP, anno:.ANNO_DECISIONE, stato:.COD_STATO_PROGETTO, soggetto:.DESC_SOGGETTO, settore:.DESC_SETTORE_INTERVENTO, area:.DESC_AREA_INTERVENTO, importo:.IMPORTO_COSTO_PROGETTO, regione:.LOC_REGIONI}'
```

### Look up a list of CUPs

Given a file `cups.txt` (one CUP per line):

```bash
while IFS= read -r cup; do echo "=== $cup ==="; curl -sS -X GET "https://api.sogei.it/rgs/opencup/o/extServiceApi/v1/opendataes/cup/$cup" -H "x-ibm-client-id: ${OPENCUP_API_CLIENT_ID}" -H "x-ibm-client-secret: ${OPENCUP_API_CLIENT_SECRET}" -H "Accept: application/json" | jq '.results[0]|{cup:.CUP, stato:.COD_STATO_PROGETTO, soggetto:.DESC_SOGGETTO, settore:.DESC_SETTORE_INTERVENTO, importo:.IMPORTO_COSTO_PROGETTO}'; done < cups.txt
```

### Without API credentials (web page fallback)

The project page at `https://opencup.gov.it/portale/progetto/-/cup/{CUP}` is publicly
accessible but returns HTML. Use a browser or a headless fetch tool for scraping.

---

## Source 2 — OpenBDAP: Financial Monitoring

**Base URL:** `https://bdap-opendata.rgs.mef.gov.it/ODataProxy/MdData('bda1676b-62ab-44b7-8f9a-ca93b8534488@rgs')/DataRows`
**Auth:** None
**Field name for CUP:** `Cccodice_cup_1267962549`

### Query by CUP

```bash
curl -sS "https://bdap-opendata.rgs.mef.gov.it/ODataProxy/MdData('bda1676b-62ab-44b7-8f9a-ca93b8534488@rgs')/DataRows?\$filter=Cccodice_cup_1267962549%20eq%20'H87H21003670005'&\$inlinecount=allpages&\$top=10&\$format=json" | jq '[.d.results[]|{cup:.Cccodice_cup_1267962549, descrizione:.Ccdescrizione_cu902475141, stato:.Ccdescrizione_s1176782119, ente:.Ccdescrizione_ti177583083, settore:.Ccsettore_inter1475973826, costo:.Cccosto_lavori_e582037416}]'
```

### Query by entity fiscal code (without knowing CUPs)

```bash
curl -sS "https://bdap-opendata.rgs.mef.gov.it/ODataProxy/MdData('bda1676b-62ab-44b7-8f9a-ca93b8534488@rgs')/DataRows?\$filter=Cccodice_fiscal1934873127%20eq%20'02246660985'&\$inlinecount=allpages&\$top=10&\$format=json" | jq '[.d.results[]|{cup:.Cccodice_cup_1267962549, ente:.Ccdescrizione_ti177583083, stato:.Ccdescrizione_s1176782119}]'
```

### Common OData filters

| What | Filter |
|---|---|
| By CUP | `$filter=Cccodice_cup_1267962549 eq '{CUP}'` |
| By fiscal code | `$filter=Cccodice_fiscal1934873127 eq '{CF}'` |
| Active projects | `$filter=Cccodice_stato_1426672593 eq 'A'` |
| Closed projects | `$filter=Cccodice_stato_1426672593 eq 'C'` |
| By sector | `$filter=Ccsettore_inter1475973826 eq 'STRADALI'` |

Combine with `and`/`or`. Always add `$inlinecount=allpages` for total counts.

---

## Source 3 — SCP-MIT: Published Tenders (CIG above threshold)

**Base URL:** `https://www.serviziocontrattipubblici.it/WSConsultBandi/rest/`
**Method:** POST + `Content-Type: application/x-www-form-urlencoded`
**Note:** Use `-k` flag to skip SSL verification (self-signed certificate).
**Important:** `page_limit` and `offset` go as **URL query params**; all other filters go in the **form body**.
**`stato` values:** `1`=In corso, `2`=Scaduti, `3`=Tutti. Use `3` when searching by CIG to avoid missing results.

### Search by CIG — tender list (Bandi)

```bash
curl -sSkX POST "https://www.serviziocontrattipubblici.it/WSConsultBandi/rest/Bandi/Lista?page_limit=10&offset=0" -H "Content-Type: application/x-www-form-urlencoded" -d "stato=3&cig=8874674CA7" | jq '.'
```

### Search by CIG — award results (Esiti)

```bash
curl -sSkX POST "https://www.serviziocontrattipubblici.it/WSConsultBandi/rest/Esiti/Lista?page_limit=10&offset=0" -H "Content-Type: application/x-www-form-urlencoded" -d "stato=3&cig=8874674CA7" | jq '.'
```

> **Note:** Z-prefix CIG (below-threshold direct awards) appear in **Esiti**, not in Bandi.
> Try both endpoints when a CIG returns no results in one of them.

---

## Source 4 — ANAC BDNCP: CUP↔CIG Join & Below-Threshold CIGs

**Dataset pages:**
- CIG: `https://dati.anticorruzione.it/opendata/dataset/cig`
- CUP: `https://dati.anticorruzione.it/opendata/dataset/cup`

**Access:** Bulk CSV/JSON download (no live API — WAF blocks programmatic queries).
**Live API:** Not available.

### Workflow

1. Download the dataset CSV from the ANAC portal.
2. Load into DuckDB for fast querying:

```bash
duckdb -c "DESCRIBE SELECT * FROM read_csv_auto('cup.csv', HEADER=TRUE) LIMIT 1;"
duckdb -c "SELECT * FROM read_csv_auto('cup.csv', HEADER=TRUE) WHERE cig = 'Z063947806' LIMIT 10;"
```

### Key use cases

- Find CIG(s) associated with a CUP: filter `cup` column.
- Find details of a Z-prefix CIG (direct award): filter `cig` column.

---

## Source 5 — ANAC dettaglio-cig: Full CIG Detail

**Portal:** `https://dettaglio-cig.anticorruzione.it/cig/{CIG}`
**Method:** Browser automation via `scripts/cig-fetch.sh`
**Requires:** `agent-browser`, `jq`
**Coverage:** All CIG types (Z-prefix and alphanumeric). Returns 20+ sections.

The payload is far richer than SCP-MIT: includes `bando`, `stazioneAppaltante`,
`partecipanti`, `incaricati`, `aggiudicazione`, `quadroEconomico`, `subappalti`,
`varianti`, `categorieOpera`, `pubblicazioni`, and more.

### Fetch full detail for a single CIG

```bash
bash scripts/cig-fetch.sh 8874674CA7
# → ./8874674CA7.json
```

```bash
bash scripts/cig-fetch.sh 8874674CA7 /tmp
# → /tmp/8874674CA7.json
```

### Troubleshooting

If the script fails with `Invalid response: EOF`:

```bash
agent-browser close
```

Then rerun the script.

---

## Definition of Done

A task is complete when:

- The correct source is selected based on the decision tree above.
- API call returns data (or a clear "no results" message).
- Output is readable (not a raw JSON blob) — use `jq` to format.
- For bulk sources: DuckDB query returns and formats results.

---

## Common Errors

| Error | Cause | Fix |
|---|---|---|
| `401 Unauthorized` on OpenCUP | Wrong credentials or not set | Check `OPENCUP_API_CLIENT_ID`/`SECRET` |
| Empty results on OpenBDAP | CUP not in MOP dataset | Project may not have financial monitoring data |
| No results on SCP-MIT | Z-prefix CIG | Use ANAC BDNCP bulk instead |
| SSL error on SCP-MIT | Self-signed certificate | Add `-k` flag to curl |
