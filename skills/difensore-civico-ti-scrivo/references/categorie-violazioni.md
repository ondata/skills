# Violation categories — Difensore Civico per il Digitale

Use this file during Step 2 to identify the applicable category, and during Step 3 to pull
legal arguments and adaptable Italian language into the complaint.

Categories are not mutually exclusive — a single case can combine several.

---

## Category A — Dati non in formato aperto / non machine-readable

**When:** Data exists and is published (website, interactive map, HTML table, PDF report)
but is not available in an open, machine-readable format (CSV, JSON, XML, etc.).

**Additional questions to ask the user:**
- Is the data available in any downloadable format? Which?
- Is the data behind a login wall (SPID, CIE, registration)?
- Is there an official catalog entry (e.g. on dati.gov.it)?

**Articles to cite:** D.Lgs. 36/2006 art. 6 co. 1, 4; LG-OD REQUISITO 2; CAD art. 50 co. 1;
Direttiva (UE) 2019/1024.

**Adaptable legal language (Italian):**

```
[ENTE] rende disponibili i dati relativi a [DESCRIZIONE] unicamente in formato
[HTML/PDF/mappa interattiva], privo di leggibilità meccanica. Tale modalità di pubblicazione
contrasta con:

- l'art. 6, comma 1, del D.Lgs. 36/2006, che impone la messa a disposizione dei documenti
  in formato aperto e leggibile meccanicamente;
- il comma 4 del medesimo articolo, che sancisce il principio dell'apertura fin dalla
  progettazione e per impostazione predefinita;
- il REQUISITO 2 delle Linee guida AgID in materia di apertura dei dati (LG-OD), che impone
  che i dati siano resi disponibili in formato aperto e leggibile meccanicamente ad almeno
  3 stelle (file strutturato in formato aperto, es. CSV, JSON, XML);
- l'art. 50, comma 1, del CAD, che richiede che i dati siano resi disponibili in modo da
  consentirne la fruizione e il riutilizzo.

La pubblicazione in formato [FORMATO ATTUALE] non consente l'estrazione e il riutilizzo
automatico dei dati, rendendo di fatto impossibile qualsiasi analisi, visualizzazione o
elaborazione sistematica.
```

**Remedy to request:** "pubblichi i dati relativi a [DATASET] in formato aperto e leggibile
meccanicamente (es. CSV, JSON), con metadati descrittivi e licenza aperta, e li cataloghi
nel catalogo nazionale dei dati aperti."

---

## Category B — Barriere tecniche all'accesso automatizzato

**When:** Data is nominally available but access is blocked by: mandatory CAPTCHA on
download, compulsory SPID/CIE authentication to access open data, non-functional APIs
(declared but returning errors), or unstable URLs not exposed in the catalog.

**Additional questions to ask the user:**
- What exactly blocks the download? (CAPTCHA / login / API error message?)
- Can you share the exact error message or URL?
- Are the API documented? Where?

**Articles to cite:** D.Lgs. 36/2006 art. 6 co. 1, 4, 5; LG-OD REQUISITO 1, 2;
Direttiva (UE) 2019/1024.

**Adaptable legal language (Italian):**

```
Il portale [URL] dichiara di rendere disponibili i dati in formato aperto, ma introduce
le seguenti barriere tecniche che rendono impossibile qualsiasi accesso automatizzato:

[DESCRIBE SPECIFIC BARRIER: CAPTCHA obbligatorio su ogni download / autenticazione SPID
obbligatoria / API che restituiscono sistematicamente errore [MESSAGGIO] / URL non
documentati e non esposti nel catalogo]

Ciò contrasta con:

- l'art. 6, comma 1, del D.Lgs. 36/2006, che impone la disponibilità dei dati in formato
  leggibile meccanicamente — standard che implica l'accessibilità senza barriere manuali;
- l'art. 6, comma 5, del medesimo decreto, che impone la disponibilità dei dati dinamici
  tramite "API adeguate" — che tali non sono se restituiscono errore o richiedono
  autenticazione per accedere a dati aperti;
- il REQUISITO 1 delle LG-OD, che impone la disponibilità dei dati "per il riutilizzo a
  fini commerciali e non commerciali" senza restrizioni indebite;
- la Direttiva (UE) 2019/1024, che afferma che le condizioni di accesso "non riducono
  indebitamente le possibilità di riutilizzo".
```

