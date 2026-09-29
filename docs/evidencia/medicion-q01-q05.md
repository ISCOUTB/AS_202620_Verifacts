# Evidencia S9 — medición de Q-01 y Q-05

Generado por `scripts/medir_q01_q05.py` el 2026-09-28T22:23:56.

- Entorno: Windows 11, Python 3.14.7, uvicorn en 127.0.0.1, 1 cliente concurrente.
- Entrada: texto de 10000 caracteres, origen `texto`, con persistencia real en SQLite temporal.
- No incluye el origen `url` (depende de un sitio externo, ver ADR-0003).

| Escenario | Medida exigida | Resultado (200 corridas / 100 repeticiones) | Veredicto |
|---|---|---|---|
| Q-01 | P95 <= 3000 ms | P95 = 46.9 ms · mediana = 16.6 ms · máx = 82.3 ms | CUMPLE |
| Q-05 | 100 % de coincidencia | 100 % (1 resultado(s) distinto(s)) | CUMPLE |
