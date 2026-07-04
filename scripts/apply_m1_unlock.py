"""M1 (v6.99.120) — genera il dual-write per le 11 entità-sblocco + catene.

Input:  data/enrichment/m1_unlock_research_20260704.json — output verificato
        del workflow di ricerca (11 record: ricerca + verdetto avversariale;
        vedi docs/ethics/ETHICS-020).
Output: data/entities/batch_37_m1_unlock.json      (11 entità nuove)
        data/chains/batch_37_m1_unlock.json        (3 catene nuove)
        chirurgia su data/chains/batch_35_class1_asia_pacific.json (4 catene),
                     data/chains/batch_20_balkan.json (catena serba #34),
                     data/chains/batch_36_class1_atlantic_europe.json (#130)
        scripts/sql_m1_unlock_entities.sql          (prod, transazionale)

Idempotenza: la chirurgia asserisce exactly-once sui frammenti vecchi; una
seconda esecuzione fallisce pulita. ETHICS: le correzioni del cross-check
(ChatGPT + verificatori) sono applicate qui, documentate in ETHICS-020.

Usage: PYTHONUTF8=1 python -m scripts.apply_m1_unlock
"""
from __future__ import annotations

import json
from pathlib import Path

RESEARCH = Path("data/enrichment/m1_unlock_research_20260704.json")
ENT_OUT = Path("data/entities/batch_37_m1_unlock.json")
CHAINS_OUT = Path("data/chains/batch_37_m1_unlock.json")
SQL_OUT = Path("scripts/sql_m1_unlock_entities.sql")

# ── nomi entità esistenti referenziate (devono risolvere in JSON-land) ──
# NB (scoperte in corso d'opera, vedi ETHICS-020 §"già esistenti"):
# - Taqali, Mahdiyya e Medri Bahri sono rename nativi prod-only (M4): il
#   JSON-land li conosce come 'Taqali' / 'Dawla al-Mahdiyya' / 'Medri Bahri',
#   prod come 'مملكة تقلي' #411 / 'الدولة المهدية' #736 / 'ምድረ ባሕሪ' #658.
# - Lan Xang ESISTEVA GIÀ (#128) con nome in script THAI ล้านช้าง e lang 'lo'
#   (mismatch): qui viene RINOMINATO alla forma lao attestata ອານາຈັກລ້ານຊ້າງ
#   (pattern Wadai v6.99.110), non creato.
# I link JSON usano il nome JSON-land (per il fresh-seed); l'SQL usa gli ID
# prod noti (PROD_IDS).
LAN_XANG_NEW = "ອານາຈັກລ້ານຊ້າງ"
EXISTING = {
    "khmer_empire": "អាណាចក្រខ្មែរ",
    "vientiane": "ອານາຈັກວຽງຈັນ",
    "luang_prabang": "ອານາຈັກຫລວງພະບາງ",
    "champasak": "ອານາຈັກຈຳປາສັກ",
    "sfrj": "Социјалистичка Федеративна Република Југославија",
    "saudi": "المملكة العربية السعودية",
    "gorkha": "गोर्खा राज्य",
    "taqali": "Taqali",
    "mahdiyya": "Dawla al-Mahdiyya",
    "lan_xang": LAN_XANG_NEW,  # post-rename batch_02
}

# id prod delle entità esistenti (per gli INSERT chain_links via SQL)
PROD_IDS = {
    "អាណាចក្រខ្មែរ": 19,
    "ອານາຈັກວຽງຈັນ": 693,
    "ອານາຈັກຫລວງພະບາງ": 364,
    "ອານາຈັກຈຳປາສັກ": 363,
    "Социјалистичка Федеративна Република Југославија": 231,
    "المملكة العربية السعودية": 253,
    "गोर्खा राज्य": 399,
    "Taqali": 411,
    "Dawla al-Mahdiyya": 736,
    LAN_XANG_NEW: 128,
}


def q(s: str | None) -> str:
    """SQL string literal (o NULL)."""
    if s is None:
        return "NULL"
    return "'" + s.replace("'", "''") + "'"


def qn(v) -> str:
    return "NULL" if v is None else str(v)


def load_research() -> dict[str, dict]:
    data = json.loads(RESEARCH.read_text(encoding="utf-8"))
    return {item["key"]: item["record"] for item in data}


def apply_corrections(recs: dict[str, dict]) -> None:
    """Correzioni dai verdetti avversariali + cross-check (ETHICS-020)."""
    # nepal: attribuzione morti Terai 2015 (verificatore: il 50+ è il totale
    # complessivo, non 'uccisi dalla polizia'); drop tc 2015 (atto
    # costituzionale interno, non cambio territoriale).
    nep = recs["nepal_republic"]
    old = "police killed more than 50 Madhesi and Tharu protesters in the Terai (Human Rights Watch documented excessive and unnecessary lethal force; no senior official held accountable)"
    new = ("more than 50 people died in the Terai unrest overall (Aug 2015-Feb 2016) - protesters, mostly Madhesi and Tharu, killed by police, and at least 9 police killed by protesters; "
           "Human Rights Watch ('Like We Are Not Nepali', 2015) documented unlawful killings on both sides including excessive police force; no senior official held accountable")
    assert nep["ethical_notes"].count(old) == 1, "nepal notes target mancante"
    nep["ethical_notes"] = nep["ethical_notes"].replace(old, new)
    before = len(nep["territory_changes"])
    nep["territory_changes"] = [tc for tc in nep["territory_changes"] if tc["year"] != 2015]
    assert len(nep["territory_changes"]) == before - 1

    # medri_bahri: data Gallabat 9-10 marzo 1889 (non 10-11)
    mb = recs["medri_bahri"]
    fixed = 0
    for tc in mb["territory_changes"]:
        if "10-11 March 1889" in tc["description"]:
            tc["description"] = tc["description"].replace("10-11 March 1889", "9-10 March 1889")
            fixed += 1
    assert fixed >= 1, "medri_bahri Gallabat fix non applicato"

    # serbia: firmano 1867 = 4 fortezze; esodo 1862 ~10k dalle sei città
    # di guarnigione (di cui ~2.100 da Belgrado), non ~8k dalla sola Belgrado
    srb = recs["serbia_1815_1918"]
    srb["name_original_lang"] = "sr"  # convenzione DB (peer #95/#231/#435)
    for tc in srb["territory_changes"]:
        if tc["year"] == 1867:
            tc["region"] = "Fortresses of Belgrade, Sabac, Smederevo, Kladovo"
            if "Uzice" in tc["description"] and "1862" not in tc["description"]:
                tc["description"] += " (The Uzice and Soko garrisons had already departed in 1862, after the Kanlica conference.)"
    old62 = "~8,000 Muslims left Belgrade within a year"
    new62 = "roughly 10,000 Muslims left the six Serbian garrison towns in the 1862-1867 wave (about 2,100 of them from Belgrade)"
    n = srb["ethical_notes"].count(old62)
    for tc in srb["territory_changes"]:
        if old62 in tc["description"]:
            tc["description"] = tc["description"].replace(old62, new62)
            n += 1
    assert n >= 1, "serbia 1862 fix non applicato"
    srb["ethical_notes"] = srb["ethical_notes"].replace(old62, new62)


