# Aspectos arquitectónicos — VeriFacts

## Aspecto principal

El aspecto arquitectónico principal seleccionado es:

**Escalabilidad mediante modularidad.**

La arquitectura debe permitir incorporar nuevos mecanismos de análisis sin
modificar significativamente los demás componentes.

## Matriz de trazabilidad

Columnas del curso: **ID · Aspecto/Preocupación · Escenario · Vista C4 ·
ADR · Ubicación en código · Medida/Criterio · Evidencia de pruebas**
(más una columna de contexto delimitado).

| ID | Aspecto / Preocupación | Escenario | Vista C4 | ADR | Ubicación en código | Medida / Criterio | Evidencia de pruebas | Contexto (mapa-contextos.md) |
|---|---|---|---|---|---|---|---|---|
| A-00 | Disponibilidad del esqueleto | [Q-05](escenarios-de-calidad.md#q-05--repetibilidad-del-resultado) | Contenedor "Aplicación VeriFacts" — [C4 Nivel 2](c4/02-contenedores.md) | [ADR-0001](adr/0001-estilo-arquitectonico.md) | `app/api/routes.py` (`GET /health`) | Responde `200 {"status":"ok"}` de forma repetible ante la misma entrada | `tests/test_health.py` — **1 passed** · CI: job "Tests" en verde, ver [Actions](https://github.com/ISCOUTB/AS_202620_Verifacts/actions) | Ingesta y Presentación |
| A-01 | Escalabilidad — incorporar un nuevo analizador | [Q-02](escenarios-de-calidad.md#q-02--incorporación-de-un-nuevo-analizador) | Contenedor "Aplicación VeriFacts", componente `Analysis` — [C4 Nivel 2](c4/02-contenedores.md) | [ADR-0001](adr/0001-estilo-arquitectonico.md) | `app/modules/analysis/analyzer.py` (`RuleAnalyzer`), `app/modules/analysis/service.py` | El nuevo analizador (`RuleAnalyzer`, 3 reglas) se incorporó sin modificar `API`, `Content` ni `Scoring` | `tests/test_analysis.py` — **1 passed** | Análisis de Contenido |
| A-02 | Mantenibilidad — modificar una regla existente | [Q-03](escenarios-de-calidad.md#q-03--modificación-de-una-regla) | Contenedor "Aplicación VeriFacts", componente `Analysis` — [C4 Nivel 2](c4/02-contenedores.md) | [ADR-0001](adr/0001-estilo-arquitectonico.md) | `app/modules/analysis/analyzer.py` (`absolute_words` en `RuleAnalyzer`) | Modificar una regla no debe producir regresiones en las pruebas existentes | `tests/test_rule_modification.py` — **1 passed**, confirma que `test_health.py` y `test_analysis.py` siguen en verde | Análisis de Contenido |
| A-03 | Confiabilidad — corte vertical completo con persistencia | [Q-05](escenarios-de-calidad.md#q-05--repetibilidad-del-resultado) | Contenedores "Aplicación VeriFacts" y "Base de datos" — [C4 Nivel 2](c4/02-contenedores.md) | [ADR-0001](adr/0001-estilo-arquitectonico.md) | `app/api/routes.py` (`POST /analysis`), `app/persistence/repository.py` | La misma entrada produce el mismo `score`, `classification` y `factors`, y queda persistida y recuperable por `id` | `tests/test_analysis.py` — **1 passed** | Análisis de Contenido → Historial de Análisis |
| A-04 | Bajo acoplamiento — frontend como cliente HTTP independiente | [Q-02](escenarios-de-calidad.md#q-02--incorporación-de-un-nuevo-analizador) | Contenedor "Interfaz web" — [C4 Nivel 2](c4/02-contenedores.md) | [ADR-0002](adr/0002-contextos-sin-cambios.md) | `frontend/src/api/client.ts` | El frontend se incorporó sin agregar lógica de negocio ni tocar los módulos internos del backend (`API`, `Content`, `Analysis`, `Scoring`) | Verificación manual (pasos 17–18 del README); sin prueba de componente automatizada todavía — ver [Pendiente](../README.md#pendiente) | Ingesta y Presentación |
| A-05 | Modificabilidad — contrato de API ejecutable y versionado (S7) | [Q-01](escenarios-de-calidad.md#q-01--tiempo-de-respuesta-del-análisis), [Q-02](escenarios-de-calidad.md#q-02--incorporación-de-un-nuevo-analizador) | Todas las flechas del Contenedor "Aplicación VeriFacts" — [C4 Nivel 2](c4/02-contenedores.md) | [ADR-0003](adr/0003-integracion-sincrona.md) | `docs/contracts/openapi.yaml`, `tests/test_contract.py` | Un cambio incompatible en la respuesta de la API (campo renombrado, tipo cambiado, arreglo envuelto en objeto) rompe el pipeline antes de `master` | `tests/test_contract.py` — **12 passed**; verificado manualmente que renombrar `score`→`risk_score` en `app/api/routes.py` hace fallar 4 de esas pruebas, y que revertir el cambio las vuelve a poner en verde (20 passed en total) | Ingesta y Presentación → Análisis de Contenido → Historial de Análisis |
| A-06 | Confiabilidad e interpretabilidad — pesos, umbrales y significado del resultado en código generado con IA (S9) | [Q-05](escenarios-de-calidad.md#q-05--repetibilidad-del-resultado), [Q-04](escenarios-de-calidad.md#q-04--comprensión-del-resultado), [Q-01](escenarios-de-calidad.md#q-01--tiempo-de-respuesta-del-análisis) | Contenedor "Aplicación VeriFacts", componente `Scoring` — [C4 Nivel 2](c4/02-contenedores.md) | [ADR-0006](adr/0006-semantica-del-resultado.md), [ADR-0007](adr/0007-no-incorporar-componente-generativo.md) | `app/modules/scoring/service.py` (`UMBRAL_RIESGO_MEDIO`, `UMBRAL_RIESGO_ALTO`, `MAX_SCORE`), pesos en `app/modules/analysis/analyzer.py` | Cambiar un peso, umbral o tope sin actualizar ADR y prueba rompe el pipeline; la misma entrada produce el mismo resultado (100 %); P95 ≤ 3 s con 10.000 caracteres | `tests/test_scoring_boundaries.py` — **12 passed**; `tests/test_boundaries.py` — **3 passed** (erosión); de 5 defectos inducidos, la suite previa no detectaba 3 y las pruebas nuevas detectan los 5 ([mutaciones](evidencia/mutaciones-s9.md)); medición local en [evidencia Q-01/Q-05](evidencia/medicion-q01-q05.md); auditoría en [auditoria-s9.md](auditoria-s9.md) | Análisis de Contenido |
| A-07 | Rendimiento y operación — arranque en frío en Render y su mitigación (reto operativo S10) | [Q-01](escenarios-de-calidad.md#q-01--tiempo-de-respuesta-del-análisis) | Contenedor "Aplicación VeriFacts" y su despliegue — [C4 Nivel 2](c4/02-contenedores.md) | [ADR-0008](adr/0008-mantener-render-mitigar-arranque-frio.md), complementa [ADR-0005](adr/0005-comparacion-lambda-render.md) | `render.yaml`, `Dockerfile`, `.github/workflows/keepalive.yml`, `scripts/payload_10k.py`, `scripts/medir_render.py`, `app/observability.py` | P95 ≤ 3.000 ms para `POST /analysis` con 10.000 caracteres; la primera petición tras inactividad también debe responder en ≤ 3 s | [medicion-render-s10.md](evidencia/medicion-render-s10.md): en caliente P95 = 211,3 ms (cumple); primera petición tras 20 min sin tráfico ≈ 22,4 s (no cumple), mitigada con keep-alive cuya efectividad se registra en el mismo documento · CI: Tests y SonarCloud en [Actions](https://github.com/ISCOUTB/AS_202620_Verifacts/actions) | Ingesta y Presentación |
| A-08 | Resiliencia de la integración externa (URL) y modos de fallo (S11) | [Q-01](escenarios-de-calidad.md#q-01--tiempo-de-respuesta-del-análisis), [Q-05](escenarios-de-calidad.md#q-05--repetibilidad-del-resultado) | Contenedor "Aplicación VeriFacts" y flecha hacia el sitio externo — [C4 Nivel 2](c4/02-contenedores.md) | [ADR-0009](adr/0009-decision-extraccion-modulo-analisis.md), [ADR-0003](adr/0003-integracion-sincrona.md) | `app/modules/content/service.py` (`extract_from_url`), `app/api/routes.py` | Un fallo de descarga o extracción responde 400 controlado (no 500). Timeout de 4 s, 504/422, límite de tamaño y WAL están **pendientes** ([arc42 §11](arc42/11-riesgos-y-deuda-tecnica.md)) | `tests/test_url_ingestion.py` — **5 passed** (fallos simulados de descarga y de extracción vacía); no prueban timeout ni 504 | Ingesta y Presentación |
| A-09 | Consistencia de datos, caché e idempotencia (S12) | [Q-05](escenarios-de-calidad.md#q-05--repetibilidad-del-resultado) | Contenedores "Aplicación VeriFacts" y "Base de datos" — [C4 Nivel 2](c4/02-contenedores.md) | [ADR-0011](adr/0011-historial-registro-unico-sin-propietario.md), [ADR-0009](adr/0009-decision-extraccion-modulo-analisis.md) | `app/persistence/repository.py` (`save_analysis`, `get_analysis`, `list_analyses`, `count_analyses`), `app/api/routes.py` | Tabla operación → garantía ([arc42 §8.6](arc42/08-conceptos-transversales.md#86-consistencia-de-datos)); sin caché de aplicación ([§8.7](arc42/08-conceptos-transversales.md#87-política-de-caché)); idempotencia diseñada, no implementada | `tests/test_consistencia.py` — **6 passed** | Historial de Análisis |
| A-10 | Despliegue de referencia en el servidor del laboratorio (S12) | [Q-01](escenarios-de-calidad.md#q-01--tiempo-de-respuesta-del-análisis), [Q-05](escenarios-de-calidad.md#q-05--repetibilidad-del-resultado) | Contenedores "Aplicación VeriFacts", "Interfaz web" y "Base de datos" — [C4 Nivel 2](c4/02-contenedores.md) | [ADR-0010](adr/0010-despliegue-laboratorio-dokploy.md) | `deploy/compose.lab.yaml`, `frontend/Dockerfile`, `frontend/nginx.conf`, `Dockerfile` | La URL del laboratorio responde y el historial persiste tras un redespliegue | Comprobaciones en [despliegue.md](despliegue.md); job `Build y smoke test de la imagen` de CI (solo la imagen de la API) | Ingesta y Presentación · Historial de Análisis |

Los once aspectos caen dentro de Análisis de Contenido, Ingesta y
Presentación o Historial de Análisis (ver
[mapa de contextos](mapa-contextos.md)); ninguno queda sin contexto
asociado.

La fila **A-04** tiene evidencia manual, no automatizada, y queda como
trabajo pendiente incorporarle una prueba de componente. A-00 a A-03, A-05 y
A-06 tienen código y prueba automatizada citable. **A-07** se sustenta en
mediciones documentadas, no en una prueba automatizada, y declara un
incumplimiento (arranque en frío) con su mitigación y sus límites.

## Decisión relacionada

La decisión arquitectónica que sustenta A-00, A-01, A-02, A-03 y A-04 está
registrada en:

[ADR-0001 — Usar monolito modular](adr/0001-estilo-arquitectonico.md)
(indexado también en [Sección 9](arc42/09-decisiones-arquitectonicas.md)).

La decisión que sustenta A-05 — mantener ambas fronteras de integración
síncronas y formalizarlas en un contrato ejecutable — está registrada en:

[ADR-0003 — Mantener integración síncrona en las dos fronteras actuales](adr/0003-integracion-sincrona.md)

La decisión que sustenta A-06 — los pesos, los umbrales y el significado del
resultado los decide el equipo y no la herramienta que generó el código — está
registrada en:

[ADR-0006 — Semántica del resultado](adr/0006-semantica-del-resultado.md)

y, para la decisión de no incorporar un componente generativo en ejecución:

[ADR-0007 — No incorporar un componente generativo](adr/0007-no-incorporar-componente-generativo.md)

La decisión que sustenta A-07 — mantener Render y mitigar el arranque en frío,
sin concluir una comparación con Lambda que no se midió — está registrada en:

[ADR-0008 — Mantener Render y mitigar el arranque en frío](adr/0008-mantener-render-mitigar-arranque-frio.md)

La fila **A-08** declara qué mitigaciones de la entrega S11 están implementadas y cuáles son un plan
(ver [arc42 §11](arc42/11-riesgos-y-deuda-tecnica.md)). La fila **A-09** tiene pruebas ejecutables de las
garantías de consistencia y declara que la idempotencia está pendiente. La fila **A-10** depende de las
comprobaciones manuales registradas en [despliegue.md](despliegue.md).

La decisión que sustenta A-08 y A-09 — no extraer el módulo y mantener un historial único de solo
adición — está registrada en el [ADR-0009](adr/0009-decision-extraccion-modulo-analisis.md) y el
[ADR-0011](adr/0011-historial-registro-unico-sin-propietario.md); la de A-10, en el
[ADR-0010](adr/0010-despliegue-laboratorio-dokploy.md).

## Relación

El escenario Q-02 es el escenario principal que motiva la selección del
monolito modular, y ya cuenta con dos evidencias reales: la incorporación de
`RuleAnalyzer` (A-01) y la incorporación del frontend como cliente HTTP
independiente (A-04) — ambas sin modificar los módulos internos existentes.
El escenario Q-03 complementa la decisión exigiendo cambios localizados en
las reglas de análisis, con su prueba de modificación (A-02). El escenario
Q-05 tiene dos evidencias: la disponibilidad del esqueleto (A-00) y la
repetibilidad del corte vertical completo con persistencia (A-03). El
escenario Q-01 tiene la medición local de P95 (A-06), el contrato de la API
(A-05) y la medición en Render con 10.000 caracteres (A-07), que cumple en
caliente y no cumple en la primera petición tras inactividad; el límite más
importante, que el POST no se midió como primera petición en frío, está
documentado en la evidencia.

Las tácticas concretas que responden a estos escenarios están documentadas
en [arc42 sección 4](arc42/04-estrategia-de-solucion.md).
