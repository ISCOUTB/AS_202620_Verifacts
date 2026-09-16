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

Los seis aspectos caen dentro de Análisis de Contenido, Ingesta y
Presentación o Historial de Análisis (ver
[mapa de contextos](mapa-contextos.md)); ninguno queda sin contexto
asociado.

Solo la fila **A-02** permanece "Pendiente" en el sentido estricto (la
prueba de modificación de regla ya existe, pero no hay una segunda
verificación independiente); **A-04** tiene evidencia manual, no
automatizada, y queda como trabajo pendiente incorporarle una prueba de
componente. El resto (A-00, A-01, A-03, A-05) tiene código y prueba
automatizada real y citable. La columna CI de A-00 requiere reemplazar el
marcador `[PENDIENTE]` por la URL real de un run en verde tomada de la
pestaña **Actions** del repositorio.

## Decisión relacionada

La decisión arquitectónica que sustenta A-00, A-01, A-02, A-03 y A-04 está
registrada en:

[ADR-0001 — Usar monolito modular](adr/0001-estilo-arquitectonico.md)
(indexado también en [Sección 9](arc42/09-decisiones-arquitectonicas.md)).

La decisión que sustenta A-05 — mantener ambas fronteras de integración
síncronas y formalizarlas en un contrato ejecutable — está registrada en:

[ADR-0003 — Mantener integración síncrona en las dos fronteras actuales](adr/0003-integracion-sincrona.md)

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
