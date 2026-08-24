# arc42 — Sección 1: Introducción y objetivos

## 1.1 Descripción general

VeriFacts es una aplicación web orientada al análisis de contenidos digitales
para identificar indicadores asociados a posibles casos de desinformación.

El sistema permitirá que un usuario introduzca un texto o una URL y obtenga
una evaluación acompañada de una puntuación de riesgo, una clasificación y
una explicación de los factores detectados.

VeriFacts no pretende determinar de manera absoluta si una información es
verdadera o falsa. Su propósito es proporcionar indicadores que ayuden al
usuario a realizar una evaluación inicial y crítica del contenido.

---

## 1.2 Problema

La circulación masiva de información en Internet dificulta que los usuarios
puedan determinar rápidamente la confiabilidad de determinados contenidos.

Algunas publicaciones pueden presentar lenguaje sensacionalista,
afirmaciones absolutas, ausencia de fuentes verificables u otras características
que dificultan su evaluación.

La verificación manual requiere consultar diferentes fuentes y analizar el
contenido, lo cual puede consumir tiempo.

VeriFacts busca automatizar una parte de esta evaluación mediante diferentes
mecanismos de análisis.

---

## 1.3 Interesados

### Usuario final

Persona que desea evaluar un contenido antes de compartirlo o utilizarlo como
fuente de información.

### Estudiante

Usuario que puede utilizar la herramienta para fortalecer prácticas de
alfabetización digital y pensamiento crítico.

### Docente

Puede utilizar VeriFacts como apoyo en actividades educativas relacionadas
con evaluación de información digital.

### Analista de información

Puede utilizar el resultado como una primera señal para priorizar una revisión
más detallada.

### Equipo de desarrollo

Responsable de evolucionar y mantener la solución durante el proyecto.

---

## 1.4 Objetivos de negocio y relación con los interesados

| ID | Objetivo | Interesado relacionado | Resultado esperado |
|---|---|---|---|
| OBJ-01 | Facilitar una evaluación inicial de contenidos digitales antes de utilizarlos o compartirlos | Usuario final | El usuario obtiene indicadores comprensibles sobre el contenido |
| OBJ-02 | Apoyar el desarrollo de pensamiento crítico frente a información digital | Estudiante | El estudiante puede identificar señales asociadas a posibles contenidos engañosos |
| OBJ-03 | Proporcionar una herramienta de apoyo para actividades educativas de alfabetización digital | Docente | El docente puede utilizar el sistema como recurso educativo |
| OBJ-04 | Proporcionar señales que permitan priorizar una revisión posterior | Analista | El analista identifica contenidos que requieren mayor atención |
| OBJ-05 | Mantener una arquitectura que pueda evolucionar durante el semestre | Equipo de desarrollo | Nuevos mecanismos de análisis pueden incorporarse con cambios controlados |

---

## 1.5 Alcance

### Incluido

- Recepción de texto.
- Recepción de URL.
- Extracción básica de contenido.
- Análisis basado en reglas.
- Análisis lingüístico.
- Generación de puntuación.
- Clasificación del resultado.
- Explicación de factores.
- Registro de análisis.

### Fuera del alcance

- Verificación absoluta de hechos.
- Monitoreo permanente de redes sociales.
- Análisis avanzado de vídeo.
- Análisis avanzado de imágenes.
- Despliegue productivo.
- Infraestructura distribuida compleja.

---

## 1.6 Objetivos arquitectónicos

| ID | Objetivo arquitectónico | Interesado | Atributo relacionado |
|---|---|---|---|
| AO-01 | Permitir incorporar nuevos mecanismos de análisis sin modificar significativamente los existentes | Equipo de desarrollo | Escalabilidad / Mantenibilidad |
| AO-02 | Mantener tiempos de respuesta adecuados durante el análisis | Usuario final | Rendimiento |
| AO-03 | Permitir modificar reglas de análisis de forma localizada | Equipo de desarrollo | Mantenibilidad |
| AO-04 | Presentar resultados comprensibles para usuarios no técnicos | Usuario / Docente | Usabilidad |
| AO-05 | Producir resultados repetibles bajo las mismas condiciones | Usuario / Analista | Confiabilidad |
