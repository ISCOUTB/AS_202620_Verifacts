# ADR-0006: Los pesos, los umbrales y el significado del resultado son decisión del equipo

- Estado: Aceptado
- Fecha: 2026-09-28
- Decisor: Equipo VeriFacts (no la herramienta que generó el código)

## Contexto

`app/modules/scoring/service.py` y las reglas de `RuleAnalyzer` se construyeron
con apoyo de IA (ver [docs/ia.md](../ia.md)). Compila, tiene pruebas en verde y
aun así, al auditarlo en S9, se encontraron tres hechos que ninguna prueba
previa detectaba:

1. **"Riesgo alto" es inalcanzable con las reglas actuales.** Cada regla suma
   una sola vez: 20 (sensacionalismo) + 15 (mayúsculas) + 15 (afirmación
   absoluta) = **50**, y el umbral de "Riesgo alto" es 60.
2. **"Riesgo bajo" no significa "confiable".** El texto *"El Ministerio
   confirmó que la vacuna causa esterilidad, según fuentes cercanas."* produce 0
   hallazgos y "Riesgo bajo". El motor mide el *estilo* de la redacción, no la
   veracidad de su contenido (restricción
   [R-ALC-01](../arc42/02-restricciones.md)).
3. **El error no es simétrico.** Un falso "Riesgo alto" hace que el usuario
   revise de más; un falso "Riesgo bajo" le da tranquilidad sobre un contenido
   que puede ser dañino. Cuánto pesa cada error es una decisión de producto, no
   de implementación.

Además, `test_analysis.py` fija `score == 50` y "Riesgo medio": una persona o un
modelo que cambie pesos y prueba a la vez mantiene todo en verde. Con un defecto
inducido en el umbral (`<` por `<=`), la suite previa seguía pasando (ver
[evidencia de mutaciones](../evidencia/mutaciones-s9.md)).

## Decisión

1. **Significado.** La clasificación expresa *señales de estilo detectadas*, no
   veracidad. "Riesgo bajo" quiere decir "no se detectaron señales de estilo",
   nunca "el contenido es confiable". Cualquier interfaz que muestre el resultado
   debe conservar esa lectura.
2. **Valores vigentes.** Pesos: sensacionalismo 20, mayúsculas 15, afirmación
   absoluta 15. Tope 100. Umbrales: `< 30` bajo, `< 60` medio, `≥ 60` alto. Viven
   como constantes con nombre en `app/modules/scoring/service.py`.
3. **"Riesgo alto" queda reservado.** Se mantiene definido en 60 pero se declara
   inalcanzable con `RuleAnalyzer` (máximo 50). Se vuelve alcanzable cuando exista
   un segundo analizador; ese día se revisa este ADR con evidencia, no antes.
4. **Regla de cambio.** Modificar un peso, un umbral o el tope exige, en el mismo
   commit: actualizar este ADR (o crear uno que lo reemplace) y actualizar
   `tests/test_scoring_boundaries.py`. Aplica igual si el cambio lo redactó una IA.
5. **Qué sí se delega.** La implementación de reglas ya decididas se puede
   generar con IA porque se verifica con pruebas. La calibración de pesos y
   umbrales no se delega.

## Alternativas consideradas

### Bajar el umbral alto a 50

**Ventaja:** haría alcanzable "Riesgo alto" hoy.

**Motivo del descarte:** sin dataset no hay base para 50; un texto con tres
señales de estilo pasaría a "alto" y se sobre-alertaría. El número se elegiría
para que el código "cuadre", no porque signifique algo.

### Subir los pesos de las reglas

**Motivo del descarte:** infla el puntaje sin evidencia de que las señales
correlacionen con desinformación.

### Delegar la calibración a un modelo generativo

**Motivo del descarte:** ya rechazado en el Registro 03 de
[docs/ia.md](../ia.md) por dependencia externa y falta de trazabilidad.
Además, no habría una prueba que decida si el umbral elegido es el correcto.

### Renombrar las etiquetas ("Sin señales de estilo detectadas")

**Ventaja:** haría explícita la semántica en la propia respuesta.

**Motivo del aplazamiento:** cambia `docs/contracts/openapi.yaml` y los tests
que fijan las etiquetas. Se decide en un ADR nuevo cuando se aborde el escenario
[Q-04](../escenarios-de-calidad.md#q-04--comprensión-del-resultado) con la interfaz.

## Consecuencias positivas

- Los valores que definen el resultado son visibles, con nombre y con dueño.
- Una modificación accidental de un peso, umbral o tope hace fallar una prueba
  (ver [mutaciones](../evidencia/mutaciones-s9.md)).
- El límite del enfoque por reglas queda declarado en lugar de ignorado.

## Consecuencias negativas

- Mientras solo exista `RuleAnalyzer`, el usuario nunca verá "Riesgo alto".
- Un contenido engañoso escrito con calma sigue clasificándose "Riesgo bajo".
- Cambiar un umbral cuesta más (ADR + prueba), a propósito.

## Deuda aceptada

Los umbrales 30/60 no están calibrados con datos. Se aceptan como punto de
partida mientras no exista un conjunto de evaluación.

## Escenarios relacionados

- [Q-05 — Repetibilidad del resultado](../escenarios-de-calidad.md#q-05--repetibilidad-del-resultado)
- [Q-04 — Comprensión del resultado](../escenarios-de-calidad.md#q-04--comprensión-del-resultado)
- [Q-01 — Tiempo de respuesta](../escenarios-de-calidad.md#q-01--tiempo-de-respuesta-del-análisis) (medición compartida)

## Evidencia

- Código: [`app/modules/scoring/service.py`](../../app/modules/scoring/service.py)
- Pruebas: [`tests/test_scoring_boundaries.py`](../../tests/test_scoring_boundaries.py)
- Defectos inducidos: [docs/evidencia/mutaciones-s9.md](../evidencia/mutaciones-s9.md)
- Medición: [docs/evidencia/medicion-q01-q05.md](../evidencia/medicion-q01-q05.md)
- Fila **A-06** de la [tabla de aspectos](../aspectos.md)

## Estado

Aceptado. Si esta decisión cambia, se crea un nuevo ADR que la reemplace.
