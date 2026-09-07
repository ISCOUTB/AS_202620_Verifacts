# ADR-0001: Usar monolito modular

- Estado: Aceptado
- Fecha: 2026-08-24
- Decisor: Equipo VeriFacts

## Contexto

VeriFacts requiere una arquitectura capaz de soportar la evolución de sus
mecanismos de análisis sin introducir una complejidad de infraestructura que
no sea adecuada para el alcance académico.

Los escenarios prioritarios son:

- Q-01 — Tiempo de respuesta del análisis.
- Q-02 — Incorporación de un nuevo analizador.
- Q-03 — Modificación de una regla.
- Q-04 — Comprensión del resultado.
- Q-05 — Repetibilidad del resultado.

La decisión está relacionada principalmente con Q-02 y Q-03.

## Decisión

VeriFacts utilizará un **monolito modular**.

La aplicación será una única unidad ejecutable, organizada internamente en
los módulos:

- API.
- Content.
- Analysis.
- Scoring.

Los límites entre módulos deberán mantenerse para evitar dependencias
innecesarias.

## Alternativas consideradas

### Arquitectura por capas

**Ventaja:**

Simplicidad inicial y facilidad de comprensión.

**Motivo del descarte:**

Puede producir cambios transversales cuando el motor de análisis evoluciona,
lo que afecta especialmente al escenario Q-02.

---

### Arquitectura hexagonal

**Ventaja:**

Alta testabilidad y sustitución de infraestructura.

**Motivo del descarte:**

Introduce mayor indirección y complejidad estructural de la necesaria para el
alcance actual.

---

### Monolito modular

**Ventaja:**

Combina una ejecución sencilla con límites internos que facilitan la
evolución de los módulos.

**Decisión:**

Seleccionado.

## Consecuencias positivas

- Ejecución sencilla.
- Baja complejidad operativa.
- No requiere comunicación de red entre módulos.
- Facilita la evolución del motor de análisis.
- Facilita pruebas localizadas.
- Adecuado para el tamaño del equipo.

## Consecuencias negativas

- Los módulos no escalan independientemente.
- Un fallo grave puede afectar toda la aplicación.
- Se necesita disciplina para mantener las fronteras.
- Podría ser necesario separar un módulo en el futuro.

## Deuda aceptada

Se acepta mantener todos los módulos dentro del mismo proceso mientras los
escenarios no demuestren una necesidad de distribución.

También se acepta mantener ejecución local durante el prototipo.

## Escenarios relacionados

- [Q-01 — Tiempo de respuesta](../escenarios-de-calidad.md#q-01--tiempo-de-respuesta-del-análisis)
- [Q-02 — Incorporación de un nuevo analizador](../escenarios-de-calidad.md#q-02--incorporación-de-un-nuevo-analizador)
- [Q-03 — Modificación de una regla](../escenarios-de-calidad.md#q-03--modificación-de-una-regla)
- [Q-04 — Comprensión del resultado](../escenarios-de-calidad.md#q-04--comprensión-del-resultado)
- [Q-05 — Repetibilidad del resultado](../escenarios-de-calidad.md#q-05--repetibilidad-del-resultado)

## Estado

Aceptado.

Si en el futuro se requiere reemplazar esta decisión, deberá crearse un nuevo
ADR en lugar de modificar este documento.
