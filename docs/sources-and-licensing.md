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

Formalny rejestr sampli produkcyjnych to pola `source` we wpisach czterech baz
(`data/library/*.json`); każdy klocek (`hero`, `tło`, `instrument`, nuta
instrumentu) ma źródło, autora, licencję, url i kanał pobrania. Kandydaci na
bramki dokumentują proweniencję już w manifeście bramki. **Pola `source`
kopiuj z istniejącego wpisu rejestru** (`title`, `author`, `license`, `url`,
`channel`, `notes`) — własny słownik w nowym skrypcie bramki rozjechał się
ze schematem i `library_tool check` wyłapał to dopiero po `accept`. Historyczny rejestr
dawnej fabryki: `legacy/old-factory/data/sources.json`.

## Katalog zweryfikowanych bibliotek dźwięków (osiągalnych z sandboxa Arena)

Egress sandboxa tnie TLS do Wikimedia/NPS/Freesound/raw.githubusercontent (patrz LESSONS); sprawdzonym kanałem jest **`git clone` z github.com** (najlepiej `--depth 1 --filter=blob:none --sparse` + `git sparse-checkout set <katalog>`). Poniższe repozytoria zweryfikowano 2026-09-22 (odpalone klony/API, potwierdzone pliki audio i licencje). Każdy pobrany sample i tak rejestrujemy w `data/sources.json` (AGENTS.md #8) — licencją jest status ORYGINAŁU, nie mirrora.

| Repozytorium | Zawartość | Licencja (oryginału) | Format / uwagi |
|---|---|---|---|
| `rosuH/YSL` | Mirror całej Yellowstone Sound Library: zwierzęta (**Wolves**, kojoty, kruk, łoś, żubr, **Red Fox**, ptaki), ogień, grzmot, gejzery, woda, błotne kotły, pejzaże dźwiękowe, maszyny (skuter śnieżny, wóz konny). **NIE MA niedźwiedzia** (dawniej błędnie opisano inwentarz — 2026-09-23 skorygowano po `git ls-tree` na HEAD) | Public Domain (NPS, praca rządu USA) | MP3; duże pliki ambientowe (do 25 min) — wycinać fragment; użyte dotąd: `wolf_howl.mp3`, `steam_vent.mp3`, `lava_rumble.mp3` i `campfire.mp3` (Fire 6-11,5 s / 6-9 s) |
| `novincode/atomcut-library` | ~100 packów z OpenGameArt + Kenney + Freesound: **miecze (20 SFX ataków i zderzeń), metal i drewno (100 SFX), kroki (kamień/żwir/błoto/śnieg/trawa/skóra/zbroja), magia i zaklęcia, potwory/gobliny/zombie/alieni, drzwi, woda/plusk/slime/błoto, szelest liści, pękające drewno, Sci-Fi (60+50 SFX, lasery/fazery/tarcze), bagna/ambience, głosy (wysiłek/ból/okrzyki), księgi, karty, kości, klawiatura** | CC0 1.0 (OpenGameArt/Kenney/Freesound — filtr CC0 w `sources/*.json`; brak LICENSE w korzeniu repo, licencję każdego packu potwierdzamy na stronie OGA przy pobraniu) | **M4A/AAC 48 kHz** — soundfile nie czyta: dekodować przez `pip install av` (PyAV, działa w venv) → WAV; pliki krótkie, gotowe na stemy |
| `Daarko/sparkstream-sounds` | Kenney: **impacts/whooshes (130)**, kliknięcia UI (151), digital/Sci-Fi beeps (135), RPG audio (51) | CC0 1.0 (Kenney; oryginalne teksty licencji w `credits/`) | WAV; profesjonalny sound design (nie nagrania terenowe) — idealne do impacts/whooshów i beepów SF |
| `sgossner/VCSL` | Versilian Community Sample Library — **próbki prawdziwych instrumentów** (dzwony, smyczki, dęte, perkusja, etniczne) | CC0 1.0 | Duże (~4 GB) — wyłącznie sparse-checkout wybranych instrumentów; zamiennik syntetycznych padów/dzwonków prawdziwym timbrem w scenach fantasy/mistycznych |
| `sgossner/VSCO-2-CE` | VSCO 2 Community Edition — orkiestra (nagrania sekcji, staccati, uderzenia) | CC0 1.0 | ~2,3 GB, sparse-checkout; epickie stingery/fantazyjne kulminacje |

**Paczki atomcut sprawdzone odsłuchowo w sesjach 2026-09-23** (ścieżki
`packs/<id>/audio/*.m4a`, każda z `pack.json` z licencją CC0 i autorem):

| Pack | Do czego | Werdykt |
|---|---|---|
| `opengameart-male-gruntyelling-sounds` (haeldb) | **wrzaski/okrzyki bojowe, orkowie, hordy** — 62 prawdziwe męskie krzyki | **przyjęty g007** (o.3 → `warband_cry_03`); technika: pitch-down 4–5 st + saturacja |
| `opengameart-monster-sound-effects-pack` (ogrebane) | ryki potworów/bestii | **przyjęty g004** (r.1 → `beast_roar_long_01`) |
| `opengameart-magic-spell-sfx` (jaggedstone) | czary, pociski magiczne | **przyjęty g004** (m.2 → `spell_cast_bolt_01`) |
| `opengameart-goblins-sound-pack` (artisticdude) | gobliny | **odrzucony 2× (g004, g005)** — wokalizacja kreskówkowa („Smerfy”), pitch-down nie pomaga |
| `opengameart-80-cc0-creature-sfx` (rubberduck) | stwory, trolle, grunty | **odrzucony (g006)** jako wrzask bojowy; zapas na potwory |
| `opengameart-40-cc0-water-splash-slime-sfx` (rubberduck) | plusk, bąble, woda, slime | rozpoznany, niewykorzystany (do plusków punktowych, nie do teł) |
| `opengameart-swamp-environment-audio` (lokif) | ambience bagien | rozpoznany, zapas na tła mokradeł |

Niesprawdzone, a obiecujące (są w mirrorze): `opengameart-20-sword-sound-effects-attacks-and-clashes`
(miecze), `opengameart-zombies-sound-pack`, `opengameart-voiceover-pack-fighter-40-taunts`,
`opengameart-15-vocal-male-strainhurtpainjump-sounds` (głosy wysiłku),
`opengameart-100-cc0-metal-and-wood-sfx`, `opengameart-75-cc0-breaking-falling-hit-sfx`.

**Yellowstone (YSL) — realny inwentarz** po `git ls-tree HEAD` (2026-09-23):
wilki, kojoty, lis, łoś, żubr (jedzenie/ruja), kruk, ~20 gatunków ptaków,
żaby, ogień, grzmot, gejzery (kilkanaście), fumarole, gorące źródła
(**The Dragon's Mouth** = woda bijąca o ściany jaskini, użyta w g008),
Yellowstone Lake, błotne kotły, skuter śnieżny, wóz konny. **Nie ma
niedźwiedzia** ani nagrań „las/deszcz/morze”.

Pomocnicze: `Cy4nWare/sfx-api` (Kenney CC0, duplikat sparkstream przez jsdelivr), `stargatedaw/stargate-sample-pack` (PD, sample instrumentów do DAW — marginalne dla jingli). Odrzucone: repozytoria „SFX generowane z kodu" (blip8, free-sfx-bgm — sprzeczne z zasadą żywych sampli), scraper BBC Sound Effects (host blokowany + licencja RemArc niekomercyjna).

Procedura pobierania: (1) potwierdź licencję packu na stronie źródłowej;
(2) sparse-clone do `/tmp`; (3) obowiązkowa audycja `python scripts/stem_probe.py <nagranie>`;
(4) wytnij kandydata skryptem bramki `scripts/build_gate_gNNN.py` do
`data/gates/<bramka>/candidates/<nazwa>.mp3` (dla prostych wycinków wystarczy
`python scripts/make_stem.py <źródło> --start S --end E --out ...`;
MP3/WAV/M4A — dekodowanie PyAV automatycznie, fade wliczony); (5) manifest
bramki z wpisem `entry` zawierającym proweniencję; (6) po akceptacji
`library_tool.py accept` przenosi plik do `audio/library/` i dopisuje wpis
do rejestru. Odrzuty nie wchodzą do gita.

## Sample Scout — pobieranie przez GitHub Actions

Gdy potrzebnego zdarzenia nie ma w zweryfikowanych bibliotekach, użyj workflow **Sample scout**. Runner GitHub Actions ma dostęp do Freesound i Internet Archive, którego nie ma sandbox Arena. Workflow pobiera najwyżej pięć kandydatów CC0 do ograniczonego katalogu `legacy/source/sample_scout/`, zapisuje manifest z URL-em oryginału, autorem, licencją, metryką społecznościową, rozmiarem i SHA-256, a następnie commit bota udostępnia pliki kolejnemu agentowi przez `git fetch`.

- `freesound`: wymaga sekretu Actions `FREESOUND_TOKEN`; ranking: średnia ocena, liczba ocen, pobrania;
- `archive.org`: bez sekretu; ranking: liczba pobrań, wyłącznie po potwierdzeniu CC0 w metadanych;
- **Uruchomienie z sesji agenta:** token sandboksa (GitHub App) nie ma
  uprawnienia `actions:write`, więc `gh workflow run` zwraca `HTTP 403:
  Resource not accessible by integration`. Obejście wbudowane w workflow —
  wyzwalacz `repository_dispatch`, który wymaga tylko `contents:write`:

  ```bash
  gh api repos/szybkoiwyraznie-rgb/mtgdatabase/dispatches \
    -f event_type=sample-scout \
    -F 'client_payload[source]=archive.org' \
    -F 'client_payload[query]=orc war cry' \
    -F 'client_payload[count]=5'
  ```

  Działa dopiero, gdy wersja workflow z tym wyzwalaczem jest w `main`
  (GitHub czyta `repository_dispatch` wyłącznie z domyślnej gałęzi).
  Alternatywa ręczna: **Actions → Sample scout → Run workflow** z `main`.
  Nie proś właściciela o token ani o rozszerzanie uprawnień aplikacji;
  kandydaci zastępują poprzednią paczkę, aby repozytorium nie rosło bez limitu;
- workflow zapisuje **kandydatów**, nie źródła produkcyjne. Agent weryfikuje
  proweniencję, wystawia kandydata w bramce odsłuchowej i dopiero po
  akceptacji właściciela wpis trafia do `data/library/*.json` (AGENTS.md #8).

Nie umieszczaj tokenu Freesound w workflow, kodzie ani pliku konfiguracyjnym — wyłącznie w sekretach GitHub Actions.
