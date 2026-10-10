# Persistencia del historial en Render

Prueba manual sobre https://verifacts-api.onrender.com (plan gratuito; ver [costos](../costos.md)), realizada el 2026-10-10.

## Observación

| Hora (UTC) | Evento | Resultado |
|---|---|---|
| ≈ 22:53 | Última petición `POST /analysis` de la serie de medición ([render_frio.csv](render_frio.csv)) | HTTP 200, registro guardado |
| 22:53 → 23:16 | Sin tráfico hacia el servicio (≈ 23 min) | — |
| 23:16:41 | `POST /analysis` desde `/docs` | `"id": 1`, `created_at` 2026-10-10 23:16:41 — [captura](persistencia-post-1.png) |
| 23:17:18 | `POST /analysis` desde `/docs` | `"id": 2` — [captura](persistencia-post-2.png) |

SQLite asigna ids crecientes: con una base que se conserva, el siguiente `id` continúa la
secuencia. Aquí la secuencia volvió a empezar en 1 después de una petición exitosa previa, así
que la base de datos se recreó entre las 22:53 y las 23:16. El segundo POST (`id` 2, 37 s
después) confirma que, mientras la instancia permanece activa, el historial se conserva.

## Conclusión

El historial no sobrevive a la inactividad o al reinicio del servicio en el plan gratuito de
Render: el almacenamiento es efímero y la base `data/verifacts.db` se pierde. Se acepta como
deuda, registrada en el [ADR-0008](../adr/0008-mantener-render-mitigar-arranque-frio.md).
Mitigaciones posibles: disco persistente de pago o migrar a PostgreSQL. El keep-alive reduce
las suspensiones por inactividad, pero no evita la pérdida en un redespliegue.

## Límites

1. No se hizo una prueba de reinicio ni de redespliegue manual desde el panel de Render.
2. No se aisló qué evento recreó la base entre las 22:53 y las 23:16: pudo ser la suspensión
   por inactividad (≈ 23 min, mayor que el umbral aproximado de 15 min del plan gratuito) o
   un redespliegue automático tras un push a `master`.
3. Una sola instancia y una sola observación, el 2026-10-10.