**Remedy to request:** "rimuova le barriere tecniche che impediscono l'accesso automatizzato
ai dati (es. elimini il CAPTCHA dai download / renda le API funzionanti e documentate /
pubblichi URL stabili nel catalogo) e garantisca l'accesso senza autenticazione ai dati
di natura aperta."

---

## Category C — Portale o servizio non funzionante / obsoleto

**When:** A PA's website or digital service is significantly degraded: persistent downtime,
broken search functions, missing HTTPS, severely outdated software, or features declared
available that are actually inaccessible.

**Additional questions to ask the user:**
- Which specific functions are broken? Since when?
- Is the issue documented anywhere (no notice on the site)?
- HTTP or HTTPS? What browser warning appears?

**Articles to cite:** CAD art. 7 co. 1 (qualità servizi online); Linee guida di design AgID
(TLS/HTTPS obbligatorio); CAD art. 17 co. 1-quater.

**Adaptable legal language (Italian):**

```
Il sito [URL], di competenza di [ENTE], presenta le seguenti criticità persistenti che
compromettono la consultabilità e l'usabilità del servizio:

[DESCRIBE: ricerca non funzionante / servizio non raggiungibile / assenza HTTPS /
sistema obsoleto senza aggiornamenti da anni]

In particolare:
- [CRITICITÀ 1 con evidenza tecnica e data di rilevazione]
- [CRITICITÀ 2 con evidenza tecnica e data di rilevazione]

Ciò contrasta con:

- l'art. 7 del CAD, che impone che i soggetti pubblici rendano disponibili on-line i propri
  servizi nel rispetto degli standard e dei livelli di qualità individuati da AgID;
[IF HTTP:] - le Linee guida AgID sulla sicurezza (TLS e cipher suite) e le Linee guida di
  design per i siti web della PA, che rendono obbligatorio l'uso del protocollo HTTPS;
- il principio di reperibilità e qualità dei servizi digitali.

L'impatto concreto è il seguente: [DESCRIBE IMPACT on citizens, professionals, businesses].
```

**Remedy to request:** "ripristini il corretto funzionamento del servizio [SPECIFICO] e
adegui il sito agli standard di sicurezza e qualità previsti dalle Linee guida AgID,
in particolare [HTTPS / ricerca funzionante / aggiornamento sistema]."

---

## Category D — Licenza inadeguata / violazione "open by default"

**When:** Data or content published by a PA carries: a restrictive copyright notice that
limits reuse; no license at all (different from the "open by default" presumption); a license
that explicitly prohibits commercial use or redistribution; or conditions contradicting D.Lgs.
36/2006.

**Additional questions to ask the user:**
- Where exactly are the restrictive clauses? (URL of the legal notice / license page)
- What does the clause say? (exact quote if possible)
- Is there a specific dataset or all content on the site?

**Articles to cite:** CAD art. 52 co. 2 (open by default); D.Lgs. 36/2006 art. 6 co. 4;
LG-OD REQUISITO 1.

**Adaptable legal language (Italian):**

```
Le note legali / la licenza pubblicata da [ENTE] alla pagina [URL] contengono le seguenti
disposizioni restrittive:

"[CITAZIONE ESATTA DELLA CLAUSOLA RESTRITTIVA]"

Tali condizioni contrastano con:

- l'art. 52, comma 2, del CAD, secondo cui i dati e i documenti pubblicati dalle
  pubbliche amministrazioni "senza l'espressa adozione di una licenza [...] si intendono
  rilasciati come dati di tipo aperto" — principio noto come "open by default";
- l'art. 6, comma 4, del D.Lgs. 36/2006, che sancisce il principio dell'apertura fin
  dalla progettazione e per impostazione predefinita;
- il REQUISITO 1 delle LG-OD, che impone la disponibilità dei dati per il riutilizzo
  "a fini commerciali e non commerciali".

Le restrizioni adottate non appaiono motivate da specifiche eccezioni previste dalla
normativa vigente, né è indicata alcuna giustificazione puntuale per l'adozione di
condizioni più restrittive rispetto allo standard "open by default".
```

**Remedy to request:** "adegui le note legali / la licenza pubblicata sul sito alla normativa
vigente in materia di open data, adottando una licenza aperta conforme (es. CC0, CC BY 4.0,
IODL 2.0) e rimuovendo le restrizioni non motivate al riutilizzo dei contenuti istituzionali."

---

