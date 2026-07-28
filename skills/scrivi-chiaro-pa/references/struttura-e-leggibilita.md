# Structure, usability, findability, accessibility

How to structure content, write UI microcopy, make text findable by search engines, and keep it accessible and inclusive. Examples in Italian (✅ = use, ❌ = avoid).

## Structuring content

### Paragraphs

Split content into short paragraphs so the reader finds information fast. Assume mobile reading.

### Lists

- Bullet lists make text more readable. Items must be consistent with the intro sentence, short and clear, correctly aligned (punctuation rules: see `stile-di-scrittura.md`).
- Numbered lists guide the reader through a process, one action per step, no intro sentence needed. Link any documents needed to complete the step.
- Avoid nested sub-lists: start a new list instead.

### Links

- Make the destination or purpose of every link clear from its text: ✅ *Leggi la scheda di sintesi Rapporto sull'attuazione del Servizio Civile: anno 2017* ❌ *Leggi qui la scheda…*. Never "clicca qui".
- Only link genuinely relevant content — too many links blur the text.
- Open links in the same tab, with few exceptions (e.g. another site).

### Navigation menus and labels

Write labels from the user's point of view: simple, common, immediately understandable terms. Keep one syntactic approach — do not mix verb-based (*"Scarica il documento"*), noun-based (*"Documenti scaricabili"*) and questions. ✅ *Servizi per le imprese* ❌ *Imprese*. Labels drive the user's mental model of the site: keep tone, granularity, and style consistent.

### Notes

On a web page, use footnotes only for normative references. For further reading, bibliographies, or technical documents, use lists with links instead.

### FAQ

Do not create FAQ sections that duplicate content. If a question is frequent, fix the page that should answer it.

### Contact details

- **Email**: lowercase, no hyphens or spaces, always an active `mailto:` link.
- **Phone numbers**: always alongside other contact channels; include the international prefix and group digits with spaces (*+39 06 123 456 78*); make them active `tel:` links.

### Attached documents and PDFs

Write content as web pages, not attachments. If an attachment is unavoidable (e.g. some norms): clear and accessible text, correct heading hierarchy and metadata, no blank pages or filler images, a description of the document on the page before the link, and the link must state file type and size.

### Data

Prefer visual presentation (charts, maps) over big tables; tables have mobile and readability limits. When tables are needed: little text per cell, few columns.

## Usability and microcopy

### Buttons

Clear, specific calls to action: ✅ *"Cerca"*, *"Paga adesso"*, *"Scarica il modulo"*, *"Iscriviti adesso"* ❌ *"Ok"*, *"Invia"*. Mind the difference between *"Cancella"* and *"Annulla"*. Button text must state the action performed: ✅ *Conferma i tuoi dati* ❌ *Clicca qui*.

### Confirmation messages

Always confirm the outcome of a user action with text. If a further action follows, explain its consequence:

- ✅ *Premendo "Conferma" invierai la tua richiesta e non potrai più modificare i dati* → [Conferma] [Annulla]
- ❌ *Confermi?* → [Invia] [Annulla]

### Error messages

Say exactly what is missing or wrong and how to fix it: ✅ *Inserisci un numero di telefono valido. Tutti i campi con l'asterisco (\*) sono obbligatori* ❌ *Errore*.

### Form microcopy

Add short instruction or example texts to form fields, so the user knows what information is expected and how to use the interface.

### Empty pages

Never leave dead ends (e.g. empty search results). Offer a way forward: ✅ *La ricerca di "[parole chiave]" non ha prodotto nessun risultato. Torna alla pagina precedente per una nuova ricerca, oppure vai alla pagina contatti.* ❌ *Not found*.

## Writing for search engines

- **Titles**: max 65 characters, clear and descriptive, search-friendly, no special characters, no trailing full stop, normal capitalization rules, no acronyms. ✅ *Riduci, riusa, ricicla: come gestire i rifiuti a Venezia* ❌ *Io riduco, riuso, riciclo*.
- **Summaries** (page description): on every page, max 150 characters, ends with a full stop, does not repeat title or body, clear and specific.
- **Keywords**: build a list of the terms that define the site's topics, drop synonyms, prefer the simplest terms (check Google Trends); use the list for menus and tags.
- **Captions**: every image gets a short caption (max two lines), with author and license when needed.
- **Migrations**: when content moves, set redirects to preserve indexing and not lose users arriving from search engines.

## Accessibility and inclusion

- **Contrast and font size**: check text/background contrast and avoid small type.
- **Captcha**: never based only on images, audio, or color distinction.
- **Alt text**: describe image/video content in the `alt` attribute — short, pertinent, specific, coherent with the text's keywords. Essential for accessibility.
- **Interface never relies on color/image/audio alone**: buttons combine shape, color, and text.
- **Content usable by everyone**: including people with motor, speech, sight, or age-related difficulties. Offer multiple contact channels (phone with prefix as a link, email as a link, address).
- **Disability**: say *"persone con disabilità"*; avoid *"diversamente abile"*, *"disabile"*, *"handicappato"*, *"persone che soffrono di una disabilità"*.
- **Feminine forms**: decline titles when the office holder is a woman — *la ministra*, *la sindaca*, *l'architetta*, *la giudice*, *l'ambasciatrice*; invariant terms stay (*la presidente*, *la dirigente*).
- **Cultural identity**: use precise terms (richiedenti asilo, rifugiati, migranti irregolari); no generalizations by origin, ethnicity, religion, culture. ✅ *Nella notte sono sbarcate circa 30 persone.* ❌ *Nella notte sono sbarcati circa 30 clandestini.*
- **Inclusive language**: people-first, no stereotypes; when giving examples, do not default to one gender (❌ *Il presidente di Acme, Mario Rossi…*).
- **Jargon**: technical terms only if the audience surely understands them; otherwise use synonyms or explain briefly.
- **Translations**: consider translations for critical content (health care, residence permits, emergencies — at least English). Machine translation is acceptable if verified, declared, and understandable; translate tags and metadata too.
