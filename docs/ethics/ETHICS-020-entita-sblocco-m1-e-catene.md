# ETHICS-020 — Entità-sblocco M1 (8 nuove + 1 rename) e completamento catene

**Data**: 2026-07-04
**Versione**: v6.99.120
**Stato**: implementato
**Origine**: coda M1 da ETHICS-017 (B1c) + follow-up ETHICS-019 (Repubblica Khmer)
**Metodo**: workflow di ricerca multi-agente (1 ricercatore + 1 fact-checker
avversariale per entità, fonti verificate via web; log in
`data/enrichment/m1_unlock_research_20260704.json`) + cross-check ChatGPT
gpt-5.5 sulle 8 decisioni di incatenamento (log in `data/chatgpt_review/20260704/`).
**Generatore dual-write**: `scripts/apply_m1_unlock.py` →
`data/entities/batch_37_m1_unlock.json`, `data/chains/batch_37_m1_unlock.json`,
chirurgia su batch_20/35/36, `scripts/sql_m1_unlock_entities.sql`.

---

## Scoperta in corso d'opera: 3 delle 11 entità pianificate ESISTEVANO GIÀ

Le guardie SQL e la ricognizione per varianti hanno rivelato che l'handoff
(e le note di ETHICS-017 stesse) erano sbagliati su tre entità "mancanti":

- **Lan Xang esisteva già come #128** — ma con `name_original` in **script
  thai** `ล้านช้าง` e `lang='lo'` (mismatch script-lingua, mai flaggato perché
  il detector non era ancora in uso su quel batch). Risolto QUI con il rename
  nativo `ล้านช้าง → ອານາຈັກລ້ານຊ້າງ` (forma lao attestata, = label Wikidata
  Q853477), pattern Wadai/ETHICS-001: la forma thai resta come variante con
  contesto esplicito. Le catene 123/124/125 sono incatenate a #128.
- **Lo Stato Mahdista esisteva già come #736** (`الدولة المهدية`, 1885-1898) —
  è uno dei **rename nativi prod-only** (JSON-land: `Dawla al-Mahdiyya`,
  batch_24): la coda M4 dei 17 rename è quindi la fonte di verità, non
  l'elenco ETHICS-017. La catena Taqali→Mahdiyya usa #736.
