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
