# ANAC OCDS bulk: the full procedure structure

The tabular datasets give you one row per CIG. The OCDS bulk gives you the **whole
procedure as one object**: lots, parties with their roles, awards, contracts. Use it when
the flat view is not enough — who the parties were, how lots relate to awards, what the
procurement method was.

**URL pattern** (one file per month):

```
https://dati.anticorruzione.it/opendata/download/dataset/ocds/filesystem/bulk/{YYYY}/{MM}.json
```

**Licence** CC-BY-SA 4.0, declared in the file manifest. **Size ~3,1 GB per month**
uncompressed — over 35 GB for a year. Do not download one to look at it.

### Where the identifiers live

Verified on 151 consecutive releases:

| Identifier | Path | Notes |
|---|---|---|
| **CIG** | `tender.lots[].id` | 151/151 releases; same value in `awards[].items[].id` and `relatedLot` |
| tender id | `tender.id` | **not a CIG** — it is the procedure id (`CONSIP_RDO_5571347`, `225-17693`, a URI…). Only 1 of 151 happened to be a CIG |
| OCID | `ocid` | `ocds-hu01ve-{tender.id}` |
| CF stazione appaltante | `buyer.id`, `parties[].identifier.id` | scheme `IT-CF` |
| **Codice AUSA** | `parties[].additionalIdentifiers[]` | scheme `AUSA` |
| CPV | `awards[].items[].classification.id` | scheme `CPV` |
| **CUP** | — | **absent**: no `planning` block in any of the 151 releases. For the CUP use the `cup` dataset |

Most releases carry a single lot (148 of 151), so one release usually means one CIG — but
do not assume it: read the array.

### Inspecting it without downloading it

The endpoint honours `Range`, so the first few MB are enough to see the schema:

```bash
curl -sS -r 0-2000000 "https://dati.anticorruzione.it/opendata/download/dataset/ocds/filesystem/bulk/2025/06.json" -o sample.json
```

The slice is truncated JSON: parse it incrementally (`json.JSONDecoder().raw_decode` in a
loop over the `releases` array) rather than with `jq`, which needs a complete document.

