# ADR-0001: Selección del estilo arquitectónico

- Estado: Propuesto
- Fecha: 2026-08-18
- Decisor: Pedro Jose Castro Blanquicett

## Contexto

VeriFacts es una aplicación web para analizar contenidos digitales e
identificar indicadores asociados a posibles casos de desinformación.

El sistema debe recibir texto o URL, procesar el contenido, aplicar diferentes
mecanismos de análisis y generar una puntuación explicable.

Los principales atributos priorizados son:

- Escalabilidad.
- Mantenibilidad.
- Rendimiento.
- Usabilidad.
- Confiabilidad.

Los escenarios relacionados con escalabilidad y mantenibilidad requieren que
sea posible incorporar nuevos mecanismos de análisis sin modificar
significativamente el resto del sistema.

Al mismo tiempo, el proyecto debe ser realizable durante un semestre, se
ejecutará localmente y no requiere infraestructura distribuida.

## Decisión

Se utilizará un **monolito modular** como estilo arquitectónico principal
para VeriFacts.

La aplicación se ejecutará como una única unidad, pero organizará sus
responsabilidades en módulos independientes:

- API.
- Content.
- Analysis.
- Scoring.

Los módulos tendrán responsabilidades delimitadas y se evitarán dependencias
innecesarias entre ellos.

## Alternativas consideradas

### Alternativa 1 — Arquitectura por capas

La arquitectura por capas ofrece una estructura sencilla y fácil de comprender.

Se descartó porque la evolución del motor de análisis puede generar cambios
transversales entre presentación, lógica y persistencia.

Aunque presenta un menor costo inicial, no favorece tanto el escenario de
incorporación frecuente de nuevos mecanismos de análisis.

### Alternativa 2 — Arquitectura hexagonal

La arquitectura hexagonal favorece la testabilidad y la sustitución de
adaptadores, manteniendo el dominio independiente de la infraestructura.

Se descartó porque introduce mayor indirección y estructura para un proyecto
académico pequeño que no necesita múltiples adaptadores o infraestructura
intercambiable en esta etapa.

### Alternativa 3 — Monolito modular

El monolito modular mantiene una única aplicación y un único proceso, pero
establece límites internos entre las funcionalidades.

Fue seleccionado porque proporciona un equilibrio entre simplicidad inicial,
mantenibilidad y evolución gradual.

## Consecuencias positivas

- El sistema es sencillo de ejecutar localmente.
- Los módulos tienen responsabilidades claras.
- Se puede incorporar nuevo análisis sin modificar directamente otros módulos.
- No existe comunicación de red entre módulos internos.
- La solución es adecuada para un equipo pequeño.
- La arquitectura permite evolucionar posteriormente si aparece una necesidad
  real de separación.

## Consecuencias negativas

- Todos los módulos comparten el mismo proceso.
- Un fallo grave puede afectar a toda la aplicación.
- Los módulos no pueden escalarse independientemente.
- Se necesita disciplina para evitar dependencias indebidas entre módulos.
- La aplicación seguirá siendo un único artefacto de ejecución.

## Deuda aceptada

Se acepta que el sistema no tendrá escalabilidad independiente por módulo en la
versión inicial.

También se acepta mantener SQLite y ejecución local mientras los escenarios
del proyecto no justifiquen una infraestructura más compleja.

## Relación con los escenarios de calidad

### Escenario de escalabilidad

La incorporación de nuevos analizadores deberá poder realizarse dentro del
Analysis Engine sin modificar la interfaz ni la persistencia.

### Escenario de mantenibilidad

La modificación de una regla deberá quedar limitada al módulo correspondiente
y sus pruebas.

### Escenario de rendimiento

Las llamadas entre módulos serán locales, evitando latencia de red interna.

### Escenario de confiabilidad

Las responsabilidades separadas permitirán probar los componentes de manera
independiente.

## Estado

Propuesto.

Este ADR deberá considerarse una decisión de arquitectura y no deberá
modificarse después de ser aceptado. Si una decisión futura reemplaza esta
arquitectura, deberá registrarse un nuevo ADR.
