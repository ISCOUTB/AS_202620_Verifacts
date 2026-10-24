# Contrato del mensaje `verifacts.analysis.requested` (v1.0)

Prototipo aislado del taller de mensajería asíncrona. La decisión de **no**
incorporarlo al sistema está en [ADR-0013](../adr/0013-no-incorporar-mensajeria-asincrona.md).
Código: `experiments/messaging/contract.py`. Pruebas: `tests/test_messaging.py`.

## 1. Operación candidata

**Extracción y análisis de una URL** (`POST /analysis` con `url`):
`extract_from_url()` descarga el sitio de forma síncrona
([ADR-0003](../adr/0003-integracion-sincrona.md)). Es la única operación del
sistema con red externa, y por tanto la única con fallos transitorios reales
(MF-01 y MF-02 de la [entrega S11](../entregas/entrega-modos-fallo-idempotencia-adr.md)).
El mensaje modela "pedir que se analice esta fuente" desacoplando al productor
(API) del consumidor (worker).

## 2. Esquema

| Campo | Tipo | Obligatorio | Significado |
|---|---|---|---|
| `type` | texto | informativo | Siempre `verifacts.analysis.requested`; no se valida. |
| `schema_version` | texto `MAJOR.MINOR` | sí | Versión del contrato. Hoy `1.0`. |
| `message_id` | texto (UUID hex) | sí | Identifica **este envío**. Cambia en cada publicación. |
| `correlation_id` | texto (UUID hex) | sí | Identifica **la petición del usuario**; se conserva entre reintentos y logs. |
| `idempotency_key` | texto (SHA-256 hex) | sí | `SHA-256(source_type + "::" + fuente normalizada)`. Identifica **el pedido**; es la base de la deduplicación. |
| `source_type` | `"url"` \| `"texto"` | sí | Origen de la fuente. |
| `source` | texto | sí | La URL o el texto a analizar. |
| `produced_at` | texto ISO-8601 UTC | sí | Instante de producción. |

Ejemplo:

```json
{
  "type": "verifacts.analysis.requested",
  "schema_version": "1.0",
  "message_id": "75c8d23149d8457286b0bc82387d65d3",
  "correlation_id": "da2d89a477464cc09931f0274a2eab7f",
  "idempotency_key": "<sha256 de url::https://ejemplo.test/lento>",
  "source_type": "url",
  "source": "https://ejemplo.test/lento",
  "produced_at": "2026-10-23T15:04:05+00:00"
}
```

`message_id` y `idempotency_key` son distintos a propósito: dos publicaciones
del mismo pedido (reintento del productor, doble clic del usuario) tienen
distinto `message_id` pero la misma `idempotency_key`.

## 3. Criterio de compatibilidad

| Cambio | Clasificación | Qué se hace |
|---|---|---|
| Agregar un campo **opcional** | Compatible → sube MINOR (`1.0` → `1.1`) | Los consumidores v1 lo ignoran (lector tolerante). Probado: `test_cambio_menor_con_campo_nuevo_sigue_siendo_compatible`. |
| Quitar o renombrar un campo, cambiar su tipo o su significado, volver obligatorio uno opcional | **Incompatible** → sube MAJOR (`2.0`) | Se publica en una cola nueva `analysis.requested.v2`; v1 se drena en paralelo y luego se retira. |
| Mensaje con MAJOR distinto al que entiende el consumidor | Rechazo | A la DLQ **sin reintentos** (reintentar no lo arregla). Probado: `test_cambio_mayor_va_a_dlq_sin_reintentos`. |
| Falta un campo obligatorio o el JSON es inválido | Rechazo | Igual: DLQ directa con motivo `contract: ...`. |

Orden de despliegue ante un cambio compatible: primero los **consumidores**
(que ya toleran campos extra), luego el productor.

## 4. Garantía de entrega elegida: al menos una vez

| Alternativa | Decisión | Motivo |
|---|---|---|
| A lo sumo una vez | Descartada | Un fallo del worker perdería análisis en silencio: el usuario nunca recibiría resultado ni error. |
| **Al menos una vez** | **Elegida** | No se pierde ninguna petición; es lo que ofrecen RabbitMQ (ack manual) y los servicios administrados por defecto. |
| Exactamente una vez | Descartada como garantía de transporte | Exige transacciones broker+base de datos; se logra el mismo **efecto** con idempotencia (sección 5). |

**Consecuencias asumidas** (cada una tiene prueba o está declarada en [límites](limites-del-experimento.md)):

