#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Postprodukcja korpusu sampli: wyrównanie głośności, limiter, filtr DC.

Powód (audyt 2026-09-28, `docs/audits/2026-09-28-audio-audit-fullscan.md`):
korpus miał rozpiętość głośności 43,9 LU, 58 plików z true peakiem powyżej
+1 dBTP, 19 z offsetem DC i 28 z energią zepchniętą w infradźwięki. Przy
odsłuchu seryjnym „cichy" myliło się z „zły".

Łańcuch na plik:

1. filtr górnoprzepustowy — 25 Hz dla wszystkich (offset DC i subsonic),
   45 Hz dla plików oflagowanych w audycie jako `sub_dominant` (> 80 %
   energii poniżej 60 Hz — na typowym sprzęcie to i tak niesłyszalne,
   a zjada cały headroom),
2. pomiar głośności (LUFS wg BS.1770-4) i wzmocnienie do wspólnego celu,
   z limitem wzmocnienia (domyślnie +15 dB — powyżej wychodzi szum tła),
3. limiter true peak z miękką obwiednią, sufit domyślnie −1 dBTP,
4. zapis MP3 (VBR, jakość 0) + weryfikacja **na zapisanym pliku**:
   ponowny pomiar LUFS/true peak i SNR transkodowania.

Operacja jest odwracalna: poprzednia wersja plików siedzi w historii gita.

Użycie:
    python scripts/postprocess_samples.py --dry-run
    python scripts/postprocess_samples.py --report data/samples/postprocess.json
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy import ndimage, signal

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_samples_full import integrated_lufs, true_peak_dbtp  # noqa: E402

EPS = 1e-12
ROOT = Path(__file__).resolve().parent.parent


def db_to_lin(x: float) -> float:
    return 10.0 ** (x / 20.0)


def highpass(data: np.ndarray, fs: int, cutoff: float) -> np.ndarray:
    """Filtr górnoprzepustowy bez przesunięcia fazy (filtfilt, 2. rzędu)."""
    sos = signal.butter(2, cutoff, btype="highpass", fs=fs, output="sos")
    return signal.sosfiltfilt(sos, data, axis=0)


def biquad_low_shelf(data: np.ndarray, fs: int, fc: float = 180.0, gain_db: float = -3.0, q: float = 0.707) -> np.ndarray:
    A = 10.0 ** (gain_db / 40.0)
    w0 = 2.0 * math.pi * fc / fs
    cos_w0 = math.cos(w0)
    sin_w0 = math.sin(w0)
    alpha = sin_w0 / (2.0 * q)
    b0 = A * ((A + 1.0) - (A - 1.0) * cos_w0 + 2.0 * math.sqrt(A) * alpha)
    b1 = 2.0 * A * ((A - 1.0) - (A + 1.0) * cos_w0)
    b2 = A * ((A + 1.0) - (A - 1.0) * cos_w0 - 2.0 * math.sqrt(A) * alpha)
    a0 = (A + 1.0) + (A - 1.0) * cos_w0 + 2.0 * math.sqrt(A) * alpha
    a1 = -2.0 * ((A - 1.0) + (A + 1.0) * cos_w0)
    a2 = (A + 1.0) + (A - 1.0) * cos_w0 - 2.0 * math.sqrt(A) * alpha
    b = np.array([b0, b1, b2]) / a0
    a = np.array([a0, a1, a2]) / a0
    return signal.lfilter(b, a, data, axis=0)


def biquad_high_shelf(data: np.ndarray, fs: int, fc: float = 3500.0, gain_db: float = 3.5, q: float = 0.707) -> np.ndarray:
    A = 10.0 ** (gain_db / 40.0)
    w0 = 2.0 * math.pi * fc / fs
    cos_w0 = math.cos(w0)
    sin_w0 = math.sin(w0)
    alpha = sin_w0 / (2.0 * q)
    b0 = A * ((A + 1.0) + (A - 1.0) * cos_w0 + 2.0 * math.sqrt(A) * alpha)
    b1 = -2.0 * A * ((A - 1.0) + (A + 1.0) * cos_w0)
    b2 = A * ((A + 1.0) + (A - 1.0) * cos_w0 - 2.0 * math.sqrt(A) * alpha)
    a0 = (A + 1.0) - (A - 1.0) * cos_w0 + 2.0 * math.sqrt(A) * alpha
    a1 = 2.0 * ((A - 1.0) - (A + 1.0) * cos_w0)
    a2 = (A + 1.0) - (A - 1.0) * cos_w0 - 2.0 * math.sqrt(A) * alpha
    b = np.array([b0, b1, b2]) / a0
    a = np.array([a0, a1, a2]) / a0
    return signal.lfilter(b, a, data, axis=0)


