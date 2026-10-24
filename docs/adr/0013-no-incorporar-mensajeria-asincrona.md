# ADR-0013: No incorporar mensajería asíncrona; mantener síncrona la extracción de URL y conservar un prototipo aislado

- Estado: Aceptado
- Fecha: 2026-10-23
- Decisor: Equipo VeriFacts

## Contexto

El taller pide elegir una operación real con desacoplamiento temporal, reintento
o procesamiento en segundo plano. Se evaluaron cuatro candidatas:

| Candidata | ¿Justifica una cola? | Motivo |
|---|---|---|
| `POST /analysis` con `text` | No | P95 = 46,9 ms con 10.000 caracteres ([medición S9](../evidencia/medicion-q01-q05.md)); sin red externa. |
| Escritura en SQLite (`save_analysis`) | No | Local y atómica; su riesgo (MF-04) se mitiga con WAL y reintento en proceso. |
| Entrenamiento del modelo ML | No | Se ejecuta por script fuera de línea, no en el flujo de una petición. |
| **`POST /analysis` con `url`** (`extract_from_url`) | **Candidata** | Única operación con red externa: fallos transitorios (MF-01) y permanentes (MF-02), y el [ADR-0003](0003-integracion-sincrona.md) dejó escrito que se reconsideraría aquí. |

Sobre la candidata hay un hecho que condiciona la decisión: **el origen `url` no
está medido**. La medición S9 excluye `url` expresamente, y no existen hoy el
timeout (MF-01) ni la idempotencia (MF-05). Es decir, no hay evidencia de que
el origen `url` incumpla [Q-01](../escenarios-de-calidad.md#q-01--tiempo-de-respuesta-del-análisis).

Para verificar las propiedades sin comprometer el sistema se construyó un
prototipo aislado en `experiments/messaging/` (simulador en memoria): contrato
versionado, entrega al menos una vez, consumidor idempotente, backoff, DLQ y
trazas. Ver [contrato](../mensajeria/contrato-mensaje.md) y
[evidencia](../mensajeria/evidencia-ejecucion.md).

## Decisión

1. **No se incorpora** un broker, cola ni worker al sistema. `extract_from_url()` sigue síncrono.
2. El prototipo **se conserva aislado** (`experiments/`, ningún módulo de `app/` lo importa; lo comprueba una prueba) como evidencia de viabilidad y base si se cumplen los disparadores.
3. Las dos propiedades que más valor aportan se implementan **de forma síncrona** primero: timeout estricto (MF-01) e idempotencia por `Idempotency-Key` o hash del contenido (MF-05).
4. Se fijan **disparadores de reevaluación** (más abajo).

## Alternativas consideradas

### Síncrona con timeout e idempotencia (elegida)

El usuario recibe resultado o error en la misma respuesta; no hay estado
intermedio; el contrato `openapi.yaml` 1.0.0 no cambia.

### Asíncrona con cola y worker (descartada por ahora)

Probada en el prototipo. Comparación:

| Criterio | Síncrona + MF-01/MF-05 | Asíncrona con cola |
|---|---|---|
| Contrato HTTP | Sin cambios (1.0.0, `test_contract.py` intacto) | `POST` deja de devolver el resultado: hace falta un estado de trabajo y una operación de consulta; cambia el contrato y sus pruebas |
| Q-01 con `text` | Cumple (46,9 ms) | Cumple, pero añade un salto sin necesidad |
| Q-01 con `url` | Acotado por el timeout; el timeout de 4 s previsto en MF-01 **ya supera** los 3 s, así que un sitio lento falla rápido en vez de cumplir | Responde de inmediato, pero el análisis termina después: **Q-01 habría que redefinirlo** para `url` (hoy mide hasta "presenta el resultado") |
| Duplicados | `Idempotency-Key` + tabla transaccional local | Consumidor idempotente + deduplicación (probado en el prototipo); la clave es necesaria en ambos casos |
| Fallo recuperable | Reintento manual del usuario o un reintento corto dentro del presupuesto de tiempo | Reintentos automáticos con backoff y DLQ (probado) |
| Visibilidad del fallo | Inmediata (error HTTP) | Diferida (hay que consultar estado o la DLQ) |
| Consistencia | Lee lo que escribe tras el `POST` ([arc42 §8.6](../arc42/08-conceptos-transversales.md#86-consistencia-de-datos)) | Eventual: la consulta inmediata puede no encontrar resultado |
| Piezas nuevas | Ninguna | Broker o worker + almacén de estado + manejo de DLQ; un servicio más en el compose del laboratorio, con el límite de [R-TEC-05](../arc42/02-restricciones.md) (sin tarjeta) y un equipo de dos personas |
| Reversibilidad | Alta | Baja una vez que los clientes dependen del flujo asíncrono |

### A lo sumo una vez / exactamente una vez

Descartadas como garantía de transporte; razones en el
[contrato](../mensajeria/contrato-mensaje.md#4-garantía-de-entrega-elegida-al-menos-una-vez).

## Consecuencias positivas

- Se conserva el contrato, el frontend y las pruebas de contrato existentes.
- El equipo dispone de un diseño ya probado (contrato, idempotencia, reintentos, trazas) si deja de ser opcional.
- Las mitigaciones síncronas (MF-01, MF-05) son un paso necesario en cualquier caso: la asíncrona también necesita la clave de idempotencia.

## Consecuencias negativas (riesgo aceptado)

- **El riesgo del [ADR-0003](0003-integracion-sincrona.md) sigue vigente**: una URL lenta retiene un hilo de Uvicorn y un pico de peticiones `url` puede agotar los workers.
- Mientras no se implementen MF-01 y MF-05, un fallo de red sigue devolviendo 400 sin reintento y un reenvío crea un registro duplicado.
- El prototipo puede desactualizarse respecto a `app/` (no está conectado a `extract_from_url()` real; ver [límites](../mensajeria/limites-del-experimento.md)).

## Deuda aceptada

Medir el origen `url` (script análogo a `scripts/medir_q01_q05.py`, con sitios de
prueba controlados) para sustentar con datos la decisión de no incorporar. Hasta
entonces, este ADR se basa en la **ausencia de evidencia** de incumplimiento, no
en evidencia de cumplimiento.

## Disparadores de reevaluación

Este ADR se reemplaza por uno nuevo si ocurre alguna de estas condiciones (los
umbrales numéricos son una propuesta a validar por el equipo):

1. La medición del origen `url` da P95 > 3.000 ms con timeout aplicado, o más de un 5 % de fallos transitorios en las URL de prueba.
2. Una prueba de carga con peticiones `url` agota los workers de Uvicorn.
3. Aparece un caso de uso por lotes (analizar una lista de URLs) o un segundo consumidor (por ejemplo, `MLAnalyzer` en otro proceso; ver [ADR-0009](0009-decision-extraccion-modulo-analisis.md)).

## Escenarios relacionados

- [Q-01 — Tiempo de respuesta del análisis](../escenarios-de-calidad.md#q-01--tiempo-de-respuesta-del-análisis)
- [Q-05 — Repetibilidad del resultado](../escenarios-de-calidad.md#q-05--repetibilidad-del-resultado)

## Estado

Aceptado. Complementa al [ADR-0003](0003-integracion-sincrona.md) con una
adenda fechada; no lo reemplaza.
