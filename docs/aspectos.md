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

Los cuatro aspectos caen dentro de Análisis de Contenido, Ingesta y Presentación o Historial de Análisis (ver [mapa de contextos](mapa-contextos.md)); ninguno queda sin contexto asociado.

Solo la fila **A-02** permanece "Pendiente" en evidencia de pruebas; el resto
tiene código y prueba real citables. La columna CI de A-00 requiere
reemplazar el marcador `[PENDIENTE]` por la URL real de un run en verde
tomada de la pestaña **Actions** del repositorio después de confirmar que
`.github/workflows/tests.yml` está en la ruta correcta y se dispara con el
próximo `push`.

## Decisión relacionada

La decisión arquitectónica que sustenta A-00, A-01, A-02, A-03 y A-04 está
registrada en:

[ADR-0001 — Usar monolito modular](adr/0001-estilo-arquitectonico.md)
(indexado también en [Sección 9](arc42/09-decisiones-arquitectonicas.md)).

## Relación

El escenario Q-02 es el escenario principal que motiva la selección del
monolito modular, y ya cuenta con dos evidencias reales: la incorporación de
`RuleAnalyzer` (A-01) y la incorporación del frontend como cliente HTTP
independiente (A-04) — ambas sin modificar los módulos internos existentes.
El escenario Q-03 complementa la decisión exigiendo cambios localizados en
las reglas de análisis, y es el único aspecto que sigue pendiente de prueba
(A-02). El escenario Q-05 tiene dos evidencias: la disponibilidad del
esqueleto (A-00) y la repetibilidad del corte vertical completo con
persistencia (A-03).

Las tácticas concretas que responden a estos escenarios están documentadas
en [arc42 sección 4](arc42/04-estrategia-de-solucion.md).
