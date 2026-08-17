# ANAC BDNCP: CUP↔CIG Join & Below-Threshold CIGs

**Dataset pages:**
- CIG: `https://dati.anticorruzione.it/opendata/dataset/cig`
- CUP: `https://dati.anticorruzione.it/opendata/dataset/cup`

### Three access channels — do not confuse them

The **CKAN API is behind a WAF** that demands a Chrome-like User-Agent — and rejects with
**HTTP 200** plus an HTML "Request Rejected" page, so checking the status code does not
catch it. Tested: `curl/8.0`, an empty UA, `python-requests/2.31` and even a bare
`Mozilla/5.0` are all rejected; the UA must carry `AppleWebKit/537.36` **and** a
`Chrome/… Safari/…` tail. **Downloads under `/opendata/download/` have no such
requirement** — they serve any client, including a plain `curl`.

> **But the same WAF also filters by client IP, and that rule hits the downloads too.**
> The UA rule is not the only one: requests from Azure IP space get a **403 Forbidden**
> (312-byte HTML page, `server: volt-adc`) on `/opendata/download/` regardless of
> User-Agent. Measured 2026-08-13 on `…/dataset/cup/filesystem/cup_csv.zip`:
>
> | Client IP | F5 PoP seen by ANAC | wget bare | wget +Chrome UA | curl bare | curl +Chrome UA |
> |---|---|---|---|---|---|
> | GitHub Actions runner, Azure `westcentralus`, `172.208.154.2` | `dal3-dal` (Dallas) | 403 | 403 | 403 | 403 |
> | Italian residential | `fr4-fra` (Frankfurt) | ok (exit 0, status not captured) | — | 206 | 206 |
> | Cloudflare Worker, invoked **from that same runner** | `dc12-ash` (Ashburn) | — | — | **200** | — |
>
> Two things follow. A Chrome-like UA does **not** rescue the download: varying the client
> changes nothing. And **the rule is not geographic** — the Worker's own request left from
> a US PoP (`cf-ray … -IAD`, ANAC logged `dc12-ash`) and was served 200, full 81,930,566-byte
> ZIP, `unzip -t` clean. What is blocked is the IP range, not the continent: Azure out,
> Cloudflare through.
>
> This is the cause of the recurring failures of the `pnrr_cup_cig` workflow in
> `ondata/liberiamoli-tutti` (identical 403 verified on the runs of 2026-07-06, 07-13,
> 07-20, 07-27, 08-03, 08-10).
>
> **Working fix, verified end-to-end from a runner:** fetch through a Cloudflare Worker
> acting as a plain `?url=<target>` GET proxy. Keep the proxy URL out of the code — pass
> it in from a repository secret. **Untested**, so claim nothing about them: self-hosted
> runners, EU VPS egress, GitHub Azure private networking, dataset mirrors. Note the block
> is on the *download* host; the CKAN API's UA rule is a separate, still-valid constraint.

Export the UA once and use it for the API calls:

```bash
export ANAC_UA='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
```

**CKAN discovery API — works.** Use it to resolve resource URLs, formats and sizes
instead of browsing the portal. Costs a few KB:

```bash
curl -sS -H "User-Agent: ${ANAC_UA}" "https://dati.anticorruzione.it/opendata/api/3/action/package_show?id=cup" | jq -r '.result.resources[] | "\(.name) | \(.format) | \(.size) | \(.url)"'
```

`package_list` returns the full catalogue (70+ datasets: `cig`, `cup`, `smartcig`,
`stazioni-appaltanti`, `aggiudicazioni`, `fonti-finanziamento`, `partecipanti`,
`subappalti`, `varianti`, plus yearly series `cig-2007`…`cig-2025` and
`ocds-appalti-ordinari-2018`…`2026`).

**Bulk download — works with any client.** Resources are ZIP archives, from a few KB to
over 1 GB, and support `Range` requests: inspect a multi-GB file's header without pulling
it whole. Still verify what you got is not an HTML page before parsing:

```bash
head -c 200 downloaded.file | grep -qi '<html' && echo "HTML page, not data — the resource URL is wrong or the portal returned an error"
```

**OCDS REST API — decommissioned.** `api.anticorruzione.it/opendata/ocds/api/v1/1.0.0/`
returns 404 (WSO2 `am:fault`) on every endpoint tried, including `version`, `releases` and
`tender/id/count/active`. Do not use it.

