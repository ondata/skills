# ANAC contract lifecycle: what happened after the award

Sources 4 and 5 describe the tender. This family describes **what happened to the
contract**: who bid, who won and at what discount, how the works advanced, what was
certified and paid, what was subcontracted, varied, suspended or terminated early.

Twelve datasets, **all keyed on `cig` as the first column**, most with
`id_aggiudicazione` as a secondary key.

| Dataset | Answers | Key columns beyond `cig` |
|---|---|---|
| `aggiudicazioni` | how it was awarded | `importo_aggiudicazione`, `ribasso_aggiudicazione`, `criterio_aggiudicazione`, `esito`, `numero_offerte_ammesse` / `_escluse`, `num_imprese_offerenti`, `flag_subappalto`, `data_aggiudicazione_definitiva` |
| `aggiudicatari` | who won | `codice_fiscale`, `denominazione`, `ruolo`, `tipo_soggetto` |
| `partecipanti` | who bid and lost | same four columns |
| `stati-avanzamento` | **how much was certified and paid** | `importo_sal`, `progressivo_sal`, `data_emissione_sal`, `flag_ritardo`, `n_giorni_scostamento`, **`DATA_CERT_PAGAMENTO`**, **`IMPORTO_CERT_PAGAMENTO`**, `GIORNI_PROROGA` |
| `quadro-economico` | how the money is split | `importo_lavori`, `importo_servizi`, `importo_forniture`, `importo_progettazione`, `importo_sicurezza`, `somme_a_disposizione` |
| `fonti-finanziamento` | where the money comes from | 12 mutually exclusive columns: state / regional / local earmarked funds, `mutuo`, `apporto_di_capitali_privati`, own budget… |
| `subappalti` | who subcontracted what | `cf_subappaltante`, `codice_fiscale`, `denominazione`, `descrizione_categoria`, `cod_cpv`, `data_autorizzazione` |
| `avvio-contratto` | when work started | `data_stipula_contratto`, `data_inizio_effettiva`, `data_termine_contrattuale`, `consegna_frazionata` |
| `sospensioni` | when it stopped | `data_sospensione`, `data_ripresa`, `descrizione_motivo` |
| `varianti` | what changed | `motivo_variante`, `data_approvazione_variante`, `CIG_PROROGA` |
| `fine-contratto` | how it ended | `data_effettiva_ultimazione`, `motivo_risoluzione`, `motivo_interruzione_anticipata`, `giorni_proroga` |
| `collaudo` | how it was signed off | `esito_collaudo`, `data_cert_collaudo`, `RISERVE_AVANZATE`, `RISERVE_DEFINITE`, `IMPORTO_CONTENZ_RISOLTO` |

`stati-avanzamento` is what makes the CIG side symmetrical to the CUP side: BDAP MOP
`sal` gives payments **per project and year**, this one gives them **per contract, per
SAL, with dates**.

### Full dumps and monthly increments

Each dataset is published as a **full dump** plus **monthly incremental releases**
(`{YYYYMMDD}-{dataset}_csv.zip`). The full archives run from a hundred megabytes to nearly a
gigabyte — `partecipanti` and `aggiudicazioni` are the heavy ones, `subappalti` and
`stati-avanzamento` the manageable ones.

An increment is **orders of magnitude smaller than the dump**, and that is the trap: it
downloads fast, parses cleanly and looks like a complete dataset. **Pull the full dump first
and apply the increments**, or you will be looking at one month of activity while believing it
is the whole archive. Read `{dataset}_csv_logCsv.csv` to see which releases exist — and
filter it by format, since it lists CSV, JSON and TTL together and the TTL row counts are
much larger.

### Joining the lifecycle

```bash
# after downloading and unzipping the datasets you need
duckdb -c "
  SELECT a.cig, a.importo_aggiudicazione, a.ribasso_aggiudicazione, w.denominazione AS vincitore,
         (SELECT sum(IMPORTO_CERT_PAGAMENTO) FROM read_csv_auto('stati-avanzamento.csv') s WHERE s.cig = a.cig) AS pagato
  FROM read_csv_auto('aggiudicazioni.csv') a
  LEFT JOIN read_csv_auto('aggiudicatari.csv') w ON w.cig = a.cig
  WHERE a.cig = 'B972725FF4';"
```

> **A CIG can carry several awards.** `id_aggiudicazione` distinguishes them, and every
> lifecycle dataset repeats it: join on `cig` **and** `id_aggiudicazione` when you need
> per-award figures, or sums will mix distinct awards of the same tender.

