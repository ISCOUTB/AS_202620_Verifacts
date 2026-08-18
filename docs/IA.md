# Inteligencia Artificial

## Propósito

VeriFact contempla el uso de técnicas de Inteligencia Artificial y procesamiento de lenguaje natural como complemento al análisis basado en reglas.

La Inteligencia Artificial no será responsable de determinar de forma absoluta si un contenido es verdadero o falso. Su función será aportar características adicionales para estimar el nivel de riesgo del contenido.

## Estrategia de implementación

El proyecto se desarrollará de manera incremental.

### Primera etapa

Se implementará un análisis basado en reglas para detectar características como:

- lenguaje sensacionalista;
- exceso de mayúsculas;
- uso excesivo de signos;
- afirmaciones absolutas;
- ausencia aparente de fuentes.

### Segunda etapa

Se incorporarán técnicas de procesamiento de lenguaje natural para obtener características lingüísticas adicionales.

La herramienta inicialmente considerada es spaCy.

### Tercera etapa

Se evaluará la incorporación de un modelo de Machine Learning utilizando herramientas como scikit-learn.

## Flujo previsto

```text
Contenido
    |
    v
Preprocesamiento
    |
    +-----------> Rule Engine
    |
    +-----------> NLP Analyzer
    |
    +-----------> ML Model
                   |
                   v
             Scoring Engine
                   |
                   v
               Resultado
