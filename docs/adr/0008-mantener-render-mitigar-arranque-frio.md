# ADR-0008: Mantener Render y mitigar el arranque en frío (Reto operativo S10)

- Estado: Aceptado
- Fecha: 2026-10-10
- Decisor: Equipo VeriFacts
- Relación: complementa y corrige las conclusiones comparativas del [ADR-0005](0005-comparacion-lambda-render.md); no lo reemplaza.

## Contexto

El equipo identificó la comparación entre Render y AWS Lambda como el reto operativo de la
semana 10, con el escenario [Q-01](../escenarios-de-calidad.md#q-01--tiempo-de-respuesta-del-análisis)
y umbral P95 ≤ 3.000 ms. Confirmación docente de que este es el escenario asignado: pendiente.

El ADR-0005 comparó plataformas con cargas no equivalentes:

- El P95 local de 46,9 ms se midió con 10.000 caracteres, mientras el evento de SAM llevaba un texto de 63 caracteres.
- El P95 de 20.005,9 ms de SAM correspondía a `GET /health`, y se atribuyó también a `POST /analysis`.
- El tiempo de SAM local es una emulación, no latencia real de AWS ni costo facturable.

Por eso esas cifras no se usan como evidencia de esta decisión. El prototipo `serverless-prototype/`
se conserva como exploración, sin medición equivalente. En este corte el equipo decidió
no medir con SAM ni desplegar en AWS.

## Evidencia utilizada

Medición de Render con un payload de 10.000 caracteres: [medicion-render-s10.md](../evidencia/medicion-render-s10.md).

| Estado | Resultado | Umbral 3.000 ms |
|---|---|---|
| Caliente, `POST /analysis` (n=50) | P95 211,3 ms | Cumple |
| Primera petición tras 20 min sin tráfico (2 observaciones) | ≈22,4 s | No cumple |

## Corrección de causalidad

El ADR-0005 atribuía el arranque en frío de Lambda a imports «dentro del handler». En el código,
`serverless-prototype/lambda_handler.py` importa `app.main` y `app/modules/content/service.py`
importa `trafilatura`, ambos a nivel de módulo. Esa explicación queda retirada.

## Decisión

1. **Mantener Render** como plataforma de despliegue.
2. **Mitigar el arranque en frío** con una petición periódica a `GET /health` mediante
   [keepalive.yml](../../.github/workflows/keepalive.yml) (GitHub Actions, cada 5 minutos).
3. **Declarar el incumplimiento**: Q-01 se cumple en caliente y no se cumple en la primera
   petición tras inactividad. La mitigación está configurada, pero su efectividad no se ha
   medido todavía; se registrará en `medicion-render-s10.md`.

## Alternativas consideradas

| Alternativa | Motivo |
|---|---|
| Migrar a AWS Lambda | Descartada por ahora: no hay medición equivalente que la justifique y el equipo decidió no desplegar en AWS en este corte. |
| Plan de pago de Render sin suspensión por inactividad | Elimina el arranque en frío. Su costo no se evaluó aquí; es la opción si la mitigación resulta insuficiente. |
| Servicio externo de monitoreo para el ping | Descartada: agrega un tercero; el workflow vive en el propio repositorio. |
| No hacer nada | Descartada: la primera petición tras inactividad tarda ≈22 s frente a un umbral de 3 s. |

## Consecuencias

- En caliente, Render cumple Q-01 con un margen de unas 14 veces.
- El keep-alive es de mejor esfuerzo: los workflows programados de GitHub pueden retrasarse u
  omitirse, y en repositorios públicos se desactivan tras 60 días sin actividad.
- El ping consume horas de instancia gratuitas de Render; hay que comprobar que el
  total mensual alcanza (ver [costos](../costos.md)).
- El historial SQLite puede perderse en un reinicio o redespliegue (almacenamiento efímero);
  es independiente de esta decisión (ver [persistencia](../evidencia/persistencia-render.md)).

## Cuándo se reabre

Se crea un nuevo ADR (sin reescribir este) si ocurre alguno de estos casos:

- La primera petición tras un periodo sin tráfico real sigue superando 3 s con el keep-alive activo.
- Las horas gratuitas de Render dejan de alcanzar.
- La persistencia del historial pasa a ser un requisito.

En ese caso se comparan las opciones con el mismo payload de 10.000 caracteres,
separando estado frío y caliente.

## Relacionados

- [ADR-0005](0005-comparacion-lambda-render.md)
- [Escenario Q-01](../escenarios-de-calidad.md#q-01--tiempo-de-respuesta-del-análisis)
- [Medición en Render](../evidencia/medicion-render-s10.md)
