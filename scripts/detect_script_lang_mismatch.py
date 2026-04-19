"""v6.78 audit v4 Round 8: detect script/lang mismatch in entities.

Per ogni entity:
- Detect prevailing script of `name_original`
- Compare to expected script for `name_original_lang`
- Flag mismatches (Latin transliteration where native script expected)

Output: research_output/audit_v4/round8_script_lang_mismatch.json
NOTE: non auto-applica fix (riscrivere il nome è decisione manuale).
"""
import json
import sys
import urllib.request
import unicodedata

if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def fetch_entities():
    state = []
    for offset in range(0, 1100, 100):
        try:
            url = f'https://atlaspi.cra-srl.com/v1/entities/light?limit=100&offset={offset}'
            with urllib.request.urlopen(url, timeout=10) as r:
                state.extend(json.loads(r.read().decode()).get('entities', []))
        except Exception:
            break
    return state


def detect_script(s):
    if not s:
        return 'empty'
    counts = {}
    for c in s:
        if c.isspace() or c in '.,()[]{}\'"-:;/&|':
            continue
        try:
            name = unicodedata.name(c, '')
        except Exception:
            continue
        if 'CJK' in name or 'HIRAGANA' in name or 'KATAKANA' in name:
            key = 'CJK'
        elif 'ARABIC' in name:
            key = 'Arabic'
        elif 'CYRILLIC' in name:
            key = 'Cyrillic'
        elif 'GREEK' in name:
            key = 'Greek'
        elif 'HEBREW' in name:
            key = 'Hebrew'
        elif any(s in name for s in ('DEVANAGARI', 'BENGALI', 'TAMIL', 'TELUGU', 'KANNADA', 'MALAYALAM', 'GUJARATI', 'GURMUKHI', 'ORIYA', 'SINHALA')):
            key = 'Indic'
        elif any(s in name for s in ('THAI', 'KHMER', 'LAO', 'MYANMAR')):
            key = 'SE_Asian'
        elif any(s in name for s in ('CUNEIFORM', 'EGYPTIAN', 'OLD PERSIAN', 'UGARITIC', 'PHOENICIAN', 'ARAMAIC')):
            key = 'Ancient'
        elif 'ETHIOPIC' in name or 'MEROITIC' in name:
            key = 'Ge_ez_Meroitic'
        elif 'MONGOLIAN' in name:
            key = 'Mongolian'
        elif 'TIBETAN' in name:
            key = 'Tibetan'
        elif 'GEORGIAN' in name or 'ARMENIAN' in name:
            key = 'Caucasian'
        elif 'LATIN' in name:
            key = 'Latin'
        else:
            key = 'Other'
        counts[key] = counts.get(key, 0) + 1
    if not counts:
        return 'empty'
    return max(counts, key=counts.get)


LANG_SCRIPT = {
    # Latin script langs
    **{k: 'Latin' for k in [
        'la', 'en', 'fr', 'es', 'it', 'de', 'pt', 'nl', 'sv', 'no', 'da', 'is',
        'pl', 'cs', 'sk', 'hu', 'ro', 'tr', 'eu', 'ca', 'gl', 'cy', 'ga', 'gv',
        'fi', 'et', 'lv', 'lt', 'mt', 'sq', 'hr', 'sl', 'bs', 'fo', 'kw',
        'ay', 'qu', 'gn', 'nah', 'ng', 'sw', 'mi', 'haw', 'sm', 'to', 'fj',
        'mg', 'pap', 'fil', 'tl', 'id', 'ms', 'jv', 'su', 'mfe', 'crs', 'wo',
        'ff', 'so', 'zu', 'xh', 'ts', 'st', 'tn', 'sn', 'rw', 'rn', 'lg',
        'aa', 'ny', 'oc', 'mus', 'crk', 'ojg', 'iu', 'kl', 'mh', 'na', 'gil',
        'ty', 'kau', 'kr', 'bm',  # Bambara is Latin
    ]},
    # Cyrillic
    **{k: 'Cyrillic' for k in ['ru', 'uk', 'be', 'bg', 'sr', 'mk', 'mn', 'ky', 'kk', 'tt', 'kv', 'mdf', 'sah', 'tg', 'cv']},
    # Arabic
    **{k: 'Arabic' for k in ['ar', 'fa', 'ur', 'ps', 'ku', 'ckb', 'sd', 'ug', 'azb', 'pnb', 'ota']},
    # Greek
    **{k: 'Greek' for k in ['el', 'grc']},
    # Hebrew
    **{k: 'Hebrew' for k in ['he', 'yi']},
    # Indic
    **{k: 'Indic' for k in ['hi', 'bn', 'ta', 'te', 'ml', 'mr', 'gu', 'kn', 'or', 'pa', 'si', 'ne', 'sa']},
    # SE Asian
    **{k: 'SE_Asian' for k in ['th', 'lo', 'km', 'my']},
    # CJK
    **{k: 'CJK' for k in ['zh', 'ja', 'ko', 'lzh', 'cmn', 'yue', 'wuu']},
    # Ancient scripts
    **{k: 'Ancient' for k in ['akk', 'sux', 'peo', 'uga', 'hit', 'arc', 'phn', 'egy', 'pal', 'xpu', 'xlu']},
    # Ge'ez / Meroitic
    **{k: 'Ge_ez_Meroitic' for k in ['gez', 'am', 'ti', 'tig', 'wal']},
    # Mongolian
    **{k: 'Mongolian' for k in ['mnc']},
    # Tibetan
    **{k: 'Tibetan' for k in ['bo', 'dz']},
    # Caucasian
    **{k: 'Caucasian' for k in ['ka', 'hy', 'oss', 'os']},
}


