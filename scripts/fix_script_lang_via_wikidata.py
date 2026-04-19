"""v6.81 audit v4 Round 11: per ogni entity con script/lang mismatch + wikidata_qid,
fetcha il label nella lingua nativa da Wikidata e genera patch per name_original.

NB: questo SCRIPT RISCRIVE name_original usando dati Wikidata. Esegui in modalita'
dry-run prima per review. ETHICS: rispetta CLAUDE.md ETHICS-001 — il name_original
DEVE essere nella lingua locale/nativa, non in transliteration.
"""
import json
import sys
import urllib.request
import time

if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


HEADERS = {'User-Agent': 'AtlasPI/6.81 (https://atlaspi.cra-srl.com)'}


def fetch_wikidata(qid):
    try:
        url = f'https://www.wikidata.org/wiki/Special:EntityData/{qid}.json'
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read().decode())
    except Exception:
        return None


def fetch_entity_qid(eid):
    try:
        with urllib.request.urlopen(f'https://atlaspi.cra-srl.com/v1/entities/{eid}', timeout=10) as r:
            return json.loads(r.read().decode())
    except Exception:
        return None


def get_native_label(wd_data, qid, lang):
    """Get label in `lang` from Wikidata entity data."""
    if not wd_data:
        return None
    entities = wd_data.get('entities', {})
    e = entities.get(qid)
    if not e:
        return None
    labels = e.get('labels', {})
    # Try exact lang
    if lang in labels:
        return labels[lang].get('value')
    # Try aliases for that lang
    aliases = e.get('aliases', {})
    if lang in aliases and aliases[lang]:
        return aliases[lang][0].get('value')
    return None


def main():
    # Load mismatches
    with open('research_output/audit_v4/round8_script_lang_mismatch.json', encoding='utf-8') as f:
        mismatches = json.load(f)
    print(f'Loaded {len(mismatches)} mismatches')

    patches = []
    skipped_no_qid = 0
    skipped_no_label = 0
    skipped_unicode_decode = 0

    for i, m in enumerate(mismatches):
        eid = m['id']
        lang = m['lang']
        current_name = m['name']
        # Fetch entity to get wikidata_qid
        ent = fetch_entity_qid(eid)
        if not ent:
            continue
        qid = ent.get('wikidata_qid')
        if not qid:
            skipped_no_qid += 1
            continue
        wd = fetch_wikidata(qid)
        native_label = get_native_label(wd, qid, lang)
        if not native_label:
            skipped_no_label += 1
            continue
        if native_label == current_name:
            continue  # already correct (shouldn't happen but safety)
        # Build patch: name_original → native_label, current → name_variants[lang+'-Latn']
        patches.append({
            'resource': 'entity',
            'id': eid,
            'field': 'name_original',
            'new_value': native_label,
            'rationale': (
                f"ETHICS-001 enforcement (audit v4 Round 11): name_original era "
                f"'{current_name}' (Latin transliteration) per lang='{lang}'. "
                f"Wikidata {qid} fornisce label nativo '{native_label}' nella lingua "
                f"corretta. CLAUDE.md prescribe nome primario in lingua locale."
            ),
            'source': f'Wikidata {qid} labels.{lang}',
            'audit_ref': f'v4/round11/script_lang_native_restore'
        })
        if i % 30 == 0:
            print(f'Progress: {i}/{len(mismatches)}, patches={len(patches)}')
        time.sleep(0.4)  # rate limit

    print(f'\nFinal: {len(patches)} patches')
    print(f'Skipped: no QID={skipped_no_qid}, no native label={skipped_no_label}')

    with open('data/wikidata/v681_round11_native_names.json', 'w', encoding='utf-8') as f:
        json.dump(patches, f, ensure_ascii=False, indent=2)
    print('Wrote data/wikidata/v681_round11_native_names.json')


if __name__ == '__main__':
    main()