def validate_boundary(key: str, rec: dict) -> None:
    g = rec["boundary_geojson"]
    assert g["type"] in ("Polygon", "MultiPolygon"), key
    rings = g["coordinates"] if g["type"] == "Polygon" else [r for poly in g["coordinates"] for r in poly]
    for ring in rings:
        if ring[0] != ring[-1]:
            ring.append(list(ring[0]))  # chiudi il ring (GeoJSON RFC 7946)
        lons = [p[0] for p in ring]
        assert max(lons) - min(lons) < 180, f"{key}: polygon crosses antimeridian!"
        assert len(ring) >= 4, key
    try:
        from shapely.geometry import shape
        shp = shape(g)
        assert shp.is_valid, f"{key}: invalid geometry"
        assert shp.area > 0.01, f"{key}: degenerate polygon"
    except ImportError:
        pass


# 8 entità NUOVE. lan_xang (#128), mahdist_state (#736) e medri_bahri (#658)
# esistevano già su prod — la loro ricerca resta nel file committato come
# materiale di enrichment (coda M4), vedi ETHICS-020.
ENTITY_KEYS = [
    "cambodia_post_angkor", "khmer_republic",
    "serbia_1815_1918", "kingdom_shs_yugoslavia",
    "diriyah_emirate", "najd_emirate", "nepal_republic",
    "ndebele_kingdom",
]


def build_entity_json(rec: dict) -> dict:
    out = {
        "name_original": rec["name_original"],
        "name_original_lang": rec["name_original_lang"],
        "entity_type": rec["entity_type"],
        "year_start": rec["year_start"],
        "year_end": rec.get("year_end"),
        "capital_name": rec["capital_name"],
        "capital_lat": rec["capital_lat"],
        "capital_lon": rec["capital_lon"],
        "confidence_score": rec["confidence_score"],
        "status": "confirmed",
        "boundary_geojson": rec["boundary_geojson"],
        "boundary_source": "historical_approximation",
        "ethical_notes": rec["ethical_notes"],
        # NB: il seed non mappa wikidata_qid (debito M4) — documentato qui
        # e applicato su prod via SQL.
        "wikidata_qid": rec.get("wikidata_qid"),
        "name_variants": rec["name_variants"],
        "territory_changes": [
            {k: tc.get(k) for k in ("year", "region", "change_type", "description", "population_affected", "confidence_score") if k in tc or k == "population_affected"}
            for tc in rec["territory_changes"]
        ],
        "sources": rec["sources"],
    }
    return out


