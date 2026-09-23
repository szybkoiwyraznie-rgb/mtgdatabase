# System sygnatur dźwiękowych

Architektura produkcyjna warstwy audio gry fabularnej (decyzja właściciela
2026-09-23; zastępuje „fabrykę jingli" — historia w `legacy/old-factory/`).

## Idea

Każda fabuła dostaje jedno **okno dźwiękowe** (sygnaturę): maks. 10 sekund,
pojawia się w grze co 40–120 s. Sygnatura składa się z czterech klocków:

```text
tło (d)  +  hero (c)  +  koda (a)  +  instrument (b)
```

- **(d) tło** — przestrzeń miejsca (np. wiatr w wąwozie, chór żab): niski,
  równy podkład na pełną długość okna.
- **(c) hero** — jedno główne zdarzenie fabuły (krzyk kruka, zew nura):
  żywe nagranie, czytelne, w oknie czasowym z receptury.
- **(a) koda (gest)** — krótka muzyczna odpowiedź zdefiniowana **semantycznie**
  (zagrożenie, cud, tajemnica...) i zapisywana nutowo (MIDI: nuta, on, off, vel).
- **(b) instrument** — brzmienie, na którym koda jest odtwarzana
  (jednostkowe nagrania prawdziwych instrumentów: VCSL/VSCO).

Koda nie zna instrumentu, instrument nie zna kody — iloczyn a×b daje
różnorodność bez dodatkowej pracy (ta sama „tajemnica" na harfie, dzwonach
albo szkle to trzy brzmienia).

## Cztery bazy (data/library/*.json)

`heroes.json`, `backgrounds.json`, `gestures.json`, `instruments.json`.
Każdy wpis ma: id, **opis semantyczny** (rola, charakter, dobry/zły do),
proweniencję licencyjną (źródło, autor, licencja, url, kanał pobrania)
i pieczątkę akceptacji `approved` (bramka, wybór, data).

- Bazy **startują puste i rosną organicznie** — wpis trafia do bazy wyłącznie
  przez akceptację właściciela w bramce odsłuchowej (`docs/gate-protocol.md`).
- Zasada „rola przed plikiem": agent najpierw definiuje rolę semantyczną
  („krzyk dużego ptaka zwiadowczego"), sprawdza, czy rola jest obsadzona,
  i dopiero wtedy pozyskuje kandydatów.
- Odrzuceni kandydaci **nigdy nie wchodzą do repozytorium** (żyją w `work/`,
  które jest gitignore).

## Receptury i produkty

- `data/recipes/<id>.json` — jedna receptura na fabułę (aktualna):

```json
{
  "story_id": "1",
  "length_sec": 8.5,
  "seed": 7,
  "background": {"id": "wind_canyon_01", "offset_sec": 0.0, "target_db": -32},
  "hero": {"id": "raven_cry_double_01", "at_sec": 1.3, "target_db": -15},
  "coda": {"gesture": "g1b_march_pulse", "instrument": "timpani", "at_sec": 4.6, "target_db": -21}
}
```

- Produkt to **znacząco `audio/signatures/<id>.mp3`** — nazwa to bezwzględnie
  numer fabuły (paczka ZIP buduje się płasko z tego katalogu; skrypt
  `build_pack.py` odrzuca każdą inną nazwę).
- Zablokowana kombinacja a·b·c·d nie może się powtórzyć między fabułami
  (walidator `library_tool.py check`).
- Nowa wersja sygnatury = ta sama nazwa pliku (historię trzyma git), zwykle
  przez wymianę jednego klocka — nie przez re-miks.

## Render i QA (scripts/render_signature.py)

Mix jest deterministyczny: poziomy `target_db`, okna `at_sec` z receptury,
humanizacja ziarnicowana seedem. Bramki twarde:

- długość ≤ 10 s;
- hero czytelny: RMS(okno hero) ≥ RMS(1 s przed hero) + 6 dB;
- całość RMS ≥ -26 dBFS;
- udział energii > 6 kHz ≤ 20 %.

Jakość wynika z konstrukcji (zatwierdzone klocki + zatwierdzone gesty),
nie z oceny po fakcie — bramki pilnują tylko poprawności montażu.

## Pozyskiwanie kandydatów

- **teła/hero (d, c):** zweryfikowane biblioteki (`docs/sources-and-licensing.md`):
  `git clone` sparse z github.com (YSL/NPS PD, atomcut CC0, Kenney CC0);
  gdy brakuje — workflow Sample scout (Freesound/Archive.org przez GHA).
  Obowiązkowa audycja `stem_probe.py` przed cięciem (ciche głowy nagrań!).
- **instrumenty (b):** VCSL / VSCO-2 CE (CC0), sparse-checkout `--no-cone`
  konkretnych plików nutowych; commitujemy tylko potrzebne nuty (MP3).
- **kody (a):** definicje nutowe pisane przez agenta w PLC (patrz protokół
  bramki) — render kandydacki na neutralnym instrumencie referencyjnym.

## Folder audio/library/

Przyjęte klocki: `heroes/`, `backgrounds/`, `instruments/<instrument>/`.
Wszystko MP3 44,1 kHz stereo. Są commitowane (to rdzeń warsztatu).
