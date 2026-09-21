#!/usr/bin/env python3
"""
fetch_stems.py - Pobiera bazowe próbki foley CC0 / Public Domain z repozytoriów
otwartych (Wikimedia, US National Park Service, Gravity Sound).
Zapewnia bazę dźwiękową dla silnika audio_engine.py.
"""

import os
import time
import urllib.request
import json
import subprocess

STEMS_DIR = os.path.join(os.path.dirname(__file__), "stems")
os.makedirs(STEMS_DIR, exist_ok=True)

HEADERS = {
    "User-Agent": "GameAudioOrchestrator/2.0 (contact: gamedev@example.org)"
}

# Mapa kluczowych próbek CC0 / Public Domain
STEM_SOURCES = {
    # 1. Broń i walka
    "sword_draw.mp3": "https://upload.wikimedia.org/wikipedia/commons/9/9b/Sword_12_%28Gravity_Sound%29.mp3",
    "sword_swipe.mp3": "https://upload.wikimedia.org/wikipedia/commons/1/19/Sword_Swipe_%28Gravity_Sound%29.mp3",
    # 2. Ruch i fizyka (Foley)
    "whoosh_flap.mp3": "https://upload.wikimedia.org/wikipedia/commons/2/23/Swipe_%28Gravity_Sound%29.mp3",
    "gravel_feet.mp3": "https://upload.wikimedia.org/wikipedia/commons/c/c8/Feet_shuffling_in_gravel_%28Gravity_Sound%29.mp3",
    "impact_smack.mp3": "https://upload.wikimedia.org/wikipedia/commons/6/6a/Smack_%28Gravity_Sound%29.mp3",
    # 3. Woda
    "water_splash.ogg": "https://upload.wikimedia.org/wikipedia/commons/8/83/Bathtub_water_splashes.ogg",
    # 4. Zwierzęta i potwory (Yellowstone NPS / US Govt Public Domain)
    "raven_call.mp3": "https://upload.wikimedia.org/wikipedia/commons/9/9c/Yellowstone_sound_library_-_Common_Raven_-_001.mp3",
    "bear_growl.mp3": "https://upload.wikimedia.org/wikipedia/commons/3/30/Yellowstone_sound_library_-_Grizzly_Bears_Roar_-_001.mp3",
    "alligator_bellow.ogg": "https://upload.wikimedia.org/wikipedia/commons/d/d4/Alligatorbellowedit.ogg"
}

def download_file(url, target_path):
    if os.path.exists(target_path) and os.path.getsize(target_path) > 1000:
        print(f"[OK] Istnieje: {os.path.basename(target_path)}")
        return True
    
    print(f"[POBIERANIE] {os.path.basename(target_path)}...")
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req) as resp, open(target_path, "wb") as f:
            f.write(resp.read())
        print(f"[ZAPISANO] {os.path.basename(target_path)}")
        time.sleep(1.0) # Szacunek dla serwerów
        return True
    except Exception as e:
        print(f"[BŁĄD] Nie udało się pobrać {url}: {e}")
        return False

def main():
    print("=== POBIERANIE BAZOWYCH PRÓBEK FOLEY CC0 ===")
    for filename, url in STEM_SOURCES.items():
        target = os.path.join(STEMS_DIR, filename)
        download_file(url, target)
    print("\nKompletowanie próbek zakończone!")

if __name__ == "__main__":
    main()
