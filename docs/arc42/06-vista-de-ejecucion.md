# arc42 — Sección 6: Vista de ejecución

Esta sección describe cómo colaboran los bloques en tiempo de ejecución para
escenarios concretos. En este incremento existen **tres** escenarios
ejecutables de extremo a extremo sobre el backend, más la interfaz web que
los consume a todos, y un contrato ejecutable que los describe formalmente
(S7).

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
lógica de negocio y persistencia. Acepta dos orígenes mutuamente
excluyentes — `text` o `url` — validados por
`AnalysisRequest.check_exactly_one_source()` antes de llegar a `Content`.

### Precondición

El servidor se inició con `python run.py` (lo cual también inicializa la
base de datos SQLite mediante `initialize_database()`).

### Secuencia (origen `text`)

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
  |           | save_analysis(content, score, classification, factors,  |
  |           | source_type)                                            |
  |           |─────────────────────────────────────────────────────────▶|
  |           |                          id                              |
  |           |◀─────────────────────────────────────────────────────────|
  |◀──────────|                                                          |
  | 200 {id, score, classification, factors, source_type, created_at}   |
```

1. El cliente envía `POST /analysis` con `{"text": "..."}` o
   `{"url": "..."}` (nunca ambos).
2. `create_analysis()` en `app/api/routes.py` recibe la solicitud, ya
   validada por el esquema `AnalysisRequest` (Pydantic): exactamente un
   origen presente, o `422` antes de tocar ningún módulo interno.
3. Si el origen es `url`, delega primero en `extract_from_url()`
   (`app/modules/content/service.py`, vía `trafilatura`); si la descarga
   o la extracción fallan, responde `400` sin llegar a `normalize_content`.
   Si el origen es `text` (o ya se extrajo desde una `url`), delega en
   `normalize_content()`; si el texto queda vacío tras normalizar,
   responde `400`. **Nota:** con `text`, un valor solo de espacios en
   blanco nunca llega a esta función: `check_exactly_one_source` ya lo
   trata como ausente y corta con `422` un paso antes (ver
   `tests/test_contract.py::test_post_analysis_whitespace_only_text_returns_422`).
4. Delega en `analyze_content()` (`app/modules/analysis/service.py`), que
   usa `RuleAnalyzer` para producir una lista de `Finding`.
5. Delega en `calculate_score()` y `classify_score()`
   (`app/modules/scoring/service.py`) para obtener la puntuación y la
   clasificación.
6. Delega en `save_analysis()` (`app/persistence/repository.py`), que
   inserta el registro en SQLite (con `source_type` y marca de tiempo
   `created_at`) y devuelve su `id`.
7. `API` construye y retorna `AnalysisResponse` con `id`, `score`,
   `classification`, `factors`, `source_type` y `created_at`.

### Verificación automatizada

Este flujo está cubierto por `tests/test_analysis.py`, que valida tanto la
respuesta HTTP como que el registro quedó correctamente persistido (vía
`get_analysis()`). El contrato exacto de la respuesta (tipos, campos
obligatorios, valores permitidos de `classification` y `source_type`) está
verificado además por `tests/test_contract.py`. Ver las filas **A-03** y
**A-05** en la [tabla de aspectos](../aspectos.md).

### Nota de alcance

Este escenario todavía no cubre analizadores NLP/ML — solo `RuleAnalyzer`
(ver [Registro de uso de IA](../ia.md)). La extracción de contenido desde
una `url` **sí** está implementada (`app/modules/content/service.py`, vía
`trafilatura`); una versión anterior de esta sección la listaba como
pendiente, lo cual ya no era cierto — corregido en S7 junto con el resto
del contrato.

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
  | 200 [AnalysisSummary, ...]                  |
  | Header: X-Total-Count: <total>              |
```

1. El cliente (la pestaña "Historial" del frontend, o `curl`) envía
   `GET /analysis` con `limit` y `offset` opcionales (`Query`, validados
   entre 1–100 y ≥0 respectivamente; fuera de rango responde `400`).
2. `read_analyses()` en `app/api/routes.py` delega en `list_analyses()` y
   `count_analyses()` (`app/persistence/repository.py`).
