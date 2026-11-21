# VeriFacts — Documento Guía del Sistema Integrado y Respuesta al Desafío Final (3 Páginas)

**Asignatura:** Arquitectura de Software · **Organización:** ISCOUTB  
**Proyecto:** VeriFacts — Plataforma Modular de Detección de Indicadores de Desinformación  
**Equipo:** Pedro Jose Castro Blanquicett, Cristian David Cardeno Gulloso  
**Repositorio Oficial:** [https://github.com/ISCOUTB/AS_202620_Verifacts](https://github.com/ISCOUTB/AS_202620_Verifacts)  
**Enlace al Commit Etiquetado Final (`entrega-final`):** [https://github.com/ISCOUTB/AS_202620_Verifacts/tree/entrega-final](https://github.com/ISCOUTB/AS_202620_Verifacts/tree/entrega-final)  
**URL Oficial del Sistema en Producción (Dokploy Lab UTB):** [https://verifacts.iscoutb.dev](https://verifacts.iscoutb.dev)  
- **Interfaz Web (React):** [https://verifacts.iscoutb.dev](https://verifacts.iscoutb.dev) · **Healthcheck:** [https://verifacts.iscoutb.dev/health](https://verifacts.iscoutb.dev/health)  
- **Swagger / OpenAPI:** [https://verifacts.iscoutb.dev/docs](https://verifacts.iscoutb.dev/docs) · **Métricas Prometheus:** [https://verifacts.iscoutb.dev/metrics](https://verifacts.iscoutb.dev/metrics)  

---

## PÁGINA 1 · Comportamiento Actual del Sistema Integrado y Mapa de Integración S11–S14

### 1.1 Comportamiento Actual del Sistema (Qué hace hoy en código y producción)

VeriFacts opera en producción como un **monolito modular** en Python 3.12 / FastAPI con persistencia en **SQLite** sobre volumen Docker permanente (`/data/verifacts.db`), consumido por una **interfaz web en React 18 / TypeScript** servida por **Nginx** bajo un único dominio institucional con certificado TLS válido gestionado vía Cloudflare y Traefik (`https://verifacts.iscoutb.dev`).

1. **Cortes verticales ejecutables y verificados de extremo a extremo:**
   - **Análisis de contenido (`POST /analysis`):** Recibe un texto directo o una URL (mutuamente excluyentes, validados con HTTP 422 en el esquema Pydantic). Para URLs, `Content` descarga y extrae el cuerpo principal con `trafilatura` (respondiendo HTTP 400 controlado si falla la descarga o la extracción queda vacía). Luego normaliza el texto, `Analysis` (`RuleAnalyzer`) evalúa de forma determinista las reglas heurísticas (lenguaje sensacionalista, exceso de mayúsculas, afirmaciones absolutas), `Scoring` calcula la puntuación acotada (`0–100`) y clasificación (`Confiable`, `Riesgo medio`, `Riesgo alto`), y `Persistence` ejecuta `INSERT` + `commit` atómico en SQLite releyendo el registro confirmado antes de responder.
   - **Historial paginado (`GET /analysis?limit=20&offset=0`):** Retorna la lista ordenada cronológicamente y expone el total físico en la cabecera `X-Total-Count`. Tras cada análisis exitoso, el frontend invalida la vista ejecutando `history.refresh()`.
   - **Consulta puntual (`GET /analysis/{id}`):** Recupera un análisis inmutable por su identificador con garantía *read-your-writes*, o retorna HTTP 404 sin efectos laterales si no existe.
   - **Observabilidad (`GET /health`, `GET /metrics`, logs JSON):** Emite una línea JSON estructurada por petición (`request_id`, ruta, estado HTTP, `duration_ms`) y expone contadores Prometheus en memoria.
2. **Batería de verificación automatizada y aceptación funcional:**
   - **66 pruebas automatizadas en verde (`python -m pytest -q`)** ejecutadas en cada push en GitHub Actions: salud (`test_health.py`), flujo extremo a extremo (`test_analysis.py`), historial (`test_analysis_history.py`), cambio localizado de regla para Q-03 (`test_rule_modification.py`), contrato ejecutable OpenAPI 3.1 (`test_contract.py`, 12 pruebas), fronteras de módulos y umbrales de scoring (`test_boundaries.py`, `test_scoring_boundaries.py`, 15 pruebas), fallos de ingesta URL (`test_url_ingestion.py`, 5 pruebas), consistencia de datos S12 (`test_consistencia.py`, 6 pruebas), observabilidad (`test_observability.py`) y prototipo aislado de mensajería (`test_messaging.py`, 16 pruebas).
   - **Aceptación funcional reproducible:** Script [`aceptar.bat`](../../aceptar.bat) y registro real [`evidencia-aceptacion.txt`](../../evidencia-aceptacion.txt) con 8 casos (`C1` a `C8`) verificando salud, UI, texto, URL válida, URL inválida (400), texto vacío (422), historial (200) e ID inexistente (404).
3. **Declaración honesta del alcance (Implementado vs. Parcial vs. Pendiente en [`arc42 §11`](../arc42/11-riesgos-y-deuda-tecnica.md)):**
   - **Implementado / Mitigado:** Pruebas bloqueantes de límites y pesos (**MF-06 / AM-08**), dominio institucional HTTPS y eliminación de *cold start* en Dokploy (**MF-09 / RP-06**), consultas SQL parametrizadas (**AM-06**), caché HTTP inmutable de 1 año en Nginx para activos estáticos del frontend (`arc42 §8.7`), y saneamiento de dependencias (**AM-07**, `pytest>=9.0.3`).
   - **Parcial:** Fallo de descarga/extracción URL devuelve HTTP 400 conforme a `openapi.yaml` en lugar de 422 (**MF-02**); SQLite opera con `busy_timeout` nativo de 5 s en proceso único, sin activar aún modo WAL (**MF-04 / RP-05**).
   - **Pendiente (solo diseño documentado):** Timeout propio de 4 s con respuesta HTTP 504 en scraping (**MF-01 / RP-04**), tope `MAX_CONTENT_LENGTH` con respuesta HTTP 413 (**MF-03 / RP-03**), clave `Idempotency-Key` con tabla `idempotency_records` (**MF-05**), filtro anti-SSRF de IPs privadas en `extract_from_url` (**MF-07 / RP-01**) y segregación/anonimización del historial global sin propietario (**MF-08 / RP-02**).

### 1.2 Mapa de Integración de las Evidencias S11–S14, Taller y Revisión entre Pares

Cada incremento semanal se integró en la arquitectura maestra (`arc42`, `aspectos.md`, `ADR` y suite de pruebas):

| Hito / Semana | Qué se integró al repositorio | Aspecto ([`aspectos.md`](../aspectos.md)) | Sección `arc42` | ADR Asociado | Código / Pruebas / Evidencia |
|---|---|:---:|---|---|---|
| **S11: Resiliencia, Modos de Fallo, Idempotencia y Extracción** | Análisis del pipeline crítico `POST /analysis`, matriz `MF-01` a `MF-06` con columna de estado real, diseño de máquina de estados de idempotencia y decisión de no extraer el módulo de análisis. | **A-08** | [§11.1–§11.3](../arc42/11-riesgos-y-deuda-tecnica.md) | [ADR-0009](../adr/0009-decision-extraccion-modulo-analisis.md)<br>[ADR-0003](../adr/0003-integracion-sincrona.md) | [`entrega-modos-fallo-idempotencia-adr.md`](entrega-modos-fallo-idempotencia-adr.md) · [`tests/test_url_ingestion.py`](../../tests/test_url_ingestion.py) (5 passed) |
| **S12: Consistencia, Caché, Invalidación, Costo de Reversión y Dokploy** | Matriz de 7 columnas operación→garantía, diseño de caché en 3 dimensiones (qué/dónde/cuánto), invalidación tras escritura, costo de reversión de datos y despliegue en laboratorio UTB. | **A-09**<br>**A-10** | [§7](../arc42/07-despliegue.md)<br>[§8.6–§8.9](../arc42/08-conceptos-transversales.md) | [ADR-0010](../adr/0010-despliegue-laboratorio-dokploy.md)<br>[ADR-0011](../adr/0011-historial-registro-unico-sin-propietario.md)<br>[ADR-0012](../adr/0012-modelo-almacenamiento-sqlite-costo-reversion.md) | [`entrega-consistencia-cache-costo-reversion.md`](entrega-consistencia-cache-costo-reversion.md) · [`tests/test_consistencia.py`](../../tests/test_consistencia.py) (6 passed) · [`despliegue.md`](../despliegue.md) |
| **Taller S13: Mensajería Asíncrona (Prototipo Aislado)** | Contrato versionado `verifacts.analysis.requested`, broker en memoria *at-least-once*, consumidor idempotente, *exponential backoff*, DLQ y telemetría por `message_id`, aislado de `app/`. | **A-11** | [§8.9](../arc42/08-conceptos-transversales.md)<br>[§9](../arc42/09-decisiones-arquitectonicas.md) | [ADR-0013](../adr/0013-no-incorporar-mensajeria-asincrona.md) | `experiments/messaging/` · [`tests/test_messaging.py`](../../tests/test_messaging.py) (16 passed) · [`docs/mensajeria/`](../mensajeria/contrato-mensaje.md) |
| **S13: Seguridad, Amenazas, Dependencias y Privacidad** | DFD con límites de confianza, matriz STRIDE + OWASP API Top 10 (`AM-01` a `AM-08`), auditoría SCA backend/frontend, barrido histórico de secretos (327 commits) y política *Privacy by Design*. | **A-12** | [§8.10–§8.11](../arc42/08-conceptos-transversales.md)<br>[§11.1](../arc42/11-riesgos-y-deuda-tecnica.md) | [ADR-0007](../adr/0007-no-incorporar-componente-generativo.md)<br>[ADR-0011](../adr/0011-historial-registro-unico-sin-propietario.md) | [`entrega-seguridad-amenazas-dependencias-privacidad.md`](entrega-seguridad-amenazas-dependencias-privacidad.md) · [`revision-secretos-s12.md`](../evidencia/revision-secretos-s12.md) |
| **S14: Medición de Escenarios en Producción y Revisión de Pares** | Evaluación ATAM, contraste empírico de Q-01 y Q-05 en Local vs. Render vs. Dokploy UTB, descomposición de cuellos de botella e incorporación formal de hallazgos de pares (`RP-01` a `RP-06`). | **A-13** | [§10](../arc42/10-requisitos-de-calidad.md)<br>[§11.4](../arc42/11-riesgos-y-deuda-tecnica.md#114-riesgos-y-observaciones-señaladas-en-la-revisión-de-pares-semana-14) | [ADR-0008](../adr/0008-mantener-render-mitigar-arranque-frio.md)<br>[ADR-0010](../adr/0010-despliegue-laboratorio-dokploy.md) | [`entrega-medicion-escenario-revision-pares.md`](entrega-medicion-escenario-revision-pares.md) · [`scripts/medir_render.py`](../../scripts/medir_render.py) |

---

## PÁGINA 2 · Justificación de la Evolución Arquitectónica y Decisiones Clave

La evolución de VeriFacts desde el Corte 1 hasta la Entrega Final estuvo guiada por la **evidencia empírica** sobre los cinco escenarios de calidad (`Q-01` a `Q-05`) y el principio de **evitar complejidad accidental** cuando las mediciones demostraron que una estructura simple y bien modularizada cumplía los umbrales con amplio margen.

### 2.1 Por qué se preservó el Monolito Modular y no se extrajo el Módulo de Análisis (`ADR-0001`, `ADR-0002`, `ADR-0009`)
- **Contexto de evolución:** Tras el Corte 1 se añadieron la extracción de contenido desde URLs (`trafilatura`), el historial paginado y el cliente web en React. En la Semana 11 se evaluó formalmente si el pipeline de ingesta y análisis debía extraerse a un microservicio independiente ([ADR-0009](../adr/0009-decision-extraccion-modulo-analisis.md)).
- **Justificación técnica:**
  1. **Latencia de cómputo despreciable:** El motor `RuleAnalyzer` + `Scoring` procesa 10.000 caracteres en memoria en **$< 15\text{ ms}$**. Extraerlo a otro contenedor cambiaría llamadas a funciones en memoria por serialización HTTP/JSON sobre red, degradando `Q-01` sin ganancia de escalabilidad.
  2. **Transaccionalidad simple sin Sagas:** Mantener los tres contextos delimitados (*Ingesta y Presentación*, *Análisis de Contenido*, *Historial de Análisis*) dentro del mismo proceso permite que la única mutación de estado ocurra en una transacción local ACID en SQLite (`save_analysis`), haciendo innecesaria una Saga distribuida.
  3. **Fronteras internas vigiladas por pruebas:** El bajo acoplamiento del monolito modular se protege en CI con [`tests/test_boundaries.py`](../../tests/test_boundaries.py) (ningún módulo fuera de `repository.py` importa `sqlite3`, y `scoring` solo consume la interfaz pública `analysis.service`) y [`tests/test_contract.py`](../../tests/test_contract.py) (contrato OpenAPI 3.1 inmutable hacia el frontend).

### 2.2 Por qué la Integración se mantuvo Síncrona y el Prototipo de Mensajería quedó Aislado (`ADR-0003`, `ADR-0013`)
- **Evaluación en el Taller S13:** La única operación con dependencia externa es `POST /analysis` con origen `url`. Para evaluar su desacoplamiento asíncrono sin comprometer la estabilidad del producto, se construyó un prototipo completo en [`experiments/messaging/`](../../experiments/messaging/) con contrato formal versionado (`verifacts.analysis.requested v1`), consumidor idempotente por `message_id`, reintentos con *exponential backoff* ante fallos transitorios (`FetchTimeoutError`, `Upstream5xxError`) y desvío a *Dead Letter Queue* (DLQ) ante fallos permanentes, verificado por **16 pruebas unitarias** en [`tests/test_messaging.py`](../../tests/test_messaging.py).
- **Decisión arquitectónica ([ADR-0013](../adr/0013-no-incorporar-mensajeria-asincrona.md)):** Se decidió **no incorporar** el broker al sistema en producción porque:
  1. **Experiencia de usuario interactiva:** El usuario espera el diagnóstico de la noticia en pantalla inmediatamente tras pulsar «Analizar». Pasar a `202 Accepted` obligaría a implementar *polling* o WebSockets en React, aumentando la latencia percibida.
  2. **Cumplimiento holgado del presupuesto de tiempo:** Con un $P95 = 195,4\text{ ms}$ en producción (frente al umbral de $3.000\text{ ms}$ de `Q-01`), la vía síncrona dispone de más de $2,8\text{ s}$ de margen. La falla de sitios externos lentos se mitiga con un timeout síncrono acotado (`MF-01`), no con una cola de mensajería.

### 2.3 Evolución del Despliegue y Resolución del Cuello de Botella de *Cold Start* (`ADR-0004`, `ADR-0005`, `ADR-0008`, `ADR-0010`)
La arquitectura de despliegue evolucionó en tres etapas guiadas por las mediciones del escenario **Q-01** ($P95 \le 3.000\text{ ms}$ con payload de 10.000 caracteres) y **Q-05** ($100\%$ repetibilidad):

| Etapa de Infraestructura | Muestra ($n$) | Mediana | P95 Medido | Umbral Q-01 | Margen | Veredicto Q-01 / Q-05 | Hallazgo Arquitectónico y Decisión Tomada |
|---|---:|---:|---:|---:|---:|:---:|---|
| **1. Local (S9)** (`127.0.0.1`, SQLite local) | 200 | 16,6 ms | **46,9 ms** | $\le 3.000\text{ ms}$ | $63,9\times$ | **CUMPLE / 100%** | Demostró que el cómputo (`<15 ms`) y SQLite (`<5 ms`) no son cuello de botella. |
| **2. Prototipo Serverless AWS SAM (S8)** | 10 | 21,0 ms | **634,6 ms** (frío) | $\le 3.000\text{ ms}$ | $4,7\times$ | **CUMPLE / 100%** | Descartado como plataforma primaria ([ADR-0005](../adr/0005-comparacion-lambda-render.md)) por pérdida de SQLite local y fricción operativa. |
| **3. Render Cloud — Caliente (S10)** | 50 | 197,1 ms | **211,3 ms** | $\le 3.000\text{ ms}$ | $14,2\times$ | **CUMPLE / 100%** | En operación activa cumple holgadamente; filesystem efímero pierde la BD en redeploy. |
| **4. Render Cloud — En Frío (S10)** *(tras 20 min sin tráfico)* | 3 | 22.348 ms | **22.450,0 ms** | $\le 3.000\text{ ms}$ | **$-7,5\times$** | **NO CUMPLE / 100%** | El plan gratuito suspende el contenedor tras 15 min de inactividad, violando `Q-01` ([ADR-0008](../adr/0008-mantener-render-mitigar-arranque-frio.md)). |
| **5. Producción Oficial Dokploy UTB (S12–S14)** (`https://verifacts.iscoutb.dev`) | 50 | 178,2 ms | **195,4 ms** | $\le 3.000\text{ ms}$ | **$15,3\times$** | **CUMPLE / 100%** | **Solución definitiva ([ADR-0010](../adr/0010-despliegue-laboratorio-dokploy.md)):** Contenedores `web` + `api` activos 24/7 sin *cold start*, proxy Nginx en dominio único con SSL Cloudflare y volumen persistente `verifacts_data`. |

- **Descomposición del cuello de botella en producción ($195,4\text{ ms}$ totales):** Más del $80\%$ ($\approx 148\text{ ms}$) corresponde a transporte WAN, *handshake* TLS en Cloudflare y enrutamiento Traefik→Nginx; menos del $10\%$ ($\approx 15\text{ ms}$) al motor heurístico en memoria; y menos del $5\%$ ($\approx 5\text{ ms}$) a la escritura síncrona en SQLite.

### 2.4 Consistencia por Operación, Política de Caché y Decisión de Datos más Costosa de Revertir (`ADR-0006`, `ADR-0007`, `ADR-0011`, `ADR-0012`)
1. **Determinismo y Semántica Controlada por el Equipo (`ADR-0006`, `ADR-0007`):** Se rechazó incorporar un LLM generativo en ejecución (vulneraría `Q-01` por latencia externa, `Q-05` por no determinismo y `Q-04` por opacidad) y se prohibió alterar pesos/umbrales arbitrariamente sin ADR y pruebas de mutación ([`auditoria-s9.md`](../auditoria-s9.md)).
2. **Garantías de Consistencia y Política de Caché (`arc42 §8.6–§8.8`):** `POST /analysis` garantiza consistencia fuerte en un nodo tras commit; `GET /analysis/{id}` garantiza *read-your-writes* sobre registros inmutables; `GET /analysis` ofrece consistencia eventual refrescada activamente por el frontend (`history.refresh()`). Se justificó **no implementar caché en el backend** (cómputo $< 15\text{ ms}$, consulta SQLite $< 2\text{ ms}$), manteniendo como única caché activa la de activos estáticos en Nginx (`/assets/` con `expires 1y; immutable`).
3. **Decisión de Datos más Costosa de Revertir ([ADR-0012](../adr/0012-modelo-almacenamiento-sqlite-costo-reversion.md)):** Al comparar cuantitativamente las 5 decisiones de datos del sistema, se demostró que **almacenar el contenido completo en un historial único sin propietario (`ADR-0011`)** es la más costosa de revertir (**40–80 horas-persona**, frente a 16–24 h de migrar SQLite a PostgreSQL o 4–8 h de cambiar el formato de `factors`), porque acumula datos históricos anónimos imposibles de atribuir retroactivamente a un usuario y exige rediseñar contratos, interfaz de autenticación y políticas de Habeas Data.

---

## PÁGINA 3 · Respuesta al Desafío Final, Revisión entre Pares y Guía de Verificación

### 3.1 Respuesta Arquitectónica al Desafío Final Asignado: Resolución de Tensiones y Madurez del Sistema

El desafío final exige demostrar cómo las piezas desarrolladas entre las semanas 1 y 14 forman un **sistema integrado coherente**, capaz de sostener su comportamiento en producción y de justificar rigurosamente sus compromisos (*trade-offs*) y su plan de evolución:

1. **Tensión 1 — Rendimiento (`Q-01`, $\le 3.000\text{ ms}$) vs. Explicabilidad y Repetibilidad (`Q-04`, `Q-05`, $100\%$):**
   - *Resolución:* Se priorizó un motor heurístico determinista en memoria (`RuleAnalyzer` + `Scoring`) gobernado por constantes auditables (`ADR-0006`) y protegido por 15 pruebas de límites y mutación en CI (`MF-06`), descartando componentes generativos (`ADR-0007`). Resultado en producción: **$P95 = 195,4\text{ ms}$** y **$100\%$ de repetibilidad**.
2. **Tensión 2 — Simplicidad Operativa del Monolito Modular (`Q-02`, `Q-03`) vs. Resiliencia en la Frontera Externa (`POST /analysis` con URL):**
   - *Resolución:* Se preservó el monolito modular sin extraer microservicios (`ADR-0009`) ni introducir colas de mensajería en el producto (`ADR-0013`), aislando la captura de errores de red en `app/modules/content/service.py` (retornando HTTP 400 controlado y probado en `tests/test_url_ingestion.py`) y dejando diseñado el contrato asíncrono en `experiments/messaging/` como activo reutilizable solo si en el futuro se incorpora procesamiento NLP pesado.
3. **Tensión 3 — Trazabilidad Abierta del Historial (`R-DAT-01`) vs. Seguridad Perimetral y Privacidad de Datos (S13 + Revisión de Pares S14):**
   - *Resolución:* En lugar de ocultar limitaciones o aplicar parches apresurados que rompieran el contrato `openapi.yaml` (`v1.0.0`), el equipo auditó las amenazas con STRIDE/OWASP (`AM-01` a `AM-08`), asimiló los **6 hallazgos de la revisión entre pares (`RP-01` a `RP-06`)** en [`arc42 §11.4`](../arc42/11-riesgos-y-deuda-tecnica.md#114-riesgos-y-observaciones-señaladas-en-la-revisión-de-pares-semana-14) y ejecutó de inmediato la mitigación de infraestructura (`RP-06` / `MF-09`), dejando priorizada la hoja de ruta de cierre para el siguiente ciclo.

### 3.2 Síntesis Integrada de Riesgos, Seguridad (S13) y Revisión entre Pares (S14) en `arc42 §11`

| Prioridad | ID Par / Modo Fallo / Amenaza | Hallazgo Integrado (Pares + Auditoría S11–S14) | Estado Real en Código | Evidencia Actual o Diseño Técnico de Cierre |
|:---:|---|---|:---:|---|
| **Resuelto** | **RP-06 · MF-09 · AM-05** | *Cold start* de 22,4 s en Render y tráfico HTTP sin cifrar (`sslip.io`) en el laboratorio. | **Mitigado** | Migración a Dokploy UTB con contenedor continuo ($P95 = 195,4\text{ ms}$) y dominio [`https://verifacts.iscoutb.dev`](https://verifacts.iscoutb.dev) bajo SSL Cloudflare ([ADR-0010](../adr/0010-despliegue-laboratorio-dokploy.md)). |
| **Resuelto** | **MF-06 · AM-06 · AM-07 · AM-08** | Regresión en reglas de scoring, inyección SQL en persistencia y CVEs en dependencias (`pytest`). | **Implementado** | `test_boundaries.py` y `test_scoring_boundaries.py` (15 passed); SQL parametrizado (`?`) en `repository.py:108`; SCA limpio con `pytest>=9.0.3` y 0 secretos en 327 commits. |
| **P1** | **RP-01 · MF-07 · AM-01** | **Riesgo SSRF en ingesta de URL:** `extract_from_url` no filtra IPs privadas (`127.0.0.1`, RFC 1918) ni esquemas no HTTP. | **Pendiente** | Diseño en S13/S14: validar esquema `http`/`https`, resolver DNS previo descartando rangos privados/loopback y limitar redirecciones antes de `trafilatura.fetch_url`. |
| **P1** | **RP-02 · MF-08 · AM-04** | **Historial global público con IDs secuenciales (BOLA/IDOR y Habeas Data):** cualquiera lee textos de terceros. | **Pendiente** (Diseño) | Evaluado en [ADR-0011](../adr/0011-historial-registro-unico-sin-propietario.md) y [ADR-0012](../adr/0012-modelo-almacenamiento-sqlite-costo-reversion.md) (40–80 h). Plan: omitir `content` completo en `GET /analysis`, migrar IDs a UUIDv4 y retención de 30 días. |
| **P2** | **RP-03 · MF-03 · AM-02** | **Ausencia de límite de tamaño (`MAX_CONTENT_LENGTH` / HTTP 413):** riesgo de agotamiento de RAM por payloads masivos. | **Pendiente** | Diseño: `Field(..., max_length=50_000)` en `AnalysisRequest`, límite de buffer de 2 MB en scraping y `client_max_body_size 1M` en Nginx devolviendo HTTP 413. |
| **P2** | **RP-04 · MF-01 · MF-02 · AM-03** | **Falta de timeout propio en scraping URL:** sitios lentos bloquean el worker; fallo actual retorna HTTP 400. | **Parcial** | MF-02 retorna HTTP 400 controlado (`test_url_ingestion.py`). Plan para MF-01: timeout estricto de 4 s con respuesta HTTP 504 Gateway Timeout. |
| **P3** | **RP-05 · MF-04 · MF-05** | **Concurrencia en SQLite y duplicados ante reintentos de red en `POST /analysis`.** | **Parcial / Pendiente** | SQLite opera con `busy_timeout` de 5 s; plan: activar `PRAGMA journal_mode=WAL` e implementar cabecera `Idempotency-Key` con tabla `idempotency_records` (S11). |

### 3.3 Guía Rápida de Verificación para el Evaluador (Reproducción en < 2 minutos)

1. **Comprobar el sistema desplegado en producción (`https://verifacts.iscoutb.dev`):**
   ```cmd
   curl -sS https://verifacts.iscoutb.dev/health
   curl -sS -X POST https://verifacts.iscoutb.dev/analysis -H "Content-Type: application/json" -d "{\"text\":\"ESTA NOTICIA ES TOTALMENTE CIERTA!!! Todos deben compartirla!!!\"}"
   curl -sS "https://verifacts.iscoutb.dev/analysis?limit=3&offset=0"
   curl -sS https://verifacts.iscoutb.dev/metrics
   ```
2. **Ejecutar la batería completa de pruebas automatizadas en local (`66 passed`):**
   ```cmd
   git checkout entrega-final
   python -m pytest -q
   ```
3. **Índice rápido de navegación del repositorio en el tag `entrega-final`:**
   - **Documentación maestra:** [`README.md`](../../README.md) · [`docs/aspectos.md`](../aspectos.md) (`A-00` a `A-13`) · [`docs/arc42/`](../arc42/01-introduccion-y-objetivos.md) (§1 a §12) · [`docs/c4/`](../c4/01-contexto.md) (Niveles 1–3) · [`docs/adr/`](../adr/0001-estilo-arquitectonico.md) (`ADR-0001` a `ADR-0013`).
   - **Entregas del corte final:** [S11 Resiliencia e Idempotencia](entrega-modos-fallo-idempotencia-adr.md) · [S12 Consistencia, Caché y Costo de Reversión](entrega-consistencia-cache-costo-reversion.md) · [Taller Mensajería Asíncrona](../mensajeria/contrato-mensaje.md) · [S13 Seguridad, Amenazas, Dependencias y Privacidad](entrega-seguridad-amenazas-dependencias-privacidad.md) · [S14 Medición ATAM y Revisión entre Pares](entrega-medicion-escenario-revision-pares.md).
