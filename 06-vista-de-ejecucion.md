# arc42 — Sección 6: Vista de ejecución

Esta sección describe cómo colaboran los bloques en tiempo de ejecución para
escenarios concretos. En este incremento solo existe un escenario ejecutable
de extremo a extremo: la comprobación de disponibilidad.

---

## 6.1 Escenario: Comprobación de disponibilidad (`GET /health`)

Este es el **corte vertical ejecutable** de este incremento — ver también la
guía de ejecución en el [README](../../README.md#corte-vertical-ejecutable).

### Precondición

El servidor se inició con `python run.py` y está escuchando en
`http://127.0.0.1:8000`.

### Secuencia

```text
Usuario/Cliente          API (app/api/routes.py)
      |                            |
      |  GET /health               |
      |───────────────────────────▶|
      |                            | construye {"status": "ok"}
      |                            |
      |   200 OK                   |
      |◀───────────────────────────|
      |  {"status": "ok"}          |
```

1. El cliente (navegador, `curl`, o `TestClient` en las pruebas) envía
   `GET /health`.
2. FastAPI enruta la solicitud a `health_check()` en `app/api/routes.py`.
3. La función construye y retorna el diccionario `{"status": "ok"}`.
4. FastAPI lo serializa como JSON y responde con código `200`.

### Verificación automatizada

Este flujo está cubierto por `tests/test_health.py`, ejecutado localmente
con `pytest -q` y automáticamente en cada `push` mediante GitHub Actions
(`.github/workflows/tests.yml`). Ver la fila **A-00** en la
[tabla de aspectos](../aspectos.md) para la trazabilidad completa hasta la
evidencia de prueba.

### Nota de alcance

Este escenario **no** atraviesa los bloques `Content`, `Analysis` ni
`Scoring` — únicamente valida que el bloque `API` está operativo. Es
intencionalmente el corte más delgado posible: demuestra que el esqueleto
arranca, responde y está verificado por una prueba automatizada antes de
construir la lógica de negocio sobre él.

---

## 6.2 Escenario previsto: Análisis de contenido (pendiente de implementación)

Se documenta aquí como referencia para el siguiente incremento, una vez que
`Content`, `Analysis` y `Scoring` tengan lógica implementada.

```text
Usuario      API      Content      Analysis      Scoring
  |           |           |            |             |
  | POST      |           |            |             |
  | /analysis |           |            |             |
  |──────────▶|           |            |             |
  |           | normaliza |            |             |
  |           |──────────▶|            |             |
  |           |           | contenido  |             |
  |           |           |───────────▶|             |
  |           |           |            | hallazgos   |
  |           |           |            |────────────▶|
  |           |           |            |             | puntuación +
  |           |           |            |             | clasificación
  |           |◀──────────────────────────────────────|
  |◀──────────|           |            |             |
  | resultado |           |            |             |
```

Este escenario corresponde a los objetivos arquitectónicos descritos en la
[Sección 1](01-introduccion-y-objetivos.md#16-objetivos-arquitectónicos) y no
forma parte del corte vertical actual.
