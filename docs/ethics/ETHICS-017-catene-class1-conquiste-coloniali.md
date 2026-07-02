# ETHICS-017 — Catene Class-1 verso potenze coloniali/imperiali (B1c)

**Data**: 2026-07-02 · **Stato**: decisione presa + eseguita (v6.99.110).
**Correlati**: ETHICS-001 (nomi locali), ETHICS-002 (transizioni esplicite),
ETHICS-009 (categorie coloniali), ETHICS-015 (modello lineare, unificazioni),
`docs/structural-tracks-plan.md` (track B1). **Cross-check**: ChatGPT-5.5
(log in `data/chatgpt_review/20260702/`), recepito.

## Contesto

Track B1c: ~27 entità moderne orfane (query Class-1) vengono collegate in catene
successorie. La maggior parte di queste successioni **termina in una conquista
coloniale o imperiale** (britannica, francese, Qing, siamese, statunitense,
belga/leopoldiana). Ogni link è una *claim* storica: le decisioni di
rappresentazione qui sotto determinano come gli agenti AI vedranno la fine di
questi stati.

## Decisioni

### 1. La conquista si registra come link, non si omette
Lo stato conquistato viene collegato **all'entità del conquistatore** (es.
`KwaZulu → British Empire`, `Imerina → Republique francaise`) con
`transition_type=CONQUEST`, `is_violent=true` e note non eufemistiche
(guerre, deportazioni, massacri, saccheggi documentati con fonti).
Omettere il link "per pudore" nasconderebbe la conquista; è esattamente ciò
che il progetto rifiuta (verità prima del comfort).
Nota semantica: la catena documenta la *successione del potere sulla regione*,
non una filiazione dinastica — il conquistatore non è "erede" del conquistato,
e le note lo esplicitano dove serve.

### 2. `CONQUEST` vs `ANNEXATION` — niente eufemismi, niente drammatizzazioni
- **CONQUEST** (`is_violent=true`): sottomissione militare — Zulu 1879/1887,
  Sikh 1849, Maratha 1818, Kandy 1815, Hawaiʻi 1893 (colpo di stato armato
  con appoggio USA), Dahomey 1894, Merina 1897, Wadai 1909, Luba→Stato Libero
  del Congo 1889-94, Dzungar→Qing 1755-58 (genocidio, note esplicite),
  Vientiane→Siam 1828 (città rasa al suolo + deportazioni di massa),
  Mrauk U→Konbaung 1785, Due Sicilie→Italia 1861 (+ guerra al brigantaggio),
  Torwa→Rozwi 1684.
- **ANNEXATION** (enum già esistente, "incorporazione formale"): protettorati
  e incorporazioni formali — Rarotonga→British Empire 1888 (protettorato
  richiesto dagli ariki temendo la Francia; MAI descritto come consenso
  popolare universale), Luang Prabang→Indochina francese 1893
  (`is_violent=true`: imposto tramite la coercizione militare della guerra
  franco-siamese), Champasak→Indochina 1904 (dissoluzione amministrativa
  sotto coercizione coloniale, senza battaglia → `is_violent=false` ma la
  coercizione è esplicitata), Travancore→India: **UNIFICATION** 1949
  (adesione formalmente volontaria sotto pressione reale — documentata).
  Un protettorato imposto non è una "successione pacifica": le note portano
  sempre il contesto coercitivo.

### 3. Esclusioni documentate (il modello lineare non deve forzare)
- **Taiping #452**: stato ribelle distrutto dallo stato da cui era sorto
  (i Qing non cessarono mai di esistere) — una catena `Qing→Taiping` o
  `Taiping→Qing` assertirebbe una successione falsa. NON in catena.
- **Soyo #837**: provincia secessionista coesistita col Regno del Kongo —
  il modello lineare implica subentro, qui non c'è. NON in catena.
