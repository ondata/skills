# Servizio Contratti Pubblici (SCP-MIT) — API Reference

**Base URL:** `https://www.serviziocontrattipubblici.it/WSConsultBandi/rest`
**Source:** WADL at `/application.wadl?detail=true`
**SSL:** Self-signed certificate — use `-k` with curl.

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
curl -sSkX POST "https://www.serviziocontrattipubblici.it/WSConsultBandi/rest/Bandi/Lista?page_limit=10&offset=0" -H "Content-Type: application/x-www-form-urlencoded" -d "stato=3&cig=A041D85520" | jq '.'
```

### Search Esiti by CIG

```bash
curl -sSkX POST "https://www.serviziocontrattipubblici.it/WSConsultBandi/rest/Esiti/Lista?page_limit=10&offset=0" -H "Content-Type: application/x-www-form-urlencoded" -d "stato=3&cig=Z1C35E8E03" | jq '.'
```

### Search by fiscal code of contracting authority

```bash
curl -sSkX POST "https://www.serviziocontrattipubblici.it/WSConsultBandi/rest/Bandi/Lista?page_limit=20&offset=0" -H "Content-Type: application/x-www-form-urlencoded" -d "stato=3&codiceFiscaleSA=02246660985" | jq '{total:.total, items:[.data[]|{oggetto,importo,dataPubblicazione}]}'
```

### Pagination

```bash
curl -sSkX POST "https://www.serviziocontrattipubblici.it/WSConsultBandi/rest/Bandi/Lista?page_limit=10&offset=10" -H "Content-Type: application/x-www-form-urlencoded" -d "stato=3&oggetto=restauro" | jq '.'
```

---

## Notes

- Z-prefix CIG (direct awards) found in **Esiti**, not in Bandi — always try both.
- Web UI at `/it/consultazione/bandi-avvisi-ed-esiti-di-gara` blocks headless browsers (WAF).
- `stato=3` is the confirmed working value for published/active records.
