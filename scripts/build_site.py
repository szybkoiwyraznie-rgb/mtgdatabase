#!/usr/bin/env python3
"""Gablotka/biblioteka systemu sygnatur (GitHub Pages) — wersja wielostronicowa.

Strony:
  index.html          — spis treści biblioteki + liczniki + archiwum bramek
  fabuly.html         — fabuły z gotową sygnaturą: odsłuch, scenariusz, linki
  baza-tla.html       — (d) backgrounds: pełne metadane + odsłuch
  baza-hero.html      — (c) heroes: pełne metadane + odsłuch
  baza-gesty.html     — (a) gestures: definicja nutowa + opis + demo (jeśli da się wyrenderować)
  baza-instrumenty.html — (b) instruments: charakter + odsłuch każdej nuty

Bramki odbywają się poza Pages (docs/gate-protocol.md). Ta strona jest
wyłącznie biblioteką tego, co właściciel już zatwierdził.

Usage: python scripts/build_site.py --out site/generated
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
LIB = REPO / "data" / "library"

CSS = """
  :root { color-scheme: dark; }
  body { font-family: ui-sans-serif, system-ui, sans-serif; background:#111418; color:#e6e9ee; max-width:900px; margin:0 auto; padding:24px 16px 90px; line-height:1.55; }
  a { color:#7db4f2; text-decoration:none; } a:hover { text-decoration:underline; }
  h1 { font-size:1.4rem; } h2 { font-size:1.05rem; margin:0 0 .3em; }
  .sub { color:#9fb3c8; font-size:.9rem; margin-bottom:2em; }
  nav { display:flex; flex-wrap:wrap; gap:10px; margin:1.4em 0 2.2em; }
  nav a, .tile { display:block; background:#181c22; border:1px solid #262c36; border-radius:12px; padding:14px 18px; color:#e6e9ee; min-width:150px; }
  nav a:hover { border-color:#f2c66d; text-decoration:none; }
  .tile b { display:block; font-size:1.02rem; margin-bottom:.2em; }
  .tile span { font-size:.8rem; color:#8bd3a8; }
  .card { background:#181c22; border:1px solid #262c36; border-radius:12px; padding:14px 18px; margin:.8em 0; }
  .eid { color:#f2c66d; font-weight:700; font-family:ui-monospace, monospace; font-size:.92rem; }
  .meta { font-size:.82rem; color:#aeb9c4; margin:.35em 0; }
  .src { font-size:.72rem; color:#6c7a89; margin-top:.5em; }
  .ok { font-size:.75rem; color:#8bd3a8; }
  .use { font-size:.78rem; color:#9fb3c8; margin-top:.4em; }
  .story { font-size:.86rem; color:#aeb9c4; margin:.5em 0; }
  .scen { font-size:.82rem; background:#0d1014; border-radius:8px; padding:8px 12px; color:#c9d4df; margin:.4em 0; }
  audio { width:100%; height:34px; margin-top:.5em; }
  .notes td { font-family:ui-monospace, monospace; font-size:.78rem; padding:2px 10px 2px 0; color:#c9d4df; }
  .empty { background:#181c22; border:1px dashed #39424f; border-radius:12px; padding:22px; color:#8a97a5; font-size:.9rem; text-align:center; }
  .gate { font-size:.82rem; color:#9fb3c8; }
"""

NAV = ("<nav>"
       "<a class=\"tile\" href=\"baza-tla.html\"><b>(d) Tła</b><span>{n_d} wpisów</span></a>"
       "<a class=\"tile\" href=\"baza-hero.html\"><b>(c) Hero</b><span>{n_c} wpisów</span></a>"
       "<a class=\"tile\" href=\"baza-gesty.html\"><b>(a) Gesty muzyczne</b><span>{n_a} wpisów</span></a>"
       "<a class=\"tile\" href=\"baza-instrumenty.html\"><b>(b) Instrumenty</b><span>{n_b} wpisów</span></a>"
       "<a class=\"tile\" href=\"fabuly.html\"><b>Fabuły z sygnaturą</b><span>{n_s} gotowych</span></a>"
       "</nav>")

PAGE = """<!doctype html>
<html lang="pl"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — Biblioteka sygnatur</title>
<style>{css}</style></head><body>
{body}
<p class="src" style="margin-top:3em">System sygnatur — <a href="index.html">strona główna biblioteki</a></p>
</body></html>
"""


def esc(x) -> str:
    return html.escape(str(x))


def load(path: Path, default):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default


def src_line(src: dict | None) -> str:
    if not src:
        return ""
    parts = [esc(src.get("title", "")), esc(src.get("author", "")), esc(src.get("license", ""))]
    line = " · ".join(p for p in parts if p)
    if src.get("notes"):
        line += f" — {esc(src['notes'])}"
    if src.get("url"):
        line += f' · <a href="{esc(src["url"])}">źródło</a>'
    return f'<p class="src">{line}</p>'


def approved_line(ap: dict | None) -> str:
    if not ap:
        return ""
    return f'<p class="ok">✓ zatwierdzone: {esc(ap.get("gate", ""))} ({esc(ap.get("date", ""))}), wybór {esc(ap.get("choice", ""))}</p>'


# katalog wyjściowy bieżącego builda — potrzebny do odcisku pliku audio
_OUT: Path | None = None


def cache_bust(src_rel: str) -> str:
    """Dokleja ?v=<odcisk treści>, żeby przeglądarka nie grała starej wersji.

    Bez tego player trzyma w cache plik o tej samej nazwie (np. audio/5.mp3)
    nawet po przemontowaniu fabuły — właściciel słyszał starą sygnaturę.
    """
    if _OUT is None:
        return src_rel
    f = _OUT / src_rel
    if not f.exists():
        return src_rel
    digest = hashlib.md5(f.read_bytes()).hexdigest()[:10]
    return f"{src_rel}?v={digest}"


def player(src_rel: str) -> str:
    return f'<audio controls preload="none" src="{esc(cache_bust(src_rel))}"></audio>'


def usage_line(uses: list[str], link: bool = True) -> str:
    if not uses:
        return '<p class="use">jeszcze nieużywany w żadnej sygnaturze</p>'
    items = ", ".join(f'<a href="fabuly.html#f{esc(u)}">fabuła {esc(u)}</a>' if link else esc(u) for u in uses)
    return f'<p class="use">używany w: {items}</p>'


def page(title: str, body: str) -> str:
    return PAGE.format(title=esc(title), css=CSS, body=body)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=REPO / "site" / "generated")
    args = parser.parse_args()
    out = args.out.resolve()
    audio_out = out / "audio"
    lib_out = audio_out / "lib"
    import shutil
    if out.exists():
        shutil.rmtree(out)
    lib_out.mkdir(parents=True, exist_ok=True)
    global _OUT
    _OUT = out

    catalog = load(REPO / "data" / "catalog.json", {"stories": []})["stories"]
    regs = {k: load(LIB / f"{k}.json", {"entries": []})["entries"] for k in
            ("backgrounds", "heroes", "gestures", "instruments")}
    recipes = {p.stem: load(p, {}) for p in (REPO / "data" / "recipes").glob("*.json")}
    sig_dir = REPO / "audio" / "signatures"
    sigs = {p.stem: p for p in sig_dir.glob("*.mp3")} if sig_dir.is_dir() else {}

    # mapa użycia: id klocka -> [id fabuł]
    usage: dict[str, list[str]] = {}
    for sid, r in recipes.items():
        keys = [r.get("background", {}).get("id"), r.get("hero", {}).get("id")]
        coda = r.get("coda") or {}
        keys += [coda.get("gesture"), coda.get("instrument")]
        for k in keys:
            if k:
                usage.setdefault(k, []).append(sid)

    def copy_audio(src_rel: str) -> str | None:
        src = REPO / src_rel
        if not src.exists():
            return None
        dst = lib_out / src_rel.replace("audio/library/", "").replace("/", "_")
        shutil.copy2(src, dst)
        return f"audio/lib/{dst.name}"

    # ---------- baza: tła ----------
    cards = []
    for e in sorted(regs["backgrounds"], key=lambda x: x["id"]):
        audio = copy_audio(e["file"])
        cards.append(
            f'<div class="card" id="{esc(e["id"])}"><h2><span class="eid">{esc(e["id"])}</span></h2>'
            f'<p class="meta"><b>{esc(e.get("setting", ""))}</b> — {esc(e.get("desc", ""))} · '
            f'{e.get("duration_sec", "?")} s · poziom ref. {e.get("level_ref_db", "?")} dB · pętla: {"tak" if e.get("loopable") else "nie"}</p>'
            + (player(audio) if audio else '<p class="meta">(brak pliku)</p>')
            + approved_line(e.get("approved")) + usage_line(usage.get(e["id"], [])) + src_line(e.get("source")) + "</div>")
    bg_body = ("<h1>Baza (d) — tła</h1><p class=\"sub\">Przestrzenie miejsca: niski równy podkład pod całe okno sygnatury.</p>"
               + ("\n".join(cards) if cards else '<div class="empty">baza pusta — pierwsze tła czekają na bramkę odsłuchową</div>'))
    (out / "baza-tla.html").write_text(page("Baza tła", bg_body), encoding="utf-8")

    # ---------- baza: hero ----------
    cards = []
    for e in sorted(regs["heroes"], key=lambda x: x["id"]):
        audio = copy_audio(e["file"])
        good = ", ".join(esc(g) for g in e.get("good_for", []))
        bad = ", ".join(esc(b) for b in e.get("bad_for", []))
        cards.append(
            f'<div class="card" id="{esc(e["id"])}"><h2><span class="eid">{esc(e["id"])}</span></h2>'
            f'<p class="meta"><b>rola: {esc(e.get("role", ""))}</b> — {esc(e.get("desc", ""))}<br>'
            f'charakter: {esc(e.get("character", ""))} · dystans: {esc(e.get("distance", ""))} · energia: {esc(e.get("energy", ""))} · {e.get("duration_sec", "?")} s<br>'
            + (f"dobry do: {good} · " if good else "") + (f"zły do: {bad}" if bad else "") + "</p>"
            + (player(audio) if audio else '<p class="meta">(brak pliku)</p>')
            + approved_line(e.get("approved")) + usage_line(usage.get(e["id"], [])) + src_line(e.get("source")) + "</div>")
    hero_body = ("<h1>Baza (c) — hero</h1><p class=\"sub\">Główne zdarzenia fabuł: żywe, rozpoznawalne nagrania.</p>"
                 + ("\n".join(cards) if cards else '<div class="empty">baza pusta — pierwsi hero czekają na bramkę</div>'))
    (out / "baza-hero.html").write_text(page("Baza hero", hero_body), encoding="utf-8")

    # ---------- baza: gesty ----------
    try:
        import sys
        sys.path.insert(0, str(REPO / "scripts"))
        import coda_synth
        import sig_audio as dsp
    except Exception:
        coda_synth = None

    def gesture_demo(g: dict) -> str | None:
        if not coda_synth:
            return None
        inst_ids = usage.get(g["id"], [])
        candidate_insts = []
        for sid in inst_ids:
            coda = recipes.get(sid, {}).get("coda") or {}
            if coda.get("gesture") == g["id"] and coda.get("instrument"):
                candidate_insts.append(coda["instrument"])
        tags = set(g.get("instrument_tags", []))
        candidate_insts += [i["id"] for i in regs["instruments"] if tags & set(i.get("instrument_tags", []) or [])]
        candidate_insts += [i["id"] for i in regs["instruments"]]
        for inst_id in dict.fromkeys(candidate_insts):
            inst = next((i for i in regs["instruments"] if i["id"] == inst_id), None)
            if not inst:
                continue
            try:
                samples = inst.get("samples", {})
                if "articulations" in samples:
                    sample_map = {"articulations": {a: [str(REPO / f) for f in fs] for a, fs in samples["articulations"].items()}}
                else:
                    sample_map = {k: str(REPO / v) for k, v in samples.items()}
                res = coda_synth.render_coda(g, {**inst, "samples": sample_map}, seed=11)
                if res.note_count == 0 or len(res.warnings) >= res.note_count:
                    continue
                dst = lib_out / f"demo_{g['id']}.mp3"
                dsp.encode_mp3(dst, dsp.peak_ceiling(res.wave, 0.9))
                return f"audio/lib/{dst.name}"
            except Exception:
                continue
        return None

    cards = []
    for g in sorted(regs["gestures"], key=lambda x: x["id"]):
        rows = "".join(
            f"<tr><td>{esc(dsp.midi_to_name(int(n['midi']))) if coda_synth else n['midi']}</td>"
            f"<td>{float(n['on']):.2f}–{float(n['off']):.2f} s</td><td>vel {float(n.get('vel', 0.8)):.2f}</td></tr>"
            for n in g.get("notes", []))
        if not coda_synth:
            rows = "".join(f"<tr><td>nuta {n.get('midi')}</td><td>{float(n['on']):.2f}–{float(n['off']):.2f} s</td><td>vel {float(n.get('vel', 0.8)):.2f}</td></tr>" for n in g.get("notes", []))
        demo = gesture_demo(g)
        cards.append(
            f'<div class="card" id="{esc(g["id"])}"><h2><span class="eid">{esc(g["id"])}</span></h2>'
            f'<p class="meta"><b>{esc(g.get("semantic", ""))}</b> — {esc(g.get("desc", ""))}</p>'
            f'<table class="notes"><tr><td><i>nuta</i></td><td><i>czas</i></td><td><i>siła</i></td></tr>{rows}</table>'
            + (player(demo) if demo else '<p class="meta">(odsłuch po pierwszym użyciu w sygnaturze)</p>')
            + approved_line(g.get("approved")) + usage_line(usage.get(g["id"], [])) + "</div>")
    ges_body = ("<h1>Baza (a) — gesty muzyczne</h1><p class=\"sub\">Muzyczne odpowiedzi świata: definicje nutowe z semantyką. Brzmienie zależy od wybranego instrumentu (b).</p>"
                + ("\n".join(cards) if cards else '<div class="empty">baza pusta — pierwsze gesty czekają na bramkę</div>'))
    (out / "baza-gesty.html").write_text(page("Baza gesty", ges_body), encoding="utf-8")

    # ---------- baza: instrumenty ----------
    cards = []
    for e in sorted(regs["instruments"], key=lambda x: x["id"]):
        note_players = []
        samples = e.get("samples", {})
        items = sorted(samples.items(), key=lambda kv: int(kv[0]) if str(kv[0]).isdigit() else 999) if "articulations" not in samples else []
        for midi, rel in items:
            rel_audio = copy_audio(rel)
            if rel_audio:
                label = dsp.midi_to_name(int(midi)) if coda_synth else f"nuta {midi}"
                note_players.append(f"<p class=\"meta\">{label}</p>{player(rel_audio)}")
        cards.append(
            f'<div class="card" id="{esc(e["id"])}"><h2><span class="eid">{esc(e["id"])}</span></h2>'
            f'<p class="meta"><b>{esc(e.get("semantic", ""))}</b> · rodzina: {esc(e.get("family", ""))} · '
            f'{len(samples.get("articulations", samples))} próbek</p>'
            + "".join(note_players)
            + approved_line(e.get("approved")) + usage_line(usage.get(e["id"], [])) + src_line(e.get("source")) + "</div>")
    inst_body = ("<h1>Baza (b) — instrumenty</h1><p class=\"sub\">Brzmienie kód: jednostkowe nagrania prawdziwych instrumentów.</p>"
                 + ("\n".join(cards) if cards else '<div class="empty">baza pusta — pierwsze instrumenty czekają na bramkę</div>'))
    (out / "baza-instrumenty.html").write_text(page("Baza instrumenty", inst_body), encoding="utf-8")

    # ---------- fabuły z sygnaturą ----------
    by_id = {int(s["id"]): s for s in catalog}

    def last_touch(sid: str) -> tuple[float, str]:
        """Czas ostatniej modyfikacji fabuły (żądanie właściciela: najnowsze
        najwyżej). Bierzemy nowszą z dat commitów sygnatury i receptury;
        dla plików niezacommitowanych — mtime z dysku."""
        import subprocess
        best = 0.0
        for path in (sigs[sid], REPO / "data" / "recipes" / f"{sid}.json"):
            try:
                ct = subprocess.run(["git", "log", "-1", "--format=%ct", "--", str(path)],
                                    capture_output=True, text=True, cwd=REPO, timeout=10)
                ts = float(ct.stdout.strip() or 0)
                dirty = subprocess.run(["git", "status", "--porcelain", "--", str(path)],
                                       capture_output=True, text=True, cwd=REPO, timeout=10)
                if dirty.stdout.strip() or ts == 0:
                    ts = max(ts, path.stat().st_mtime)
            except Exception:
                ts = path.stat().st_mtime if path.exists() else 0.0
            best = max(best, ts)
        import datetime
        label = datetime.datetime.fromtimestamp(best).strftime("%Y-%m-%d %H:%M") if best else "?"
        return best, label

    touched = {sid: last_touch(sid) for sid in sigs}
    cards = []
    for sid in sorted(sigs, key=lambda s: (-touched[s][0], int(s))):
        story = by_id.get(int(sid))
        if not story:
            continue
        dst = audio_out / f"{sid}.mp3"
        shutil.copy2(sigs[sid], dst)
        r = recipes.get(sid, {})
        coda = r.get("coda") or {}
        scen = []
        bg = r.get("background", {})
        if bg.get("id"):
            scen.append(f'0,0 s — tło <a href="baza-tla.html#{esc(bg["id"])}">{esc(bg["id"])}</a> ({bg.get("target_db", "?")} dB)')
        hr = r.get("hero", {})
        if hr.get("id"):
            scen.append(f'{float(hr.get("at_sec", 0)):.1f} s — hero <a href="baza-hero.html#{esc(hr["id"])}">{esc(hr["id"])}</a> ({hr.get("target_db", "?")} dB)')
        if coda.get("gesture"):
            scen.append(f'{float(coda.get("at_sec", 0)):.1f} s — koda <a href="baza-gesty.html#{esc(coda["gesture"])}">{esc(coda["gesture"])}</a> '
                        f'na <a href="baza-instrumenty.html#{esc(coda.get("instrument", ""))}">{esc(coda.get("instrument", ""))}</a> ({coda.get("target_db", "?")} dB)')
        scen.append(f'długość {r.get("length_sec", "?")} s · seed {r.get("seed", "?")}')
        scen.append(f'zmieniono {touched[sid][1]}')
        cards.append(
            f'<div class="card" id="f{esc(sid)}"><h2><span class="eid">{esc(sid)}</span> {esc(story["title"])}</h2>'
            f'<p class="story">{esc(story["story"])}</p>'
            f'<p class="scen">{" · ".join(scen)}</p>'
            + player(f"audio/{sid}.mp3") + "</div>")
    fab_body = ("<h1>Fabuły z gotową sygnaturą</h1>"
                f"<p class=\"sub\">{len(sigs)} gotowych · najnowsze zmiany najwyżej · receptury w <code>data/recipes/</code> · produkty w <code>audio/signatures/&lt;id&gt;.mp3</code></p>"
                + ("\n".join(cards) if cards else '<div class="empty">jeszcze żadna fabuła nie ma sygnatury — pierwsza bramka (g001) w toku</div>'))
    (out / "fabuly.html").write_text(page("Fabuły", fab_body), encoding="utf-8")

    # ---------- gates archive ----------
    gate_rows = []
    gates_dir = REPO / "data" / "gates"
    for gdir in sorted(gates_dir.glob("g*/")) if gates_dir.exists() else []:
        m = load(gdir / "manifest.json", None)
        if not m:
            continue
        stories = ", ".join(str(s["story_id"]) for s in m.get("stories", []))
        state = "rozstrzygnięta" if m.get("verdicts") else "czeka na werdykt"
        gate_rows.append(f'<p class="gate"><b>{esc(m["id"])}</b> ({esc(m.get("created", ""))}) — fabuły: {esc(stories)} — {state}</p>')

    # ---------- index ----------
    nav = NAV.format(n_d=len(regs["backgrounds"]), n_c=len(regs["heroes"]), n_a=len(regs["gestures"]),
                     n_b=len(regs["instruments"]), n_s=len(sigs))
    idx_body = ("<h1>Biblioteka sygnatur</h1>"
                "<p class=\"sub\">Warstwa dźwiękowa gry fabularnej: każda fabuła = tło (d) + hero (c) + gest muzyczny (a) na instrumencie (b). "
                "Wszystko tu jest zatwierdzone w bramkach odsłuchowych.</p>" + nav
                + ("<h2>Archiwum bramek</h2>" + "".join(gate_rows) if gate_rows else ""))
    (out / "index.html").write_text(page("Biblioteka sygnatur", idx_body), encoding="utf-8")
    print(f"{out}: 6 stron, {sum(len(v) for v in regs.values())} wpisów baz, {len(sigs)} sygnatur")


if __name__ == "__main__":
    main()
