# ADR-0001: Selección del estilo arquitectónico

- Estado: Propuesto
- Fecha: 2026-08-23
- Decisor: Equipo VeriFacts

## Contexto

VeriFacts requiere una arquitectura que permita analizar contenidos digitales
y evolucionar sus mecanismos de análisis durante el proyecto.

Los principales atributos priorizados son:

- Escalabilidad.
- Mantenibilidad.
- Rendimiento.
- Usabilidad.
- Confiabilidad.

Los escenarios Q-01, Q-02, Q-03, Q-04 y Q-05 definidos en
`docs/escenarios-de-calidad.md` representan las principales necesidades
arquitectónicas.

El proyecto además está condicionado por restricciones académicas,
organizativas y técnicas que favorecen una solución sencilla de ejecutar.

## Decisión

Se selecciona **Monolito Modular** como estilo arquitectónico principal.

La aplicación será una única unidad ejecutable, organizada mediante módulos
con responsabilidades claramente delimitadas:

- API.
- Content.
- Analysis.
- Scoring.

## Alternativas consideradas

### Alternativa 1 — Arquitectura por capas

**Ventaja principal:**

Simplicidad inicial y facilidad de comprensión.

**Desventaja principal:**

Puede producir cambios transversales cuando evoluciona el motor de análisis.

**Escenarios afectados:**

Q-02 y Q-03.

**Decisión:**

Descartada para la línea base porque el escenario de evolución del análisis es
prioritario.

---

### Alternativa 2 — Arquitectura hexagonal

**Ventaja principal:**

Favorece testabilidad y sustitución de infraestructura.

**Desventaja principal:**

Introduce mayor indirección y complejidad estructural.

**Escenarios afectados:**

Q-03 y Q-05.

**Decisión:**

Descartada para esta etapa porque las ventajas de separación de infraestructura
no compensan el costo adicional para el alcance actual.

---

### Alternativa 3 — Monolito modular

**Ventaja principal:**

Combina una ejecución sencilla con límites internos entre responsabilidades.

**Desventaja principal:**

Los módulos siguen compartiendo proceso y despliegue y requieren disciplina
para evitar acoplamiento indebido.

**Escenarios afectados:**

Q-01, Q-02, Q-03 y Q-05.

**Decisión:**

Seleccionada.

## Consecuencias positivas

- Simplicidad de ejecución.
- Menor infraestructura.
- Bajo costo de comunicación entre módulos.
- Evolución gradual del Analysis Engine.
- Facilita las pruebas.
- Adecuado para el tamaño del equipo.

## Consecuencias negativas

- Los módulos no pueden escalarse independientemente.
- Un fallo importante puede afectar toda la aplicación.
- Se necesita disciplina para mantener las fronteras.
- Puede requerirse una futura migración si aparecen necesidades de escala
  independiente.

## Deuda aceptada

Se acepta mantener un monolito modular durante el prototipo y no introducir
microservicios mientras los escenarios no demuestren una necesidad real.

También se acepta utilizar infraestructura local durante el desarrollo.

## Relación con escenarios

| Escenario | Relación con la decisión |
|---|---|
| Q-01 | El procesamiento interno evita latencia de red entre módulos |
| Q-02 | Los límites modulares facilitan incorporar nuevos analizadores |
| Q-03 | La responsabilidad localizada reduce cambios transversales |
| Q-04 | La arquitectura permite mantener una interfaz sencilla |
| Q-05 | Los módulos pueden probarse de forma independiente |

## Estado

Propuesto
