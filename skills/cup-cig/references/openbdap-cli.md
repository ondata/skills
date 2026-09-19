# OpenBDAP CLI — the MOP branch in one command

`openbdap-pp-cli` is a command-line client for **one** of the nine sources: BDAP / OpenBDAP
(MOP), source #2. It does not know about OpenCUP, ANAC, ReGiS, OpenCoesione or SCP-MIT, and
it does not change the entry point of the decision tree: **a CUP still starts at OpenCUP**.
What it collapses is the MOP branch — the hunt for the right regional partition, the two-ids
problem, the mangled column names and the client-side counting that `bdap-mop.md` documents
by hand.

A miss here is still the normal case: roughly half of an arbitrary set of CUP is not in MOP.
`openbdap-pp-cli cup X` answering `trovati: 0` means *not in MOP*, never *no such project*.

**Optional dependency.** Everything below can be done with `curl` against the OData endpoints
in `bdap-mop.md`; the CLI is the shorter path when it is installed, not a requirement.

```bash
npx -y @mvanhorn/printing-press-library install openbdap   # CLI + agent skill
npx -y @mvanhorn/printing-press-library install openbdap --cli-only
openbdap-pp-cli doctor                                     # connectivity + paths
```

The CLI's own help and JSON keys are in Italian (`righe`, `dove`, `limite`, `trovati`). Add
`--agent` to any command for JSON on stdout and no prompts.

Everything here was checked on 2026-09-19. A build older than that date differs on four
points, all of them ways of being quietly wrong rather than failing: no `localizzazione`
section in `dossier` and the region guessed from the owner's name, no note when a result is
truncated, no `archivio_vuoto` field, and `scarica` emitting latin-1. If a run does not match
what this file describes, reinstall before suspecting the data.

---

## Run `allinea` first — almost everything depends on it

```bash
openbdap-pp-cli allinea                 # a few minutes, ~3.900 datasets
openbdap-pp-cli allinea --tema <tema>   # a subset
openbdap-pp-cli campi --aggiorna --tema <tema>   # second index, only for `campi`
```

The archive holds the catalogue, not the rows: `cup`, `cig`, `dossier` and `opere` fetch live
data, but they need it to know **which** dataset to query. With no archive all four answer
`trovati: 0`, `sezioni: {}` and **exit 0** — the same shape as a genuine miss, which here is
the normal case. What separates the two is `archivio_vuoto: true`, set alongside the `nota`
and absent when the code is simply not in MOP. **Read that field before concluding anything
from a zero**; the exit code will not tell you, by design, because the command did not fail.

Genuinely archive-free, because they take an OData resource id directly: `colonne`, `righe`,
`conta`, `scarica`, plus `catalogo`, `dati`, `gruppi`, `tag`, `licenze`.

---

## Command map — what replaces what

| Question | Command | What it replaces |
|---|---|---|
| Registry details of a CUP in MOP | `cup <CUP>` | one OData call on the national `prg`, with readable field names |
| Everything MOP holds on a CUP | `dossier <CUP>` | Localizzazione to find the region, then six regional resources queried one by one |
| Whose CUP is this CIG, and at what price | `cig <CIG>` | a fan-out over the 21 regional `gar` partitions, plus `pga` for the bidders |
| All the works of an entity | `opere --cf <CF>` | the paginated national `prg` query plus a client-side count |
| Which resource id for region × family | `mop --regione X --famiglia Y` | the dataset map, both ids returned |
| Where does the work fall | `dossier` section `localizzazione`, or `mop --famiglia localizzazione` | the national Localizzazione dataset, with the 6-digit ISTAT code assembled by hand |
| Which dataset holds a field | `campi "codice fiscale"` | opening datasets one by one |
| Readable name → filter id | `colonne <odata id>` | guessing `Cccodice_cup_1267962549` |
| Filtered rows | `righe <odata id> --dove "Codice CUP=..."` | `$filter` with mangled ids |
| A count that is not zero | `conta <odata id> --dove ...` | counting `.d.results` client-side |

`mop` and `cerca` return **both** ids for every dataset — `id` (package id, for the CSV dump)
and `odata_id` (XML resource id, for OData) — which is what makes the two-ids trap disappear.

---

## Worked example — a CUP end to end

```bash
openbdap-pp-cli dossier B24B13000160001 --agent
```

One call, about 9 seconds: it finds the project in the national `prg`, reads the national
Localizzazione to learn which region it is, and returns `progetto` plus the sections
`localizzazione`, `gare`, `pagamenti`, `partecipanti`, `piano-costi`, `soggetti-titolari`.
`gare` comes back with `Codice CIG`, `Importo Aggiudicazione` and `Descrizione Soggetto`
already filled, so a CUP→CIG bridge and the award amount arrive in the same object, and
`localizzazione` carries `Codice ISTAT Comune` already concatenated from province and
municipality.

