# arc42 — Sección 8: Conceptos transversales

Esta sección reúne decisiones y convenciones que aplican a **varios**
módulos a la vez, en lugar de pertenecer a uno solo.

## 8.1 Validación de entrada

Toda solicitud HTTP se valida mediante modelos Pydantic (`AnalysisRequest`,
`AnalysisResponse` en `app/api/routes.py`) antes de llegar a la lógica de
negocio. Una entrada inválida (por ejemplo, sin el campo `text`) es
rechazada por FastAPI con `422` antes de ejecutar cualquier módulo interno;
una entrada vacía tras normalizar es rechazada explícitamente por `Content`
con `400`. Este concepto aplica a `API` y `Content` por igual.

## 8.2 Manejo de errores

Los módulos internos (`Content`, `Analysis`, `Scoring`, `Persistencia`)
lanzan excepciones de Python estándar (por ejemplo `ValueError`); es
responsabilidad exclusiva de `API` traducir esas excepciones a respuestas
HTTP (`HTTPException`). Ningún módulo interno conoce HTTP directamente — esto
mantiene la separación de responsabilidades exigida por el monolito modular
(ver [ADR-0001](../adr/0001-estilo-arquitectonico.md)).

## 8.3 Estrategia de pruebas

Cada corte vertical ejecutable tiene una prueba de extremo a extremo con
`TestClient` de FastAPI (`tests/test_health.py`, `tests/test_analysis.py`),
en lugar de únicamente pruebas unitarias aisladas por módulo. Esto se decidió
porque el aspecto arquitectónico principal (ver [aspectos.md](../aspectos.md))
es la escalabilidad mediante modularidad, y la forma más directa de
verificarla es confirmar que un cambio en un módulo no rompe el recorrido
completo.

## 8.4 Convención de nombres y estructura de módulos

