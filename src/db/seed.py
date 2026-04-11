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
                [-9.5, 36.0], [-3.0, 43.5], [3.0, 50.0], [10.0, 47.0],
                [16.0, 48.5], [25.0, 47.0], [30.0, 45.0], [42.0, 42.0],
                [46.0, 37.5], [36.0, 32.0], [35.5, 30.0], [32.0, 31.0],
                [25.0, 31.5], [10.0, 31.0], [-1.0, 35.0], [-9.5, 36.0],
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
                [15.0, 36.0], [17.0, 47.0], [23.0, 48.0], [29.0, 46.0],
                [35.0, 43.0], [44.0, 40.0], [48.0, 37.0], [44.0, 32.0],
                [36.0, 31.0], [25.0, 31.0], [20.0, 34.0], [15.0, 36.0],
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
                [-81.0, 2.0], [-79.0, -2.0], [-77.0, -8.0], [-75.0, -14.0],
                [-71.0, -22.0], [-68.0, -35.0], [-72.0, -33.0], [-75.0, -18.0],
                [-78.0, -8.0], [-80.0, -2.0], [-81.0, 2.0],
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
                [61.0, 24.0], [64.0, 30.0], [68.0, 36.0], [74.0, 37.0],
                [78.0, 35.0], [82.0, 28.0], [88.0, 27.0], [92.0, 25.0],
                [97.0, 16.0], [92.0, 10.0], [80.0, 7.0], [77.0, 8.0],
                [72.0, 20.0], [66.0, 24.0], [61.0, 24.0],
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
                [34.2, 29.5], [34.3, 31.5], [34.8, 33.0], [35.9, 33.3],
                [35.9, 32.5], [35.5, 31.0], [35.4, 29.5], [34.2, 29.5],
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
                [20.0, 42.0], [20.3, 42.6], [20.7, 43.0], [21.0, 43.2],
                [21.5, 42.9], [21.8, 42.5], [21.6, 42.1], [20.9, 41.9],
                [20.0, 42.0],
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
                [23.4, 37.7], [23.3, 38.1], [23.6, 38.3],
                [24.0, 38.2], [24.1, 37.9], [23.9, 37.6], [23.4, 37.7],
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
                [24.0, 38.0], [24.0, 52.0], [45.0, 58.0], [70.0, 60.0],
                [100.0, 55.0], [120.0, 52.0], [130.0, 42.0], [118.0, 30.0],
                [108.0, 22.0], [95.0, 24.0], [75.0, 30.0], [50.0, 32.0],
                [35.0, 35.0], [24.0, 38.0],
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
                [12.0, -3.0], [13.0, -1.0], [16.0, -2.0], [19.0, -4.0],
                [18.0, -8.0], [16.0, -10.0], [13.0, -9.0], [12.0, -6.0],
                [12.0, -3.0],
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
