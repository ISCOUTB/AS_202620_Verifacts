# Violaciones de modularidad detectadas · VeriFacts

Este documento registra violaciones a la regla transversal de propiedad de
datos (ver [arc42 §8.6](arc42/08-conceptos-transversales.md#modelo-de-dominio-y-contextos-delimitados-s6)
y [`docs/propiedad-datos.md`](propiedad-datos.md)), y su plan de corrección.
Se referencia desde ambos documentos, así que debe existir aunque esté
vacío de violaciones reales.

## Método de auditoría

Buscar accesos directos a la base de datos (`sqlite3.connect` /
`_get_connection`) fuera de `app/persistence/repository.py`:

```cmd
findstr /s /i "sqlite3.connect" app\*.py
```

Repetir esta búsqueda cada vez que se agregue un módulo nuevo o un endpoint
nuevo que lea o escriba historial.

## Registro

| Fecha de auditoría | Violación encontrada | Módulo(s) involucrados | Estado |
|---|---|---|---|
| 2026-09-07 | Ninguna — `app/api/routes.py` y los `service.py` de `analysis`/`scoring` solo llaman a `save_analysis()`/`get_analysis()`, sin acceso directo a `sqlite3` | — | ✅ Sin violaciones al momento de esta revisión |
| 2026-09-28 | `app/modules/scoring/service.py` importaba `Finding` desde `app/modules/analysis/analyzer.py` (archivo interno de otro módulo). Sin violación de propiedad de datos: ningún módulo usa `sqlite3` fuera de `repository.py` | Scoring → Analysis | ✅ Corregido (importa desde `analysis.service`); vigilado por `tests/test_boundaries.py`. Detalle en [auditoría S9](auditoria-s9.md) |

## Nota para el corte 1

Este archivo debe volver a revisarse cuando se implementen los endpoints de
lectura (`GET /analysis`, `GET /analysis/{id}`) y la ingestión por URL,
porque son los puntos donde más fácilmente un nuevo endpoint podría tentar a
escribir directamente en la tabla `analyses` en vez de pasar por
`app/persistence/repository.py`.
