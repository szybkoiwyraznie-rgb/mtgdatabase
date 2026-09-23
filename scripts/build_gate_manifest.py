#!/usr/bin/env python3
"""Jednorazowy builder manifestu bramki g001 (pilotaż systemu sygnatur).

Produkuje work/gates/g001/manifest.json z kandydatami i wpisami gotowymi do
przyjęcia przez `library_tool.py accept`. Uruchamiać z katalogu repo.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sig_audio as dsp  # noqa: E402

G = Path("work/gates/g001")

cat = {s["id"]: s for s in json.loads(Path("data/catalog.json").read_text(encoding="utf-8"))["stories"]}


def dur(f: str) -> float:
    wave, _ = dsp.load_any(G / f)
    return round(wave.shape[1] / dsp.SR, 2)


YSL = {
    "title": "Yellowstone Sound Library (NPS)",
    "author": "National Park Service",
    "license": "Public Domain (utwór rządu USA)",
    "url": "https://www.nps.gov/yell/learn/photosmultimedia/soundlibrary.htm",
    "channel": "git clone sparse z github.com/rosuH/YSL (mirror)",
}
VCSL = {
    "title": "Versilian Community Sample Library",
    "author": "Versilian Studios + społeczność",
    "license": "CC0 1.0",
    "url": "https://vis.versilstudios.com/vcsl.html",
    "channel": "git clone sparse (no-cone) z github.com/sgossner/VCSL",
}
YSL_T, YSL_L = YSL["title"], YSL["license"]
VCSL_T, VCSL_L = VCSL["title"], VCSL["license"]
DEF_NOTE = "definicja nutowa — render bramkowy na neutralnym fortepianie"


def bg(entry_suffix, setting, desc, file, gatefile, source_note, level):
    return {
        "entry": {
            "id": entry_suffix, "setting": setting, "desc": desc,
            "file": f"audio/library/backgrounds/{entry_suffix}.mp3",
            "duration_sec": dur(gatefile), "level_ref_db": level, "loopable": True,
            "source": {**YSL, "notes": source_note},
        }
    }


def hero(eid, role, desc, gatefile, character, distance, energy, good, bad, source_note):
    return {
        "entry": {
            "id": eid, "role": role, "desc": desc,
            "file": f"audio/library/heroes/{eid}.mp3",
            "duration_sec": dur(gatefile), "character": character, "distance": distance,
            "energy": energy, "good_for": good, "bad_for": bad,
            "source": {**YSL, "notes": source_note},
        }
    }


def inst(deffile, samples, source_note):
    entry = json.loads((G / "defs" / deffile).read_text(encoding="utf-8"))
    entry["samples"] = samples
    entry["source"] = {**VCSL, "notes": source_note}
    return {"entry": entry}


def gesture(deffile):
    return {"entry": json.loads((G / "defs" / deffile).read_text(encoding="utf-8"))}


def cand(label, title, gatefile, desc, source_text, entry_obj):
    return {"label": label, "title": title, "file": gatefile, "desc": desc,
            "source": source_text, **entry_obj}


manifest = {
    "id": "g001",
    "created": "2026-09-23",
    "note": "Bramka pilotażowa systemu sygnatur: dwie fabuły, cztery bazy od zera. "
            "Kody (a) renderowane na neutralnym fortepianie; instrumenty (b) grają "
            "własną frazę demonstracyjną, niezależną od fabuły.",
    "stories": [
        {
            "story_id": 1, "title": cat["1"]["title"], "story": cat["1"]["story"],
            "slots": {
                "d": {"role": "wąwóz nad urwiskiem, gdzie zbiera się armia — zimna, niska przestrzeń napięcia",
                      "candidates": [
                          cand("d.1", "wiatr w urwisku", "candidates/s1_d1.mp3",
                               "susz wiatru między skałami", f"{YSL_T} — Hurricane Vent; {YSL_L}",
                               bg("wind_canyon_01", "wąwóz / urwisko", "szum wiatru między skałami, równy niski podmuch",
                                  None, "candidates/s1_d1.mp3", "Hurricane Vent 5.0-13.0 s", -32)),
                          cand("d.2", "oddalony grzmot nad wąwozem", "candidates/s1_d2.mp3",
                               "głęboki pomruk zbierającej się burzy", f"{YSL_T} — Thunder; {YSL_L}",
                               bg("thunder_far_01", "wąwóz / burza w oddali", "niski toczący się grzmot, złowieszcza pogoda",
                                  None, "candidates/s1_d2.mp3", "Thunder 24.0-32.0 s", -33)),
                          cand("d.3", "podziemny pomruk", "candidates/s1_d3.mp3",
                               "echo i bulgot — jakby ziemia oddychała pod stopami", f"{YSL_T} — The Dragon's Mouth; {YSL_L}",
                               bg("cavern_rumble_01", "wąwóz / podziemia", "niskie bulgoczące echo jaskini, niepokój od spodu",
                                  None, "candidates/s1_d3.mp3", "The Dragon's Mouth 52.0-60.0 s", -33)),
                      ]},
                "c": {"role": "krzyk crebaina — skrzydlaci zwiadowcy dają znak armii",
                      "candidates": [
                          cand("c.1", "pojedynczy krzyk kruka", "candidates/s1_c1.mp3",
                               "jedno ostre, bliskie wołanie", f"{YSL_T} — Common Raven; {YSL_L}",
                               hero("raven_cry_single_01", "krzyk dużego ptaka zwiadowczego",
                                    "pojedynczy ostry krzyk kruka, bliski", "candidates/s1_c1.mp3",
                                    "ostry, gardłowy", "bliski", "wysoka",
                                    ["sygnał", "ostateczna zapowiedź"], ["tło", "smutek"],
                                    "Common Raven 3.4-4.7 s")),
                          cand("c.2", "podwójny krzyk kruka", "candidates/s1_c2.mp3",
                               "dwa krzyki — jakby ptaki odpowiadały sobie", f"{YSL_T} — Common Raven; {YSL_L}",
                               hero("raven_cry_double_01", "krzyk dużego ptaka zwiadowczego",
                                    "dwa krzyki krucze w krótkim odstępie", "candidates/s1_c2.mp3",
                                    "ostry, wielokrotny", "bliski", "wysoka",
                                    ["sygnał", "porozumienie stada"], ["tło"],
                                    "Common Raven 4.6-6.3 s")),
                          cand("c.3", "wrzask kruka (długi)", "candidates/s1_c3.mp3",
                               "wydłużony, agresywny wrzask", f"{YSL_T} — Common Raven; {YSL_L}",
                               hero("raven_yell_long_01", "krzyk dużego ptaka zwiadowczego",
                                    "długi agresywny wrzask kruka", "candidates/s1_c3.mp3",
                                    "agresywny, przeciągany", "bliski", "bardzo wysoka",
                                    ["atak", "alarm"], ["subtelność"],
                                    "Common Raven 6.0-7.8 s")),
                      ]},
                "a": {"role": "muzyczna odpowiedź na sygnał crebainów (render neutralny: fortepian)",
                      "candidates": [
                          cand("a.1", "złowieszczy sygnał", "candidates/g1a_omen_low_fall.mp3",
                               "długa niska nuta opada o ton i nie znajduje rozwiązania", DEF_NOTE,
                               gesture("g1a_omen_low_fall.json")),
                          cand("a.2", "marsz zagrożenia", "candidates/g1b_march_pulse.mp3",
                               "dwa krótkie impulsy jak kroki armii, potem długi cień", DEF_NOTE,
                               gesture("g1b_march_pulse.json")),
                          cand("a.3", "pustka po sygnale", "candidates/g1c_void_tone.mp3",
                               "jeden cichy długi ton — wąwóz zamiera w oczekiwaniu", DEF_NOTE,
                               gesture("g1c_void_tone.json")),
                      ]},
                "b": {"role": "brzmienie kody dla mrocznej sceny",
                      "candidates": [
                          cand("b.1", "kotły (timpani)", "candidates/b_timpani.mp3",
                               "ciężkie, miękkie uderzenia — groza i marsz", f"{VCSL_T} — Timpani 1; {VCSL_L}",
                               inst("b_timpani.json",
                                    {"38": "audio/library/instruments/timpani/hit_soft.mp3",
                                     "39": "audio/library/instruments/timpani/hit_mid.mp3",
                                     "41": "audio/library/instruments/timpani/hit_hard.mp3"},
                                    "Timpani1 Hit v2 rr1 + v3 rr3, Timpani2 Hit v2 rr1")),
                          cand("b.2", "flet basowy barokowy", "candidates/b_bass_recorder.mp3",
                               "drewniany, skryty, archaiczny — intryga i stara wojna", f"{VCSL_T} — Baroque Bass Recorder; {VCSL_L}",
                               inst("b_bass_recorder.json",
                                    {"41": "audio/library/instruments/bass_recorder/F2_stac.mp3",
                                     "48": "audio/library/instruments/bass_recorder/C3_susvib.mp3"},
                                    "BassRecorder Stac F2 rr1 + SusVib C3 rr1")),
                          cand("b.3", "dzwony rurowe", "candidates/b_chimes.mp3",
                               "zimne uderzenia z pogłosem — uroczystość, fatum", f"{VCSL_T} — Tubular Bells; {VCSL_L}",
                               inst("b_chimes.json",
                                    {"52": "audio/library/instruments/chimes/E3_ff.mp3",
                                     "58": "audio/library/instruments/chimes/As3_ff.mp3"},
                                    "chimes E3 ff rr2 + A#3 ff rr1")),
                      ]},
            },
        },
        {
            "story_id": 4, "title": cat["4"]["title"], "story": cat["4"]["story"],
            "slots": {
                "d": {"role": "mgliste jezioro z ruinami — spokojna, tajemnicza przestrzeń wody",
                      "candidates": [
                          cand("d.1", "śpiewające jezioro", "candidates/s4_d1.mp3",
                               "dziwne ciche «pieśni» wody — zjawisko singing lake", f"{YSL_T} — Singing Lake; {YSL_L}",
                               bg("lake_singing_01", "jezioro / mgła", "eteryczne ciche pieśni wody na jeziorze",
                                  None, "candidates/s4_d1.mp3", "Singing Lake 60.0-68.0 s", -33)),
                          cand("d.2", "bulgoczące źródło", "candidates/s4_d2.mp3",
                               "delikatne perlenie wody przy brzegu", f"{YSL_T} — Black Sand Pool; {YSL_L}",
                               bg("lake_bubbles_01", "jezioro / brzeg", "ciche bulgotanie wody w płytkim zbiorniku",
                                  None, "candidates/s4_d2.mp3", "Black Sand Pool 12.0-20.0 s", -33)),
                          cand("d.3", "nocne żaby nad wodą", "candidates/s4_d3.mp3",
                               "chór żab po zmroku — żywa, ale spokojna okolica", f"{YSL_T} — Boreal Chorus Frogs; {YSL_L}",
                               bg("frogs_night_01", "jezioro / noc", "chór żab nad wodą nocą",
                                  None, "candidates/s4_d3.mp3", "Chorus Frogs 100.5-108.5 s", -34)),
                      ]},
                "c": {"role": "jeden tajemniczy głos w mgle — zew miejsca, nie akcja",
                      "candidates": [
                          cand("c.1", "zew nura (loon)", "candidates/s4_c1.mp3",
                               "nawiedzony, wysoki zew ptaka wodnego", f"{YSL_T} — Common Loon; {YSL_L}",
                               hero("loon_wail_01", "zew tajemniczego ptaka wodnego",
                                    "wysoki nawiedzony zew nura nad jeziorem", "candidates/s4_c1.mp3",
                                    "nawiedzony, melodyjny", "daleki", "średnia",
                                    ["tajemnica", "samotność", "magia miejsca"], ["walka"],
                                    "Common Loon 64.0-66.6 s")),
                          cand("c.2", "drżący okrzyk nura (yodel)", "candidates/s4_c2.mp3",
                               "drżące opadające wołanie — jak echo pytania", f"{YSL_T} — Common Loon; {YSL_L}",
                               hero("loon_yodel_01", "zew tajemniczego ptaka wodnego",
                                    "drżący opadający okrzyk nura (yodel)", "candidates/s4_c2.mp3",
                                    "drżący, opadający", "daleki", "średnia",
                                    ["tajemnica", "groteska natury"], ["walka"],
                                    "Common Loon 95.4-98.6 s")),
                          cand("c.3", "śpiew jeziora", "candidates/s4_c3.mp3",
                               "samo jezioro odpowiada — narastający ton wody", f"{YSL_T} — Singing Lake; {YSL_L}",
                               hero("lake_song_swell_01", "głos żywiołu wody",
                                    "narastający śpiew jeziora z miękkim pluskiem", "candidates/s4_c3.mp3",
                                    "organiczny, narastający", "bliski", "średnio-wysoka",
                                    ["manifestacja magii", "odpowiedź miejsca"], ["cisza absolutna"],
                                    "Singing Lake 1.0-4.4 s")),
                      ]},
                "a": {"role": "muzyczna odpowiedź na mgły sanktuarium (render neutralny: fortepian)",
                      "candidates": [
                          cand("a.1", "cud / odkrycie", "candidates/g4a_discovery_open.mp3",
                               "dwie jasne nuty otwierające światło nad ruinami", DEF_NOTE,
                               gesture("g4a_discovery_open.json")),
                          cand("a.2", "tajemnica", "candidates/g4b_mystery_tritone.mp3",
                               "wysoka nuta wisząca nad niskim szmerem — pytanie bez odpowiedzi", DEF_NOTE,
                               gesture("g4b_mystery_tritone.json")),
                          cand("a.3", "spokój / ulga", "candidates/g4c_relief_descent.mp3",
                               "trzy łagodne nuty opadają jak liście na wodę", DEF_NOTE,
                               gesture("g4c_relief_descent.json")),
                      ]},
                "b": {"role": "brzmienie kody dla magicznej sceny",
                      "candidates": [
                          cand("b.1", "harfa koncertowa", "candidates/b_harp.mp3",
                               "świetliste krople — magia czysta, jasna", f"{VCSL_T} — Concert Harp; {VCSL_L}",
                               inst("b_harp.json",
                                    {"45": "audio/library/instruments/harp/A2_mf.mp3",
                                     "52": "audio/library/instruments/harp/E3_mf.mp3",
                                     "62": "audio/library/instruments/harp/D4_mf.mp3"},
                                    "KSHarp A2/E3/D4 mf1")),
                          cand("b.2", "dzwony rurowe", "candidates/b_chimes.mp3",
                               "uroczysty odległy dzwon — rytuał, świątynia", f"{VCSL_T} — Tubular Bells; {VCSL_L}",
                               inst("b_chimes.json",
                                    {"52": "audio/library/instruments/chimes/E3_ff.mp3",
                                     "58": "audio/library/instruments/chimes/As3_ff.mp3"},
                                    "chimes E3 ff rr2 + A#3 ff rr1")),
                          cand("b.3", "szkło (wine glasses)", "candidates/b_wine_glasses.mp3",
                               "eteryczny śpiew szkła — nieziemsko, senno", f"{VCSL_T} — Wine Glasses; {VCSL_L}",
                               inst("b_wine_glasses.json",
                                    {"63": "audio/library/instruments/wine_glasses/Ds4.mp3",
                                     "66": "audio/library/instruments/wine_glasses/Fs4.mp3",
                                     "68": "audio/library/instruments/wine_glasses/As4.mp3",
                                     "74": "audio/library/instruments/wine_glasses/D5.mp3"},
                                    "glass 1-4 Sustains Fast")),
                      ]},
            },
        },
    ],
}

out = G / "manifest.json"
out.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
total = sum(len(story["slots"][slot]["candidates"]) for story in manifest["stories"] for slot in story["slots"])
print(f"zapisano {out} — {total} kandydatów")
