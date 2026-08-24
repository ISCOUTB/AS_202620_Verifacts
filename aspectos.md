# Aspectos arquitectónicos — VeriFacts

## Aspecto principal

El aspecto arquitectónico principal seleccionado es:

**Escalabilidad mediante modularidad.**

La arquitectura debe permitir incorporar nuevos mecanismos de análisis sin
modificar significativamente los demás componentes.

## Matriz de trazabilidad

| ID | Aspecto | Atributo | Preocupación | Escenario | Medida | Impacto | Riesgo | Pruebas |
|---|---|---|---|---|---|---|---|---|
| A-00 | Disponibilidad del esqueleto | Confiabilidad | Verificar que el servicio arranca y responde | [Q-05](escenarios-de-calidad.md#q-05--repetibilidad-del-resultado) | El servicio responde `200 {"status":"ok"}` en `/health` de forma repetible | Alto | Bajo | `tests/test_health.py` — **1 passed** (ejecutado localmente con `pytest -q` y en cada push vía `.github/workflows/tests.yml`) |
| A-01 | Escalabilidad | Escalabilidad | Incorporar nuevos mecanismos de análisis | [Q-02](escenarios-de-calidad.md#q-02--incorporación-de-un-nuevo-analizador) | Cambio limitado al módulo `Analysis` y sus pruebas | Alto | Alto | Pendiente — requiere que `Analysis` tenga al menos un `Analyzer` implementado |
| A-02 | Escalabilidad | Mantenibilidad | Modificar reglas existentes | [Q-03](escenarios-de-calidad.md#q-03--modificación-de-una-regla) | Cambio localizado sin regresiones | Alto | Medio-alto | Pendiente — requiere que exista al menos una regla implementada en `Analysis` |

Solo la fila **A-00** cuenta hoy con evidencia de prueba real sobre código
en ejecución, porque es la única que corresponde al corte vertical actual
(ver [Sección 6 — Vista de ejecución](arc42/06-vista-de-ejecucion.md)). Las
filas A-01 y A-02 permanecerán "Pendiente" en la columna Pruebas hasta que
el módulo `Analysis` tenga lógica implementada.

## Decisión relacionada

La decisión arquitectónica se encuentra registrada en:

[ADR-0001 — Usar monolito modular](adr/0001-estilo-arquitectonico.md)
(indexado también en [Sección 9](arc42/09-decisiones-arquitectonicas.md)).

## Relación

El escenario Q-02 es el escenario principal que motiva la selección del
monolito modular. El escenario Q-03 complementa la decisión al exigir
cambios localizados en las reglas de análisis. El escenario Q-05 es el que
ya tiene verificación ejecutable en este incremento (fila A-00).

Las tácticas concretas que responden a estos escenarios están documentadas
en [arc42 sección 4](arc42/04-estrategia-de-solucion.md).
