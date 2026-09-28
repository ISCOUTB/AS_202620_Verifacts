# Aspectos arquitectónicos — VeriFacts

## Aspecto principal

El aspecto arquitectónico principal seleccionado es:

**Escalabilidad mediante modularidad.**

La arquitectura debe permitir incorporar nuevos mecanismos de análisis sin
modificar significativamente los demás componentes.

## Matriz de trazabilidad

Columnas del curso: **ID · Aspecto/Preocupación · Escenario · Vista C4 ·
ADR · Ubicación en código · Medida/Criterio · Evidencia de pruebas**.

| ID | Aspecto / Preocupación | Escenario | Vista C4 | ADR | Ubicación en código | Medida / Criterio | Evidencia de pruebas | Contexto (mapa-contextos.md) |
|---|---|---|---|---|---|---|---|---|
| A-00 | Disponibilidad del esqueleto | [Q-05](escenarios-de-calidad.md#q-05--repetibilidad-del-resultado) | Contenedor "Aplicación VeriFacts" — [C4 Nivel 2](c4/02-contenedores.md) | [ADR-0001](adr/0001-estilo-arquitectonico.md) | `app/api/routes.py` (`GET /health`) | Responde `200 {"status":"ok"}` de forma repetible ante la misma entrada | `tests/test_health.py` — **1 passed** · CI: job "Tests" en verde, ver [Actions](https://github.com/ISCOUTB/AS_202620_Verifacts/actions) | Ingesta y Presentación |
| A-01 | Escalabilidad — incorporar un nuevo analizador | [Q-02](escenarios-de-calidad.md#q-02--incorporación-de-un-nuevo-analizador) | Contenedor "Aplicación VeriFacts", componente `Analysis` — [C4 Nivel 2](c4/02-contenedores.md) | [ADR-0001](adr/0001-estilo-arquitectonico.md) | `app/modules/analysis/analyzer.py` (`RuleAnalyzer`), `app/modules/analysis/service.py` | El nuevo analizador (`RuleAnalyzer`, 3 reglas) se incorporó sin modificar `API`, `Content` ni `Scoring` | `tests/test_analysis.py` — **1 passed** | Análisis de Contenido |
| A-02 | Mantenibilidad — modificar una regla existente | [Q-03](escenarios-de-calidad.md#q-03--modificación-de-una-regla) | Contenedor "Aplicación VeriFacts", componente `Analysis` — [C4 Nivel 2](c4/02-contenedores.md) | [ADR-0001](adr/0001-estilo-arquitectonico.md) | `app/modules/analysis/analyzer.py` (`absolute_words` en `RuleAnalyzer`) | Modificar una regla no debe producir regresiones en las pruebas existentes | `tests/test_rule_modification.py` — **1 passed**, confirma que `test_health.py` y `test_analysis.py` siguen en verde | Análisis de Contenido |
| A-03 | Confiabilidad — corte vertical completo con persistencia | [Q-05](escenarios-de-calidad.md#q-05--repetibilidad-del-resultado) | Contenedores "Aplicación VeriFacts" y "Base de datos" — [C4 Nivel 2](c4/02-contenedores.md) | [ADR-0001](adr/0001-estilo-arquitectonico.md) | `app/api/routes.py` (`POST /analysis`), `app/persistence/repository.py` | La misma entrada produce el mismo `score`, `classification` y `factors`, y queda persistida y recuperable por `id` | `tests/test_analysis.py` — **1 passed** | Análisis de Contenido → Historial de Análisis |
| A-04 | Bajo acoplamiento — frontend como cliente HTTP independiente | [Q-02](escenarios-de-calidad.md#q-02--incorporación-de-un-nuevo-analizador) | Contenedor "Interfaz web" — [C4 Nivel 2](c4/02-contenedores.md) | [ADR-0002](adr/0002-contextos-sin-cambios.md) | `frontend/src/api/client.ts` | El frontend se incorporó sin agregar lógica de negocio ni tocar los módulos internos del backend (`API`, `Content`, `Analysis`, `Scoring`) | Verificación manual (pasos 17–18 del README); sin prueba de componente automatizada todavía — ver [Pendiente](../README.md#pendiente) | Ingesta y Presentación |
| A-05 | Modificabilidad — contrato de API ejecutable y versionado (S7) | [Q-01](escenarios-de-calidad.md#q-01--tiempo-de-respuesta-del-análisis), [Q-02](escenarios-de-calidad.md#q-02--incorporación-de-un-nuevo-analizador) | Todas las flechas del Contenedor "Aplicación VeriFacts" — [C4 Nivel 2](c4/02-contenedores.md) | [ADR-0003](adr/0003-integracion-sincrona.md) | `docs/contracts/openapi.yaml`, `tests/test_contract.py` | Un cambio incompatible en la respuesta de la API (campo renombrado, tipo cambiado, arreglo envuelto en objeto) rompe el pipeline antes de `master` | `tests/test_contract.py` — **12 passed**; verificado manualmente que renombrar `score`→`risk_score` en `app/api/routes.py` hace fallar 4 de esas pruebas, y que revertir el cambio las vuelve a poner en verde (20 passed en total) | Ingesta y Presentación → Análisis de Contenido → Historial de Análisis |
| A-06 | Confiabilidad e interpretabilidad — pesos, umbrales y significado del resultado en código generado con IA (S9) | [Q-05](escenarios-de-calidad.md#q-05--repetibilidad-del-resultado), [Q-04](escenarios-de-calidad.md#q-04--comprensión-del-resultado), [Q-01](escenarios-de-calidad.md#q-01--tiempo-de-respuesta-del-análisis) | Contenedor "Aplicación VeriFacts", componente `Scoring` — [C4 Nivel 2](c4/02-contenedores.md) | [ADR-0006](adr/0006-semantica-del-resultado.md) | `app/modules/scoring/service.py` (`UMBRAL_RIESGO_MEDIO`, `UMBRAL_RIESGO_ALTO`, `MAX_SCORE`), pesos en `app/modules/analysis/analyzer.py` | Cambiar un peso, umbral o tope sin actualizar ADR y prueba rompe el pipeline; la misma entrada produce el mismo resultado (100 %); P95 ≤ 3 s con 10.000 caracteres | `tests/test_scoring_boundaries.py` — **12 passed**; `tests/test_boundaries.py` — **3 passed** (erosión); de 5 defectos inducidos, la suite previa no detectaba 3 y las pruebas nuevas detectan los 5 ([mutaciones](evidencia/mutaciones-s9.md)); medición en [evidencia Q-01/Q-05](evidencia/medicion-q01-q05.md); auditoría en [auditoria-s9.md](auditoria-s9.md) | Análisis de Contenido |

Los siete aspectos caen dentro de Análisis de Contenido, Ingesta y
Presentación o Historial de Análisis (ver
[mapa de contextos](mapa-contextos.md)); ninguno queda sin contexto
asociado.

Solo la fila **A-02** permanece "Pendiente" en el sentido estricto (la
prueba de modificación de regla ya existe, pero no hay una segunda
verificación independiente); **A-04** tiene evidencia manual, no
automatizada, y queda como trabajo pendiente incorporarle una prueba de
componente. El resto (A-00, A-01, A-03, A-05, A-06) tiene código y prueba
automatizada real y citable, incluida la columna CI de A-00.

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

## Relación

El escenario Q-02 es el escenario principal que motiva la selección del
monolito modular, y ya cuenta con dos evidencias reales: la incorporación de
`RuleAnalyzer` (A-01) y la incorporación del frontend como cliente HTTP
independiente (A-04) — ambas sin modificar los módulos internos existentes.
El escenario Q-03 complementa la decisión exigiendo cambios localizados en
las reglas de análisis, y es el único aspecto que sigue pendiente de una
segunda prueba (A-02). El escenario Q-05 tiene dos evidencias: la
disponibilidad del esqueleto (A-00) y la repetibilidad del corte vertical
completo con persistencia (A-03). El escenario Q-01 gana, con A-05, su
primera evidencia automatizada: el contrato de la API no puede degradarse
en silencio, aunque la medición formal de P95 (Q-01) siga pendiente.

Las tácticas concretas que responden a estos escenarios están documentadas
en [arc42 sección 4](arc42/04-estrategia-de-solucion.md).
