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
garantía que necesita y qué pasa si el dato llega tarde. No hay una garantía única global; cada fila
de la tabla siguiente es una decisión explícita del arquitecto.

**Alcance.** Los datos viven en un único archivo SQLite escrito por un solo proceso (`run.py`, un worker
de Uvicorn). No hay réplicas ni caché de aplicación, así que no existen lecturas obsoletas entre nodos. Por
eso la garantía fuerte no cuesta nada hoy; empezaría a costar si se añadieran réplicas o más procesos (ver
los disparadores del [ADR-0011](../adr/0011-historial-registro-unico-sin-propietario.md) y
[ADR-0012](../adr/0012-modelo-almacenamiento-sqlite-costo-reversion.md)).

**Límites de lo demostrado.** Cuando la tabla dice «fuerte», se refiere al modelo concreto que el código y las
pruebas sostienen: un único archivo SQLite, un solo proceso, `INSERT` + `commit` antes de responder y relectura
en una segunda conexión. **No se afirma** linearizabilidad en sentido general: no hay réplicas, no se probó
concurrencia real (hilos o procesos simultáneos) y las etiquetas de aislamiento (SERIALIZABLE) describen las
transacciones individuales de SQLite, no un comportamiento global del sistema. Si cambia cualquiera de esos
supuestos (réplicas, más procesos, caché), las garantías de la tabla deben revisarse (disparadores en el
ADR-0011 y el ADR-0012).

**Prototipo de mensajería: garantías aparte.** El prototipo aislado de `experiments/messaging/` tiene sus propias
garantías (entrega al menos una vez con consumidor idempotente, en un broker en memoria simulado). No son
garantías del producto ni se mezclan con esta tabla; su alcance y sus límites están en
[docs/mensajeria/limites-del-experimento.md](../mensajeria/limites-del-experimento.md) y en el
[ADR-0013](../adr/0013-no-incorporar-mensajeria-asincrona.md).

### Tabla: operación → garantía de consistencia

La siguiente matriz es la referencia canónica. Cada fila corresponde a una operación real del sistema
(`app/api/routes.py`), e indica el modelo de consistencia requerido, el mecanismo con el que se cumple
en el código actual, y la prueba ejecutable que lo verifica.

| Operación (endpoint) | Garantía requerida | Si el dato llega tarde… | Mecanismo de cumplimiento (código) | Nivel de aislamiento SQLite | Idempotente | Prueba ejecutable |
|---|---|---|---|---|---|---|
| **Crear análisis** `POST /analysis` (`routes.py:62`) | **Fuerte en el modelo de un nodo** (visibilidad tras `commit`; no se afirma linearizabilidad general) | No llega tarde: `save_analysis()` hace `INSERT` + `commit` antes de responder. El riesgo es que se pierda la respuesta HTTP y el cliente reintente → duplicado (MF-05). | `save_analysis` abre conexión, ejecuta `INSERT INTO analyses …` y llama a `commit` (`repository.py:95-134`). La API relee el registro con `get_analysis(id)` en una **segunda** conexión antes de contestar (`routes.py:103`), confirmando que el dato ya es visible fuera de la transacción original. | SERIALIZABLE (por defecto en SQLite; un solo escritor con bloqueo de archivo). `busy_timeout` implícito de 5 s. | **No.** Cada invocación genera un nuevo `id` autoincremental, aunque el contenido sea idéntico. Diseño de idempotencia pendiente (MF-05). | `test_post_deja_el_registro_confirmado_y_legible_desde_otra_conexion`, `test_post_no_es_idempotente_pero_el_calculo_es_determinista` |
| **Consultar análisis** `GET /analysis/{id}` (`routes.py:116`) | **Read-your-writes** (en el modelo de un nodo SQLite) | «Mi análisis desapareció»: 404 justo después de crearlo. No ocurre en el modelo actual: la lectura va al mismo archivo ya confirmado, sin réplicas ni caché. | `get_analysis(id)` abre una conexión nueva y ejecuta `SELECT … WHERE id = ?` (`repository.py:139-166`). Los registros son de solo adición (inmutables): dos lecturas del mismo `id` siempre devuelven el mismo cuerpo. Sin caché ni réplica. | SERIALIZABLE (lectura; no compite con escrituras porque es solo `SELECT`). | **Sí** (segura y repetible, sin efectos laterales). | `test_get_por_id_es_repetible_y_no_modifica_el_estado`, `test_get_de_id_inexistente_responde_404_sin_crear_registros` |
| **Listar historial** `GET /analysis` (`routes.py:129`) | **Eventual** (hasta la siguiente recarga de pantalla) | Un análisis nuevo aparece en la siguiente carga. Entre dos páginas puede repetirse un elemento y el total (`X-Total-Count`) no coincidir (DT-01). | `list_analyses` y `count_analyses` son **dos consultas separadas** en conexiones distintas (`repository.py:169` y `:197`), sin instantánea común. El frontend invalida por recarga explícita: `history.refresh()` tras cada `POST` exitoso. | Cada consulta individual es SERIALIZABLE, pero no hay transacción que las agrupe. | **Sí** (sin efectos laterales). | `test_listado_informa_el_total_almacenado_en_la_cabecera`; el límite está caracterizado en `test_limite_conocido_paginacion_por_offset_puede_repetir_un_elemento` |
| **Métricas** `GET /metrics` (`routes.py` vía `observability.py`) | **Eventual y no durable** | Contadores atrasados o en cero tras reiniciar el proceso. | Contadores en memoria del proceso (`app/observability.py`), no persistidos. Ninguna decisión de negocio depende de ellos. | N/A (no toca SQLite). | **Sí** (sin efectos laterales). | `tests/test_observability.py` |

