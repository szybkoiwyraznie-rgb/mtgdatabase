#!/usr/bin/env python3
"""
audio_engine.py - Deterministyczny silnik renderowania fabularnych jingli audio (3-6s).
Łączy proceduralne tła ambientowe z realnymi próbkami foley CC0 na podstawie
scenariusza JSON (Sound Recipe).
"""

import os
import json
import shutil
import subprocess
import numpy as np
import soundfile as sf
from scipy import signal

SR = 44100
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STEMS_DIR = os.path.join(BASE_DIR, "stems")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Znalezienie ffmpeg
FFMPEG_BIN = shutil.which("ffmpeg") or "/tmp/bin/ffmpeg" or "/home/user/bin/ffmpeg"

def load_stem(stem_name, target_sr=SR):
    path = os.path.join(STEMS_DIR, stem_name)
    if not os.path.exists(path):
        # Sprawdzenie alternatywnych rozszerzeń
        base = os.path.splitext(path)[0]
        for ext in [".mp3", ".ogg", ".wav"]:
            if os.path.exists(base + ext):
                path = base + ext
                break
    if not os.path.exists(path):
        print(f"[OSTRZEŻENIE] Brak próbki: {stem_name}")
        return np.zeros(int(target_sr * 0.5))
    
    data, orig_sr = sf.read(path)
    if len(data.shape) > 1:
        data = data.mean(axis=1)
    if orig_sr != target_sr:
        new_len = int(len(data) * target_sr / orig_sr)
        data = signal.resample(data, new_len)
    return data

def generate_ambiance(amb_type, duration_sec, sr=SR):
    samples = int(sr * duration_sec)
    t = np.linspace(0, duration_sec, samples, endpoint=False)
    L = np.zeros(samples)
    R = np.zeros(samples)
    
    if amb_type == "mountain_wind":
        raw = np.cumsum(np.random.normal(0, 1, samples))
        b, a = signal.butter(2, 380 / (sr/2), btype='low')
        wind = signal.lfilter(b, a, raw)
        wind = wind / np.max(np.abs(wind)) * 0.35 * (np.sin(np.pi * t / duration_sec) ** 0.5)
        L = wind * 0.8
        R = wind * 1.1
    elif amb_type == "cave_flooded":
        raw = np.cumsum(np.random.normal(0, 1, samples))
        b, a = signal.butter(2, [70 / (sr/2), 500 / (sr/2)], btype='band')
        water = signal.lfilter(b, a, raw)
        water = water / np.max(np.abs(water)) * 0.25
        L = water * 0.75
        R = water * 0.85
    elif amb_type == "forest_night":
        raw = np.random.normal(0, 1, samples)
        b, a = signal.butter(2, [400 / (sr/2), 2500 / (sr/2)], btype='band')
        breeze = signal.lfilter(b, a, raw) * 0.15
        L = breeze * 0.9
        R = breeze * 1.0
    return L, R

def generate_drone(drone_type, freq, duration_sec, sr=SR):
    samples = int(sr * duration_sec)
    t = np.linspace(0, duration_sec, samples, endpoint=False)
    if drone_type == "cinematic_sub":
        sub = 0.5 * np.sin(2 * np.pi * freq * t) + 0.25 * np.sin(2 * np.pi * (freq * 1.5) * t)
        env = np.clip(t / 2.0, 0.2, 1.0)
        env[-int(sr*0.8):] *= np.linspace(1.0, 0.0, int(sr*0.8))
        return np.tanh(sub * env * 1.5) * 0.45
    elif drone_type == "eldrazi_alien":
        drone = (0.35 * np.sin(2 * np.pi * freq * t) +
                 0.25 * np.sin(2 * np.pi * (freq * 1.414) * t) +
                 0.18 * np.sin(2 * np.pi * (freq * 2.828) * t + 0.6 * np.sin(2 * np.pi * 3.2 * t)))
        env = 0.35 + 0.45 * (1 - np.cos(np.pi * t / duration_sec))
        return drone * env * 0.35
    return np.zeros(samples)

