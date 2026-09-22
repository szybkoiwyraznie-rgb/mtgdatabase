"""
Game Event Sound Vignette Generator (Text-to-Audio Orchestration)
================================================================
Ten skrypt demonstruje dwa podejścia do generowania 3-6s efektów fabularnych:
1. Pipeline A (Offline/Kompozycyjny): Programistyczne miksowanie warstw foley/ambient z DSP i FFmpeg.
2. Pipeline B (AI API): Zapytanie do Text-to-Sound-Effects (np. ElevenLabs SFX API) z translacją lore -> prompt akustyczny.
"""

import os
import json
import urllib.request

# -------------------------------------------------------------------------
# 1. ARCHITEKTURA PROMPT-ENGINEERINGU DLA MODELI SFX
# -------------------------------------------------------------------------
# Modele generatywne (ElevenLabs SFX, Stable Audio, AudioCraft) NIE rozumieją
# poetyckiego opisu świata (np. "zwiadowcy Sarumana", "hełm z koralu").
# Rola Orchestratora to przetłumaczenie fabuły na warstwy czysto akustyczne.

EVENT_PROMPTS = {
    "dunland_cliff": {
        "lore": "Uruk-hai na urwisku, armia Sarumana w wąwozie, pochodnie, pikujący kruk crebain, sygnał ostrza.",
        "duration_seconds": 5.0,
        "sfx_prompt": (
            "cinematic dark fantasy trailer sound cue, ominous mountain canyon wind ambiance, "
            "deep 45Hz sub drone tension, sudden torch fire whoosh igniting, "
            "piercing crow screech caw echoing across rocky ravine, "
            "sharp metallic sword unsheathe scrape, hyper-realistic, dark atmospheric game audio"
        )
    },
    "zendikar_canyon": {
        "lore": "Merfolk z Coralhelm i potężny Baloth w zalanym kanionie, wiszące skały, patrole Eldrazi powyżej.",
        "duration_seconds": 5.0,
        "sfx_prompt": (
            "flooded rocky cave canyon foley, eerie otherworldly dissonant humming drone overhead, "
            "massive heavy fantasy beast footsteps stomping violently through deep water, "
            "huge wet water splashes sloshing, low guttural creature breathing, "
            "subtle coral shell clink, wet cave echo"
        )
    }
}

# -------------------------------------------------------------------------
# 2. GENEROWANIE PRZEZ ELEVENLABS SOUND EFFECTS API (opcjonalne, gdy podany klucz)
# -------------------------------------------------------------------------
def generate_via_elevenlabs(prompt: str, duration_sec: float, output_path: str, api_key: str):
    """
    Wywołuje oficjalne Text-to-Sound-Effects API z ElevenLabs:
    POST https://api.elevenlabs.io/v1/sound-generation
    """
    url = "https://api.elevenlabs.io/v1/sound-generation"
    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json"
    }
    payload = {
        "text": prompt,
        "duration_seconds": duration_sec,
        "prompt_influence": 0.35
    }
    req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers=headers)
    with urllib.request.urlopen(req) as resp:
        audio_data = resp.read()
    with open(output_path, "wb") as f:
        f.write(audio_data)
    print(f"[ElevenLabs API] Wygenerowano plik: {output_path}")

if __name__ == "__main__":
    print("Dostępne szablony zdarzeń fabularnych:")
    for k, v in EVENT_PROMPTS.items():
        print(f"\n--- {k.upper()} ---")
        print(f"Lore: {v['lore']}")
        print(f"Acoustic Prompt: {v['sfx_prompt']}")
        print(f"Długość: {v['duration_seconds']}s")