**Decisión del arquitecto.** Se paga garantía fuerte solo donde un dato atrasado rompe una regla de negocio:
confirmar que un análisis quedó guardado y poder leerlo enseguida. El listado y las métricas toleran retraso
porque ninguna regla de negocio se rompe (no hay cupos, saldos ni pagos). La decisión de modelo de
almacenamiento y su costo de reversión están formalizados en el [ADR-0012](../adr/0012-modelo-almacenamiento-sqlite-costo-reversion.md).

### Verificación contra la implementación

Dos de las operaciones (crear y consultar) están **verificadas con pruebas ejecutables**
(`tests/test_consistencia.py`, 6 pruebas), no solo descritas. Cada prueba contrasta la garantía declarada
en la tabla anterior contra el comportamiento real del código. Las pruebas son secuenciales (`TestClient`, una conexión tras otra, sin hilos
concurrentes): demuestran visibilidad tras `commit` en un nodo, no linearizabilidad bajo concurrencia ni con réplicas.

| Operación verificada | Garantía probada | Prueba(s) | Qué demuestra |
|---|---|---|---|
| **Crear** (`POST /analysis`) | Visibilidad tras `commit` (modelo de un nodo): el registro es legible desde otra conexión inmediatamente después | `test_post_deja_el_registro_confirmado_y_legible_desde_otra_conexion` | Llama a `POST`, luego invoca `get_analysis(id)` (que abre una conexión nueva) y verifica que todos los campos coinciden. Si la transacción no hubiera hecho `commit`, este `SELECT` devolvería `None`. |
| **Crear** (`POST /analysis`) | No idempotente pero determinista | `test_post_no_es_idempotente_pero_el_calculo_es_determinista` | Envía el mismo texto dos veces: obtiene `id` distintos (no idempotente, MF-05), pero `score`, `classification` y `factors` idénticos (Q-05). |
| **Consultar** (`GET /analysis/{id}`) | Read-your-writes: lectura repetible e inmutable | `test_get_por_id_es_repetible_y_no_modifica_el_estado` | Dos `GET` consecutivos al mismo `id` devuelven el mismo JSON; el conteo de registros no cambia. |
| **Consultar** (`GET /analysis/{id}`) | 404 sin efectos laterales | `test_get_de_id_inexistente_responde_404_sin_crear_registros` | Un `GET` a un `id` inexistente devuelve 404 y no crea registros. |
| **Listar** (`GET /analysis`) | Total correcto en cabecera | `test_listado_informa_el_total_almacenado_en_la_cabecera` | Verifica que `X-Total-Count` coincide con `count_analyses()`. |
| **Listar** (`GET /analysis`) | Límite conocido documentado | `test_limite_conocido_paginacion_por_offset_puede_repetir_un_elemento` | Demuestra que una inserción entre dos páginas causa que un elemento se repita (DT-01). |

