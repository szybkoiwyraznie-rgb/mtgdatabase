#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etap 2: mapowanie profili semantycznych na klasy taksonomii.

Czyta data/semantics/taxonomy.json (wzorce per klasa) i
data/semantics/story-profiles.json, przypisuje każdej fabule po jednej
klasie na warstwę (największa liczba trafień wzorców; remis rozstrzyga
kolejność klas w taksonomii). Raportuje pokrycie i liczniki.

Użycie:
  scripts/map_profiles.py             # raport pokrycia + liczniki
  scripts/map_profiles.py --write     # zapisuje data/semantics/story-classes.json
  scripts/map_profiles.py --show L K  # wypisz fabuły klasy K w warstwie L
"""
import json
import re
import sys
import collections
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PREFIX = '(?<![a-ząćęłńóśźż])'


def load():
    tax = json.loads((ROOT / 'data/semantics/taxonomy.json').read_text('utf-8'))
    prof = json.loads(
        (ROOT / 'data/semantics/story-profiles.json').read_text('utf-8')
    )['profiles']
    return tax, prof


def compile_layers(tax):
    layers = {}
    for lname, layer in tax['layers'].items():
        defs = []
        for k in layer['klasy']:
            pats = [re.compile(PREFIX + w) for w in k['wzorce']]
            defs.append((k['id'], pats))
        layers[lname] = defs
    return layers


def classify(defs, text):
    best, best_score = None, 0
    for cid, pats in defs:
        score = sum(len(p.findall(text)) for p in pats)
        if score > best_score:
            best, best_score = cid, score
    return best


def main(argv):
    tax, prof = load()
    layers = compile_layers(tax)
    result = {}
    ok = True
    for lname, defs in layers.items():
        counts = collections.Counter()
        for sid, p in sorted(prof.items(), key=lambda kv: int(kv[0])):
            text = (p[lname]['opis'] + ' ' + ' '.join(p[lname]['cechy'])).lower()
            cid = classify(defs, text)
            result.setdefault(sid, {})[lname] = cid
            if cid is None:
                ok = False
                print(f'BRAK KLASY: fabuła {sid}, warstwa {lname}')
            else:
                counts[cid] += 1
        n = sum(counts.values())
        print(f'{lname}: {n}/{len(prof)} przypisane, klas użytych '
              f'{len(counts)}/{len(defs)}')
        if '--counts' in argv:
            for cid, c in counts.most_common():
                print(f'   {c:4d}  {cid}')

    if '--show' in argv:
        i = argv.index('--show')
        lname, kid = argv[i + 1], argv[i + 2]
        for sid in sorted(result, key=int):
            if result[sid].get(lname) == kid:
                print(f'   {sid}: {prof[sid][lname]["opis"][:100]}')

    # kontrola twardej reguły: unikalna kombinacja a·b·c·d
    combos = collections.Counter(
        tuple(result[sid][ln] for ln in ('background', 'hero', 'mood',
                                         'instrumentation'))
        for sid in result
    )
    dup = {k: v for k, v in combos.items() if v > 1}
    print(f'kombinacje a·b·c·d: {len(combos)} unikalnych na {len(result)} fabuł; '
          f'powtórzonych: {len(dup)}')
    if dup:
        print('NARUSZENIE unique_combo (typy 1:1 z klockami — ADR 0006, aneks '
              '„Jeden typ = jeden klocek"). Rozwiązanie: doprecyzowanie '
              'taksonomii — propozycja nowego typu dla jednej fabuły z pary '
              '(bramka tekstowa właściciela), nigdy drugi klocek w typie.')

    if '--write' in argv:
        out = {
            'schema': 1,
            'taxonomy_version': tax['version'],
            'note': 'Mapowanie fabuł na klasy taksonomii (Etap 2). '
                    'Szkic do przeglądu; po akceptacji taksonomii v1 staje się '
                    'wiążący.',
            'classes': result,
        }
        path = ROOT / 'data/semantics/story-classes.json'
        path.write_text(
            json.dumps(out, ensure_ascii=False, indent=2) + '\n', 'utf-8')
        print(f'zapisano {path.relative_to(ROOT)}')

    return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