def render_recipe(recipe):
    recipe_id = recipe.get("id", "event_render")
    dur = recipe.get("duration_sec", 5.5)
    total_samples = int(SR * dur)
    t = np.linspace(0, dur, total_samples, endpoint=False)
    
    L_master = np.zeros(total_samples)
    R_master = np.zeros(total_samples)
    
    # 1. Tło Ambiance
    amb_cfg = recipe.get("ambiance", {})
    amb_type = amb_cfg.get("type", "mountain_wind")
    amb_vol = amb_cfg.get("volume", 1.0)
    amb_L, amb_R = generate_ambiance(amb_type, dur, SR)
    
    # 2. Dron sub-basowy / tonalny
    drone_cfg = recipe.get("drone", {})
    drone_type = drone_cfg.get("type", "none")
    drone_freq = drone_cfg.get("freq", 45.0)
    drone_vol = drone_cfg.get("volume", 1.0)
    drone_sig = generate_drone(drone_type, drone_freq, dur, SR) * drone_vol
    
    amb_L += drone_sig * 0.9
    amb_R += drone_sig * 1.0
    
    # Maska duckingu dla tła
    duck_mask = np.ones(total_samples)
    
    # 3. Zdarzenia Foley
    events = recipe.get("foley_events", [])
    for ev in events:
        stem_name = ev.get("stem")
        start_t = ev.get("time_sec", 1.0)
        vol = ev.get("volume", 1.0)
        pan = ev.get("pan", 0.0) # -1.0 lewo, +1.0 prawo
        pitch = ev.get("pitch_factor", 1.0) # >1.0 wyżej, <1.0 niżej
        duck = ev.get("duck_ambiance", 0.0) # od 0.0 do 0.7
        echo_send = ev.get("echo_send", 0.0)
        
        # Generator wbudowanych procedur dla złożonych zdarzeń
        if stem_name == "beast_step_water":
            smack = load_stem("impact_smack.mp3")[:int(SR*0.25)]
            splash = load_stem("water_splash.ogg")[int(SR*25.0):int(SR*26.3)]
            idx = int(start_t * SR)
            if idx < total_samples:
                l_s = min(len(smack), total_samples - idx)
                L_master[idx:idx+l_s] += (smack[:l_s] / (np.max(np.abs(smack))+1e-4)) * (0.8 - pan*0.2) * 0.65 * vol
                R_master[idx:idx+l_s] += (smack[:l_s] / (np.max(np.abs(smack))+1e-4)) * (0.8 + pan*0.2) * 0.65 * vol
                
                idx_sp = idx + int(SR * 0.035)
                if idx_sp < total_samples:
                    l_sp = min(len(splash), total_samples - idx_sp)
                    L_master[idx_sp:idx_sp+l_sp] += (splash[:l_sp] / (np.max(np.abs(splash))+1e-4)) * (0.9 - pan*0.25) * 0.95 * vol
                    R_master[idx_sp:idx_sp+l_sp] += (splash[:l_sp] / (np.max(np.abs(splash))+1e-4)) * (0.9 + pan*0.25) * 0.95 * vol
            continue
            
        elif stem_name == "beast_roar":
            grizz = load_stem("bear_growl.mp3")[int(SR*2.15):int(SR*3.75)]
            alli = load_stem("alligator_bellow.ogg")[int(SR*14.0):int(SR*15.6)]
            # High-pass i presence boost
            b_hp, a_hp = signal.butter(2, 120 / (SR/2), btype='high')
            g_clean = signal.lfilter(b_hp, a_hp, grizz)
            b_bp, a_bp = signal.butter(2, [1000 / (SR/2), 3500 / (SR/2)], btype='band')
            g_pres = signal.lfilter(b_bp, a_bp, g_clean)
            
            target_len = int(len(g_clean) * 1.22)
            g_low = signal.resample(g_clean, target_len)
            g_mid = signal.resample(g_clean, target_len)
            g_p_str = signal.resample(g_pres, target_len)
            a_str = signal.resample(alli, target_len)
            
            roar_comp = (g_low*0.7 + g_mid*0.8 + g_p_str*0.6)
            roar = roar_comp / (np.max(np.abs(roar_comp))+1e-4) * 0.75 + (a_str / (np.max(np.abs(a_str))+1e-4)) * 0.45
            roar = np.tanh(roar * 2.2)
            raw_audio = roar / (np.max(np.abs(roar))+1e-4)
        else:
            raw_audio = load_stem(stem_name)
            if stem_name == "raven_call.mp3":
                # Wycięcie czystego krakania kruka
                raw_audio = raw_audio[int(SR*7.75):int(SR*9.2)]
            elif stem_name == "whoosh_flap.mp3":
                raw_audio = raw_audio[:int(SR*0.55)]
                
            if pitch != 1.0:
                raw_audio = signal.resample(raw_audio, int(len(raw_audio) * (1.0 / pitch)))
            raw_audio = raw_audio / (np.max(np.abs(raw_audio)) + 1e-4)

        start_idx = int(start_t * SR)
        seg_len = min(len(raw_audio), total_samples - start_idx)
        if start_idx < total_samples and seg_len > 0:
            clip = raw_audio[:seg_len] * vol
            L_master[start_idx:start_idx+seg_len] += clip * (1.0 - max(0.0, pan))
            R_master[start_idx:start_idx+seg_len] += clip * (1.0 + min(0.0, pan))
            
            # Ducking tła
            if duck > 0:
                d_end = min(total_samples, start_idx + seg_len + int(SR*0.2))
                duck_mask[start_idx:d_end] = np.minimum(duck_mask[start_idx:d_end], 1.0 - duck)
                
            # Echo send
            if echo_send > 0:
                delay = int(0.14 * SR)
                if start_idx + delay + seg_len < total_samples:
                    L_master[start_idx+delay:start_idx+delay+seg_len] += clip * echo_send * 0.5
                    R_master[start_idx+delay:start_idx+delay+seg_len] += clip * echo_send * 0.35

    # Aplikacja duckingu na tło
    L_master += amb_L * amb_vol * duck_mask
    R_master += amb_R * amb_vol * duck_mask
    
    # Master limiter & Soft clip
    mix = np.column_stack([L_master, R_master])
    mix = np.tanh(mix * 1.1) / 1.1
    mix = mix / (np.max(np.abs(mix)) + 1e-4) * 0.93
    
    raw_wav_path = os.path.join(OUTPUT_DIR, f"{recipe_id}.wav")
    final_mp3_path = os.path.join(OUTPUT_DIR, f"{recipe_id}.mp3")
    sf.write(raw_wav_path, mix, SR)
    
    # Konwersja do MP3 za pomocą ffmpeg
    if os.path.exists(FFMPEG_BIN):
        subprocess.run([
            FFMPEG_BIN, "-y", "-i", raw_wav_path,
            "-af", "acompressor=threshold=-11dB:ratio=3:attack=12:release=160",
            final_mp3_path
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        os.remove(raw_wav_path)
        print(f"[RENDER ZAKOŃCZONY] -> {final_mp3_path}")
        return final_mp3_path
    else:
        print(f"[RENDER ZAKOŃCZONY (WAV)] -> {raw_wav_path}")
        return raw_wav_path

def main():
    recipe_file = os.path.join(BASE_DIR, "recipes_sample.json")
    if not os.path.exists(recipe_file):
        print(f"Brak pliku receptur: {recipe_file}")
        return
    with open(recipe_file, "r", encoding="utf-8") as f:
        recipes = json.load(f)
    print(f"=== ROZPOCZYNAM RENDEROWANIE {len(recipes)} EFEKTÓW ===")
    for rec in recipes:
        render_recipe(rec)
    print("Wszystkie efekty wyrenderowane pomyślnie!")

if __name__ == "__main__":
    main()
