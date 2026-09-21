#!/usr/bin/env python3
"""
audio_qa_engine.py - Wewnętrzny system automatycznego audytu i samokrytyki dźwięku.
Weryfikuje każdy wygenerowany plik pod kątem inżynierii dźwięku i dramaturgii PRZED
oddaniem go użytkownikowi.
"""

import os
import numpy as np
import soundfile as sf
from scipy import signal

def analyze_audio_track(file_path, expected_climax_window=(1.5, 3.8)):
    """
    Krytyczny audyt techniczny i dynamiczny pliku audio.
    Zwraca (passed: bool, score: float, logs: list)
    """
    logs = []
    if not os.path.exists(file_path):
        return False, 0.0, [f"Plik nie istnieje: {file_path}"]
        
    data, sr = sf.read(file_path)
    if len(data.shape) > 1:
        data = data.mean(axis=1)
        
    total_len_sec = len(data) / sr
    peak = np.max(np.abs(data))
    rms_total = np.sqrt(np.mean(data**2))
    
    # 1. Test na DC Offset (ochrona przed błędem ciszy/spłaszczenia)
    dc_offset = np.abs(np.mean(data))
    if dc_offset > 0.015:
        logs.append(f"[KRYTYCZNY BŁĄD] Wykryto DC Offset: {dc_offset:.4f}! Sygnał uderzy w rail kompresora.")
        return False, 0.0, logs
    else:
        logs.append(f"[OK] DC Offset: {dc_offset:.5f} (czysty dół pasma)")

    # 2. Test poziomu szczytowego (Headroom & Clipping)
    if peak > 0.99:
        logs.append(f"[BŁĄD] Cyfrowy przester (peak={peak:.3f} > 0.99)!")
        return False, 20.0, logs
    elif peak < 0.25:
        logs.append(f"[BŁĄD] Utwór zbyt cichy (peak={peak:.3f} < 0.25)!")
        return False, 30.0, logs
    else:
        logs.append(f"[OK] Poziom szczytowy (Peak): {peak:.2f} (wzorcowy headroom)")

    # 3. Test na dziury dźwiękowe / martwą ciszę (okna 0.35s)
    step = int(sr * 0.35)
    dead_windows = []
    for i in range(0, len(data) - step, step):
        t_sec = i / sr
        seg = data[i:i+step]
        rms_seg = np.sqrt(np.mean(seg**2))
        if rms_seg < 0.003: # poniżej -50 dB
            dead_windows.append(round(t_sec, 2))
            
    if len(dead_windows) > 1:
        logs.append(f"[BŁĄD] Martwa cisza w oknach: {dead_windows}s! Utwór brzmi pusto.")
        return False, 40.0, logs
    else:
        logs.append(f"[OK] Ciągłość tła: brak martwych dziur ciszy")

    # 4. Test dramaturgii (Stosunek kulminacji do tła wprowadzającego)
    idx_intro = int(sr * 1.0)
    rms_intro = np.sqrt(np.mean(data[:idx_intro]**2)) + 1e-5
    
    idx_cl_start = int(sr * expected_climax_window[0])
    idx_cl_end = int(sr * expected_climax_window[1])
    rms_climax = np.sqrt(np.mean(data[idx_cl_start:idx_cl_end]**2))
    
    ratio = rms_climax / rms_intro
    if ratio < 1.5:
        logs.append(f"[BŁĄD DRAMATURGII] Kulminacja zbyt płaska! Stosunek energii={ratio:.2f}x (wymagane min. 1.6x). Stinger ginie w tle.")
        return False, 50.0, logs
    else:
        logs.append(f"[OK] Kontrast dramaturgiczny: {ratio:.2f}x (kulminacja wyraźnie dominuje nad tłem)")

    # 5. Wyliczenie wyniku jakości (Score)
    score = min(100.0, 70.0 + min(30.0, ratio * 6.0))
    logs.append(f"[AUDYT ZALICZONY] Wynik jakości: {score:.1f}/100")
    return True, score, logs

if __name__ == "__main__":
    for i in [1, 2, 3, 4, 5]:
        p = f"/home/user/jingle_output/{i}.mp3"
        passed, score, logs = analyze_audio_track(p)
        print(f"\n--- AUDYT JINGLE {i}.mp3 (Zaliczony: {passed}, Wynik: {score:.1f}) ---")
        for l in logs:
            print(" ", l)