3. `API` retorna el cuerpo como un **arreglo plano** de `AnalysisSummary`
   (no un objeto envoltorio), ordenado por `id` descendente (más
   recientes primero). El total disponible para paginar viaja en la
   cabecera HTTP `X-Total-Count`, **no** dentro del cuerpo — así lo
   consume `frontend/src/api/client.ts` (`fetchAnalysisList()`) y así lo
   fija `docs/contracts/openapi.yaml`.

   > **Corrección S7:** esta sección describía antes un cuerpo envoltorio
   > `{total, limit, offset, items[]}` que el código nunca implementó. El
   > frontend siempre asumió el arreglo plano + cabecera; era la
   > documentación, no el código, la que estaba desactualizada. Es
   > exactamente el tipo de desajuste silencioso que
   > `tests/test_contract.py::test_list_analysis_body_is_flat_array_matching_contract`
   > ahora detecta automáticamente en cada `push`.

Para un análisis puntual, `GET /analysis/{id}` delega directamente en
`get_analysis()` y responde `404` si el `id` no existe — usado por el
frontend al expandir una fila del historial.

### Verificación automatizada

Este flujo está cubierto por `tests/test_analysis_history.py`: crea un
análisis, confirma que aparece en el listado, recupera su detalle por
`id`, y confirma `404` ante un `id` inexistente. La forma exacta del
cuerpo (arreglo plano) y de la cabecera `X-Total-Count` están verificadas
además por `tests/test_contract.py`. Ver las filas **A-04** y **A-05** en
la [tabla de aspectos](../aspectos.md).

### Nota de alcance

`list_analyses()` no filtra por contenido ni por rango de fechas todavía —
solo pagina por `id` descendente. Un filtro de búsqueda queda fuera del
alcance de este incremento.

---

## 6.4 La interfaz web como cliente de los tres escenarios

La interfaz web (`frontend/`) no introduce un cuarto flujo de negocio: es un
cliente HTTP de los tres escenarios anteriores (`frontend/src/api/client.ts`).
El indicador de conexión llama a 6.1 al cargar y cada 20 segundos; el
formulario de análisis llama a 6.2 al enviarse (con el toggle Texto/URL); la
pestaña de historial llama a 6.3 al abrirse y al paginar. El backend habilita
esta comunicación entre orígenes distintos (`localhost:5173` →
`127.0.0.1:8000`) mediante `CORSMiddleware` en `app/main.py`. Ver
[C4 — Contenedores](../c4/02-contenedores.md) para la vista de despliegue de
ambos contenedores, y [ADR-0003](../adr/0003-integracion-sincrona.md) para
la justificación de mantener ambas fronteras síncronas.

---

## 6.5 Contrato de la API y prueba de contrato (S7)

Los tres escenarios anteriores comparten una única fuente de verdad sobre su
forma: [docs/contracts/openapi.yaml](../contracts/openapi.yaml) (OpenAPI
3.1, versión `1.0.0`).

### Qué verifica `tests/test_contract.py`

- Que cada respuesta real de `GET /health`, `POST /analysis`,
  `GET /analysis` y `GET /analysis/{id}` cumple el esquema declarado en el
  contrato (campos obligatorios, tipos, valores permitidos de
  `classification` y `source_type`).
- Que `GET /analysis` responde con un arreglo plano y expone el total vía
  `X-Total-Count`, no con un objeto envoltorio (ver 6.3).
- Que los códigos de estado (`200`, `400`, `404`, `422`) coinciden con los
  declarados para cada operación.

Esta prueba corre en el mismo pipeline que el resto de `tests/`
(`.github/workflows/tests.yml`), así que un cambio incompatible en la API
rompe el `push` o el `pull request` antes de llegar a `master` — no
depende de que alguien lo note manualmente en el frontend.

### Comprobación de que detecta un cambio incompatible

Se verificó manualmente que renombrar el campo `score` a `risk_score` en
`AnalysisResponse`/`AnalysisSummary` (`app/api/routes.py`) hace fallar
`tests/test_contract.py` (4 pruebas), porque `AnalysisSummary(**result)`
ya no puede construirse a partir de las columnas reales de
`app/persistence/repository.py`. Revertido el cambio, las 20 pruebas del
proyecto vuelven a pasar. Ver
[ADR-0003](../adr/0003-integracion-sincrona.md) para la decisión de
integración que este contrato formaliza, y la fila **A-05** en la
[tabla de aspectos](../aspectos.md) para la evidencia completa.
