# Matriz comparativa de estilos arquitectónicos

La comparación utiliza los atributos y escenarios definidos para VeriFacts.

| Criterio | Capas | Hexagonal | Monolito modular |
|---|---|---|---|
| Simplicidad inicial | Alta | Baja | Alta |
| Rendimiento local | Alto | Alto | Alto |
| Testabilidad | Media | Alta | Alta |
| Mantenibilidad | Media | Alta | Alta |
| Incorporación de analizadores | Baja | Alta | Alta |
| Complejidad inicial | Baja | Alta | Media-baja |
| Adecuación al semestre | Alta | Media | Alta |
| Evolución gradual | Media | Alta | Muy alta |

## Capas

Favorece la simplicidad inicial, pero puede producir cambios transversales
cuando el sistema evoluciona.

## Hexagonal

Favorece la testabilidad y la sustitución de infraestructura, pero introduce
mayor indirección y complejidad.

## Monolito modular

Mantiene una ejecución sencilla y permite establecer límites internos entre
módulos, favoreciendo la evolución gradual.

## Decisión

Se selecciona **monolito modular** porque ofrece el mejor equilibrio entre los
escenarios de escalabilidad y mantenibilidad y las restricciones del proyecto.