- **Medri Bahri esisteva già come #658** (`ምድረ ባሕሪ`, 1137-1879, QID
  Q3699102) — idem, JSON-land `Medri Bahri` (batch_21). ETHICS-018 ne
  chiedeva la creazione: la premessa era errata (la variante era stata
  rimossa da Aksum, ma l'entità propria esisteva). NIENTE creato.

**Lezione (per le prossime sessioni)**: prima di creare un'entità "mancante",
cercarla su prod anche per **variante** e per **script alternativi**, non solo
per name_original esatto. La ricerca completa delle 3 entità (fonti, varianti,
note etiche più ricche di quelle presenti su prod) resta committata in
`data/enrichment/m1_unlock_research_20260704.json` come materiale di
enrichment per la coda M4.

## Le 8 entità nuove

| Entità | Anni | Verdetto fact-checker | Note etiche salienti |
|---|---|---|---|
| កម្ពុជា (Longvek-Oudong) | 1431-1863 | CONFIRM | disambiguatore nel nome (ព្រះរាជាណាចក្រកម្ពុជា è già di #256); sacchi di Angkor 1431 e Longvek 1594; perdita Kampuchea Krom; Tran Tay 1834-41; protettorato 1863 sotto coercizione |
| សាធារណរដ្ឋខ្មែរ (Khmer Republic) | 1970-1975 | CONFIRM | colma il gap ETHICS-019 (QID Q1054184 spostato qui dal vecchio #240); bombardamenti USA (perpetratore nominato, stime contese documentate); pogrom anti-vietnamiti 1970 |
| Кнежевина Србија | 1815-1918 | CORRECT (2 fix applicati) | Serbia sia vittima sia perpetratrice: espulsioni 1862-67 e 1878 (ETHNIC_CLEANSING), guerre balcaniche (rapporto Carnegie), perdite WWI ~25%; creata su indicazione del cross-check (D2) |
| Краљевина Срба, Хрвата и Словенаца | 1918-1941 | CONFIRM | annessione contestata del Montenegro (due letture registrate); dittatura del 6 gennaio; invasione dell'Asse |
| إمارة الدرعية (Dirʿiyya) | 1744-1818 | CONFIRM | sacco di Karbala 1802, Taif 1803, distruzione al-Baqi; ri-datazione saudita 2022 al 1727 trattata come periodizzazione politicizzata |
| إمارة نجد (Najd) | 1824-1891 | CONFIRM | discriminazione degli sciiti di al-Hasa; violenza dinastica cronica esplicitata |
| सङ्घीय लोकतान्त्रिक गणतन्त्र नेपाल | 2008- | CORRECT (2 fix applicati) | guerra civile ~13-17k morti con attribuzione per perpetratore (maggioranza documentata a forze statali, INSEC); morti Terai 2015 ri-attribuite (totale complessivo, non "uccisi dalla polizia") |
| Mthwakazi (Regno Ndebele) | 1838-1893 | CONFIRM | endonimo primario; frode della Rudd Concession; Maxim guns a Shangani/Bembesi (BSAC/Rhodes nominati); stato a sua volta costruito su conquista dei Rozvi |

(Le ricerche verificate per Lan Xang [CONFIRM], Mahdiyya [CONFIRM] e Medri
Bahri [CORRECT, fix Gallabat 9-10 marzo 1889] restano valide come materiale
di enrichment per le entità esistenti #128/#736/#658 — coda M4.)

Correzioni del fact-checker applicate nel generatore (`apply_corrections`):
Nepal (attribuzione morti Terai + drop del territory_change 2015, atto
costituzionale non territoriale), Serbia (firmano 1867 = 4 fortezze; esodo
1862 ≈10.000 dalle sei città di guarnigione, ~2.100 da Belgrado).

## Decisioni di incatenamento (cross-check ChatGPT: 6 AGREE, 2 DISAGREE recepiti)

1. **Cambogia (D1, AGREE)**: #256 (1953-, senza fine) resta il contenitore
   della continuità monarchica INCLUSA l'interruzione 1970-93; Khmer Republic
   e Kampuchea Democratica restano entità separate NON incatenate in avanti
   finché manca la PRK (1979-89): una catena che terminasse sul regime del
   genocidio sarebbe fuorviante. Documentato sul chain-level note della 126.
2. **Serbia (D2, DISAGREE recepito)**: il cross-check ha bocciato il link
   diretto Ottomano→SHS (falsa continuità sopra il vuoto 1815-1918) → creata
   l'entità **Кнежевина Србија (1815-1918)** e catena 34 estesa:
   Ottoman →(DECOLONIZATION 1815, violenta)→ Србија →(UNIFICATION 1918)→
   СХС →(REVOLUTION 1945, violenta)→ СФРЈ #231.
3. **Montenegro (D3, AGREE)**: catena 130 + СХС con **ANNEXATION 1918,
   is_violent=true** (assemblea di Podgorica sotto presenza militare serba,
   Christmas Uprising 1919 represso); entrambe le letture storiografiche
   registrate, nessuna arbitrata.
4. **Nepal (D4, AGREE)**: REVOLUTION 2008 con is_violent=true riferito al
   processo rivoluzionario (guerra 1996-2006 + Jana Andolan II), con nota
   esplicita che il voto finale (560-4) fu pacifico. Marcarla non-violenta
   avrebbe cancellato la guerra che l'ha prodotta.
5. **Arabia Saudita (D5, DISAGREE recepito)**: transizione Najd→Regno 1932
   tipizzata **UNIFICATION** (stato costruito per conquista: Riyadh 1902,
   Ha'il 1921, Hejaz 1924-25 col massacro di Taif) e NON "restoration", che
   avrebbe eufemizzato; la restaurazione dinastica resta nelle note. Catena
   DYNASTY con i due interregni (1818-24, 1891-1902) documentati sui link.
6. **Khmer Empire→post-Angkor (D6, AGREE)**: SUCCESSION 1431 con
   is_violent=true — stessa polity reale ricollocata dopo il sacco
   ayutthayano (perpetratore nominato), non conquista del successore.
7. **Lan Xang (D7, AGREE)**: PARTITION 1707/1707/1713 non violenta
   (divisione negoziata dopo stallo armato) in testa alle catene 123/124/125;
   nota che Champasak si separò dalla sfera di Vientiane nel 1713.
8. **Medri Bahri (D8, AGREE)**: NESSUN link — il predecessore Aksum sarebbe
   l'anacronismo rimosso da ETHICS-018, il successore (Eritrea italiana) non
   esiste ancora nel dataset. Entità standalone con chain_notes.

## Rischi di distorsione considerati

- **Falsa continuità**: ogni gap reale (1818-24, 1891-1902, 1017-1070 per
  Sri Lanka in coda, 1421-1515 Zeta→Montenegro già documentato) è annotato
  sui link, mai colmato d'ufficio.
- **Catene come legittimazione**: la catena saudita è DYNASTY (casa Al Saud),
  non una pretesa di stato continuo; la ri-datazione ufficiale saudita del
  2022 (1727) è documentata come politicizzata, non adottata.
- **Direzione del nome**: tutti i primari sono endonimi attestati
  (Mthwakazi, non "Matabele"; الدولة المهدية, non "Dervish Empire").
- **JSON-land vs prod**: il link JSON a Taqali usa 'Taqali' (nome JSON
  corrente, rename nativo in coda M4), l'SQL usa l'id prod 411 — la
  riconciliazione del nome resta tracciata in M4, non nascosta qui.

## Follow-up espliciti

- PRK (1979-1989) + Stato di Cambogia (1989-93) → poi estensione in avanti
  della catena 126 (D1).
- Eritrea italiana (1890-1941) → poi catena per Medri Bahri (D8).
- Serbia moderna (1992-/2006-) → completamento catena 34 oltre la СФРЈ.
- Sri Lanka #142 / Kemet #26: dossier di split pronti (ricerca 2026-07-04),
  record ETHICS dedicato al momento dello split.