def biquad_peaking(data: np.ndarray, fs: int, fc: float = 4500.0, gain_db: float = -3.5, q: float = 1.2) -> np.ndarray:
    A = 10.0 ** (gain_db / 40.0)
    w0 = 2.0 * math.pi * fc / fs
    cos_w0 = math.cos(w0)
    sin_w0 = math.sin(w0)
    alpha = sin_w0 / (2.0 * q)
    b0 = 1.0 + alpha * A
    b1 = -2.0 * cos_w0
    b2 = 1.0 - alpha * A
    a0 = 1.0 + alpha / A
    a1 = -2.0 * cos_w0
    a2 = 1.0 - alpha / A
    b = np.array([b0, b1, b2]) / a0
    a = np.array([a0, a1, a2]) / a0
    return signal.lfilter(b, a, data, axis=0)


def limit_true_peak(data: np.ndarray, fs: int, ceiling_db: float,
                    attack_ms: float = 1.5) -> tuple[np.ndarray, float]:
    """Limiter działający na obwiedni nadpróbkowanej 4x.

    Zwraca (sygnał, szczytowa redukcja wzmocnienia w dB, średnia redukcja
    w dB). Szczyt mówi, jak mocno przycięty jest najgłośniejszy transjent,
    średnia — jak bardzo dociśnięty jest cały plik; do budżetowania nadaje się
    tylko ta druga. Zamiast twardego
    obcinania próbek liczymy gładką krzywą wzmocnienia (minimum filter +
    wygładzenie gaussowskie), więc nie powstają trzaski ani zniekształcenia
    schodkowe.
    """
    ceiling = db_to_lin(ceiling_db)
    up = signal.resample_poly(data, 4, 1, axis=0)
    env = np.max(np.abs(up), axis=1)
    if float(np.max(env)) <= ceiling:
        return data, 0.0, 0.0

    gain = np.minimum(1.0, ceiling / np.maximum(env, EPS))
    win = max(3, int(attack_ms * 1e-3 * fs * 4))
    gain = ndimage.minimum_filter1d(gain, size=2 * win + 1, mode="nearest")
    gain = ndimage.gaussian_filter1d(gain, sigma=win / 2.0, mode="nearest")
    gain_ds = gain[::4][: len(data)]
    if len(gain_ds) < len(data):  # dopchnięcie po zaokrągleniu długości
        gain_ds = np.pad(gain_ds, (0, len(data) - len(gain_ds)), mode="edge")
    out = data * gain_ds[:, None]

    # zabezpieczenie: po wygładzeniu obwiedni może zostać ułamek dB nad sufitem
    tp = db_to_lin(true_peak_dbtp(out, fs))
    if tp > ceiling:
        out = out * (ceiling / tp)
    gr_db = 20.0 * np.log10(np.maximum(gain_ds, EPS))
    return out, round(float(np.min(gr_db)), 2), round(float(np.mean(gr_db)), 2)


def transcode_snr(before: np.ndarray, after: np.ndarray) -> float:
    """SNR między sygnałem przed i po zapisie MP3 (wyrównany o opóźnienie)."""
    a, b = before.mean(axis=1), after.mean(axis=1)
    n = min(len(a), len(b))
    if n < 64:
        return 0.0
    a, b = a[:n], b[:n]
    corr = np.fft.irfft(np.fft.rfft(b, 2 * n) * np.conj(np.fft.rfft(a, 2 * n)))
    lag = int(np.argmax(corr[:2000]))
    bb = b[lag:]
    aa = a[: len(bb)]
    err = aa - bb
    return round(float(10.0 * np.log10(np.sum(aa**2) / max(float(np.sum(err**2)), EPS))), 1)


