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
  („krzyk dużego ptaka zwiadowczego"), sprawdza stan bazy i użycie wpisów,
  i dopiero wtedy pozyskuje kandydatów.
- **Reuse bez limitów (ADR 0006):** klocki są reużywalne; jedyna twarda
  reguła to unikalna kombinacja a·b·c·d między fabułami. Różnorodność
  zapewnia miękki ranking resolvera nad zbiorem semantycznie pasujących
  wpisów (profil fabuły → kafeteria → resolver; plan:
  `docs/roadmap-semantyka.md`). Statystyki: `library_tool.py report`.
- Odrzuceni kandydaci **nigdy nie wchodzą do baz** — ale cała bramka
  (`data/gates/gNNN/`) jest commitowana, jako trwała dokumentacja procesu
  doboru (odporna na resety sandboksa).

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

### Gwarancja słyszalności kodu (ADR 0004)

Montaż nie przechodzi odsłuchu właściciela — jego poprawność gwarantują
bramki maszynowe nad FINALNYM mixem:

- **atak każdej nuty** w oknie 0,3 s musi przewyższać kontekst tuż przed o
  co najmniej 2,5 dB (`note_attack_margin_db`); nuty ucięte przez
  master-fade są poza bramką;
- **licznik nut**: zagrane == liczba nut gestu (adaptacja rejestru nie wolno
  zgubić nuty — twardy błąd);
- **autokalibracja**: zanim bramka krzyknie, render w pętli (≤6 iteracji)
  dobija maskowane nuty o brakujący margin +0,5 dB zapasu (sufit 8 dB).
  Boosty lądują w warnings i audycie (`coda_boosts_db`). Sufit nasycił się?
  → geometria układu hero/kody lub parowanie gest×instrument jest
  niewykonalne — agent poprawia układ czasowy, nie podbija „na okoł";
- `coda.target_db` receptury znaczy teraz **poziom RMS pojedynczej nuty
  (przed velocity)**, nie całego bloku kodów.

### Adaptacja rejestru kody (scripts/coda_synth.py)

Gesty w bazie a zapisujemy w rejestrze muzycznym (nuty MIDI), a instrumenty
bazy b mają wąski, nieciągły zakres sampli. Koda NIE może cicho „gubić" nut —
stosuje deterministyczną drabinę (każdy krok loguje `!` w renderze i audycie):

1. dokładne midi albo najbliższa w ±3 półtony;
2. nuty spoza zakresu przenoszone o oktawę (±12, ±24), jeśli wpadną w bank w ±3;
3. jeśli nadal brakuje nut — CAŁY gest transponowany jednolicie (t ∈ ±24),
   wybierając przesunięcie o maks. liczbie dopasowanych nut (rytm i kontur bez
   zmian), potem min. korekta i min. |t|;
4. dopiero co się nie zmieściło — pominięte z jawnego ostrzeżeniem.

Dodatkowo każda nuta brzmi co najmniej `MIN_NOTE_AUDIBLE_SEC` (1,2 s) —
krótkie wycinki jednostrzałowców (udarzenia kotłów 0,3 s) zanikały pod tłem
i stapiały się w jedno „bum". Miks nigdy nie wykracza poza `length_sec`:
ogon kody wychodzi w wspólnym master-fade, więc plik ma równo tyle sekund,
ile każe receptura.

Wynik adaptacji odsłuchuje agent (nie właściciel); gdy adaptacja psuje zamiar
gestu (np. zjadł trójton), remedium nie jest „ładniejszy maper", tylko nowe
sampla / wariant gestu przez bramkę — patrz ADR 0004.

Tło krótsze niż sygnatura zapętlamy crossfade'em (`sig_audio.loop_to_length`),
żeby szew pętli nie klikał.

Bramki twarde (całość):

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

### Obróbka kandydata: skrypt, nie ręczna edycja

Każda bramka ma własny `scripts/build_gate_gNNN.py`, który z surowego
źródła robi kandydatów **deterministycznie** i drukuje metryki. Dzięki temu
poprawka po werdykcie („utnij koniec”) jest zmianą parametru, a nie nowym
plikiem znikąd. Gotowe cegiełki do ponownego użycia:

- `build_gate_g003.to_roar(wave, semitones, hp_hz, lp_hz, drive)` —
  pitch-down z filtrem i saturacją (podstawa „poważnych” głosów);
- `build_gate_g003.soft_limit(wave, crest_db)` — tanh **przed**
  `normalize_rms`; odwrotna kolejność gasi RMS (crest 21 dB → −22 dB);
- `build_gate_g004.oga_source(...)` — proweniencja paczek OGA;
- `build_gate_g007.trim_silence(wave)` — obcięcie cichych brzegów;
  nagrania terenowe miewają sekundę zapasu przed zdarzeniem;
- `build_gate_g007.make_warcry(..., end_sec=)` — warstwowanie kilku głosów
  z rozjazdem czasowym i rozstrojeniem (efekt „tłumu”, nie chórku).

Poziom kandydatów wyrównuj do **−15 dB RMS** (głosy/hero) albo do
`level_ref_db` wpisu (tła, zwykle −33 dB), żeby porównanie w bramce dotyczyło
charakteru, a nie głośności.

## Folder audio/library/

Przyjęte klocki: `heroes/`, `backgrounds/`, `instruments/<instrument>/`.
Wszystko MP3 44,1 kHz stereo. Są commitowane (to rdzeń warsztatu).
