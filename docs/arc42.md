# arc42 — VeriFact

# 1. Introducción y objetivos

## 1.1 Descripción general

VeriFact es una aplicación web orientada al análisis automatizado de contenidos digitales.

El usuario podrá ingresar un texto o una URL para solicitar un análisis. El sistema procesará el contenido, identificará diferentes indicadores asociados a posibles casos de desinformación y generará una puntuación de riesgo acompañada de una explicación.

El sistema no pretende determinar de manera absoluta si un contenido es verdadero o falso. Su función es proporcionar indicadores que apoyen la evaluación crítica del usuario.

---

## 1.2 Problema

La cantidad de información disponible en Internet dificulta que los usuarios puedan determinar rápidamente la confiabilidad de determinados contenidos.

La revisión manual requiere consultar múltiples fuentes y analizar características del contenido, lo cual puede resultar lento y difícil para usuarios sin herramientas especializadas.

VeriFact busca automatizar parte de esta evaluación mediante un conjunto de analizadores independientes.

---

## 1.3 Objetivo general

Diseñar e implementar un prototipo web modular capaz de analizar contenidos digitales, identificar indicadores asociados a posibles casos de desinformación y presentar un resultado interpretable para el usuario.

---

## 1.4 Objetivos específicos

1. Permitir el ingreso de texto para análisis.
2. Permitir el ingreso de una URL.
3. Extraer y procesar el contenido recibido.
4. Detectar indicadores mediante reglas.
5. Incorporar análisis lingüístico como mecanismo complementario.
6. Generar una puntuación de riesgo.
7. Mostrar una explicación de los factores detectados.
8. Mantener una arquitectura modular que permita incorporar nuevos mecanismos de análisis.

---

## 1.5 Alcance

### Incluido

- Interfaz web.
- Recepción de texto.
- Recepción de URL.
- Extracción básica de contenido.
- Motor de reglas.
- Análisis lingüístico.
- Motor de puntuación.
- Persistencia de resultados.
- Visualización de resultados.

### Fuera del alcance actual

- Despliegue productivo.
- Monitoreo permanente de redes sociales.
- Verificación absoluta de hechos.
- Análisis avanzado de video.
- Análisis avanzado de imágenes.
- Infraestructura distribuida.
- Autenticación empresarial.
- Arquitectura de microservicios.

---

## 1.6 Usuarios

### Usuario final

Persona que desea evaluar un contenido digital.

### Estudiante o docente

Usuario que puede utilizar la herramienta con fines educativos y de alfabetización digital.

### Analista

Usuario que puede utilizar los resultados como apoyo para una revisión inicial.

---

# 2. Restricciones arquitectónicas

## 2.1 Restricción académica

El proyecto debe poder desarrollarse dentro del periodo académico y por un equipo pequeño.

### Justificación

Se priorizará una arquitectura modular sencilla frente a una arquitectura distribuida compleja.

Esto permite invertir el tiempo en la funcionalidad y en las decisiones arquitectónicas relevantes.

---

## 2.2 Restricción de ejecución local

El prototipo será ejecutado localmente durante el desarrollo y las demostraciones.

### Justificación

No se requiere infraestructura cloud para cumplir el objetivo académico.

El uso local reduce la complejidad operativa y facilita la demostración del prototipo.

---

## 2.3 Restricción tecnológica

Las principales tecnologías serán:

- React.
- TypeScript.
- Python.
- FastAPI.
- SQLite.
- SQLAlchemy.
- spaCy.
- scikit-learn.
- GitHub.
- SonarCloud.

### Justificación

La combinación permite desarrollar una aplicación web funcional y facilita integrar procesamiento de lenguaje natural y Machine Learning sin introducir infraestructura innecesaria.

---

## 2.4 Restricción de alcance

El sistema no pretende establecer la verdad absoluta de un contenido.

### Justificación

La evaluación de hechos depende de contexto, fuentes y conocimiento externo. Por esta razón, VeriFact se limita a generar indicadores y niveles de riesgo.

---

## 2.5 Restricción de seguridad

La seguridad no constituye el principal objetivo del prototipo debido a su naturaleza académica y a que no manejará información sensible.

Sin embargo, se aplicarán prácticas básicas:

- validación de entradas;
- uso de variables de entorno cuando corresponda;
- exclusión de secretos del repositorio;
- manejo adecuado de errores.

### Justificación

Se busca mantener un nivel razonable de seguridad sin introducir complejidad innecesaria en el prototipo.

---

# 3. Contexto y alcance

## 3.1 Contexto de negocio

VeriFact se encuentra dentro del contexto de consumo y evaluación de información digital.

El usuario utiliza la aplicación para analizar un contenido antes de considerarlo confiable o compartirlo.

---

## 3.2 Sistemas y actores externos

### Usuario

Introduce texto o URL y consulta los resultados del análisis.

### Sitio web externo

Puede proporcionar contenido cuando el usuario introduce una URL.

### GitHub

Gestiona el código fuente, las tareas y el trabajo colaborativo del equipo.

### SonarCloud

Analiza la calidad del código durante el desarrollo.

---

## 3.3 Contexto técnico

La solución se compone de:

```text
React
   |
   | HTTP/REST
   v
FastAPI
   |
   +-- Content Extractor
   +-- Rule Engine
   +-- NLP Analyzer
   +-- Scoring Engine
   |
   v
SQLite
