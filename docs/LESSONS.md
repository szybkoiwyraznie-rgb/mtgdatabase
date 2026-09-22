# LESSONS — trwała wiedza projektu

Ten plik zawiera krótkie, praktyczne lekcje wynikające z pracy agentów. Każdy wpis powinien odpowiadać na pytanie: co się wydarzyło, czego się nauczyliśmy i jak zapobiec powtórce.

## Format wpisu

```markdown
## YYYY-MM-DD — Krótki tytuł

- Sytuacja:
- Wniosek:
- Zasada / działanie zapobiegawcze:
```

## 2026-09-21 — Workflow musi być bezpieczny na branchu roboczym

- Sytuacja: deployment Pages nie powinien wykonywać się przed scaleniem do `main`.
- Wniosek: build i deploy trzeba rozdzielić warunkiem gałęzi.
- Zasada / działanie zapobiegawcze: na branchach roboczych uruchamiaj build i walidację, a deployment wykonuj tylko z `main`.
