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

**Alcance.** Los datos viven en un único archivo SQLite escrito por un solo proceso
(`run.py`, un worker de Uvicorn). No hay réplicas ni caché de aplicación, por lo que no existen
lecturas obsoletas entre nodos; las garantías dependen solo de las transacciones locales. El
modelo de datos y el costo de revertirlo están en el [ADR-0011](../adr/0011-historial-registro-unico-sin-propietario.md).

### Tabla: operación → garantía de consistencia

| Operación | Código | Qué garantiza | Idempotente | Verificación |
|---|---|---|---|---|
| `POST /analysis` (crear) | `app/api/routes.py:62` → `save_analysis` (`app/persistence/repository.py:95`) | **Atomicidad y durabilidad:** el `INSERT` se confirma (`commit`) antes de responder; el registro existe completo o no existe. **Lectura propia:** `create_analysis` vuelve a leerlo con `get_analysis` (otra conexión) antes de contestar. | **No.** Cada invocación crea un `id` nuevo, aunque el contenido sea igual (MF-05). El resultado calculado sí es determinista (Q-05). | `tests/test_consistencia.py`: `test_post_deja_el_registro_confirmado_y_legible_desde_otra_conexion`, `test_post_no_es_idempotente_pero_el_calculo_es_determinista` |
| `GET /analysis/{id}` (consultar) | `app/api/routes.py:116` → `get_analysis` (`app/persistence/repository.py:139`) | **Lectura confirmada:** devuelve solo registros ya confirmados, sin lecturas sucias; un `id` inexistente da 404. Como los registros son de solo adición, dos lecturas del mismo `id` devuelven el mismo cuerpo. | **Sí** (segura y repetible, sin efectos) | `test_get_por_id_es_repetible_y_no_modifica_el_estado`, `test_get_de_id_inexistente_responde_404_sin_crear_registros` |
| `GET /analysis` (listar) | `app/api/routes.py:129` → `list_analyses` (`:169`) y `count_analyses` (`:197`) | Cada consulta ve un estado confirmado. **Límite:** lista y total son dos consultas en conexiones distintas, sin instantánea común; una inserción entre ambas, o entre dos páginas, puede desajustar el total o repetir un elemento (paginación por `OFFSET`). Es consistencia eventual dentro de una misma carga de pantalla. | **Sí** (sin efectos) | `test_listado_informa_el_total_almacenado_en_la_cabecera`; el límite está caracterizado en `test_limite_conocido_paginacion_por_offset_puede_repetir_un_elemento` |
| `GET /health` | `app/api/routes.py:57` | No toca datos | **Sí** | `tests/test_health.py` |

### Notas

- **Aislamiento.** SQLite serializa las escrituras con un bloqueo de archivo. Si una escritura espera
  más de 5 s (valor por defecto de `sqlite3` en Python), falla con `database is locked` (MF-04).
- **Esquema.** Las migraciones son aditivas (`PRAGMA table_info` + `ALTER TABLE`) y nunca borran datos.
- **Dos de las filas están verificadas contra la implementación** con pruebas ejecutables
  (`tests/test_consistencia.py`, 6 pruebas), no solo descritas.

## 8.7 Política de caché

**Decisión: no hay caché de aplicación en esta etapa.** La respuesta se calcula en cada petición.

| Qué se podría cachear | Dónde | Cuánto | Decisión y justificación |
|---|---|---|---|
| Resultado de `POST /analysis` por huella del contenido | En proceso | — | **No.** El cálculo cuesta unos milisegundos (P95 local 46,9 ms; P95 en Render 211,3 ms con 10.000 caracteres, ver [medición](../evidencia/medicion-render-s10.md)), muy por debajo de los 3 s de Q-01. Además, un cambio de pesos o umbrales ([ADR-0006](../adr/0006-semantica-del-resultado.md)) dejaría resultados guardados desactualizados y rompería Q-05. |
| `GET /analysis/{id}` | Cabeceras HTTP (`Cache-Control`) | Larga (los registros son inmutables) | **No por ahora.** Es cacheable de forma segura, pero hoy no aporta: la consulta por `id` no está en la ruta crítica. |
| `GET /analysis` (listado) | — | — | **No.** Cambia con cada escritura; una caché obligaría a invalidarla (ver 8.8). |
| Texto extraído de una URL | En proceso, por URL | **Diseño condicional:** 10 minutos y 128 entradas como máximo | **No implementado.** Es lo único costoso (red). Se implementaría si la telemetría muestra URL repetidas o un P95 de extracción cercano a 3 s. Se cachea el **texto extraído**, no la puntuación, para que un cambio de reglas no lo invalide. |
| Archivos estáticos del frontend | Navegador, mediante nginx | 1 año (nombres con hash de Vite) | **Sí, implementada:** `location /assets/` con `expires 1y` e `immutable` en [`frontend/nginx.conf`](../../frontend/nginx.conf). Es la única caché del sistema. |

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
