# arc42 — Sección 6: Vista de ejecución

Esta sección describe cómo colaboran los bloques en tiempo de ejecución para
escenarios concretos. En este incremento existen **tres** escenarios
ejecutables de extremo a extremo sobre el backend, más la interfaz web que
los consume a todos.

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

1. El cliente (navegador, `curl`, `TestClient`, o el indicador de conexión
   del frontend) envía `GET /health`.
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
que el servicio arranca.

---

## 6.2 Escenario: Análisis de contenido (`POST /analysis`)

Este es el **corte vertical completo** de análisis: atraviesa interfaz,
lógica de negocio y persistencia.

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
  | 200 {id, score, classification, factors, created_at}                |
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
   inserta el registro en SQLite (con marca de tiempo `created_at`) y
   devuelve su `id`.
7. `API` construye y retorna `AnalysisResponse` con `id`, `score`,
   `classification`, `factors` y `created_at`.

### Verificación automatizada

Este flujo está cubierto por `tests/test_analysis.py`, que valida tanto la
respuesta HTTP como que el registro quedó correctamente persistido (vía
`get_analysis()`). Ver la fila **A-03** en la
[tabla de aspectos](../aspectos.md).

### Nota de alcance

Este escenario todavía no cubre: extracción de contenido desde una URL, ni
analizadores NLP/ML — ver
[Sección 3.6 — Alcance de este incremento](03-contexto-y-alcance.md#36-alcance-de-este-incremento).

---

## 6.3 Escenario: Consulta de historial (`GET /analysis`, `GET /analysis/{id}`)

### Precondición

El servidor se inició con `python run.py`. Existen cero o más análisis
guardados de ejecuciones anteriores del escenario 6.2.

### Secuencia (listado paginado)

```text
Usuario      API                          Persistencia
  |           |                                |
  | GET /analysis?limit=8&offset=0             |
  |──────────▶|                                |
  |           | list_analyses(limit, offset)   |
  |           |───────────────────────────────▶|
  |           |     filas (más recientes primero) |
  |           |◀───────────────────────────────|
  |           | count_analyses()               |
  |           |───────────────────────────────▶|
  |           |              total              |
  |           |◀───────────────────────────────|
  |◀──────────|                                |
  | 200 {total, limit, offset, items[]}         |
```

1. El cliente (la pestaña "Historial" del frontend, o `curl`) envía
   `GET /analysis` con `limit` y `offset` opcionales (`Query`, validados
   entre 1–100 y ≥0 respectivamente).
2. `read_analyses()` en `app/api/routes.py` delega en `list_analyses()` y
   `count_analyses()` (`app/persistence/repository.py`).
3. `API` retorna `AnalysisListResponse` con el total disponible (para que el
   cliente calcule la paginación) y los elementos de la página actual,
   ordenados por `id` descendente (más recientes primero).

Para un análisis puntual, `GET /analysis/{id}` delega directamente en
`get_analysis()` y responde `404` si el `id` no existe — usado por el
frontend al expandir una fila del historial.

### Verificación automatizada

Este flujo está cubierto por `tests/test_history.py`: crea un análisis,
confirma que aparece en el listado paginado, recupera su detalle por `id`, y
confirma `404` ante un `id` inexistente. Ver la fila **A-04** en la
[tabla de aspectos](../aspectos.md).

### Nota de alcance

`list_analyses()` no filtra por contenido ni por rango de fechas todavía —
solo pagina por `id` descendente. Un filtro de búsqueda queda fuera del
alcance de este incremento.

---

## 6.4 La interfaz web como cliente de los tres escenarios

La interfaz web (`frontend/`) no introduce un cuarto flujo de negocio: es un
cliente HTTP de los tres escenarios anteriores (`frontend/src/api/client.ts`).
El indicador de conexión llama a 6.1 al cargar y cada 20 segundos; el
formulario de análisis llama a 6.2 al enviarse; la pestaña de historial
llama a 6.3 al abrirse y al paginar. El backend habilita esta comunicación
entre orígenes distintos (`localhost:5173` → `127.0.0.1:8000`) mediante
`CORSMiddleware` en `app/main.py`. Ver
[C4 — Contenedores](../c4/02-contenedores.md) para la vista de despliegue de
ambos contenedores.
