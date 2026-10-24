# Evidencia de ejecución — taller de mensajería asíncrona

- **Fecha:** 2026-10-23
- **Entorno de las pruebas y la demo:** Windows (`win32`), Python 3.14.7, pytest 9.1.1, ejecutado por el equipo en su máquina con el entorno virtual `.venv`
- **Entorno de las mutaciones (sección 3):** Linux, Python 3.12.3
- **Commit:** https://github.com/ISCOUTB/AS_202620_Verifacts/commit/86712bb8f4711f41900ead9fca12544ab10a8421

Cómo reproducir (CMD, desde la raíz del repositorio, con el entorno virtual activo):

```cmd
python -m pytest tests\test_messaging.py -v
python -m pytest -q
python -m experiments.messaging.demo
```

## 1. Pruebas del prototipo (`python -m pytest tests\test_messaging.py -v`)

```text
platform win32 -- Python 3.14.7, pytest-9.1.1, pluggy-1.6.0
collected 16 items

tests/test_messaging.py::test_contrato_ida_y_vuelta PASSED                                   [  6%]
tests/test_messaging.py::test_cambio_menor_con_campo_nuevo_sigue_siendo_compatible PASSED    [ 12%]
tests/test_messaging.py::test_cambio_mayor_va_a_dlq_sin_reintentos PASSED                    [ 18%]
tests/test_messaging.py::test_campo_obligatorio_ausente_es_error_de_contrato PASSED          [ 25%]
tests/test_messaging.py::test_publicacion_duplicada_produce_un_solo_efecto PASSED            [ 31%]
tests/test_messaging.py::test_mismo_pedido_con_otro_message_id_se_deduplica_por_clave_de_idempotencia PASSED [ 37%]
tests/test_messaging.py::test_carrera_entre_consumidores_no_duplica_el_efecto PASSED         [ 43%]
tests/test_messaging.py::test_ack_perdido_provoca_reentrega_y_el_efecto_sigue_siendo_uno PASSED [ 50%]
tests/test_messaging.py::test_politica_de_backoff_exponencial_con_tope PASSED                [ 56%]
tests/test_messaging.py::test_fallo_recuperable_se_recupera_con_backoff PASSED               [ 62%]
tests/test_messaging.py::test_reintentos_agotados_terminan_en_dlq_con_motivo PASSED          [ 68%]
tests/test_messaging.py::test_fallo_permanente_va_directo_a_dlq_sin_reintentar PASSED        [ 75%]
tests/test_messaging.py::test_mensaje_de_dlq_se_puede_reprocesar_tras_corregir_la_causa PASSED [ 81%]
tests/test_messaging.py::test_un_mensaje_se_sigue_de_productor_a_consumidor PASSED           [ 87%]
tests/test_messaging.py::test_el_prototipo_esta_aislado_de_app PASSED                        [ 93%]
tests/test_messaging.py::test_clave_de_idempotencia_coincide_con_el_fallback_de_mf05 PASSED  [100%]

================================ 16 passed in 4.50s ================================
```

## 2. Suite completa (`python -m pytest -q`)

```text
66 passed, 4 warnings in 4.99s
```

Las 4 advertencias son de dependencias (`fastapi/starlette` con `httpx` y `jsonschema.RefResolver`); ninguna proviene del prototipo. Las 50 pruebas previas del sistema siguen en verde, así que el prototipo no alteró el programa principal.

## 3. Prueba de que las pruebas detectan fallos (mutaciones)

Se alteró una línea del código del prototipo, se ejecutó `tests/test_messaging.py` y se restauró el archivo.

| Mutación | Resultado |
|---|---|
| Sin deduplicación (`INSERT OR REPLACE` y `exists()` siempre falso) | 3 pruebas fallan: publicación duplicada, mismo pedido con otro `message_id`, `ack` perdido |
| Backoff constante (`factor = 1.0`) | 1 prueba falla: `test_fallo_recuperable_se_recupera_con_backoff` |
| Fallo permanente tratado como recuperable | 2 pruebas fallan: fallo permanente directo a DLQ y reproceso desde la DLQ |
| Sin límite de intentos (nunca va a la DLQ) | La prueba falla por `RuntimeError` del guardia de bucle de `run_until_idle` |

## 4. Demostración reproducible (`python -m experiments.messaging.demo`)

Los identificadores cambian en cada ejecución (son UUID). Cada línea JSON es un evento de log; la última tabla es la traza de un solo mensaje.

