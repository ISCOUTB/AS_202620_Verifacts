# Aspecto arquitectónico: Escalabilidad

## Declaración

La arquitectura de VeriFact debe permitir incorporar nuevos mecanismos de análisis de contenido sin requerir modificaciones significativas en los componentes existentes.

## Motivación

El núcleo del sistema es el análisis de contenidos digitales. Durante el desarrollo pueden aparecer nuevas necesidades, como:

- nuevas reglas de detección;
- análisis lingüístico;
- nuevos algoritmos;
- modelos de Machine Learning;
- nuevas fuentes de información.

Por esta razón, el análisis se separa en componentes independientes.

## Decisión arquitectónica

El backend se organizará de manera modular, separando:

- extracción de contenido;
- análisis basado en reglas;
- análisis lingüístico;
- cálculo de puntuación;
- persistencia.

La comunicación entre estos componentes se realizará mediante interfaces y estructuras de datos definidas por la aplicación.

## Arquitectura prevista

```text
                     FastAPI
                        |
        +---------------+----------------+
        |               |                |
        v               v                v
Content Extractor  Rule Engine      NLP Analyzer
        |               |                |
        +---------------+----------------+
                        |
                        v
                 Scoring Engine
                        |
                        v
                     SQLite
