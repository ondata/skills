# SCP-MIT: historical published tenders (up to 2023)

**Base URL:** `https://www.serviziocontrattipubblici.it/WSConsultBandi/rest/`
**Method:** POST + `Content-Type: application/x-www-form-urlencoded`
**Volume:** 232.227 Bandi, 561.871 Esiti
**Full API reference:** `references/scp-mit-api.md`

> **This source stopped being fed at the end of 2023.** Tenders published after
> 01/01/2024 are **39** in the whole archive, and after 01/01/2025 **zero** — publication
> moved to ANAC with the digitalisation reform. Use SCP-MIT for the historical record
> only; **from 2024 on its successor is the PVL (`anac-pvl.md`)**, which picks up exactly where
> this one stops.

Three rules that decide whether a query returns anything:

- **`stato` is mandatory.** Omitting it returns `total: 0` even for a CIG that is
  certainly present. Values: `1`=In corso, `2`=Scaduti, `3`=Tutti — use `3`.
- **`page_limit` and `offset` are URL query params**; every filter goes in the form body.
- **Only Esiti expose the `cig` field**, and the value carries a trailing dash
  (`7383208FF8-`). Bandi records have no CIG at all: `id`, `oggetto`, `ente`, `provincia`,
  `dataPubblicazione`, `importo`, `dataScadenza`.

### Search by CIG — award results (Esiti)

```bash
curl -sSX POST "https://www.serviziocontrattipubblici.it/WSConsultBandi/rest/Esiti/Lista?page_limit=10&offset=0" -H "Content-Type: application/x-www-form-urlencoded" -d "stato=3&cig=7383208FF8" | jq '.'
```

### Browse by date — tender list (Bandi)

```bash
curl -sSX POST "https://www.serviziocontrattipubblici.it/WSConsultBandi/rest/Bandi/Lista?page_limit=10&offset=0" -H "Content-Type: application/x-www-form-urlencoded" -d "stato=3&pubblicatoDopoIl=01/01/2022" | jq '.'
```

> The `-k` flag is **no longer needed**: the certificate validates. Older instructions
> carried it because of a former self-signed certificate.

---

## Full API reference (endpoints, params, examples)

## Servizio Contratti Pubblici (SCP-MIT) — API Reference

**Base URL:** `https://www.serviziocontrattipubblici.it/WSConsultBandi/rest`
**Source:** WADL at `/application.wadl?detail=true`
**SSL:** the certificate validates (checked 2026-08-12); `-k` is no longer needed.

> **Coverage stops at 2023.** Bandi published after 01/01/2024: 39 in the whole archive.
> After 01/01/2025: none. Totals: 232.227 Bandi, 561.871 Esiti. Publication moved to
> ANAC's BDNCP with the 2024 digitalisation reform — treat this API as a historical
> archive.
>
> **`stato` is mandatory**: without it a query returns `total: 0` even for a CIG that is
> present. **Only Esiti carry the `cig` field**, with a trailing dash (`7383208FF8-`).

---

## General call pattern

```
POST {base_url}/{Resource}/Lista?page_limit={N}&offset={N}
Content-Type: application/x-www-form-urlencoded

{filter params in body}
```

- `page_limit` and `offset` → **URL query params**
- All filter params → **form body**

---

## Resources

Three parallel resources with identical filter parameters:

| Resource | Description |
|---|---|
| `Bandi` | Published tenders |
| `Esiti` | Award results |
| `Avvisi` | Notices |

---

## Endpoint: Lista (Bandi / Esiti / Avvisi)

```
POST /Bandi/Lista?page_limit={N}&offset={N}
POST /Esiti/Lista?page_limit={N}&offset={N}
POST /Avvisi/Lista?page_limit={N}&offset={N}
```

### URL params

| Param | Type | Description |
|---|---|---|
| `page_limit` | int | Page size |
| `offset` | int | Offset for pagination |

### Body params (form-encoded)

