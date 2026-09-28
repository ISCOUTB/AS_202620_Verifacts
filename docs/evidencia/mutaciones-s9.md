# Evidencia S9 — defectos inducidos (2026-09-28)

Generado por `scripts/mutaciones_s9.py`. Cada defecto se aplica solo, sobre una copia temporal.

| Defecto inducido | Suite previa a S9 | Pruebas nuevas de S9 |
|---|---|---|
| M1 frontera `<` -> `<=` en 30 | PASA (no detecta) | FALLA (detecta) |
| M2 umbral alto 60 -> 50 | FALLA (detecta) | FALLA (detecta) |
| M3 sin tope de 100 | PASA (no detecta) | FALLA (detecta) |
| M4 peso sensacionalismo 20 -> 25 | FALLA (detecta) | FALLA (detecta) |
| M5 scoring importa analyzer.py (cruza límite) | PASA (no detecta) | FALLA (detecta) |
