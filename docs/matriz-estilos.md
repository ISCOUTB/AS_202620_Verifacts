# Matriz comparativa de estilos arquitectónicos

La comparación se realiza utilizando los escenarios de calidad definidos
para VeriFacts y considerando las restricciones actuales del proyecto.

Escala:

- 1 = desfavorable
- 3 = intermedio
- 5 = favorable

| Criterio | Capas | Hexagonal | Monolito modular |
|---|---:|---:|---:|
| Simplicidad inicial | 5 | 2 | 4 |
| Rendimiento local | 5 | 4 | 5 |
| Testabilidad | 3 | 5 | 4 |
| Mantenibilidad | 3 | 5 | 5 |
| Incorporación de nuevos analizadores | 2 | 5 | 5 |
| Complejidad inicial | 5 | 2 | 4 |
| Adecuación al equipo y semestre | 5 | 3 | 5 |
| Evolución gradual | 3 | 4 | 5 |

## Capas

### Ventajas

- Estructura sencilla.
- Fácil de comprender.
- Bajo costo inicial.
- Adecuado para un prototipo pequeño.

### Costos

Los cambios que atraviesan varias responsabilidades pueden producir
modificaciones transversales.

La evolución del Analysis Engine puede terminar afectando distintas capas.

---

## Hexagonal

### Ventajas

- Alta testabilidad.
- Mayor independencia de infraestructura.
- Facilita sustituir adaptadores.
- Protege el dominio frente a detalles externos.

### Costos

- Mayor cantidad de abstracciones.
- Mayor indirección.
- Más código de infraestructura para un proyecto pequeño.
- Puede introducir complejidad antes de que exista una necesidad real.

---

## Monolito modular

### Ventajas

- Mantiene la simplicidad de ejecución de un monolito.
- Permite separar funcionalidades por módulos.
- Facilita la evolución progresiva del Analysis Engine.
- Reduce el costo operativo.
- Mantiene las llamadas internas sin comunicación de red.

### Costos

- Requiere disciplina en los límites entre módulos.
- Al compartir proceso y despliegue, un problema grave puede afectar toda la
  aplicación.
- La escalabilidad independiente de cada módulo no existe inicialmente.

---

## Decisión

Se selecciona **Monolito modular**.

La elección responde principalmente a los escenarios de escalabilidad y
mantenibilidad, manteniendo una complejidad compatible con las restricciones
del proyecto.

Capas se descarta porque favorece la simplicidad inicial pero puede introducir
cambios transversales.

Hexagonal se descarta porque ofrece ventajas de testabilidad y sustitución de
infraestructura que no justifican su mayor indirección para el alcance actual.

Monolito modular ofrece el equilibrio más adecuado entre simplicidad,
mantenibilidad y evolución gradual.
