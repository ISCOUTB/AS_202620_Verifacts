# arc42 — Sección 6: Vista de ejecución

Esta sección describe cómo colaboran los bloques en tiempo de ejecución para
escenarios concretos. En este incremento existen **dos** escenarios
ejecutables de extremo a extremo.

---

## 6.1 Escenario: Comprobación de disponibilidad (`GET /health`)

Ver también la guía de ejecución en el
[README](../../README.md#corte-vertical-ejecutable).

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
con `python -m pytest -q` y automáticamente en cada `push` mediante GitHub
Actions (`.github/workflows/tests.yml`). Ver la fila **A-00** en la
[tabla de aspectos](../aspectos.md) para la trazabilidad completa hasta la
evidencia de prueba.

### Nota de alcance

Este escenario **no** atraviesa los bloques `Content`, `Analysis` ni
`Scoring` — únicamente valida que el bloque `API` está operativo. Es el
corte más delgado posible, y sigue siendo útil como comprobación mínima de
que el servicio arranca, incluso ahora que existe el escenario 6.2.

---

## 6.2 Escenario: Análisis de contenido (`POST /analysis`)

Este es el **corte vertical completo** de este incremento: atraviesa
interfaz, lógica de negocio y persistencia.

### Precondición

El servidor se inició con `python run.py` (lo cual también inicializa la
base de datos SQLite mediante `initialize_database()`).

### Secuencia

```text
Usuario      API          Content      Analysis      Scoring      Persistencia
  |           |               |            |             |              |
  | POST      |               |            |             |              |
  | /analysis |               |            |             |              |
  |──────────▶|               |            |             |              |
  |           | normalize_    |            |             |              |
  |           | content(text) |            |             |              |
  |           |──────────────▶|            |             |              |
  |           |  contenido    |            |             |              |
  |           | normalizado   |            |             |              |
  |           |◀──────────────|            |             |              |
  |           | analyze_content(contenido) |             |              |
  |           |───────────────────────────▶|             |              |
  |           |            findings (List[Finding])      |              |
  |           |◀───────────────────────────|             |              |
  |           | calculate_score(findings) /              |              |
  |           | classify_score(score)                    |              |
  |           |──────────────────────────────────────────▶|              |
  |           |          score + classification           |              |
  |           |◀──────────────────────────────────────────|              |
  |           | save_analysis(content, score, classification, factors)  |
  |           |─────────────────────────────────────────────────────────▶|
  |           |                          id                              |
  |           |◀─────────────────────────────────────────────────────────|
  |◀──────────|                                                          |
  | 200 {id, score, classification, factors}                            |
```

1. El cliente envía `POST /analysis` con `{"text": "..."}`.
2. `create_analysis()` en `app/api/routes.py` recibe la solicitud, ya
   validada por el esquema `AnalysisRequest` (Pydantic).
3. Delega en `normalize_content()` (`app/modules/content/service.py`); si el
   texto queda vacío tras normalizar, se responde `400`.
4. Delega en `analyze_content()` (`app/modules/analysis/service.py`), que
   usa `RuleAnalyzer` para producir una lista de `Finding`.
5. Delega en `calculate_score()` y `classify_score()`
   (`app/modules/scoring/service.py`) para obtener la puntuación y la
   clasificación.
6. Delega en `save_analysis()` (`app/persistence/repository.py`), que
   inserta el registro en SQLite y devuelve su `id`.
7. `API` construye y retorna `AnalysisResponse` con `id`, `score`,
   `classification` y `factors`.

### Verificación automatizada

Este flujo está cubierto por `tests/test_analysis.py`, que valida tanto la
respuesta HTTP como que el registro quedó correctamente persistido (vía
`get_analysis()`). Ver la fila **A-03** en la
[tabla de aspectos](../aspectos.md).

### Nota de alcance

Este escenario todavía no cubre: extracción de contenido desde una URL,
analizadores NLP/ML, ni interfaz web — ver
[Sección 3.6 — Alcance de este incremento](03-contexto-y-alcance.md#36-alcance-de-este-incremento).