### Notas

- **Aislamiento.** SQLite serializa las escrituras con un bloqueo de archivo. Si una escritura espera más
  de 5 s (valor por defecto de `sqlite3` en Python), falla con `database is locked` (MF-04).
- **Esquema.** Las migraciones son aditivas (`PRAGMA table_info` + `ALTER TABLE`) y nunca borran datos.
- **Modelo de datos y costo de reversión.** La decisión de almacenamiento más costosa de revertir
  (contenido completo sin propietario en SQLite) está formalizada en el [ADR-0012](../adr/0012-modelo-almacenamiento-sqlite-costo-reversion.md),
  que compara las cinco decisiones de datos y cuantifica el esfuerzo de migración.

## 8.7 Política de caché

**Decisión: no hay caché de aplicación en esta etapa.** La respuesta se calcula en cada petición. Las
escrituras van directo a SQLite, así que *write-through* y *write-back* no aplican. Tampoco se justifica una
caché distribuida (Redis o similar): hay un solo proceso.

### Diseño: qué, dónde y cuánto

La siguiente tabla evalúa cada dato candidato a caché con las tres dimensiones requeridas (qué se cachea,
dónde se almacena y cuánto dura), junto con la estrategia de invalidación y la decisión tomada.

| Qué se cachearía | Dónde | Cuánto (TTL / duración) | Estrategia de invalidación | Decisión y justificación |
|---|---|---|---|---|
| **Resultado del cálculo** de `POST /analysis` por huella del contenido | Caché local en proceso (diccionario en memoria, clave = SHA-256 del texto normalizado) | Sin expiración por tiempo; máximo 256 entradas (LRU) | No requiere invalidación por escrituras (es resultado de un cálculo puro). Se invalida si cambian pesos o umbrales ([ADR-0006](../adr/0006-semantica-del-resultado.md)), pero hoy eso implica redesplegar → la caché se pierde naturalmente al reiniciar. | **No implementada.** El cálculo cuesta milisegundos (P95 local 46,9 ms; P95 en Render 211,3 ms con 10.000 caracteres, ver [medición](../evidencia/medicion-render-s10.md)), muy por debajo de los 3 s de Q-01. Un cambio de pesos dejaría resultados guardados desactualizados y rompería Q-05. El ahorro no justifica el riesgo. |
| **Listado paginado** `GET /analysis` | Caché local en proceso, patrón *cache-aside* (clave = `(limit, offset)`) | TTL de 30 s | **Vaciar por completo** después del `commit` de cada `POST /analysis` exitoso, antes de responder al cliente. No por tiempo solamente: la invalidación activa tras escritura es imprescindible para que el listado refleje el análisis recién creado en la misma sesión. | **No implementada.** La consulta es por índice y de 8 filas por página; no aporta. Si se activara, la garantía del listado seguiría siendo eventual, con tope de 30 s para otras sesiones. |
| **Texto extraído de una URL** | Caché local en proceso, clave = URL normalizada (LRU) | TTL de 10 min y máximo 128 entradas | Solo por tiempo: es independiente de las escrituras en `analyses`. Se cachea el **texto extraído**, no la puntuación, para que un cambio de reglas no lo invalide. | **Condicional, no implementada.** Es lo único costoso (red). Se activa si la telemetría muestra URL repetidas o un P95 de extracción cercano a 3 s. |
| **Análisis individual** `GET /analysis/{id}` | Cabeceras HTTP (`Cache-Control: private, immutable`) en la respuesta | Larga (los registros son inmutables, de solo adición) | No requiere invalidación: un `id` siempre devuelve el mismo contenido. | **No implementada por ahora.** Es cacheable de forma segura por el navegador, pero la consulta por `id` no está en la ruta crítica del usuario. |
| **Archivos estáticos del frontend** | Navegador del usuario, servidos por nginx | 1 año (nombres con hash de contenido generado por Vite) | El hash cambia con cada compilación; los nombres antiguos simplemente dejan de referenciarse. | **Sí, implementada:** `location /assets/` con `expires 1y` e `immutable` en [`frontend/nginx.conf`](../../frontend/nginx.conf). Es la **única caché activa** del sistema. |

