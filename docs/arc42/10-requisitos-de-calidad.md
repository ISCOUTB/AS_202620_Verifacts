# arc42 — Sección 10: Requisitos de calidad

Esta sección reúne los requisitos de calidad de VeriFacts. El contenido
detallado vive en documentos dedicados para poder referenciarse desde
múltiples secciones (Sección 4, ADRs, tabla de aspectos); aquí se presenta
el resumen y los enlaces.

## 10.1 Árbol de utilidad

El árbol de utilidad descompone la calidad general del sistema en atributos,
refinamientos y escenarios verificables.

Ver: [Árbol de utilidad](../arbol-utilidad.md)

## 10.2 Escenarios de calidad

| ID | Atributo | Resumen | Prioridad |
|---|---|---|---|
| Q-01 | Rendimiento | El análisis de un texto de hasta 10.000 caracteres responde con P95 ≤ 3 s | Muy alta |
| Q-02 | Escalabilidad | Se incorpora un nuevo analizador sin modificar `API`, `Content` ni `Scoring` | Muy alta |
| Q-03 | Mantenibilidad | Se modifica una regla existente sin afectar módulos no relacionados | Alta |
| Q-04 | Usabilidad | Un usuario sin conocimientos técnicos comprende el resultado sin asistencia | Alta |
| Q-05 | Confiabilidad | La misma entrada y configuración producen el mismo resultado | Alta |

Detalle completo (fuente, estímulo, artefacto, entorno, respuesta, medida) en:
[Escenarios de calidad](../escenarios-de-calidad.md)

## 10.3 De escenario a decisión

La forma en que cada escenario se traduce en una táctica concreta está en la
[Sección 4 — Estrategia de solución](04-estrategia-de-solucion.md), y la
decisión arquitectónica resultante está registrada en
[ADR-0001](../adr/0001-estilo-arquitectonico.md) (ver
[Sección 9](09-decisiones-arquitectonicas.md)).

## 10.4 Verificación

Estado actual, fila por fila (ver la [tabla de aspectos](../aspectos.md)
para la trazabilidad completa hasta el código):

| Escenario | Estado de verificación |
|---|---|
| Q-01 | Pendiente — el pipeline `POST /analysis` ya existe y se ejecuta localmente, pero no hay una medición formal de P95 todavía |
| Q-02 | **Con evidencia** — `RuleAnalyzer` se incorporó sin tocar `API`, `Content` ni `Scoring`; verificado en `tests/test_analysis.py` (fila A-01) |
| Q-03 | Pendiente — falta una prueba que module una regla existente y confirme ausencia de regresiones (fila A-02) |
| Q-04 | Pendiente — depende de la interfaz web, todavía no implementada |
| Q-05 | **Con evidencia** — `GET /health` (`tests/test_health.py`, fila A-00) y `POST /analysis` con persistencia (`tests/test_analysis.py`, fila A-03) |

A diferencia del incremento anterior, ya no todos los escenarios dependen de
módulos sin implementar: `Content`, `Analysis`, `Scoring` y `Persistencia`
tienen lógica real y un corte vertical completo (`POST /analysis`) que los
atraviesa — ver [Sección 6 — Vista de ejecución](06-vista-de-ejecucion.md#62-escenario-análisis-de-contenido-post-analysis).
Lo que falta cerrar es evidencia específica por escenario (medición de P95
para Q-01, prueba de modificación de regla para Q-03, prueba de usuario para
Q-04), no la existencia del código.
