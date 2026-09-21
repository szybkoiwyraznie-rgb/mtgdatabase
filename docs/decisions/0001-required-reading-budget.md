# ADR 0001: Budżet obowiązkowej lektury

- Status: accepted
- Data: 2026-09-21

## Decyzja

Obowiązkowa lektura agenta nie może przekraczać 50 000 tokenów. Zbiór jest jawnie wymieniony w `docs/required-reading.md` i sprawdzany automatycznie.

## Uzasadnienie

Agent musi mieć dostęp do pełnego kontekstu operacyjnego, ale nadmiar dokumentacji obniża skuteczność i zwiększa ryzyko pominięcia ważnych zasad. Historia i szczegółowe raporty pozostają dostępne w archiwum, lecz nie są wczytywane domyślnie.

## Konsekwencje

Każda rozbudowa instrukcji wymaga usunięcia duplikatów lub przeniesienia materiału historycznego. Przekroczenie budżetu blokuje walidację i wymaga odchudzenia dokumentacji przed dalszą pracą.
