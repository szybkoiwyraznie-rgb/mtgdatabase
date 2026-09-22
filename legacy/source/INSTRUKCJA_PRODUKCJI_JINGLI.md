# INSTRUKCJA DLA AGENTA: PRODUKCJA FABULARNYCH JINGLI AUDIO (5–6s MP3)

Niniejszy dokument jest wzorcem technologicznym i wykonawczym do tworzenia krótkich (ok. 5.5s), narracyjnych efektów dźwiękowych (audio vignettes / stingers) na podstawie pliku z opisami fabularnymi (`fabuła.csv`).

Każde zdarzenie z arkusza ma otrzymać dedykowany, przemyślany plik MP3 nazwany swoim numerem ID (np. `1.mp3`, `2.mp3`, `24.mp3`, `542.mp3`).

---

## 1. STRUKTURA PLIKU ŹRÓDŁOWEGO (`fabuła.csv`)
Plik jest w formacie TSV (rozdzielany tabulatorem):
* **Kolumna 1:** Identyfikator liczbowy zdarzenia (np. `1`, `2`, `3`...).
* **Kolumna 2:** Pełny opis fabularny zdarzenia (Lore narracyjne).

---

## 2. STANDARD JAKOŚCI V2 (ZASADY INŻYNIERII DŹWIĘKU)
Dźwięk nie może być prostym, syntetycznym „pikaniem” ani monofonicznym szumem. Każdy 5.5-sekundowy jingle opiera się na **trójwarstwowej dramaturgii**:

```text
[0.0s ────────────────────────────── 5.5s]  Warstwa 1: Ambiance (Tło przestrzeni + Sub-bass/Dron)
      [0.8s ────────────── 3.8s]            Warstwa 2: Foley (Fizyczny ruch: kroki, woda, ogień)
            [1.8s ────── 3.6s]              Warstwa 3: Stinger (Kulminacja: ryk, ostrze, magia)
                                            *Ducking: Tło wycisza się o -50% w trakcie Stingera!
```

### Złote reguły miksu:
1. **Unikanie maskowania (Separacja czasowa):**
   * Nigdy nie nakładaj najgłośniejszego rozbryzgu wody lub uderzenia w tej samej milisekundzie, w której ryczy bestia lub wybrzmiewa dobycie miecza.
   * Daj kluczowemu zdarzeniu (wokaliza, sygnał, portal) czyste okno (zwykle w przedziale 1.8s – 3.6s).
2. **Separacja planów (Dry / Wet):**
   * **Błąd V1:** Nałożenie globalnego echa jaskini na całą ścieżkę zepchnęło ryk w odległe tło.
   * **Standard V2:** Główny obiekt (paszcza potwora, orkowe ostrze) uderza jako bezpośredni, czysty i głośny sygnał w centrum panoramy (`pan=0.0`), a pogłos jaskini/kanionu jest dodawany jako odbicie na ścianach (`delay ~120-180 ms`).
3. **Pasma częstotliwości (Prezencja):**
   * Dla wokaliz potworów i zwierząt: podbijaj pasmo **1000–3500 Hz** (ludzkie ucho słyszy tam chrypę i agresję paszczy) oraz stosuj miękkie nasycenie (`np.tanh`).
   * Zawsze filtruj skrajny dół (`high-pass 80–120 Hz`), by usunąć niechciany szum z nagrań terenowych.

---

## 3. PROFILOWANIE BRZMIENIA POD GATUNKI FABUŁY

| Typ sceny | Warstwa 1 (Tło) | Warstwa 2 (Fizyka / Foley) | Warstwa 3 (Punkt kulminacyjny) |
| :--- | :--- | :--- | :--- |
| **Góry / Wąwóz / Bitwa** | Górski świst wiatru + sub-dron 44 Hz | Trzaski pochodni / iskry / łopot skrzydeł | Przeszywający krzyk kruka / wyciągnięcie stali z pochwy |
| **Zalana Jaskinia / Bestia**| Pogłos zalanej groty + kapanie kropel | Ciężkie tąpnięcie w kamień + rozbryzg wody | Bliski, gardłowy ryk (grizzly + aligator) na pierwszym planie |
| **Gabinet / Spisek / Chochlik**| Cicha komnata + niski szmer intrygi | Skwierczenie płonącego pergaminu / ogień | Złośliwy pisk/chichot chochlika + eteryczny puls kryształu |
| **Mistyczne Jezioro / Baśń**| Spokojny plusk fal o kamień we mgle | Szelest przewracanych stron księgi | Czysty, krystaliczny akord arturiańskich dzwonów |
| **Akademia Magii / Portal**| Otwarty taras + wirujący szum portalu | Szelest rozwiewanych notatek na wietrze | Pęknięcie próżni / świst zaklęcia odsyłającego (banish) |

---

## 4. INSTRUKCJA WYKONAWCZA DLA AGENTA (JAK REALIZOWAĆ ZLECENIE)

Gdy użytkownik prosi o realizację kolejnej partii (np. *„Zrób jingle od 6 do 15”*):

1. **Odczytaj zadany zakres z `/home/user/uploads/fabuła.csv`:**
   * Wyciągnij wiersze o numerach ID od 6 do 15.
2. **Zaprojektuj dramaturgię każdego jingle'a:**
   * Przeanalizuj treść: Jakie jest otoczenie? Jaki jest główny ruch fizyczny? Jaki jest punkt kulminacyjny?
3. **Wygeneruj plik audio w Pythonie:**
   * Użyj `scipy.signal`, `soundfile`, `numpy` oraz `ffmpeg` (znajdującego się w `/tmp/bin/ffmpeg` lub ścieżce systemowej).
   * Zadbaj o to, by plik trwał 5.5 sekundy i miał głośność znormalizowaną do ok. -0.5 dBFS.
4. **Zapisz wynikowy plik jako:**
   * `/home/user/jingle_output/{id}.mp3` (np. `6.mp3`, `7.mp3`, `8.mp3`...).
5. **Dbaj o limit przestrzeni roboczej:**
   * Wszystkie pliki tymczasowe (`.wav`, surowe próbniki) twórz w `/tmp/` i usuwaj je zaraz po eksporcie do `.mp3`.
   * Dzięki temu katalog roboczy zajmuje poniżej 1 MB na każde kilkadziesiąt plików!
