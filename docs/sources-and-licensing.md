# Źródła sampli i warsztat

Projekt jest niekomercyjny i przeznaczony do prywatnego użycia offline, ale status licencji każdego źródła musi być zapisany. Prywatność nie zastępuje warunków licencji.

Rejestr powinien zawierać co najmniej:

```text
name
url
author
license
attribution_required
allowed_for_pages_preview
allowed_for_offline_zip
checked_at
notes
```

Agent może badać nowe biblioteki i narzędzia, ale nie powinien automatycznie dołączać materiału o nieznanej licencji do paczki dystrybucyjnej. Materiał eksperymentalny można oznaczyć jako roboczy i trzymać poza publicznym buildem Pages.

Formalny rejestr istniejących sampli znajduje się w `data/sources.json`; każdy nowy sample dopisujemy tam przed użyciem w produkcji. Uwaga: edycja `alligator_bellow` jest CC BY-SA 2.5 (ShareAlike) — do nowych renderów używaj surowego oryginału FWS (PD).

## Katalog zweryfikowanych bibliotek dźwięków (osiągalnych z sandboxa Arena)

Egress sandboxa tnie TLS do Wikimedia/NPS/Freesound/raw.githubusercontent (patrz LESSONS); sprawdzonym kanałem jest **`git clone` z github.com** (najlepiej `--depth 1 --filter=blob:none --sparse` + `git sparse-checkout set <katalog>`). Poniższe repozytoria zweryfikowano 2026-09-22 (odpalone klony/API, potwierdzone pliki audio i licencje). Każdy pobrany sample i tak rejestrujemy w `data/sources.json` (AGENTS.md #8) — licencją jest status ORYGINAŁU, nie mirrora.

| Repozytorium | Zawartość | Licencja (oryginału) | Format / uwagi |
|---|---|---|---|
| `rosuH/YSL` | Mirror całej Yellowstone Sound Library: zwierzęta (wilk, niedźwiedź, kruk, łoś, kojot, orzeł…), ogień, grzmot, gejzery, woda, błotne kotły, pejzaże dźwiękowe, maszyny (skuter śnieżny, wóz konny) | Public Domain (NPS, praca rządu USA) | MP3; duże pliki ambientowe (do 25 min) — wycinać fragment; użyte dotąd: `wolf_howl.mp3`, `steam_vent.mp3`, `lava_rumble.mp3` i `campfire.mp3` (Fire 6-11,5 s / 6-9 s) |
| `novincode/atomcut-library` | ~100 packów z OpenGameArt + Kenney + Freesound: **miecze (20 SFX ataków i zderzeń), metal i drewno (100 SFX), kroki (kamień/żwir/błoto/śnieg/trawa/skóra/zbroja), magia i zaklęcia, potwory/gobliny/zombie/alieni, drzwi, woda/plusk/slime/błoto, szelest liści, pękające drewno, Sci-Fi (60+50 SFX, lasery/fazery/tarcze), bagna/ambience, głosy (wysiłek/ból/okrzyki), księgi, karty, kości, klawiatura** | CC0 1.0 (OpenGameArt/Kenney/Freesound — filtr CC0 w `sources/*.json`; brak LICENSE w korzeniu repo, licencję każdego packu potwierdzamy na stronie OGA przy pobraniu) | **M4A/AAC 48 kHz** — soundfile nie czyta: dekodować przez `pip install av` (PyAV, działa w venv) → WAV; pliki krótkie, gotowe na stemy |
| `Daarko/sparkstream-sounds` | Kenney: **impacts/whooshes (130)**, kliknięcia UI (151), digital/Sci-Fi beeps (135), RPG audio (51) | CC0 1.0 (Kenney; oryginalne teksty licencji w `credits/`) | WAV; profesjonalny sound design (nie nagrania terenowe) — idealne do impacts/whooshów i beepów SF |
| `sgossner/VCSL` | Versilian Community Sample Library — **próbki prawdziwych instrumentów** (dzwony, smyczki, dęte, perkusja, etniczne) | CC0 1.0 | Duże (~4 GB) — wyłącznie sparse-checkout wybranych instrumentów; zamiennik syntetycznych padów/dzwonków prawdziwym timbrem w scenach fantasy/mistycznych |
| `sgossner/VSCO-2-CE` | VSCO 2 Community Edition — orkiestra (nagrania sekcji, staccati, uderzenia) | CC0 1.0 | ~2,3 GB, sparse-checkout; epickie stingery/fantazyjne kulminacje |

Pomocnicze: `Cy4nWare/sfx-api` (Kenney CC0, duplikat sparkstream przez jsdelivr), `stargatedaw/stargate-sample-pack` (PD, sample instrumentów do DAW — marginalne dla jingli). Odrzucone: repozytoria „SFX generowane z kodu" (blip8, free-sfx-bgm — sprzeczne z zasadą żywych sampli), scraper BBC Sound Effects (host blokowany + licencja RemArc niekomercyjna).

Procedura pobierania: (1) potwierdź licencję packu na stronie źródłowej; (2) sparse-clone do `/tmp`; (3) wytnij fragment i zapisz stem narzędziem `python scripts/make_stem.py <źródło> --start S --end E --out legacy/source/game-audio-pipeline/stems/<nazwa>.mp3` (obsługuje MP3/WAV/M4A — dekodowanie PyAV automatycznie, fade wliczony); (4) zarejestruj w `data/sources.json` z url oryginału i kanałem pobrania w `notes`.

## Sample Scout — pobieranie przez GitHub Actions

Gdy potrzebnego zdarzenia nie ma w zweryfikowanych bibliotekach, użyj workflow **Sample scout**. Runner GitHub Actions ma dostęp do Freesound i Internet Archive, którego nie ma sandbox Arena. Workflow pobiera najwyżej pięć kandydatów CC0 do ograniczonego katalogu `legacy/source/sample_scout/`, zapisuje manifest z URL-em oryginału, autorem, licencją, metryką społecznościową, rozmiarem i SHA-256, a następnie commit bota udostępnia pliki kolejnemu agentowi przez `git fetch`.

- `freesound`: wymaga sekretu Actions `FREESOUND_TOKEN`; ranking: średnia ocena, liczba ocen, pobrania;
- `archive.org`: bez sekretu; ranking: liczba pobrań, wyłącznie po potwierdzeniu CC0 w metadanych;
- uruchamiaj tylko z `main` przez **Actions → Sample scout → Run workflow**; kandydaci zastępują poprzednią paczkę, aby repozytorium nie rosło bez limitu;
- workflow zapisuje **kandydatów**, nie źródła produkcyjne. Przed użyciem agent odsłuchuje plik, sprawdza oryginalną stronę/licencję i dopiero wtedy wpisuje wybrany stem do `data/sources.json` zgodnie z regułą 8 z `AGENTS.md`.

Nie umieszczaj tokenu Freesound w workflow, kodzie ani pliku konfiguracyjnym — wyłącznie w sekretach GitHub Actions.