def gain_and_limit(filtered: np.ndarray, fs: int, *, gain_db: float, ceiling_db: float,
                   target_lufs: float, max_total_gain_db: float, max_limiter_gr_db: float,
                   tol_lu: float, iters: int, max_makeup_db: float = 4.0,
                   max_peak_gr_db: float = 12.0) -> tuple[np.ndarray, float, float, float]:
    """Wzmocnienie + limiter z pętlą kompensacji ubytku po limitowaniu.

    Limiter ścina transjenty, więc materiał perkusyjny po limitowaniu ląduje
    kilka LU poniżej celu (sam limiter potrafi zabrać 5–10 dB szczytu). Pętla
    domierza głośność na sygnale **po** limitowaniu i dokłada wzmocnienie,
    dopóki: (a) ubytek przekracza tolerancję, (b) budżet redukcji limitera nie
    jest wyczerpany, (c) łączne wzmocnienie mieści się w limicie (ochrona
    przed wyciąganiem szumu tła).

    Zwraca (sygnał, łączne wzmocnienie dB, szczytowa i średnia redukcja
    limitera dB, LUFS wyniku).
    """
    total = base = min(gain_db, max_total_gain_db)
    processed, limiter_gr, limiter_gr_mean = limit_true_peak(
        filtered * db_to_lin(total), fs, ceiling_db)
    lufs_now = integrated_lufs(processed, fs)
    for _ in range(max(0, iters)):
        deficit = target_lufs - lufs_now
        if deficit <= tol_lu or limiter_gr_mean <= -max_limiter_gr_db:
            break
        step = min(deficit, 2.0, max_total_gain_db - total, base + max_makeup_db - total)
        if step <= 0.01:
            break
        cand_total = total + step
        cand, cand_gr, cand_gr_mean = limit_true_peak(
            filtered * db_to_lin(cand_total), fs, ceiling_db)
        cand_lufs = integrated_lufs(cand, fs)
        if cand_lufs - lufs_now < 0.15 * step:  # dalsze pompowanie już nic nie daje
            break
        if cand_gr <= -max_peak_gr_db:  # atak zostałby spłaszczony
            break
        total, processed, lufs_now = cand_total, cand, cand_lufs
        limiter_gr, limiter_gr_mean = cand_gr, cand_gr_mean
    return processed, round(total, 2), limiter_gr, limiter_gr_mean, lufs_now


def mono_excess_lu(data: np.ndarray, fs: int) -> float:
    """Strata przy zejściu do mono PONAD bazowe 3,01 LU wynikające z definicji
    BS.1770 (suma mocy kanałów). Nadwyżka = treść kasująca się w przeciwfazie."""
    if data.shape[1] < 2:
        return 0.0
    stereo = integrated_lufs(data, fs)
    mono = integrated_lufs(data.mean(axis=1, keepdims=True), fs)
    return (stereo - mono) - 3.01


def narrow_sides(data: np.ndarray, fs: int, target_excess_lu: float,
                 min_side_gain: float = 0.0) -> tuple[np.ndarray, float, float, float]:
    """Zwęża składową boczną (S) tak, aby sample przetrwał zejście do mono.

    L = M + S, R = M - S. Przyciszenie S nie rusza treści wspólnej (M), więc
    w stereo zmienia się tylko szerokość obrazu, a w mono przestaje znikać
    energia. Szukamy NAJWIĘKSZEJ szerokości spełniającej próg — czyli
    ingerujemy tak mało, jak się da.
    """
    before = mono_excess_lu(data, fs)
    if data.shape[1] < 2 or before <= target_excess_lu:
        return data, 1.0, before, before

    mid = data.mean(axis=1)
    side = (data[:, 0] - data[:, 1]) / 2.0

    def rebuild(g: float) -> np.ndarray:
        return np.stack([mid + g * side, mid - g * side], axis=1)

    lo, hi = min_side_gain, 1.0
    if mono_excess_lu(rebuild(lo), fs) > target_excess_lu:
        best = lo
    else:
        for _ in range(18):
            gmid = (lo + hi) / 2.0
            if mono_excess_lu(rebuild(gmid), fs) > target_excess_lu:
                hi = gmid
            else:
                lo = gmid
        best = lo
    fixed = rebuild(best)
    return fixed, best, before, mono_excess_lu(fixed, fs)


