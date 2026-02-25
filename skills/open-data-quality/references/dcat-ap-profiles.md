# DCAT-AP National Profiles Reference

Comparison of DCAT-AP national profiles for metadata completeness validation.
Use this file when Phase 5 of the skill detects a specific national profile.

Cardinality notation: **M** = Mandatory, **R** = Recommended, **O** = Optional, **—** = Not defined

---

## Dataset-level fields

| RDF property | DCAT-AP 2.x | IT | DE | FR | BE | NL | UK | ES |
|-------------|:-----------:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| `dct:title` | **M** | **M** | **M** | **M** | **M** | **M** | **M** | **M** |
| `dct:description` | **M** | **M** | **M** | **M** | **M** | **M** | **M** | **M** |
| `dcat:distribution` | R | R | R | R | R | R | R | R |
| `dct:publisher` | **M** | **M** | **M** | **M** | **M** | **M** | R | **M** |
| `dcat:keyword` | R | R | R | R | R | R | R | R |
| `dcat:theme` | R | **M** | R | R | R | R | R | R |
| `dct:identifier` | R | **M** | **M** | R | **M** | **M** | R | **M** |
| `dct:issued` | R | R | R | R | R | R | R | R |
| `dct:modified` | R | R | R | R | R | R | R | R |
| `dct:language` | R | R | R | R | R | R | R | R |
| `dct:license` | R | R | R | R | **M** | R | R | R |
| `dct:accrualPeriodicity` | R | R | R | R | R | R | R | R |
| `dct:spatial` | R | R | R | R | R | **M** | R | R |
| `dct:temporal` | O | R | O | O | O | O | O | O |
| `dcat:contactPoint` | R | R | R | R | R | R | R | R |
| `dct:conformsTo` | O | R | O | O | O | R | O | O |
| `dct:provenance` | O | — | — | — | O | R | O | — |
| `dct:rightsHolder` | O | — | R | — | R | — | O | — |
| `foaf:landingPage` | O | — | O | O | O | R | O | O |
| `adms:versionInfo` | O | O | O | — | O | O | O | — |
| `adms:versionNotes` | O | O | O | — | O | O | O | — |
| **`dcatapit:datasetHolder`** | — | **M** | — | — | — | — | — | — |
| **`dcatapit:creator`** | — | O | — | — | — | — | — | — |
| **`dcatapit:geographicalName`** | — | O | — | — | — | — | — | — |
| `dcat:spatialResolutionInMeters` | O | — | O | O | — | R | O | — |
| `dcat:temporalResolution` | O | — | O | — | — | — | — | — |

---

## Distribution-level fields

| RDF property | DCAT-AP 2.x | IT | DE | FR | BE | NL | UK | ES |
|-------------|:-----------:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| `dcat:accessURL` | **M** | **M** | **M** | **M** | **M** | **M** | **M** | **M** |
| `dcat:downloadURL` | R | R | R | R | R | R | R | R |
| `dct:format` | R | R | R | R | R | R | R | R |
| `dcat:mediaType` | R | R | R | R | R | R | R | R |
| `dct:license` | R | **M** | R | R | **M** | R | R | R |
| `dct:description` | O | R | O | O | O | R | O | O |
| `dct:issued` | O | R | O | O | O | O | O | O |
| `dct:modified` | O | R | O | O | O | O | O | O |
| `dcat:byteSize` | O | R | O | O | O | R | O | O |
| `spdx:checksum` | O | O | O | — | O | O | O | — |
| `cnt:characterEncoding` | — | R | — | — | — | — | — | — |
| `dct:rights` | O | — | O | — | O | — | O | — |
| `dct:conformsTo` | O | O | O | — | O | R | O | — |
| `adms:status` | O | O | O | — | O | O | O | — |

---

## Profile-specific identifiers and vocabularies

### CKAN field mapping (how DCAT properties appear in CKAN JSON)

Different CKAN instances serialize DCAT differently. Common mappings:

