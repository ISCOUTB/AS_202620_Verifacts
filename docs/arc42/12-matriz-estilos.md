# Matriz comparativa de estilos arquitectónicos

La comparación se realiza directamente sobre los escenarios Q-01 a Q-05 del
árbol de utilidad de VeriFacts.

## Escala

- Favorable: el estilo facilita el escenario.
- Neutral: el estilo no presenta una ventaja o desventaja significativa.
- Desfavorable: el estilo introduce dificultades relevantes para el escenario.

| Escenario | Capas | Hexagonal | Monolito modular | Decisión |
|---|---|---|---|---|
| Q-01 Rendimiento | Favorable: llamadas directas entre capas | Favorable: pequeño costo de abstracción | Muy favorable: ejecución local sin red interna | Monolito modular |
| Q-02 Nuevo analizador | Desfavorable: riesgo de cambios transversales | Muy favorable: facilita sustitución y extensión | Muy favorable: módulo Analysis independiente | Monolito modular |
| Q-03 Modificación de regla | Neutral: depende de disciplina de capas | Favorable: separación de responsabilidades | Muy favorable: regla encapsulada dentro de Analysis | Monolito modular |
| Q-04 Comprensión del resultado | Neutral | Neutral | Neutral | Monolito modular |
| Q-05 Repetibilidad | Favorable: flujo simple | Muy favorable: fácil aislamiento de componentes | Favorable: componentes separados sin distribución | Monolito modular |

## Análisis

### Q-01

Los tres estilos pueden proporcionar buen rendimiento en una aplicación local.
El monolito modular evita añadir comunicación de red entre módulos.

### Q-02

Este es el escenario más importante para la decisión.

La arquitectura por capas puede producir modificaciones transversales al
agregar un nuevo mecanismo de análisis. Hexagonal ofrece una excelente
separación, pero introduce mayor indirección. El monolito modular proporciona
extensión localizada con una complejidad menor.

### Q-03

La separación interna del monolito modular permite aislar las reglas dentro
del módulo `Analysis`.

### Q-04

El estilo arquitectónico tiene impacto indirecto sobre la interfaz, por lo que
ninguna alternativa presenta una ventaja decisiva.

### Q-05

Hexagonal presenta una ventaja de testabilidad, pero el monolito modular
también permite separar componentes y probarlos sin introducir la complejidad
adicional de puertos y adaptadores.

## Decisión

Se selecciona **monolito modular** porque ofrece el mejor equilibrio para los
escenarios prioritarios Q-01, Q-02 y Q-03 y cumple las restricciones de tiempo,
tamaño del equipo y ejecución local.
