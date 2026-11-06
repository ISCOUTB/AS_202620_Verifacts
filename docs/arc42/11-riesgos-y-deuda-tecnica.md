# arc42 — Sección 11: Riesgos y deuda técnica

Esta sección reúne los modos de fallo y riesgos conocidos de VeriFacts, **con su estado real en el
código** (commit `3544894`). Distingue tres estados y no presenta como aplicado lo que solo está
diseñado:

- **Implementado**: existe en el código y tiene una prueba citable.
- **Parcial**: el sistema se comporta de forma controlada, pero no como lo describe la mitigación prevista.
- **Pendiente**: solo existe como diseño o plan.

El análisis detallado de los modos MF-01 a MF-06 está en
[`docs/entregas/entrega-modos-fallo-idempotencia-adr.md`](../entregas/entrega-modos-fallo-idempotencia-adr.md);
la decisión de no extraer el módulo, en el [ADR-0009](../adr/0009-decision-extraccion-modulo-analisis.md);
la decisión de datos más costosa de revertir, en el [ADR-0012](../adr/0012-modelo-almacenamiento-sqlite-costo-reversion.md).
El modelado formal de amenazas (STRIDE/OWASP API) y los riesgos de privacidad (AM-01 a AM-08) están consolidados en [`docs/entregas/entrega-seguridad-amenazas-dependencias-privacidad.md`](../entregas/entrega-seguridad-amenazas-dependencias-privacidad.md).

## 11.1 Modos de fallo y riesgos

| ID | Riesgo / modo de fallo | Prob. | Impacto | Mitigación prevista | Estado | Evidencia o plan |
|---|---|---|---|---|---|---|
| MF-01 | La URL externa no responde o responde lento (timeout) | Media | Alto (Q-01) | Timeout de 4 s en la descarga y respuesta 504 | **Pendiente** | `extract_from_url` llama a `trafilatura.fetch_url(url)` sin timeout propio (usa el valor por defecto de la biblioteca) y no distingue el timeout de otros fallos. Un fallo de descarga ya se traduce a 400, no a 500 (ver MF-02). |
| MF-02 | El sitio bloquea el scraping o devuelve error HTTP | Media | Medio | Error controlado con mensaje claro (422) | **Parcial** | Descarga fallida y extracción vacía devuelven **400** con mensaje, no 500: `tests/test_url_ingestion.py` (`..._fetch_failure_returns_400`, `..._extraction_empty_returns_400`). Se mantiene 400 porque así lo fija el contrato [`openapi.yaml`](../contracts/openapi.yaml); 422 queda como mejora. |
| MF-03 | Contenido gigante agota memoria o CPU | Baja | Alto | Límite de longitud y respuesta 413 | **Pendiente** | No hay `MAX_CONTENT_LENGTH` ni `max_length` en `AnalysisRequest` ni en `normalize_content`. Plan: validar el tamaño antes de normalizar. |
| MF-04 | SQLite bloqueada por escrituras concurrentes | Baja | Medio | WAL, `busy_timeout` y reintento con espera | **Parcial** | No se activa WAL ni reintento. El módulo `sqlite3` de Python espera hasta 5 s por defecto antes de fallar con `database is locked`; el proceso es único (`run.py`). |
| MF-05 | Se pierde la confirmación y el cliente reintenta (duplicado) | Media | Medio | `Idempotency-Key` o huella del contenido con tabla de deduplicación | **Pendiente** (diseño) | Hoy cada `POST /analysis` crea un registro nuevo: `tests/test_consistencia.py::test_post_no_es_idempotente_pero_el_calculo_es_determinista`. |
| MF-06 | Un cambio de pesos o umbrales altera las clasificaciones | Media | Alto (Q-05) | Pruebas de límites en CI | **Implementado** | `tests/test_boundaries.py`, `tests/test_scoring_boundaries.py`, `tests/test_rule_modification.py`; se ejecutan en el job `Tests` de CI. El bloqueo de la fusión depende de la protección de rama, que no está verificada. |
| MF-07 | SSRF: la API descarga cualquier URL que envíe un cliente | Media | Alto | Aceptar solo `http`/`https`, rechazar IP privadas, loopback y de enlace local, limitar redirecciones | **Pendiente** | `extract_from_url` no valida esquema ni destino. El contenido extraído se guarda en `content` y se devuelve en `GET /analysis/{id}`. Con el despliegue en el laboratorio, la API puede alcanzar la red interna del servidor. |
| MF-08 | El historial es global: cualquier visitante lee el texto que enviaron otros | Alta | Alto | No exponer `content` en el listado, retención limitada, o identidad por sesión | **Pendiente** | `GET /analysis` y `GET /analysis/{id}` no tienen autenticación y los `id` son enteros consecutivos. Tensión con [R-DAT-01](02-restricciones.md). Decisión y costo de reversión en el [ADR-0011](../adr/0011-historial-registro-unico-sin-propietario.md) y [ADR-0012](../adr/0012-modelo-almacenamiento-sqlite-costo-reversion.md). |
| MF-09 | Tráfico sin cifrar en el despliegue del laboratorio | Alta | Medio | Dominio con certificado válido | **Mitigado** | Resuelto con el subdominio institucional https://verifacts.iscoutb.dev servido bajo HTTPS válido con terminación TLS en Cloudflare y Traefik. Se retiró el dominio sslip.io no seguro. |
| MF-10 | Caída del servidor del laboratorio o pérdida del volumen | Baja | Alto | Réplica o copia de seguridad del volumen | **Pendiente** | Un solo servidor; Volume Backups de Dokploy no está configurado. Render queda como despliegue secundario. |
| MF-11 | Un push parcial a `master` dispara un despliegue fallido | Alta | Bajo | Subir los cambios de despliegue en un solo push, o acotar *Watch Paths* | **Parcial** | Observado el 2026-10-19 con el commit `f721a9d` (ADR-0010). |