> **This kills the API, not the data.** The OCDS releases are still published as monthly
> bulk files and are perfectly reachable — see `anac-ocds.md`. What is gone is the ability to
> *query* a single CIG in OCDS: you slice the month's file instead. For point lookups
> prefer the tabular `cig` / `smartcig` datasets.

### Freshness before download

Each dataset publishes a `*_logCsv.csv` (9-13 KB) listing date and row count of every
release. Check how old the data is *before* pulling hundreds of megabytes:

```bash
curl -sS -H "User-Agent: ${ANAC_UA}" "https://dati.anticorruzione.it/opendata/download/dataset/cup/filesystem/cup_csv_logCsv.csv" | tail -3
```

### Workflow

1. Resolve the resource URL via the CKAN API (this call needs `$ANAC_UA`), then download
   it — the download itself needs no special User-Agent.
2. Load into DuckDB for fast querying:

Resources are published as **ZIP archives** — DuckDB cannot read them in place, unzip
first. `read_csv_auto` then detects the `;` delimiter on its own. Column names are
uppercase:

```bash
curl -sS -H "User-Agent: ${ANAC_UA}" "https://dati.anticorruzione.it/opendata/download/dataset/cup/filesystem/cup_csv.zip" -o cup_csv.zip && unzip -o cup_csv.zip
duckdb -c "DESCRIBE SELECT * FROM read_csv_auto('cup_csv.csv');"
# Z0B19B38F4 is a below-threshold CIG → CUP B89D15001000009
duckdb -c "SELECT * FROM read_csv_auto('cup_csv.csv') WHERE CIG = 'Z0B19B38F4';"
```

### Which dataset holds what

| Dataset | Rows / size | Key columns | Has CUP? |
|---|---|---|---|
| `cup` | 7.167.369 rows, 196 MB | `CIG`, `CUP` — nothing else | **yes, this is the bridge** |
| `cig` | incremental, ~200-550 MB per release | 61 cols: `importo_lotto`, `cod_cpv`, `tipo_scelta_contraente`, `stato`, `ESITO`, **`luogo_istat`** (6 digits), `codice_ausa`, `cf_amministrazione_appaltante`, `CUI_PROGRAMMA`, `CIG_COLLEGAMENTO`, `cig_accordo_quadro`, `FLAG_PNRR_PNC` | no |
| `smartcig` | ~680k rows per release | 26 cols: `importo_lotto`, `tipo_scelta_contraente`, `tipo_fattispecie_contrattuale`, `stato`, `data_comunicazione`, **`istat_comune`** (9 digits), `codice_ausa`, `cf_amministrazione_appaltante` | no |

Neither `cig` nor `smartcig` carries the CUP: for the association always go through the
`cup` dataset.

**Watch the two different territorial formats.** `cig.luogo_istat` is the plain 6-digit
ISTAT code; `smartcig.istat_comune` is **9 digits** — region(3) + province(3) +
comune(3) — so the ISTAT municipality code is its **last 6 characters**
(`004021046` → `021046`, Malles Venosta). In the sample, `istat_comune` was empty in
2,6% of records.

> `cig` is published as **incremental releases** on top of the last full dump: a single
> monthly file gives a partial view that looks complete. Check `cig_csv_logCsv.csv` to
> see which releases exist before assuming coverage.

### Key use cases

- Find CIG(s) associated with a CUP: filter the `CUP` column.
- Find the CUP(s) of a CIG, below-threshold included: filter the `CIG` column.

> **The `cup` dataset is just two columns, `CIG;CUP` — 7.167.369 rows as of 2026-08-06.**
> It is the authoritative CIG↔CUP bridge and it **does include below-threshold CIGs**
> (verified on a head sample: 23.475 of 69.918 rows carry the historical `Z` prefix).
> The relation is **many-to-many**: the same CUP carries several CIG, and a CIG can
> map to several CUP. Any amount aggregated across this join needs an explicit
> de-duplication rule, or it double-counts.

> **The two bridges do not fully agree — use both when completeness matters.** Measured on
> **48 CUPs** present in both sources: MOP Gare yields 257 CUP-CIG pairs, ANAC `cup` yields
> 251, **250 coincide — 7 exist only in MOP and 1 only in ANAC** (3,1% divergence). Five of
> the seven missing from ANAC are historical `Z` codes, but not all: CUP `C32C20005090001`
> has four CIG in MOP that ANAC does not associate, two of them ordinary. They come from
> different administrative chains, so treat the **union** as the complete set and the
> difference as a signal, not as an error — and state which source you used.

> Rows are **not sorted by CIG**, so prefix search is not possible on the raw file:
> index it after download if you plan repeated lookups.

