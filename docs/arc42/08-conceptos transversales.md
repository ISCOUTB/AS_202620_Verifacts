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


<!-- DÓNDE VA: docs/arc42/08-conceptos-transversales.md
     Añade esta subsección al final del archivo existente (no borres lo que ya tenían).
     Si la sección 8 aún no existe como archivo, créala con este contenido. -->

## Modelo de dominio y contextos delimitados (S6)

### Lenguaje ubicuo

| Término | Significado en el dominio |
|---|---|
| Contenido | Texto o URL que el usuario envía para analizar |
| Análisis | Proceso que evalúa un Contenido en busca de señales de desinformación |
| Factor / Señal | Indicio individual detectado (sensacionalismo, mayúsculas, afirmación absoluta, ausencia de fuentes, lenguaje emocional) |
| Puntuación (Score) | Valor numérico resultante de combinar las Señales |
| Clasificación | Etiqueta derivada de la Puntuación |
| Historial | Registro persistente de Análisis pasados |


### Contextos delimitados

Se identifican tres contextos dentro del monolito modular: **Ingesta y Presentación**, **Análisis de Contenido** (núcleo del dominio) e **Historial de Análisis** (soporte). El detalle del mapa de contextos, las relaciones entre ellos y la tabla de propiedad de datos están en [`docs/mapa-contextos.md`](../mapa-contextos.md).

### Regla transversal de propiedad de datos

Cada tabla de la base de datos tiene un único módulo autorizado a escribir en ella. Los demás módulos que necesiten ese dato lo reciben como resultado de una llamada, nunca escribiendo directamente sobre la tabla ajena. El detalle de qué módulo escribe qué está en [`docs/propiedad-datos.md`](../propiedad-datos.md); las violaciones encontradas frente a esta regla y su plan de corrección están en [`docs/violaciones-modularidad.md`](../violaciones-modularidad.md).
transversal: cualquier documento nuevo que agregue un aspecto debe respetar
esas ocho columnas.
