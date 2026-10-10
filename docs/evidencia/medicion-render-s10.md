# Medición en Render — Reto operativo S10

Escenario: [Q-01 — Tiempo de respuesta](../escenarios-de-calidad.md#q-01--tiempo-de-respuesta-del-análisis).
Umbral: P95 ≤ 3.000 ms. Decisión asociada: [ADR-0008](../adr/0008-mantener-render-mitigar-arranque-frio.md).

## Manifiesto

| Campo | Valor |
|---|---|
| Sistema medido | https://verifacts-api.onrender.com (Render, plan gratuito; ver [costos](../costos.md)) |
| Payload | 10.000 caracteres, generado por `scripts/payload_10k.py` |
| Script | `scripts/medir_render.py` |
| Cliente | Windows-11-10.0.26200-SP0, Python 3.14.7, `httpx`, un cliente secuencial |
| Serie caliente | finalizada 2026-10-10T22:11:42Z, 50 corridas, tras una petición de calentamiento no registrada |
| Serie frío | finalizada 2026-10-10T22:53:09Z, 3 corridas, 20 minutos sin tráfico entre corridas |
| Commit desplegado | no registrado por el script |
| Series completas | [render_caliente.csv](render_caliente.csv) · [render_frio.csv](render_frio.csv) |

## Resultados en caliente (n = 50 por operación)

| Operación | Mediana (ms) | P95 (ms) | Máx (ms) | ¿P95 ≤ 3.000 ms? |
|---|---:|---:|---:|---|
| GET /health | 181,3 | 201,4 | 218,3 | — |
| POST /analysis | 197,1 | 211,3 | 505,2 | Sí |

## Resultados en frío (3 corridas)

| Corrida | Inactividad previa | GET /health (ms) | POST /analysis (ms) | Lectura |
|---|---|---:|---:|---|
| 1 | Ninguna (corrió justo después de la serie caliente) | 262,6 | 498,3 | Servicio despierto; no es una observación fría |
| 2 | 20 min | 22.515,6 | 237,5 | El GET fue la primera petición y despertó el servicio |
| 3 | 20 min | 22.348,0 | 214,3 | Ídem |

Con solo dos observaciones frías no se calcula un P95; se reporta el rango.
La primera petición tras 20 minutos sin tráfico tardó entre 22,3 y 22,5 s,
unas 7,5 veces el umbral de 3 s. Las peticiones siguientes volvieron a tiempos normales.

## Lectura

- **En caliente**, `POST /analysis` con 10.000 caracteres cumple Q-01 con un margen
  de unas 14 veces (P95 de 211,3 ms frente a 3.000 ms).
- **Tras inactividad**, la primera petición no cumple Q-01.
- La diferencia entre las medianas de POST y GET en caliente es de 15,8 ms. Esto es
  consistente con que la mayor parte del tiempo observado es red y plataforma, y no el
  análisis (interpretación; no se aisló ese componente).
- Referencia local (medición S9, otro entorno y sin red pública): P95 de 46,9 ms en
  [medicion-q01-q05.md](medicion-q01-q05.md). No es comparable uno a uno con esta serie.

## Límites de la medición

1. **Orden de las operaciones.** En cada corrida `GET /health` precede a `POST /analysis`,
   por lo que el POST nunca fue la primera petición tras la inactividad. No se midió un
   `POST /analysis` en frío directo. Se espera un costo similar porque el despertar es
   de la plataforma, pero eso es una inferencia.
2. **Pocas observaciones frías.** Hay 2 observaciones frías reales (la corrida 1 no lo fue).
3. **Una sola máquina y red cliente.** La latencia de red depende de esa ubicación.
4. **Instrumentación interna.** El middleware de `app/observability.py` empieza a medir cuando
   la petición ya entró a la aplicación, así que no ve el tiempo de despertar de la plataforma.
5. **Commit no registrado.** El script no guardó el hash desplegado; el despliegue sigue a `master`.
6. **Alcance.** En este corte no se midió AWS Lambda ni SAM. No se afirma ninguna
   comparación entre plataformas (ver ADR-0008).