## Category E — Silenzio su richiesta di riutilizzo (art. 5 D.Lgs. 36/2006)

**When:** The user sent a formal data-reuse request to a PA under art. 5 D.Lgs. 36/2006,
the 30-day deadline has expired (+ any communicated extension), and the PA has not responded,
not provided the data, and not issued a motivated refusal.

**Additional questions to ask the user:**
- Exact date the request was sent. Via PEC? Which address?
- Do you have the PEC delivery receipts (accettazione + consegna)?
- Did the PA acknowledge receipt or request an extension?
- Was a previous DCD complaint already filed about this?

**Articles to cite:** D.Lgs. 36/2006 art. 5 co. 1, 3; CAD art. 17 co. 1-quater.

**Adaptable legal language (Italian):**

```
In data [DATA], il/la segnalante ha presentato formale richiesta di riutilizzo dei dati
ai sensi dell'art. 5 del D.Lgs. 36/2006 all'indirizzo [PEC/EMAIL DI DESTINAZIONE], chiedendo
[OGGETTO DELLA RICHIESTA].

Decorso il termine di trenta giorni previsto dall'art. 5, comma 1, del D.Lgs. 36/2006
(scadenza: [DATA SCADENZA]), [ENTE] non ha:
- reso disponibili i dati richiesti;
- comunicato alcuna proroga entro i ventuno giorni previsti dal medesimo articolo;
- adottato un provvedimento espresso di diniego motivato ai sensi del comma 3.

Si configura pertanto un silenzio-inadempimento in violazione dell'art. 5, comma 1, del
D.Lgs. 36/2006, nonché la mancata adozione del provvedimento motivato prescritto dal
comma 3 in caso di diniego.

[IF APPLICABLE: Si segnala inoltre che analogo comportamento era già stato portato
all'attenzione del Difensore Civico per il Digitale in data [DATA PRECEDENTE SEGNALAZIONE],
protocollo [N.], senza che [ENTE] abbia posto rimedio alla situazione.]
```

**Remedy to request:** "solleciti [ENTE] a concludere il procedimento avviato con la richiesta
del [DATA], rendendo disponibili i dati richiesti in formato aperto con licenza aperta,
ovvero adottando un provvedimento espresso e motivato di diniego con indicazione dei mezzi
di tutela, ai sensi dell'art. 5, commi 1 e 3, del D.Lgs. 36/2006."

---

## Category F — Sollecito: mancata azione su precedente segnalazione al DCD

**When:** The user has already filed a DCD complaint (Funzione A) and either: the DCD did
not respond within 90 days, or the DCD transmitted the complaint to AGID but the PA has
not remedied the violation.

**Additional questions to ask the user:**
- Date of the previous segnalazione. Protocol number assigned by AGID?
- Did you receive any response from the DCD?
- Is the PA's conduct still the same as described in the original complaint?

**Articles to cite:** CAD art. 17 co. 1-quater; Regolamento DCD art. 8; CAD art. 18-bis.

**Adaptable legal language (Italian):**

```
In data [DATA PRIMA SEGNALAZIONE], il/la segnalante aveva già presentato a codesto Ufficio
segnalazione relativa alle medesime violazioni da parte di [ENTE], regolarmente protocollata
con n. [NUMERO DI PROTOCOLLO / "e ricevuta di protocollo"].

A distanza di [N MESI] dalla prima segnalazione, [ENTE] non ha posto alcun rimedio alla
violazione originariamente segnalata. [DESCRIVI LA SITUAZIONE ATTUALE: i dati continuano ad
essere pubblicati con le medesime criticità / il portale è ancora non funzionante / ecc.]

[IF DCD DID NOT RESPOND:] Inoltre, codesto Ufficio non ha comunicato al segnalante l'avvio
del procedimento né l'eventuale archiviazione della prima segnalazione, ai sensi dell'art. 8
del Regolamento (D.T. n. 270/2022).

Con la presente si sollecita pertanto un intervento più incisivo ai sensi dell'art. 18-bis
del CAD, inclusa l'eventuale applicazione delle sanzioni ivi previste in caso di persistente
inadempienza da parte di [ENTE].
```

**Remedy to request:** "accerti lo stato della precedente segnalazione (prot. [N.]) e, ove
[ENTE] non abbia ancora ottemperato, eserciti i poteri di cui all'art. 18-bis del CAD,
compresi, se del caso, i poteri sanzionatori ivi previsti."

---