- **Differite per entità-controparte mancanti** (non asserire ciò che non si
  può collegare onestamente): Arabia Saudita #253 (mancano Emirato di
  Dirʿiyya e di Najd), Gorkha/Nepal #399 (manca il Nepal repubblicano),
  Taqali #411 (manca lo Stato Mahdista), regno post-angkoriano di Cambogia
  (Longvek/Oudong 1431-1863), Regno dei Serbi, Croati e Sloveni (serve anche
  alla catena serba #34), Lan Xang (predecessore dei tre regni lao),
  Regno Ndebele (successore sul terreno dei Rozwi). → elencate nel piano
  come entità da creare.

### 4. Cambogia: nessuna successione khmer falsa
Il design iniziale (`Impero khmer → Indochina, 1863`) era **doppiamente
anacronistico** (l'impero di Angkor finisce nel 1431; l'Indochina nasce nel
1887) — bocciato al cross-check. La catena è ridotta a
`Indochine française → ព្រះរាជាណាចក្រកម្ពុជា (1953)` con la lignée
khmer e il regno post-angkoriano mancante documentati nelle note di catena,
non asseriti come link.

### 5. Montenegro: fine-catena senza successore modellabile
`Зета → Кнежевина Црна Гора` termina nel 1918 senza link successore (il
Regno SHS non esiste come entità; la SFRJ 1945 sarebbe anacronistica).
L'annessione contestata (Assemblea di Podgorica 24-26.11.1918, deposizione di
Nikola I, insurrezione di Natale 7.1.1919 e repressione) è documentata in
`ethical_notes` sia a livello catena sia sull'ultimo link, con successore
non-modellato esplicitato — la catena NON deve leggersi come "scomparsa
pacifica".

### 6. Potenze regionali conquistate = catene autonome
Sikh, Maratha, Kandy, Zulu ecc. NON vengono innestate nella catena di
paramountcy indiana #19 (o simili): sarebbero rappresentate come "tappe"
della lignée del conquistatore, cancellandone la statualità distinta.
Ricevono catene autonome che terminano nell'entità conquistatrice. Le
conquiste dell'epoca della Compagnia (1818, 1849) puntano a `British Empire`
(1583-1997), non al `British Raj` (1858-) — anacronismo evitato.

### 7. Backport nome nativo: Wadai (ETHICS-001)
Il JSON aveva `Dar Wadai` (latinizzato) come `name_original` mentre prod ha
già il nativo `سلطنة وداي` — uno dei 18 rename prod-only (debito M4). Il
nome nativo è backportato nel JSON (direzione già decisa: nativo primario);
la forma latina resta come `name_variant`. Gli altri 17 restano in coda M4.

### 8. Flag di qualità emersi (non corretti qui — coda enrichment)
- **#534 "Repiblik Dayiti"** (1804-1806): il *Primo Impero* di Haiti
  (Dessalines) è etichettato "repubblica" — nome quasi certamente errato
  (atteso: *Anpi an Ayiti / Empire d'Haïti*). `#209 "Républik Ayiti"` è un
  ibrido grafico (kreyòl corretto: *Repiblik d Ayiti*). Rename = processo
  ETHICS-001 con fonti → coda.
- **#240 "សាធារណរដ្ឋខ្មែរ"** (1975-1979): il nome è "Repubblica Khmer"
  (1970-75) ma gli anni sono quelli della **Kampuchea Democratica** (Khmer
  rossi). Possibile mislabel di un regime genocida → verifica prioritaria.

## Rischio di distorsione (riassunto)
Il rischio principale era la **normalizzazione della conquista coloniale**
(eufemizzarla come "successione") o, all'opposto, la **cancellazione dello
stato conquistato** (lasciarlo orfano, invisibile alla navigazione per
catene). Le decisioni 1-6 tengono entrambe le verità: lo stato è esistito, e
la sua fine violenta/coercitiva è registrata come tale, dalle fonti, in
entrambe le prospettive (incluse le verità scomode dei conquistati: tratta
degli schiavi di Dahomey e Wadai, sacrifici annuali di Abomey — verità prima
del comfort in tutte le direzioni).