Cada módulo de negocio (`content`, `analysis`, `scoring`) expone su
funcionalidad a través de un `service.py` con funciones de nivel de módulo
(no clases), mientras que la lógica interna que sí necesita estado
(`RuleAnalyzer`) vive en un archivo separado (`analyzer.py`). Esta
convención facilita ubicar el punto de extensión correcto al agregar un
nuevo analizador (ver escenario
[Q-02](../escenarios-de-calidad.md#q-02--incorporación-de-un-nuevo-analizador)).

## 8.5 Trazabilidad documental

Todo aspecto arquitectónico relevante debe poder seguirse desde el escenario de calidad que lo
motiva hasta la evidencia de prueba, pasando por la vista C4 y el ADR correspondientes. Esa cadena
completa vive en [docs/aspectos.md](../aspectos.md) y es, en sí misma, un concepto transversal:
cualquier documento nuevo que agregue un aspecto debe respetar esas columnas.

## 8.6 Consistencia de datos

**Principio.** La consistencia se decide **por operación, no por sistema**: cada operación declara la
garantía que necesita (eventual, *read-your-writes*, causal o fuerte) y qué pasa si el dato llega tarde.
Las operaciones son las del sistema real (`app/api/routes.py`); no hay otras.

**Alcance.** Los datos viven en un único archivo SQLite escrito por un solo proceso (`run.py`, un worker
de Uvicorn). No hay réplicas ni caché de aplicación, así que no existen lecturas obsoletas entre nodos. Por
eso la garantía fuerte no cuesta nada hoy; empezaría a costar si se añadieran réplicas o más procesos (ver
los disparadores del [ADR-0011](../adr/0011-historial-registro-unico-sin-propietario.md)).

### Tabla: operación → garantía de consistencia

| Operación | Garantía | Si el dato llega tarde… | Cómo se cumple |
|---|---|---|---|
| Crear un análisis (`POST /analysis`) | **Fuerte** | No llega tarde: se confirma antes de responder. El riesgo contrario es que se pierda la respuesta y el cliente reintente: se crea un duplicado (MF-05, el POST no es idempotente). | `save_analysis` hace `INSERT` y `commit` en una transacción (`app/persistence/repository.py:95`); la API relee el registro con `get_analysis`, en otra conexión, antes de contestar (`app/api/routes.py:62`). Un solo archivo, sin réplicas. |
| Ver el análisis recién creado (`GET /analysis/{id}`) | **Read-your-writes** (en la práctica fuerte, por tener un solo nodo) | «Mi análisis desapareció»: un 404 justo después de crearlo. | Se lee del mismo archivo ya confirmado, sin caché ni réplica que pueda ir atrasada (`app/persistence/repository.py:139`, `app/api/routes.py:116`). Los registros son de solo adición: dos lecturas del mismo `id` devuelven lo mismo. |
| Listado del historial (`GET /analysis`) | **Eventual** (hasta la siguiente recarga de la pantalla) | Un análisis nuevo aparece en la siguiente carga. Entre dos páginas puede repetirse un elemento y el total (`X-Total-Count`) no coincidir con la página (DT-01). | Sin caché en el servidor. El frontend invalida por recarga explícita: `history.refresh()` tras cada `POST` exitoso. Lista y total son dos consultas sin instantánea común (`app/persistence/repository.py:169` y `:197`). |
| Leer las métricas (`GET /metrics`) | **Eventual y no durable** | Contadores atrasados, o en cero tras reiniciar el proceso. | Contadores en memoria del proceso (`app/observability.py`), solo para observación; ninguna decisión de negocio depende de ellos. |

**Decisión del arquitecto.** Se paga garantía fuerte solo donde un dato atrasado rompe una regla: confirmar
que un análisis quedó guardado y poder leerlo enseguida. El listado y las métricas toleran retraso porque
ninguna regla de negocio se rompe (no hay cupos, saldos ni pagos).

### Verificación contra la implementación

Dos de las operaciones, crear y consultar, están verificadas con pruebas ejecutables
(`tests/test_consistencia.py`, 6 pruebas), no solo descritas:

| Operación | Prueba |
|---|---|
| Crear | `test_post_deja_el_registro_confirmado_y_legible_desde_otra_conexion`, `test_post_no_es_idempotente_pero_el_calculo_es_determinista` |
| Consultar | `test_get_por_id_es_repetible_y_no_modifica_el_estado`, `test_get_de_id_inexistente_responde_404_sin_crear_registros` |
| Listar | `test_listado_informa_el_total_almacenado_en_la_cabecera`; el límite está caracterizado en `test_limite_conocido_paginacion_por_offset_puede_repetir_un_elemento` |

### Notas

- **Aislamiento.** SQLite serializa las escrituras con un bloqueo de archivo. Si una escritura espera más
  de 5 s (valor por defecto de `sqlite3` en Python), falla con `database is locked` (MF-04).
- **Esquema.** Las migraciones son aditivas (`PRAGMA table_info` + `ALTER TABLE`) y nunca borran datos.

## 8.7 Política de caché

**Decisión: no hay caché de aplicación en esta etapa.** La respuesta se calcula en cada petición. Las
escrituras van directo a SQLite, así que *write-through* y *write-back* no aplican. Tampoco se justifica una
caché distribuida (Redis o similar): hay un solo proceso.

| Qué | Dónde | Cuánto | Invalidación | Decisión |
|---|---|---|---|---|
| Resultado de `POST /analysis` por huella del contenido | Caché local, en proceso | — | — | **No.** El cálculo cuesta milisegundos (P95 local 46,9 ms; P95 en Render 211,3 ms con 10.000 caracteres, ver [medición](../evidencia/medicion-render-s10.md)), muy por debajo de los 3 s de Q-01. Un cambio de pesos o umbrales ([ADR-0006](../adr/0006-semantica-del-resultado.md)) dejaría resultados guardados desactualizados y rompería Q-05. |
| Listado `GET /analysis` | Caché local, patrón *cache-aside* | TTL de 30 s | Vaciar por completo después del `commit` de cada `POST` exitoso | **No implementada.** Es la caché que el listado necesitaría, pero la consulta es por índice y de 8 filas por página; no aporta. Si se activara, la garantía del listado seguiría siendo eventual, con tope de 30 s. |
| Texto extraído de una URL | Caché local, clave = URL normalizada | TTL de 10 min y 128 entradas (LRU) | Solo por tiempo: es independiente de las escrituras. Se cachea el **texto extraído**, no la puntuación, para que un cambio de reglas no lo invalide | **Condicional, no implementada.** Es lo único costoso (red). Se activa si la telemetría muestra URL repetidas o un P95 de extracción cercano a 3 s. |
| `GET /analysis/{id}` | Cabeceras HTTP (`Cache-Control: private`) | Larga: los registros son inmutables | No requiere | **No por ahora.** Es cacheable de forma segura, pero no está en la ruta crítica. |
| Archivos estáticos del frontend | Navegador, servidos por nginx | 1 año (nombres con hash de Vite) | El hash cambia con cada compilación | **Sí, implementada:** `location /assets/` con `expires 1y` e `immutable` en [`frontend/nginx.conf`](../../frontend/nginx.conf). Es la única caché del sistema. |

## 8.8 Política de invalidación tras una escritura

- **Backend:** como no hay caché de aplicación, no hay nada que invalidar; toda lectura refleja lo
  confirmado por la última escritura.
- **Frontend:** el historial se invalida por **recarga explícita**. Tras un `POST /analysis` exitoso,
  `App.tsx` llama a `history.refresh()`, que vuelve a pedir la primera página
  (`frontend/src/hooks/useAnalysisHistory.ts`). Las demás páginas se piden al navegar.
- **Si se añadiera caché del listado:** se vaciaría por completo después del `commit` de cada
  `POST /analysis` exitoso (no por tiempo), antes de responder al cliente.
- **Si se añadiera la caché de texto extraído:** no se invalida por escrituras (es independiente de
  ellas); expira por tiempo (10 minutos).
- **Límite conocido:** dos pestañas abiertas no se enteran de las escrituras de la otra hasta recargar.

## 8.9 Idempotencia y flujo por eventos

- **Idempotencia.** `POST /analysis` no es idempotente hoy. El diseño (clave `Idempotency-Key` o huella
  SHA-256, tabla de deduplicación y estados `PENDING`/`COMPLETED`/`FAILED`) está en la
  [entrega S11](../entregas/entrega-modos-fallo-idempotencia-adr.md#3-diseño-de-idempotencia-o-saga)
  y su estado real es **pendiente** (MF-05 en [§11](11-riesgos-y-deuda-tecnica.md)).
- **Flujo por eventos.** No existe: no hay broker, cola ni consumidores. La integración es síncrona
  ([ADR-0003](../adr/0003-integracion-sincrona.md)) y el broker fue descartado en el
  [ADR-0009](../adr/0009-decision-extraccion-modulo-analisis.md). La saga compensatoria del documento
  de S11 es un diseño futuro, solo aplicable si se extrajera el módulo de análisis.

## 8.10 Modelo de dominio y contextos delimitados (S6)

### 8.10.1 Lenguaje ubicuo

| Término | Significado en el dominio |
|---|---|
| Contenido | Texto o URL que el usuario envía para analizar |
| Análisis | Proceso que evalúa un Contenido en busca de señales de desinformación |
| Factor / Señal | Indicio individual detectado (sensacionalismo, mayúsculas, afirmación absoluta, ausencia de fuentes, lenguaje emocional) |
| Puntuación (Score) | Valor numérico resultante de combinar las Señales |
| Clasificación | Etiqueta derivada de la Puntuación |
| Historial | Registro persistente de Análisis pasados |


### 8.10.2 Contextos delimitados

Se identifican tres contextos dentro del monolito modular: **Ingesta y Presentación**, **Análisis de Contenido** (núcleo del dominio) e **Historial de Análisis** (soporte). El detalle del mapa de contextos, las relaciones entre ellos y la tabla de propiedad de datos están en [`docs/mapa-contextos.md`](../mapa-contextos.md).

### 8.10.3 Regla transversal de propiedad de datos

Cada tabla de la base de datos tiene un único módulo autorizado a escribir en ella. Los demás módulos que necesiten ese dato lo reciben como resultado de una llamada, nunca escribiendo directamente sobre la tabla ajena. El detalle de qué módulo escribe qué está en [`docs/propiedad-datos.md`](../propiedad-datos.md); las violaciones encontradas frente a esta regla y su plan de corrección están en [`docs/violaciones-modularidad.md`](../violaciones-modularidad.md).