## Category G — Mancata pubblicazione di dataset ad alto valore (HVD)

**When:** A PA responsible for one or more High Value Dataset (HVD) categories defined in
Reg. (UE) 2023/138 has not published the required datasets — i.e., the datasets are entirely
absent from the national open data catalog (dati.gov.it) and not accessible via API, past
the 9 June 2024 deadline.

Distinct from Category A (wrong format) and Category B (access barriers): here the data
does not exist at all in the catalog.

**Additional questions to ask the user:**
- Which HVD category is affected? (geospaziale / osservazione della terra e ambiente /
  meteorologica / statistica / imprese e proprietà societaria / mobilità)
- Which specific PA is responsible? Note: multiple PAs may hold obligations per category.
  For "imprese": Camere di Commercio / Unioncamere; for "mobilità": MIT + Regioni.
  Draft one *segnalazione* per PA.
- Have you verified on dati.gov.it filtering by the `hvd_category` field? What result?
- Have you cross-checked on data.europa.eu for Italian datasets in this category?

**Articles to cite:** Reg. (UE) 2023/138 artt. 3 par. 1 e 4 parr. 2–3; D.Lgs. 36/2006 artt.
12-bis co. 1, 9 co. 2 e 12 ult. co.

**Adaptable legal language (Italian):**

```
[ENTE] non ha reso disponibile alcuna serie di dati rientrante nella categoria
"[CATEGORIA HVD]" prevista dall'allegato del Regolamento di esecuzione (UE) 2023/138 della
Commissione, del 21 dicembre 2022, né sul catalogo nazionale dei dati aperti (dati.gov.it)
né tramite API accessibili pubblicamente.

Tale inadempienza perdura da oltre [N MESI] rispetto alla scadenza del 9 giugno 2024, data
dalla quale il Regolamento è applicabile ai sensi del suo articolo 6 (pubblicato in GUUE
L 19/43 del 20 gennaio 2023, entrato in vigore il 9 febbraio 2023, applicabile dal 9 giugno
2024). L'assenza è stata verificata direttamente su dati.gov.it tramite filtro sul campo
hvd_category e confermata su data.europa.eu.

Ciò contrasta con:

- l'art. 3, paragrafo 1, del Reg. (UE) 2023/138, che impone agli enti pubblici che
  detengono serie di dati di elevato valore di garantirne la messa a disposizione "in
  formati leggibili meccanicamente tramite API corrispondenti alle ragionevoli esigenze dei
  riutilizzatori";
- l'art. 4, paragrafo 2, del medesimo Regolamento, che estende l'obbligo alle serie di
  dati esistenti create prima della data di applicazione;
- l'art. 4, paragrafo 3, del medesimo Regolamento, che impone licenza CC0 o CC BY 4.0;
- l'art. 12-bis, comma 1, del D.Lgs. 24 gennaio 2006, n. 36, che recepisce
  nell'ordinamento nazionale tali obblighi, disponendo che le serie di dati di elevato
  valore siano rese disponibili gratuitamente, leggibili meccanicamente, fornite mediante
  API e come download in blocco;
- l'art. 9, comma 2, del medesimo D.Lgs. 36/2006, che impone l'utilizzo del catalogo
  nazionale dei dati aperti gestito da AgID (dati.gov.it) come "punto di accesso unico alle
  serie di dati";
- l'art. 12, ultimo comma, del D.Lgs. 36/2006, che prevede esplicitamente il ricorso
  al difensore civico per il digitale in caso di violazione delle disposizioni del decreto.

Il Regolamento (UE) 2023/138 è direttamente applicabile negli Stati membri ai sensi
dell'art. 288, secondo comma, del TFUE, senza necessità di recepimento nazionale.
[ENTE] rientra nell'ambito soggettivo di applicazione ai sensi [dell'art. 1, comma 2, del
D.Lgs. 36/2006 / dell'art. 2, comma 2, del CAD — eliminare la variante non applicabile].
```

**Remedy to request:** "pubblichi le serie di dati ad alto valore della categoria
"[CATEGORIA HVD]" in formati leggibili meccanicamente tramite API pubblica con licenza CC0
o CC BY 4.0, le renda disponibili come download in blocco ove applicabile, e le cataloghi
su dati.gov.it con il campo hvd_category valorizzato, nel rispetto del Reg. (UE) 2023/138
e dell'art. 12-bis del D.Lgs. 36/2006."
