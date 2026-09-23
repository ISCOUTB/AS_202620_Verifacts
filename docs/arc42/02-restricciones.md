# arc42 — Sección 2: Restricciones

Las siguientes restricciones condicionan las decisiones arquitectónicas de
VeriFacts.

## 2.1 Restricciones organizativas

### R-TEC-01 — Ejecución local y despliegue accesible

El prototipo debe poder ejecutarse localmente y, a partir de este incremento,
también debe estar desplegado en un entorno accesible desde internet para su
evaluación.

**Justificación:** el incremento de despliegue exige una URL pública,
verificable desde fuera de la red de la universidad.

**Impacto:** el sistema se empaqueta con Docker (`Dockerfile`) y se despliega
como infraestructura como código (`render.yaml`) en Render, sin dejar de
poder ejecutarse localmente con `python run.py`. Ver
[docs/despliegue.md](../despliegue.md).

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

### R-TEC-05 — Límite de costo y sin tarjeta de crédito

El despliegue debe realizarse sin incurrir en costos monetarios y sin requerir
una tarjeta de crédito o método de pago.

**Justificación:** el proyecto es académico y no cuenta con presupuesto ni
método de pago institucional asignado para infraestructura cloud.

**Impacto:** se eligió el plan gratuito (Free) de Render, que no exige tarjeta
de crédito para registrarse ni para desplegar. Esto implica renunciar a disco
persistente y aceptar que el servicio "duerme" tras inactividad. Ver
[docs/costos.md](../costos.md) para el detalle de supuestos y límites de la
capa gratuita.

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
