# ANAC Pubblicità Legale (PVL): the only live per-CIG lookup

Every other source on the CIG side is a bulk download. The **Piattaforma di Pubblicità a
Valore Legale** — where notices have been published since 2024, replacing the old
channels — has a **live searchable API**, and its free-text search accepts a CIG.

Access it through the `anac-pl` CLI (`--agent` gives JSON + non-interactive mode):

```bash
anac-pl cerca --query B972725FF4 --size 3 --agent          # find the notice for a CIG
anac-pl avvisi get <idAvviso> --agent                      # full structured detail
anac-pl avvisi cronologia <idAvviso> --agent               # corrections over time
anac-pl tipologie list                                     # the 12 notice templates
```

### Why it is worth a round trip

| What you get | Available elsewhere? |
|---|---|
| **link to the tender documents** (`documenti_di_gara_link`) | **no** — unique to this source |
| history of a notice's corrections | **no** |
| deadline for receipt (`termine_ricezione`), estimated lot value | no |
| CPV **with its Italian description**, lot description | code only, elsewhere |
| framework agreement / dynamic purchasing / e-auction flags | no |
| CIG per lot, contracting authority `codice_fiscale` | yes — and that is your join key |

The detail is eForms-shaped: one object per lot, each carrying `cig`, `cpv`,
`descrizione`, `valore_complessivo_stimato`, `termine_ricezione`, `natura_principale`,
`luogo_istat` and the documents link.

### Coverage and limits — verified

- **Starts in 2024.** A 2018 CIG returns nothing; 2025-2026 CIGs resolve. This makes PVL
  and **SCP-MIT complementary in time**, not alternative: SCP-MIT up to 2023, PVL from
  2024 on.
- **Below-threshold notices are included** — template `8a` "Affidamenti diretti sotto
  soglia" (scheda `AD3`) returns results. Do not assume this source is above-threshold only.
- **Not every CIG has a notice.** Of four CIGs tested, two resolved; one was pre-2024 and
  one — a small direct award — simply has no published notice. Absence here is not
  evidence the CIG does not exist: check the ANAC datasets.
- **No CUP anywhere in the payload.** The CIG↔CUP bridge remains the `cup` dataset.
- **`luogo_istat` here is not always a code.** Despite the name, it carries either a
  9-digit code (`003015146`) or the **municipality name in plain text** (`FIUMINATA`,
  `AMATRICE`): 8 notices out of 9 inspected returned the name. Test the value before
  parsing it, and do not feed it to a numeric join. Use `smartcig` / `cig` when you need a
  reliable code.

> `anac-pl sync` keeps a local SQLite copy for offline work, and `search-local` queries it
> without network. Useful when iterating over many CIGs.

