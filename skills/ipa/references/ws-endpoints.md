# IPA Web Services — Riferimento Endpoint

Base URL: `https://www.indicepa.gov.it`
Metodo: POST, `--data-urlencode` per tutti i parametri
AUTH_ID: sempre obbligatorio (da `${IPA_auth_id}` dopo `source ~/.zshrc`)

---

## WS16 — Cerca ente per nome/acronimo

**Quando:** l'utente conosce il nome ma non il codice IPA.

```bash
curl -s -X POST "https://www.indicepa.gov.it/ws/WS16DESAMMServices/api/WS16_DES_AMM" \
  --data-urlencode "AUTH_ID=${IPA_auth_id}" \
  --data-urlencode "DESCR=<stringa>"
```

**Risposta:** `[{ cod_amm, acronimo, des_amm }]`

---

## WS05 — Dati anagrafici completi di un ente

**Quando:** hai `cod_amm` e vuoi sede, CF, email, sito, responsabile.

```bash
curl -s -X POST "https://www.indicepa.gov.it/ws/WS05AMMServices/api/WS05_AMM" \
  --data-urlencode "AUTH_ID=${IPA_auth_id}" \
  --data-urlencode "COD_AMM=<cod_amm>"
```

**Risposta:** `{ cod_amm, des_amm, acronimo, regione, provincia, comune, cap, indirizzo, cf, sito_istituzionale, mail1..mail5, tipologia, categoria, data_accreditamento }`

---

## WS20 — Lista PEC di un ente

**Quando:** vuoi gli indirizzi PEC ufficiali di un ente.

```bash
curl -s -X POST "https://www.indicepa.gov.it/ws/WS20PECServices/api/WS20_PEC" \
  --data-urlencode "AUTH_ID=${IPA_auth_id}" \
  --data-urlencode "COD_AMM=<cod_amm>"
```

**Risposta:** `[{ pec, tipo, denominazione, comune, ... }]`
`tipo` può essere `"Pec"` o `"Sercq"` (servizio elettronico recapito certificato qualificato).

---

## WS03 — Unità Organizzative di un ente

**Quando:** vuoi l'elenco degli uffici interni con contatti.

```bash
curl -s -X POST "https://www.indicepa.gov.it/ws/WS03OUServices/api/WS03_OU" \
  --data-urlencode "AUTH_ID=${IPA_auth_id}" \
  --data-urlencode "COD_AMM=<cod_amm>"
```

**Risposta:** `[{ cod_uni_ou, des_ou, comune, indirizzo, tel, mail1..mail3, nome_resp, cogn_resp }]`

---

## WS01 — Uffici per fatturazione elettronica (da CF)

**Quando:** il cittadino deve emettere fattura elettronica e ha solo il CF dell'ente.
Il `cod_uni_ou` restituito è il **codice destinatario** (campo "Codice Ufficio" in FatturaPA).

```bash
curl -s -X POST "https://www.indicepa.gov.it/ws/WS01SFECFServices/api/WS01_SFE_CF" \
  --data-urlencode "AUTH_ID=${IPA_auth_id}" \
  --data-urlencode "CF=<codice_fiscale>"
```

**Risposta:** `[{ cod_amm, des_amm, OU: [{ des_ou, cod_uni_ou, stato_canale }] }]`
`stato_canale: "A"` = canale attivo.

---

## WS04 — Uffici con fatturazione elettronica (da codice IPA)

**Quando:** hai il `cod_amm` e vuoi sapere quali UO ricevono fatture elettroniche.

```bash
curl -s -X POST "https://www.indicepa.gov.it/ws/WS04SFEServices/api/WS04_SFE" \
  --data-urlencode "AUTH_ID=${IPA_auth_id}" \
  --data-urlencode "COD_AMM=<cod_amm>"
```

**Risposta:** lista UO con SFE attivo — stessa struttura di WS01.

---

## WS06 — Dettagli di un ufficio specifico (da cod_uni_ou)

**Quando:** hai il codice univoco a 6 caratteri di un ufficio.

```bash
curl -s -X POST "https://www.indicepa.gov.it/ws/WS06OUCODUNIServices/api/WS06_OU_COD_UNI" \
  --data-urlencode "AUTH_ID=${IPA_auth_id}" \
  --data-urlencode "COD_UNI_OU=<cod_uni_ou>"
```

**Risposta:** dati completi UO inclusi SFE (`cf`, `stato_canale`) e NSO (`cf_nso`, `stato_canale_nso`).

---

## WS07 — A quale ente appartiene un indirizzo email?

**Quando:** vuoi verificare se un'email è ufficialmente registrata in IPA.

```bash
curl -s -X POST "https://www.indicepa.gov.it/ws/WS07EMAILServices/api/WS07_EMAIL" \
  --data-urlencode "AUTH_ID=${IPA_auth_id}" \
  --data-urlencode "EMAIL=<indirizzo_email>"
```

**Risposta:** `[{ tipo_email, tipo_entita (AMM/AOO/UO), cod_amm, des_amm, cod_entita }]`

---

## WS23 — Domicilio digitale da codice fiscale

**Quando:** hai il CF dell'ente (non il codice IPA) e vuoi il suo domicilio digitale.

```bash
curl -s -X POST "https://www.indicepa.gov.it/ws/WS23DOMDIGCFServices/api/WS23_DOM_DIG_CF" \
  --data-urlencode "AUTH_ID=${IPA_auth_id}" \
  --data-urlencode "CF=<codice_fiscale>"
```

**Risposta:** `[{ domicilio_digitale, tipo, cod_amm, des_amm }]`

---

## Codici errore comuni

| Codice | Significato |
|---|---|
| 0 | Nessun errore |
| 21-23 | Problema con COD_AMM (mancante/errato/non trovato) |
| 1-3 | Problema con CF |
| 10-12 | Problema con EMAIL |
| 900-902 | AUTH_ID mancante/vuoto/errato → ri-esegui `source ~/.zshrc` |
