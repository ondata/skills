# OpenBDAP CLI — the MOP branch in one command

`openbdap-pp-cli` is a command-line client for **one** of the nine sources: BDAP / OpenBDAP
(MOP), source #2. It does not know about OpenCUP, ANAC, ReGiS, OpenCoesione or SCP-MIT, and
it does not change the entry point of the decision tree: **a CUP still starts at OpenCUP**.
What it collapses is the MOP branch — the region-resolution dance, the two-ids problem, the
mangled column names and the client-side counting that `bdap-mop.md` documents by hand.

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

---

## Run `allinea` first — almost everything depends on it

```bash
openbdap-pp-cli allinea                 # a few minutes, ~3.900 datasets
openbdap-pp-cli allinea --tema <tema>   # a subset
openbdap-pp-cli campi --aggiorna --tema <tema>   # second index, only for `campi`
```

The archive holds the catalogue, not the rows: `cup`, `cig`, `dossier` and `opere` fetch live
data, but they need it to know **which** dataset to query. Verified against an empty archive:
all four answer `trovati: 0`, `sezioni: {}` and **exit 0**, with a `nota` in the JSON and a
warning on stderr. An agent that reads only `trovati` cannot tell that from a real miss — and
a real miss is the normal case here, so the misreading is silent and plausible.

Genuinely archive-free, because they take an OData resource id directly: `colonne`, `righe`,
`conta`, `scarica`, plus `catalogo`, `dati`, `gruppi`, `tag`, `licenze`.

`--home` does not move the archive: the `--db` default is an absolute platform path
(`~/.local/share/openbdap-pp-cli/data.db` on Linux) and only `--db` overrides it. A "fresh
home" test that does not pass `--db` is still reading the old archive.

---

## Command map — what replaces what

| Question | Command | What it replaces |
|---|---|---|
| Registry details of a CUP in MOP | `cup <CUP>` | one OData call on the national `prg`, with readable field names |
| Everything MOP holds on a CUP | `dossier <CUP>` | the `loc` → region → five regional resources dance |
| Whose CUP is this CIG, and at what price | `cig <CIG>` | a fan-out over the 21 regional `gar` partitions |
| All the works of an entity | `opere --cf <CF>` | the paginated national `prg` query plus a client-side count |
| Which resource id for region × family | `mop --regione X --famiglia Y` | the dataset map, both ids returned |
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

One call, about 5 seconds: it finds the project in the national `prg`, derives the region
(`regione: "Valle d'Aosta"`, `regione_dedotta: true`) and returns `progetto` plus the
sections `gare`, `pagamenti`, `partecipanti`, `piano-costi`, `soggetti-titolari`. `gare` comes
back with `Codice CIG`, `Importo Aggiudicazione` and `Descrizione Soggetto` already filled,
so a CUP→CIG bridge and the award amount arrive in the same object.

From a CIG instead, when you also know the region, scope the search — the difference is real
and not cache: **~24s scanning all partitions, ~2s with `--regione`**.

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

- **No `localizzazione` family.** `mop` maps six families — `progetti`, `gare`, `partecipanti`,
  `pagamenti`, `piano-costi`, `soggetti-titolari` — and `dossier` returns the same six. The
  territorial question in the SKILL's *Territorial attribution* table goes through the
  national Localizzazione dataset by hand, which the CLI still makes comfortable:

  ```bash
  openbdap-pp-cli righe c4cce647-cec4-4b60-a8ab-d308ecfba743 --dove "Codice CUP=B24B13000160001" --agent
  ```

  Remember it returns `Codice Provincia` and `Codice Comune` separately: concatenate for the
  6-digit ISTAT code, and expect more than one row for a multi-municipality CUP.
- **Nothing outside BDAP.** OpenCUP registry, ANAC tenders, PNRR and cohesion monitoring stay
  where the decision tree puts them.

## Traps that survive the CLI

| Trap | What happens | Fix |
|---|---|---|
| Silent truncation | `righe` defaults to `--limite 50` and returns exactly 50 rows **with no warning**, even when the filter matches hundreds | run `conta` first, or `--tutte --limite 0` |
| Same for sections | `dossier` and `cup` cap each section at `--limite 50` | raise `--limite` when a section looks suspiciously round |
| `scarica` is latin-1 | the CSV dump is passed through as the portal serves it: `à` arrives as the single byte `0xE0`, delimiter `;`, CRLF | `iconv -f latin1 -t utf8` before DuckDB, exactly as for the raw dump |
| JSON is not | the OData path (`cup`, `dossier`, `righe`, `cig`) returns clean UTF-8 — no conversion, and converting it corrupts it | leave it alone |
| A CUP outside MOP | `trovati: 0`, `sezioni: {}`, exit code 0 | not an error: fall back to OpenCUP and ANAC |
| An empty archive looks the same | same `trovati: 0` and exit 0, told apart only by the `nota` field | read `nota`, or run `allinea` before concluding a CUP is not in MOP |

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
