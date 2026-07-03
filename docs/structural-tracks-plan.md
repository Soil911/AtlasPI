# AtlasPI — Piano tracce strutturali (chain linkage + split + enrichment)

> Preparato 2026-06-04 (fine sessione v6.99.101) per la **sessione intensa successiva**.
> Clirim: "le vorrei fare tutte" → questo doc è il worklist eseguibile delle tre tracce.
> ETHICS-sensitive (confini/nomi/conquiste): ogni link/split è una *claim* storica,
> non un dato meccanico (ETHICS-002/003). Fonti accademiche REALI verificate, mai inventate.

## Stato di partenza
- Prod **v6.99.103**, CI verde, suite 1329 verde, **79 catene, 766 orfani** (da 772).
- **Fase A chiusa** (v6.99.101, chain dedup): 107→77 catene, hardening `_dedupe_by_name` + fence CI.
- **B1a fatta** (v6.99.102): estese Iran #9 (Afsharidi), Francia #8/#74 (Premier Empire),
  Romania #35 (Regno + Valacchia tedesca #579 droppata). `scripts/apply_chain_links_b1a.py`.
- **B1b fatta** (v6.99.103): NUOVE catene Brasile #109 + Italia #110. Modello unificazioni
  FISSO = linea principale + annessi nelle note.
- **Babilonia #171**: decisione presa + design COMPLETO in `docs/ethics/ETHICS-015...` →
  ESECUZIONE = primo task prossima sessione (vedi `NEXT_SESSION_PROMPT.md`).
- ⚠️ **Deploy**: l'auto-deploy GitHub "Deploy to production" ha riportato success ma NON
  ha aggiornato il VPS (HEAD restava fermo). **Usa sempre `cra-deploy`** (path diretto se
  l'alias non è caricato: `/c/Users/cliri/bin/cra-deploy.sh atlaspi`).

### Aggiornamento 2026-07-02 (sessione v6.99.106-107)
- ✅ **Babilonia #171 ESEGUITA** (v6.99.106): deprecata + 14 ref ri-homati; NUOVA entità
  #1042 "𒆳𒆍𒀭𒊏𒆠 (Post-Kassite)" (−1155..−626) per l'evento #213 (Sennacherib −689,
  anacronistico su #490 — emendamento in ETHICS-015 con cross-check ChatGPT).
- ✅ **Coerenza deprecati end-to-end** (v6.99.107): ADR-005 su ~20 endpoint discovery,
  backport status prod→JSON (66), fix 5 chain_links prod + cascata 13 ref JSON,
  guard ingest_chains + fence `test_chain_deprecated_json_audit`, follow-up
  ETHICS-012 #3/#5 chiusi. CI riparata (introspezione route FastAPI ≥ 0.139 —
  era rossa dal 17/06 e lo startup-audit sicurezza era cieco).