When Localizzazione has no row for the CUP, the region is guessed from a region name inside
`Descrizione Titolare` / `Descrizione Ente`, and that guess is declared with
`regione_dedotta: true`. It only fires for entities whose name contains the region
(`REGIONE AUTONOMA VALLE D'AOSTA`), never for a municipality, so on a fallback the command
queries every partition: correct, just slower.

From a CIG instead, when you also know the region, scope the search: **~19s against ~2s**,
measured with `--no-cache`. What is left is not traffic — the 42 partitions of `gar` and `pga`
are queried twelve at a time and their schema is read once per family — but the client's own
rate limiter, which paces at two requests a second out of courtesy to a public portal.
`--rate-limit 0` takes the same search to ~4s; use it for one search, not for `allinea`.
Responses are cached for a few minutes, so a list of CIGs worked through in one go pays less
than the first number suggests.

```bash
openbdap-pp-cli cig BAE51BB300 --regione "Valle d'Aosta" --agent
```

Set-wide, by readable column name, with a count first:

```bash
openbdap-pp-cli conta bda1676b-62ab-44b7-8f9a-ca93b8534488 --dove "Descrizione Titolare~COMUNE DI PALERMO"
openbdap-pp-cli righe bda1676b-62ab-44b7-8f9a-ca93b8534488 --dove "Descrizione Titolare~COMUNE DI PALERMO" --campi "Codice CUP,Descrizione CUP Integrale" --tutte --limite 0 --csv
```

`=` is equality, `~` is substring.

---

## What the CLI does not cover

- **Nothing outside BDAP.** OpenCUP registry, ANAC tenders, PNRR and cohesion monitoring stay
  where the decision tree puts them.
- **No territorial share.** `localizzazione` lists every municipality a CUP touches and gives
  no percentage, so an amount still cannot be split across them: that is a MOP limit, not a
  CLI one, and ReGiS remains the only source with a share.

All seven MOP families are reachable. `dossier` returns six of them plus `localizzazione`, and
`mop --famiglia localizzazione` returns the national dataset on its own — note that a
`--regione` filter hides that row, because Localizzazione is national and carries no region.

## Traps that survive the CLI

| Trap | What happens | Fix |
|---|---|---|
| Truncation, now announced | `righe` still defaults to `--limite 50`, but a result that touches the limit carries `meta.nota` with the real total (`risultato troncato a --limite 50 di 347 righe`) and a warning on stderr. `results` stays an array | read `meta.nota`, then `--tutte --limite 0`. Same note in `cup`, `cig` and each `dossier` section |
| A CUP outside MOP | `trovati: 0`, `sezioni: {}`, exit code 0 | not an error: fall back to OpenCUP and ANAC |
| An empty archive looks the same | same `trovati: 0` and exit 0 | the discriminator is `archivio_vuoto: true`, not the exit code |
| `scarica --raw` is latin-1 | the default output is converted to UTF-8 (byte-identical to `iconv -f ISO-8859-1`), but `--raw` hands you the portal's own bytes: `à` as `0xE0`, delimiter `;`, CRLF | only ask for `--raw` if you are going to convert it yourself |
| JSON needs nothing | the OData path (`cup`, `dossier`, `righe`, `cig`) returns clean UTF-8 — converting it corrupts it | leave it alone |

---

## CLI, web portal or raw OData

| You need | Route | Why |
|---|---|---|
| A handful of CUP, scripted, joinable with other sources | **CLI** | JSON or CSV, readable column names, no 300-CUP cap |
| A set-wide question (all the works of an entity, a whole region) | **CLI** | real totals, `--tutte` pagination, the dump when it is worth it |
| Which dataset even exists, or where a field lives | **CLI** (`cerca`, `campi`, `serie`) | the portal's own catalogue search is the weak part |
| The **MOP indicators** of a work | **web portal** | the `RICERCA PER CUP` form on `openbdap.rgs.mef.gov.it` returns an Excel with three sheets — *Dettaglio CUP*, *Dettaglio CIG*, *Dettaglio Indicatori*. The indicators sheet has no counterpart in the open-data catalogue: the only datasets named *Indicatori* there are the budget *Note Integrative*, nothing MOP |
| A quick visual check on one entity | **web portal** | the per-entity report, addressable by fiscal code: `https://openbdap.rgs.mef.gov.it/BO/OpenDocument?modalita=link&docID=FgAUHFlfxgsAFwYAAACHAiUbeOO1D67w&T=BusinessObject&idType=CUID&noDetailsPanel=true&X_Ente=<CF>` (redirects to a BusinessObjects session; not scriptable) |
| Something the CLI has no flag for | **raw OData** | `bdap-mop.md` keeps the endpoints, and the CLI is not a prerequisite for any of them |

The web form caps at **300 CUP per query** and hands back Excel: past that, or whenever the
result has to be joined with ANAC or OpenCUP, the CLI is the route.

The onData vademecum documenting both web routes:
<https://pnrr.datibenecomune.it/fonti/openbdap/>
