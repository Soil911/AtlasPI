# Enrichment session 002 + 003 — top-demanded entità (analytics-driven)

**Data**: 2026-05-13
**Versione**: v6.99.1
**Driver**: api_request_logs analytics (top entity richieste ultimo mese)

## Methodology data-driven

Query analytics su `api_request_logs.path ~ '^/v1/entities/[0-9]+$'`
group by entity_id. Top 40 entity richieste cross-validate con
`(SELECT count(*) FROM sources WHERE entity_id=g.id) < 3`.

Risultato: 20 entity ad alto traffico (10-19 hits/mese) con poche fonti.

## Top search queries (parallelo)

Da `query_string LIKE 'q=%'` su `/v1/search*`:
- "Roma" (33 hits) → id 1 Imperium Romanum + 1034 Res Publica (S1)
- "venice" (32 hits) → curation gap
- "Achaemenid" (15+4 = 19) → id 27 (S2 batch 1)
- "Mughal" (14) → id 12 (già OK)
- "byzantine" (24 totali) → id 11 (S2 batch 4)
- "Aksum" (5) → id 853 (4 sources OK)

## Entità arricchite Session 2

### Batch 1 — Ancient empires (top demand)
| id | name | hits/mese | sources before→after | conf before→after |
|----|------|-----------|----------------------|-------------------|
| 27 | Xšāça (Achaemenid) | 19 | 2→5 | 0.80→0.85 |
| 26 | Kemet (Egypt) | 15 | 2→5 | 0.80→0.85 |
| 52 | Kush | 18 | 3→6 | 0.60→0.75 |
| 36 | Qart-ḥadašt (Carthage) | 11 | 2→5 | 0.70→0.80 |

### Batch 2 — Egypt + Horn of Africa
| id | name | hits/mese | sources before→after | conf before→after |
|----|------|-----------|----------------------|-------------------|
| 1031 | Punt | 12 | 2→5 | 0.40→0.60 |
| 1005 | Solomonic Ethiopia early | 13 | 2→5 | 0.70→0.78 |
| 1006 | Sultanate of Shewa | 11 | 2→5 | 0.45→0.65 |
| 1007 | Zeila | 11 | 3→6 | 0.60→0.72 |

### Batch 3 — Sahel polities
| id | name | hits/mese | sources before→after | conf before→after |
|----|------|-----------|----------------------|-------------------|
| 1001 | Wadan | 12 | 2→5 | 0.60→0.70 |
| 1002 | Oualata | 12 | 2→5 | 0.50→0.65 |
| 986 | Banu Midrar | 12 | 2→5 | 0.60→0.78 |
| 1033 | al-Tunjur | 11 | 2→5 | 0.30→0.55 |

### Batch 4 — Misc (Byzantine + Slavic + SE Asia)
| id | name | hits/mese | sources before→after | conf before→after |
|----|------|-----------|----------------------|-------------------|
| 11 | Βασιλεία Ῥωμαίων (Byzantine) | 24 (search) | 3→6 | 0.85→0.95 |
| 705 | 蘭芳共和國 (Lan Fang) | 10 | 2→5 | 0.60→0.70 |
| 665 | Зета (Zeta) | 11 | 2→5 | 0.60→0.75 |
| 679 | Полацкае княства (Polotsk) | 11 | 2→5 | 0.50→0.65 |

## Entità arricchite Session 3

| id | name | hits/mese | sources before→after | conf before→after |
|----|------|-----------|----------------------|-------------------|
| 988 | بنو حماد (Hammadid) | 11 | 2→5 | 0.65→0.78 |
| 664 | Видинско царство (Vidin Tsardom) | 11 | 2→5 | 0.65→0.75 |
| 875 | Lemro / Mrauk-U Arakan | 12 | 2→5 | 0.55→0.70 |
| 900 | Ta-hua-lo / Lavo Kingdom | 12 | 2→5 | 0.55→0.70 |

## Source highlights

- Stanford UP (Treadgold Byzantine), Oxford UP (Kaldellis), Cambridge UP (Crampton, Fage&Oliver)
- Brill (Chekroun&Hirsch, Baadj Hammadid)
- University of California Press (Marcus Ethiopia)
- University of Michigan Press (Fine Late Medieval Balkans)
- Encyclopaedia of Islam, Second Edition (multiple)
- Journal of African History, Journal of North African Studies
- PLoS ONE (Schwartz Carthage osteoarchaeology, Matisoo-Smith Phoenician mtDNA)
- Africana Encyclopedia, Cambridge History of Africa
- Cornell SEAP Publications (Heidhues Lanfang)

## Combined statistics (Session 1 + 2 + 3)

- **Total entities arricchite**: 41/994 active (4.1%)
- **Total sources**: 2400 → 2942 (+542)
- **Entity con ≥3 sources**: ~530 → 618 (+88)
- **Top demanded ben coperte**: 40/40 in top-traffic list

## Workflow validato

```
1. SQL gap analysis (analytics-driven): top demanded ∩ sources<3
2. WebFetch batch parallel (4-5 entity/batch):
   - OpenAlex API per topics mainstream (cited_by_count filter)
   - Wikipedia REST + references mining per topics nicchia
3. SQL INSERT in sources + confidence_score UPDATE via SSH
4. Log markdown per audit trail
```

## Next iteration priorities

Da analytics, ancora con < 3 sources e ≥10 hits/mese:
- 901 Tambralinga (currently 3 sources)
- 871 Halin (currently 3 sources)
- Entity sotto-coperte per regioni: Centro-Asia, India pre-Mughal, SE Asia maritime

Curation manual queue (da session 1):
- 961 Izapa, 970 Salinar, 971 Gallinazo, 1026 Tekrur, 1029 Lembeh-Shemba

Search query "venice" (32 hits) → curation gap, verifica esistenza entità.
Search query "Florence" (4 hits) → idem.
