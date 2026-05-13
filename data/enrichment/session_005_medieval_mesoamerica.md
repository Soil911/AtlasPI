# Enrichment session 005 — medieval European + Mesoamerica + canonical

**Data**: 2026-05-13
**Versione**: v6.99.3
**Driver**: gap analysis post-S4, top demanded ∩ sources<3

## Entità arricchite (16)

| id | name | era | sources before→after | conf before→after |
|----|------|-----|----------------------|-------------------|
| 46 | Cahokia | 1050-1400 | 2→5 | 0.55→0.78 |
| 37 | मौर्य साम्राज्य (Maurya) | -322 to -185 | 2→5 | 0.70→0.85 |
| 89 | Imperium Francorum (Carolingian) | 800-888 | 2→5 | 0.82→0.90 |
| 78 | Великое княжество Московское (Moscow) | 1263-1547 | 2→5 | 0.75→0.85 |
| 99 | Oesterreich-Ungarn (Austria-Hungary) | 1867-1918 | 2→5 | 0.92→0.95 |
| 76 | Regnum Langobardorum | 568-774 | 2→5 | 0.70→0.85 |
| 75 | Ostrogotenreich | 493-553 | 2→5 | 0.70→0.85 |
| 40 | Haudenosaunee (Iroquois) | 1142- | 2→5 | 0.55→0.75 |
| 83 | Schweizerische Eidgenossenschaft | 1291- | 2→5 | 0.75→0.85 |
| 3 | İstanbul (Constantinople) | -657- | 2→5 | 0.50→0.85 |
| 91 | Rioghacht na hEireann (Ireland) | -500 to 1801 | 2→5 | 0.85→0.85 |
| 431 | Regnum Francorum (Merovingian) | 481-800 | 2→5 | 0.75→0.85 |
| 439 | Gothia | 250-1475 | 2→5 | 0.60→0.85 |
| 35 | བོད (Tibet) | 1950- | 2→5 | 0.40→0.75 |
| 920 | K'iik'aab (Cobá) | 426-810 | 2→5 | 0.50→0.70 |
| 929 | Huexotzinco | 1300-1521 | 2→5 | 0.65→0.78 |

## Highlight delle citazioni

- **Cambridge UP**: McKitterick *Charlemagne: The Formation of a European
  Identity* (2008), Allchin *The Archaeology of Early Historic South Asia*
  (1995), Kulikowski *Rome's Gothic Wars* (2007), Cameron *Cambridge Ancient
  History Vol XIV* (2007), Church & Head *A Concise History of Switzerland*
  (2013)
- **Oxford UP**: Wickham *Framing the Early Middle Ages* (2005), Heather
  *Goths and Romans* (1991), Goldstein *A History of Modern Tibet* (1991),
  Canny *Making Ireland British* (2001), Connolly *Divided Kingdom: Ireland
  1630-1800* (2010), Riasanovsky *A History of Russia* (2019), Siecienski
  *The Filioque* (2010), Olivelle *Kauṭilya's Arthaśāstra* (2013)
- **Yale UP**: Shakabpa *Tibet: A Political History* (1967)
- **UC Press**: Wolfram *History of the Goths* (1990), Effros *Merovingian
  Mortuary Archaeology* (2003), Goldstein (vedi sopra)
- **Brill**: Cohen *Religious Diversity in Ostrogothic Italy* (2016)
- **Walter de Gruyter**: Mathisen & Shanzer *The Battle of Vouillé*
- **Carnegie Institution**: Thompson *Preliminary Study of Cobá* (1932,
  classic archaeology)
- **Encyclopaedia of Islam 2nd ed.** (multiple)
- **Westview Press**: Smith *Tibetan Nation* (1996)

## Cumulative stats (S1+S2+S3+S4+S5)

| Metric | Inizio audit | Post S5 | Delta |
|---|---|---|---|
| Total entities arricchite | 0 | **61** | +61 |
| Total sources DB | 2400 | **3002** | **+602** |
| Entity con ≥3 sources | 530 | **637** | +107 |
| Entity con ≥4 sources | ~80 | **191** | +111 |
| Avg sources/entity (active) | ~2 | **3** | +50% |
| Top demanded entity ben coperte | ~5/40 | **40/40** | ✅ |

## Workflow checkpoint

Pattern stabile (5 sessioni consecutive):
1. SQL gap analysis (post-done exclusion)
2. WebFetch parallel batch (4-5 entity)
3. Mix OpenAlex + Wikipedia refs + canonical knowledge
4. SQL apply via SSH + confidence_score update
5. Log markdown + commit + deploy

**Tempo medio sessione**: ~30-45 min per ~15 entity.

## Priority queue per sessione 6

Pacific Oceania batch (TUTTE entity con 2 sources):
- 760 Tui Cakau (Fiji, 1700-1874)
- 759 Tui Nayau (Fiji, 1700-1874)
- 754 Sau o Futuna (1500-1961)
- 753 Hau o ʻUvea (1500-1961)
- 770 Taotao Tano (Marianas, -1500 to 1668)
- 748 Pulotu (-1500 to 1000, Polynesian mythical homeland)
- 644 Cacicazgo de Coclé (Panama, 300-1520)
- 913 Pa' Chan (Maya, 359-808)

Plus cleanup low-confidence (0.4-0.5) entity restanti.
