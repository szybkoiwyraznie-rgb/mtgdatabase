# Obowiązkowa lektura agenta

To jest indeks dokumentów, które agent musi przeczytać przed pracą:

1. `AGENTS.md`
2. `README.md`
3. `CONTRIBUTING.md`
4. `docs/required-reading.md`
5. `docs/agent-workflow.md`
6. `docs/architecture.md`
7. `docs/feedback-system.md`
8. `docs/sources-and-licensing.md`
9. `docs/LESSONS.md`
10. wszystkie pliki `docs/decisions/*.md` oznaczone jako aktywne

Dokumenty historyczne i szczegółowe raporty nie należą do obowiązkowej lektury. Można je przechowywać w `docs/archive/`, aby nie zwiększać budżetu kontekstu.

## Budżet

Cała obowiązkowa lektura ma limit **50 000 tokenów**. Walidator stosuje konserwatywne przybliżenie tokenów na podstawie długości tekstu. Jeśli limit jest przekroczony, agent musi przed rozpoczęciem pracy:

- usunąć powtórzenia;
- skrócić przykłady i opisy historyczne;
- połączyć rozproszone zasady;
- zachować decyzje, ograniczenia, procedury i kryteria jakości;
- przenieść szczegóły historyczne do `docs/archive/`;
- ponownie uruchomić walidator.

Nie wolno rozwiązywać przekroczenia przez usuwanie istotnych zasad bez ich zachowania w dokumentacji archiwalnej lub aktualnej.