# ── 3 catene NUOVE ────────────────────────────────────────────────────
def build_new_chains(recs: dict[str, dict]) -> list[dict]:
    dir_name = recs["diriyah_emirate"]["name_original"]
    najd_name = recs["najd_emirate"]["name_original"]
    nep_name = recs["nepal_republic"]["name_original"]
    mah_name = EXISTING["mahdiyya"]  # JSON-land (prod #736 = 'الدولة المهدية')
    return [
        {
            "name": "Saudi dynastic states: إمارة الدرعية → إمارة نجد → المملكة العربية السعودية",
            "name_lang": "en",
            "chain_type": "DYNASTY",
            "region": "Arabian Peninsula / Najd",
            "description": "The three Saudi-Wahhabi states of the Al Saud: the Emirate of Diriyah (1744-1818, destroyed by the Ottoman-Egyptian expedition), the Emirate of Najd (1824-1891, ended by the Rashidi conquest at Mulayda), and the Kingdom of Saudi Arabia (proclaimed 1932 after Ibn Saud's 1902-1932 reconquest and unification).",
            "confidence_score": 0.8,
            "ethical_notes": "ETHICS-002: every transition in this chain is violent and is recorded as such. The chain is DYNASTIC (same Al Saud house), not an unbroken state: two interregna (1818-1824 under Egyptian occupation after Ibrahim Pasha razed Diriyah and had Imam Abdullah bin Saud executed; 1891-1902 under Rashidi rule with the Al Saud exiled in Kuwait) are documented on the links, not papered over. The third state's unification was by conquest: Riyadh 1902, Ha'il 1921, the Hejaz 1924-25 (including the Ta'if massacre of 1924, ~300-400 civilians killed by the Ikhwan) - per the cross-check, the 1932 transition is typed UNIFICATION (conquest-built), not 'restoration'. The state-sponsored 2022 re-dating of the first state's founding to 1727 is treated as politicized periodization (see the Diriyah entity record).",
            "sources": [
                {"citation": "Madawi Al-Rasheed, A History of Saudi Arabia, Cambridge University Press, 2002 (2nd ed. 2010)", "url": None, "source_type": "academic"},
                {"citation": "Alexei Vassiliev, The History of Saudi Arabia, Saqi Books, 1998", "url": None, "source_type": "academic"},
                {"citation": "R. Bayly Winder, Saudi Arabia in the Nineteenth Century, Macmillan, 1965", "url": None, "source_type": "academic"},
            ],
            "links": [
                {"entity_name": dir_name, "transition_year": None, "transition_type": None, "is_violent": False,
                 "description": "The first Saudi state: the 1744 pact between Muhammad ibn Saud and Muhammad ibn Abd al-Wahhab turned the Diriyah town emirate into an expansionist religious-political state that conquered Najd, al-Hasa and the Hejaz.",
                 "ethical_notes": None},
                {"entity_name": najd_name, "transition_year": 1824, "transition_type": "RESTORATION", "is_violent": True,
                 "description": "Al Saud restoration after a six-year interregnum (1818-1824): Ibrahim Pasha's Ottoman-Egyptian army had razed Diriyah (1818) and executed Imam Abdullah bin Saud in Istanbul; in 1824 Turki ibn Abdullah retook Riyadh from the Egyptian garrison by siege and made it the new capital.",
                 "ethical_notes": "The 1818-1824 gap (Egyptian occupation, failed risings of Mishari bin Saud 1819-20 and Turki 1821-23) is real and documented - the chain records a dynastic restoration, not state continuity."},
                {"entity_name": EXISTING["saudi"], "transition_year": 1932, "transition_type": "UNIFICATION", "is_violent": True,
                 "description": "After the Rashidi conquest of Najd (Mulayda 1891) and Al Saud exile in Kuwait, Abdulaziz Ibn Saud retook Riyadh in 1902 and unified the peninsula by conquest over three decades: Ha'il and the Rashidi emirate (1921), the Hejaz (1924-25), proclamation of the Kingdom of Saudi Arabia on 23 September 1932.",
                 "ethical_notes": "Typed UNIFICATION (not 'restoration') per cross-check: the third state was conquest-built. The conquest of the Hejaz included the Ta'if massacre (September 1924, ~300-400 civilians killed by the Ikhwan); the Ikhwan themselves were crushed by Ibn Saud at Sabilla (1929) when they pressed to continue raiding."},
            ],
        },
        {
            "name": "Nepalese state: गोर्खा राज्य → सङ्घीय लोकतान्त्रिक गणतन्त्र नेपाल",
            "name_lang": "en",
            "chain_type": "SUCCESSION",
            "region": "South Asia / Himalaya",
            "description": "The Nepalese state from the Gorkha conquest-founded Shah kingdom (1768) to the Federal Democratic Republic declared on 28 May 2008 by the 1st Constituent Assembly, which abolished the 240-year monarchy.",
            "confidence_score": 0.9,
            "ethical_notes": "ETHICS-002: the 2008 transition is typed REVOLUTION with is_violent=true - the abolition vote itself (560-4) was peaceful and King Gyanendra left the palace without resistance, but the republic was the direct outcome of the 1996-2006 civil war (~13,000 deaths documented by OHCHR, Nepali government figures to ~17,000; the majority of documented killings attributed to state security forces per INSEC) and of the April 2006 Jana Andolan II uprising (~18-25 protesters killed by royal security forces). Marking it non-violent would erase the war that produced it.",
            "sources": [
                {"citation": "John Whelpton, A History of Nepal, Cambridge University Press, 2005", "url": None, "source_type": "academic"},
                {"citation": "OHCHR, Nepal Conflict Report, 2012", "url": "https://www.ohchr.org/en/documents/reports/nepal-conflict-report", "source_type": "primary"},
                {"citation": "Sebastian von Einsiedel, David M. Malone, Suman Pradhan (eds.), Nepal in Transition: From People's War to Fragile Peace, Cambridge University Press, 2012", "url": None, "source_type": "academic"},
            ],
            "links": [
                {"entity_name": EXISTING["gorkha"], "transition_year": None, "transition_type": None, "is_violent": False,
                 "description": "The Shah kingdom founded by Prithvi Narayan Shah's conquest of the Kathmandu valley (1768-69), expanded through the Anglo-Nepalese war (1814-16, Sugauli treaty), ruled 1846-1951 by the hereditary Rana premiership, and ended by the 2006-08 peace process.",
                 "ethical_notes": None},
                {"entity_name": nep_name, "transition_year": 2008, "transition_type": "REVOLUTION", "is_violent": True,
                 "description": "On 28 May 2008 the newly elected Constituent Assembly abolished the monarchy (560-4) and declared a federal democratic republic; Gyanendra Shah left Narayanhiti palace peacefully on 11 June 2008.",
                 "ethical_notes": "is_violent=true refers to the revolutionary process (1996-2006 people's war, ~13,000-17,000 dead; 2006 Jana Andolan II), not to the final vote, which was peaceful - see chain-level note."},
            ],
        },
        {
            "name": "Taqali and the Mahdiyya: مملكة تقلي → الدولة المهدية",
            "name_lang": "en",
            "chain_type": "SUCCESSION",
            "region": "Northeast Africa / Sudan (Nuba mountains)",
            "description": "The Nuba-mountains kingdom of Taqali, independent for over three centuries, conquered by the Mahdist state: invaded from 1883, its ruler Makk Adam captured in July 1884 (he died in Mahdist captivity); the Mahdiyya itself was destroyed by the British-led Anglo-Egyptian reconquest in 1898-99.",
            "confidence_score": 0.7,
            "ethical_notes": "ETHICS-002: the transition is a violent conquest and is recorded as such. Taqali's resistance in the hills was never fully broken - Mahdist control of the Nuba mountains remained contested, and a Taqali lineage re-emerged as a client under the Anglo-Egyptian Condominium; the chain records the 1884 destruction of the independent kingdom, not a total erasure of the Taqali polity's people. The successor's own end (Omdurman 1898, ~10,000-12,000 Sudanese dead to Maxim guns and artillery against 48 British-led casualties; Condominium agreement 1899) is colonial violence, perpetrator named on the Mahdist entity record.",
            "sources": [
                {"citation": "Janet J. Ewald, Soldiers, Traders, and Slaves: State Formation and Economic Transformation in the Greater Nile Valley, 1700-1885, University of Wisconsin Press, 1990", "url": None, "source_type": "academic"},
                {"citation": "P. M. Holt, The Mahdist State in the Sudan, 1881-1898, 2nd ed., Clarendon Press, 1970", "url": None, "source_type": "academic"},
            ],
            "links": [
                {"entity_name": EXISTING["taqali"], "transition_year": None, "transition_type": None, "is_violent": False,
                 "description": "The kingdom of Taqali in the Nuba mountains (from ~1570), a hill state that preserved independence from Sennar and from Turco-Egyptian Sudan through tribute diplomacy and mountain warfare.",
                 "ethical_notes": None},
                {"entity_name": mah_name, "transition_year": 1884, "transition_type": "CONQUEST", "is_violent": True,
                 "description": "Mahdist forces invaded Taqali from 1883; Makk Adam was captured in July 1884 and died in Mahdist captivity. Resistance in the hills continued through the Mahdist period.",
                 "ethical_notes": "Violent conquest, perpetrator named (Mahdist state). Taqali's entity record ends 1884 with this conquest."},
            ],
        },
    ]