1. **Habrá duplicados**: publicación repetida y reentrega tras `ack` perdido. → el consumidor debe ser idempotente.
2. **No hay orden global**: un reintento puede terminar después de un mensaje posterior. El contrato no depende del orden.
3. **La latencia crece con los fallos**: con la política de la sección 6, un mensaje que se agota espera 1 + 2 + 4 = 7 s de backoff antes de ir a la DLQ (más el tiempo de cada intento).
4. **El error es diferido**: el usuario no lo ve en la misma respuesta HTTP (ver [ADR-0013](../adr/0013-no-incorporar-mensajeria-asincrona.md)).

## 5. Duplicados: consumidor idempotente

El resultado se guarda en `async_results` con `idempotency_key` como **clave primaria**
y se inserta con `INSERT OR IGNORE`: la deduplicación y el efecto ocurren en la
misma sentencia atómica de SQLite.

1. Si la clave ya existe → `duplicate_skipped`, `ack`, sin recalcular.
2. Si no existe → fetch, normalizar, analizar, puntuar e insertar.
3. Si entre (1) y (2) otro consumidor insertó primero → el `INSERT OR IGNORE` no inserta, se cuenta como `duplicate_skipped`.

El prototipo usa su propio almacén (`async_results`), **no** la tabla `analyses`
ni `data/verifacts.db`. Es la misma idea que el diseño MF-05 de la entrega S11
(clave `Idempotency-Key` o SHA-256 del contenido), con una tabla más simple porque
el consumidor, a diferencia de una API HTTP, no necesita guardar el cuerpo de respuesta.

## 6. Reintentos, backoff y mensajes fallidos

| Parámetro | Valor | Nota |
|---|---|---|
| `max_attempts` | 4 entregas por mensaje | Incluye la primera. |
| Backoff | `min(30 s, 1 s × 2^(intento−1))` → 1 s, 2 s, 4 s | Exponencial con tope. |
| Jitter | 0 en pruebas (determinismo); ±20 % recomendado fuera de pruebas | Parámetro `jitter` de `RetryPolicy`; **no** se prueba con valor distinto de 0. |
| `visibility_timeout` | 30 s simulados | Sin `ack` en ese plazo, el broker reentrega. |

Clasificación de fallos:

| Fallo | Tratamiento | Prueba |
|---|---|---|
| Transitorio (`TransientFetchError`: timeout, 5xx) y excepciones desconocidas | `nack` → reintento con backoff; al agotar intentos → DLQ con `retries_exhausted: ...` | `test_fallo_recuperable_se_recupera_con_backoff`, `test_reintentos_agotados_terminan_en_dlq_con_motivo` |
| Permanente (`PermanentFetchError`: 404, 403 anti-bot) y contenido vacío | DLQ directa, 1 intento | `test_fallo_permanente_va_directo_a_dlq_sin_reintentar` |
| Mensaje venenoso (contrato inválido o MAJOR incompatible) | DLQ directa, 1 intento | `test_cambio_mayor_va_a_dlq_sin_reintentos` |

La DLQ conserva el mensaje original, el número de intentos y el motivo.
`redrive_dlq()` devuelve todo a la cola principal tras corregir la causa
(`test_mensaje_de_dlq_se_puede_reprocesar_tras_corregir_la_causa`).

## 7. Seguimiento de un mensaje (log y métricas)

Todos los eventos son JSON con `ts`, `event`, `message_id` y `correlation_id`.
Filtrando por `message_id` se obtiene el recorrido completo:

| Evento | Lo emite | Campos extra |
|---|---|---|
| `published` | productor/broker | — |
| `delivered` | broker | `attempt` |
| `retry_scheduled` | broker | `attempt`, `delay_s`, `reason` |
| `redelivery_after_timeout` | broker | `attempt` |
| `ack_lost` | broker (fallo inyectado) | — |
| `duplicate_skipped` | consumidor | `attempt` |
| `processed` | consumidor | `attempt`, `score`, `classification`, `e2e_s` |
| `dead_lettered` | broker | `attempt`, `reason` |
| `redriven` | operación manual | — |

Contadores (formato de texto Prometheus, igual que `/metrics` de la API):
`published`, `delivered`, `processed`, `duplicates_skipped`, `retry_scheduled`,
`redelivered_after_timeout`, `dead_lettered`, más el resumen
`end_to_end_seconds` (cuenta, suma y máximo entre publicación y procesamiento).
Prueba: `test_un_mensaje_se_sigue_de_productor_a_consumidor`.

## 8. Equivalencia con un broker real (no verificada)

| En el simulador | En RabbitMQ (referencia, **no probado aquí**) |
|---|---|
| `poll` + `ack` | Consumo con `ack` manual |
| `nack` con backoff | Colas de reintento con TTL + dead-letter exchange |
| DLQ | Dead-letter exchange / cola `.dlq` |
| `visibility_timeout` | Reentrega al cerrarse el canal sin ack |
