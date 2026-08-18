# VeriFact

## Sistema inteligente para análisis de información digital

VeriFact es una aplicación web orientada al análisis automatizado de contenidos digitales para identificar indicadores asociados a posibles casos de desinformación.

El usuario podrá ingresar un texto o una URL y obtener una evaluación basada en diferentes características del contenido, acompañada de una puntuación de riesgo y una explicación de los factores detectados.

El sistema no pretende determinar de forma absoluta si una información es verdadera o falsa. Su objetivo es proporcionar indicadores que sirvan como apoyo para que el usuario evalúe críticamente la información.

---

## Problema

La circulación masiva de información en Internet dificulta que los usuarios puedan determinar rápidamente la confiabilidad de determinados contenidos.

Las publicaciones pueden presentar lenguaje sensacionalista, afirmaciones absolutas, ausencia de fuentes verificables y otros patrones que dificultan su evaluación.

La verificación manual requiere consultar diferentes fuentes y puede consumir tiempo, por lo que VeriFact propone automatizar una parte de este análisis.

---

## Objetivo

Diseñar e implementar un prototipo web modular capaz de analizar contenidos digitales, identificar indicadores asociados a posibles casos de desinformación y presentar un resultado interpretable para el usuario.

---

## Alcance del prototipo

El prototipo contempla:

- Ingreso de texto para análisis.
- Ingreso de URL.
- Extracción básica de contenido.
- Análisis basado en reglas.
- Análisis lingüístico.
- Generación de una puntuación.
- Clasificación del nivel de riesgo.
- Explicación de los factores detectados.
- Registro básico de los análisis realizados.

El sistema se ejecutará localmente durante el desarrollo y las demostraciones.

---

## Arquitectura

La solución se plantea como una arquitectura modular:

```text
                    React
                 Frontend
                     |
                  HTTP/REST
                     |
                     v
                  FastAPI
                 Backend
                     |
        +------------+------------+
        |            |            |
        v            v            v
 Content        Rule Engine    NLP Analyzer
 Extractor
        \            |            /
         \           |           /
          +----------+----------+
                     |
                     v
              Scoring Engine
                     |
