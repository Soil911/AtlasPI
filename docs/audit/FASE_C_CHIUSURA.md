# AtlasPI — Audit v4 Fase C Closure Report

**Data**: 2026-04-19
**Release deployate**: v6.71.0 → v6.79.0 (9 release nel ciclo Fase C)
**Stato finale**: live su https://atlaspi.cra-srl.com v6.79.0

---

## Summary esecutivo

Il ciclo Fase C ha chiuso il piano audit v4 in 9 release sequenziali, ciascuna deployata in produzione con verifica end-to-end. Il valore consegnato in questa fase è quasi tutto **strutturale**:

1. Cross-reference Wikidata sistematico (52% → 69%)
2. Sites archeologici linkati a polities (0% → 93%)
3. Cities linkate a polities (16% → 99%)
4. Drift detection automatizzato giornaliero
5. Documentazione esplicita di drift legittimi (site-vs-polity, capital iconica vs storica)

---

## Release ledger Fase C

| Release | Tema | Δ Quality |
|---------|------|-----------|
| v6.71.0 | Round 1: wrong QID + Rome missing + site-vs-polity | 5 wrong QID corretti, Rome→Q2277, 2 ethical_notes annotate |
| v6.72.0 | Round 2: 42 duplicate QIDs → 0 | 42 secondary entity liberate, no duplicate QID rimangono |
| v6.73.0 | Round 3: mid-band 144 + 3 collision | +141 QIDs, scoperto pattern apply→verify→collision_fix |
| v6.74.0 | Round 4: conservative 0.60-0.75 | +42 QIDs (≥2 strong reasons gate) |
| v6.75.0 | Round 5: HIGH drift annotations | 54 entities con drift HIGH annotate in ethical_notes |
| v6.76.0 | Round 6: no-match pickup via English variants | +31 QIDs (16% pickup rate) |
| v6.77.0 | Round 7: Sites FK backfill PostGIS | 0% → 93.1% sites linked |
| v6.78.0 | Round 8: Cities FK + script/lang detector | 84% NULL → 99.1% linked + diagnostic report |
| v6.79.0 | Round 9: nightly cron + closure | continuous drift detection installed |

---

## Stato finale dataset

### Wikidata cross-reference

| Metric | Pre-audit v4 | Post-Fase A | Post-Fase C |
|--------|--------------|-------------|-------------|
| Entità con QID | 0 | 540 | **711** (68.8%) |
| Duplicate QID | N/A | 42 | **0** |
| HIGH drift annotated | 0 | 0 | 56 (Ugarit/Troy + 54) |

### Foreign key integrity

| Resource | Pre-audit v4 NULL | Post-Fase C NULL | % linked |
|----------|-------------------|------------------|----------|
| sites.entity_id | 1249 (100%) | 86 | **93.1%** |
| cities.entity_id | 92 (84%) | 1 | **99.1%** |

### Continuous validation

- ✅ Nightly drift check via `/etc/cron.daily/atlaspi-drift` su VPS
- ✅ Reports persisted in `/var/log/atlaspi/drift_YYYYMMDD.md`
- ✅ Alert syslog `atlaspi-drift` su HIGH count increase day-over-day
- ✅ Auto-cleanup after 30 giorni

---

## Pattern sistemici riconosciuti

### Confermati dal lavoro

1. **Site vs Polity** (Round 1 + Round 5): siti archeologici e polities storiche hanno date range diverse legittimi. Wikidata aggrega; AtlasPI separa per polity-specific era. Annotation pattern in ethical_notes ora baseline.

2. **Capital iconica vs prima** (Round 5): pattern già visto in v6.65 (HRE Wien, Mali Niani, Mughal Delhi); confermato esteso (Achaemenid Persepolis vs Pasargadae, Ottoman Istanbul pre-1453).

3. **Native script vs Latin transliteration duplicates** (Round 3): pattern AtlasPI-internal di seed che produce sia "ᏣᎳᎩ" che "Tsalagi" come entità separate. Round 3 ha trovato 3 collision interne; Round 8 detector ha trovato ~187 candidate (false positive heavy).

4. **English name_variants pickup** (Round 6): ~16% delle 188 no-match risolvibili semplicemente cercando il nome inglese. Suggests need to **always** add English name_variant a entità con native script primary.

### Lezioni metodologiche

1. **Mai applicare QID senza verifica diretta**. Il handoff Fase A+B aveva 2 QID sbagliati (film + atleta). Sempre `wbsearchentities` + `Special:EntityData` prima di apply.

2. **Apply → Verify → Collision Fix** è il pattern corretto, non "Pre-filter only". Il batch può creare collisioni interne non rilevabili con check pre.

3. **PostGIS bbox prefilter** è critico per CROSS JOIN su geometrie. Senza, una query da 30 secondi diventa una query da 7+ minuti che muore.

