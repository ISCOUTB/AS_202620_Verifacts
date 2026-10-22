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
| MF-09 | Tráfico sin cifrar en el despliegue del laboratorio | Alta | Medio | Dominio con certificado válido | **Pendiente** | El dominio `sslip.io` solo sirve HTTP (ver [ADR-0010](../adr/0010-despliegue-laboratorio-dokploy.md)). En el celular los navegadores que fuerzan HTTPS muestran «conexión no privada»; ver [despliegue.md](../despliegue.md). |
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
4. MF-09: dominio con certificado, cuando el profesor lo asigne.
