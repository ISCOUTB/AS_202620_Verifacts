# Registro de uso de IA — VeriFacts

## Propósito

Este documento registra el uso de herramientas de Inteligencia Artificial
durante el desarrollo del proyecto, y las decisiones de aceptación o rechazo
relacionadas con su uso, tanto como herramienta de apoyo documental como
componente potencial del propio producto VeriFacts.

---

## Registro 01 — Asistencia documental

**Herramienta:** ChatGPT

**Uso:** apoyo en la redacción y organización inicial de documentación
arquitectónica, incluyendo propuestas para arc42, escenarios de calidad,
matrices y ADR.

**Decisión:** Aceptado como herramienta de apoyo documental.

**Motivo:** permite acelerar la organización de información proporcionada
por el equipo.

**Control aplicado:** las decisiones finales y las medidas de los escenarios
son revisadas por el equipo y deben corresponder con el repositorio.

---

## Registro 02 — Comparación de estilos arquitectónicos

**Herramienta:** ChatGPT

**Uso:** apoyo para estructurar la comparación entre arquitectura por capas,
hexagonal y monolito modular.

**Decisión:** Aceptado como apoyo.

**Motivo:** ayuda a identificar ventajas, costos y consecuencias que después
son contrastadas con los escenarios específicos de VeriFacts.

---

## Registro 03 — IA como clasificador principal del producto

**Herramienta evaluada:** modelo de lenguaje externo / LLM.

**Uso previsto:** clasificar directamente un contenido como verdadero o
falso.

**Decisión:** Rechazado para la primera versión.

**Motivo:** introduciría dependencia externa, dificultaría la trazabilidad
del resultado y no corresponde con el objetivo del sistema de proporcionar
indicadores explicables.

---

## Registro 04 — Machine Learning

**Herramienta:** scikit-learn.

**Uso previsto:** evaluar modelos de clasificación como complemento del
motor basado en reglas.

**Decisión:** Pendiente de evaluación.

**Motivo:** dependerá de la disponibilidad de un dataset y de evidencia de
que el modelo mejora los resultados frente al enfoque basado en reglas.

---

## Tecnologías de IA evaluadas para el producto

| Tecnología | Uso previsto | Estado | Justificación |
|---|---|---|---|
| spaCy | Procesamiento de características lingüísticas | Aceptada inicialmente | Compatible con Python y adecuada para procesamiento lingüístico |
| scikit-learn | Clasificación y experimentación ML | Pendiente | Permite evaluar modelos ligeros durante el proyecto |
| Modelos externos/LLM | Análisis complementario | No seleccionado inicialmente | Introduce dependencia externa y dificulta la trazabilidad del resultado |

## Estrategia de incorporación al producto

1. **Reglas** (etapa actual planeada): lenguaje sensacionalista, exceso de
   mayúsculas, uso excesivo de signos, afirmaciones absolutas, ausencia
   aparente de fuentes.
2. **NLP**: evaluación de spaCy para características lingüísticas
   adicionales.
3. **Machine Learning**: evaluación de scikit-learn, condicionada a la
   disponibilidad de un dataset adecuado.

## Principio de uso

La Inteligencia Artificial se utiliza como apoyo documental y como
componente experimental del producto, no como autoridad para determinar la
verdad absoluta de un contenido. Las decisiones finales de arquitectura y
los criterios de evaluación son responsabilidad del equipo.
