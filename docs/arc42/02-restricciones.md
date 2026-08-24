# arc42 — Sección 2: Restricciones arquitectónicas

Las restricciones condicionan las decisiones arquitectónicas de VeriFacts y
se clasifican según su naturaleza.

## 2.1 Restricciones organizativas

### R-ORG-01 — Tiempo académico

**Restricción:** el proyecto debe desarrollarse durante el semestre académico.

**Justificación:** el tiempo disponible limita la cantidad de infraestructura
y funcionalidades que pueden implementarse.

**Impacto arquitectónico:** se prioriza una arquitectura modular sencilla frente
a una solución distribuida de mayor complejidad.

---

### R-ORG-02 — Tamaño del equipo

**Restricción:** el proyecto es desarrollado por un equipo pequeño.

**Justificación:** la capacidad disponible para desarrollo, pruebas e
infraestructura es limitada.

**Impacto arquitectónico:** se evita introducir microservicios e infraestructura
operativa innecesaria.

---

### R-ORG-03 — Alcance académico

**Restricción:** el objetivo es demostrar decisiones de arquitectura y un
prototipo funcional, no construir una plataforma productiva.

**Justificación:** el proyecto se evalúa dentro de un contexto académico.

**Impacto arquitectónico:** se priorizan las decisiones que aportan valor al
prototipo y a los escenarios de calidad.

---

## 2.2 Restricciones técnicas

### R-TEC-01 — Ejecución local

**Restricción:** el prototipo debe poder ejecutarse localmente.

**Justificación:** no se requiere inicialmente un despliegue productivo.

**Impacto arquitectónico:** la solución evita depender de infraestructura cloud
para funcionar.

---

### R-TEC-02 — Recursos computacionales limitados

**Restricción:** el procesamiento debe poder ejecutarse en equipos de desarrollo
convencionales.

**Justificación:** el proyecto no dispone de infraestructura especializada.

**Impacto arquitectónico:** los mecanismos de análisis y modelos deberán ser
seleccionados considerando su costo computacional.

---

### R-TEC-03 — Tecnologías accesibles

**Restricción:** se utilizarán tecnologías disponibles y conocidas por el equipo.

**Justificación:** reduce el tiempo dedicado a aprender infraestructura nueva.

**Impacto arquitectónico:** se utilizarán Python, FastAPI, React y herramientas
de análisis compatibles con Python.

---

### R-TEC-04 — Persistencia apropiada para el prototipo

**Restricción:** la persistencia inicial debe ser sencilla de instalar y
utilizar localmente.

**Justificación:** el prototipo no requiere inicialmente una infraestructura
de base de datos productiva.

**Impacto arquitectónico:** se utilizará SQLite en la primera versión.

---

## 2.3 Restricciones legales y de datos

### R-LEG-01 — No presentar el resultado como verificación absoluta

**Restricción:** el sistema no presentará su resultado como una determinación
definitiva de verdad o falsedad.

**Justificación:** el análisis automatizado únicamente identifica indicadores
y patrones; no sustituye una verificación humana.

**Impacto arquitectónico:** la interfaz y los resultados utilizarán lenguaje de
riesgo o confiabilidad y mostrarán los factores detectados.

---

### R-LEG-02 — No almacenar información sensible innecesaria

**Restricción:** el prototipo evitará almacenar información personal que no sea
necesaria para su funcionamiento.

**Justificación:** se reduce la exposición innecesaria de datos durante el
desarrollo académico.

**Impacto arquitectónico:** la persistencia se limitará a la información
necesaria para registrar los análisis.