4. **Conservare il dato AtlasPI quando in conflict con Wikidata**: spesso AtlasPI è più preciso (es. polity-specific era vs site-multi-phase). Wikidata come cross-reference, NON source-of-truth.

---

## Cosa non è stato fatto (deferred a future release)

### Strutturale (richiede ADR)

- **Merge entità duplicate**: 42 secondary entities hanno QID NULL ma rimangono nel DB. Decisione "merge vs keep-split" richiede ADR per:
  - Convention naming (qual entità tenere?)
  - Migration script per ricollegare events/rulers/sites/chains della secondary alla primary
  - Public API: cambia entity_count, possibili broken bookmarks

- **Split entità bundled**: Babilonia (3 polities), Chola (Sangam + Medieval), Kanem-Bornu (vs Kanem + Bornu sub-entities). Audit v2 Agent 04 raccomandava split.

### Pattern (richiede pipeline refinement)

- **Script/lang mismatch refined fix**: il detector v6.78 ha 187 falsi positivi su lang=ar. Refined version dovrebbe filtrare "almeno N caratteri non-Latin presenti = OK". Stima: 1-2h.

- **Sites NULL residui (86)**: sites in regioni dove AtlasPI manca boundary (SE Asia, sub-Sahara). Backfill possibile via:
  - country_code lookup (Natural Earth)
  - admin region match
  - manual review per UNESCO sites famosi

- **No-match restanti (157)**: 188 - 31 picked-up = 157 ancora NULL. Composte da:
  - Pre-contact indigenous polities (Wikidata gaps genuini)
  - Entità con name in script poco supportato da Wikidata search
  - Possibile soluzione: contribuire QID a Wikidata, poi re-bootstrap

### Architetturale (richiede design)

- **Schema `capital_history[]`**: pattern ricorrente — entità lunga durata con capitali multiple. Round 5 ha annotato 54 casi via ethical_notes ma soluzione strutturale è schema extension.

- **4 entità mancanti** (Premier Empire français, Afsharid, Regnum Francorum Carolingian 751-843, Virreinato del Perú dataset cleanup): create new entities richiede seed pipeline run.

---

## Continuous validation: come usare

### Lettura nightly report

```bash
# Latest report
ssh -i ~/.ssh/cra_vps root@77.81.229.242 \
  "ls -t /var/log/atlaspi/drift_*.md | head -1 | xargs cat | head -50"

# Day-over-day diff
ssh -i ~/.ssh/cra_vps root@77.81.229.242 \
  "diff /var/log/atlaspi/drift_$(date -d 'yesterday' +%Y%m%d).md /var/log/atlaspi/drift_$(date +%Y%m%d).md"

# Syslog alerts
ssh -i ~/.ssh/cra_vps root@77.81.229.242 \
  "journalctl -t atlaspi-drift -n 50"
```

### Cosa fare se HIGH count aumenta

Significa che Wikidata ha avuto un edit che ora confligge con AtlasPI (raro ma possibile). Steps:

1. Cat il report del giorno: `cat /var/log/atlaspi/drift_YYYYMMDD.md`
2. Identifica nuovi HIGH (entità non presenti ieri)
3. Verifica manualmente la fonte Wikidata
4. Decidi:
   - Se Wikidata è corretto → patch AtlasPI
   - Se AtlasPI è corretto → annotare in ethical_notes che AtlasPI rigetta drift Wikidata

---

## Riferimenti

- **Audit v4 Fase A+B handoff originale**: `docs/audit/FASE_A_B_HANDOFF.md`
- **Fase A+B closure (sessione precedente)**: `docs/audit/FASE_C_HANDOFF.md`
- **CHANGELOG dettagliato**: `CHANGELOG.md` v6.69 → v6.79
- **ETHICS records pertinenti**: ETHICS-009 (categorie politiche coloniali), ETHICS-010 (Wikidata cross-reference)
- **Nightly cron**: `/etc/cron.daily/atlaspi-drift` su VPS, source `scripts/nightly_drift_check.sh`

---

## Chiusura

Il piano audit v4 (Fase A+B+C) è **chiuso**. AtlasPI ha:

- Cross-reference Wikidata stabile (711/1034 = 69%) con zero duplicati e annotation completa dei drift legittimi
- FK integrity sites/cities risolti al 99-93%
- Pipeline di drift detection automatizzata day-over-day
- Documentazione metodologica trasferibile a future fasi (split, merge, missing entities)

Le decisioni rimanenti sono tutte **architettoniche** (richiedono ADR) o **pipeline refinement** (richiedono tempo dedicato), non bug né debiti tecnici critici. Il dataset è ora "audit-tested baseline" su cui costruire features successive in confidence.
