# arc42 — Sección 9: Decisiones arquitectónicas

Las decisiones arquitectónicas significativas de VeriFacts se registran como
**ADR (Architecture Decision Records)** independientes en `docs/adr/`, para
mantener un historial inmutable: si una decisión cambia, se crea un nuevo ADR
en lugar de modificar el anterior.

## Índice de decisiones

| ID | Título | Estado | Documento |
|---|---|---|---|
| ADR-0001 | Usar monolito modular como estilo arquitectónico | Aceptado | [docs/adr/0001-estilo-arquitectonico.md](../adr/0001-estilo-arquitectonico.md) |

## Relación con los escenarios de calidad

Cada ADR referencia los escenarios (Q-01 a Q-05) que motivan la decisión. La
trazabilidad completa entre escenarios, tácticas y decisiones está en:

- [Sección 4 — Estrategia de solución](04-estrategia-de-solucion.md)
- [Sección 10 — Requisitos de calidad](10-requisitos-de-calidad.md)
- [Matriz comparativa de estilos](../matriz-estilos.md)

## Próximas decisiones pendientes de registrar

Estas decisiones aún no se han tomado, pero se anticipa que requerirán un
ADR propio cuando se implementen los módulos correspondientes:

- Persistencia: confirmación de SQLite + SQLAlchemy para el historial de
  análisis (actualmente es solo una restricción, ver
  [R-TEC-04](02-restricciones.md)).
- Contrato del módulo `Analysis`: forma concreta de la interfaz `Analyzer`.
- Incorporación (o no) de Machine Learning al motor de análisis — depende de
  la evaluación registrada en [Registro de uso de IA](../ia.md).
