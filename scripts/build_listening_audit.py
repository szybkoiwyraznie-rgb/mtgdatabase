#!/usr/bin/env python3
"""Buduje katalog audytu odsłuchowego właściciela (odsluch/).

Z całej historii gita (wszystkie refy zdalne) zbiera każde pojawienie się
pliku MP3 fabuły: wersje produkcyjne (audio/samples/<id>.mp3) i kandydatów
(variants/<batch>/vN/<id>.mp3). Unikalne bloby eksportuje do
odsluch/audio/<id>/<vid>.mp3 (vid = 12 znaków skrótu blobu gita) i buduje
samodzielną stronę odsluch/index.html + odsluch/data.js.

Strona działa lokalnie z pliku (file://, ścieżki względne), zapisuje wybory
w localStorage (odporność na przeładowanie/brak prądu) i generuje raport
JSON ("Stwórz raport"), który właściciel odsyła agentowi. Agent składa z
niego dream team najlepszych wersji i analizuje preferencje.

Dopasowanie promptów: data/samples/generated-manifest.jsonl (plus unia
wszystkich wersji tego pliku z historii) mapuje wygenerowany plik na prompt;
wersjom po postprodukcji przypisywany jest prompt najbliższej wcześniejszej
generacji na tej samej ścieżce (źródło dźwięku).

Użycie:
    python scripts/build_listening_audit.py             # buduje odsluch/
    python scripts/build_listening_audit.py --stats     # tylko statystyki
"""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUT_DIR = REPO / "odsluch"
ROUND_RE = re.compile(r"\b([rb]\d{3}[a-z]*)\b")
VAR_PATH_RE = re.compile(r"^variants/([^/]+)/(?:v(\d+)/)?(\d+)\.mp3$")
PROD_PATH_RE = re.compile(r"^audio/samples/(\d+)\.mp3$")
RAW_RE = re.compile(r"^:([0-7]+) ([0-7]+) ([0-9a-f]+) ([0-9a-f]+) ([AMD])\t(.+)$")
IMG_DIR_DEFAULT = r"C:\Users\Jacek PC\Desktop\MtG Fusion\img"


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True).stdout


def git_root_refs_present() -> bool:
    """Strona wymaga pełnej historii (fetch wszystkich gałęzi)."""
    shallow = subprocess.run(
        ["git", "rev-parse", "--is-shallow-repository"], cwd=REPO,
        capture_output=True, text=True).stdout.strip()
    return shallow != "true"


# ---------------------------------------------------------------------------
# 1. Zdarzenia na plikach MP3 w całej historii
# ---------------------------------------------------------------------------

def collect_events() -> list[dict]:
    out = git("log", "--all", "--raw", "--no-renames", "--no-abbrev",
              "--format=%x01%H%x02%cI%x02%s", "--", "audio/samples", "variants")
    events: list[dict] = []
    cur = None
    for line in out.splitlines():
        if line.startswith("\x01"):
            h, date, subj = line[1:].split("\x02")
            cur = {"commit": h, "date": date, "subj": subj}
        else:
            m = RAW_RE.match(line)
            if not m or not m.group(6).endswith(".mp3"):
                continue
            old, new, st, path = m.group(3), m.group(4), m.group(5), m.group(6)
            blob = new if st in "AM" else old
            if set(blob) == {"0"}:
                continue
            events.append({"blob": blob, "path": path, **cur})
    return events


# ---------------------------------------------------------------------------
# 2. Manifest generacji (unia: drzewo robocze + wszystkie wersje z historii)
# ---------------------------------------------------------------------------

def manifest_entries() -> list[dict]:
    lines: set[str] = set()
    wt = REPO / "data/samples/generated-manifest.jsonl"
    if wt.exists():
        lines.update(ln for ln in wt.read_text(encoding="utf-8").splitlines() if ln.strip())
    out = git("log", "--all", "--raw", "--no-abbrev", "--format=%H",
              "--", "data/samples/generated-manifest.jsonl")
    blobs = set(m.group(1) for m in re.finditer(
        r"^:\d+ \d+ [0-9a-f]+ ([0-9a-f]{40}) M", out, re.M))
    for b in blobs:
        txt = git("cat-file", "blob", b)
        lines.update(ln for ln in txt.splitlines() if ln.strip())
    entries = []
    for ln in lines:
        try:
            entries.append(json.loads(ln))
        except json.JSONDecodeError:
            continue
    return entries


def norm_manifest_file(f: str) -> str:
    f = f.replace("\\", "/")
    f = re.sub(r"^/home/runner/work/mtgdatabase/mtgdatabase/", "", f)
    return f


# ---------------------------------------------------------------------------
# 3. Inwentarz wersji per fabuła
# ---------------------------------------------------------------------------

def subject_round(subj: str) -> str | None:
    m = ROUND_RE.search(subj)
    return m.group(1) if m else None