# ── chirurgia catene esistenti ───────────────────────────────────────
def chain_surgery(recs: dict[str, dict]) -> None:
    lx = LAN_XANG_NEW
    pa = recs["cambodia_post_angkor"]["name_original"]  # កម្ពុជា (Longvek-Oudong)
    srb = recs["serbia_1815_1918"]["name_original"]  # Кнежевина Србија
    shs = recs["kingdom_shs_yugoslavia"]["name_original"]  # Краљевина СХС

    def lx_link(desc: str) -> str:
        return ('{"entity_name": "' + lx + '", "transition_year": null, "transition_type": null, "is_violent": false, '
                '"description": "' + desc + '", "ethical_notes": null},\n      ')

    LX_DESC = ("Lan Xang (1354-1707), the unified Lao kingdom of the middle Mekong founded by Fa Ngum with Khmer military backing; "
               "capitals Luang Prabang (1354-1560) and Vientiane (1560-1707); partitioned in 1707 after the succession crisis that followed Sourigna Vongsa's death (1694).")

    edits: list[tuple[str, list[tuple[str, str]]]] = []

    # batch_02 (CRLF) — rename nativo #128: ล้านช้าง (thai) → ອານາຈັກລ້ານຊ້າງ (lao)
    # Pattern Wadai (ETHICS-001, v6.99.110): la forma thai resta come variante.
    edits.append(("data/entities/batch_02_asia.json", [
        ('"name_original": "ล้านช้าง",', '"name_original": "ອານາຈັກລ້ານຊ້າງ",'),
        ('"name_variants": [\r\n      {\r\n        "name": "Lan Xang",\r\n        "lang": "en",\r\n        "period_start": 1354,\r\n        "period_end": 1707,\r\n        "context": "denominazione romanizzata standard",\r\n        "source": "Stuart-Fox, The Lao Kingdom of Lan Xang (1998)"\r\n      },',
         '"name_variants": [\r\n      {\r\n        "name": "Lan Xang",\r\n        "lang": "en",\r\n        "period_start": 1354,\r\n        "period_end": 1707,\r\n        "context": "denominazione romanizzata standard",\r\n        "source": "Stuart-Fox, The Lao Kingdom of Lan Xang (1998)"\r\n      },\r\n      {\r\n        "name": "ล้านช้าง",\r\n        "lang": "th",\r\n        "period_start": 1354,\r\n        "period_end": 1707,\r\n        "context": "forma in script thai (era erroneamente il nome primario con lang=lo fino al rename ETHICS-001 in v6.99.120 — la forma lao attestata è ອານາຈັກລ້ານຊ້າງ, cfr. Wikidata Q853477)",\r\n        "source": "storiografia thai; ETHICS-020"\r\n      },\r\n      {\r\n        "name": "ລ້ານຊ້າງຮົ່ມຂາວ (Lan Xang Hom Khao)",\r\n        "lang": "lo",\r\n        "period_start": 1354,\r\n        "period_end": 1707,\r\n        "context": "nome cerimoniale completo attestato dato da Fa Ngum: \'Milione di elefanti e parasole bianco\'",\r\n        "source": "Cronache lao (Nithan Khun Borom); Stuart-Fox 1998"\r\n      },'),
    ]))

    # batch_35 (LF) — 4 catene
    edits.append(("data/chains/batch_35_class1_asia_pacific.json", [
        # — Vientiane 123 —
        ('"Lan Xang partition — Vientiane line: ອານາຈັກວຽງຈັນ → Siam"',
         '"Lan Xang partition — Vientiane line: ອານາຈັກລ້ານຊ້າງ → ອານາຈັກວຽງຈັນ → Siam"'),
        ('PREDECESSOR NOTE: Lan Xang (1354-1707), the unified Lao kingdom whose 1707 partition created Vientiane, Luang Prabang and Champasak, is NOT yet an entity in this dataset — its creation is queued; until then the three partition chains start at the successor kingdoms.',
         'PREDECESSOR: Lan Xang (1354-1707) was added as an entity in v6.99.120 (ETHICS-020) and now heads the three partition chains; the 1707 division was a negotiated/de facto partition after an armed standoff, not a battlefield conquest.'),
        ('"links": [\n      {"entity_name": "ອານາຈັກວຽງຈັນ", "transition_year": null, "transition_type": null, "is_violent": false, "description": "The kingdom of Vientiane, created in the 1707 partition of Lan Xang; a Siamese vassal after 1779, its last king Chao Anouvong (r. 1805-1828) attempted to restore Lao independence and recreate Lan Xang.", "ethical_notes": "See chain-level note: the Lan Xang predecessor entity does not yet exist."},',
         '"links": [\n      ' + lx_link(LX_DESC) + '{"entity_name": "ອານາຈັກວຽງຈັນ", "transition_year": 1707, "transition_type": "PARTITION", "is_violent": false, "description": "The kingdom of Vientiane, created in the 1707 partition of Lan Xang; a Siamese vassal after 1779, its last king Chao Anouvong (r. 1805-1828) attempted to restore Lao independence and recreate Lan Xang.", "ethical_notes": "The 1707 partition was a negotiated division between Kingkitsarat (Luang Prabang) and Sai Ong Hue (Vientiane) after an armed standoff."},'),
        # — Luang Prabang 124 —
        ('"Lan Xang partition — Luang Prabang line: ອານາຈັກຫລວງພະບາງ → French Indochina"',
         '"Lan Xang partition — Luang Prabang line: ອານາຈັກລ້ານຊ້າງ → ອານາຈັກຫລວງພະບາງ → French Indochina"'),
        ('"links": [\n      {"entity_name": "ອານາຈັກຫລວງພະບາງ", "transition_year": null, "transition_type": null, "is_violent": false, "description": "The kingdom of Luang Prabang, created in the 1707 partition of Lan Xang; tributary to Siam (and at times Vietnam and China) through the 18th-19th centuries; sacked by Black Flag raiders in 1887.", "ethical_notes": "See the Vientiane-line chain for the missing Lan Xang predecessor entity (queued)."},',
         '"links": [\n      ' + lx_link(LX_DESC) + '{"entity_name": "ອານາຈັກຫລວງພະບາງ", "transition_year": 1707, "transition_type": "PARTITION", "is_violent": false, "description": "The kingdom of Luang Prabang, created in the 1707 partition of Lan Xang; tributary to Siam (and at times Vietnam and China) through the 18th-19th centuries; sacked by Black Flag raiders in 1887.", "ethical_notes": "Northern successor of the 1707 partition, under Kingkitsarat (crowned rival king at Luang Prabang in 1705)."},'),
        # — Champasak 125 —
        ('"Lan Xang partition — Champasak line: ອານາຈັກຈຳປາສັກ → French Indochina"',
         '"Lan Xang partition — Champasak line: ອານາຈັກລ້ານຊ້າງ → ອານາຈັກຈຳປາສັກ → French Indochina"'),
        ('"links": [\n      {"entity_name": "ອານາຈັກຈຳປາສັກ", "transition_year": null, "transition_type": null, "is_violent": false, "description": "The kingdom of Champasak on the lower Mekong, created in the 1713 completion of the Lan Xang partition under Nokasad; a Siamese vassal from 1778; joined Anouvong\'s war (1826-28) and was reduced to a Siamese-appointed governorship in its aftermath.", "ethical_notes": null},',
         '"links": [\n      ' + lx_link(LX_DESC) + '{"entity_name": "ອານາຈັກຈຳປາສັກ", "transition_year": 1713, "transition_type": "PARTITION", "is_violent": false, "description": "The kingdom of Champasak on the lower Mekong, created in the 1713 completion of the Lan Xang partition under Nokasad; a Siamese vassal from 1778; joined Anouvong\'s war (1826-28) and was reduced to a Siamese-appointed governorship in its aftermath.", "ethical_notes": "Champasak separated from the Vientiane sphere in 1713 after a southern secession, completing the three-way division of Lan Xang."},'),
        # — Cambodian state 126 —
        ('"Cambodian state: Indochine française → Kingdom of Cambodia"',
         '"Cambodian state: អាណាចក្រខ្មែរ → កម្ពុជា (Longvek-Oudong) → Indochine française → Kingdom of Cambodia"'),
        ('DELIBERATELY SHORT CHAIN (see ETHICS-017 §4): the Khmer lineage behind modern Cambodia runs Funan → Chenla → Khmer Empire (see the existing Thai/Khmer trunk chain) and then through the post-Angkor Kingdom of Cambodia (Longvek/Oudong, 1431-1863, squeezed between Siamese and Vietnamese suzerainty) — but that post-Angkor kingdom is NOT yet an entity in this dataset, and linking the Khmer EMPIRE (ended 1431) directly to French Indochina (born 1887) would assert a false 432-year succession jump. The missing entity is queued; when created, this chain should be extended backwards.',
         'EXTENDED BACKWARDS in v6.99.120 (ETHICS-020): the post-Angkor Kingdom of Cambodia (Longvek/Oudong, 1431-1863) now exists as an entity, closing the 432-year gap that kept this chain deliberately short (ETHICS-017 §4). The chain now runs Khmer Empire → post-Angkor Cambodia → French Indochina → Kingdom of Cambodia; the deeper lineage (Funan → Chenla → Khmer Empire) remains on the Thai/Khmer trunk chain. The FORWARD extension (1970 Khmer Republic → 1975-79 Democratic Kampuchea → PRK → 1993 restoration) is deliberately NOT chained: the PRK (1979-89) entity is still missing and a chain ending at the genocide regime would misrepresent; the interruption regimes exist as entities (សាធារណរដ្ឋខ្មែរ 1970-75, កម្ពុជាប្រជាធិបតេយ្យ 1975-79) and are documented in the successor entity notes.',
        ),
        ('"links": [\n      {"entity_name": "Indochine francaise", "transition_year": null, "transition_type": null, "is_violent": false, "description": "French colonial rule over Cambodia: protectorate treaty imposed on King Norodom on 11 August 1863, tightened by the 1884 convention (provoking the 1884-86 rising, repressed), folded into the Indochinese Union at its creation in 1887.",',
         '"links": [\n      {"entity_name": "អាណាចក្រខ្មែរ", "transition_year": null, "transition_type": null, "is_violent": false, "description": "The Khmer Empire (802-1431), the Angkorian state whose capital Yasodharapura was the region\'s hegemon for six centuries.", "ethical_notes": "Also heads the Thai/Khmer Southeast Asian trunk chain; both successions are real (Ayutthaya absorbed much of the empire\'s west; the Khmer royal line continued south-east)."},\n      {"entity_name": "កម្ពុជា (Longvek-Oudong)", "transition_year": 1431, "transition_type": "SUCCESSION", "is_violent": true, "description": "After Ayutthaya sacked Yasodharapura/Angkor (~1431), the Khmer court relocated south-east (Chaktomuk, then Longvek, then Oudong): the same royal polity relocated, not a new state - typed SUCCESSION with is_violent=true because the trigger was the Ayutthayan conquest.", "ethical_notes": "Perpetrator of the 1431 sack named: Ayutthaya (Siam). Longvek fell to Naresuan of Ayutthaya on 3 January 1594 with mass deportations - see the entity record."},\n      {"entity_name": "Indochine francaise", "transition_year": 1863, "transition_type": "ANNEXATION", "is_violent": false, "description": "French colonial rule over Cambodia: protectorate treaty imposed on King Norodom on 11 August 1863, tightened by the 1884 convention (provoking the 1884-86 rising, repressed), folded into the Indochinese Union at its creation in 1887.",'),
    ]))

    # batch_20 (CRLF) — catena serba 34
    OTTOMAN_TAIL = ('"ethical_notes": "The Great Migrations of Serbs (1690, 1739) into Habsburg territory reshaped the ethnic map of the Balkans and are often cited in modern Serbian-Croatian disputes."\r\n'
                    '      }\r\n'
                    '    ]')
    def link20(name: str, year, ttype: str, violent: bool, desc: str, ethics: str | None) -> str:
        e = 'null' if ethics is None else json.dumps(ethics, ensure_ascii=False)
        return ('      {\r\n'
                f'        "entity_name": {json.dumps(name, ensure_ascii=False)},\r\n'
                f'        "transition_year": {year},\r\n'
                f'        "transition_type": "{ttype}",\r\n'
                f'        "is_violent": {"true" if violent else "false"},\r\n'
                f'        "description": {json.dumps(desc, ensure_ascii=False)},\r\n'
                f'        "ethical_notes": {e}\r\n'
                '      }')
    new_links_34 = ",\r\n".join([
        link20(srb, 1815, "DECOLONIZATION", True,
               "Serbian self-rule re-emerged from the Ottoman Empire through the uprisings of 1804-1815: de facto autonomy from the Second Uprising settlement (1815), hereditary autonomous principality by hatt-i sharif (1830), full international independence at the Treaty of Berlin (1878), kingdom from 1882.",
               "The transition was a violent decolonization (two uprisings, 1804-13 and 1815). ETHICS-002: the consolidating Serbian state was also a perpetrator - the 1862-67 removal of the Muslim population from the garrison towns and the 1878 expulsions from the Nis/Toplica sanjaks (~49,000 Albanians among at least 71,000 Muslims) are recorded on the entity."),
        link20(shs, 1918, "UNIFICATION", False,
               "On 1 December 1918 the Kingdom of Serbia merged with the State of Slovenes, Croats and Serbs (and, via the contested Podgorica Assembly, with Montenegro) into the Kingdom of Serbs, Croats and Slovenes, renamed Yugoslavia in 1929.",
               "The Serbia-side unification was negotiated and peaceful; the Montenegrin absorption was contested and its aftermath violent (Christmas Uprising 1919) - see the Montenegrin chain, where that link is typed ANNEXATION."),
        link20(EXISTING["sfrj"], 1945, "REVOLUTION", True,
               "The Axis invasion (April 1941) destroyed the kingdom; after four years of occupation, partition, genocide (NDH camps, Jasenovac) and multi-sided war, the communist Partisans established the Federal People's Republic (AVNOJ 1943; monarchy abolished 29 November 1945).",
               "The 1941-45 period saw occupation, the Holocaust and the Ustasa genocide of Serbs, Roma and Jews, and civil war among resistance movements - the socialist state emerged from that violence, not from a peaceful succession."),
    ])
    edits.append(("data/chains/batch_20_balkan.json", [
        ('"name": "Serbian state trunk: Raska → Srpsko Carstvo → Српска деспотовина → Ottoman → Jugoslavija → Serbia"',
         '"name": "Serbian state trunk: Raska → Srpsko Carstvo → Српска деспотовина → Ottoman → Кнежевина Србија → Југославија (СХС → СФРЈ)"'),
        (OTTOMAN_TAIL,
         OTTOMAN_TAIL[:-len('\r\n      }\r\n    ]')] + '\r\n      },\r\n' + new_links_34 + '\r\n    ]'),
    ]))

    # batch_36 (LF) — catena montenegrina 130
    edits.append(("data/chains/batch_36_class1_atlantic_europe.json", [
        ('"Montenegrin state: Зета → Црна Гора"',
         '"Montenegrin state: Зета → Црна Гора → Краљевина СХС"'),
        ('TERMINAL EVENT NOT MODELLED AS A LINK (see ETHICS-017 §5): the chain ends in 1918 because no suitable successor entity exists in the dataset — the Kingdom of Serbs, Croats and Slovenes (1918-1929/41) is missing (queued; it is also needed by the Serbian trunk chain), and linking to socialist Yugoslavia (1945-) would be anachronistic.',
         'TERMINAL LINK ADDED in v6.99.120 (ETHICS-020): the Kingdom of Serbs, Croats and Slovenes now exists as an entity and the 1918 annexation is modelled as a chain link typed ANNEXATION, is_violent=true.'),
    ]))

    for relpath, pairs in edits:
        p = Path(relpath)
        raw = p.read_bytes().decode("utf-8")
        # newline-agnostic: git autocrlf può materializzare i file LF come
        # CRLF nel working tree — prova entrambe le forme dei frammenti.
        for old, new in pairs:
            lf_old, lf_new = old.replace("\r\n", "\n"), new.replace("\r\n", "\n")
            candidates = [
                (old, new),
                (lf_old, lf_new),
                (lf_old.replace("\n", "\r\n"), lf_new.replace("\n", "\r\n")),
            ]
            for o, nw in candidates:
                if raw.count(o) == 1:
                    raw = raw.replace(o, nw)
                    break
            else:
                counts = [raw.count(o) for o, _ in candidates]
                raise AssertionError(f"{relpath}: occorrenze {counts} (attesa 1): {old[:70]!r}")
        p.write_bytes(raw.encode("utf-8"))
        json.loads(raw)
        print(f"OK chirurgia {relpath}: {len(pairs)} edit")

    # append del link SHS alla catena 130 (dopo il link Црна Гора, one-line style)
    p = Path("data/chains/batch_36_class1_atlantic_europe.json")
    raw = p.read_bytes().decode("utf-8")
    i = raw.find('"Montenegrin state: Зета → Црна Гора → Краљевина СХС"')
    j = raw.find('"links": [', i)
    # trova la fine dell'array links: il primo "]<nl>  }" dopo j
    k = raw.find("]\n  }", j)
    if k < 0:
        k = raw.find("]\r\n  }", j)
    assert i > 0 and j > i and k > j
    shs_link = ('{"entity_name": ' + json.dumps(shs, ensure_ascii=False) + ', "transition_year": 1918, "transition_type": "ANNEXATION", "is_violent": true, '
                '"description": "With King Nikola I in exile and the country under Serbian military occupation, the Podgorica Assembly (24-29 November 1918), elected under conditions controlled by unionist forces, deposed the king and declared unconditional union with Serbia; the Greens\' Christmas Uprising (January 1919, Cetinje) was suppressed by the Serbian army and pro-union militias, with guerrilla resistance into the mid-1920s.", '
                '"ethical_notes": "Montenegrin historiography (Pavlović, \'Balkan Anschluss\') reads the union as annexation; Serbian unionist historiography as voluntary unification - both readings recorded, not arbitrated (no-single-version principle). Typed ANNEXATION with is_violent=true for the armed suppression that followed."}')
    # l'ultimo link prima di ] deve terminare con '}' — inserisci ',\n      <link>\n    '
    insert_at = raw.rfind("}", j, k) + 1
    nl = "\r\n" if "\r\n" in raw[j:k] else "\n"
    raw = raw[:insert_at] + "," + nl + "      " + shs_link + raw[insert_at:]
    p.write_bytes(raw.encode("utf-8"))
    json.loads(raw)
    print("OK chirurgia batch_36 append link SHS (catena 130)")