def frame_rms_db(mono: np.ndarray, fs: int, frame_ms: float = 10.0) -> np.ndarray:
    """Obwiednia RMS w dB — DOKŁADNIE jak `audit_samples_full.frame_rms_db`.

    Musi być identyczna, bo `long_trail_silence` jest flagą audytu. Jeśli trym
    szuka ciszy inaczej niż audyt, ogona z niskopoziomowym szumem nie da się ściąć:
    zmierzone na 461 — ostatnia próbka nad −45 dB wypadała na 3,332 s, a ostatnia
    ramka nad −45 dB na 2,280 s, czyli 1,05 s szumu, którego trym po szczycie
    nie uznawał za ciszę, więc flaga zostawała mimo `--trim-trail-s`.
    """
    n = max(1, int(fs * frame_ms / 1000.0))
    usable = len(mono) - (len(mono) % n)
    if usable <= 0:
        rms_all = float(np.sqrt(np.mean(mono ** 2))) if mono.size else 0.0
        return np.array([20.0 * np.log10(max(rms_all, 1e-12))])
    frames = mono[:usable].reshape(-1, n)
    rms = np.sqrt(np.mean(frames ** 2, axis=1))
    return 20.0 * np.log10(np.maximum(rms, 1e-12))


def trim_trailing_silence(data: np.ndarray, fs: int, keep_s: float,
                          floor_db: float = -45.0, fade_ms: float = 40.0) -> tuple[np.ndarray, float]:
    """Odcina martwą ciszę z końca pliku, zostawiając `keep_s` ogona + krótki fade.

    Powód: audyt flaguje `long_trail_silence` (> 1,5 s ciszy), a w grze martwy
    ogon brzmi jak zacięcie. Nie ruszamy ciszy wstępnej — nią zajmuje się
    `refine_corpus_audio.py`.

    Ciszy szukamy po RMS ramki 10 ms, czyli TAK SAMO jak audyt liczy
    `trail_silence_s` (`frame_rms_db(data.mean(axis=1), fs, 10.0) > SILENCE_DB`).
    Wcześniejsza wersja szukała po szczycie próbki (`np.abs(data).max(axis=1)`),
    który jest znacznie czulszy — pojedyncza próbka nad progiem wystarczała, żeby
    uznać miejsce za dźwięk.
    """
    mono = data.mean(axis=1)
    frames = frame_rms_db(mono, fs, 10.0)
    idx = np.flatnonzero(frames > floor_db)
    if not len(idx):
        return data, 0.0
    n_frame = max(1, int(fs * 10.0 / 1000.0))
    cut = min(len(mono), int((idx[-1] + 1) * n_frame) + int(fs * keep_s))
    if cut >= len(mono):
        return data, 0.0
    out = data[:cut].copy()
    n_fade = min(len(out), int(fs * fade_ms / 1000.0))
    if n_fade:
        out[-n_fade:] *= np.linspace(1.0, 0.0, n_fade)[:, None]
    return out, round((len(mono) - cut) / fs, 3)


def trim_leading_silence(data: np.ndarray, fs: int, keep_s: float,
                         floor_db: float = -45.0, fade_ms: float = 20.0) -> tuple[np.ndarray, float]:
    """Odcina martwą ciszę z początku pliku, zostawiając `keep_s` + krótki fade-in.

    Symetria do `trim_trailing_silence`: audyt flaguje `long_lead_silence`
    (> 0,6 s), a w grze pół sekundy ciszy przed dźwiękiem brzmi jak opóźnienie.
    """
    thr = db_to_lin(floor_db)
    mono = np.abs(data).max(axis=1)
    idx = np.flatnonzero(mono > thr)
    if not len(idx):
        return data, 0.0
    cut = max(0, int(idx[0]) - int(fs * keep_s))
    if cut <= 0:
        return data, 0.0
    out = data[cut:].copy()
    n_fade = min(len(out), int(fs * fade_ms / 1000.0))
    if n_fade:
        out[:n_fade] *= np.linspace(0.0, 1.0, n_fade)[:, None]
    return out, round(cut / fs, 3)


def edge_fades(data: np.ndarray, fs: int, ms: float) -> np.ndarray:
    """Krótkie fade-in/out na krawędziach — audyt flaguje `cut_start_hard`/`cut_end_hard`."""
    if ms <= 0 or not len(data):
        return data
    n = min(len(data), int(fs * ms / 1000.0))
    if not n:
        return data
    out = data.copy()
    out[:n] *= np.linspace(0.0, 1.0, n)[:, None]
    out[-n:] *= np.linspace(1.0, 0.0, n)[:, None]
    return out


