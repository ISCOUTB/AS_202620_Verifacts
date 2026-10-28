# Entrega Semana 12: Consistencia de Datos, Política de Caché, Invalidación y Decisión de Datos más Costosa de Revertir

**Proyecto:** VeriFacts — Sistema de Detección de Desinformación  
**Equipo:** Pedro Jose Castro Blanquicett, Cristian David Cardeno, Julian Samuel Cabeza Pena  
**Repositorio:** [https://github.com/ISCOUTB/AS_202620_Verifacts](https://github.com/ISCOUTB/AS_202620_Verifacts)  
**Fecha de formalización:** 2026-10-21 (Actualizado 2026-10-28)  
**Correspondencia arquitectónica:** arc42 [§8.6](../arc42/08-conceptos-transversales.md#86-consistencia-de-datos), [§8.7](../arc42/08-conceptos-transversales.md#87-política-de-caché), [§8.8](../arc42/08-conceptos-transversales.md#88-política-de-invalidación-tras-una-escritura), [ADR-0011](../adr/0011-historial-registro-unico-sin-propietario.md), [ADR-0012](../adr/0012-modelo-almacenamiento-sqlite-costo-reversion.md), y [Aspecto A-09](../aspectos.md#matriz-de-trazabilidad).

---

## 1. Matriz de Consistencia: Operación → Garantía

La consistencia en VeriFacts se decide **por operación y no de forma global**. Toda la persistencia reside en un archivo único de SQLite (`data/verifacts.db`) administrado exclusivamente por `app/persistence/repository.py` y servido por un único worker Uvicorn. No existen réplicas de base de datos ni caché distribuida en esta etapa.

### 1.1 Tabla Canónica de Consistencia por Operación

| Operación (Endpoint) | Garantía requerida | Si el dato llega tarde… | Mecanismo de cumplimiento en el código | Nivel de aislamiento SQLite | ¿Idempotente? | Prueba ejecutable asociada |
|---|---|---|---|---|:---:|---|
| **Crear análisis**<br>`POST /analysis`<br>(`routes.py:62`) | **Fuerte en un nodo**<br>(visibilidad inmediata tras commit) | No llega tarde: `save_analysis()` ejecuta `INSERT` + `commit` antes de emitir respuesta HTTP. | `save_analysis` abre conexión, ejecuta `INSERT INTO analyses …` y llama a `commit` (`repository.py:95-134`). Para certificar visibilidad externa, la API relee con `get_analysis(id)` en una **segunda conexión independiente** antes de responder (`routes.py:103`). | SERIALIZABLE (por bloqueo de archivo nativo de SQLite; timeout de 5 s). | **No.**<br>Cada llamada genera nuevo `id` autoincremental (MF-05). | `test_post_deja_el_registro_confirmado_y_legible_desde_otra_conexion`,<br>`test_post_no_es_idempotente_pero_el_calculo_es_determinista` |
| **Consultar análisis**<br>`GET /analysis/{id}`<br>(`routes.py:116`) | **Read-your-writes**<br>(en el modelo local de SQLite) | «Mi análisis desapareció»: 404 justo después de crearlo. No ocurre: la lectura consulta el mismo archivo ya confirmado. | `get_analysis(id)` abre conexión nueva y ejecuta `SELECT … WHERE id = ?` (`repository.py:139-166`). Los registros son de solo adición (inmutables): lecturas sucesivas retornan exactamente el mismo cuerpo. | SERIALIZABLE (lectura compartida sin contención de escritura). | **Sí.**<br>Segura y repetible. | `test_get_por_id_es_repetible_y_no_modifica_el_estado`,<br>`test_get_de_id_inexistente_responde_404_sin_crear_registros` |
| **Listar historial**<br>`GET /analysis`<br>(`routes.py:129`) | **Eventual**<br>(hasta la recarga de pantalla) | Un análisis nuevo aparece en la siguiente recarga. Entre dos páginas un elemento puede repetirse si hubo una inserción concurrente (DT-01). | `list_analyses` y `count_analyses` son **dos consultas separadas** sin transacción que las agrupe (`repository.py:169` y `:197`). El frontend invalida y refresca explícitamente con `history.refresh()` tras cada `POST` exitoso. | Transacciones de lectura independientes. | **Sí.**<br>Sin efectos laterales. | `test_listado_informa_el_total_almacenado_en_la_cabecera`,<br>`test_limite_conocido_paginacion_por_offset_puede_repetir_un_elemento` |
| **Métricas**<br>`GET /metrics`<br>(`routes.py`) | **Eventual y no durable** | Contadores atrasados o en cero si el contenedor se reinicia. | Contadores atómicos en memoria (`app/observability.py`). Ninguna regla de negocio depende de ellos. | N/A (no interactúa con SQLite). | **Sí.**<br>Solo lectura de contadores. | `tests/test_observability.py` |

---

## 2. Verificación contra la Implementación

Las garantías anteriores no son meras declaraciones teóricas: se verifican de extremo a extremo mediante **6 pruebas automatizadas** en [`tests/test_consistencia.py`](../../tests/test_consistencia.py):

| Operación Verificada | Garantía Probada | Prueba Ejecutable (`tests/test_consistencia.py`) | Qué Demuestra Técnicamente |
|---|---|---|---|
| **Crear** (`POST /analysis`) | Visibilidad tras `commit` en otra conexión | `test_post_deja_el_registro_confirmado_y_legible_desde_otra_conexion` | Envía una petición `POST`, toma el `id` devuelto y ejecuta `get_analysis(id)` desde una conexión de base de datos distinta. Si el `commit` no fuese síncrono y atómico, la consulta retornaría `None`. |
| **Crear** (`POST /analysis`) | Cómputo determinista vs. Falta de idempotencia | `test_post_no_es_idempotente_pero_el_calculo_es_determinista` | Envía el mismo texto dos veces seguidas: comprueba que se generan dos `id` diferentes (demostrando que la API actual no es idempotente), pero los valores de `score`, `classification` y `factors` son 100 % idénticos (satisfaciendo Q-05). |
| **Consultar** (`GET /analysis/{id}`) | Lectura repetible e inmutabilidad (*Read-your-writes*) | `test_get_por_id_es_repetible_y_no_modifica_el_estado` | Ejecuta dos `GET` consecutivos sobre el mismo `id`: confirma que el JSON de respuesta es idéntico y que el número de registros en la tabla no sufre alteraciones. |
| **Consultar** (`GET /analysis/{id}`) | Consulta inexistente sin efectos laterales | `test_get_de_id_inexistente_responde_404_sin_crear_registros` | Consulta un `id` inexistente: verifica que el sistema responde con `HTTP 404` sin alterar contadores ni insertar registros residuales. |
| **Listar** (`GET /analysis`) | Coherencia del total en cabeceras | `test_listado_informa_el_total_almacenado_en_la_cabecera` | Valida que la cabecera `X-Total-Count` coincida exactamente con el total físico reportado por `count_analyses()`. |
| **Listar** (`GET /analysis`) | Límite conocido de paginación por offset | `test_limite_conocido_paginacion_por_offset_puede_repetir_un_elemento` | Demuestra y caracteriza el límite conocido DT-01: una inserción concurrente entre consultas de dos páginas puede desplazar la ventana y repetir un elemento en la paginación por `OFFSET`. |

---

## 3. Diseño de Caché: Qué, Dónde y Cuánto

### 3.1 Postura Arquitectónica: Justificación de No-Caché en Backend
En la arquitectura actual de VeriFacts, **no se implementa caché de aplicación en el backend** por tres razones de peso:
1. **Presupuesto de latencia holgado:** El pipeline completo de análisis responde en P95 = 46,9 ms local y 211,3 ms en Render (con 10.000 caracteres), muy por debajo de los 3.000 ms exigidos por **Q-01**. Introducir caché no aporta un beneficio perceptible para el usuario.
2. **Arquitectura monoproceso y monolítica:** Al operar con un solo worker y un archivo SQLite local, no existen lecturas remotas de red hacia un servidor de base de datos independiente. El sistema operativo ya mantiene en buffer de memoria las páginas de SQLite.
3. **Prevención de inconsistencias:** Cachear el cálculo lingüístico introduciría el riesgo de servir resultados obsoletos si se recalibran reglas o umbrales (violando **Q-05**).

---

### 3.2 Matriz de Diseño de Caché (Tres Dimensiones)

La siguiente tabla documenta la evaluación exhaustiva de cada dato del sistema bajo las tres dimensiones requeridas (**qué**, **dónde** y **cuánto tiempo**), junto a su mecanismo de invalidación:

| # | Qué se cachearía | Dónde | Cuánto (TTL / Duración) | Estrategia de Invalidación | Decisión y Justificación |
|:---:|---|---|---|---|---|
| **1** | **Resultado del cálculo lingüístico** (`POST /analysis`) | Caché local en memoria del proceso (clave: hash SHA-256 del texto normalizado) | Máximo 256 entradas (política LRU) sin expiración por tiempo | Se invalida al reiniciar el proceso o redesplegar ante cambios de pesos en Scoring ([ADR-0006](../adr/0006-semantica-del-resultado.md)). | **No implementada.** El cómputo en CPU toma menos de 50 ms. Una caché no justificaría la complejidad de invalidación ni el riesgo de servir puntuaciones obsoletas ante cambios de reglas. |
| **2** | **Listado del historial** (`GET /analysis`) | Caché local en memoria (*cache-aside*, clave: `limit:offset`) | TTL de 30 segundos | **Invalidación activa:** Vaciado total de la caché tras el commit de cada `POST /analysis` exitoso, antes de retornar al cliente. | **No implementada.** La consulta a SQLite toma < 2 ms para 8 registros. La invalidación activa añadiría contención entre hilos sin beneficio medible. |
| **3** | **Texto plano extraído de una URL** | Caché local en memoria (clave: URL normalizada) | TTL de 10 minutos (máximo 128 entradas) | Expiración pasiva por tiempo (independiente de escrituras en base de datos). | **Diseñada, no implementada.** Es el único componente con latencia de red variable. Se activaría como táctica solo si el tráfico real demostrase re-análisis frecuente de las mismas URLs. |
| **4** | **Análisis individual persistido** (`GET /analysis/{id}`) | Cabeceras HTTP en cliente (`Cache-Control: private, immutable`) | Larga duración (el registro es inmutable) | No requiere invalidación: un `id` numérico jamás se actualiza ni se reasigna. | **No implementada por ahora.** Es técnicamente segura, pero la consulta puntual por ID no es la ruta crítica de navegación del usuario. |
| **5** | **Archivos estáticos del Frontend** (`.js`, `.css`, imágenes) | Caché en navegador web del cliente, servida por Nginx | **1 año** (`Cache-Control: public, max-age=31536000, immutable`) | **Invalidación por Hash de Contenido:** Vite genera nombres únicos con huella criptográfica (`index-B1x2...js`). Cuando se publica una nueva versión, los nombres cambian automáticamente. | ✅ **IMPLEMENTADA.** Configurada en `frontend/nginx.conf` (`location /assets/ { expires 1y; add_header Cache-Control "..."; }`). **Es la única caché activa del sistema.** |

---

## 4. Política de Invalidación tras una Escritura

* **Comportamiento en Backend (Estado Real):**  
  Al no existir capa de caché de aplicación en memoria, **toda consulta `GET` lee directamente el estado confirmado en SQLite**. No existe ventana de obsolescencia ni desfase entre nodos.
* **Comportamiento en Frontend (Estado Real):**  
  La interfaz web en React (`frontend/`) invalida el catálogo mediante **recarga explícita**:
  * Tras un `POST /analysis` exitoso, el componente principal dispara `history.refresh()` a través del hook `useAnalysisHistory.ts`.
  * Esto fuerza una petición HTTP fresca `GET /analysis?limit=8&offset=0`, garantizando que el usuario observe de inmediato en pantalla el análisis que acaba de generar.
* **Diseño para Caché Futura del Listado:**  
  Si en el futuro se activase la caché del historial en backend, la política definida es la **invalidación síncrona tras commit**:
  ```python
  # app/api/routes.py (diseño objetivo)
  analysis_id = repository.save_analysis(...)
  cache_service.invalidate_all("analyses_list:*")  # Vaciado inmediato
  return AnalysisResponse(...)
  ```
  Esto garantiza que el cliente no reciba una instantánea desactualizada al navegar inmediatamente al historial.

---

## 5. Garantías del Flujo por Eventos

* **¿Existe flujo por eventos en el producto? NO.**  
  VeriFacts opera bajo una integración síncrona estricta de extremo a extremo, ratificada en el [ADR-0003](../adr/0003-integracion-sincrona.md) y en el [ADR-0009](../adr/0009-decision-extraccion-modulo-analisis.md). No hay broker de mensajería (RabbitMQ, Kafka) ni workers asíncronos en el ciclo de producción.
* **Prototipo de Mensajería Aislado (Taller S13):**  
  El prototipo desarrollado en `experiments/messaging/` evalúa de forma puramente experimental la entrega *at-least-once*, reintentos con backoff y Dead Letter Queue (DLQ) en memoria ([ADR-0013](../adr/0013-no-incorporar-mensajeria-asincrona.md)). Dichas garantías pertenecen a un laboratorio cerrado y **no forman parte de las garantías transaccionales del producto VeriFacts**.

---

## 6. ADR de la Decisión de Datos más Costosa de Revertir

### 6.1 Documento Formal
> 👉 **Referencia:** [`docs/adr/0012-modelo-almacenamiento-sqlite-costo-reversion.md`](../adr/0012-modelo-almacenamiento-sqlite-costo-reversion.md)  
> **Título:** ADR-0012: Modelo de almacenamiento en SQLite — decisión de datos más costosa de revertir  
> **Estado:** Aceptado (2026-10-21)

---

### 6.2 Comparativa Cuantitativa de Costo de Reversión

Se evaluaron y clasificaron las 5 decisiones de datos del sistema, ordenadas de mayor a menor costo de reversión:

| # | Decisión de Datos Evaluada | Qué exigiría revertirla | Impacto en Migración de Datos Existentes | Impacto en Contrato y Clientes | Esfuerzo Estimado | Justificación del Costo Relativo |
|:---:|---|---|---|---|:---:|---|
| **4+5** | **Contenido completo sin propietario** *(Historial global anónimo en SQLite)* | Diseñar esquema de autenticación/usuarios, asociar `user_id` a análisis, política de retención y borrado. | **Irreversible para datos históricos:** Imposible atribuir retroactivamente un autor a los textos guardados. Requiere decisión legal/humana caso a caso o borrado destructivo. | **Alto:** Modificación profunda del contrato OpenAPI, endpoints protegidos, login en frontend. | 🔴 **ALTO**<br>**(40–80 h)** | **Es la decisión más costosa de revertir porque cada día que opera el sistema acumula más datos anónimos irrecuperables con potencial pasivo legal (Habeas Data / GDPR).** |
| **3** | Identificador entero autoincremental (`id: 1, 2, 3...`) | Cambiar tipo a UUIDv4 en base de datos, API y frontend. | Script de mapeo para generar UUIDs conservando equivalencia `old_id → uuid`. | **Alto:** Rompe enlaces y bookmarks existentes; requiere nueva versión de API. | 🟡 **Medio-Alto**<br>(20–40 h) | Afecta contratos externos, pero es 100 % automatizable mediante scripts técnicos. |
| **1** | Motor SQLite local → PostgreSQL independiente | Configurar servidor de base de datos, variables de entorno y adaptar driver en `repository.py`. | Volcado estándar `sqlite3 .dump` e importación en tablas de PostgreSQL. | **Nulo:** El contrato HTTP y los esquemas JSON de la API no cambian. | 🟡 **Medio**<br>(16–24 h) | La persistencia está encapsulada exclusivamente en `app/persistence/repository.py` ([propiedad de datos](../propiedad-datos.md)). |
| **2** | Campo `factors` como texto (`"A \| B"`) → JSON relacional | Modificar serialización en `save_analysis()` y `get_analysis()`. | Consulta SQL simple: `UPDATE analyses SET factors = ...`. | **Nulo:** La API ya expone `factors` como `list[str]`. | 🟢 **Bajo**<br>(4–8 h) | Cambio puramente interno sin repercusión fuera del módulo de repositorio. |
| **1b** | Añadir réplica de lectura o caché en base de datos | Configurar réplica de SQLite o capa Redis en repositorio. | Ninguna migración requerida. | **Nulo.** | 🟢 **Bajo**<br>(8–16 h) | Optimización interna de lectura sin impacto de esquema. |

---

### 6.3 Justificación Arquitectónica: ¿Por qué la combinación 4+5 es la más costosa?

1. **Acumulación Irreversible de Pasivos:** A diferencia de una migración de base de datos técnica (SQLite a Postgres) que se resuelve con un script de volcado en una tarde, los datos acumulados sin identidad no tienen autor conocido en el mundo real. No existe algoritmo que deduzca quién envió una noticia anónima en el pasado.
2. **Exposición Pública de Textos:** Los textos completos guardados han sido legibles mediante `GET /analysis/{id}` por cualquier cliente. La información expuesta no puede revocarse una vez consumida.
3. **Radio de Impacto Transversal:** Cambiar esta decisión obliga a reescribir la capa de base de datos, crear servicios de identidad, incorporar componentes de login en React, actualizar contratos de API y modificar la totalidad de la suite de pruebas automatizadas.

---

## 7. Trazabilidad Documental y en Código

* **Matriz de Aspectos Arquitectónicos:** Registrado formalmente como aspecto **A-09** en [`docs/aspectos.md`](../aspectos.md#matriz-de-trazabilidad).
* **Conceptos Transversales:** Secciones [§8.6](../arc42/08-conceptos-transversales.md#86-consistencia-de-datos), [§8.7](../arc42/08-conceptos-transversales.md#87-política-de-caché) y [§8.8](../arc42/08-conceptos-transversales.md#88-política-de-invalidación-tras-una-escritura).
* **Pruebas de Verificación:** [`tests/test_consistencia.py`](../../tests/test_consistencia.py) (6 passed).
* **Decisión de Arquitectura Asociada:** [ADR-0012 — Modelo de almacenamiento en SQLite y costo de reversión](../adr/0012-modelo-almacenamiento-sqlite-costo-reversion.md).
