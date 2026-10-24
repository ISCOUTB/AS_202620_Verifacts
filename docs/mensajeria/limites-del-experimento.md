# Límites del experimento

Lo que el prototipo **demuestra** y lo que **no**. Lectura recomendada junto con
[ADR-0013](../adr/0013-no-incorporar-mensajeria-asincrona.md).

## Qué demuestra

- Un contrato versionado con criterio de compatibilidad ejecutable.
- Que, con entrega al menos una vez, un consumidor idempotente produce un único efecto ante publicación duplicada, mismo pedido con otro `message_id`, `ack` perdido y carrera entre consumidores.
- Reintento con backoff exponencial, DLQ con motivo y reproceso manual.
- Seguimiento de un mensaje por `message_id`/`correlation_id` y métricas de contadores.
- Que las pruebas detectan fallos reales: se mutó el código (sin deduplicación, backoff constante, fallo permanente tratado como recuperable, sin límite de intentos) y cada mutación hizo fallar al menos una prueba.

## Qué NO demuestra

1. **No es un broker real.** Vive en memoria, en un solo proceso y un solo hilo: sin red, sin persistencia ni reinicios del broker, sin concurrencia real. La rama de carrera entre consumidores se prueba **forzando** el chequeo previo con `monkeypatch`, no con hilos.
2. **El tiempo es simulado.** `ManualClock` salta al siguiente evento; no se midió latencia real, ni rendimiento, ni cuántos mensajes por segundo soporta.
3. **El jitter no está probado** (se usa 0 en las pruebas para que el backoff sea determinista).
4. **`extract_from_url()` real no está conectado.** Hoy lanza `ValueError` tanto si el sitio no responde como si el HTML no tiene texto, y no distingue fallo transitorio de permanente. Para usarlo habría que clasificar el error (p. ej. por código HTTP). El prototipo usa `ScriptedFetcher`.
5. **La clave de idempotencia identifica el pedido, no el contenido.** Si una página cambia, reenviar la misma URL devuelve el resultado ya guardado. En un sistema real haría falta una caducidad o incluir un hash del contenido.
6. **Sin orden, sin límite de tamaño de mensaje, sin autenticación entre productor y broker, sin política de retención de la DLQ.**
7. **No se midió el origen `url` del sistema real.** La decisión del ADR-0013 de no incorporar se apoya en esa ausencia de medición y define cuándo debe revisarse; no prueba que el origen `url` cumpla Q-01.
8. **Entornos distintos.** Las pruebas y la demo se ejecutaron en Windows con Python 3.14.7 (66 pruebas en verde en la suite completa); las mutaciones se ejecutaron en Linux con Python 3.12.3 y no se repitieron en Windows. El resultado en CI (Python 3.12) queda citado en la [evidencia](evidencia-ejecucion.md).
9. El prototipo no modifica `app/`, `data/verifacts.db`, `openapi.yaml` ni el frontend; `test_el_prototipo_esta_aislado_de_app` verifica que ningún archivo de `app/` lo importe.
