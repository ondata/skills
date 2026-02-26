# DCAT-AP_IT Field Reference

Full list of dataset and distribution fields, with cardinality (M=mandatory, R=recommended, O=optional)
and controlled vocabulary references.

---

## Dataset (`dcat:Dataset`) Fields

| Field | DCAT-AP_IT | Cardinality | Notes |
|-------|-----------|-------------|-------|
| Title | `dct:title` | M | Multilingual (it, en). Must be meaningful, not just "dataset" |
| Description | `dct:description` | M | Multilingual. Min 100 chars recommended |
| Publisher | `dct:publisher` | M | URI from IPA registry preferred |
| Issued | `dct:issued` | R | ISO 8601 date. Common issue: empty string "" |
| Modified | `dct:modified` | R | ISO 8601 date. Common issue: DD-MM-YYYY format |
| Theme | `dcat:theme` | M | From EuroVoc or SKOS themes |
| Identifier | `dct:identifier` | M | Unique. Pattern: `ISTAT_CODE:slug` e.g. `c_a638:protocolli-2024` |
| Language | `dct:language` | R | URI: `http://publications.europa.eu/resource/authority/language/ITA` |
| License | `dct:license` | R | URI from controlled vocabulary (see below) |
| Spatial coverage | `dct:spatial` | R | GeoNames URI preferred |
| Temporal coverage | `dct:temporal` | R | `dcat:startDate` + `dcat:endDate` in ISO 8601 |
| Update frequency | `dct:accrualPeriodicity` | R | From MDR frequency vocabulary |
| Contact point | `dcat:contactPoint` | R | `vcard:hasEmail` |
| Holder | `dct:rightsHolder` | M (IT) | Specific to Italian profile |
| Creator | `dct:creator` | O | Specific to Italian profile |
| Conforms to | `dct:conformsTo` | O | Schema/standard reference |
| Geographical name | `dcatapit:geographicalName` | O | |
| Tags | `dcat:keyword` | R | Min 3 recommended; multilingual preferred |

---

## Distribution (`dcat:Distribution`) Fields

| Field | DCAT-AP_IT | Cardinality | Notes |
|-------|-----------|-------------|-------|
| Access URL | `dcat:accessURL` | M | Resolvable URI |
| Download URL | `dcat:downloadURL` | R | Direct file link preferred over landing page |
| Format | `dct:format` | R | From MDR file format vocabulary |
| Media type | `dcat:mediaType` | R | IANA type e.g. `text/csv` |
| License | `dct:license` | M (IT) | **Must be on each distribution**, not just dataset |
| Description | `dct:description` | R | What does this specific file contain? |
| Issued | `dct:issued` | R | |
| Modified | `dct:modified` | R | |
| Byte size | `dcat:byteSize` | R | Common issue: `0` or missing |
| Checksum | `spdx:checksum` | O | |
| Encoding | `cnt:characterEncoding` | R (IT) | Should be `UTF-8` |
| Status | `adms:status` | O | |

---

## Common License URIs (Italian PA)

| License | URI |
|---------|-----|
| CC BY 4.0 | `https://w3id.org/italia/controlled-vocabulary/licences/A21_CCBY40` |
| CC BY-SA 4.0 | `https://w3id.org/italia/controlled-vocabulary/licences/A29_CCBYSA40` |
| CC0 1.0 | `https://w3id.org/italia/controlled-vocabulary/licences/A11_CCO10` |
| IODL 2.0 | `https://w3id.org/italia/controlled-vocabulary/licences/B19_IODL20` |

---

## Update Frequency Values

From MDR: `http://publications.europa.eu/resource/authority/frequency/`

Common values: `ANNUAL`, `MONTHLY`, `WEEKLY`, `DAILY`, `QUARTERLY`, `BIENNIAL`, `IRREGULAR`, `UNKNOWN`

---

## Theme Values

From EuroVoc themes used in Italian PA:

| Code | Theme |
|------|-------|
| `AGRI` | Agriculture |
| `ECON` | Economy and finance |
| `EDUC` | Education |
| `ENER` | Energy |
| `ENVI` | Environment |
| `GOVE` | Government and public sector |
| `HEAL` | Health |
| `JUST` | Justice |
| `REGI` | Regions and cities |
| `SOCI` | Population and society |
| `TECH` | Science and technology |
| `TRAN` | Transport |

---

## Validation Checklist for Italian PA

Use this to self-evaluate DCAT-AP_IT compliance:

**Mandatory (must fix)**:
- [ ] Title in Italian (and English if possible)
- [ ] Description in Italian (>100 chars)
- [ ] Publisher with URI from IPA
- [ ] Identifier in format `ISTAT_CODE:slug`
- [ ] Theme from EuroVoc
- [ ] At least one Distribution
- [ ] License on each Distribution (not just on dataset)
- [ ] Holder (`dct:rightsHolder`) declared
- [ ] Access URL resolvable (HTTP 200)

**Recommended (should fix)**:
- [ ] Issued date in ISO 8601
- [ ] Modified date in ISO 8601
- [ ] Language declared
- [ ] At least 3 tags
- [ ] Spatial coverage (GeoNames URI)
- [ ] Temporal coverage with start/end
- [ ] Update frequency declared
- [ ] Contact point with email
- [ ] Download URL pointing to direct file
- [ ] Byte size > 0
- [ ] Encoding declared as UTF-8
- [ ] Format and MIME type declared
