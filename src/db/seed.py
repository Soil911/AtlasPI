"""Dati demo per AtlasPI — 10 entità storiche.

ETHICS: ogni entità dimostra i principi etici del progetto.
I nomi originali hanno priorità (ETHICS-001).
Le conquiste sono documentate esplicitamente (ETHICS-002).
I territori contestati mostrano tutte le versioni (ETHICS-003).
"""

import json
import logging

from sqlalchemy.orm import Session

from src.db.database import SessionLocal
from src.db.models import GeoEntity, NameVariant, Source, TerritoryChange

logger = logging.getLogger(__name__)


DEMO_ENTITIES = [
    # ─── 1. Impero Romano ───────────────────────────────────────
    {
        "name_original": "Imperium Romanum",
        "name_original_lang": "la",
        "entity_type": "empire",
        "year_start": -27,
        "year_end": 476,
        "capital_name": "Roma",
        "capital_lat": 41.9028,
        "capital_lon": 12.4964,
        "confidence_score": 0.90,
        "status": "confirmed",
        "boundary_geojson": {
            "type": "Polygon",
            "coordinates": [[
                [-9.5, 37.0], [-8.8, 38.7], [-9.1, 39.8], [-8.0, 41.2],
                [-7.5, 42.0], [-5.5, 43.3], [-3.0, 43.5], [-1.5, 43.3],
                [0.0, 42.5], [1.5, 43.0], [3.0, 43.5], [3.5, 46.0],
                [5.0, 47.5], [6.5, 49.0], [7.5, 50.5], [8.0, 50.0],
                [9.5, 48.5], [10.5, 47.5], [12.0, 47.0], [13.5, 47.5],
                [15.0, 48.0], [16.5, 48.3], [18.0, 47.8], [19.5, 46.5],
                [20.0, 45.5], [21.5, 44.5], [22.5, 44.0], [24.0, 44.5],
                [26.0, 45.5], [28.5, 45.0], [30.0, 44.0], [32.0, 43.5],
                [34.0, 42.5], [36.0, 42.0], [38.0, 40.5], [40.0, 39.0],
                [42.0, 37.5], [44.5, 37.0], [46.0, 36.5], [44.0, 34.0],
                [42.0, 33.0], [39.5, 32.0], [36.5, 31.5], [35.8, 32.5],
                [35.2, 31.0], [34.5, 29.5], [32.5, 30.0], [30.0, 31.0],
                [27.0, 31.2], [25.0, 31.5], [22.0, 31.5], [17.0, 31.0],
                [12.5, 32.5], [10.0, 33.5], [8.5, 34.0], [5.0, 34.5],
                [2.5, 35.0], [0.0, 35.5], [-2.0, 35.5], [-5.5, 35.8],
                [-7.0, 36.0], [-9.5, 37.0],
            ]],
        },
        "ethical_notes": (
            "Confini mostrati al periodo di massima espansione (~117 d.C., "
            "sotto Traiano). L'espansione fu ottenuta attraverso conquista "
            "militare sistematica di decine di popoli. I dati demografici "
            "sulle vittime sono incerti ma le fonti indicano violenza su "
            "larga scala. Vedi ETHICS-002."
        ),
        "name_variants": [
            {"name": "Roman Empire", "lang": "en", "period_start": -27, "period_end": 476,
             "context": "denominazione inglese moderna", "source": "Oxford Classical Dictionary"},
            {"name": "Impero Romano", "lang": "it", "period_start": -27, "period_end": 476,
             "context": "denominazione italiana", "source": "Enciclopedia Treccani"},
            {"name": "Res Publica Romana", "lang": "la", "period_start": -509, "period_end": -27,
             "context": "nome del periodo repubblicano precedente", "source": "Livio, Ab Urbe Condita"},
        ],
        "territory_changes": [
            {"year": -51, "region": "Gallia", "change_type": "CONQUEST_MILITARY",
             "description": "Conquista di Giulio Cesare (58-50 a.C.). Le fonti antiche stimano 1-3 milioni di morti. La storiografia moderna ritiene le cifre probabilmente esagerate ma indicative di violenza su larga scala.",
             "population_affected": 1000000, "confidence_score": 0.75},
            {"year": 43, "region": "Britannia", "change_type": "CONQUEST_MILITARY",
             "description": "Invasione sotto l'imperatore Claudio. Resistenza prolungata dei popoli locali, inclusa la rivolta di Boudicca (60-61 d.C.).",
             "population_affected": None, "confidence_score": 0.80},
            {"year": 106, "region": "Dacia", "change_type": "CONQUEST_MILITARY",
             "description": "Conquista sotto Traiano. Distruzione quasi totale del regno dacico e deportazione della popolazione.",
             "population_affected": None, "confidence_score": 0.70},
        ],
        "sources": [
            {"citation": "Cesare, De Bello Gallico", "source_type": "primary"},
            {"citation": "Goldsworthy, A. Caesar: Life of a Colossus (2006)", "source_type": "academic"},
            {"citation": "Enciclopedia Treccani, voce 'Impero Romano'", "url": "https://www.treccani.it", "source_type": "secondary"},
        ],
    },
    # ─── 2. Impero Ottomano ─────────────────────────────────────
    {
        "name_original": "Osmanlı İmparatorluğu",
        "name_original_lang": "tr",
        "entity_type": "empire",
        "year_start": 1299,
        "year_end": 1922,
        "capital_name": "İstanbul",
        "capital_lat": 41.0082,
        "capital_lon": 28.9784,
        "confidence_score": 0.85,
        "status": "confirmed",
        "boundary_geojson": {
            "type": "Polygon",
            "coordinates": [[
                [15.5, 39.5], [16.0, 41.0], [16.5, 42.5], [17.0, 43.5],
                [17.5, 45.0], [18.5, 45.5], [19.0, 46.5], [20.0, 47.0],
                [21.5, 46.5], [22.5, 46.0], [24.0, 45.5], [25.5, 45.0],
                [27.0, 44.5], [28.5, 44.0], [29.5, 43.5], [30.0, 42.0],
                [31.5, 41.5], [33.0, 41.0], [35.0, 40.5], [36.5, 39.5],
                [38.0, 38.5], [40.0, 37.5], [41.5, 37.0], [43.0, 36.5],
                [44.5, 36.0], [45.0, 35.0], [44.5, 33.5], [43.0, 32.0],
                [41.0, 31.0], [39.5, 30.5], [37.5, 30.0], [36.0, 31.0],
                [35.0, 31.5], [34.5, 30.0], [33.5, 29.0], [32.0, 29.5],
                [30.0, 30.5], [27.5, 31.0], [25.0, 31.5], [23.0, 32.0],
                [21.0, 32.5], [19.5, 33.0], [18.0, 34.0], [16.5, 35.0],
                [15.5, 36.5], [15.0, 37.5], [15.5, 39.5],
            ]],
        },
        "ethical_notes": (
            "Confini mostrati al periodo di massima espansione (~1683). "
            "L'impero includeva popolazioni diverse sotto un sistema "
            "amministrativo complesso (millet). La rappresentazione non "
            "deve né celebrare né demonizzare — documentare la complessità."
        ),
        "name_variants": [
            {"name": "Ottoman Empire", "lang": "en", "period_start": 1299, "period_end": 1922,
             "context": "denominazione inglese", "source": "Encyclopaedia Britannica"},
            {"name": "Impero Ottomano", "lang": "it", "period_start": 1299, "period_end": 1922,
             "context": "denominazione italiana", "source": "Enciclopedia Treccani"},
            {"name": "Devlet-i Aliyye-i Osmâniyye", "lang": "ota", "period_start": 1299, "period_end": 1922,
             "context": "nome ufficiale in turco ottomano", "source": "Finkel, Osman's Dream (2005)"},
        ],
        "territory_changes": [
            {"year": 1453, "region": "Costantinopoli", "change_type": "CONQUEST_MILITARY",
             "description": "Conquista di Costantinopoli da parte di Mehmed II. Fine dell'Impero Romano d'Oriente. La città fu rinominata İstanbul.",
             "population_affected": None, "confidence_score": 0.95},
            {"year": 1683, "region": "Europa Centrale", "change_type": "CONQUEST_MILITARY",
             "description": "Massima espansione in Europa con l'assedio di Vienna. Sconfitta che segna l'inizio del declino territoriale.",
             "population_affected": None, "confidence_score": 0.90},
        ],
        "sources": [
            {"citation": "Finkel, C. Osman's Dream: The Story of the Ottoman Empire (2005)", "source_type": "academic"},
            {"citation": "Encyclopaedia Britannica, voce 'Ottoman Empire'", "source_type": "secondary"},
        ],
    },
    # ─── 3. İstanbul (città attraverso il tempo) ───────────────
    {
        "name_original": "İstanbul",
        "name_original_lang": "tr",
        "entity_type": "city",
        "year_start": -657,
        "year_end": None,
        "capital_name": "İstanbul",
        "capital_lat": 41.0082,
        "capital_lon": 28.9784,
        "confidence_score": 0.95,
        "status": "confirmed",
        "boundary_geojson": {
            "type": "Point",
            "coordinates": [28.9784, 41.0082],
        },
        "ethical_notes": (
            "ETHICS-001: il nome primario è quello locale attuale (İstanbul). "
            "I nomi storici Byzantium e Constantinopolis sono varianti con "
            "contesto temporale esplicito. Nessun nome è 'più corretto' "
            "di un altro — ciascuno riflette un'epoca diversa."
        ),
        "name_variants": [
            {"name": "Byzantium", "lang": "la", "period_start": -657, "period_end": 330,
             "context": "nome greco originale della colonia", "source": "Tucidide, I.94"},
            {"name": "Constantinopolis", "lang": "la", "period_start": 330, "period_end": 1453,
             "context": "nome romano-bizantino, da Costantino I", "source": "Enciclopedia Treccani"},
            {"name": "Costantinopoli", "lang": "it", "period_start": 330, "period_end": 1453,
             "context": "forma italiana del nome romano-bizantino", "source": "Enciclopedia Treccani"},
            {"name": "Constantinople", "lang": "en", "period_start": 330, "period_end": 1453,
             "context": "forma inglese del nome romano-bizantino", "source": "Encyclopaedia Britannica"},
            {"name": "Βυζάντιον", "lang": "grc", "period_start": -657, "period_end": 330,
             "context": "nome originale in greco antico", "source": "Erodoto, IV.144"},
        ],
        "territory_changes": [
            {"year": -657, "region": "Bosforo", "change_type": "TREATY",
             "description": "Fondazione come colonia greca di Megara.",
             "confidence_score": 0.60},
            {"year": 330, "region": "Bosforo", "change_type": "TREATY",
             "description": "Costantino I rifonda la città come nuova capitale dell'Impero Romano.",
             "confidence_score": 0.95},
            {"year": 1453, "region": "Bosforo", "change_type": "CONQUEST_MILITARY",
             "description": "Conquista ottomana sotto Mehmed II. La città diventa capitale dell'Impero Ottomano.",
             "confidence_score": 0.95},
        ],
        "sources": [
            {"citation": "Tucidide, Guerra del Peloponneso, I.94", "source_type": "primary"},
            {"citation": "Freely, J. Istanbul: The Imperial City (1996)", "source_type": "academic"},
        ],
    },
    # ─── 4. Tawantinsuyu (Impero Inca) ─────────────────────────
    {
        "name_original": "Tawantinsuyu",
        "name_original_lang": "qu",
        "entity_type": "empire",
        "year_start": 1438,
        "year_end": 1533,
        "capital_name": "Qusqu",
        "capital_lat": -13.5320,
        "capital_lon": -71.9675,
        "confidence_score": 0.70,
        "status": "confirmed",
        "boundary_geojson": {
            "type": "Polygon",
            "coordinates": [[
                [-80.2, 1.5], [-79.5, 0.0], [-79.8, -1.5], [-79.0, -3.0],
                [-78.5, -4.5], [-78.0, -6.0], [-77.5, -7.5], [-76.5, -9.0],
                [-76.0, -10.5], [-75.5, -12.0], [-75.0, -14.0], [-74.0, -15.5],
                [-72.5, -17.0], [-71.0, -18.5], [-70.0, -20.0], [-69.5, -22.0],
                [-69.0, -25.0], [-69.5, -27.5], [-70.0, -30.0], [-70.5, -33.0],
                [-71.5, -34.5], [-72.0, -33.0], [-72.5, -30.0], [-73.0, -27.0],
                [-73.5, -24.0], [-74.0, -21.0], [-74.5, -18.0], [-75.5, -15.5],
                [-76.5, -13.0], [-77.0, -11.0], [-78.0, -8.5], [-79.0, -5.5],
                [-79.5, -3.5], [-80.0, -1.5], [-80.2, 1.5],
            ]],
        },
        "ethical_notes": (
            "ETHICS-001: il nome originale è in lingua Quechua (Tawantinsuyu = "
            "'quattro regioni unite'). 'Impero Inca' è la denominazione europea. "
            "Il confidence_score è più basso perché le fonti sono prevalentemente "
            "orali — la civiltà non aveva scrittura alfabetica (usava i quipu). "
            "Le fonti scritte sono quasi esclusivamente dei conquistadores spagnoli, "
            "con i bias che questo comporta."
        ),
        "name_variants": [
            {"name": "Inca Empire", "lang": "en",
             "context": "denominazione europea — 'Inca' era il titolo del sovrano, non il nome dello stato",
             "source": "D'Altroy, The Incas (2002)"},
            {"name": "Impero Inca", "lang": "it",
             "context": "denominazione italiana", "source": "Enciclopedia Treccani"},
            {"name": "Cusco", "lang": "es", "period_start": 1533, "period_end": None,
             "context": "nome spagnolo della capitale, imposto dopo la conquista",
             "source": "Hemming, The Conquest of the Incas (1970)"},
        ],
        "territory_changes": [
            {"year": 1533, "region": "Tawantinsuyu", "change_type": "COLONIZATION",
             "description": "Conquista spagnola sotto Francisco Pizarro. Cattura e esecuzione dell'ultimo Sapa Inca Atahualpa. Distruzione sistematica delle strutture politiche e religiose.",
             "population_affected": 8000000, "confidence_score": 0.60},
        ],
        "sources": [
            {"citation": "D'Altroy, T.N. The Incas (2002)", "source_type": "academic"},
            {"citation": "Hemming, J. The Conquest of the Incas (1970)", "source_type": "academic"},
            {"citation": "Garcilaso de la Vega, Comentarios Reales de los Incas (1609)", "source_type": "primary"},
        ],
    },
    # ─── 5. British Raj ─────────────────────────────────────────
    {
        "name_original": "British Raj",
        "name_original_lang": "en",
        "entity_type": "colony",
        "year_start": 1858,
        "year_end": 1947,
        "capital_name": "New Delhi",
        "capital_lat": 28.6139,
        "capital_lon": 77.2090,
        "confidence_score": 0.90,
        "status": "confirmed",
        "boundary_geojson": {
            "type": "Polygon",
            "coordinates": [[
                [61.5, 25.0], [62.5, 26.5], [63.5, 28.0], [64.5, 29.5],
                [66.0, 31.0], [67.5, 33.0], [69.0, 34.5], [70.5, 35.5],
                [72.0, 36.5], [74.0, 37.0], [75.5, 36.5], [77.0, 35.5],
                [78.5, 34.0], [80.0, 32.0], [81.5, 30.0], [83.0, 28.5],
                [85.0, 27.5], [87.0, 27.0], [89.0, 26.5], [91.0, 25.5],
                [92.5, 24.5], [93.5, 23.0], [94.5, 21.0], [95.5, 18.5],
                [96.0, 16.5], [95.0, 14.0], [93.0, 11.0], [91.0, 9.5],
                [88.0, 8.0], [85.0, 7.5], [82.0, 7.0], [80.0, 7.5],
                [78.0, 8.5], [76.5, 10.0], [75.5, 12.0], [75.0, 14.0],
                [74.0, 16.5], [73.5, 18.5], [72.5, 20.5], [71.0, 22.0],
                [69.5, 23.0], [67.5, 24.0], [65.0, 24.5], [63.0, 24.5],
                [61.5, 25.0],
            ]],
        },
        "ethical_notes": (
            "ETHICS-001: il nome 'British Raj' è una costruzione coloniale. "
            "I popoli del subcontinente usavano nomi propri per le proprie "
            "terre (Bharat, Hindustan, etc.). Il nome coloniale è mantenuto "
            "come name_original perché identifica specificamente l'entità "
            "coloniale, non il subcontinente. Le varianti includono i nomi "
            "indigeni. ETHICS-002: l'acquisizione avvenne tramite colonizzazione "
            "e cessione forzata."
        ),
        "name_variants": [
            {"name": "भारत", "lang": "hi", "context": "Bharat — nome indigeno del subcontinente in Hindi",
             "source": "Costituzione dell'India, Art. 1"},
            {"name": "Hindustan", "lang": "ur", "context": "nome persiano/urdu del subcontinente",
             "source": "Encyclopaedia Britannica"},
            {"name": "India britannica", "lang": "it", "context": "denominazione italiana",
             "source": "Enciclopedia Treccani"},
        ],
        "territory_changes": [
            {"year": 1858, "region": "Subcontinente indiano", "change_type": "COLONIZATION",
             "description": "Dopo la rivolta dei Sepoy (1857), la Corona britannica assume il controllo diretto dalla Compagnia delle Indie Orientali. Imposizione di amministrazione coloniale su centinaia di milioni di persone.",
             "population_affected": 250000000, "confidence_score": 0.90},
            {"year": 1947, "region": "Subcontinente indiano", "change_type": "LIBERATION",
             "description": "Indipendenza e Partizione. La divisione in India e Pakistan causò una delle più grandi migrazioni forzate della storia: 10-20 milioni di sfollati, 200.000-2.000.000 di morti.",
             "population_affected": 15000000, "confidence_score": 0.85},
        ],
        "sources": [
            {"citation": "Dalrymple, W. The Anarchy (2019)", "source_type": "academic"},
            {"citation": "Tharoor, S. Inglorious Empire (2017)", "source_type": "academic"},
        ],
    },
    # ─── 6. Palestina / Israele (contestato) ────────────────────
    {
        "name_original": "فلسطين / ישראל",
        "name_original_lang": "mul",
        "entity_type": "disputed_territory",
        "year_start": 1948,
        "year_end": None,
        "capital_name": None,
        "capital_lat": 31.7683,
        "capital_lon": 35.2137,
        "confidence_score": 0.40,
        "status": "disputed",
        "boundary_geojson": {
            "type": "Polygon",
            "coordinates": [[
                [34.25, 29.50], [34.22, 30.00], [34.20, 30.50], [34.22, 30.90],
                [34.27, 31.25], [34.35, 31.50], [34.50, 31.80], [34.55, 32.10],
                [34.70, 32.35], [34.85, 32.60], [35.00, 32.80], [35.10, 33.00],
                [35.40, 33.15], [35.65, 33.28], [35.88, 33.28], [35.90, 33.10],
                [35.87, 32.80], [35.85, 32.50], [35.80, 32.20], [35.70, 31.95],
                [35.60, 31.70], [35.50, 31.40], [35.48, 31.20], [35.45, 30.90],
                [35.42, 30.60], [35.40, 30.20], [35.38, 29.80], [35.35, 29.50],
                [35.00, 29.50], [34.65, 29.48], [34.25, 29.50],
            ]],
        },
        "ethical_notes": (
            "ETHICS-003: territorio attivamente contestato. Questo record NON "
            "arbitra la disputa. Entrambe le denominazioni sono presenti come "
            "name_original. Non è stata impostata una capitale perché sia "
            "Gerusalemme/al-Quds che Tel Aviv/Ramallah sono rivendicate da "
            "parti diverse. Il confidence_score basso riflette l'impossibilità "
            "di una rappresentazione unica accettata da tutte le parti. "
            "I confini mostrati sono approssimativi e contestati."
        ),
        "name_variants": [
            {"name": "Palestine", "lang": "en", "context": "denominazione internazionale",
             "source": "Nazioni Unite"},
            {"name": "Israel", "lang": "en", "period_start": 1948,
             "context": "stato proclamato nel 1948, riconosciuto dalla maggioranza degli stati ONU",
             "source": "Nazioni Unite, Risoluzione 181 (1947)"},
            {"name": "فلسطين", "lang": "ar", "context": "nome arabo",
             "source": "Autorità Nazionale Palestinese"},
            {"name": "ישראל", "lang": "he", "period_start": 1948,
             "context": "nome ebraico dello stato", "source": "Dichiarazione d'Indipendenza (1948)"},
            {"name": "Palestina", "lang": "it", "context": "denominazione italiana del territorio storico",
             "source": "Enciclopedia Treccani"},
        ],
        "territory_changes": [
            {"year": 1948, "region": "Mandato Britannico di Palestina", "change_type": "REVOLUTION",
             "description": "Fine del Mandato britannico. Proclamazione dello Stato di Israele. Guerra arabo-israeliana. Nakba: espulsione e fuga di circa 700.000 palestinesi.",
             "population_affected": 700000, "confidence_score": 0.80},
            {"year": 1967, "region": "Cisgiordania, Gaza, Golan, Sinai", "change_type": "CONQUEST_MILITARY",
             "description": "Guerra dei Sei Giorni. Occupazione israeliana di Cisgiordania, Striscia di Gaza, Alture del Golan e Penisola del Sinai.",
             "population_affected": 1000000, "confidence_score": 0.90},
        ],
        "sources": [
            {"citation": "Morris, B. 1948: A History of the First Arab-Israeli War (2008)", "source_type": "academic"},
            {"citation": "Pappe, I. The Ethnic Cleansing of Palestine (2006)", "source_type": "academic"},
            {"citation": "Nazioni Unite, Risoluzione 242 (1967)", "source_type": "primary"},
        ],
    },
    # ─── 7. Kosovo ──────────────────────────────────────────────
    {
        "name_original": "Republika e Kosovës",
        "name_original_lang": "sq",
        "entity_type": "disputed_territory",
        "year_start": 2008,
        "year_end": None,
        "capital_name": "Prishtina",
        "capital_lat": 42.6629,
        "capital_lon": 21.1655,
        "confidence_score": 0.55,
        "status": "disputed",
        "boundary_geojson": {
            "type": "Polygon",
            "coordinates": [[
                [20.04, 42.55], [20.06, 42.68], [20.12, 42.75], [20.25, 42.82],
                [20.38, 42.88], [20.50, 42.92], [20.60, 42.95], [20.73, 42.98],
                [20.85, 43.00], [20.95, 43.00], [21.05, 42.98], [21.15, 42.92],
                [21.25, 42.85], [21.38, 42.78], [21.48, 42.70], [21.55, 42.60],
                [21.58, 42.50], [21.58, 42.40], [21.55, 42.30], [21.48, 42.22],
                [21.40, 42.15], [21.30, 42.10], [21.18, 42.08], [21.05, 42.09],
                [20.92, 42.12], [20.78, 42.18], [20.65, 42.22], [20.50, 42.28],
                [20.38, 42.32], [20.25, 42.38], [20.15, 42.42], [20.08, 42.48],
                [20.04, 42.55],
            ]],
        },
        "ethical_notes": (
            "ETHICS-003: il Kosovo ha dichiarato l'indipendenza nel 2008, "
            "riconosciuta da oltre 100 stati membri ONU ma non dalla Serbia "
            "e da alcuni altri stati. Il nome primario è in albanese (lingua "
            "della maggioranza della popolazione). Il nome serbo è incluso "
            "come variante. Il database non prende posizione sulla legittimità."
        ),
        "name_variants": [
            {"name": "Република Косово", "lang": "sr", "context": "nome serbo — la Serbia non riconosce l'indipendenza",
             "source": "Costituzione della Serbia"},
            {"name": "Kosovo", "lang": "en", "context": "denominazione internazionale comune",
             "source": "Corte Internazionale di Giustizia, Parere consultivo (2010)"},
            {"name": "Kosova", "lang": "sq", "context": "forma albanese abbreviata",
             "source": "Costituzione del Kosovo (2008)"},
        ],
        "territory_changes": [
            {"year": 1999, "region": "Kosovo", "change_type": "LIBERATION",
             "description": "Intervento NATO dopo pulizia etnica serba. Risoluzione ONU 1244 pone il Kosovo sotto amministrazione internazionale.",
             "population_affected": 800000, "confidence_score": 0.90},
            {"year": 2008, "region": "Kosovo", "change_type": "REVOLUTION",
             "description": "Dichiarazione unilaterale di indipendenza dalla Serbia. Riconoscimento parziale dalla comunità internazionale.",
             "confidence_score": 0.85},
        ],
        "sources": [
            {"citation": "Corte Internazionale di Giustizia, Parere consultivo sulla dichiarazione di indipendenza del Kosovo (2010)", "source_type": "primary"},
            {"citation": "Judah, T. Kosovo: What Everyone Needs to Know (2008)", "source_type": "academic"},
        ],
    },
    # ─── 8. Atene antica ───────────────────────────────────────
    {
        "name_original": "Ἀθῆναι",
        "name_original_lang": "grc",
        "entity_type": "city-state",
        "year_start": -508,
        "year_end": -322,
        "capital_name": "Ἀθῆναι",
        "capital_lat": 37.9838,
        "capital_lon": 23.7275,
        "confidence_score": 0.80,
        "status": "confirmed",
        "boundary_geojson": {
            "type": "Polygon",
            "coordinates": [[
                [23.40, 37.65], [23.35, 37.80], [23.30, 37.95], [23.28, 38.10],
                [23.30, 38.20], [23.35, 38.30], [23.42, 38.35], [23.55, 38.38],
                [23.65, 38.38], [23.78, 38.35], [23.90, 38.30], [24.00, 38.22],
                [24.05, 38.12], [24.08, 38.00], [24.08, 37.90], [24.05, 37.80],
                [23.98, 37.72], [23.88, 37.65], [23.75, 37.60], [23.62, 37.58],
                [23.50, 37.60], [23.40, 37.65],
            ]],
        },
        "ethical_notes": (
            "Confini della regione dell'Attica nel periodo della democrazia "
            "ateniese (508-322 a.C.). La democrazia era limitata ai maschi "
            "adulti liberi — escludeva donne, schiavi e stranieri residenti "
            "(meteci). Questa è una precisazione storica necessaria."
        ),
        "name_variants": [
            {"name": "Athens", "lang": "en", "context": "denominazione inglese",
             "source": "Oxford Classical Dictionary"},
            {"name": "Atene", "lang": "it", "context": "denominazione italiana",
             "source": "Enciclopedia Treccani"},
            {"name": "Athenae", "lang": "la", "context": "denominazione latina",
             "source": "Cicerone, De Finibus"},
        ],
        "territory_changes": [
            {"year": -508, "region": "Attica", "change_type": "REVOLUTION",
             "description": "Riforme di Clistene: istituzione della democrazia. Riorganizzazione delle tribù e creazione dell'assemblea popolare (ecclesia).",
             "confidence_score": 0.75},
            {"year": -322, "region": "Attica", "change_type": "CONQUEST_MILITARY",
             "description": "Sconfitta nella guerra lamiaca. Fine dell'indipendenza politica di Atene sotto il dominio macedone.",
             "confidence_score": 0.80},
        ],
        "sources": [
            {"citation": "Aristotele, Costituzione degli Ateniesi", "source_type": "primary"},
            {"citation": "Hansen, M.H. The Athenian Democracy in the Age of Demosthenes (1991)", "source_type": "academic"},
        ],
    },
    # ─── 9. Impero Mongolo ──────────────────────────────────────
    {
        "name_original": "ᠶᠡᠬᠡ ᠮᠣᠩᠭᠣᠯ ᠤᠯᠤᠰ",
        "name_original_lang": "mn",
        "entity_type": "empire",
        "year_start": 1206,
        "year_end": 1368,
        "capital_name": "Karakorum",
        "capital_lat": 47.1986,
        "capital_lon": 102.8310,
        "confidence_score": 0.75,
        "status": "confirmed",
        "boundary_geojson": {
            "type": "Polygon",
            "coordinates": [[
                [24.0, 38.0], [24.0, 40.0], [25.0, 43.0], [26.0, 45.0],
                [28.0, 48.0], [30.0, 50.0], [33.0, 52.0], [37.0, 54.0],
                [42.0, 56.0], [48.0, 57.5], [55.0, 58.5], [62.0, 59.5],
                [70.0, 60.0], [78.0, 59.5], [85.0, 58.0], [92.0, 56.5],
                [98.0, 55.0], [104.0, 53.5], [110.0, 52.0], [115.0, 50.5],
                [120.0, 48.5], [124.0, 46.0], [127.0, 44.0], [130.0, 42.0],
                [128.0, 38.0], [125.0, 35.0], [122.0, 32.5], [119.0, 30.5],
                [116.0, 28.5], [113.0, 26.0], [110.0, 24.0], [107.0, 22.5],
                [103.0, 22.0], [99.0, 22.5], [95.0, 24.0], [90.0, 26.0],
                [85.0, 28.0], [80.0, 29.5], [75.0, 30.5], [70.0, 31.0],
                [64.0, 31.5], [58.0, 32.0], [52.0, 32.5], [47.0, 33.0],
                [42.0, 34.0], [37.0, 35.5], [33.0, 36.5], [29.0, 37.5],
                [24.0, 38.0],
            ]],
        },
        "ethical_notes": (
            "ETHICS-002: l'Impero Mongolo rappresenta la più grande conquista "
            "militare contigua della storia. Le stime delle vittime variano "
            "enormemente (11-40 milioni). Le conquiste comportarono distruzione "
            "di intere città e civiltà (Baghdad 1258, Khwarezm). Il nome "
            "originale è in scrittura mongola tradizionale (Yeke Mongγol Ulus)."
        ),
        "name_variants": [
            {"name": "Mongol Empire", "lang": "en", "context": "denominazione inglese",
             "source": "Encyclopaedia Britannica"},
            {"name": "Impero Mongolo", "lang": "it", "context": "denominazione italiana",
             "source": "Enciclopedia Treccani"},
            {"name": "Их Монгол Улс", "lang": "mn", "context": "nome in cirillico mongolo moderno",
             "source": "Weatherford, Genghis Khan and the Making of the Modern World (2004)"},
        ],
        "territory_changes": [
            {"year": 1219, "region": "Khwarezm", "change_type": "CONQUEST_MILITARY",
             "description": "Invasione dell'Impero Corasmio. Distruzione totale di città come Samarcanda, Bukhara, Merv. Milioni di vittime stimate.",
             "population_affected": 2000000, "confidence_score": 0.60},
            {"year": 1258, "region": "Baghdad", "change_type": "CONQUEST_MILITARY",
             "description": "Sacco di Baghdad sotto Hulagu Khan. Distruzione del Califfato Abbaside. Fonti riportano centinaia di migliaia di vittime.",
             "population_affected": 200000, "confidence_score": 0.55},
        ],
        "sources": [
            {"citation": "Weatherford, J. Genghis Khan and the Making of the Modern World (2004)", "source_type": "academic"},
            {"citation": "Rashid al-Din, Jami' al-Tawarikh (1307)", "source_type": "primary"},
        ],
    },
    # ─── 10. Regno del Kongo ────────────────────────────────────
    {
        "name_original": "Kongo dia Ntotila",
        "name_original_lang": "kg",
        "entity_type": "kingdom",
        "year_start": 1390,
        "year_end": 1914,
        "capital_name": "M'banza-Kongo",
        "capital_lat": -6.2663,
        "capital_lon": 14.2401,
        "confidence_score": 0.65,
        "status": "confirmed",
        "boundary_geojson": {
            "type": "Polygon",
            "coordinates": [[
                [12.2, -4.5], [12.5, -3.5], [13.0, -2.5], [13.8, -1.8],
                [14.5, -1.5], [15.2, -1.8], [16.0, -2.2], [17.0, -2.8],
                [18.0, -3.5], [18.8, -4.2], [19.0, -5.0], [18.8, -6.0],
                [18.5, -7.0], [18.0, -7.8], [17.2, -8.5], [16.5, -9.0],
                [15.5, -9.5], [14.8, -9.8], [14.0, -9.5], [13.2, -9.0],
                [12.5, -8.2], [12.2, -7.2], [12.0, -6.2], [12.0, -5.2],
                [12.2, -4.5],
            ]],
        },
        "ethical_notes": (
            "ETHICS-001: il nome originale è in lingua Kikongo. Il confidence_score "
            "è più basso perché le fonti scritte pre-coloniali sono limitate. "
            "ETHICS-002: il regno fu progressivamente smantellato dalla colonizzazione "
            "portoghese e poi belga. La tratta degli schiavi transatlantica devastò "
            "la regione per secoli. Il dominio belga del Congo (sotto Leopoldo II) "
            "causò atrocità documentate con milioni di vittime."
        ),
        "name_variants": [
            {"name": "Kingdom of Kongo", "lang": "en", "context": "denominazione inglese",
             "source": "Thornton, The Kingdom of Kongo (1983)"},
            {"name": "Regno del Kongo", "lang": "it", "context": "denominazione italiana",
             "source": "Enciclopedia Treccani"},
            {"name": "Reino do Congo", "lang": "pt", "period_start": 1491,
             "context": "nome portoghese dopo il contatto europeo",
             "source": "Thornton, The Kingdom of Kongo (1983)"},
        ],
        "territory_changes": [
            {"year": 1491, "region": "Kongo", "change_type": "TREATY",
             "description": "Primo contatto con i portoghesi. Conversione al cristianesimo del re Nzinga a Nkuwu. Inizio dell'influenza europea.",
             "confidence_score": 0.70},
            {"year": 1665, "region": "Kongo", "change_type": "CONQUEST_MILITARY",
             "description": "Battaglia di Mbwila. Sconfitta del Kongo da parte dei portoghesi. Inizio della frammentazione politica.",
             "confidence_score": 0.65},
            {"year": 1885, "region": "Congo", "change_type": "COLONIZATION",
             "description": "Conferenza di Berlino: il territorio diventa proprietà personale di Leopoldo II del Belgio. Sfruttamento brutale della popolazione: lavoro forzato, mutilazioni, milioni di morti stimate.",
             "population_affected": 10000000, "confidence_score": 0.70},
        ],
        "sources": [
            {"citation": "Thornton, J. The Kingdom of Kongo (1983)", "source_type": "academic"},
            {"citation": "Hochschild, A. King Leopold's Ghost (1998)", "source_type": "academic"},
            {"citation": "Vansina, J. Kingdoms of the Savanna (1966)", "source_type": "academic"},
        ],
    },
    # ─── 11. Impero Bizantino ───────────────────────────────────
    {
        "name_original": "Βασιλεία Ῥωμαίων",
        "name_original_lang": "grc",
        "entity_type": "empire",
        "year_start": 395,
        "year_end": 1453,
        "capital_name": "Κωνσταντινούπολις",
        "capital_lat": 41.0082,
        "capital_lon": 28.9784,
        "confidence_score": 0.85,
        "status": "confirmed",
        "boundary_geojson": {
            "type": "Polygon",
            "coordinates": [[
                [19.0, 35.0], [20.0, 38.0], [22.0, 40.0], [25.0, 41.5],
                [28.5, 41.0], [31.0, 41.5], [35.0, 40.0], [37.0, 38.0],
                [36.0, 35.5], [35.0, 34.0], [32.0, 35.0], [28.0, 36.0],
                [25.0, 35.5], [22.0, 34.5], [19.0, 35.0],
            ]],
        },
        "ethical_notes": (
            "L'Impero Bizantino si autodefiniva 'Impero Romano' (Βασιλεία Ῥωμαίων). "
            "Il termine 'Bizantino' e' una costruzione storiografica occidentale "
            "del XVI secolo. name_original usa il nome che i suoi cittadini usavano. "
            "I confini mostrati sono del periodo medio (~1000 d.C.)."
        ),
        "name_variants": [
            {"name": "Byzantine Empire", "lang": "en", "context": "termine storiografico occidentale moderno",
             "source": "Encyclopaedia Britannica"},
            {"name": "Impero Bizantino", "lang": "it", "context": "termine italiano moderno",
             "source": "Enciclopedia Treccani"},
            {"name": "Eastern Roman Empire", "lang": "en", "context": "denominazione alternativa inglese",
             "source": "Oxford Dictionary of Byzantium"},
        ],
        "territory_changes": [
            {"year": 395, "region": "Mediterraneo orientale", "change_type": "INHERITANCE",
             "description": "Divisione dell'Impero Romano alla morte di Teodosio I.",
             "confidence_score": 0.90},
            {"year": 1204, "region": "Costantinopoli", "change_type": "CONQUEST_MILITARY",
             "description": "Quarta Crociata: sacco di Costantinopoli da parte dei crociati latini. Distruzione e saccheggio della capitale cristiana da parte di altri cristiani.",
             "confidence_score": 0.90},
        ],
        "sources": [
            {"citation": "Ostrogorsky, G. History of the Byzantine State (1969)", "source_type": "academic"},
            {"citation": "Norwich, J.J. Byzantium (1988-1995)", "source_type": "academic"},
        ],
    },
    # ─── 12. Impero Mughal ──────────────────────────────────────
    {
        "name_original": "مغلیہ سلطنت",
        "name_original_lang": "ur",
        "entity_type": "empire",
        "year_start": 1526,
        "year_end": 1857,
        "capital_name": "Delhi",
        "capital_lat": 28.6139,
        "capital_lon": 77.2090,
        "confidence_score": 0.80,
        "status": "confirmed",
        "boundary_geojson": {
            "type": "Polygon",
            "coordinates": [[
                [66.0, 25.0], [68.0, 30.0], [70.0, 35.0], [74.0, 36.0],
                [78.0, 34.0], [82.0, 27.0], [88.0, 25.0], [90.0, 22.0],
                [85.0, 18.0], [80.0, 14.0], [75.0, 12.0], [72.0, 18.0],
                [68.0, 22.0], [66.0, 25.0],
            ]],
        },
        "ethical_notes": (
            "ETHICS-001: il nome originale e' in Urdu. 'Mughal' deriva dal persiano "
            "per 'Mongolo' — la dinastia discendeva da Tamerlano e Gengis Khan. "
            "L'impero fu multireligioso sotto Akbar, poi progressivamente intollerante "
            "sotto Aurangzeb. I confini mostrati sono al periodo di massima espansione (~1700)."
        ),
        "name_variants": [
            {"name": "Mughal Empire", "lang": "en", "context": "denominazione inglese",
             "source": "Encyclopaedia Britannica"},
            {"name": "Impero Moghul", "lang": "it", "context": "denominazione italiana",
             "source": "Enciclopedia Treccani"},
            {"name": "گورکانیان", "lang": "fa", "period_start": 1526, "period_end": 1857,
             "context": "nome persiano (Gurkaniyan)", "source": "Richards, The Mughal Empire (1993)"},
        ],
        "territory_changes": [
            {"year": 1526, "region": "Nord India", "change_type": "CONQUEST_MILITARY",
             "description": "Babur sconfigge il Sultanato di Delhi nella battaglia di Panipat. Fondazione dell'Impero Mughal.",
             "confidence_score": 0.85},
            {"year": 1857, "region": "India", "change_type": "COLONIZATION",
             "description": "Ultimo imperatore Mughal deposto dalla Compagnia delle Indie Orientali dopo la rivolta dei Sepoy. Fine formale dell'impero.",
             "confidence_score": 0.90},
        ],
        "sources": [
            {"citation": "Richards, J.F. The Mughal Empire (1993)", "source_type": "academic"},
            {"citation": "Dalrymple, W. The Last Mughal (2006)", "source_type": "academic"},
        ],
    },
    # ─── 13. Impero Safavide ────────────────────────────────────
    {
        "name_original": "دولت صفویه",
        "name_original_lang": "fa",
        "entity_type": "empire",
        "year_start": 1501,
        "year_end": 1736,
        "capital_name": "Eṣfahān",
        "capital_lat": 32.6546,
        "capital_lon": 51.6680,
        "confidence_score": 0.75,
        "status": "confirmed",
        "boundary_geojson": {
            "type": "Polygon",
            "coordinates": [[
                [44.0, 30.0], [44.5, 34.0], [46.0, 37.0], [48.0, 39.0],
                [51.0, 40.0], [54.0, 38.5], [58.0, 37.5], [62.0, 36.0],
                [65.0, 34.0], [63.0, 29.0], [60.0, 26.0], [56.0, 25.0],
                [52.0, 26.0], [48.0, 28.0], [44.0, 30.0],
            ]],
        },
        "ethical_notes": (
            "L'Impero Safavide e' fondamentale per l'identità iraniana moderna. "
            "Impose lo sciismo come religione di stato — decisione con enormi "
            "conseguenze geopolitiche che persistono ancora oggi nella divisione "
            "sunnita-sciita. La conversione fu spesso forzata."
        ),
        "name_variants": [
            {"name": "Safavid Empire", "lang": "en", "context": "denominazione inglese",
             "source": "Encyclopaedia Britannica"},
            {"name": "Impero Safavide", "lang": "it", "context": "denominazione italiana",
             "source": "Enciclopedia Treccani"},
        ],
        "territory_changes": [
            {"year": 1501, "region": "Persia", "change_type": "CONQUEST_MILITARY",
             "description": "Ismail I conquista Tabriz e si proclama Shah. Imposizione dello sciismo duodecimano come religione di stato.",
             "confidence_score": 0.80},
        ],
        "sources": [
            {"citation": "Floor, W. & Herzig, E. Iran and the World in the Safavid Age (2012)", "source_type": "academic"},
            {"citation": "Matthee, R. Persia in Crisis: Safavid Decline (2012)", "source_type": "academic"},
        ],
    },
    # ─── 14. Shogunato Tokugawa ─────────────────────────────────
    {
        "name_original": "徳川幕府",
        "name_original_lang": "ja",
        "entity_type": "empire",
        "year_start": 1603,
        "year_end": 1868,
        "capital_name": "江戸",
        "capital_lat": 35.6762,
        "capital_lon": 139.6503,
        "confidence_score": 0.85,
        "status": "confirmed",
        "boundary_geojson": {
            "type": "Polygon",
            "coordinates": [[
                [129.5, 31.0], [130.0, 33.0], [131.0, 34.0], [132.5, 34.5],
                [135.0, 35.0], [137.0, 36.5], [139.5, 38.0], [140.5, 40.0],
                [141.5, 42.0], [142.0, 43.5], [145.0, 45.0], [145.5, 43.0],
                [144.0, 41.0], [142.0, 39.0], [141.0, 37.0], [140.5, 35.5],
                [140.0, 34.0], [138.0, 33.0], [135.0, 33.5], [132.0, 32.5],
                [130.5, 31.5], [129.5, 31.0],
            ]],
        },
        "ethical_notes": (
            "ETHICS-001: il nome originale e' in giapponese. Lo Shogunato manteneva "
            "un rigido sistema di caste (shi-nō-kō-shō) e un isolamento quasi totale "
            "(sakoku) dal 1639 al 1853. La popolazione Ainu di Hokkaido fu "
            "progressivamente colonizzata durante questo periodo."
        ),
        "name_variants": [
            {"name": "Tokugawa Shogunate", "lang": "en", "context": "denominazione inglese",
             "source": "Encyclopaedia Britannica"},
            {"name": "Shogunato Tokugawa", "lang": "it", "context": "denominazione italiana",
             "source": "Enciclopedia Treccani"},
            {"name": "Edo period", "lang": "en", "period_start": 1603, "period_end": 1868,
             "context": "nome del periodo storico dalla capitale Edo (Tokyo)",
             "source": "Totman, Early Modern Japan (1993)"},
        ],
        "territory_changes": [
            {"year": 1603, "region": "Giappone", "change_type": "REVOLUTION",
             "description": "Tokugawa Ieyasu unifica il Giappone dopo la battaglia di Sekigahara (1600) e viene nominato Shogun dall'Imperatore.",
             "confidence_score": 0.90},
            {"year": 1868, "region": "Giappone", "change_type": "REVOLUTION",
             "description": "Restaurazione Meiji: lo Shogunato cade e il potere torna all'Imperatore. Inizio della modernizzazione del Giappone.",
             "confidence_score": 0.95},
        ],
        "sources": [
            {"citation": "Totman, C. Early Modern Japan (1993)", "source_type": "academic"},
            {"citation": "Jansen, M. The Making of Modern Japan (2000)", "source_type": "academic"},
        ],
    },
    # ─── 15. Impero Qing ────────────────────────────────────────
    {
        "name_original": "大清帝國",
        "name_original_lang": "zh",
        "entity_type": "empire",
        "year_start": 1636,
        "year_end": 1912,
        "capital_name": "北京",
        "capital_lat": 39.9042,
        "capital_lon": 116.4074,
        "confidence_score": 0.85,
        "status": "confirmed",
        "boundary_geojson": {
            "type": "Polygon",
            "coordinates": [[
                [73.0, 40.0], [78.0, 44.0], [85.0, 48.0], [95.0, 50.0],
                [110.0, 52.0], [120.0, 53.0], [130.0, 48.0], [135.0, 43.0],
                [128.0, 38.0], [122.0, 33.0], [121.0, 28.0], [117.0, 24.0],
                [110.0, 20.0], [108.0, 18.0], [105.0, 22.0], [100.0, 22.0],
                [97.0, 28.0], [92.0, 28.0], [87.0, 28.0], [80.0, 32.0],
                [76.0, 36.0], [73.0, 40.0],
            ]],
        },
        "ethical_notes": (
            "ETHICS-001: il nome originale e' in cinese tradizionale. La dinastia Qing "
            "era mancese, non han — una distinzione etnica cruciale. L'espansione "
            "includeva la conquista del Tibet, del Xinjiang e della Mongolia, "
            "territori le cui popolazioni non si identificavano come 'cinesi'. "
            "Le Guerre dell'Oppio (1839-1860) rappresentano un punto di svolta "
            "nell'imperialismo occidentale in Asia."
        ),
        "name_variants": [
            {"name": "Qing Dynasty", "lang": "en", "context": "denominazione inglese",
             "source": "Encyclopaedia Britannica"},
            {"name": "Dinastia Qing", "lang": "it", "context": "denominazione italiana",
             "source": "Enciclopedia Treccani"},
            {"name": "ᡩᠠᡳᠴᡳᠩ ᡤᡠᡵᡠᠨ", "lang": "mnc", "context": "nome in lingua mancese (Daicing Gurun)",
             "source": "Elliott, The Manchu Way (2001)"},
        ],
        "territory_changes": [
            {"year": 1644, "region": "Cina", "change_type": "CONQUEST_MILITARY",
             "description": "I Mancesi conquistano Pechino e la dinastia Ming crolla. Violenza su larga scala durante la transizione; il taglio forzato della treccia (queue order) provoca resistenza e massacri.",
             "population_affected": 25000000, "confidence_score": 0.65},
            {"year": 1839, "region": "Cina meridionale", "change_type": "CONQUEST_MILITARY",
             "description": "Prima Guerra dell'Oppio: la Gran Bretagna attacca la Cina per mantenere il commercio di oppio. Trattato di Nanchino (1842): cessione forzata di Hong Kong.",
             "confidence_score": 0.90},
        ],
        "sources": [
            {"citation": "Elliott, M. The Manchu Way (2001)", "source_type": "academic"},
            {"citation": "Rowe, W. China's Last Empire: The Great Qing (2009)", "source_type": "academic"},
        ],
    },
    # ─── 16. Impero Russo ───────────────────────────────────────
    {
        "name_original": "Российская Империя",
        "name_original_lang": "ru",
        "entity_type": "empire",
        "year_start": 1721,
        "year_end": 1917,
        "capital_name": "Санкт-Петербург",
        "capital_lat": 59.9343,
        "capital_lon": 30.3351,
        "confidence_score": 0.85,
        "status": "confirmed",
        "boundary_geojson": {
            "type": "Polygon",
            "coordinates": [[
                [20.0, 45.0], [22.0, 50.0], [25.0, 55.0], [30.0, 60.0],
                [35.0, 65.0], [45.0, 70.0], [60.0, 72.0], [90.0, 73.0],
                [120.0, 70.0], [140.0, 65.0], [170.0, 65.0], [180.0, 62.0],
                [170.0, 55.0], [155.0, 50.0], [140.0, 45.0], [135.0, 42.0],
                [128.0, 43.0], [115.0, 45.0], [100.0, 48.0], [85.0, 50.0],
                [70.0, 48.0], [55.0, 42.0], [50.0, 38.0], [45.0, 40.0],
                [38.0, 42.0], [32.0, 44.0], [25.0, 44.0], [20.0, 45.0],
            ]],
        },
        "ethical_notes": (
            "L'Impero Russo si espanse attraverso la colonizzazione di territori "
            "abitati da centinaia di popoli diversi (Siberia, Caucaso, Asia Centrale). "
            "La conquista del Caucaso comportò deportazioni di massa (Circassi). "
            "Il servaggio (schiavitù di fatto) fu abolito solo nel 1861."
        ),
        "name_variants": [
            {"name": "Russian Empire", "lang": "en", "context": "denominazione inglese",
             "source": "Encyclopaedia Britannica"},
            {"name": "Impero Russo", "lang": "it", "context": "denominazione italiana",
             "source": "Enciclopedia Treccani"},
        ],
        "territory_changes": [
            {"year": 1721, "region": "Russia", "change_type": "TREATY",
             "description": "Trattato di Nystad: Pietro il Grande proclama l'Impero Russo dopo la vittoria sulla Svezia.",
             "confidence_score": 0.90},
            {"year": 1864, "region": "Caucaso", "change_type": "ETHNIC_CLEANSING",
             "description": "Espulsione dei Circassi dal Caucaso nord-occidentale. Si stima che 500.000-1.500.000 persone siano state deportate o uccise.",
             "population_affected": 1000000, "confidence_score": 0.70},
        ],
        "sources": [
            {"citation": "Lieven, D. Empire: The Russian Empire and Its Rivals (2000)", "source_type": "academic"},
            {"citation": "Richmond, W. The Circassian Genocide (2013)", "source_type": "academic"},
        ],
    },
    # ─── 17. Impero Azteco ──────────────────────────────────────
    {
        "name_original": "Ēxcān Tlahtōlōyān",
        "name_original_lang": "nah",
        "entity_type": "empire",
        "year_start": 1428,
        "year_end": 1521,
        "capital_name": "Tenochtitlan",
        "capital_lat": 19.4326,
        "capital_lon": -99.1332,
        "confidence_score": 0.70,
        "status": "confirmed",
        "boundary_geojson": {
            "type": "Polygon",
            "coordinates": [[
                [-99.5, 17.5], [-98.0, 16.5], [-96.0, 16.0], [-95.0, 17.0],
                [-94.5, 18.0], [-96.0, 19.5], [-97.5, 20.5], [-99.0, 21.0],
                [-100.5, 20.5], [-101.0, 19.5], [-100.5, 18.5], [-99.5, 17.5],
            ]],
        },
        "ethical_notes": (
            "ETHICS-001: il nome originale e' in nahuatl (Ēxcān Tlahtōlōyān = "
            "'Tripla Alleanza'). 'Impero Azteco' e' una semplificazione europea. "
            "Il confidence_score e' piu' basso perché le fonti scritte nahua "
            "pre-conquista sono limitate (i codici furono in larga parte distrutti "
            "dai conquistadores spagnoli). ETHICS-002: la conquista spagnola "
            "causò il crollo demografico piu' devastante della storia documentata."
        ),
        "name_variants": [
            {"name": "Aztec Empire", "lang": "en",
             "context": "denominazione europea — 'Azteco' deriva da Aztlán, luogo mitico di origine",
             "source": "Smith, The Aztecs (2012)"},
            {"name": "Impero Azteco", "lang": "it", "context": "denominazione italiana",
             "source": "Enciclopedia Treccani"},
            {"name": "Triple Alliance", "lang": "en",
             "context": "traduzione del nome nahuatl (alleanza Tenochtitlan-Texcoco-Tlacopan)",
             "source": "Hassig, Aztec Warfare (1988)"},
        ],
        "territory_changes": [
            {"year": 1521, "region": "Messico Centrale", "change_type": "COLONIZATION",
             "description": "Hernán Cortés conquista Tenochtitlan con alleati indigeni. Vaiolo e altre malattie europee devastano la popolazione: da ~25 milioni a ~1 milione in un secolo.",
             "population_affected": 24000000, "confidence_score": 0.65},
        ],
        "sources": [
            {"citation": "Smith, M.E. The Aztecs (2012)", "source_type": "academic"},
            {"citation": "Hassig, R. Aztec Warfare (1988)", "source_type": "academic"},
            {"citation": "León-Portilla, M. Visión de los Vencidos (1959)", "source_type": "primary"},
        ],
    },
    # ─── 18. Impero del Mali ────────────────────────────────────
    {
        "name_original": "Manden Kurufaba",
        "name_original_lang": "bm",
        "entity_type": "empire",
        "year_start": 1235,
        "year_end": 1600,
        "capital_name": "Niani",
        "capital_lat": 11.3833,
        "capital_lon": -8.6833,
        "confidence_score": 0.60,
        "status": "confirmed",
        "boundary_geojson": {
            "type": "Polygon",
            "coordinates": [[
                [-16.0, 12.0], [-15.0, 14.0], [-12.0, 16.0], [-8.0, 17.0],
                [-4.0, 17.5], [0.0, 17.0], [2.0, 15.0], [0.0, 12.0],
                [-4.0, 10.0], [-8.0, 9.0], [-12.0, 10.0], [-14.0, 11.0],
                [-16.0, 12.0],
            ]],
        },
        "ethical_notes": (
            "ETHICS-001: il nome originale e' in Bambara. Il confidence_score e' "
            "piu' basso perché la tradizione storiografica e' in parte orale "
            "(griot). Le fonti scritte principali sono arabe (Ibn Battuta, Al-Umari). "
            "Mansa Musa (r. 1312-1337) e' considerato tra le persone piu' ricche "
            "della storia — il suo pellegrinaggio alla Mecca nel 1324 causò inflazione "
            "in Egitto per il volume d'oro distribuito."
        ),
        "name_variants": [
            {"name": "Mali Empire", "lang": "en", "context": "denominazione inglese",
             "source": "Encyclopaedia Britannica"},
            {"name": "Impero del Mali", "lang": "it", "context": "denominazione italiana",
             "source": "Enciclopedia Treccani"},
        ],
        "territory_changes": [
            {"year": 1235, "region": "Africa Occidentale", "change_type": "CONQUEST_MILITARY",
             "description": "Sundiata Keita sconfigge il re Sumanguru nella battaglia di Kirina. Fondazione dell'Impero del Mali.",
             "confidence_score": 0.55},
        ],
        "sources": [
            {"citation": "Levtzion, N. Ancient Ghana and Mali (1973)", "source_type": "academic"},
            {"citation": "Ibn Battuta, Rihla (1354)", "source_type": "primary"},
            {"citation": "Niane, D.T. Sundiata: An Epic of Old Mali (1960)", "source_type": "primary"},
        ],
    },
    # ─── 19. Impero Khmer ──────────────────────────────────────
    {
        "name_original": "អាណាចក្រខ្មែរ",
        "name_original_lang": "km",
        "entity_type": "empire",
        "year_start": 802,
        "year_end": 1431,
        "capital_name": "Angkor",
        "capital_lat": 13.4125,
        "capital_lon": 103.8670,
        "confidence_score": 0.70,
        "status": "confirmed",
        "boundary_geojson": {
            "type": "Polygon",
            "coordinates": [[
                [100.0, 10.0], [100.5, 14.0], [102.0, 16.0], [104.0, 17.5],
                [106.5, 17.0], [108.0, 15.5], [107.5, 12.0], [106.0, 10.5],
                [104.0, 9.5], [102.0, 9.5], [100.0, 10.0],
            ]],
        },
        "ethical_notes": (
            "ETHICS-001: il nome originale e' in khmer. L'Impero Khmer costruì "
            "Angkor Wat, il piu' grande edificio religioso del mondo. Le cause "
            "del declino sono ancora dibattute (cambiamenti climatici, invasioni "
            "thai, crisi idrica). Il confidence_score riflette l'incertezza "
            "sulle fonti, in parte epigrafiche."
        ),
        "name_variants": [
            {"name": "Khmer Empire", "lang": "en", "context": "denominazione inglese",
             "source": "Encyclopaedia Britannica"},
            {"name": "Impero Khmer", "lang": "it", "context": "denominazione italiana",
             "source": "Enciclopedia Treccani"},
            {"name": "Angkor", "lang": "km", "context": "nome dalla capitale, spesso usato per l'intero impero",
             "source": "Higham, The Civilization of Angkor (2001)"},
        ],
        "territory_changes": [
            {"year": 802, "region": "Sud-Est Asiatico", "change_type": "REVOLUTION",
             "description": "Jayavarman II si proclama devaraja (re-dio) sul monte Kulen. Fondazione dell'Impero Khmer unificato.",
             "confidence_score": 0.65},
        ],
        "sources": [
            {"citation": "Higham, C. The Civilization of Angkor (2001)", "source_type": "academic"},
            {"citation": "Coe, M. Angkor and the Khmer Civilization (2003)", "source_type": "academic"},
        ],
    },
    # ─── 20. Taiwan (contestato) ────────────────────────────────
    {
        "name_original": "臺灣 / Taiwan",
        "name_original_lang": "zh",
        "entity_type": "disputed_territory",
        "year_start": 1949,
        "year_end": None,
        "capital_name": "Taipei",
        "capital_lat": 25.0330,
        "capital_lon": 121.5654,
        "confidence_score": 0.50,
        "status": "disputed",
        "boundary_geojson": {
            "type": "Polygon",
            "coordinates": [[
                [120.2, 22.0], [120.0, 23.0], [120.5, 24.5], [121.0, 25.3],
                [121.8, 25.3], [122.0, 24.5], [121.5, 23.0], [121.0, 22.0],
                [120.2, 22.0],
            ]],
        },
        "ethical_notes": (
            "ETHICS-003: Taiwan e' un territorio il cui status e' attivamente contestato. "
            "La Repubblica di Cina (ROC) governa de facto l'isola dal 1949, ma la "
            "Repubblica Popolare Cinese (PRC) la rivendica come propria provincia. "
            "La maggioranza degli stati ONU non riconosce Taiwan come stato indipendente "
            "ma mantiene relazioni commerciali de facto. Questo record non arbitra la disputa."
        ),
        "name_variants": [
            {"name": "Republic of China", "lang": "en", "period_start": 1949,
             "context": "nome ufficiale del governo che controlla l'isola",
             "source": "Costituzione della ROC"},
            {"name": "中華民國", "lang": "zh", "period_start": 1912,
             "context": "nome cinese della Repubblica di Cina",
             "source": "Costituzione della ROC"},
            {"name": "Chinese Taipei", "lang": "en",
             "context": "nome usato in contesti internazionali (Olimpiadi, OMS) per evitare conflitto diplomatico",
             "source": "Comitato Olimpico Internazionale"},
        ],
        "territory_changes": [
            {"year": 1949, "region": "Taiwan", "change_type": "REVOLUTION",
             "description": "Il governo della Repubblica di Cina si ritira a Taiwan dopo la vittoria comunista nella guerra civile cinese.",
             "confidence_score": 0.90},
        ],
        "sources": [
            {"citation": "Rigger, S. Why Taiwan Matters (2011)", "source_type": "academic"},
            {"citation": "Bush, R. Uncharted Strait: The Future of China-Taiwan Relations (2013)", "source_type": "academic"},
        ],
    },
    # ─── 21. Sahara Occidentale (contestato) ────────────────────
    {
        "name_original": "الصحراء الغربية / Sahara Occidental",
        "name_original_lang": "ar",
        "entity_type": "disputed_territory",
        "year_start": 1975,
        "year_end": None,
        "capital_name": None,
        "capital_lat": 24.2155,
        "capital_lon": -12.8858,
        "confidence_score": 0.40,
        "status": "disputed",
        "boundary_geojson": {
            "type": "Polygon",
            "coordinates": [[
                [-17.1, 21.4], [-17.0, 23.0], [-16.0, 24.0], [-14.8, 24.7],
                [-13.0, 24.0], [-12.0, 23.5], [-8.7, 21.3], [-12.0, 21.3],
                [-13.2, 21.4], [-15.0, 21.3], [-17.1, 21.4],
            ]],
        },
        "ethical_notes": (
            "ETHICS-003: il Sahara Occidentale e' l'ultimo territorio in Africa "
            "classificato come 'non autonomo' dall'ONU. Il Marocco occupa e "
            "amministra la maggior parte del territorio dal 1975. Il Fronte "
            "Polisario, sostenuto dall'Algeria, rivendica l'indipendenza come "
            "Repubblica Araba Sahrawi Democratica (RASD). Il referendum promesso "
            "dall'ONU non si e' mai tenuto. Questo record documenta entrambe le posizioni."
        ),
        "name_variants": [
            {"name": "Western Sahara", "lang": "en", "context": "denominazione internazionale ONU",
             "source": "Nazioni Unite"},
            {"name": "Sahara Occidental", "lang": "es", "context": "nome in spagnolo (ex colonia spagnola)",
             "source": "Nazioni Unite"},
            {"name": "الجمهورية العربية الصحراوية الديمقراطية", "lang": "ar",
             "context": "RASD — nome rivendicato dal Fronte Polisario",
             "source": "Fronte Polisario"},
        ],
        "territory_changes": [
            {"year": 1975, "region": "Sahara Occidentale", "change_type": "CONQUEST_MILITARY",
             "description": "Marcia Verde: il Marocco occupa il Sahara Occidentale dopo il ritiro della Spagna. Guerra con il Fronte Polisario fino al cessate il fuoco del 1991.",
             "population_affected": 170000, "confidence_score": 0.80},
        ],
        "sources": [
            {"citation": "Shelley, T. Endgame in the Western Sahara (2004)", "source_type": "academic"},
            {"citation": "Nazioni Unite, Risoluzione 690 (1991)", "source_type": "primary"},
        ],
    },
    # ─── 22. Impero Songhai ─────────────────────────────────────
    {
        "name_original": "Songhai",
        "name_original_lang": "ses",
        "entity_type": "empire",
        "year_start": 1464,
        "year_end": 1591,
        "capital_name": "Gao",
        "capital_lat": 16.2717,
        "capital_lon": -0.0433,
        "confidence_score": 0.60,
        "status": "confirmed",
        "boundary_geojson": {
            "type": "Polygon",
            "coordinates": [[
                [-12.0, 12.0], [-10.0, 15.0], [-5.0, 17.0], [0.0, 18.0],
                [4.0, 17.0], [4.0, 14.0], [2.0, 12.0], [-2.0, 11.0],
                [-6.0, 10.0], [-10.0, 11.0], [-12.0, 12.0],
            ]],
        },
        "ethical_notes": (
            "ETHICS-001: uno dei piu' grandi imperi africani precoloniali. "
            "Le universita' di Timbuktu (Sankore) erano centri di cultura "
            "islamica di importanza mondiale. Le fonti sono in parte arabe "
            "(Tarikh al-Sudan, Tarikh al-Fattash) e in parte orali."
        ),
        "name_variants": [
            {"name": "Songhai Empire", "lang": "en", "context": "denominazione inglese",
             "source": "Encyclopaedia Britannica"},
            {"name": "Impero Songhai", "lang": "it", "context": "denominazione italiana",
             "source": "Enciclopedia Treccani"},
        ],
        "territory_changes": [
            {"year": 1468, "region": "Timbuktu", "change_type": "CONQUEST_MILITARY",
             "description": "Sunni Ali conquista Timbuktu dall'Impero del Mali, espandendo il Songhai in tutta l'ansa del Niger.",
             "confidence_score": 0.60},
            {"year": 1591, "region": "Songhai", "change_type": "CONQUEST_MILITARY",
             "description": "Invasione marocchina: l'esercito saadiano con armi da fuoco sconfigge i Songhai nella battaglia di Tondibi. Fine dell'impero.",
             "confidence_score": 0.65},
        ],
        "sources": [
            {"citation": "Hunwick, J. Timbuktu and the Songhay Empire (1999)", "source_type": "academic"},
            {"citation": "al-Sadi, Tarikh al-Sudan (~1655)", "source_type": "primary"},
        ],
    },
    # ─── 23. Repubblica di Venezia ──────────────────────────────
    {
        "name_original": "Serenìsima Repùblega de Venèsia",
        "name_original_lang": "vec",
        "entity_type": "republic",
        "year_start": 697,
        "year_end": 1797,
        "capital_name": "Venèsia",
        "capital_lat": 45.4408,
        "capital_lon": 12.3155,
        "confidence_score": 0.85,
        "status": "confirmed",
        "boundary_geojson": {
            "type": "Point",
            "coordinates": [12.3155, 45.4408],
        },
        "ethical_notes": (
            "La Serenissima era una repubblica oligarchica, non democratica "
            "nel senso moderno. Solo i patrizi avevano diritto di voto. "
            "Venezia fu una potenza coloniale nel Mediterraneo orientale "
            "(Creta, Cipro, Dalmazia) e giocò un ruolo chiave nella "
            "Quarta Crociata che saccheggiò Costantinopoli nel 1204."
        ),
        "name_variants": [
            {"name": "Republic of Venice", "lang": "en", "context": "denominazione inglese",
             "source": "Encyclopaedia Britannica"},
            {"name": "Repubblica di Venezia", "lang": "it", "context": "denominazione italiana",
             "source": "Enciclopedia Treccani"},
        ],
        "territory_changes": [
            {"year": 1204, "region": "Costantinopoli", "change_type": "CONQUEST_MILITARY",
             "description": "Venezia devia la Quarta Crociata contro Costantinopoli. Saccheggio della capitale bizantina e acquisizione di territori nel Mediterraneo orientale.",
             "confidence_score": 0.90},
            {"year": 1797, "region": "Venezia", "change_type": "CONQUEST_MILITARY",
             "description": "Napoleone Bonaparte conquista Venezia. Fine della repubblica dopo 1100 anni. Trattato di Campoformio: Venezia ceduta all'Austria.",
             "confidence_score": 0.95},
        ],
        "sources": [
            {"citation": "Norwich, J.J. A History of Venice (1982)", "source_type": "academic"},
            {"citation": "Madden, T. Venice: A New History (2012)", "source_type": "academic"},
        ],
    },
    # ─── 24. Impero Etiope ──────────────────────────────────────
    {
        "name_original": "የኢትዮጵያ ንጉሠ ነገሥት መንግሥት",
        "name_original_lang": "am",
        "entity_type": "empire",
        "year_start": 1270,
        "year_end": 1974,
        "capital_name": "Addis Abeba",
        "capital_lat": 9.0250,
        "capital_lon": 38.7469,
        "confidence_score": 0.75,
        "status": "confirmed",
        "boundary_geojson": {
            "type": "Polygon",
            "coordinates": [[
                [33.0, 4.0], [34.0, 6.0], [36.0, 8.0], [38.0, 10.0],
                [40.0, 12.0], [42.0, 13.0], [44.0, 12.0], [46.0, 10.0],
                [48.0, 8.0], [47.0, 5.0], [45.0, 3.0], [42.0, 2.0],
                [39.0, 3.0], [36.0, 3.5], [33.0, 4.0],
            ]],
        },
        "ethical_notes": (
            "ETHICS-001: il nome originale e' in amarico. L'Etiopia e' uno dei "
            "pochissimi paesi africani mai colonizzati (Italia sconfitta ad Adua "
            "nel 1896; occupazione fascista 1936-1941 non riconosciuta). "
            "La dinastia Salomonide rivendicava discendenza dal Re Salomone e "
            "dalla Regina di Saba. L'impero includeva popoli diversi (Amhara, "
            "Oromo, Tigrinya, Somali) con tensioni etniche tuttora irrisolte."
        ),
        "name_variants": [
            {"name": "Ethiopian Empire", "lang": "en", "context": "denominazione inglese",
             "source": "Encyclopaedia Britannica"},
            {"name": "Impero Etiope", "lang": "it", "context": "denominazione italiana",
             "source": "Enciclopedia Treccani"},
            {"name": "Abyssinia", "lang": "en", "context": "nome europeo storico — considerato obsoleto e riduttivo",
             "source": "Marcus, A History of Ethiopia (2002)"},
        ],
        "territory_changes": [
            {"year": 1896, "region": "Adua", "change_type": "LIBERATION",
             "description": "Vittoria etiope contro l'Italia nella battaglia di Adua. L'Etiopia mantiene l'indipendenza — evento simbolo della resistenza africana al colonialismo.",
             "confidence_score": 0.90},
            {"year": 1936, "region": "Etiopia", "change_type": "CONQUEST_MILITARY",
             "description": "L'Italia fascista invade l'Etiopia usando gas tossici (vietati dalla Convenzione di Ginevra). Occupazione fino al 1941.",
             "population_affected": 760000, "confidence_score": 0.80},
        ],
        "sources": [
            {"citation": "Marcus, H. A History of Ethiopia (2002)", "source_type": "academic"},
            {"citation": "Pankhurst, R. The Ethiopians: A History (2001)", "source_type": "academic"},
        ],
    },
    # ─── 25. Crimea (contestata) ────────────────────────────────
    {
        "name_original": "Крим / Крым",
        "name_original_lang": "uk",
        "entity_type": "disputed_territory",
        "year_start": 2014,
        "year_end": None,
        "capital_name": None,
        "capital_lat": 44.9521,
        "capital_lon": 34.1024,
        "confidence_score": 0.35,
        "status": "disputed",
        "boundary_geojson": {
            "type": "Polygon",
            "coordinates": [[
                [32.5, 44.4], [32.8, 45.2], [33.5, 45.8], [34.5, 45.6],
                [35.2, 45.4], [36.0, 45.5], [36.6, 45.2], [36.5, 44.8],
                [35.8, 44.4], [35.0, 44.3], [34.0, 44.4], [33.0, 44.4],
                [32.5, 44.4],
            ]],
        },
        "ethical_notes": (
            "ETHICS-003: la Crimea e' un territorio attivamente contestato tra "
            "Ucraina e Russia. Annessa dalla Russia nel 2014 dopo un referendum "
            "non riconosciuto dalla comunità internazionale. L'Ucraina e la "
            "maggior parte degli stati ONU considerano la Crimea territorio "
            "ucraino sotto occupazione russa. name_original include sia la forma "
            "ucraina (Крим) che russa (Крым). Questo record non arbitra la disputa."
        ),
        "name_variants": [
            {"name": "Crimea", "lang": "en", "context": "denominazione internazionale",
             "source": "Nazioni Unite"},
            {"name": "Qırım", "lang": "crh", "context": "nome in lingua tartara di Crimea — popolazione indigena deportata in massa nel 1944",
             "source": "Williams, The Crimean Tatars (2001)"},
        ],
        "territory_changes": [
            {"year": 1944, "region": "Crimea", "change_type": "ETHNIC_CLEANSING",
             "description": "Stalin ordina la deportazione totale dei Tartari di Crimea in Asia Centrale. Si stima che il 18-46% sia morto durante il trasferimento o subito dopo.",
             "population_affected": 200000, "confidence_score": 0.85},
            {"year": 2014, "region": "Crimea", "change_type": "CONQUEST_MILITARY",
             "description": "Annessione russa della Crimea dopo l'intervento militare e un referendum contestato. Condannata come violazione del diritto internazionale dalla Risoluzione ONU 68/262.",
             "confidence_score": 0.90},
        ],
        "sources": [
            {"citation": "Williams, B.G. The Crimean Tatars (2001)", "source_type": "academic"},
            {"citation": "Nazioni Unite, Risoluzione 68/262 (2014)", "source_type": "primary"},
            {"citation": "Plokhy, S. The Gates of Europe: A History of Ukraine (2015)", "source_type": "academic"},
        ],
    },
    # ─── 26. Antico Egitto ──────────────────────────────────────
    {
        "name_original": "Kemet",
        "name_original_lang": "egy",
        "entity_type": "empire",
        "year_start": -3100,
        "year_end": -30,
        "capital_name": "Memphis / Thebes",
        "capital_lat": 29.8680,
        "capital_lon": 31.2559,
        "confidence_score": 0.80,
        "status": "confirmed",
        "boundary_geojson": {
            "type": "Polygon",
            "coordinates": [[
                [29.0, 22.0], [29.5, 24.0], [30.5, 26.0], [31.5, 28.0],
                [32.0, 30.0], [32.5, 31.5], [34.0, 31.5], [35.0, 30.0],
                [34.0, 28.0], [33.5, 26.0], [33.0, 24.0], [32.0, 22.0],
                [29.0, 22.0],
            ]],
        },
        "ethical_notes": (
            "ETHICS-001: il nome originale 'Kemet' (terra nera) e' il nome che gli "
            "antichi egizi usavano per il loro paese. 'Egitto' deriva dal greco "
            "Aigyptos. I confini variano enormemente nei 3000 anni di storia. "
            "Quelli mostrati sono una approssimazione del Nuovo Regno (~1400 a.C.)."
        ),
        "name_variants": [
            {"name": "Ancient Egypt", "lang": "en", "context": "denominazione inglese",
             "source": "Encyclopaedia Britannica"},
            {"name": "Antico Egitto", "lang": "it", "context": "denominazione italiana",
             "source": "Enciclopedia Treccani"},
            {"name": "Αἴγυπτος", "lang": "grc", "context": "nome greco, origine del termine moderno",
             "source": "Erodoto, Storie II"},
        ],
        "territory_changes": [
            {"year": -3100, "region": "Valle del Nilo", "change_type": "REVOLUTION",
             "description": "Unificazione dell'Alto e Basso Egitto tradizionalmente attribuita a Narmer/Menes.",
             "confidence_score": 0.55},
            {"year": -30, "region": "Egitto", "change_type": "CONQUEST_MILITARY",
             "description": "Conquista romana dopo la sconfitta di Cleopatra VII e Marco Antonio. L'Egitto diventa provincia romana.",
             "confidence_score": 0.90},
        ],
        "sources": [
            {"citation": "Shaw, I. The Oxford History of Ancient Egypt (2000)", "source_type": "academic"},
            {"citation": "Erodoto, Storie, Libro II", "source_type": "primary"},
        ],
    },
    # ─── 27. Impero Persiano Achemenide ─────────────────────────
    {
        "name_original": "Xšāça",
        "name_original_lang": "peo",
        "entity_type": "empire",
        "year_start": -550,
        "year_end": -330,
        "capital_name": "Persepolis",
        "capital_lat": 29.9352,
        "capital_lon": 52.8914,
        "confidence_score": 0.80,
        "status": "confirmed",
        "boundary_geojson": {
            "type": "Polygon",
            "coordinates": [[
                [26.0, 30.0], [28.0, 35.0], [30.0, 38.0], [35.0, 40.0],
                [42.0, 40.5], [50.0, 40.0], [55.0, 38.0], [62.0, 37.0],
                [68.0, 35.0], [72.0, 30.0], [68.0, 25.0], [60.0, 24.0],
                [52.0, 25.0], [45.0, 28.0], [38.0, 30.0], [34.0, 31.0],
                [30.0, 30.5], [26.0, 30.0],
            ]],
        },
        "ethical_notes": (
            "ETHICS-001: il nome in antico persiano (Xšāça = 'il regno') e' il "
            "nome proprio. 'Persia' e' la forma greca. L'Impero Achemenide sotto "
            "Ciro il Grande pratico' una politica relativamente tollerante verso "
            "i popoli conquistati (Cilindro di Ciro), pur restando un impero "
            "costruito sulla conquista militare."
        ),
        "name_variants": [
            {"name": "Achaemenid Empire", "lang": "en", "context": "denominazione inglese",
             "source": "Encyclopaedia Britannica"},
            {"name": "Impero Persiano", "lang": "it", "context": "denominazione italiana",
             "source": "Enciclopedia Treccani"},
            {"name": "هخامنشیان", "lang": "fa", "context": "nome persiano moderno",
             "source": "Briant, From Cyrus to Alexander (2002)"},
        ],
        "territory_changes": [
            {"year": -550, "region": "Media", "change_type": "CONQUEST_MILITARY",
             "description": "Ciro II sconfigge i Medi e fonda l'Impero Persiano.",
             "confidence_score": 0.80},
            {"year": -330, "region": "Persia", "change_type": "CONQUEST_MILITARY",
             "description": "Alessandro Magno sconfigge Dario III. Fine dell'Impero Achemenide.",
             "confidence_score": 0.90},
        ],
        "sources": [
            {"citation": "Briant, P. From Cyrus to Alexander (2002)", "source_type": "academic"},
            {"citation": "Erodoto, Storie, Libri I-VII", "source_type": "primary"},
        ],
    },
    # ─── 28. Impero Spagnolo ────────────────────────────────────
    {
        "name_original": "Imperio Español",
        "name_original_lang": "es",
        "entity_type": "empire",
        "year_start": 1492,
        "year_end": 1898,
        "capital_name": "Madrid",
        "capital_lat": 40.4168,
        "capital_lon": -3.7038,
        "confidence_score": 0.85,
        "status": "confirmed",
        "boundary_geojson": {
            "type": "Point",
            "coordinates": [-3.7038, 40.4168],
        },
        "ethical_notes": (
            "ETHICS-002: il piu' grande impero coloniale della storia pre-britannica. "
            "La conquista delle Americhe causo' il crollo demografico piu' catastrofico "
            "della storia: si stima 90% della popolazione indigena morta in un secolo "
            "per malattie, guerra e sfruttamento. Il sistema delle encomiendas fu "
            "schiavitu' de facto. I confini non sono mostrati come poligono per la "
            "vastita' e dispersione dell'impero (4 continenti)."
        ),
        "name_variants": [
            {"name": "Spanish Empire", "lang": "en", "context": "denominazione inglese",
             "source": "Encyclopaedia Britannica"},
            {"name": "Impero Spagnolo", "lang": "it", "context": "denominazione italiana",
             "source": "Enciclopedia Treccani"},
        ],
        "territory_changes": [
            {"year": 1492, "region": "Americhe", "change_type": "COLONIZATION",
             "description": "Colombo raggiunge le Americhe. Inizio della colonizzazione spagnola del continente.",
             "confidence_score": 0.95},
            {"year": 1521, "region": "Messico", "change_type": "CONQUEST_MILITARY",
             "description": "Cortés conquista l'Impero Azteco. Distruzione di Tenochtitlan.",
             "population_affected": 24000000, "confidence_score": 0.70},
            {"year": 1898, "region": "Cuba, Filippine, Porto Rico", "change_type": "CESSION_FORCED",
             "description": "Guerra ispano-americana: la Spagna cede le ultime colonie. Fine dell'impero.",
             "confidence_score": 0.95},
        ],
        "sources": [
            {"citation": "Kamen, H. Empire: How Spain Became a World Power (2003)", "source_type": "academic"},
            {"citation": "Las Casas, B. Brevísima Relación de la Destruición de las Indias (1552)", "source_type": "primary"},
        ],
    },
    # ─── 29. Gran Bretagna / Impero Britannico ──────────────────
    {
        "name_original": "British Empire",
        "name_original_lang": "en",
        "entity_type": "empire",
        "year_start": 1583,
        "year_end": 1997,
        "capital_name": "London",
        "capital_lat": 51.5074,
        "capital_lon": -0.1278,
        "confidence_score": 0.90,
        "status": "confirmed",
        "boundary_geojson": {
            "type": "Point",
            "coordinates": [-0.1278, 51.5074],
        },
        "ethical_notes": (
            "ETHICS-002: il piu' grande impero della storia per estensione (~35 milioni km²). "
            "Responsabile di colonizzazione, schiavitu' transatlantica, carestie indotte "
            "(Bengala 1943: 2-3 milioni di morti), repressione di movimenti indipendentisti. "
            "I confini non sono mostrati come poligono per la vastita' (tutti i continenti). "
            "Il British Raj (India) e' un'entita' separata nel database."
        ),
        "name_variants": [
            {"name": "Impero Britannico", "lang": "it", "context": "denominazione italiana",
             "source": "Enciclopedia Treccani"},
        ],
        "territory_changes": [
            {"year": 1757, "region": "Bengala", "change_type": "CONQUEST_MILITARY",
             "description": "Battaglia di Plassey: la Compagnia delle Indie Orientali conquista il Bengala. Inizio del dominio britannico in India.",
             "confidence_score": 0.90},
            {"year": 1997, "region": "Hong Kong", "change_type": "TREATY",
             "description": "Restituzione di Hong Kong alla Cina. Fine formale dell'Impero Britannico.",
             "confidence_score": 0.95},
        ],
        "sources": [
            {"citation": "Ferguson, N. Empire: How Britain Made the Modern World (2003)", "source_type": "academic"},
            {"citation": "Tharoor, S. Inglorious Empire (2017)", "source_type": "academic"},
        ],
    },
    # ─── 30. Sacro Romano Impero ────────────────────────────────
    {
        "name_original": "Sacrum Imperium Romanum",
        "name_original_lang": "la",
        "entity_type": "empire",
        "year_start": 800,
        "year_end": 1806,
        "capital_name": "Wien",
        "capital_lat": 48.2082,
        "capital_lon": 16.3738,
        "confidence_score": 0.80,
        "status": "confirmed",
        "boundary_geojson": {
            "type": "Polygon",
            "coordinates": [[
                [2.0, 46.0], [4.0, 49.0], [6.0, 51.0], [8.0, 54.0],
                [10.0, 55.0], [12.0, 54.5], [14.0, 54.0], [16.0, 51.0],
                [17.0, 49.0], [16.5, 47.0], [15.0, 46.0], [13.0, 46.5],
                [11.0, 46.0], [9.0, 46.0], [6.0, 45.5], [3.0, 45.0],
                [2.0, 46.0],
            ]],
        },
        "ethical_notes": (
            "Voltaire scrisse che non era 'né sacro, né romano, né un impero'. "
            "Struttura politica estremamente frammentata con centinaia di entita' "
            "semi-indipendenti. I confini mostrati sono molto approssimativi "
            "per la natura fluida del territorio."
        ),
        "name_variants": [
            {"name": "Holy Roman Empire", "lang": "en", "context": "denominazione inglese",
             "source": "Encyclopaedia Britannica"},
            {"name": "Sacro Romano Impero", "lang": "it", "context": "denominazione italiana",
             "source": "Enciclopedia Treccani"},
            {"name": "Heiliges Römisches Reich", "lang": "de", "context": "nome tedesco",
             "source": "Wilson, Heart of Europe (2016)"},
        ],
        "territory_changes": [
            {"year": 800, "region": "Europa Centrale", "change_type": "TREATY",
             "description": "Incoronazione di Carlo Magno a Roma da parte di Papa Leone III. Fondazione tradizionale.",
             "confidence_score": 0.85},
            {"year": 1806, "region": "Europa Centrale", "change_type": "CONQUEST_MILITARY",
             "description": "Napoleone forza la dissoluzione dell'Impero dopo la battaglia di Austerlitz.",
             "confidence_score": 0.95},
        ],
        "sources": [
            {"citation": "Wilson, P. Heart of Europe: A History of the Holy Roman Empire (2016)", "source_type": "academic"},
            {"citation": "Whaley, J. Germany and the Holy Roman Empire (2012)", "source_type": "academic"},
        ],
    },
    # ─── 31. Califfato Abbaside ─────────────────────────────────
    {
        "name_original": "الخلافة العباسية",
        "name_original_lang": "ar",
        "entity_type": "empire",
        "year_start": 750,
        "year_end": 1258,
        "capital_name": "بغداد",
        "capital_lat": 33.3152,
        "capital_lon": 44.3661,
        "confidence_score": 0.75,
        "status": "confirmed",
        "boundary_geojson": {
            "type": "Polygon",
            "coordinates": [[
                [25.0, 30.0], [28.0, 34.0], [32.0, 37.0], [38.0, 38.0],
                [45.0, 37.5], [52.0, 38.0], [58.0, 37.0], [62.0, 35.0],
                [65.0, 30.0], [62.0, 25.0], [55.0, 22.0], [48.0, 20.0],
                [42.0, 15.0], [38.0, 14.0], [35.0, 20.0], [32.0, 25.0],
                [28.0, 28.0], [25.0, 30.0],
            ]],
        },
        "ethical_notes": (
            "ETHICS-001: il nome originale e' in arabo. L'era abbaside e' considerata "
            "l'eta' d'oro islamica: Baghdad era la citta' piu' grande del mondo e un "
            "centro di scienza, filosofia e letteratura. I confini variano enormemente "
            "nei 500 anni di esistenza; quelli mostrati sono del periodo iniziale (~800)."
        ),
        "name_variants": [
            {"name": "Abbasid Caliphate", "lang": "en", "context": "denominazione inglese",
             "source": "Encyclopaedia Britannica"},
            {"name": "Califfato Abbaside", "lang": "it", "context": "denominazione italiana",
             "source": "Enciclopedia Treccani"},
        ],
        "territory_changes": [
            {"year": 750, "region": "Medio Oriente", "change_type": "REVOLUTION",
             "description": "Rivoluzione abbaside: rovesciamento degli Omayyadi. Trasferimento della capitale a Baghdad.",
             "confidence_score": 0.85},
            {"year": 1258, "region": "Baghdad", "change_type": "CONQUEST_MILITARY",
             "description": "Sacco di Baghdad da parte dei Mongoli sotto Hulagu Khan. Fine del Califfato. Distruzione della biblioteca e massacro stimato in centinaia di migliaia di vittime.",
             "population_affected": 200000, "confidence_score": 0.60},
        ],
        "sources": [
            {"citation": "Kennedy, H. When Baghdad Ruled the Muslim World (2004)", "source_type": "academic"},
            {"citation": "al-Tabari, Tarikh al-Rusul wa al-Muluk", "source_type": "primary"},
        ],
    },
    # ─── 32. Impero del Giappone (moderno) ──────────────────────
    {
        "name_original": "大日本帝國",
        "name_original_lang": "ja",
        "entity_type": "empire",
        "year_start": 1868,
        "year_end": 1947,
        "capital_name": "東京",
        "capital_lat": 35.6762,
        "capital_lon": 139.6503,
        "confidence_score": 0.90,
        "status": "confirmed",
        "boundary_geojson": {
            "type": "Polygon",
            "coordinates": [[
                [123.0, 24.0], [127.0, 26.0], [129.5, 31.0], [131.0, 34.0],
                [135.0, 35.5], [140.0, 38.0], [142.0, 43.0], [145.0, 45.5],
                [145.5, 43.0], [141.5, 39.0], [140.5, 35.0], [137.0, 33.0],
                [132.0, 32.0], [128.0, 28.0], [123.0, 24.0],
            ]],
        },
        "ethical_notes": (
            "ETHICS-002: l'Impero del Giappone fu responsabile di crimini di guerra "
            "estesi: massacro di Nanchino (1937, 200.000-300.000 vittime), sistema "
            "delle comfort women, esperimenti dell'Unità 731, brutalita' nei campi "
            "di prigionia. Distinzione dal Giappone Tokugawa (entita' separata)."
        ),
        "name_variants": [
            {"name": "Empire of Japan", "lang": "en", "context": "denominazione inglese",
             "source": "Encyclopaedia Britannica"},
            {"name": "Impero del Giappone", "lang": "it", "context": "denominazione italiana",
             "source": "Enciclopedia Treccani"},
        ],
        "territory_changes": [
            {"year": 1910, "region": "Corea", "change_type": "COLONIZATION",
             "description": "Annessione della Corea. Repressione della cultura e lingua coreana per 35 anni.",
             "population_affected": 17000000, "confidence_score": 0.90},
            {"year": 1937, "region": "Nanchino", "change_type": "CONQUEST_MILITARY",
             "description": "Massacro di Nanchino: l'esercito imperiale massacra civili e prigionieri di guerra cinesi.",
             "population_affected": 300000, "confidence_score": 0.80},
        ],
        "sources": [
            {"citation": "Bix, H. Hirohito and the Making of Modern Japan (2000)", "source_type": "academic"},
            {"citation": "Chang, I. The Rape of Nanking (1997)", "source_type": "academic"},
        ],
    },
    # ─── 33. Granducato di Lituania ─────────────────────────────
    {
        "name_original": "Lietuvos Didžioji Kunigaikštystė",
        "name_original_lang": "lt",
        "entity_type": "kingdom",
        "year_start": 1236,
        "year_end": 1795,
        "capital_name": "Vilnius",
        "capital_lat": 54.6872,
        "capital_lon": 25.2797,
        "confidence_score": 0.75,
        "status": "confirmed",
        "boundary_geojson": {
            "type": "Polygon",
            "coordinates": [[
                [20.5, 52.0], [22.0, 54.0], [24.0, 56.0], [26.0, 56.5],
                [28.0, 55.5], [31.0, 54.0], [33.0, 52.5], [32.0, 50.0],
                [28.0, 48.5], [25.0, 49.0], [22.0, 50.5], [20.5, 52.0],
            ]],
        },
        "ethical_notes": (
            "Il Granducato di Lituania fu il piu' grande stato d'Europa nel XV secolo. "
            "Multietnico e multireligioso, includeva lituani, ruteni, polacchi e tartari. "
            "L'unione con la Polonia (1569, Unione di Lublino) creo' la Confederazione "
            "polacco-lituana."
        ),
        "name_variants": [
            {"name": "Grand Duchy of Lithuania", "lang": "en", "context": "denominazione inglese",
             "source": "Encyclopaedia Britannica"},
            {"name": "Granducato di Lituania", "lang": "it", "context": "denominazione italiana",
             "source": "Enciclopedia Treccani"},
        ],
        "territory_changes": [
            {"year": 1569, "region": "Polonia-Lituania", "change_type": "TREATY",
             "description": "Unione di Lublino: fusione con il Regno di Polonia nella Confederazione polacco-lituana.",
             "confidence_score": 0.85},
            {"year": 1795, "region": "Lituania", "change_type": "CONQUEST_MILITARY",
             "description": "Terza spartizione della Polonia: la Lituania e' divisa tra Russia, Prussia e Austria.",
             "confidence_score": 0.90},
        ],
        "sources": [
            {"citation": "Rowell, S.C. Lithuania Ascending (1994)", "source_type": "academic"},
            {"citation": "Stone, D. The Polish-Lithuanian State, 1386-1795 (2001)", "source_type": "academic"},
        ],
    },
    # ─── 34. Impero Zulu ────────────────────────────────────────
    {
        "name_original": "KwaZulu",
        "name_original_lang": "zu",
        "entity_type": "kingdom",
        "year_start": 1816,
        "year_end": 1897,
        "capital_name": "KwaBulawayo",
        "capital_lat": -28.3,
        "capital_lon": 31.0,
        "confidence_score": 0.70,
        "status": "confirmed",
        "boundary_geojson": {
            "type": "Polygon",
            "coordinates": [[
                [29.0, -27.0], [29.5, -28.0], [30.0, -29.5], [31.0, -30.0],
                [32.5, -29.5], [32.8, -28.0], [32.0, -27.0], [31.0, -26.5],
                [30.0, -26.5], [29.0, -27.0],
            ]],
        },
        "ethical_notes": (
            "ETHICS-001: il nome in lingua zulu. Il regno di Shaka Zulu unifico' "
            "le comunita' nguni in un potente stato militare. Il Mfecane "
            "(dispersione violenta di popoli) associato all'espansione zulu e' "
            "dibattuto: la storiografia coloniale lo esagero' per giustificare "
            "l'occupazione europea dei territori 'spopolati'."
        ),
        "name_variants": [
            {"name": "Zulu Kingdom", "lang": "en", "context": "denominazione inglese",
             "source": "Encyclopaedia Britannica"},
            {"name": "Regno Zulu", "lang": "it", "context": "denominazione italiana",
             "source": "Enciclopedia Treccani"},
        ],
        "territory_changes": [
            {"year": 1879, "region": "KwaZulu", "change_type": "CONQUEST_MILITARY",
             "description": "Guerra anglo-zulu: dopo la vittoria zulu a Isandlwana, la Gran Bretagna conquista e smembra il regno.",
             "confidence_score": 0.85},
        ],
        "sources": [
            {"citation": "Laband, J. The Rise and Fall of the Zulu Nation (1997)", "source_type": "academic"},
            {"citation": "Morris, D. The Washing of the Spears (1965)", "source_type": "academic"},
        ],
    },
    # ─── 35. Tibet (contestato) ─────────────────────────────────
    {
        "name_original": "བོད",
        "name_original_lang": "bo",
        "entity_type": "disputed_territory",
        "year_start": 1950,
        "year_end": None,
        "capital_name": "Lhasa",
        "capital_lat": 29.6520,
        "capital_lon": 91.1721,
        "confidence_score": 0.40,
        "status": "disputed",
        "boundary_geojson": {
            "type": "Polygon",
            "coordinates": [[
                [78.0, 30.0], [80.0, 32.0], [84.0, 33.5], [88.0, 34.0],
                [92.0, 34.5], [96.0, 34.0], [99.0, 33.0], [102.0, 30.0],
                [99.0, 28.0], [96.0, 27.5], [92.0, 27.0], [88.0, 27.5],
                [84.0, 28.0], [80.0, 29.0], [78.0, 30.0],
            ]],
        },
        "ethical_notes": (
            "ETHICS-003: il Tibet e' un territorio attivamente contestato. La Cina "
            "lo considera una 'regione autonoma' della RPC. Il Governo Tibetano in "
            "Esilio (Dharamsala, India) e molte organizzazioni internazionali "
            "contestano l'annessione del 1950. Il Dalai Lama e' in esilio dal 1959. "
            "Restrizioni alla liberta' religiosa e culturale sono documentate."
        ),
        "name_variants": [
            {"name": "Tibet", "lang": "en", "context": "denominazione internazionale",
             "source": "Encyclopaedia Britannica"},
            {"name": "西藏", "lang": "zh", "context": "nome cinese (Xīzàng)",
             "source": "Goldstein, A History of Modern Tibet (1989)"},
        ],
        "territory_changes": [
            {"year": 1950, "region": "Tibet", "change_type": "CONQUEST_MILITARY",
             "description": "L'Esercito Popolare di Liberazione invade il Tibet. L'Accordo in 17 Punti (1951) e' considerato firmato sotto coercizione.",
             "confidence_score": 0.85},
            {"year": 1959, "region": "Lhasa", "change_type": "CONQUEST_MILITARY",
             "description": "Rivolta tibetana repressa. Il Dalai Lama fugge in India. Inizio dell'esilio.",
             "population_affected": 86000, "confidence_score": 0.75},
        ],
        "sources": [
            {"citation": "Goldstein, M. A History of Modern Tibet (1989)", "source_type": "academic"},
            {"citation": "Shakya, T. The Dragon in the Land of Snows (1999)", "source_type": "academic"},
        ],
    },
    # ─── 36. Carthago ───────────────────────────────────────────
    {
        "name_original": "Qart-ḥadašt",
        "name_original_lang": "xpu",
        "entity_type": "republic",
        "year_start": -814,
        "year_end": -146,
        "capital_name": "Qart-ḥadašt",
        "capital_lat": 36.8528,
        "capital_lon": 10.3234,
        "confidence_score": 0.70,
        "status": "confirmed",
        "boundary_geojson": {
            "type": "Polygon",
            "coordinates": [[
                [-2.0, 35.5], [0.0, 37.0], [3.0, 38.0], [6.0, 37.5],
                [9.0, 37.0], [11.0, 37.5], [14.0, 36.0], [11.0, 33.0],
                [9.0, 32.0], [5.0, 33.5], [1.0, 34.5], [-2.0, 35.5],
            ]],
        },
        "ethical_notes": (
            "ETHICS-001: il nome fenicio Qart-ḥadašt = 'citta' nuova'. Le fonti "
            "su Cartagine sono quasi esclusivamente romane (i vincitori). La "
            "storiografia fenicia e' andata perduta con la distruzione della citta'. "
            "Questo e' un esempio critico di ETHICS-002: la storia scritta dai vincitori."
        ),
        "name_variants": [
            {"name": "Carthage", "lang": "en", "context": "denominazione inglese dal latino Carthago",
             "source": "Encyclopaedia Britannica"},
            {"name": "Cartagine", "lang": "it", "context": "denominazione italiana",
             "source": "Enciclopedia Treccani"},
            {"name": "Καρχηδών", "lang": "grc", "context": "nome greco",
             "source": "Polibio, Storie"},
        ],
        "territory_changes": [
            {"year": -146, "region": "Nord Africa", "change_type": "GENOCIDE",
             "description": "Terza Guerra Punica: Roma distrugge completamente Cartagine. La citta' e' rasa al suolo, la popolazione superstite venduta come schiava.",
             "population_affected": 500000, "confidence_score": 0.65},
        ],
        "sources": [
            {"citation": "Hoyos, D. The Carthaginians (2010)", "source_type": "academic"},
            {"citation": "Polibio, Storie, Libri I-III", "source_type": "primary"},
        ],
    },
    # ─── 37. Impero Maurya ──────────────────────────────────────
    {
        "name_original": "मौर्य साम्राज्य",
        "name_original_lang": "sa",
        "entity_type": "empire",
        "year_start": -322,
        "year_end": -185,
        "capital_name": "Pāṭaliputra",
        "capital_lat": 25.6100,
        "capital_lon": 85.1400,
        "confidence_score": 0.70,
        "status": "confirmed",
        "boundary_geojson": {
            "type": "Polygon",
            "coordinates": [[
                [66.0, 25.0], [68.0, 30.0], [72.0, 34.0], [78.0, 34.0],
                [84.0, 28.0], [88.0, 24.0], [86.0, 20.0], [80.0, 14.0],
                [76.0, 10.0], [73.0, 14.0], [70.0, 20.0], [66.0, 25.0],
            ]],
        },
        "ethical_notes": (
            "ETHICS-001: il nome in sanscrito. L'Impero Maurya sotto Ashoka e' "
            "notevole per la conversione al buddismo dopo la conquista del Kalinga "
            "(~260.000 morti). Gli Editti di Ashoka rappresentano uno dei primi "
            "documenti di governance etica nella storia. Il confidence_score "
            "riflette la dipendenza da fonti archeologiche e agiografiche."
        ),
        "name_variants": [
            {"name": "Maurya Empire", "lang": "en", "context": "denominazione inglese",
             "source": "Encyclopaedia Britannica"},
            {"name": "Impero Maurya", "lang": "it", "context": "denominazione italiana",
             "source": "Enciclopedia Treccani"},
        ],
        "territory_changes": [
            {"year": -261, "region": "Kalinga", "change_type": "CONQUEST_MILITARY",
             "description": "Ashoka conquista il Kalinga. La brutalita' della guerra lo porta alla conversione al buddismo e all'adozione del dharma come principio di governo.",
             "population_affected": 260000, "confidence_score": 0.60},
        ],
        "sources": [
            {"citation": "Thapar, R. Asoka and the Decline of the Mauryas (1961)", "source_type": "academic"},
            {"citation": "Editti di Ashoka (III secolo a.C.)", "source_type": "primary"},
        ],
    },
    # ─── 38. Gran Colombia ──────────────────────────────────────
    {
        "name_original": "Gran Colombia",
        "name_original_lang": "es",
        "entity_type": "republic",
        "year_start": 1819,
        "year_end": 1831,
        "capital_name": "Bogotá",
        "capital_lat": 4.7110,
        "capital_lon": -74.0721,
        "confidence_score": 0.80,
        "status": "confirmed",
        "boundary_geojson": {
            "type": "Polygon",
            "coordinates": [[
                [-80.0, 2.0], [-79.0, 4.0], [-77.0, 7.0], [-75.0, 10.0],
                [-72.0, 12.0], [-68.0, 12.5], [-63.0, 11.0], [-60.0, 8.0],
                [-60.0, 2.0], [-65.0, 0.0], [-70.0, -2.0], [-75.0, -4.0],
                [-78.0, -3.0], [-80.0, 0.0], [-80.0, 2.0],
            ]],
        },
        "ethical_notes": (
            "ETHICS-001: la Gran Colombia di Simón Bolívar fu uno dei progetti "
            "politici piu' ambiziosi del XIX secolo: unire Venezuela, Colombia, "
            "Ecuador e Panama. Duro' solo 12 anni. E' un esempio di come le "
            "lotte di liberazione dal colonialismo non sempre portano a stabilita'."
        ),
        "name_variants": [
            {"name": "Republic of Colombia", "lang": "en", "context": "nome ufficiale",
             "source": "Encyclopaedia Britannica"},
            {"name": "Gran Colombia", "lang": "it", "context": "termine storiografico per distinguerla dalla Colombia attuale",
             "source": "Enciclopedia Treccani"},
        ],
        "territory_changes": [
            {"year": 1819, "region": "Sud America settentrionale", "change_type": "LIBERATION",
             "description": "Bolívar sconfigge gli spagnoli nella battaglia di Boyacá. Proclamazione della Gran Colombia.",
             "confidence_score": 0.90},
            {"year": 1831, "region": "Gran Colombia", "change_type": "REVOLUTION",
             "description": "Dissoluzione della Gran Colombia in Venezuela, Colombia (con Panama) ed Ecuador.",
             "confidence_score": 0.90},
        ],
        "sources": [
            {"citation": "Lynch, J. Simón Bolívar: A Life (2006)", "source_type": "academic"},
            {"citation": "Arana, M. Bolivar: American Liberator (2013)", "source_type": "academic"},
        ],
    },
    # ─── 39. Cipro del Nord (contestato) ────────────────────────
    {
        "name_original": "Kuzey Kıbrıs Türk Cumhuriyeti",
        "name_original_lang": "tr",
        "entity_type": "disputed_territory",
        "year_start": 1983,
        "year_end": None,
        "capital_name": "Lefkoşa",
        "capital_lat": 35.1856,
        "capital_lon": 33.3823,
        "confidence_score": 0.35,
        "status": "disputed",
        "boundary_geojson": {
            "type": "Polygon",
            "coordinates": [[
                [32.3, 35.05], [33.0, 35.1], [33.6, 35.2], [34.1, 35.5],
                [34.6, 35.6], [34.6, 35.35], [34.0, 35.1], [33.5, 34.95],
                [32.8, 34.95], [32.3, 35.05],
            ]],
        },
        "ethical_notes": (
            "ETHICS-003: la Repubblica Turca di Cipro del Nord e' riconosciuta "
            "solo dalla Turchia. L'ONU e la comunita' internazionale riconoscono "
            "la sovranita' della Repubblica di Cipro sull'intera isola. La "
            "divisione risale all'invasione turca del 1974 dopo il colpo di "
            "stato greco-cipriota. Questo record documenta entrambe le posizioni."
        ),
        "name_variants": [
            {"name": "Northern Cyprus", "lang": "en", "context": "denominazione internazionale comune",
             "source": "Nazioni Unite"},
            {"name": "Cipro del Nord", "lang": "it", "context": "denominazione italiana",
             "source": "Enciclopedia Treccani"},
        ],
        "territory_changes": [
            {"year": 1974, "region": "Cipro settentrionale", "change_type": "CONQUEST_MILITARY",
             "description": "Invasione turca di Cipro dopo il colpo di stato greco-cipriota. Circa 200.000 greco-ciprioti sfollati dal nord.",
             "population_affected": 200000, "confidence_score": 0.85},
        ],
        "sources": [
            {"citation": "Ker-Lindsay, J. The Cyprus Problem (2011)", "source_type": "academic"},
            {"citation": "Nazioni Unite, Risoluzione 541 (1983)", "source_type": "primary"},
        ],
    },
    # ─── 40. Confederazione Irochese ────────────────────────────
    {
        "name_original": "Haudenosaunee",
        "name_original_lang": "moh",
        "entity_type": "confederation",
        "year_start": 1142,
        "year_end": None,
        "capital_name": "Onondaga",
        "capital_lat": 42.9700,
        "capital_lon": -76.1800,
        "confidence_score": 0.55,
        "status": "confirmed",
        "boundary_geojson": {
            "type": "Polygon",
            "coordinates": [[
                [-79.0, 42.0], [-77.5, 43.0], [-76.0, 43.5], [-74.5, 43.0],
                [-73.5, 42.5], [-74.0, 41.5], [-75.5, 41.0], [-77.0, 41.5],
                [-78.5, 41.5], [-79.0, 42.0],
            ]],
        },
        "ethical_notes": (
            "ETHICS-001: Haudenosaunee ('popolo della lunga casa') e' il nome proprio. "
            "'Irochesi' e' un esonimo (nome dato da altri, probabilmente di origine "
            "francese/algonchina). La Confederazione esiste ancora oggi come nazione "
            "sovrana. La Grande Legge della Pace (Gayanashagowa) e' considerata una "
            "delle influenze sulla Costituzione degli Stati Uniti — fatto spesso "
            "omesso nella storiografia occidentale. Il confidence_score riflette "
            "la predominanza di fonti orali pre-contatto."
        ),
        "name_variants": [
            {"name": "Iroquois Confederacy", "lang": "en",
             "context": "esonimo — 'Irochesi' non e' il nome che il popolo si da'",
             "source": "Fenton, The Great Law and the Longhouse (1998)"},
            {"name": "Confederazione Irochese", "lang": "it", "context": "denominazione italiana (esonimo)",
             "source": "Enciclopedia Treccani"},
            {"name": "Six Nations", "lang": "en", "period_start": 1722,
             "context": "dopo l'aggiunta dei Tuscarora (da Cinque a Sei Nazioni)",
             "source": "Fenton, The Great Law and the Longhouse (1998)"},
        ],
        "territory_changes": [
            {"year": 1142, "region": "Nord-Est America", "change_type": "TREATY",
             "description": "Fondazione tradizionale della Confederazione con la Grande Legge della Pace (Gayanashagowa). Data dibattuta dagli storici.",
             "confidence_score": 0.45},
        ],
        "sources": [
            {"citation": "Fenton, W. The Great Law and the Longhouse (1998)", "source_type": "academic"},
            {"citation": "Mann, C.C. 1491: New Revelations of the Americas Before Columbus (2005)", "source_type": "academic"},
        ],
    },
]


