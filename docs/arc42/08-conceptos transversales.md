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

Todo aspecto arquitectónico relevante debe poder seguirse desde el
escenario de calidad que lo motiva hasta la evidencia de prueba, pasando por
la vista C4 y el ADR correspondientes. Esa cadena completa vive en
[docs/aspectos.md](../aspectos.md) y es, en sí misma, un concepto
transversal: cualquier documento nuevo que agregue un aspecto debe respetar
esas ocho columnas.