### Justificación de no-caché en esta etapa

1. **Latencia suficiente sin caché:** El P95 del pipeline completo (46,9 ms local / 211,3 ms en Render) está
   muy por debajo del umbral de Q-01 (3.000 ms). No hay presión de rendimiento.
2. **Un solo proceso, un solo archivo:** Sin réplicas ni nodos, no hay lectura obsoleta que una caché deba
   mitigar. La caché solo ahorraría milisegundos de cómputo o una lectura de disco ya en buffer del SO.
3. **Riesgo de inconsistencia artificial:** Introducir una caché obligaría a implementar y probar la
   invalidación (especialmente del listado tras `POST`), añadiendo complejidad sin beneficio medible.

## 8.8 Política de invalidación tras una escritura

- **Backend (actual):** como no hay caché de aplicación, no hay nada que invalidar en el servidor; toda
  lectura refleja lo confirmado por la última escritura. La lectura va directo a SQLite.
- **Frontend:** el historial se invalida por **recarga explícita**. Tras un `POST /analysis` exitoso,
  `App.tsx` llama a `history.refresh()`, que vuelve a pedir la primera página
  (`frontend/src/hooks/useAnalysisHistory.ts`). Las demás páginas se piden al navegar.
- **Si se añadiera caché del listado (ver §8.7):** se vaciaría por completo después del `commit` de cada
  `POST /analysis` exitoso (invalidación activa, no por tiempo), **antes** de responder al cliente. Esto
  garantiza que el `GET /analysis` inmediato del mismo cliente vea el análisis recién creado.
- **Si se añadiera la caché de texto extraído:** no se invalida por escrituras (es independiente de
  ellas); expira solo por tiempo (10 minutos).
- **Límite conocido:** dos pestañas abiertas no se enteran de las escrituras de la otra hasta recargar.
  Un mecanismo de notificación (SSE o WebSocket) no se justifica en esta etapa.

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


## 8.11 Privacidad y Protección de Datos Personales (S13)

VeriFacts procesa contenido textual de noticias enviado por usuarios para detectar señales de desinformación. Desde la perspectiva arquitectónica, el sistema adopta los principios de **Privacidad desde el Diseño (*Privacy by Design*)** y cumplimiento de la normativa de Protección de Datos Personales (Ley Estatutaria 1581 de 2012 de Colombia, Habeas Data y directrices RGPD):

1. **Minimización de datos (*Data Minimization*):**
   - El sistema **no exige registro ni autenticación de usuarios** ([ADR-0011](../adr/0011-historial-registro-unico-sin-propietario.md)).
   - Las consultas de análisis son completamente anónimas y no se asocian a identificadores personales, correos ni números de teléfono.
2. **Limitación de la finalidad (*Purpose Limitation*):**
   - El texto y las URLs enviadas se utilizan exclusivamente para computar heurísticas de desinformación en memoria.
   - El sistema no alimenta modelos generativos comerciales externos ni elabora perfiles comerciales o políticos de usuarios ([ADR-0007](../adr/0007-no-incorporar-componente-generativo.md)).
3. **Retención acotada y depuración:**
   - La persistencia en SQLite (`data/verifacts.db`) opera bajo una política de retención máxima recomendada de 30 días, tras la cual los registros históricos pueden ser depurados mediante tareas periódicas de mantenimiento.
4. **Protección en scraping e ingesta:**
   - Se excluyen credenciales o parámetros privados en URLs (`http://user:pass@host`).
   - El motor de scraping respeta un límite de descarga de 2 MB y truncamiento de texto para prevenir sobrecarga de datos.
5. **Derecho a la supresión (*Right to Erasure*):**
   - La arquitectura contempla la eliminación física de registros específicos del historial ante solicitudes de Habeas Data donde un texto ingresado contenga datos personales indebidamente expuestos.

El detalle completo del inventario de datos, matriz de riesgos de privacidad (PR-01 a PR-03) y modelado de amenazas se encuentra formalizado en [`docs/entregas/entrega-seguridad-amenazas-dependencias-privacidad.md`](../entregas/entrega-seguridad-amenazas-dependencias-privacidad.md).
