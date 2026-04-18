# Audit v4 — Fase B: Drift Report (Wikidata ↔ AtlasPI)
**Data**: v6.70 post-bootstrap Fase A.
**Scopo**: identificare discrepanze tra AtlasPI e Wikidata sui campi chiave (anno inizio/fine, capitale, coordinate capitale). I risultati sono segnali di drift, NON errori certificati — Wikidata può avere convention diverse o bias. Ogni HIGH va valutato manualmente (Fase C).

## Stats
- Entità con Wikidata Q-ID controllate: **540**
- Entità con ≥1 drift: **300**
- Drift totali: **392**
  - HIGH: 108
  - MED: 270
  - LOW: 14
- Patch autofixable generate: **0**

## Distribuzione per campo

| Campo | HIGH | MED | LOW | Totale |
|-------|------|-----|-----|--------|
| year_start | 61 | 23 | 9 | 93 |
| year_end | 33 | 10 | 4 | 47 |
| capital_name | 0 | 207 | 0 | 207 |
| capital_coord | 14 | 30 | 0 | 44 |
| capital | 0 | 0 | 1 | 1 |

## Top 50 HIGH drift (review urgenti)

1. **[208]** Thirteen Colonies — capital coord Δ=5699.8km (AtlasPI={'lat': 39.9526, 'lon': -75.1652}, Wikidata={'lat': 51.507222222222, 'lon': -0.1275, 'qid': 'Q84'}). Ref: [Q258532](https://www.wikidata.org/wiki/Q258532) British America
2. **[498]** 𐎜𐎂𐎗𐎚 / Ugarit (city-state) — year_start: AtlasPI=-1450 vs Wikidata=-6000 (**Δ=4550y**, HIGH). Ref: [Q191369](https://www.wikidata.org/wiki/Q191369) Ugarit
3. **[91]** Rioghacht na hEireann (kingdom) — year_start: AtlasPI=-500 vs Wikidata=1542 (**Δ=2042y**, HIGH). Ref: [Q215530](https://www.wikidata.org/wiki/Q215530) Kingdom of Ireland
4. **[142]** මහා විජයබාහු (kingdom) — year_start: AtlasPI=-543 vs Wikidata=1469 (**Δ=2012y**, HIGH). Ref: [Q1530762](https://www.wikidata.org/wiki/Q1530762) Kingdom of Kandy
5. **[552]** Meroe (kingdom) — year_start: AtlasPI=-300 vs Wikidata=-2180 (**Δ=1880y**, HIGH). Ref: [Q241790](https://www.wikidata.org/wiki/Q241790) Kingdom of Kush
6. **[272]** Τροία / Wilusa (city-state) — year_end: AtlasPI=-1180 vs Wikidata=500 (**Δ=1680y**, HIGH). Ref: [Q22647](https://www.wikidata.org/wiki/Q22647) Troy
7. **[864]** 林邑 (kingdom) — year_end: AtlasPI=605 vs Wikidata=1832 (**Δ=1227y**, HIGH). Ref: [Q216786](https://www.wikidata.org/wiki/Q216786) Champa
8. **[850]** اسلامی جمہوریۂ پاکستان — capital coord Δ=1142.1km (AtlasPI={'lat': 33.6844, 'lon': 73.0479}, Wikidata={'lat': 24.86, 'lon': 67.01, 'qid': 'Q8660'}). Ref: [Q2006542](https://www.wikidata.org/wiki/Q2006542) Dominion of Pakistan
9. **[52]** Kush (kingdom) — year_start: AtlasPI=-1070 vs Wikidata=-2180 (**Δ=1110y**, HIGH). Ref: [Q241790](https://www.wikidata.org/wiki/Q241790) Kingdom of Kush
10. **[376]** சேர நாடு (kingdom) — year_start: AtlasPI=-300 vs Wikidata=800 (**Δ=1100y**, HIGH). Ref: [Q877155](https://www.wikidata.org/wiki/Q877155) Chera dynasty
11. **[439]** Gothia (principality) — year_start: AtlasPI=250 vs Wikidata=1300 (**Δ=1050y**, HIGH). Ref: [Q874954](https://www.wikidata.org/wiki/Q874954) Principality of Theodoro
12. **[973]** Kerma (kingdom) — year_start: AtlasPI=-2500 vs Wikidata=-3500 (**Δ=1000y**, HIGH). Ref: [Q1739282](https://www.wikidata.org/wiki/Q1739282) Kerma kingdom
13. **[26]** Kemet (empire) — year_start: AtlasPI=-3100 vs Wikidata=-4000 (**Δ=900y**, HIGH). Ref: [Q11768](https://www.wikidata.org/wiki/Q11768) Ancient Egypt
14. **[442]** 大和王権 (kingdom) — year_start: AtlasPI=250 vs Wikidata=-600 (**Δ=850y**, HIGH). Ref: [Q10888424](https://www.wikidata.org/wiki/Q10888424) Wakoku
15. **[327]** Алтын Орда / اردوی زرین — capital coord Δ=745.2km (AtlasPI={'lat': 48.67, 'lon': 45.31}, Wikidata={'lat': 54.966666666667, 'lon': 49.033333333333, 'qid': 'Q105284'}). Ref: [Q79965](https://www.wikidata.org/wiki/Q79965) Golden Horde
16. **[425]** Nafarroako Erresuma (kingdom) — year_start: AtlasPI=824 vs Wikidata=1512 (**Δ=688y**, HIGH). Ref: [Q63021609](https://www.wikidata.org/wiki/Q63021609) Kingdom of Navarre beyond the Pyrenees
17. **[806]** 𒅁𒆷 (kingdom) — year_end: AtlasPI=-1600 vs Wikidata=-2240 (**Δ=640y**, HIGH). Ref: [Q5743](https://www.wikidata.org/wiki/Q5743) Ebla
18. **[378]** सातवाहन — capital coord Δ=629.0km (AtlasPI={'lat': 19.6, 'lon': 75.33}, Wikidata={'lat': 16.573, 'lon': 80.358, 'qid': 'Q2087762'}). Ref: [Q5257](https://www.wikidata.org/wiki/Q5257) Satavahana dynasty
19. **[856]** Malo o Samoa (confederation) — year_start: AtlasPI=1250 vs Wikidata=1858 (**Δ=608y**, HIGH). Ref: [Q136527950](https://www.wikidata.org/wiki/Q136527950) Kingdom of Samoa
20. **[872]** သထုံ (kingdom) — year_start: AtlasPI=300 vs Wikidata=-300 (**Δ=600y**, HIGH). Ref: [Q1651832](https://www.wikidata.org/wiki/Q1651832) Thaton Kingdom
21. **[590]** ପୂର୍ବ ଗଙ୍ଗ (dynasty) — year_start: AtlasPI=498 vs Wikidata=1078 (**Δ=580y**, HIGH). Ref: [Q250515](https://www.wikidata.org/wiki/Q250515) Eastern Ganga dynasty
22. **[147]** Kanem-Bornu (empire) — year_end: AtlasPI=1893 vs Wikidata=1376 (**Δ=517y**, HIGH). Ref: [Q1537016](https://www.wikidata.org/wiki/Q1537016) Kanem Empire
23. **[614]** Βασιλεία Ἀντιγονιδῶν (kingdom) — year_start: AtlasPI=-306 vs Wikidata=-808 (**Δ=502y**, HIGH). Ref: [Q83958](https://www.wikidata.org/wiki/Q83958) Macedonia
24. **[997]** Nok (culture) — year_end: AtlasPI=500 vs Wikidata=-1 (**Δ=501y**, HIGH). Ref: [Q927291](https://www.wikidata.org/wiki/Q927291) Nok culture
25. **[51]** መንግሥተ አክሱም (kingdom) — year_start: AtlasPI=100 vs Wikidata=-400 (**Δ=500y**, HIGH). Ref: [Q139377](https://www.wikidata.org/wiki/Q139377) Kingdom of Aksum
26. **[95]** Кнежевина Црна Гора (kingdom) — year_start: AtlasPI=1515 vs Wikidata=1910 (**Δ=395y**, HIGH). Ref: [Q386496](https://www.wikidata.org/wiki/Q386496) Kingdom of Montenegro
27. **[685]** Kesultanan Tidore (sultanate) — year_start: AtlasPI=1081 vs Wikidata=1450 (**Δ=369y**, HIGH). Ref: [Q4118614](https://www.wikidata.org/wiki/Q4118614) Sultanate of Tidore
28. **[328]** چغتای خانات (khanate) — year_end: AtlasPI=1347 vs Wikidata=1687 (**Δ=340y**, HIGH). Ref: [Q487829](https://www.wikidata.org/wiki/Q487829) Chagatai Khanate
29. **[1009]** سلطنة مقديشو (city-state) — year_end: AtlasPI=1270 vs Wikidata=1600 (**Δ=330y**, HIGH). Ref: [Q861784](https://www.wikidata.org/wiki/Q861784) Sultanate of Mogadishu
30. **[746]** Harer Ge (sultanate) — year_end: AtlasPI=1887 vs Wikidata=1577 (**Δ=310y**, HIGH). Ref: [Q7636797](https://www.wikidata.org/wiki/Q7636797) Sultanate of Harar
31. **[645]** Nsi a Teke (kingdom) — year_start: AtlasPI=1400 vs Wikidata=1700 (**Δ=300y**, HIGH). Ref: [Q4778463](https://www.wikidata.org/wiki/Q4778463) Anziku Kingdom
32. **[342]** غوریان — capital coord Δ=298.0km (AtlasPI={'lat': 34.7, 'lon': 65.5}, Wikidata={'lat': 33.549166666667, 'lon': 68.423333333333, 'qid': 'Q173731'}). Ref: [Q18608788](https://www.wikidata.org/wiki/Q18608788) Ghurid Empire
33. **[408]** Sultanat Adal — capital coord Δ=271.1km (AtlasPI={'lat': 9.3117, 'lon': 42.12}, Wikidata={'lat': 11.353888888889, 'lon': 43.473888888889, 'qid': 'Q157800'}). Ref: [Q2365048](https://www.wikidata.org/wiki/Q2365048) Adal Sultanate
34. **[581]** Kurfurstentum Pfalz (principality) — year_start: AtlasPI=1356 vs Wikidata=1085 (**Δ=271y**, HIGH). Ref: [Q22880](https://www.wikidata.org/wiki/Q22880) Electoral Palatinate
35. **[92]** Tywysogaeth Cymru (kingdom) — year_end: AtlasPI=1283 vs Wikidata=1542 (**Δ=259y**, HIGH). Ref: [Q1483510](https://www.wikidata.org/wiki/Q1483510) Principality of Wales
36. **[607]** ᠬᠣᠲᠠᠨ ᠬᠠᠭᠠᠨᠯᠢᠭ (kingdom) — year_start: AtlasPI=-200 vs Wikidata=56 (**Δ=256y**, HIGH). Ref: [Q914898](https://www.wikidata.org/wiki/Q914898) Kingdom of Khotan
37. **[885]** Samudera Pasai (sultanate) — year_end: AtlasPI=1521 vs Wikidata=1267 (**Δ=254y**, HIGH). Ref: [Q3284315](https://www.wikidata.org/wiki/Q3284315) Samudra Pasai
38. **[366]** Sugbu (kingdom) — year_start: AtlasPI=1200 vs Wikidata=1450 (**Δ=250y**, HIGH). Ref: [Q4401071](https://www.wikidata.org/wiki/Q4401071) Rajahnate of Cebu
39. **[373]** ละโว้ (kingdom) — year_start: AtlasPI=450 vs Wikidata=700 (**Δ=250y**, HIGH). Ref: [Q1332305](https://www.wikidata.org/wiki/Q1332305) Lavo Kingdom
40. **[68]** Erzherzogtum Oesterreich (empire) — year_start: AtlasPI=1282 vs Wikidata=1526 (**Δ=244y**, HIGH). Ref: [Q153136](https://www.wikidata.org/wiki/Q153136) Habsburg monarchy
41. **[703]** Rajahnate of Maynila (city-state) — year_start: AtlasPI=1258 vs Wikidata=1500 (**Δ=242y**, HIGH). Ref: [Q4401247](https://www.wikidata.org/wiki/Q4401247) Maynila
42. **[50]** Campā — capital coord Δ=239.2km (AtlasPI={'lat': 15.937, 'lon': 108.277}, Wikidata={'lat': 13.92869, 'lon': 109.07507, 'qid': 'Q7929221'}). Ref: [Q216786](https://www.wikidata.org/wiki/Q216786) Champa
43. **[114]** कुषाण साम्राज्य — capital coord Δ=233.6km (AtlasPI={'lat': 34.0151, 'lon': 71.5249}, Wikidata={'lat': 34.93333333333333, 'lon': 69.23333333333333, 'qid': 'Q814388'}). Ref: [Q25979](https://www.wikidata.org/wiki/Q25979) Kushan Empire
44. **[864]** 林邑 — capital coord Δ=229.9km (AtlasPI={'lat': 15.82, 'lon': 108.21}, Wikidata={'lat': 13.92869, 'lon': 109.07507, 'qid': 'Q7929221'}). Ref: [Q216786](https://www.wikidata.org/wiki/Q216786) Champa
45. **[533]** Mosquitia — capital coord Δ=229.8km (AtlasPI={'lat': 14.04, 'lon': -83.35}, Wikidata={'lat': 12.013125, 'lon': -83.7649111111111, 'qid': 'Q885996'}). Ref: [Q6037274](https://www.wikidata.org/wiki/Q6037274) Mosquitia
46. **[167]** Kaabu — capital coord Δ=227.5km (AtlasPI={'lat': 12.35, 'lon': -14.15}, Wikidata={'lat': 13.216666666667, 'lon': -16.05, 'qid': 'Q1435754'}). Ref: [Q862478](https://www.wikidata.org/wiki/Q862478) Kaabu
47. **[135]** चालुक्य — capital coord Δ=211.9km (AtlasPI={'lat': 15.9196, 'lon': 75.6836}, Wikidata={'lat': 17.195, 'lon': 77.160833333333, 'qid': 'Q191771'}). Ref: [Q1395011](https://www.wikidata.org/wiki/Q1395011) Chalukya dynasty
48. **[270]** ממלכת ישראל (kingdom) — year_end: AtlasPI=-720 vs Wikidata=-930 (**Δ=210y**, HIGH). Ref: [Q3185305](https://www.wikidata.org/wiki/Q3185305) Kingdom of Israel
49. **[376]** சேர நாடு — capital coord Δ=209.5km (AtlasPI={'lat': 10.52, 'lon': 76.21}, Wikidata={'lat': 10.96, 'lon': 78.075, 'qid': 'Q817218'}). Ref: [Q877155](https://www.wikidata.org/wiki/Q877155) Chera dynasty
50. **[429]** Livonijas konfederacija (confederation) — year_start: AtlasPI=1228 vs Wikidata=1435 (**Δ=207y**, HIGH). Ref: [Q1064825](https://www.wikidata.org/wiki/Q1064825) Livonian confederation

## MED drift (270 totali, mostro primi 30)

1. **[608]** ᠴᠠᠭᠠᠲᠠᠶ ᠬᠠᠭᠠᠨᠠᠲ — capital coord Δ=159.8km. [Q1191125]
2. **[132]** राष्ट्रकूट — capital coord Δ=144.1km. [Q856691]
3. **[159]** Moose — capital coord Δ=141.4km. [Q862522]
4. **[896]** قۇچۇ — capital coord Δ=139.8km. [Q2662180]
5. **[328]** چغتای خانات — capital coord Δ=127.1km. [Q487829]
6. **[339]** مغولستان — capital coord Δ=127.1km. [Q1191125]
7. **[332]** Сибир ханлыгы — capital coord Δ=125.5km. [Q190513]
8. **[978]** Gobir — capital coord Δ=118.9km. [Q1533541]
9. **[460]** 後金 — capital coord Δ=117.9km. [Q1062546]
10. **[151]** Ọyọ́ — capital coord Δ=117.5km. [Q849623]
11. **[142]** මහා විජයබාහු — capital coord Δ=116.1km. [Q1530762]
12. **[73]** Corona de Castilla — capital coord Δ=114.2km. [Q179293]
13. **[851]** Oyo — capital coord Δ=111.9km. [Q849623]
14. **[880]** Nhà Hồ — capital coord Δ=90.3km. [Q1209047]
15. **[468]** 後趙 — capital coord Δ=88.8km. [Q2314907]
16. **[110]** சோழ நாடு — capital coord Δ=87.8km. [Q151148]
17. **[729]** Wasulu — capital coord Δ=85.2km. [Q568712]
18. **[730]** Fuuta Tooro — capital coord Δ=82.8km. [Q536476]
19. **[744]** Bamana ka Faama — capital coord Δ=82.8km. [Q762084]
20. **[371]** Nhà Lê — capital coord Δ=79.9km. [Q878276]
21. **[588]** ಪಶ್ಚಿಮ ಚಾಳುಕ್ಯ — capital coord Δ=78.8km. [Q14624218]
22. **[496]** بنو زيري — capital coord Δ=75.5km. [Q205718]
23. **[600]** ការ្យ​ ​សីលេន — capital coord Δ=69.0km. [Q1589163]
24. **[18]** Manden Kurufaba — capital coord Δ=67.7km. [Q184536]
25. **[554]** Faama-dugu — capital coord Δ=64.9km. [Q762084]
26. **[594]** पेशवाई — capital coord Δ=53.7km. [Q83618]
27. **[137]** ئۇيغۇر خانلىقى — capital coord Δ=53.2km. [Q831218]
28. **[296]** 吐谷浑 — capital coord Δ=53.0km. [Q1196201]
29. **[425]** Nafarroako Erresuma — capital coord Δ=50.7km. [Q63021609]
30. **[270]** ממלכת ישראל — capital coord Δ=50.3km. [Q3185305]

## Pattern systemici

- **year_start bias**: media Δ = 18.4y (44 AtlasPI>Wikidata, 49 AtlasPI<Wikidata) su 93 diff
- **year_end bias**: media Δ = -47.9y (20 AtlasPI>Wikidata, 27 AtlasPI<Wikidata) su 47 diff

## Note importanti

- **Convention BCE**: Wikidata usa astronomical numbering, AtlasPI usa convention storica. Per date BCE può esserci offset sistematico ±1y.
- **AtlasPI boundary_geojson null + Wikidata P625**: entità con capitale in AtlasPI ma senza boundary potrebbero essere backfillate via Wikidata. Vedi fase_b_drift_data.json filtrando per field='capital' note='backfill'.
- **Capitali multiple**: P36 in Wikidata può avere multiple capitali (storico successivo/precedente). Il drift è riportato sul match più vicino.