def seed_database():
    """Popola il database con i dati demo se è vuoto."""
    db: Session = SessionLocal()
    try:
        count = db.query(GeoEntity).count()
        if count > 0:
            logger.info("Database già popolato (%d entità). Skip seed.", count)
            return

        logger.info("Seeding database con %d entità demo...", len(DEMO_ENTITIES))

        for data in DEMO_ENTITIES:
            entity = GeoEntity(
                name_original=data["name_original"],
                name_original_lang=data["name_original_lang"],
                entity_type=data["entity_type"],
                year_start=data["year_start"],
                year_end=data.get("year_end"),
                capital_name=data.get("capital_name"),
                capital_lat=data.get("capital_lat"),
                capital_lon=data.get("capital_lon"),
                boundary_geojson=json.dumps(data["boundary_geojson"]) if data.get("boundary_geojson") else None,
                confidence_score=data.get("confidence_score", 0.5),
                status=data.get("status", "confirmed"),
                ethical_notes=data.get("ethical_notes"),
            )

            for nv in data.get("name_variants", []):
                entity.name_variants.append(NameVariant(**nv))

            for tc in data.get("territory_changes", []):
                entity.territory_changes.append(TerritoryChange(**tc))

            for src in data.get("sources", []):
                entity.sources.append(Source(**src))

            db.add(entity)

        db.commit()
        logger.info("Seed completato: %d entità inserite.", len(DEMO_ENTITIES))

    except Exception:
        db.rollback()
        logger.exception("Errore durante il seed del database")
        raise
    finally:
        db.close()
