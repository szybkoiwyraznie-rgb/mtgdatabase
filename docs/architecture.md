# Architektura

```text
CSV fabuł
  ↓
agent / receptura
  ↓
wersje jingli + metadane
  ↓
GitHub Pages: katalog, podstrony, odsłuch, formularz
  ↓
bezpieczny endpoint → GitHub Issues
  ↓
agent czyta feedback i tworzy kolejną wersję

najlepsze ocenione wersje → płaski ZIP → GitHub Release
```

## Repozytorium

Źródłem fabuł jest `kolekcja.csv`, tab-separated z kolumnami `Ilustracja`, `Nazwa Karty`, `Narracja`. Importer wyciąga liczbowy prefiks artID: `123DOM` staje się ID `123`, a set `DOM` pozostaje wyłącznie metadanymi. Każda fabuła otrzymuje stabilny identyfikator, tytuł i tekst `story`; ZIP używa nazwy `123.mp3`. Materiały prototypowe są rozdzielone w `legacy/source/`. Każda wersja ma własną recepturę, MP3, metadane i historię raportów.

## Prywatność

GitHub Pages w planie Free nie powinno być traktowane jako prywatny hosting. Ekran PIN może ograniczać przypadkowy dostęp, ale nie chroni plików przed osobą, która zna adres lub potrafi przeanalizować kod strony. Pliki docelowe są przeznaczone do pobrania i użycia offline; do publikacji Pages należy świadomie wybierać kopie odsłuchowe.

## Dystrybucja

Paczka nie jest przechowywana jako zwykły plik w repozytorium. GitHub Actions publikuje ją jako asset Release. Opcjonalne szyfrowanie ZIP-a odbywa się w workflow z użyciem sekretu `JINGLE_ZIP_PASSWORD`, nigdy w kodzie.