# ── SQL prod ─────────────────────────────────────────────────────────
def gen_sql(recs: dict[str, dict], new_chains: list[dict]) -> str:
    out: list[str] = []
    w = out.append
    w("-- v6.99.120 (M1/ETHICS-020) — 11 entità-sblocco + estensioni catene.")
    w("-- Generato da scripts/apply_m1_unlock.py — NON editare a mano.")
    w("-- Dual-write: JSON = data/entities/batch_37_m1_unlock.json + data/chains/*.")
    w("-- Backup pg_dump PRIMA. Applicare con psql -v ON_ERROR_STOP=1.")
    w("BEGIN;")
    w("")
    w("-- guard: nessuna delle entità nuove esiste già")
    names = [recs[k]["name_original"] for k in ENTITY_KEYS]
    w("DO $$ BEGIN")
    w("  IF EXISTS (SELECT 1 FROM geo_entities WHERE name_original IN (")
    w("    " + ", ".join(q(n) for n in names))
    w("  )) THEN RAISE EXCEPTION 'entità M1 già presenti — script già applicato?'; END IF;")
    w("END $$;")
    w("")
    for k in ENTITY_KEYS:
        r = recs[k]
        gj = json.dumps(r["boundary_geojson"], ensure_ascii=False, separators=(",", ": "))
        w(f"-- ── {k} ──")
        w("INSERT INTO geo_entities (name_original, name_original_lang, entity_type, year_start, year_end,")
        w("                          capital_name, capital_lat, capital_lon, boundary_geojson, boundary_source,")
        w("                          confidence_score, status, ethical_notes, wikidata_qid, boundary_geom)")
        w(f"VALUES ({q(r['name_original'])}, {q(r['name_original_lang'])}, {q(r['entity_type'])}, {r['year_start']}, {qn(r.get('year_end'))},")
        w(f"        {q(r['capital_name'])}, {r['capital_lat']}, {r['capital_lon']}, {q(gj)}, 'historical_approximation',")
        w(f"        {r['confidence_score']}, 'confirmed', {q(r['ethical_notes'])}, {q(r.get('wikidata_qid'))},")
        w(f"        ST_Multi(ST_GeomFromGeoJSON({q(gj)})));")
        ref = f"(SELECT id FROM geo_entities WHERE name_original = {q(r['name_original'])})"
        for v in r["name_variants"]:
            w("INSERT INTO name_variants (entity_id, name, lang, period_start, period_end, context, source) VALUES")
            w(f"  ({ref}, {q(v['name'])}, {q(v['lang'])}, {qn(v.get('period_start'))}, {qn(v.get('period_end'))}, {q(v.get('context'))}, {q(v.get('source'))});")
        for tc in r["territory_changes"]:
            w("INSERT INTO territory_changes (entity_id, year, region, change_type, description, population_affected, confidence_score) VALUES")
            w(f"  ({ref}, {tc['year']}, {q(tc['region'])}, {q(tc['change_type'])}, {q(tc['description'])}, {qn(tc.get('population_affected'))}, {tc.get('confidence_score', 0.7)});")
        for s in r["sources"]:
            w("INSERT INTO sources (entity_id, citation, url, source_type) VALUES")
            w(f"  ({ref}, {q(s['citation'])}, {q(s.get('url'))}, {q(s['source_type'])});")
        w("")

    def eref(name: str) -> str:
        if name in PROD_IDS:
            return str(PROD_IDS[name])
        return f"(SELECT id FROM geo_entities WHERE name_original = {q(name)})"

    lx = LAN_XANG_NEW
    pa = recs["cambodia_post_angkor"]["name_original"]
    srb = recs["serbia_1815_1918"]["name_original"]
    shs = recs["kingdom_shs_yugoslavia"]["name_original"]
    LXD = ("Lan Xang (1354-1707), the unified Lao kingdom of the middle Mekong founded by Fa Ngum with Khmer military backing; "
           "capitals Luang Prabang (1354-1560) and Vientiane (1560-1707); partitioned in 1707 after the succession crisis that followed Sourigna Vongsa's death (1694).")

    w("-- ── rename nativo #128: ล้านช้าง (thai, lang=lo mismatch) → forma lao attestata ──")
    w(f"UPDATE geo_entities SET name_original = {q(LAN_XANG_NEW)} WHERE id = 128 AND name_original = 'ล้านช้าง';")
    w("INSERT INTO name_variants (entity_id, name, lang, period_start, period_end, context, source)")
    w(f"SELECT 128, 'ล้านช้าง', 'th', 1354, 1707, {q('forma in script thai (era erroneamente il nome primario con lang=lo fino al rename ETHICS-001 in v6.99.120)')}, 'storiografia thai; ETHICS-020'")
    w("WHERE NOT EXISTS (SELECT 1 FROM name_variants WHERE entity_id = 128 AND name = 'ล้านช้าง');")
    w("INSERT INTO name_variants (entity_id, name, lang, period_start, period_end, context, source)")
    w(f"SELECT 128, {q('ລ້ານຊ້າງຮົ່ມຂາວ (Lan Xang Hom Khao)')}, 'lo', 1354, 1707, {q('nome cerimoniale completo attestato dato da Fa Ngum')}, 'Cronache lao (Nithan Khun Borom); Stuart-Fox 1998'")
    w(f"WHERE NOT EXISTS (SELECT 1 FROM name_variants WHERE entity_id = 128 AND name = {q('ລ້ານຊ້າງຮົ່ມຂາວ (Lan Xang Hom Khao)')});")
    w("")
    w("-- ── catene lao 123/124/125: prepend Lan Xang (#128) ──")
    for cid, ent_id, pyear, pethics in (
        (123, 693, 1707, "The 1707 partition was a negotiated division between Kingkitsarat (Luang Prabang) and Sai Ong Hue (Vientiane) after an armed standoff."),
        (124, 364, 1707, "Northern successor of the 1707 partition, under Kingkitsarat (crowned rival king at Luang Prabang in 1705)."),
        (125, 363, 1713, "Champasak separated from the Vientiane sphere in 1713 after a southern secession, completing the three-way division of Lan Xang."),
    ):
        w(f"UPDATE chain_links SET sequence_order = sequence_order + 1 WHERE chain_id = {cid};")
        w("INSERT INTO chain_links (chain_id, entity_id, sequence_order, transition_year, transition_type, is_violent, description, ethical_notes)")
        w(f"VALUES ({cid}, {eref(lx)}, 0, NULL, NULL, false, {q(LXD)}, NULL);")
        w(f"UPDATE chain_links SET transition_year = {pyear}, transition_type = 'PARTITION', is_violent = false, ethical_notes = {q(pethics)}")
        w(f"WHERE chain_id = {cid} AND sequence_order = 1 AND entity_id = {ent_id} AND transition_type IS NULL;")
        w("")
    w("UPDATE dynasty_chains SET name = 'Lan Xang partition — Vientiane line: ອານາຈັກລ້ານຊ້າງ → ອານາຈັກວຽງຈັນ → Siam' WHERE id = 123;")
    w("UPDATE dynasty_chains SET name = 'Lan Xang partition — Luang Prabang line: ອານາຈັກລ້ານຊ້າງ → ອານາຈັກຫລວງພະບາງ → French Indochina' WHERE id = 124;")
    w("UPDATE dynasty_chains SET name = 'Lan Xang partition — Champasak line: ອານາຈັກລ້ານຊ້າງ → ອານາຈັກຈຳປາສັກ → French Indochina' WHERE id = 125;")
    w("")

    w("-- ── catena cambogiana 126: prepend Khmer Empire (#19) + post-Angkor ──")
    w("UPDATE chain_links SET sequence_order = sequence_order + 2 WHERE chain_id = 126;")
    ke_desc = "The Khmer Empire (802-1431), the Angkorian state whose capital Yasodharapura was the region's hegemon for six centuries."
    ke_eth = "Also heads the Thai/Khmer Southeast Asian trunk chain; both successions are real (Ayutthaya absorbed much of the empire's west; the Khmer royal line continued south-east)."
    w("INSERT INTO chain_links (chain_id, entity_id, sequence_order, transition_year, transition_type, is_violent, description, ethical_notes)")
    w(f"VALUES (126, 19, 0, NULL, NULL, false, {q(ke_desc)}, {q(ke_eth)});")
    w("INSERT INTO chain_links (chain_id, entity_id, sequence_order, transition_year, transition_type, is_violent, description, ethical_notes)")
    w(f"VALUES (126, {eref(pa)}, 1, 1431, 'SUCCESSION', true, {q('After Ayutthaya sacked Yasodharapura/Angkor (~1431), the Khmer court relocated south-east (Chaktomuk, then Longvek, then Oudong): the same royal polity relocated, not a new state - typed SUCCESSION with is_violent=true because the trigger was the Ayutthayan conquest.')}, {q('Perpetrator of the 1431 sack named: Ayutthaya (Siam). Longvek fell to Naresuan of Ayutthaya on 3 January 1594 with mass deportations - see the entity record.')});")
    w(f"UPDATE chain_links SET transition_year = 1863, transition_type = 'ANNEXATION', is_violent = false WHERE chain_id = 126 AND sequence_order = 2 AND entity_id = 261 AND transition_type IS NULL;")
    w("UPDATE dynasty_chains SET name = 'Cambodian state: អាណាចក្រខ្មែរ → កម្ពុជា (Longvek-Oudong) → Indochine française → Kingdom of Cambodia' WHERE id = 126;")
    w("")

    w("-- ── catena serba 34: append Србија → СХС → СФРЈ ──")
    links34 = [
        (4, eref(srb), 1815, "DECOLONIZATION", True,
         "Serbian self-rule re-emerged from the Ottoman Empire through the uprisings of 1804-1815: de facto autonomy from the Second Uprising settlement (1815), hereditary autonomous principality by hatt-i sharif (1830), full international independence at the Treaty of Berlin (1878), kingdom from 1882.",
         "The transition was a violent decolonization (two uprisings, 1804-13 and 1815). ETHICS-002: the consolidating Serbian state was also a perpetrator - the 1862-67 removal of the Muslim population from the garrison towns and the 1878 expulsions from the Nis/Toplica sanjaks (~49,000 Albanians among at least 71,000 Muslims) are recorded on the entity."),
        (5, eref(shs), 1918, "UNIFICATION", False,
         "On 1 December 1918 the Kingdom of Serbia merged with the State of Slovenes, Croats and Serbs (and, via the contested Podgorica Assembly, with Montenegro) into the Kingdom of Serbs, Croats and Slovenes, renamed Yugoslavia in 1929.",
         "The Serbia-side unification was negotiated and peaceful; the Montenegrin absorption was contested and its aftermath violent (Christmas Uprising 1919) - see the Montenegrin chain, where that link is typed ANNEXATION."),
        (6, "231", 1945, "REVOLUTION", True,
         "The Axis invasion (April 1941) destroyed the kingdom; after four years of occupation, partition, genocide (NDH camps, Jasenovac) and multi-sided war, the communist Partisans established the Federal People's Republic (AVNOJ 1943; monarchy abolished 29 November 1945).",
         "The 1941-45 period saw occupation, the Holocaust and the Ustasa genocide of Serbs, Roma and Jews, and civil war among resistance movements - the socialist state emerged from that violence, not from a peaceful succession."),
    ]
    for seq, ref, year, ttype, viol, desc, eth in links34:
        w("INSERT INTO chain_links (chain_id, entity_id, sequence_order, transition_year, transition_type, is_violent, description, ethical_notes)")
        w(f"VALUES (34, {ref}, {seq}, {year}, {q(ttype)}, {'true' if viol else 'false'}, {q(desc)}, {q(eth)});")
    w("UPDATE dynasty_chains SET name = 'Serbian state trunk: Raska → Srpsko Carstvo → Српска деспотовина → Ottoman → Кнежевина Србија → Југославија (СХС → СФРЈ)' WHERE id = 34;")
    w("")

    w("-- ── catena montenegrina 130: append СХС ──")
    mne_desc = ("With King Nikola I in exile and the country under Serbian military occupation, the Podgorica Assembly (24-29 November 1918), elected under conditions controlled by unionist forces, "
                "deposed the king and declared unconditional union with Serbia; the Greens' Christmas Uprising (January 1919, Cetinje) was suppressed by the Serbian army and pro-union militias, with guerrilla resistance into the mid-1920s.")
    mne_eth = ("Montenegrin historiography (Pavlović, 'Balkan Anschluss') reads the union as annexation; Serbian unionist historiography as voluntary unification - both readings recorded, not arbitrated "
               "(no-single-version principle). Typed ANNEXATION with is_violent=true for the armed suppression that followed.")
    w("INSERT INTO chain_links (chain_id, entity_id, sequence_order, transition_year, transition_type, is_violent, description, ethical_notes)")
    w(f"VALUES (130, {eref(shs)}, 2, 1918, 'ANNEXATION', true, {q(mne_desc)}, {q(mne_eth)});")
    w("UPDATE dynasty_chains SET name = 'Montenegrin state: Зета → Црна Гора → Краљевина СХС' WHERE id = 130;")
    w("")

    w("-- ── 3 catene NUOVE ──")
    for ch in new_chains:
        w("INSERT INTO dynasty_chains (name, name_lang, chain_type, region, description, confidence_score, status, ethical_notes, sources)")
        w(f"VALUES ({q(ch['name'])}, 'en', {q(ch['chain_type'])}, {q(ch['region'])}, {q(ch['description'])}, {ch['confidence_score']}, 'confirmed', {q(ch['ethical_notes'])}, {q(json.dumps(ch['sources'], ensure_ascii=False))});")
        for i, ln in enumerate(ch["links"]):
            w("INSERT INTO chain_links (chain_id, entity_id, sequence_order, transition_year, transition_type, is_violent, description, ethical_notes)")
            w(f"VALUES ((SELECT id FROM dynasty_chains WHERE name = {q(ch['name'])}), {eref(ln['entity_name'])}, {i}, {qn(ln.get('transition_year'))}, {q(ln.get('transition_type'))}, {'true' if ln.get('is_violent') else 'false'}, {q(ln.get('description'))}, {q(ln.get('ethical_notes'))});")
        w("")

    w("-- ── validazione finale ──")
    w("DO $$")
    w("DECLARE n_ent int; bad int;")
    w("BEGIN")
    w("  SELECT count(*) INTO n_ent FROM geo_entities WHERE name_original IN (")
    w("    " + ", ".join(q(n) for n in names) + ");")
    w("  IF n_ent <> 8 THEN RAISE EXCEPTION 'attese 8 entità nuove, trovate %', n_ent; END IF;")
    w("  -- contiguità sequence_order per le catene toccate")
    w("  SELECT count(*) INTO bad FROM (")
    w("    SELECT chain_id FROM chain_links WHERE chain_id IN (34, 123, 124, 125, 126, 130)")
    w("    GROUP BY chain_id")
    w("    HAVING count(*) <> max(sequence_order) + 1 OR min(sequence_order) <> 0")
    w("  ) t;")
    w("  IF bad <> 0 THEN RAISE EXCEPTION 'sequence_order non contigui su % catene', bad; END IF;")
    w("  -- ogni link non-primo ha transition_type")
    w("  SELECT count(*) INTO bad FROM chain_links WHERE chain_id IN (34, 123, 124, 125, 126, 130)")
    w("    AND sequence_order > 0 AND transition_type IS NULL;")
    w("  IF bad <> 0 THEN RAISE EXCEPTION '% link non-primi senza transition_type', bad; END IF;")
    w("  -- antimeridian guard sui boundary nuovi (CLAUDE.md geometric check)")
    w("  SELECT count(*) INTO bad FROM geo_entities WHERE name_original IN (")
    w("    " + ", ".join(q(n) for n in names) + ")")
    w("    AND (ST_XMax(boundary_geom) - ST_XMin(boundary_geom)) >= 180;")
    w("  IF bad <> 0 THEN RAISE EXCEPTION '% boundary attraversano l''antimeridiano', bad; END IF;")
    w("  RAISE NOTICE 'M1 v6.99.120 OK: 11 entità + catene 34/123/124/125/126/130 + 3 nuove';")
    w("END $$;")
    w("")
    w("COMMIT;")
    return "\n".join(out) + "\n"