def process_one(path: Path, out_path: Path, *, target_lufs: float, ceiling_db: float,
                max_gain_db: float, hp_hz: float, dry_run: bool,
                encoder_headroom_db: float = 0.7, max_limiter_gr_db: float = 2.0,
                makeup_tol_lu: float = 0.5, makeup_iters: int = 4,
                max_makeup_db: float = 4.0, max_peak_gr_db: float = 12.0,
                fix_mono: bool = False, mono_target_excess_lu: float = 1.0,
                fix_spectral: bool = False,
                spectral_kinds: tuple[str, ...] = ("boomy", "dull", "harsh"),
                boomy_ids: set[str] | None = None,
                dull_ids: set[str] | None = None,
                harsh_ids: set[str] | None = None,
                trim_trail_s: float = 0.0, trim_lead_s: float = 0.0,
                edge_fade_ms: float = 0.0) -> dict:
    data, fs = sf.read(str(path), always_2d=True)
    lufs_before = integrated_lufs(data, fs)
    tp_before = true_peak_dbtp(data, fs)
    dc_before = float(np.mean(data))

    side_gain, mono_excess_before, mono_excess_after = 1.0, mono_excess_lu(data, fs), None
    if fix_mono:
        data, side_gain, mono_excess_before, mono_excess_after = narrow_sides(
            data, fs, mono_target_excess_lu)

    if fix_spectral:
        sid = path.stem
        if boomy_ids and sid in boomy_ids and "boomy" in spectral_kinds:
            data = biquad_low_shelf(data, fs, fc=180.0, gain_db=-3.0)
        if dull_ids and sid in dull_ids and "dull" in spectral_kinds:
            data = biquad_high_shelf(data, fs, fc=3500.0, gain_db=3.5)
        if harsh_ids and sid in harsh_ids and "harsh" in spectral_kinds:
            data = biquad_peaking(data, fs, fc=4500.0, gain_db=-3.5, q=1.2)

    trim_removed_s = 0.0
    lead_removed_s = 0.0
    if trim_trail_s > 0.0:
        data, trim_removed_s = trim_trailing_silence(data, fs, trim_trail_s)
    if trim_lead_s > 0.0:
        data, lead_removed_s = trim_leading_silence(data, fs, trim_lead_s)
    if edge_fade_ms > 0.0:
        data = edge_fades(data, fs, edge_fade_ms)

    filtered = highpass(data, fs, hp_hz)
    lufs_filtered = integrated_lufs(filtered, fs)

    raw_gain = target_lufs - lufs_filtered
    # Koder MP3 potrafi podnieść true peak o ~1 dB, więc limitujemy z zapasem
    # i i tak weryfikujemy wynik na zapisanym pliku.
    processed, gain_db, limiter_gr, limiter_gr_mean, _lufs_pre = gain_and_limit(
        filtered, fs, gain_db=raw_gain, ceiling_db=ceiling_db - encoder_headroom_db,
        target_lufs=target_lufs, max_total_gain_db=max_gain_db,
        max_limiter_gr_db=max_limiter_gr_db, tol_lu=makeup_tol_lu, iters=makeup_iters)
    gained = filtered * db_to_lin(gain_db)

    result = {
        "id": path.stem,
        "hp_hz": hp_hz,
        "trim_removed_s": trim_removed_s,
        "lead_removed_s": lead_removed_s,
        "lufs_before": lufs_before,
        "lufs_after_hp": lufs_filtered,
        "gain_db": round(gain_db, 2),
        "gain_wanted_db": round(raw_gain, 2),
        "gain_capped": bool(raw_gain > max_gain_db + 1e-9),
        "makeup_db": round(gain_db - min(raw_gain, max_gain_db), 2),
        "limiter_gr_db": limiter_gr,
        "limiter_gr_mean_db": limiter_gr_mean,
        "true_peak_before": tp_before,
        "dc_before": round(dc_before, 5),
        "side_gain": round(side_gain, 4),
        "side_gain_db": (round(20.0 * math.log10(max(side_gain, 1e-6)), 2)
                         if side_gain < 1.0 else 0.0),
        "mono_excess_before_lu": round(mono_excess_before, 2),
        "mono_excess_after_lu": (round(mono_excess_after, 2)
                                 if mono_excess_after is not None else None),
    }
    if dry_run:
        result["lufs_after"] = integrated_lufs(processed, fs)
        result["true_peak_after"] = true_peak_dbtp(processed, fs)
        return result

    bytes_before = path.stat().st_size
    tmp = out_path.with_suffix(".tmp.mp3")
    headroom = encoder_headroom_db
    attempts = 0
    while True:
        attempts += 1
        sf.write(str(tmp), processed, fs, format="MP3", subtype="MPEG_LAYER_III",
                 bitrate_mode="VARIABLE", compression_level=0.0)
        written, fs2 = sf.read(str(tmp), always_2d=True)
        tp_written = true_peak_dbtp(written, fs2)
        if tp_written <= ceiling_db + 0.02 or attempts >= 3:
            break
        # zapisany plik przekroczył sufit — powtarzamy z większym zapasem
        headroom += (tp_written - ceiling_db) + 0.15
        processed, limiter_gr, limiter_gr_mean = limit_true_peak(gained, fs, ceiling_db - headroom)
    os.replace(tmp, out_path)

    result.update({
        "encode_attempts": attempts,
        "encoder_headroom_db": round(headroom, 2),
        "limiter_gr_db": limiter_gr,
        "limiter_gr_mean_db": limiter_gr_mean,
        "lufs_after": integrated_lufs(written, fs2),
        "true_peak_after": true_peak_dbtp(written, fs2),
        "dc_after": round(float(np.mean(written)), 5),
        "transcode_snr_db": transcode_snr(processed, written),
        "bytes_before": bytes_before,
        "bytes_after": out_path.stat().st_size,
    })
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--samples-dir", default="audio/samples")
    ap.add_argument("--out-dir", default="", help="pusty = zapis w miejscu")
    ap.add_argument("--audit", default="data/samples/audio-audit-latest.json",
                    help="JSON audytu — z niego bierzemy listę plików sub_dominant i odchyleń widmowych")
    ap.add_argument("--target-lufs", type=float, default=-20.0)
    ap.add_argument("--ceiling-dbtp", type=float, default=-1.0)
    ap.add_argument("--max-gain-db", type=float, default=15.0)
    ap.add_argument("--encoder-headroom", type=float, default=0.7,
                    help="zapas pod overshoot kodera MP3 (dB)")
    ap.add_argument("--max-limiter-gr", type=float, default=2.0,
                    help="budżet ŚREDNIEJ redukcji limitera przy domierzaniu głośności (dB)")
    ap.add_argument("--max-makeup", type=float, default=4.0,
                    help="ile dB wolno dołożyć ponad wzmocnienie wyliczone z LUFS")
    ap.add_argument("--max-peak-gr", type=float, default=12.0,
                    help="górna granica szczytowej redukcji limitera (dB) — chroni atak")
    ap.add_argument("--makeup-tol", type=float, default=0.5,
                    help="tolerancja odchyłki od celu LUFS po limitowaniu (LU)")
    ap.add_argument("--makeup-iters", type=int, default=4)
    ap.add_argument("--hp-default", type=float, default=25.0)
    ap.add_argument("--hp-sub", type=float, default=45.0)
    ap.add_argument("--ids", default="", help="opcjonalna lista ID po przecinku")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--report", default="")
    ap.add_argument("--trim-lead-s", type=float, default=0.0,
                    help="ile sekund wstępu zostawić po odcięciu martwej ciszy (0 = wyłącz)")
    ap.add_argument("--edge-fade-ms", type=float, default=0.0,
                    help="długość fade-in/out na krawędziach (cut_start_hard/cut_end_hard)")
    ap.add_argument("--spectral-kinds", default="boomy,dull,harsh",
                    help="które korekty spektralne stosować przy --fix-spectral")
    ap.add_argument("--trim-trail-s", type=float, default=0.0,
                    help="ile sekund ogona zostawić po odcięciu martwej ciszy (0 = wyłącz)")
    ap.add_argument("--fix-mono", action="store_true",
                    help="zwęź składową boczną tam, gdzie sample traci energię w mono")
    ap.add_argument("--mono-target-excess", type=float, default=1.0,
                    help="dopuszczalna nadwyżka straty w mono ponad bazowe 3,01 LU")
    ap.add_argument("--fix-spectral", action="store_true",
                    help="łagodne profilowanie skrajnych odchyleń widmowych (boomy, dull, harsh)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    sub_dominant: set[str] = set()
    boomy_ids: set[str] = set()
    dull_ids: set[str] = set()
    harsh_ids: set[str] = set()

    audit_path = Path(args.audit)
    if not audit_path.exists():
        found = sorted((ROOT / "data/samples").glob("audio-audit-*.json"))
        if found:
            audit_path = found[-1]

    if audit_path.exists():
        audit = json.loads(audit_path.read_text(encoding="utf-8"))
        for r in audit.get("files", []):
            sid = str(r.get("id"))
            flags = r.get("flags", [])
            if "sub_dominant" in flags:
                sub_dominant.add(sid)
            if "boomy" in flags:
                boomy_ids.add(sid)
            if "dull" in flags:
                dull_ids.add(sid)
            if "harsh" in flags:
                harsh_ids.add(sid)

    src_dir = Path(args.samples_dir)
    out_dir = Path(args.out_dir) if args.out_dir else src_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    files = sorted(src_dir.glob("*.mp3"), key=lambda p: int(p.stem) if p.stem.isdigit() else 10**9)
    if args.ids:
        wanted = {i.strip() for i in args.ids.split(",") if i.strip()}
        files = [f for f in files if f.stem in wanted]
    if args.limit:
        files = files[: args.limit]

    rows: list[dict] = []
    for n, path in enumerate(files, 1):
        hp = args.hp_sub if path.stem in sub_dominant else args.hp_default
        try:
            rows.append(process_one(path, out_dir / path.name,
                                    target_lufs=args.target_lufs,
                                    ceiling_db=args.ceiling_dbtp,
                                    max_gain_db=args.max_gain_db,
                                    hp_hz=hp, dry_run=args.dry_run,
                                    encoder_headroom_db=args.encoder_headroom,
                                    max_limiter_gr_db=args.max_limiter_gr,
                                    makeup_tol_lu=args.makeup_tol,
                                    makeup_iters=args.makeup_iters,
                                    max_makeup_db=args.max_makeup,
                                    max_peak_gr_db=args.max_peak_gr,
                                    fix_mono=args.fix_mono,
                                    trim_trail_s=args.trim_trail_s,
                                    trim_lead_s=args.trim_lead_s,
                                    edge_fade_ms=args.edge_fade_ms,
                                    spectral_kinds=tuple(
                                        k.strip() for k in args.spectral_kinds.split(",") if k.strip()),
                                    mono_target_excess_lu=args.mono_target_excess,
                                    fix_spectral=args.fix_spectral,
                                    boomy_ids=boomy_ids,
                                    dull_ids=dull_ids,
                                    harsh_ids=harsh_ids))
        except Exception as exc:  # noqa: BLE001
            rows.append({"id": path.stem, "error": str(exc)})
        if n % 50 == 0:
            print(f"  … {n}/{len(files)}", flush=True)

    ok = [r for r in rows if "error" not in r]
    after = np.array([r["lufs_after"] for r in ok]) if ok else np.zeros(1)
    tp_after = np.array([r.get("true_peak_after", -99) for r in ok]) if ok else np.zeros(1)
    snr = np.array([r["transcode_snr_db"] for r in ok if "transcode_snr_db" in r])
    summary = {
        "files": len(ok),
        "errors": len(rows) - len(ok),
        "target_lufs": args.target_lufs,
        "ceiling_dbtp": args.ceiling_dbtp,
        "max_gain_db": args.max_gain_db,
        "dry_run": args.dry_run,
        "lufs_after_median": round(float(np.median(after)), 2),
        "lufs_after_min": round(float(np.min(after)), 2),
        "lufs_after_max": round(float(np.max(after)), 2),
        "lufs_after_std": round(float(np.std(after)), 2),
        "true_peak_after_max": round(float(np.max(tp_after)), 2),
        "gain_capped_count": sum(1 for r in ok if r.get("gain_capped")),
        "limited_count": sum(1 for r in ok if r.get("limiter_gr_db", 0.0) < -0.01),
        "over_ceiling_after_encode": sum(1 for r in ok
                                         if r.get("true_peak_after", -99) > args.ceiling_dbtp + 0.02),
        "reencoded_count": sum(1 for r in ok if r.get("encode_attempts", 1) > 1),
        "transcode_snr_median_db": round(float(np.median(snr)), 1) if snr.size else None,
        "transcode_snr_min_db": round(float(np.min(snr)), 1) if snr.size else None,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=1))

    if args.report:
        out = Path(args.report)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps({"summary": summary, "files": rows},
                                  ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"raport: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