```text
== 1. URL con 2 fallos recuperables (reintento con backoff 1 s, 2 s) ==
{"correlation_id": "a9c563d466ae493eaeb96ca12dfb4008", "event": "published", "message_id": "85d5a3aa7326438d816083d0e4a398c6", "ts": 0.0}
{"attempt": 1, "correlation_id": "a9c563d466ae493eaeb96ca12dfb4008", "event": "delivered", "message_id": "85d5a3aa7326438d816083d0e4a398c6", "ts": 0.0}
{"attempt": 1, "correlation_id": "a9c563d466ae493eaeb96ca12dfb4008", "delay_s": 1.0, "event": "retry_scheduled", "message_id": "85d5a3aa7326438d816083d0e4a398c6", "reason": "transient: timeout", "ts": 0.0}
{"attempt": 2, "correlation_id": "a9c563d466ae493eaeb96ca12dfb4008", "event": "delivered", "message_id": "85d5a3aa7326438d816083d0e4a398c6", "ts": 1.0}
{"attempt": 2, "correlation_id": "a9c563d466ae493eaeb96ca12dfb4008", "delay_s": 2.0, "event": "retry_scheduled", "message_id": "85d5a3aa7326438d816083d0e4a398c6", "reason": "transient: 503", "ts": 1.0}
{"attempt": 3, "correlation_id": "a9c563d466ae493eaeb96ca12dfb4008", "event": "delivered", "message_id": "85d5a3aa7326438d816083d0e4a398c6", "ts": 3.0}
{"attempt": 3, "classification": "Riesgo medio", "correlation_id": "a9c563d466ae493eaeb96ca12dfb4008", "e2e_s": 3.0, "event": "processed", "message_id": "85d5a3aa7326438d816083d0e4a398c6", "score": 50, "ts": 3.0}
== 2. Publicación duplicada del mismo mensaje (idempotencia) ==
{"correlation_id": "8151ed5fab58440baae69d67bb3507f1", "event": "published", "message_id": "a89fa8bbf8124ca1822d5f77d70eab11", "ts": 3.0}
{"correlation_id": "8151ed5fab58440baae69d67bb3507f1", "event": "published", "message_id": "a89fa8bbf8124ca1822d5f77d70eab11", "ts": 3.0}
{"attempt": 1, "correlation_id": "8151ed5fab58440baae69d67bb3507f1", "event": "delivered", "message_id": "a89fa8bbf8124ca1822d5f77d70eab11", "ts": 3.0}
{"attempt": 1, "classification": "Riesgo medio", "correlation_id": "8151ed5fab58440baae69d67bb3507f1", "e2e_s": 0.0, "event": "processed", "message_id": "a89fa8bbf8124ca1822d5f77d70eab11", "score": 50, "ts": 3.0}
{"attempt": 1, "correlation_id": "8151ed5fab58440baae69d67bb3507f1", "event": "delivered", "message_id": "a89fa8bbf8124ca1822d5f77d70eab11", "ts": 3.0}
{"attempt": 1, "correlation_id": "8151ed5fab58440baae69d67bb3507f1", "event": "duplicate_skipped", "message_id": "a89fa8bbf8124ca1822d5f77d70eab11", "ts": 3.0}
== 3. URL inexistente (404, fallo permanente -> DLQ sin reintentos) ==
{"correlation_id": "fd3fcd9ec122451e864ed0a1e0a3df73", "event": "published", "message_id": "15ff481200fa464aa6b9738c666ce316", "ts": 3.0}
{"attempt": 1, "correlation_id": "fd3fcd9ec122451e864ed0a1e0a3df73", "event": "delivered", "message_id": "15ff481200fa464aa6b9738c666ce316", "ts": 3.0}
{"attempt": 1, "correlation_id": "fd3fcd9ec122451e864ed0a1e0a3df73", "event": "dead_lettered", "message_id": "15ff481200fa464aa6b9738c666ce316", "reason": "permanent: 404", "ts": 3.0}
== 4. Mensaje con schema_version 2.0 (incompatible -> DLQ) ==
{"correlation_id": "c71c43c176674e79aff8ad26b0f66d1e", "event": "published", "message_id": "5fa89638e610424fbfcf905315662410", "ts": 3.0}
{"attempt": 1, "correlation_id": "c71c43c176674e79aff8ad26b0f66d1e", "event": "delivered", "message_id": "5fa89638e610424fbfcf905315662410", "ts": 3.0}
{"attempt": 1, "correlation_id": "c71c43c176674e79aff8ad26b0f66d1e", "event": "dead_lettered", "message_id": "5fa89638e610424fbfcf905315662410", "reason": "contract: schema_version 2.0 no compatible con v1", "ts": 3.0}

== Métricas ==
# TYPE verifacts_messaging_dead_lettered_total counter
verifacts_messaging_dead_lettered_total 2
# TYPE verifacts_messaging_delivered_total counter
verifacts_messaging_delivered_total 7
# TYPE verifacts_messaging_duplicates_skipped_total counter
verifacts_messaging_duplicates_skipped_total 1
# TYPE verifacts_messaging_processed_total counter
verifacts_messaging_processed_total 2
# TYPE verifacts_messaging_published_total counter
verifacts_messaging_published_total 5
# TYPE verifacts_messaging_retry_scheduled_total counter
verifacts_messaging_retry_scheduled_total 2
# TYPE verifacts_messaging_end_to_end_seconds summary
verifacts_messaging_end_to_end_seconds_count 2
verifacts_messaging_end_to_end_seconds_sum 3.000
verifacts_messaging_end_to_end_seconds_max 3.000

== DLQ ==
- 15ff4812… intentos=1 motivo=permanent: 404
- 5fa89638… intentos=1 motivo=contract: schema_version 2.0 no compatible con v1

== Traza del mensaje 85d5a3aa… ==
t=  0.0s  published
t=  0.0s  delivered
t=  0.0s  retry_scheduled
t=  1.0s  delivered
t=  1.0s  retry_scheduled
t=  3.0s  delivered
t=  3.0s  processed
```

### Cómo leer la evidencia

- **Fallo recuperable:** el mensaje `85d5a3aa…` falló con `timeout` y luego con `503`; se reprogramó con retrasos de 1 s y 2 s y se procesó en la tercera entrega, a los 3 s simulados (`e2e_s = 3.0`).
- **Duplicado:** el mensaje `a89fa8bb…` se publicó dos veces; hubo dos entregas, un `processed` y un `duplicate_skipped`. El resultado se guardó una sola vez.
- **Fallo permanente y contrato incompatible:** ambos van a la DLQ en el primer intento, sin reintentos, con su motivo.
- **Seguimiento:** filtrando por `message_id` (o `correlation_id`) se reconstruye el recorrido completo de un mensaje de productor a consumidor.