def subject_slug(subj: str) -> str:
    s = re.sub(r"\(#\d+\)", "", subj)
    s = re.sub(r"\[import-[^\]]+\]|\[skip ci\]|\[generate-[^\]]+\]", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s[:64].strip()


def build_inventory(events: list[dict], manifest: list[dict]) -> dict:
    head_blobs: dict[str, str] = {}
    for line in git("ls-tree", "HEAD", "--", "audio/samples/").splitlines():
        m = re.match(r"^\d+ blob ([0-9a-f]+)\taudio/samples/(\d+)\.mp3$", line)
        if m:
            head_blobs[m.group(2)] = m.group(1)

    # story_id -> vid -> dane wersji
    inv: dict[str, dict] = defaultdict(dict)

    def touch(sid: str, blob: str, ev: dict, kind: str):
        v = inv[sid].setdefault(blob, {
            "events": [], "kinds": set(), "var_labels": set(), "paths": set(),
        })
        v["events"].append(ev)
        v["kinds"].add(kind)
        v["paths"].add(ev["path"])
        return v

    for ev in events:
        mp = PROD_PATH_RE.match(ev["path"])
        if mp:
            touch(mp.group(1), ev["blob"], ev, "prod")
            continue
        mv = VAR_PATH_RE.match(ev["path"])
        if mv:
            batch, vno, sid = mv.group(1), mv.group(2), mv.group(3)
            v = touch(sid, ev["blob"], ev, "cand")
            v["var_labels"].add((batch, int(vno) if vno else None))
            continue
        # warianty ze starszych układów ścieżek (np. variants/b073/327_v1.mp3)
        mv2 = re.match(r"^variants/([^/]+)/(\d+)(?:_v(\d+))?\.mp3$", ev["path"])
        if mv2:
            batch, sid, vno = mv2.group(1), mv2.group(2), mv2.group(3)
            v = touch(sid, ev["blob"], ev, "cand")
            v["var_labels"].add((batch, int(vno) if vno else None))

    # indeks manifestu po znormalizowanej ścieżce
    by_path: dict[str, list[dict]] = defaultdict(list)
    for e in manifest:
        p = norm_manifest_file(e.get("file", ""))
        if p:
            by_path[p].append(e)

    stories: dict[str, list[dict]] = {}
    stats = {"versions": 0, "prompt_matched": 0, "current": 0}
    for sid, vers in inv.items():
        out_v = []
        for blob, v in vers.items():
            births = sorted(v["events"], key=lambda e: e["date"])
            first = births[0]
            birth_dt = dt.datetime.fromisoformat(first["date"])
            kinds = set(v["kinds"])
            current = head_blobs.get(sid) == blob
            if current:
                kinds.add("cur")
                stats["current"] += 1

            round_code = None
            for e in births:  # pierwsza etykieta rundy z tematu commita
                rc = subject_round(e["subj"])
                if rc:
                    round_code = rc
                    break
            batch = vno = None
            if v["var_labels"]:
                batch, vno = sorted(v["var_labels"], key=lambda t: (t[0], t[1] or 0))[-1]

            # dopasowanie promptu: najbliższa wcześniejsza generacja na ścieżce
            prompt = scenario = gen_dt = gen_batch = None
            cands = [e for p in v["paths"] for e in by_path.get(p, [])]
            if cands:
                def keyf(e):
                    g = dt.datetime.fromtimestamp(e["generated_at_unix"], dt.timezone.utc)
                    return g
                prior = [e for e in cands
                         if keyf(e) <= birth_dt + dt.timedelta(hours=36)]
                best = max(prior, key=keyf) if prior else None
                if best is None:  # fallback: najbliższa w oknie bezwzględnym
                    near = [e for e in cands
                            if abs((keyf(e) - birth_dt).total_seconds())
                            <= 10 * 86400]
                    if near:
                        best = min(near, key=lambda e: abs((keyf(e) - birth_dt)
                                   .total_seconds()))
                if best:
                    prompt = best.get("prompt")
                    scenario = best.get("sample_scenario")
                    gen_dt = keyf(best).strftime("%Y-%m-%d %H:%M")
                    gen_batch = best.get("batch")
                    stats["prompt_matched"] += 1

            out_v.append({
                "vid": blob[:12],
                "blob": blob,
                "date": birth_dt.strftime("%Y-%m-%d"),
                "sort": birth_dt.isoformat(),
                "round": round_code,
                "slug": subject_slug(first["subj"]) if not round_code else None,
                "batch": batch,
                "vno": vno,
                "gen_batch": gen_batch,
                "kinds": sorted(kinds),
                "current": current,
                "prompt": prompt,
                "scenario": scenario,
                "gen": gen_dt,
            })
            stats["versions"] += 1
        out_v.sort(key=lambda x: (x["sort"], x["vid"]))
        stories[sid] = out_v
    return {"stories": stories, "stats": stats, "head_blobs": head_blobs}


# ---------------------------------------------------------------------------
# 4. Eksport blobów do odsluch/audio/<id>/<vid>.mp3
# ---------------------------------------------------------------------------

def export_blobs(inventory: dict) -> tuple[int, int, int]:
    jobs = []  # (blob, out_path, size)
    for sid, vers in inventory["stories"].items():
        d = OUT_DIR / "audio" / sid
        d.mkdir(parents=True, exist_ok=True)
        for v in vers:
            out = d / f"{v['vid']}.mp3"
            jobs.append((v["blob"], out))
    sizes = {}
    proc = subprocess.run(["git", "cat-file", "--batch-check=%(objectname) %(objectsize)"],
                          cwd=REPO, input="\n".join(j[0] for j in jobs),
                          capture_output=True, text=True)
    for ln in proc.stdout.splitlines():
        h, s = ln.split()
        sizes[h] = int(s)
    written = skipped = 0
    p = subprocess.Popen(["git", "cat-file", "--batch"], cwd=REPO,
                         stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    assert p.stdin and p.stdout

    def read_exact(n: int) -> bytes:
        buf = b""
        while len(buf) < n:
            chunk = p.stdout.read(n - len(buf))
            if not chunk:
                raise EOFError("cat-file stream przerwany")
            buf += chunk
        return buf

    for blob, out in jobs:
        if out.exists() and out.stat().st_size == sizes.get(blob):
            skipped += 1
            continue
        p.stdin.write((blob + "\n").encode())
        p.stdin.flush()
        header = p.stdout.readline().decode().split()
        if len(header) < 3 or header[1] == "missing":
            print(f"  UWAGA: blob {blob[:12]} niedostępny, pomijam", file=sys.stderr)
            continue
        size = int(header[2])
        data = read_exact(size)
        p.stdout.read(1)  # znak nowej linii po zawartości
        out.write_bytes(data)
        written += 1
    p.stdin.close()
    p.wait()
    return written, skipped, len(jobs)


# ---------------------------------------------------------------------------
# 5. Dane katalogu i scenariuszy
# ---------------------------------------------------------------------------

def load_catalog() -> list[dict]:
    data = json.loads((REPO / "data/catalog.json").read_text(encoding="utf-8"))
    return data["stories"]


def load_current_scenarios() -> dict[str, dict]:
    out: dict[str, dict] = {}
    p = REPO / "data/samples/scenarios.jsonl"
    for ln in p.read_text(encoding="utf-8").splitlines():
        if not ln.strip():
            continue
        try:
            d = json.loads(ln)
        except json.JSONDecodeError:
            continue
        out[str(d.get("story_id"))] = d
    return out


# ---------------------------------------------------------------------------
# 6. Strona HTML
# ---------------------------------------------------------------------------

HTML = """<!doctype html>
<html lang="pl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Audyt odsłuchowy — wszystkie wersje sampli MTG</title>
<style>
:root{
  --bg:#f4f5f7; --card:#fff; --ink:#1c2733; --mut:#68758a; --line:#dde3ec;
  --acc:#2563eb; --ok:#16a34a; --bad:#dc2626; --amber:#b45309;
}
*{box-sizing:border-box}
body{margin:0;font:15px/1.45 system-ui,"Segoe UI",Roboto,Arial,sans-serif;color:var(--ink);background:var(--bg)}
header#top{position:sticky;top:0;z-index:50;border-bottom:1px solid var(--line);padding:10px 16px;backdrop-filter:blur(4px);background:rgba(255,255,255,.94)}
h1{font-size:19px;margin:2px 0 8px}
.controls{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin-top:8px}
button{font:inherit;border:1px solid var(--line);background:#fff;border-radius:8px;padding:7px 12px;cursor:pointer}
button:hover{border-color:var(--acc);color:var(--acc)}
button.primary{background:var(--acc);border-color:var(--acc);color:#fff;font-weight:600}
button.primary:hover{filter:brightness(1.08);color:#fff}
button.big{font-size:17px;padding:12px 26px}
button.ghost{background:transparent}
select,input[type=search]{font:inherit;padding:7px 10px;border:1px solid var(--line);border-radius:8px;background:#fff}
input#search{min-width:220px;flex:1}
.progress-wrap{display:flex;align-items:center;gap:12px;flex-wrap:wrap}
.bar{flex:1;min-width:160px;height:10px;background:var(--line);border-radius:6px;overflow:hidden}
#bar-fill{height:100%;width:0;background:linear-gradient(90deg,#22c55e,#16a34a);transition:width .25s}
#progress-text{font-weight:700;white-space:nowrap}
#progress-detail{color:var(--mut);font-size:13px;white-space:nowrap}
.hint{color:var(--mut);font-size:12.5px;margin:6px 0 0}
.settings{font-size:13.5px}
.settings input{width:60%;font:inherit;padding:4px 8px;border:1px solid var(--line);border-radius:6px}
main{max-width:980px;margin:0 auto;padding:16px 16px 60px}
article.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px 16px;margin:14px 0;box-shadow:0 1px 2px rgba(20,30,50,.04)}
article.card.answered{border-left:5px solid var(--ok)}
article.card.hidden{display:none}
.chead{display:flex;gap:14px;align-items:flex-start}
.thumb{width:76px;height:76px;flex:0 0 76px;border-radius:10px;background:var(--line);display:flex;align-items:center;justify-content:center;overflow:hidden;color:var(--mut);font-weight:700;font-size:20px}
.thumb img{width:100%;height:100%;object-fit:cover}
.chead h2{margin:0;font-size:17px}
.sid{display:inline-block;background:var(--ink);color:#fff;border-radius:6px;padding:1px 8px;margin-right:8px;font-size:14px}
.vcount{color:var(--mut);font-size:13px;margin:2px 0 4px}
details.narr{margin-top:4px}
details.narr summary,details.pdet summary{cursor:pointer;color:var(--mut);font-size:13px}
details.narr p,details.pdet p{margin:6px 0 2px;white-space:pre-wrap;font-size:13.5px}
.versions{margin-top:10px;display:flex;flex-direction:column;gap:7px}
label.vrow{display:flex;gap:12px;align-items:center;border:1.5px solid var(--line);border-radius:10px;padding:8px 12px;cursor:pointer;background:#fff;transition:border-color .15s, background .15s}
label.vrow:hover{border-color:var(--acc)}
label.vrow.sel{border-color:var(--ok);background:#f2fdf5}
label.vrow.cur{border-style:dashed}
label.vrow input{position:absolute;opacity:0;pointer-events:none}
.check{width:20px;height:20px;flex:0 0 20px;border-radius:50%;border:2px solid #b6c0d2;background:#fff;position:relative}
label.vrow.sel .check{border-color:var(--ok)}
label.vrow.sel .check::after{content:"✓";position:absolute;inset:0;display:flex;align-items:center;justify-content:center;color:var(--ok);font-weight:800;font-size:14px}
.vinfo{flex:0 0 240px;min-width:180px}
.vlabel{font-weight:600;font-size:13.5px}
.vline{display:flex;flex-wrap:wrap;gap:5px;align-items:center}
.badge{font-size:11px;font-weight:700;border-radius:5px;padding:1px 6px;letter-spacing:.02em}
.b-cur{background:#dcfce7;color:#14532d}
.b-prod{background:#e2e8f0;color:#334155}
.b-cand{background:#fef3c7;color:#92400e}
.b-none{background:#fee2e2;color:#7f1d1d}
audio{flex:1;min-width:230px;height:36px}
label.vrow.none{border-style:dotted}
textarea.comment{width:100%;margin-top:9px;font:inherit;padding:8px 10px;border:1px solid var(--line);border-radius:8px;min-height:44px;resize:vertical;background:#fbfcfe}
textarea.comment:focus{outline:2px solid var(--acc);border-color:var(--acc)}
.anschip{font-size:12px;color:var(--ok);font-weight:700}
footer{max-width:980px;margin:30px auto 60px;padding:0 16px}
#general-notes{width:100%;min-height:80px;font:inherit;padding:10px;border:1px solid var(--line);border-radius:10px}
.footbox{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px}
@media (max-width:760px){
  label.vrow{flex-wrap:wrap}
  .vinfo{flex:1 1 100%}
  audio{flex:1 1 100%}
}
</style>
</head>
<body>
<header id="top">
  <h1>🎧 Audyt odsłuchowy — wszystkie wersje sampli</h1>
  <div class="progress-wrap">
    <div class="bar"><div id="bar-fill"></div></div>
    <div id="progress-text">…</div>
    <div id="progress-detail"></div>
  </div>
  <div class="controls">
    <select id="filter">
      <option value="all">Wszystkie</option>
      <option value="unanswered">Nieocenione</option>
      <option value="answered">Ocenione</option>
      <option value="none">Ocenione „Żadna”</option>
      <option value="commented">Z komentarzem</option>
    </select>
    <input id="search" type="search" placeholder="Szukaj: numer lub nazwa karty…">
    <button id="btn-jump" class="ghost" title="Przewiń do pierwszej nieocenionej fabuły">▼ pierwsza nieoceniona</button>
  </div>
  <div class="controls">
    <button id="btn-save" class="ghost" title="Pobierz plik z postępem — można go potem wczytać">💾 Kopia postępu</button>
    <button id="btn-load" class="ghost">📂 Wczytaj kopię</button>
    <input type="file" id="file-load" accept=".json,application/json" hidden>
    <button id="btn-report-top" class="primary">Stwórz raport (JSON)</button>
    <details class="settings">
      <summary>⚙ Folder miniatur</summary>
      <p class="hint">Domyślnie: <code>__IMG_DEFAULT__</code> — pliki <code>&lt;numer&gt;FOT.png</code>.<br>
      Możesz też skopiować folder <code>img/</code> do katalogu <code>odsluch/</code> (obok index.html) — wtedy zadziała bez ścieżki.</p>
      <input id="imgdir" placeholder="C:\\Users\\…\\img\\">
    </details>
  </div>
  <p class="hint">Wybory zapisują się same w przeglądarce (localStorage) — zamknięcie karty nie traci postępu.
  Głośność wersji z różnych epok bywa różna (normalizacja −20 LUFS weszła później) — oceń brzmienie, nie głośność.</p>
</header>
<main id="list"></main>
<footer>
  <div class="footbox">
    <h2 style="margin-top:0">Uwagi ogólne do całego audytu</h2>
    <textarea id="general-notes" placeholder="Co ogólnie Ci się podoba / nie podoba? Jakie dźwięki są OK, jakie nie? Wzorce, które widzisz w nowych vs starych wersjach…"></textarea>
    <div class="controls" style="margin-top:14px;justify-content:center">
      <button id="btn-report" class="primary big">⬇ Stwórz raport (JSON)</button>
    </div>
    <p class="hint" style="text-align:center">Raport zawiera wszystkie Twoje wybory i komentarze. Pobrany plik wyślij agentowi (czat Arena) — na jego podstawie złapie dream team najlepszych MP3 i zaplanuje poprawki „Żadnych”.</p>
  </div>
</footer>
<script src="data.js"></script>
<script>
"use strict";
const NONE='__none__';
const LS='mtg-odsluch-audit-v1';
let state=(()=>{try{return JSON.parse(localStorage.getItem(LS))||{}}catch(e){return{}}})();
const $=s=>document.querySelector(s);
const esc=s=>String(s==null?'':s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const save=()=>{try{localStorage.setItem(LS,JSON.stringify(state))}catch(e){console.warn('localStorage:',e)}};

function winURL(dir,id){
  let p=String(dir||'').replace(/\\\\/g,'/').replace(/\/+$/,'');
  if(!p) return null;
  if(!/^([a-zA-Z]:|file:\\/\\/)/.test(p)) return null;
  return 'file:///'+encodeURI(p).replace(/#/g,'%23')+'/'+id+'FOT.png';
}
function labelOf(v){
  const parts=[];
  if(v.round) parts.push(v.round);
  if(v.batch) parts.push(v.batch+(v.vno?(' v'+v.vno):''));
  if(!parts.length&&v.slug) parts.push(v.slug);
  if(!parts.length) parts.push('bez etykiety');
  return parts.join(' · ')+' · '+v.date;
}
function cardHTML(s){
  const st=state[s.id]||{};
  const rows=s.versions.map(v=>{
    const badges=[
      v.current?'<span class="badge b-cur">OBECNY</span>':'',
      v.kinds.includes('prod')?'<span class="badge b-prod">produkcja</span>':'',
      (!v.kinds.includes('prod')&&v.kinds.includes('cand'))?'<span class="badge b-cand">kandydat</span>':'',
    ].join('');
    const det=(v.scenario||v.prompt)?('<details class="pdet"><summary>scenariusz / prompt tej generacji</summary><p>'
      +(v.scenario?('<b>'+esc(v.scenario)+'</b><br><br>'):'')+esc(v.prompt||'')
      +(v.gen?('<br><br><span style="color:var(--mut)">wygenerowano: '+esc(v.gen)+(v.gen_batch?(' · paczka '+esc(v.gen_batch)):'')+'</span>'):'')
      +'</p></details>'):'';
    return '<label class="vrow'+(v.current?' cur':'')+'" data-vid="'+v.vid+'">'
      +'<input type="radio" name="c_'+s.id+'" value="'+v.vid+'">'
      +'<span class="check"></span>'
      +'<div class="vinfo"><div class="vline">'+badges+'<span class="vlabel">'+esc(labelOf(v))+'</span></div>'+det+'</div>'
      +'<audio controls preload="none" src="audio/'+s.id+'/'+v.vid+'.mp3"></audio></label>';
  }).join('');
  const noneRow='<label class="vrow none" data-vid="'+NONE+'">'
    +'<input type="radio" name="c_'+s.id+'" value="'+NONE+'">'
    +'<span class="check"></span>'
    +'<div class="vinfo"><div class="vline"><span class="badge b-none">ŻADNA</span>'
    +'<span class="vlabel">żadna z powyższych — opisz dlaczego w uwagach</span></div></div></label>';
  return '<article class="card" data-id="'+s.id+'" data-titlelow="'+esc((''+s.title).toLowerCase())+'">'
    +'<div class="chead"><div class="thumb" data-id="'+s.id+'">'+esc(s.id)+'</div><div style="flex:1">'
    +'<h2><span class="sid">'+esc(s.id)+'</span>'+esc(s.title)+'</h2>'
    +'<div class="vcount">wersji audio: '+s.versions.length+(st.choice?' <span class="anschip">✓ oceniono</span>':'')+'</div>'
    +'<details class="narr"><summary>narracja fabuły</summary><p>'+esc(s.story||'')+'</p></details>'
    +(s.cur_scenario?('<details class="narr"><summary>obecny scenariusz sampla</summary><p>'+esc(s.cur_scenario)+'</p></details>'):'')
    +'</div></div>'
    +'<div class="versions">'+rows+noneRow+'</div>'
    +'<textarea class="comment" placeholder="Uwagi do tej fabuły (opcjonalnie) — która wersja i dlaczego, co poprawić…">'+esc(st.comment||'')+'</textarea>'
    +'</article>';
}
function renderAll(){
  $('#list').innerHTML=DATA.stories.map(cardHTML).join('');
  DATA.stories.forEach(s=>{
    const st=state[s.id]||{};
    if(st.choice) markChoice(s.id,st.choice);
  });
  applyFilter(); updateProgress();
}
function markChoice(id,val){
  const card=document.querySelector('.card[data-id="'+CSS.escape(id)+'"]');
  if(!card) return;
  card.querySelectorAll('label.vrow').forEach(l=>l.classList.toggle('sel',l.dataset.vid===val));
  card.classList.toggle('answered',!!val);
  const chip=card.querySelector('.anschip');
  if(val&&!chip){
    const vc=card.querySelector('.vcount');
    if(vc) vc.insertAdjacentHTML('beforeend',' <span class="anschip">✓ oceniono</span>');
  } else if(!val&&chip){chip.remove();}
}
function thumbsInit(){
  document.querySelectorAll('.thumb').forEach(t=>{
    const id=t.dataset.id;
    const img=document.createElement('img');
    img.loading='lazy'; img.alt='miniaturka '+id;
    let stage=0;
    const abs=winURL(state._imgdir||DATA.img_dir_default,id);
    img.onerror=()=>{
      stage++;
      if(stage===1&&abs){img.src=abs;return;}
      img.remove(); // zostaje numer jako placeholder
    };
    img.src='img/'+id+'FOT.png';
    t.appendChild(img);
  });
}
const storyById=new Map(DATA.stories.map(s=>[s.id,s]));
function cardVisible(card){
  const id=card.dataset.id;
  const st=state[id]||{}; const ans=!!st.choice;
  const f=$('#filter').value;
  if(f==='unanswered'&&ans)return false;
  if(f==='answered'&&!ans)return false;
  if(f==='none'&&st.choice!==NONE)return false;
  if(f==='commented'&&!st.comment)return false;
  const q=$('#search').value.trim().toLowerCase();
  if(q){
    const s=storyById.get(id);
    const low=card.dataset.titlelow||(''+(s?s.title:'')).toLowerCase();
    if(!(id===q||id.startsWith(q)||low.includes(q)))return false;
  }
  return true;
}
function applyFilter(){
  document.querySelectorAll('article.card').forEach(c=>c.classList.toggle('hidden',!cardVisible(c)));
}
function updateProgress(){
  const total=DATA.stories.length;
  let ans=0,none=0,comm=0;
  DATA.stories.forEach(s=>{
    const st=state[s.id]||{};
    if(st.choice){ans++;if(st.choice===NONE)none++;}
    if(st.comment)comm++;
  });
  $('#bar-fill').style.width=(total?Math.round(100*ans/total):0)+'%';
  $('#progress-text').textContent='Ocenione: '+ans+' / '+total;
  $('#progress-detail').textContent='wybrane wersje: '+(ans-none)+' · „żadna”: '+none+' · z komentarzem: '+comm;
}
document.addEventListener('play',e=>{
  if(e.target.tagName==='AUDIO')
    document.querySelectorAll('audio').forEach(a=>{if(a!==e.target)a.pause();});
},true);
$('#list').addEventListener('change',e=>{
  if(e.target.matches('input[type=radio]')){
    const card=e.target.closest('.card');const id=card.dataset.id;
    state[id]=state[id]||{};
    state[id].choice=e.target.value;
    state[id].ts=new Date().toISOString();
    save();markChoice(id,e.target.value);updateProgress();applyFilter();
  }
});
let cTimer=null;
$('#list').addEventListener('input',e=>{
  if(e.target.classList.contains('comment')){
    const id=e.target.closest('.card').dataset.id;
    state[id]=state[id]||{};
    state[id].comment=e.target.value;
    state[id].ts=new Date().toISOString();
    clearTimeout(cTimer);cTimer=setTimeout(save,350);
  }
});
$('#filter').addEventListener('change',applyFilter);
$('#search').addEventListener('input',applyFilter);
$('#btn-jump').addEventListener('click',()=>{
  const s=DATA.stories.find(s=>!(state[s.id]||{}).choice);
  if(!s){alert('Wszystkie fabuły są ocenione. 🎉');return;}
  const card=document.querySelector('.card[data-id="'+CSS.escape(s.id)+'"]');
  if(card){card.scrollIntoView({behavior:'smooth',block:'center'});card.style.outline='3px solid var(--acc)';
    setTimeout(()=>card.style.outline='',1800);}
});
$('#imgdir').value=state._imgdir||DATA.img_dir_default;
$('#imgdir').addEventListener('change',()=>{
  state._imgdir=$('#imgdir').value;save();thumbsInit();
});
$('#general-notes').value=state._notes||'';
$('#general-notes').addEventListener('input',()=>{
  state._notes=$('#general-notes').value;clearTimeout(cTimer);cTimer=setTimeout(save,350);
});
function download(name,text){
  const b=new Blob([text],{type:'application/json'});
  const a=document.createElement('a');
  a.href=URL.createObjectURL(b);a.download=name;
  document.body.appendChild(a);a.click();a.remove();
  setTimeout(()=>URL.revokeObjectURL(a.href),8000);
}
function stamp(){const d=new Date();const p=n=>String(n).padStart(2,'0');
  return d.getFullYear()+p(d.getMonth()+1)+p(d.getDate())+'-'+p(d.getHours())+p(d.getMinutes());}
function buildReport(){
  const choices=DATA.stories.map(s=>{
    const st=state[s.id]||{};
    const v=s.versions.find(x=>x.vid===st.choice);
    return{
      story_id:s.id,title:s.title,n_versions:s.versions.length,
      choice:st.choice===NONE?null:(st.choice||null),
      choice_none:st.choice===NONE,
      choice_label:v?labelOf(v):null,
      choice_current:v?!!v.current:null,
      choice_prompt:v?(v.prompt||null):null,
      choice_scenario:v?(v.scenario||null):null,
      comment:st.comment||'',answered_at:st.ts||null,
      versions:s.versions.map(x=>({vid:x.vid,label:labelOf(x),current:!!x.current,kinds:x.kinds}))
    };
  });
  const answered=choices.filter(c=>c.choice||c.choice_none).length;
  return{
    type:'listening-audit-report',version:1,generated_at:new Date().toISOString(),
    audit:{commit:DATA.commit,built:DATA.generated,stories:DATA.stories.length,
           versions_total:DATA.total_versions},
    summary:{stories:DATA.stories.length,answered,
             chose_version:choices.filter(c=>c.choice).length,
             chose_none:choices.filter(c=>c.choice_none).length,
             unanswered:DATA.stories.length-answered,
             with_comments:choices.filter(c=>c.comment).length},
    image_dir:state._imgdir||DATA.img_dir_default,
    general_notes:$('#general-notes').value||'',
    choices
  };
}
function makeReport(){
  const r=buildReport();
  if(r.summary.unanswered>0){
    if(!confirm('Masz jeszcze '+r.summary.unanswered+' nieocenionych fabuł.\\n'
      +'Wygenerować raport mimo to? (Anuluj = wróć do słuchania)'))return;
  }
  download('raport-audytu-odsluchowego-'+stamp()+'.json',JSON.stringify(r,null,2));
  alert('Raport zapisany: ocenione '+r.summary.answered+'/'+r.summary.stories
    +'\\n(„żadna”: '+r.summary.chose_none+', z komentarzem: '+r.summary.with_comments+')\\n'
    +'Wyślij pobrany plik agentowi.');
}
$('#btn-report').addEventListener('click',makeReport);
$('#btn-report-top').addEventListener('click',makeReport);
$('#btn-save').addEventListener('click',()=>{
  download('kopia-postepu-audytu-'+stamp()+'.json',JSON.stringify({
    type:'listening-audit-progress',version:1,
    saved_at:new Date().toISOString(),state},null,2));
});
$('#btn-load').addEventListener('click',()=>$('#file-load').click());
$('#file-load').addEventListener('change',e=>{
  const f=e.target.files[0];if(!f)return;
  const rd=new FileReader();
  rd.onload=()=>{
    try{
      const d=JSON.parse(rd.result);
      let st=null;
      if(d&&d.type==='listening-audit-progress'&&d.state)st=d.state;
      else if(d&&d.type==='listening-audit-report'&&Array.isArray(d.choices)){
        st={};
        d.choices.forEach(c=>{st[c.story_id]={};if(c.choice)st[c.story_id].choice=c.choice;
          if(c.choice_none)st[c.story_id].choice=NONE;
          if(c.comment)st[c.story_id].comment=c.comment;});
        if(d.general_notes)st._notes=d.general_notes;
      }else{alert('Nieznany format pliku.');return;}
      state=Object.assign({},state,st);
      save();renderAll();thumbsInit();
      $('#general-notes').value=state._notes||'';
      alert('Wczytano kopię postępu.');
    }catch(err){alert('Błąd wczytywania: '+err);}
  };
  rd.readAsText(f);e.target.value='';
});
window.addEventListener('beforeunload',save);
renderAll();thumbsInit();
</script>
</body>
</html>
"""


def render_site(inventory: dict, catalog: list[dict], scen: dict[str, dict]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stories = []
    for s in catalog:
        sid = str(s["id"])
        vers = inventory["stories"].get(sid, [])
        if not vers:
            continue
        cur = scen.get(sid, {})
        stories.append({
            "id": sid,
            "title": s.get("title", ""),
            "story": s.get("story", ""),
            "cur_scenario": cur.get("sample_scenario"),
            "cur_prompt": cur.get("prompt"),
            "cur_batch": cur.get("batch"),
            "versions": [
                {k: v[k] for k in (
                    "vid", "date", "round", "slug", "batch", "vno", "gen_batch",
                    "kinds", "current", "prompt", "scenario", "gen")}
                for v in vers
            ],
        })
    data = {
        "generated": dt.datetime.now().isoformat(timespec="seconds"),
        "commit": git("rev-parse", "HEAD").strip(),
        "total_versions": inventory["stats"]["versions"],
        "img_dir_default": IMG_DIR_DEFAULT,
        "stories": stories,
    }
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    payload = payload.replace("</", "<\\/")  # bezpieczne osadzenie w <script>
    (OUT_DIR / "data.js").write_text("const DATA = " + payload + ";\n", encoding="utf-8")
    page = (HTML.replace("__DATA_JSON__", "")
                .replace("__IMG_DEFAULT__", html.escape(IMG_DIR_DEFAULT)))
    (OUT_DIR / "index.html").write_text(page, encoding="utf-8")


README = """# Audyt odsłuchowy — instrukcja

Ten katalog jest **samodzielną aplikacją**: działa lokalnie, bez internetu.

## Jak odsłuchiwać

1. Ściągnij repozytorium na tej gałęzi (klon gita albo „Download ZIP”
   z GitHuba) i rozpakuj na pulpicie.
2. Otwórz podwójnym kliknięciem plik **`odsluch/index.html`**
   (Chrome/Edge/Firefox — cokolwiek nowszego).
3. Przy każdej fabule masz **wszystkie wersje jej sampla** z całej historii
   projektu: produkcyjne (to, co było w `audio/samples/` w danej epoce)
   i kandydatów z paczek wariantów. „OBECNY” = plik, który jest teraz
   w korpusie. Rozwiń „scenariusz / prompt tej generacji”, żeby zobaczyć,
   co dokładnie zamówiono.
4. **Zaptaszkuj** wersję, która podoba Ci się najbardziej — albo „ŻADNA”
   i wpisz w polu uwag, co jest nie tak / czego byś chciał.
5. Wybory zapisują się **same** w pamięci przeglądarki (localStorage).
   Przeładowanie strony czy restart komputera nie tracą postępu.
   Mimo to rób co jakiś czas **„💾 Kopia postępu”** — to plik JSON, który
   można potem wczytać przyciskiem „📂 Wczytaj kopię” (np. po przeniesieniu
   na inny komputer).

## Miniaturki kart

Strona szuka pliku `<numer>FOT.png` najpierw w `odsluch/img/`
(skopiuj tam swój folder `img` — wtedy działa wszędzie), a potem pod
ścieżką z ustawień (⚙ Folder miniatur), domyślnie:
`C:\\Users\\Jacek PC\\Desktop\\MtG Fusion\\img\\`.
Ścieżkę możesz zmienić w nagłówku strony.

## Koniec audytu

Na samym dole (i w nagłówku) jest przycisk **„Stwórz raport (JSON)”**.
Pobiera plik `raport-audytu-odsluchowego-<data>.json` ze wszystkimi
wyborami i komentarzami. **Wyślij ten plik agentowi** — na jego podstawie:

- zostanie złożony **dream team** (najlepsza wersja każdej fabuli wraca
  do `audio/samples/`),
- fabuły oznaczone „ŻADNA” dostaną nowy prompt zgodnie z Twoimi uwagami,
- przeprowadzę analizę preferencji (co się sprawdza, jakie parametry
  brzmią dobrze) na potrzeby przyszłych generacji.

## Uwagi techniczne

- Wersje z różnych epok mają różną głośność (normalizacja −20 LUFS
  weszła do produkcji dopiero 2026-09-28/29). Oceń brzmienie, nie poziom.
- Nazwy plików audio to skróty blobów gita (`<vid>.mp3`) — identyfikator
  wersji w raporcie mapuje się 1:1 na dokładną zawartość pliku z historii.
- Stronę przebudowuje `python scripts/build_listening_audit.py`
  (wymaga pełnej historii gita: `git fetch origin '+refs/heads/*:refs/remotes/origin/*'`).

Wygenerowano: __GENERATED__ · commit `__COMMIT__` · fabuł: __NSTORIES__ · wersji audio: __NVERS__.
"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stats", action="store_true", help="tylko statystyki, bez budowania")
    args = ap.parse_args()

    if not git_root_refs_present():
        print("UWAGA: repo wygląda na shallow — najpierw:")
        print("  git fetch --unshallow origin '+refs/heads/*:refs/remotes/origin/*'")
        return 2

    print("Zbieram zdarzenia z historii gita…")
    events = collect_events()
    print(f"  zdarzeń MP3: {len(events)}")
    print("Ładuję manifest generacji (drzewo + unia z historii)…")
    manifest = manifest_entries()
    print(f"  wpisów manifestu: {len(manifest)}")
    inv = build_inventory(events, manifest)
    st = inv["stats"]
    print(f"  fabuł z wersjami: {len(inv['stories'])} · unikalnych wersji: {st['versions']} "
          f"(produkcja-obecne: {st['current']}, z promptem: {st['prompt_matched']})")

    # warianty tylko w drzewie roboczym (gitignore) — sprawdź pokrycie historią
    wt = list((REPO / "variants").rglob("*.mp3")) if (REPO / "variants").exists() else []
    if wt:
        proc = subprocess.run(["git", "hash-object", "--stdin-paths"], cwd=REPO,
                              input="\n".join(str(p) for p in wt),
                              capture_output=True, text=True)
        hashes = proc.stdout.split()
        known = {v["blob"] for vers in inv["stories"].values() for v in vers}
        missing = [p for p, h in zip(wt, hashes) if h not in known]
        print(f"  warianty w drzewie roboczym: {len(wt)}, poza historią gita: {len(missing)}")
        for p in missing[:10]:
            print(f"    brak w historii: {p}")

    per_batch: dict[str, int] = defaultdict(int)
    for vers in inv["stories"].values():
        for v in vers:
            if v["batch"]:
                per_batch[v["batch"]] += 1
    print("  warianty per paczka:", dict(sorted(per_batch.items())))

    if args.stats:
        return 0

    print("Eksportuję pliki audio…")
    written, skipped, total = export_blobs(inv)
    print(f"  zapisano {written}, pominięto (już były) {skipped}, razem {total}")

    catalog = load_catalog()
    scen = load_current_scenarios()
    missing_audio = [s["id"] for s in catalog
                     if str(s["id"]) not in inv["stories"]]
    if missing_audio:
        print(f"  UWAGA: fabuły bez żadnej wersji w historii: {missing_audio}")

    print("Buduję stronę…")
    render_site(inv, catalog, scen)
    (OUT_DIR / "README.md").write_text(
        README.replace("__GENERATED__", dt.date.today().isoformat())
              .replace("__COMMIT__", git("rev-parse", "HEAD").strip()[:10])
              .replace("__NSTORIES__", str(len(catalog)))
              .replace("__NVERS__", str(st["versions"])),
        encoding="utf-8")
    print(f"Gotowe: {OUT_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