def main() -> None:
    recs = load_research()
    assert set(ENTITY_KEYS) <= set(recs), sorted(recs)
    apply_corrections(recs)
    for k in ENTITY_KEYS:
        validate_boundary(k, recs[k])

    entities = [build_entity_json(recs[k]) for k in ENTITY_KEYS]
    ENT_OUT.write_text(json.dumps(entities, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"OK {ENT_OUT}: {len(entities)} entità")

    new_chains = build_new_chains(recs)
    CHAINS_OUT.write_text(json.dumps(new_chains, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"OK {CHAINS_OUT}: {len(new_chains)} catene")

    # la chirurgia include il rename #128 in batch_02 → il fence va DOPO
    chain_surgery(recs)

    # fence: i riferimenti alle entità esistenti devono risolvere in JSON-land
    effective: set[str] = set()
    for path in sorted(Path("data/entities").glob("*.json")):
        for ent in json.loads(path.read_text(encoding="utf-8")):
            if ent.get("name_original"):
                effective.add(ent["name_original"])
    for label, name in EXISTING.items():
        assert name in effective, f"riferimento non risolvibile in JSON-land: {label} = {name!r}"
    print("OK fence: tutti i riferimenti risolvono in JSON-land")

    SQL_OUT.write_text(gen_sql(recs, new_chains), encoding="utf-8")
    print(f"OK {SQL_OUT}")


if __name__ == "__main__":
    main()
