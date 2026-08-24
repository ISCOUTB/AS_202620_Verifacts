# arc42 — Sección 2: Restricciones

Las siguientes restricciones condicionan las decisiones arquitectónicas de
VeriFacts.

## 2.1 Restricciones organizativas

### R-ORG-01 — Desarrollo durante un semestre

El sistema debe desarrollarse durante el periodo académico.

**Justificación:** el tiempo disponible limita la cantidad de infraestructura y
funcionalidad que puede implementarse.

**Impacto:** se prioriza una arquitectura modular sencilla frente a una solución
distribuida.

---

### R-ORG-02 — Equipo pequeño

El sistema es desarrollado por un equipo reducido.

**Justificación:** la capacidad para desarrollo, pruebas e infraestructura es
limitada.

**Impacto:** se evita introducir microservicios e infraestructura operativa
innecesaria.

---

### R-ORG-03 — Alcance académico

El objetivo es demostrar decisiones arquitectónicas y desarrollar un prototipo
funcional, no construir una plataforma productiva.

**Justificación:** el proyecto pertenece a una asignatura académica.

**Impacto:** se prioriza la arquitectura relevante para el prototipo.

---

## 2.2 Restricciones técnicas

### R-TEC-01 — Ejecución local

El prototipo debe poder ejecutarse localmente.

**Justificación:** no se exige inicialmente un despliegue productivo.

**Impacto:** se evita depender de infraestructura cloud para la ejecución.

---

### R-TEC-02 — Recursos computacionales

El procesamiento debe ejecutarse en equipos de desarrollo convencionales.

**Justificación:** no se dispone de infraestructura especializada.

**Impacto:** los mecanismos de análisis deben considerar su costo computacional.

---

### R-TEC-03 — Tecnologías disponibles

Se utilizarán tecnologías accesibles para el equipo.

**Justificación:** reduce la curva de aprendizaje y el riesgo técnico.

**Impacto:** Python, FastAPI, React y herramientas compatibles con Python serán
las tecnologías principales.

---

### R-TEC-04 — Persistencia sencilla

La persistencia inicial debe ser sencilla de instalar y utilizar localmente.

**Justificación:** el prototipo no requiere inicialmente una infraestructura de
base de datos productiva.

**Impacto:** se utilizará SQLite inicialmente.

---

## 2.3 Restricciones de alcance y datos

### R-ALC-01 — No verificar la verdad absoluta

El sistema no determinará de forma definitiva si una noticia es verdadera o
falsa.

**Justificación:** el resultado automatizado es solamente un indicador.

**Impacto:** la salida se expresará como riesgo o nivel de confiabilidad.

---

### R-DAT-01 — Evitar información sensible innecesaria

El sistema evitará almacenar datos personales que no sean necesarios.

**Justificación:** reducir exposición innecesaria durante el proyecto académico.

**Impacto:** la persistencia se limitará a información necesaria para los
análisis.