| DCAT property | CKAN JSON path | Notes |
|---------------|---------------|-------|
| `dct:title` | `.title` | Always top-level |
| `dct:description` | `.notes` | Top-level |
| `dct:publisher` | `.organization.title` | Top-level |
| `dct:license` | `.license_id` or `.license_title` | Top-level |
| `dct:issued` | `.extras[].key=="issued"` | Often in extras |
| `dct:modified` | `.extras[].key=="modified"` | Often in extras |
| `dct:identifier` | `.extras[].key=="identifier"` | Often in extras |
| `dct:language` | `.extras[].key=="language"` | Often in extras |
| `dcat:theme` | `.extras[].key=="theme"` | Often in extras |
| `dct:accrualPeriodicity` | `.extras[].key=="frequency"` | Often in extras |
| `dct:spatial` | `.extras[].key=="geographical_geonames_url"` | IT-specific path |
| `dct:temporal` | `.extras[].key=="temporal_coverage"` | Often in extras |
| `dcatapit:datasetHolder` | `.extras[].key=="holder_name"` | IT only |
| Resource format | `.resources[].format` | Per-resource |
| Resource MIME | `.resources[].mimetype` | Per-resource |
| Resource license | `.resources[].license_id` | Per-resource |
| Resource size | `.resources[].size` | Per-resource |
| Resource encoding | `.resources[].extras[].key=="encoding"` | IT, varies |

---

## National profile documentation

| Country | Profile name | Specification URL |
|---------|-------------|------------------|
| EU baseline | DCAT-AP 2.1.1 | https://joinup.ec.europa.eu/collection/semic/solution/dcat-ap |
| Italy | DCAT-AP_IT | https://www.dati.gov.it/content/dcat-ap-it-v10-profilo-italiano-dcat-ap-0 |
| Germany | DCAT-AP.de | https://www.dcat-ap.de/ |
| France | DCAT-AP_FR | https://schema.data.gouv.fr/ |
| Belgium | DCAT-AP_BE | https://www.health.belgium.be/en/dcat-ap-be |
| Netherlands | DCAT-AP_DONL | https://docs.dataportal.nl/dcat-ap-donl/ |
| UK | DCAT-AP_UK | https://guidance.data.gov.uk/publish_and_manage_data/ |
| Spain | DCAT-AP_ES | https://datos.gob.es/es/doc-developer |
| Portugal | DCAT-AP_PT | https://dados.gov.pt/ |
| Denmark | DCAT-AP_DK | https://arkitektur.digst.dk/specifikationer/registreringafdata |
| Austria | DCAT-AP_AT | https://www.data.gv.at/ |
| Switzerland | DCAT-AP_CH | https://handbook.opendata.swiss/ |

---

## Multilingual requirements

Profiles that require multilingual metadata:

| Profile | Required languages |
|---------|-------------------|
| DCAT-AP_IT | `it` + `en` recommended |
| DCAT-AP_BE | `nl` + `fr` + `de` (official languages) |
| DCAT-AP_DONL | `nl` + `en` recommended |
| DCAT-AP_FR | `fr` + `en` recommended |
| DCAT-AP_CH | `de` + `fr` + `it` + `rm` (national languages) |
| DCAT-AP_LU | `fr` + `de` + `lb` |

**Detection**:
```bash
# Check if title/notes has multilingual variants (stored as JSON string in some profiles)
jq -r '.title_translated // "Single language only"' metadata.json
```

---

## Controlled vocabulary URIs

### Licenses (SPDX / EU Publications Office)
```
CC0 1.0:       https://creativecommons.org/publicdomain/zero/1.0/
CC BY 4.0:     https://creativecommons.org/licenses/by/4.0/
CC BY-SA 4.0:  https://creativecommons.org/licenses/by-sa/4.0/
ODbL:          https://opendatacommons.org/licenses/odbl/1.0/
```

### Frequencies (MDR)
Base URI: `http://publications.europa.eu/resource/authority/frequency/`
Common values: `ANNUAL`, `MONTHLY`, `WEEKLY`, `DAILY`, `QUARTERLY`, `BIENNIAL`,
`TRIENNIAL`, `IRREGULAR`, `UNKNOWN`, `UPDATE_CONT`, `OTHER`

### Themes (EuroVoc DCAT-AP)
Base URI: `http://publications.europa.eu/resource/authority/data-theme/`
Values: `AGRI`, `ECON`, `EDUC`, `ENER`, `ENVI`, `GOVE`, `HEAL`, `INTR`,
`JUST`, `REGI`, `SOCI`, `TECH`, `TRAN`

### Languages (MDR)
Base URI: `http://publications.europa.eu/resource/authority/language/`
Common values: `ITA`, `ENG`, `DEU`, `FRA`, `NLD`, `SPA`, `POR`, `POL`

### File formats (MDR)
Base URI: `http://publications.europa.eu/resource/authority/file-type/`
Common values: `CSV`, `JSON`, `XML`, `GEOJSON`, `SHP`, `XLSX`, `PDF`, `RDF_XML`