def main():
    print('Fetching entities...')
    entities = fetch_entities()
    print(f'Got {len(entities)} entities')

    # v6.81 refined: false-positive filter.
    # Many AtlasPI entities have name_original = "نام عربی / Latin Translit"
    # The detector was flagging them because Latin chars > Arabic chars.
    # Refined logic: count chars by script and require that:
    # - if name contains ANY chars in the expected non-Latin script → OK (dual-name pattern)
    # - mismatch only if name is PURELY in unexpected script (no native chars at all)
    mismatches = []
    for e in entities:
        name = e.get('name_original', '')
        lang = (e.get('name_original_lang', '') or '').lower().strip()
        if not name or not lang:
            continue
        detected = detect_script(name)
        expected = LANG_SCRIPT.get(lang)
        if expected and expected != 'Latin' and detected == 'Latin':
            # Count chars by script to check if expected script appears at all
            counts_by_script = {}
            for c in name:
                if c.isspace() or c in '.,()[]{}\'"-:;/&|':
                    continue
                try:
                    cname = unicodedata.name(c, '')
                except Exception:
                    continue
                # Map char to script (same logic as detect_script)
                if 'CJK' in cname or 'HIRAGANA' in cname or 'KATAKANA' in cname:
                    k = 'CJK'
                elif 'ARABIC' in cname:
                    k = 'Arabic'
                elif 'CYRILLIC' in cname:
                    k = 'Cyrillic'
                elif 'GREEK' in cname:
                    k = 'Greek'
                elif 'HEBREW' in cname:
                    k = 'Hebrew'
                elif any(s in cname for s in ('DEVANAGARI', 'BENGALI', 'TAMIL', 'TELUGU', 'KANNADA', 'MALAYALAM', 'GUJARATI', 'GURMUKHI', 'ORIYA', 'SINHALA')):
                    k = 'Indic'
                elif any(s in cname for s in ('THAI', 'KHMER', 'LAO', 'MYANMAR')):
                    k = 'SE_Asian'
                elif any(s in cname for s in ('CUNEIFORM', 'EGYPTIAN', 'OLD PERSIAN', 'UGARITIC', 'PHOENICIAN', 'ARAMAIC')):
                    k = 'Ancient'
                elif 'ETHIOPIC' in cname or 'MEROITIC' in cname:
                    k = 'Ge_ez_Meroitic'
                elif 'MONGOLIAN' in cname:
                    k = 'Mongolian'
                elif 'TIBETAN' in cname:
                    k = 'Tibetan'
                elif 'GEORGIAN' in cname or 'ARMENIAN' in cname:
                    k = 'Caucasian'
                elif 'LATIN' in cname:
                    k = 'Latin'
                else:
                    k = 'Other'
                counts_by_script[k] = counts_by_script.get(k, 0) + 1

            # Mismatch ONLY if expected script has 0 chars in name (truly missing)
            expected_count = counts_by_script.get(expected, 0)
            if expected_count == 0:
                mismatches.append({
                    'id': e['id'],
                    'name': name,
                    'lang': lang,
                    'expected_script': expected,
                    'detected_script': detected,
                    'expected_chars_count': 0,
                    'kind': 'missing_native_script_chars',
                })

    print(f'\nMismatches found: {len(mismatches)}')
    print('\nSample 15:')
    for m in mismatches[:15]:
        print(f"  id={m['id']} '{m['name']}' lang={m['lang']} (expected {m['expected_script']})")

    # Save report
    out = 'research_output/audit_v4/round8_script_lang_mismatch.json'
    import os
    os.makedirs('research_output/audit_v4', exist_ok=True)
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(mismatches, f, ensure_ascii=False, indent=2)
    print(f'\nReport: {out}')

    # Group by kind
    from collections import Counter
    by_lang = Counter(m['lang'] for m in mismatches)
    print(f'\nBy lang code:')
    for lang, n in by_lang.most_common(15):
        print(f'  {lang}: {n}')


if __name__ == '__main__':
    main()
