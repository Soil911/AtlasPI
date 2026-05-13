# Enrichment session 033 — Pacific micro + Caribbean + Amazon + Sahara + Sahel cleanup

**Data**: 2026-05-13
**Versione**: v6.99.26
**Focus**: Pacific (Niue/Tokelau/Butaritari) + Lucayan + Kuhikugu + Sahrawi + Tekrur/Garoumele

## Entità arricchite (10)

| id   | name_original              | era         | conf delta  | n sources |
|------|----------------------------|-------------|-------------|-----------|
| 751  | Patuiki o Niue             | 1700-1900   | 0.40 → 0.85 | 7         |
| 752  | Taupulega o Tokelau        | 1000-1889   | 0.40 → 0.85 | 7         |
| 769  | Tuanga ni Butaritari       | 1500-1892   | 0.40 → 0.85 | 7         |
| 774  | Etalwa (Lucayan Bahamas)   | 1000-1550   | 0.45 → 0.85 | 7         |
| 795  | Kuhikugu                   | 1000-1600   | 0.55 → 0.85 | 7         |
| 826  | Amu (Sahrawi)              | 1370-1895   | 0.45 → 0.85 | 7         |
| 882  | Namayan                    | 1175-1571   | 0.35 → 0.85 | 7         |
| 905  | Balanguingui               | 1300-1848   | 0.30 → 0.85 | 7         |
| 1012 | Garoumele                  | 1200-1480   | 0.55 → 0.85 | 7         |
| 1026 | Tekrur pre-Almoravid       | 500-1040    | 0.40 → 0.85 | 7         |

**Note: S1-flagged Tekrur successfully resolved.**

## Source highlights

### Pacific micro (Niue, Tokelau, Butaritari)
- Whitcombe & Tombs / Government of Niue (Smith *Niuē-fekai* 1903)
- Bernice P. Bishop Museum (Loeb *Niue History*, Macgregor *Tokelau Ethnology*)
- U Hawai'i Press (Hooper & Huntsman *Tokelau Historical Ethnography*, Grimble *Tungaru Traditions*)
- ANU Press (Maude *Slavers in Paradise — Peruvian slave trade Polynesia 1862-64*)
- Victoria U Press (Angelo & Pasikale *Tokelau History of Government*, Chapman *Decolonisation of Niue*)
- *JPS Polynesian Society* (Huntsman & Hooper, Maude — Gilbertese Boti)
- USP Institute of Pacific Studies (Macdonald *Kiribati and Tuvalu*, Talagi *Niue*)
- Oxford UP (Sabatier *Astride the Equator — Gilbert Islands*)
- USP Pacific Studies (Lambert — Gilbertese micro-individualism)

### Caribbean Bahamas Taíno (Etalwa/Lucayan)
- U Press of Florida (Keegan *People Who Discovered Columbus*)
- U Alabama Press (Granberry & Vescelius *Languages Pre-Columbian Antilles*, Keegan & Carlson *Talking Taíno*)
- UC Press (Sauer *Early Spanish Main*)
- U Georgia Press (Craton & Saunders *Islanders in the Stream — Bahamian History*)

### Amazon Xingu (Kuhikugu)
- Routledge (Heckenberger *Ecology of Power 1000-2000*)
- *Science* (Heckenberger et al. — Amazonia 1492, Pre-Columbian Urbanism)
- *Latin American Antiquity* (Heckenberger, Petersen & Neves — village size Amazonia)
- Vintage/Knopf (Mann *1491*)

### W Sahara (Sahrawi)
- Lawrence Hill (Hodges *Western Sahara: Roots of a Desert War*)
- George Allen & Unwin (Mercer *Spanish Sahara*)
- Longman (Norris *Arab Conquest of Western Sahara*)
- Lynne Rienner (Jensen *Western Sahara — Anatomy of a Stalemate*)
- CSIC / Júcar (Caro Baroja *Estudios Saharianos*)

### Philippines (Namayan, Balanguingui)
- Ateneo de Manila UP (Scott *Barangay*)
- Imprenta Sanchez (Huerta 1865 primary)
- New Day (Dery *History of the Inarticulate*)
- Unilever Philippines (Odal-Devora — Pasig River Dwellers)
- National Museum Philippines (Fox & Legaspi *Santa Ana*)
- NUS Press (Warren *Sulu Zone 1768-1898*, *Iranun and Balangingi*)
- F. W. Cheshire/Donald Moore (Tarling *Piracy in Malay World*)
- Springer (Donoso *Bichara*)
- UP Press (Majul *Muslims in Philippines*)

### Sahel cleanup (Tekrur, Garoumele)
- Methuen (Levtzion *Ancient Ghana and Mali*)
- Karthala (Kane *Première hégémonie peule — Fuuta Tooro*)
- Brill (Thiaw *From the Senegal River to Siin* in *Migration and Membership Regimes*)
- IU African Studies (Brooks *Western African to c. 1860 — Climate Schema*)
- L'Harmattan (Ba *Histoire et politique vallée fleuve Sénégal*)
- UNESCO/Heinemann (Lange *General History of Africa* IV)
- Longman (Smith *Early States of Central Sudan*)
- BU African Studies (Cohen *Dynamics of Feudalism in Bornu*)
- Hurst & Co. (Hiribarren *History of Borno*)
- Éditions de la Sorbonne (Dewière *Sultanat du Borno XVIe-XVIIe*)

## Cumulative stats post-S33

| Metric                       | Pre-audit | Post S33 | Delta  |
|------------------------------|-----------|----------|--------|
| Total sources DB             | 2400      | **3967** | +1567  |
| Entity con ≥3 sources        | 530       | **852**  | +322   |
| Entity con ≥5 sources        | ~20       | **294**  | +274   |

## Trend complete

| Session | Entities | Focus area |
|---------|----------|------------|
| S1-S32  | 288      | (cumulative — see git log) |
| S33     | 10       | Pacific micro + Lucayan + Kuhikugu + Sahrawi + S1-flagged Tekrur |
| **Total**| **298** | 6 continenti |

## Next priorities (S34+)

- **S1-flagged residual**: Izapa, Salinar, Gallinazo (need specialized refs)
- **Ottoman/Russian Empire era**: Suomen suuriruhtinaskunta (427)
- **Africa minor**: Engaruka pre-Iron (cleanup), Kintu (Buganda precursor), Akwa
- **SE Asia minor**: Mottama, Hariphunchai, Sukhothai already covered
- **Indian Ocean**: Pate Sultanate done — focus on Comoros, Madagascar Imerina
- **Andes**: Wari-Tiwanaku already covered; focus on minor coastal Late Intermediate
- **Indigenous N Am**: Pueblo, Athabaskan, NW Coast detail
- **HRE residual**: small German states + Italian residual
