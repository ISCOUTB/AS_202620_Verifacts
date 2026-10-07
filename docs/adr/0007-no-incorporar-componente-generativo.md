# ADR-0007: No incorporar un componente generativo (LLM) al producto en esta etapa

- Estado: Aceptado
- Fecha: 2026-10-07
- Decisor: Equipo VeriFacts

## Contexto

VeriFacts calcula hoy su resultado con `RuleAnalyzer` (reglas deterministas) y
`Scoring` (pesos y umbrales fijados en el [ADR-0006](0006-semantica-del-resultado.md)).
Se evaluó si el producto debía incorporar un componente generativo (un LLM
llamado desde el backend) para clasificar el contenido o redactar la
explicación de los factores. El uso de IA como herramienta de desarrollo está
registrado aparte en [docs/ia.md](../ia.md); este ADR trata solo de si el
modelo forma parte del producto en ejecución.

## Alternativas evaluadas

| Alternativa | Q-01 latencia | Q-05 repetibilidad | Q-04 explicabilidad | Costo y operación |
|---|---|---|---|---|
| A. LLM como clasificador | Una llamada de red por análisis; el P95 medido hoy es 46,9 ms contra un máximo de 3000 ms ([medición](../evidencia/medicion-q01-q05.md)) y pasaría a depender de un tercero | La misma entrada puede dar salidas distintas; Q-05 exige 100 % | Razonamiento no verificable | Costo por llamada, clave de API como secreto, plan gratuito de Render ([costos](../costos.md)) |
| B. LLM solo para redactar la explicación | Misma dependencia de red | El score sigue siendo repetible, el texto no | Texto fluido pero no trazable a una regla | Mismo costo y secretos |
| C. Modelo clásico local (TF-IDF + regresión logística, `MLAnalyzer`) | Local, sin red | Determinista | Parcial | Requiere corpus, entrenamiento y versionar el modelo; no existe en el repositorio |
| D. No incorporar componente generativo (elegida) | Se mantiene el P95 medido | Se mantiene el 100 % | Cada factor remite a una regla | Sin costo adicional |

## Decisión

No se incorpora un componente generativo al producto en esta etapa. El motor
sigue siendo `RuleAnalyzer` + `Scoring`. La interfaz `Analysis` permite
incorporar otro analizador más adelante sin modificar `API`, `Content` ni
`Scoring` (Q-02).

## Consecuencias

- Se conservan Q-01, Q-04 y Q-05 con las medidas ya registradas.
- No se amplía la cobertura de señales: el motor sigue midiendo estilo, no
  veracidad ([ADR-0006](0006-semantica-del-resultado.md)).
- Se reevaluará si el equipo define una medida de calidad que las reglas no
  alcancen y existe un presupuesto para medir costo y latencia reales del
  modelo candidato antes de decidir.