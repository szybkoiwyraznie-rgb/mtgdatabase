# ADR 0002: Oceny od razu na stronie i natychmiastowa paczka ZIP

- Status: superseded (zastąpiony przez ADR 0003, 2026-09-23) — opisuje zakończony system ocen z issues
- Data: 2026-09-22

## Decyzja

1. Pięć jingli z `legacy/source/jingle_output/` (fabuły 1–5) to produkcyjne wersje `v1` objęte pełnymi zasadami wersjonowania, nie materiał demonstracyjny.
2. Każda ocena z issue z etykietą `feedback` musi trafiać do `data/versions.json` — automatycznie (workflow `Sync ratings from issues`) i weryfikowane w każdej pętli agenta.
3. Strona pokazuje świeżą ocenę natychmiast po wysłaniu (warstwa `localStorage` na danym urządzeniu), a po synchronizacji na wszystkich urządzeniach.
4. Paczka `best-jingles-latest.zip` w Releases ma istnieć od razu po pierwszych ocenach; bez sekretu `JINGLE_ZIP_PASSWORD` jest nieszyfrowana. Do paczki nadal trafiają wyłącznie ocenione wersje.

## Uzasadnienie

Właściciel ocenia jingle w panelu i oczekuje natychmiastowego, widocznego efektu oraz możliwości pobrania paczki bez czekania na przyszłe pętle. Stan „demo" był nieporozumieniem — te pięć jingli jest normalnymi wersjami.

## Konsekwencje

`scripts/sync_ratings.py` oraz workflow `Sync ratings from issues` są krytycznymi elementami potoku; ich awaria wstrzymuje publikację ocen. `build_best_zip.py` toleruje nieocenione wersje (pomija je), więc release nie pada pomiędzy ocenami. Warstwa `localStorage` znika przy wyczyszczeniu danych przeglądarki i nie przenosi się między urządzeniami — wtedy ratuje ją tylko synchronizacja z issues.