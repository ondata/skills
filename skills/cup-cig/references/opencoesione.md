# OpenCoesione / BDU: cohesion policy projects

Cohesion-policy projects. Two things make it the easiest source here to query in bulk: the
REST API needs **no authentication** (unlike OpenCUP, which requires client id and secret),
and it is **the only source publishing Parquet**, which makes membership tests over
thousands of CUPs a single download and a join (see below).

> The 2021-2027 monitoring moved to ReGiS, but **OpenCoesione still publishes that cycle**:
> `OC_DESCR_CICLO` carries `Ciclo di programmazione 2021-2027` rows. Do not assume the
> portal stops at 2014-2020 when checking whether a CUP is in the cohesion perimeter.

```bash
curl -sS "https://opencoesione.gov.it/it/api/progetti/?format=json&cup=E18B20001900006&page_size=1" | jq '.results[0]'
```

Resources: `progetti`, `soggetti`, `aggregati`, `temi`, `nature`, `territori`, `programmi`.
Licence CC-BY 4.0. Covers the 2000-2006 → 2021-2027 programming cycles.

| Field | Content |
|---|---|
| `cup`, `cod_locale_progetto` | the two identifiers; `cup=` is a **working filter** |
| `oc_titolo_progetto`, `oc_tema_sintetico`, `cup_descr_natura` | what the project is |
| `oc_finanz_tot_pub_netto`, `tot_pagamenti`, `percentuale_avanzamento` | money and progress |
| `oc_stato_progetto`, `oc_descr_ciclo` | status and programming cycle |
| `soggetti`, `territori` | nested arrays |

**There is no CIG here**: OpenCoesione aggregates *by CUP*, which is precisely what lets it
group information about the same intervention even when financed through several
instruments or in successive phases.

### Three traps, all verified

- **`limit` is silently ignored, and so is `per_page`.** The working parameter is
  **`page_size`**. Guess wrong and a single call returns tens of megabytes instead of a
  couple of kilobytes — which, combined with the rate limit below, will stall you.
- **Rate limit: 12 requests/minute anonymous**, 60/minute with free credentials requested at
  `info@opencoesione.gov.it`.
- Filters must be real field names — `search=` and `q=` are accepted but **ignored**, and
  return the whole catalogue's count, which looks like a successful query.

> For bulk work use the Parquet downloads below; the API is for point lookups. At 12 requests
> per minute, iterating a few thousand CUPs through it takes hours — and note that a throttled reply
> is a JSON body with a `detail` key, **not an HTTP error**, so `.count // 0` silently reads
> it as "project not found". Always branch on `.detail` before trusting a zero.

### Parquet bulk — the fastest way to answer "is this CUP in the cohesion perimeter"

Every main dataset is published in **Parquet** alongside zip/csv, at stable URLs under
`/it/opendata/<name>.parquet`. DuckDB reads them directly, no unzip, no encoding fix, no
delimiter guessing — the opposite of the BDAP dumps.

```bash
curl -sSL "https://opencoesione.gov.it/it/opendata/progetti.parquet" -o oc_progetti.parquet
duckdb -c "SELECT count(*) FROM read_parquet('oc_progetti.parquet')"
```

Available: `progetti`, `progetti_esteso`, `soggetti`, `localizzazioni`, `fasi`, `pagamenti`,
`impegni`, `indicatori`, plus per-cycle and per-fund cuts (FESR, FSE, FSC, PAC, SNAI, CTE,
SIE). Updated bimonthly, CC-BY 4.0. Key columns: `CUP`, `OC_DESCR_CICLO`, `CUP_DESCR_NATURA`.

A membership test over thousands of CUPs then costs one download and one join:

```bash
duckdb -c "SELECT count(*) FROM read_csv('my_cups.csv') c WHERE c.cup IN (SELECT CUP FROM read_parquet('oc_progetti.parquet'))"
```

Use it to kill a tempting hypothesis. When CUPs are missing from MOP it is natural to assume
"then they must be in BDU" — and for whole categories of spending that is simply false, because
they are financed outside the cohesion perimeter altogether. Post-earthquake reconstruction is
one such case: run the join and a set of thousands of CUPs comes back with a handful of hits.
**The assumption is testable in one query — test it instead of carrying it.**

