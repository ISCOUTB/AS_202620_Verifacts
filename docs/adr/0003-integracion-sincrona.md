# ADR-0003: Mantener integración síncrona en las dos fronteras actuales

- Estado: Aceptado
- Fecha: 2026-09-15
- Decisor: Equipo VeriFacts

## Contexto

VeriFacts tiene hoy dos fronteras de integración reales:

1. **Frontend (React) ↔ API** — `fetch` síncrono sobre HTTP/JSON
   (`frontend/src/api/client.ts`), habilitado por `CORSMiddleware` en
   `app/main.py`.
2. **API ↔ sitio web externo** — cuando el usuario envía una `url` en
   `POST /analysis`, `extract_from_url()`
   (`app/modules/content/service.py`) llama a `trafilatura.fetch_url()` de
   forma síncrona y bloqueante, dentro del mismo ciclo de solicitud/
   respuesta que espera el usuario.

Ninguna de las dos fronteras usa colas de mensajes, webhooks ni un worker
en segundo plano. El escenario
[Q-01](../escenarios-de-calidad.md#q-01--tiempo-de-respuesta-del-análisis)
exige P95 ≤ 3s para el pipeline completo de análisis, y esa medición
(pendiente de formalizar) no distingue hoy entre origen `texto` (rápido,
sin red) y origen `url` (depende de la latencia del sitio externo).

## Decisión

Se mantiene una integración **síncrona** en ambas fronteras: cada
solicitud HTTP recibe su respuesta en el mismo ciclo, sin colas,
callbacks ni estado intermedio persistido.

## Alternativas consideradas

### Asíncrono con cola de trabajos (tarea en segundo plano + polling o WebSocket)

**Ventaja:** desacopla la disponibilidad del sitio externo de la
disponibilidad de VeriFacts; una URL lenta no retiene el hilo que atiende
otras solicitudes.

**Motivo del descarte:** exige diseñar un mecanismo de espera (polling o
notificación), un almacén de estado de trabajos ("pendiente" /
"completado" / "error"), y un cliente que sepa reflejar un análisis "en
progreso". Es complejidad adicional no justificada para el tamaño del
equipo y el alcance académico
([R-ORG-01, R-ORG-02, R-TEC-01](../arc42/02-restricciones.md)), y ningún
escenario actual exige tolerar una caída prolongada del sitio externo sin
que el usuario lo note de inmediato.

### Síncrono (elegido)

**Ventaja:** el usuario recibe el resultado — o el error — en la misma
respuesta HTTP; no hay estado intermedio que persistir ni sincronizar
entre backend y frontend; es coherente con el resto del monolito modular
([ADR-0001](0001-estilo-arquitectonico.md)), que ya evita comunicación de
red entre módulos internos.

**Decisión:** Seleccionado.

## Consecuencias positivas

- Un cliente que cumplía el contrato ayer lo sigue cumpliendo hoy sin
  cambios: no existe una segunda llamada de "consultar estado" que
  aprender ni versionar.
- El frontend no necesita lógica de sondeo (polling) ni de reconexión.
- Los tres flujos (`GET /health`, `POST /analysis`, `GET /analysis`)
  comparten el mismo modo de fallo: si el otro lado no responde, la
  solicitud falla de forma visible (error HTTP inmediato), no en
  silencio.

## Consecuencias negativas (riesgo aceptado)

- **El origen `url` puede violar Q-01.** Si el sitio externo tarda o no
  responde, `POST /analysis` con `url` bloquea hasta que
  `trafilatura.fetch_url()` retorne (éxito, error o timeout interno de la
  librería); esa latencia se suma directamente al P95 medido para Q-01,
  que hoy no distingue origen `texto` de origen `url`.
- Un pico de solicitudes con `url` hacia sitios lentos puede agotar los
  workers de Uvicorn antes que uno con solo `text`, porque cada solicitud
  `url` retiene su hilo/tarea por más tiempo.
- No hay reintento automático: si `trafilatura.fetch_url()` falla una
  vez, el usuario recibe `400` de inmediato y debe reintentar
  manualmente.

## Deuda aceptada

Se acepta que el pipeline de análisis por `url` puede tardar más que el
de `texto`, sin un mecanismo de aislamiento (timeout explícito, cola
separada o circuit breaker) todavía. Si la medición formal de Q-01
(pendiente, ver [docs/escenarios-de-calidad.md](../escenarios-de-calidad.md#q-01--tiempo-de-respuesta-del-análisis))
muestra que el origen `url` incumple el P95 ≤ 3s, este ADR deja de
aplicar para esa frontera específica y debe reemplazarse por uno que
introduzca procesamiento asíncrono solo para `extract_from_url()`, sin
tocar la frontera Frontend↔API.

## Escenarios relacionados

- [Q-01 — Tiempo de respuesta del análisis](../escenarios-de-calidad.md#q-01--tiempo-de-respuesta-del-análisis)
  — motiva directamente el riesgo aceptado arriba.
- [Q-05 — Repetibilidad del resultado](../escenarios-de-calidad.md#q-05--repetibilidad-del-resultado)
  — una integración síncrona sin estado intermedio facilita que la misma
  entrada produzca el mismo resultado de forma predecible.

## Verificación del contrato

El contrato HTTP de ambas fronteras está especificado en
[docs/contracts/openapi.yaml](../contracts/openapi.yaml) (versión
`1.0.0`) y verificado en cada `push` por `tests/test_contract.py`. Un
cambio incompatible (renombrar un campo de la respuesta, cambiar su tipo,
o envolver en un objeto un cuerpo que hoy es un arreglo plano) rompe ese
pipeline antes de llegar al frontend — ver la fila **A-05** en la
[tabla de aspectos](../aspectos.md).

## Estado

Aceptado.

Si en el futuro se introduce procesamiento asíncrono para alguna
frontera, deberá crearse un nuevo ADR en lugar de modificar este
documento.