- 🆕 **Debito scoperto** (vedi ETHICS-012 follow-up #5): 18 rename nativi prod-only
  (→ **17** dopo v6.99.110: Wadai backportato); ~299 divergenze confidence
  bidirezionali (serve policy); 30 record JSON ombreggiati; catene etiopi #22/#100
  semanticamente duplicate + entità #853 "Aksum" dup mancato di #51; entità-fase
  meroitica nativa da creare (vedi note catena #99).

### Aggiornamento 2026-07-02 sera (sessione v6.99.110) — B1c ESEGUITA
- ✅ **B1c fatta** (v6.99.110): **21 catene nuove** (batch_34/35/36) + **3 estensioni**
  (#97 Arakan +Mrauk U+Konbaung con rename sincronizzato; #27/#49 +Segundo Imperio).
  ETHICS-017 documenta: CONQUEST vs ANNEXATION, esclusioni (Taiping/Soyo),
  Montenegro senza successore modellabile, catene autonome per le potenze
  conquistate, backport Wadai. Cross-check ChatGPT recepito (2 anacronismi evitati).
- ⏭️ **Class-1 residui** (bloccati da entità mancanti, NON dimenticati):
  Saudi #253 (servono Emirato di Dirʿiyya 1744-1818 + Emirato di Najd 1824-1891),
  Gorkha #399 (serve Nepal repubblicano 2008-), Taqali #411 (serve Stato Mahdista
  1885-1899), Rarotonga risolta, Taiping #452 e Soyo #837 esclusi per modello.
- 🆕 **Entità da creare** (sbloccano catene migliori): Lan Xang (1354-1707,
  predecessore dei 3 regni lao), Regno dei Serbi Croati e Sloveni (1918-1929/41 —
  serve ANCHE alla catena serba #34, i cui link 'Jugoslavija' non risolsero mai),
  regno post-angkoriano di Cambogia (Longvek/Oudong 1431-1863), Regno Ndebele
  (1838-1893, successore dei Rozwi), **Medri Bahri** (ምድሪ ባሕሪ, altopiano eritreo
  ~1450-1890 — da ETHICS-018: la sua variante è stata rimossa da Aksum),
  Repubblica di Hawaii NON necessaria (coperta in note). Flag qualità: #534 nome
  del Primo Impero di Haiti errato; #240 nome Khmer Republic con anni della
  Kampuchea Democratica (1975-79) — VERIFICARE.

### Aggiornamento 2026-07-03 (sessione v6.99.111-112)
- ✅ **Fix logging Alembic** (v6.99.111): fileConfig con guard — "AtlasPI pronto"
  e audit admin tornano nei docker logs.
- ✅ **Dedup trunk etiope ESEGUITO** (v6.99.112, ETHICS-018): catena #22 merged a
  4 nodi nativi (D'mt→Aksum #51→Zagwe DISSOLUTION→Solomonic), #100 eliminata
  (prod a 99 catene), #853 deprecato con re-homing a #51, 'Medri Bahri' rimossa
  (entità da creare), doppio polygon Aksum risolto.

---

## TRACK B1 — Chain linkage "Class-1" (formazione nazionale moderna) — PRIORITÀ ALTA

Linking PULITO: endpoint già esistenti, successione canonica (anche se violenta → registrata
onestamente con `is_violent=true` + `ethical_notes`). Modello `chain_links`: `sequence_order`
(0=più antica), `transition_type`, `transition_year`, `is_violent`, `description`,
`ethical_notes`, + `sources` a livello catena. Spec JSON in `data/chains/batch_NN_*.json`,
ingest idempotente via `ingest_chains` (ora hardened). **Aggiorna SEMPRE JSON + prod.**

### B1a — ESTENDERE catene esistenti (il lavoro più pulito: già "TODO-listato" nelle note)
Diverse catene hanno `ethical_notes` che dicono esplicitamente "entità intermedia non ancora
seedata, aggiungere in batch successivo". Ora quelle entità ESISTONO → inserirle:
- **Catena francese #74** (`Regnum Francorum → … → République`): inserire **Premier Empire
  français #1037** (1804-1815, REVOLUTION/CONQUEST, is_violent) tra Royaume de France e
  République. *(Le note della catena #74 lo flaggano già.)*
- **Catena iraniana #9** (`Safavid→Qajar→Pahlavi→Islamic Republic`): inserire **Afsharian
  #1038** (افشاریان, 1736-1796) [+ Zand se esiste] tra Safavid e Qajar. *(Note già flaggano
  Afsharid/Zand.)*
- **Catena messicana #27/#49**: inserire **Segundo Imperio Mexicano #522** (1864-1867,
  impero di Massimiliano, intervento francese → CONQUEST/is_violent; fucilazione 1867).
- **Catena rumena #35**: appendere **Regatul României #441** (1881-1947) + modern Romania.
  ⚠️ **Prima fixare un bug in #35**: la Valacchia è doppia — link a #579 "Furstentum Walachei"
  (nome tedesco) E #93 "Tara Romaneasca" (nome rumeno). Verificare quale tenere (ETHICS-001:
  nome locale primario → #93) e correggere la catena.

### B1b — NUOVE catene nazionali canoniche (endpoint verificati esistenti)
- **Brasile** (pronta, 2-link): Brasil Colônia #207 (1500-1822) → Império do Brasil #523
  (1822-1889, INDEPENDENCE da Portogallo). Nessuna entità repubblica → documentare 1889 in note.
- **Unificazione italiana**: Regno di Sardegna #423 → **Regno d'Italia #100** (1861).
  Annessi: Due Sicilie #572, Regno di Napoli #424 (predecessore delle Due Sicilie, fino 1816).
  ⚠️ **DECISIONE MODELLO** (vedi sotto): il modello è lineare → many→one va gestito.
- Altri candidati Class-1 (orfani, conf≥0.7, post-1400) da raggruppare in catene:
  Montenegro **#95** (Crna Gora 1515-1918), Madagascar/Merina **#162**, Dahomey **#149**,
  Zulu **#34**, Hawaii **#43**, Sikh/Khalsa **#400** (→ British Raj, link a catena indiana #19),
  Haiti **#534**, Saudi (3° stato) **#253**, Maratha **#111**, Gorkha/Nepal **#399**,
  Laos (Luang Prabang **#364** + Champasak **#363**), Mutapa **#154**, Rozwi **#155**,
  Wadai **#412**, Imerina, ecc. (lista completa: 33 entità, vedi query sotto).

### ⚠️ DECISIONE DI MODELLO (chiedere a Clirim prima di scrivere le unificazioni)
Il modello `chain_links` è **lineare** (`sequence_order`) — ottimo per successioni dinastiche
(A→B→C), scomodo per **unificazioni *molti→uno*** (Italia, Germania). Opzioni:
- (a) **[raccomandato]** linea principale (es. Sardegna→Regno d'Italia) + stati annessi
  documentati in `ethical_notes`, senza imporre un falso ordine sequenziale.
- (b) modellare ogni stato annesso come link CONQUEST/ANNEXATION verso l'entità unificata
  (ma `sequence_order` implica un ordine che non c'è).
- (c) accettare il limite e fare solo le successioni lineari pulite per ora.

---

## TRACK B2 / Track 3 — Split dei super-aggregati di successione statale

⚠️ **Distinzione etica fondamentale** (CLAUDE.md valore #4: niente periodizzazione coloniale):
NON tutti gli span lunghi vanno splittati. I **popoli/confederazioni indigene continue**
(Noongar #771 41.829 anni, Wiradjuri #772, chiefdom Solomon #317 / Vanuatu #318 / Marshall
#313 / Kanaky #315, Selk'nam #519, Aonikenk #541, Charrua #540, Arawak #527, Lenca #551…)
sono CORRETTAMENTE una sola entità long-lived — splittarli imporrebbe una periodizzazione
esterna. **Lasciare come sono** (e infatti non stanno in catene dinastiche, giusto).

**Veri split-candidate** (aggregati che conflano polities di *successione statale* distinte):
- **Babilonia #171** (combinata −1894..−539, 0.65): ridondante — esistono già Old Babylonian
  #1039 (−1894..−1595, 0.78) e Neo-Babylonian #490 (−626..−539, 0.78). Piano: **deprecate/narrow
  #171** (= follow-up #4 di wave2). ⚠️ La catena mesopotamica **#88** linka #171 a seq2 →
  ripuntare a #1039 (e verificare la coerenza con #490 a seq5). Sistemare #171 ripulisce #88.
- **Sri Lanka #142** (−543..1815, uncertain 0.4): `name_original` è il nome di un RE
  (මහා විජයබාහු = Mahā Vijayabāhu), non dell'entità. Decomporre nei regni reali: Anuradhapura,
  Polonnaruwa, Dambadeniya/Gampola/Kotte, Kandy. Più aperto/delicato → design con Clirim.
- **Kemet #26** (Egitto −3100..−30, 0.85): super-aggregato dell'intero Egitto antico.
  Valutare se decomporre per regni (Antico/Medio/Nuovo) o lasciare come macro-entità +
  documentare. Interagisce con la catena Nilo/Kush #99 (che è Nubia, non Egitto proprio).
- **Sidone #507** (𐤑𐤃𐤍, −3000..−332, city-state, 0.5), **Mixtec/Ñuu Dzahui #196** (−1500..1523):
  valutare caso per caso.

---

## TRACK 1 — Enrichment coda low-confidence (turnkey, valore marginale calante)
~206 entità <0.6. Workflow collaudato: spec `data/fixes/enrichment_sNN.json` →
`python -m scripts.apply_enrichment <spec>` (aggiorna JSON + emette SQL) → suite/fence →
commit → backup pg_dump + SQL su prod + `cra-deploy` + smoke. Standard qualità: fonti
accademiche reali verificate via WebSearch, ethical_notes non-eufemistici (ETHICS-007),
confidence calibrata onestamente, uncertain→confirmed solo se ≥0.5.

Query candidati:
```
ssh -i ~/.ssh/cra_vps root@77.81.229.242 "docker exec cra-atlaspi-db psql -U atlaspi -d atlaspi -c \"SELECT g.id,g.name_original,g.entity_type,g.year_start,g.confidence_score,(SELECT count(*) FROM sources s WHERE s.entity_id=g.id) n FROM geo_entities g WHERE g.confidence_score<0.55 AND g.status!='deprecated' ORDER BY g.confidence_score,n LIMIT 30\""
```

---

## DECISIONI DI CLIRIM (non procedere senza ok)
1. **Modello unificazioni** (B1, vedi sopra) — (a)/(b)/(c)? Default raccomandato: (a).
2. **#83**: client esterno → 422 su anni < −4000. Estendere copertura pre-4000 a.C. vs
   documentare il floor / restituire vuoto invece di 422.
3. **DOMINIO**: sblocca discoverability (MCP-registry, GSC/Bing, backlink). Decidere PRIMA,
   poi submission una volta sola (vedi memoria `seo-indexing-status`).
4. **7 insert solo-prod + sync name_original nativo** (ETHICS-012 §"#2"): cap 6 `disputed`>0.70
   in prod; add `name_variants` ai 4 insert che ne mancano.

## Worklist data (query rieseguibili)
```sql
-- Class-1 linking candidates (orfani moderni)
SELECT g.id,g.name_original,g.entity_type,g.year_start,g.year_end,g.confidence_score
FROM geo_entities g
WHERE g.status!='deprecated' AND g.id NOT IN (SELECT DISTINCT entity_id FROM chain_links)
  AND g.year_start>=1400 AND g.entity_type IN ('empire','kingdom') AND g.confidence_score>=0.7
ORDER BY g.year_start;  -- 33 righe (2026-06-04)

-- Super-aggregati (split-candidate vs popoli continui — distinguere!)
SELECT g.id,g.name_original,g.entity_type,g.year_start,g.year_end,(g.year_end-g.year_start) span,g.status
FROM geo_entities g
WHERE g.status!='deprecated' AND g.id NOT IN (SELECT DISTINCT entity_id FROM chain_links)
  AND (g.year_end-g.year_start)>900 ORDER BY span DESC;
```

## Workflow / note operative
- Deploy: **`/c/Users/cliri/bin/cra-deploy.sh atlaspi`** (auto-deploy GitHub inaffidabile).
- SQL prod manuale via stdin: `ssh -i ~/.ssh/cra_vps root@77.81.229.242 "docker exec -i cra-atlaspi-db psql -U atlaspi -d atlaspi -v ON_ERROR_STOP=1" < file.sql`. Backup pg_dump PRIMA.
- Bash sandboxato reverta i file git-tracked → usa `dangerouslyDisableSandbox` per edit-bulk/git/ssh.
- Console cp1252 → `PYTHONUTF8=1` per nomi non-ASCII.
- Cross-check ChatGPT-5.5 su decisioni etiche non-triviali: `from scripts.chatgpt_review import ask`.
- Deploy SOLO se: CI verde, suite verde, backup preso. Mai toccare codice sul VPS.
- Ogni link/split = claim storica → fonti reali, transition_type onesto (CONQUEST non
  eufemizzato), is_violent veritiero. Successione contestata → ETHICS record, non asserita in silenzio.