## 11.2 Deuda técnica

| ID | Deuda | Plan de cierre |
|---|---|---|
| DT-01 | La paginación por `OFFSET` y el total (`X-Total-Count`) son consultas separadas: puede repetirse un elemento entre páginas | Paginación por cursor (`id < último_id`) o consulta única; requiere cambiar el contrato. Caracterizada en `tests/test_consistencia.py`. |
| DT-02 | Las mitigaciones MF-01 a MF-05 y MF-07 a MF-08 solo están diseñadas | Implementar por prioridad: MF-07, MF-08, MF-01, MF-03, MF-05. Cada una con su prueba de fallo (no respuesta, respuesta tardía, duplicación). |
| DT-03 | No hay un enlace público al último run en verde de `Tests` y de `SonarCloud` ni al estado del Quality Gate | Enlazar los runs en [despliegue.md](../despliegue.md) tras cada entrega; el schedule de `keepalive.yml` se desactivó para no desplazar esos runs. |
| DT-04 | Las pruebas de URL usan descargas simuladas, no una integración real | Añadir pruebas con servidor local lento y que no responde cuando se implemente el timeout. |

## 11.3 Orden de cierre propuesto

1. MF-07 (SSRF) y MF-08 (historial global): afectan a datos de terceros y al servidor.
2. MF-01 y MF-03: timeout y tamaño máximo; dan respuestas 504 y 413 verificables.
3. MF-05: idempotencia, según el diseño de la entrega S11.
4. ~~MF-09: dominio con certificado~~ (Mitigado en producción bajo https://verifacts.iscoutb.dev con SSL Cloudflare).

## 11.4 Riesgos y observaciones señaladas en la revisión de pares (Semana 14)

Durante la sesión formal de coevaluación arquitectónica de la Semana 14, equipos de pares evaluaron el diseño, el repositorio, los escenarios de calidad y el despliegue en producción de VeriFacts (siguiendo los principios de análisis ATAM y detección de cuellos de botella). 

A continuación se incorporan formalmente los hallazgos señalados por los pares evaluadores a la gestión de riesgos y deuda técnica del proyecto:

| ID Par | Hallazgo señalado por los pares | Atributo afectado | Clasificación arquitectónica | Estado real | Decisión y plan de mitigación del equipo |
|---|---|---|---|---|---|
| **RP-01** | **Ingesta de URLs externas sin restricción de destinos internos ni esquema (Riesgo SSRF).** Los pares evidenciaron que la API descarga cualquier URL enviada por el cliente sin validar si apunta a redes privadas (`127.0.0.1`, `10.0.0.0/8`, `192.168.0.0/16`) o a esquemas no HTTP (`file://`, `ftp://`). En el servidor del laboratorio, esto permitiría a un atacante escanear la red interna del servidor Dokploy. | Seguridad (Confidencialidad e Integridad) | Modo de fallo / Vulnerabilidad (mapeado a **MF-07**) | **Pendiente** | Se asume el hallazgo como prioritario (P1). Mitigación planificada: parseo estricto del host, resolución DNS previa para descartar IPs privadas/loopback/enlace local, restricción exclusiva a esquemas `http` y `https`, y limitación de saltos de redirección. Documentado en detalle en la entrega S13. |
| **RP-02** | **Historial global público sin autenticación ni segregación por propietario (Riesgo IDOR y privacidad de datos).** Los pares señalaron que `GET /analysis` y `GET /analysis/{id}` exponen la totalidad de los análisis efectuados en la plataforma, y al emplear identificadores autoincrementales predecibles (enteros consecutivos `1, 2, 3...`), cualquier visitante puede enumerar y leer textos personales o sensibles analizados por otros. | Privacidad (Habeas Data) y Seguridad | Modo de fallo / Violación de privacidad (mapeado a **MF-08**) | **Pendiente** (Diseño) | Identificado en los [ADR-0011](../adr/0011-historial-registro-unico-sin-propietario.md) y [ADR-0012](../adr/0012-modelo-almacenamiento-sqlite-costo-reversion.md) como la decisión de datos más costosa de revertir (40–80 horas). Se mantiene honestamente como deuda técnica aceptada para el prototipo académico actual. Plan de cierre: anonimizar/enmascarar el campo `content` en el listado y migrar los identificadores a UUID v4. |
| **RP-03** | **Falta de cuota o límite de longitud en el cuerpo de la solicitud (`MAX_CONTENT_LENGTH` / HTTP 413).** Los pares observaron que aunque el escenario Q-01 fija como estímulo 10.000 caracteres, el endpoint `POST /analysis` no valida un límite superior en FastAPI ni en Pydantic (`AnalysisRequest`), permitiendo envíos de payloads masivos (ej. decenas de MB) que saturarían la memoria del worker. | Rendimiento y Disponibilidad | Modo de fallo / Denegación de servicio (mapeado a **MF-03**) | **Pendiente** | Se acepta la observación. Plan de mitigación: incorporar validación `Field(..., max_length=50_000)` en el modelo Pydantic `AnalysisRequest` y middleware de descarte temprano en Nginx (`client_max_body_size 1M`) retornando HTTP 413 Payload Too Large. |
| **RP-04** | **Bloqueo de scraping o latencia indeterminada en descarga de URLs externas (Falta de timeout propio).** Los pares advirtieron que la llamada a `trafilatura.fetch_url(url)` es síncrona y depende del timeout por defecto de la biblioteca externa, lo que puede congelar el hilo de atención ante sitios lentos o caídos. | Rendimiento (Q-01) y Robustez | Modo de fallo (mapeado a **MF-01** y **MF-02**) | **Parcial** | MF-02 devuelve error 400 controlado ante fallo de extracción (`tests/test_url_ingestion.py`). Para MF-01, se planifica implementar un timeout propio de 4 segundos con respuesta HTTP 504 Gateway Timeout. La justificación de mantener la integración síncrona en lugar de añadir cola de mensajería está documentada en el [ADR-0013](../adr/0013-no-incorporar-mensajeria-asincrona.md). |
| **RP-05** | **Riesgo de contención y concurrencia sobre la base de datos SQLite en producción.** Los pares cuestionaron si el archivo SQLite monoproceso en el volumen montado (`/data/verifacts.db`) sufrirá bloqueos (`database is locked`) ante ráfagas concurrentes de peticiones de análisis. | Rendimiento (Concurrencia) | Modo de fallo (mapeado a **MF-04**) | **Parcial** | SQLite cuenta con un `busy_timeout` de 5 s por defecto en el driver de Python. La mitigación diseñada para eliminar la contención entre lectores y escritores es habilitar `PRAGMA journal_mode=WAL;` en `app/persistence/repository.py::initialize_database()`. |
| **RP-06** | **Degradación severa del tiempo de respuesta tras inactividad (Cold Start) en Render.** Los pares observaron en la evidencia de la Semana 10 que la primera petición tras 20 minutos de inactividad tardó 22,4 s (violando el umbral de 3 s de Q-01). | Rendimiento (Q-01) y Disponibilidad | Riesgo operacional de infraestructura | **Mitigado** | Resuelto definitivamente mediante la migración del despliegue oficial al servidor del laboratorio UTB sobre Dokploy (`https://verifacts.iscoutb.dev`), empleando contenedores Docker continuos con SQLite persistente en volumen, eliminando por completo el apagado por inactividad. |