| Param | Description |
|---|---|
| `cig` | CIG code |
| `stato` | Status filter: `1`=In corso, `2`=Scaduti, `3`=Tutti |
| `oggetto` | Tender object (text search) |
| `codiceCpv` | CPV code |
| `atto` | Act type |
| `regioneSA` | Region of contracting authority |
| `provinciaSA` | Province of contracting authority |
| `stazioneAppaltante` | Contracting authority name |
| `codiceFiscaleSA` | Fiscal code of contracting authority |
| `sysconSA` | Internal SA code |
| `tipoBando` | Tender type |
| `categoria` | Category |
| `importo` | Amount (exact) |
| `importoDa` | Amount from |
| `pubblicatoDopoIl` | Published after (date) |
| `pubblicatoPrimaDel` | Published before (date) |
| `trasmessoDopoIl` | Transmitted after (date) |
| `trasmessoPrimaDel` | Transmitted before (date) |
| `tipoAtto` | Act type |
| `sceltaContr` | Contracting procedure |

### Response structure

```json
{
  "total": 1,
  "page_limit": 1,
  "offset": 0,
  "data": [
    {
      "id": 752704,
      "oggetto": "...",
      "ente": "...",
      "provincia": "PA",
      "dataPubblicazione": "28/12/2023",
      "importo": 2658377.63,
      "dataScadenza": "12/02/2024"
    }
  ]
}
```

Esiti response also includes `cig` field in each item.

---

## Endpoint: Dettaglio (Bandi)

```
GET /Bandi/Dettaglio?numeroPubblicazione={N}
```

| Param | Description |
|---|---|
| `numeroPubblicazione` | Publication number from Lista response |

---

## Endpoint: Dettaglio (Avvisi)

```
GET /Avvisi/Dettaglio?codiceSA={cod}&codiceSistema={cod}
```

---

## Endpoint: Documento

```
GET /Bandi/Documento?id={id}&numeroPubblicazione={N}&nrDoc={N}
GET /Esiti/Documento?id={id}&numeroPubblicazione={N}&nrDoc={N}
GET /Avvisi/Documento?codiceSA={cod}&codiceSistema={cod}&nrDoc={N}
GET /Esiti/DocumentoDecoded?id={id}&numeroPubblicazione={N}&nrDoc={N}
```

---

## Endpoint: CPV lookup

Hierarchical CPV code browser:

```
GET /CPV?token={text}                              # top-level search
GET /CPV/Cod1?cod0={c0}&token={text}               # level 1
GET /CPV/Cod2?cod0={c0}&cod1={c1}&token={text}     # level 2
GET /CPV/Cod3?cod0={c0}&cod1={c1}&cod2={c2}&token={text}  # level 3
GET /CPV/Dettaglio?codcpv={cpv}&token={text}       # full CPV detail
```

---

## curl examples

### Search Bandi by CIG

```bash
curl -sSX POST "https://www.serviziocontrattipubblici.it/WSConsultBandi/rest/Bandi/Lista?page_limit=10&offset=0" -H "Content-Type: application/x-www-form-urlencoded" -d "stato=3&cig=A041D85520" | jq '.'
```

### Search Esiti by CIG

```bash
curl -sSX POST "https://www.serviziocontrattipubblici.it/WSConsultBandi/rest/Esiti/Lista?page_limit=10&offset=0" -H "Content-Type: application/x-www-form-urlencoded" -d "stato=3&cig=Z1C35E8E03" | jq '.'
```

### Search by fiscal code of contracting authority

```bash
curl -sSX POST "https://www.serviziocontrattipubblici.it/WSConsultBandi/rest/Bandi/Lista?page_limit=20&offset=0" -H "Content-Type: application/x-www-form-urlencoded" -d "stato=3&codiceFiscaleSA=02246660985" | jq '{total:.total, items:[.data[]|{oggetto,importo,dataPubblicazione}]}'
```

### Pagination

```bash
curl -sSX POST "https://www.serviziocontrattipubblici.it/WSConsultBandi/rest/Bandi/Lista?page_limit=10&offset=10" -H "Content-Type: application/x-www-form-urlencoded" -d "stato=3&oggetto=restauro" | jq '.'
```

---

## Notes

- Below-threshold awards are found in **Esiti**, not in Bandi — always try both. Verified:
  `A041D85520` returns 1 in Bandi and 0 in Esiti, `Z1C35E8E03` the opposite. Historically
  these codes carried the `Z` prefix, dropped from 2024 (see SKILL.md decision tree).
- Web UI at `/it/consultazione/bandi-avvisi-ed-esiti-di-gara` blocks headless browsers (WAF).
- `stato=3` is the confirmed working value for published/active records.
