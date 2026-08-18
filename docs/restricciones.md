# Restricciones arquitectónicas — VeriFact

## 1. Desarrollo durante un semestre

### Restricción

La solución debe ser realizable dentro del periodo académico.

### Justificación

El proyecto será desarrollado por un equipo pequeño y debe priorizar las funcionalidades esenciales.

### Impacto arquitectónico

Se utilizará una arquitectura modular en lugar de una infraestructura distribuida.

---

## 2. Ejecución local

### Restricción

El prototipo debe poder ejecutarse localmente.

### Justificación

La asignatura no exige un despliegue productivo y el objetivo principal es demostrar la funcionalidad y las decisiones arquitectónicas.

### Impacto arquitectónico

Se utilizará SQLite como mecanismo de persistencia para reducir la complejidad de infraestructura.

---

## 3. Tecnologías de análisis

### Restricción

Las funciones de análisis deben poder implementarse utilizando herramientas accesibles y compatibles con Python.

### Justificación

Python posee herramientas adecuadas para procesamiento de lenguaje natural y Machine Learning.

### Impacto arquitectónico

FastAPI y Python se utilizarán como núcleo del backend y motor de análisis.

---

## 4. Alcance limitado de seguridad

### Restricción

La seguridad avanzada no constituye un objetivo principal del prototipo.

### Justificación

El sistema será académico, funcionará localmente y no manejará información sensible.

### Impacto arquitectónico

Se implementarán medidas básicas de validación y protección, pero no se incorporarán mecanismos empresariales de autenticación o infraestructura de seguridad avanzada.

---

## 5. No despliegue productivo

### Restricción

No se requiere disponibilidad 24/7 ni infraestructura cloud.

### Justificación

La aplicación será utilizada principalmente para demostraciones y pruebas del proyecto.

### Impacto arquitectónico

No se incorporarán mecanismos de balanceo de carga, alta disponibilidad ni orquestación de contenedores.

---

## 6. Evolución futura

### Restricción

La solución inicial debe poder evolucionar si el proyecto requiere nuevas técnicas de análisis.

### Justificación

Se contempla la incorporación progresiva de NLP y Machine Learning.

### Impacto arquitectónico

El Analysis Engine se mantendrá separado en componentes especializados.
