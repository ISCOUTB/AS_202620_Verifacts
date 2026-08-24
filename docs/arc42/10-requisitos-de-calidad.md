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

Actualmente solo Q-05 (confiabilidad) tiene evidencia de prueba automatizada
sobre código real, a través de `tests/test_health.py` (ver
[Sección 6 — Vista de ejecución](06-vista-de-ejecucion.md#61-escenario-comprobación-de-disponibilidad-get-health)).
Los escenarios Q-01 a Q-04 dependen de los módulos `Content`, `Analysis` y
`Scoring`, todavía no implementados, y quedan pendientes de verificación en
próximos incrementos — ver la [tabla de aspectos](../aspectos.md) para el
estado fila por fila.
