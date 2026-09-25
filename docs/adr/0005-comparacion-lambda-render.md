# ADR-0005 — Comparación de despliegue para la API: Render vs. AWS Lambda (reto de corte)

## Estado

Aceptado — 2026-09-25

## Contexto

Como parte del reto de corte de la asignatura, se pide comparar dos
alternativas de despliegue para **una pieza concreta** del sistema (no el
sistema completo), con al menos una alternativa usable sin tarjeta de
crédito, y — si una de las alternativas es una función serverless —
contrastar su arranque en frío medido contra el P95 del escenario de
calidad correspondiente.

Se eligió la pieza **API** (`verifacts-api`), y se comparó:

- **Render** (actual, ver [ADR-0004](0004-plataforma-despliegue.md)): Web
  Service sobre Docker, plan Free, sin tarjeta de crédito.
- **AWS Lambda**: función serverless, envuelta con
  [Mangum](https://github.com/Kludex/mangum) sobre la misma app FastAPI,
  sin modificar la lógica de negocio.

El escenario de calidad relevante es
[Q-01 — Tiempo de respuesta del análisis](../escenarios-de-calidad.md#q-01--tiempo-de-respuesta-del-análisis):
P95 ≤ 3 segundos.

## Prototipo y procedimiento (reproducible)

El prototipo vive en [`serverless-prototype/`](../../serverless-prototype/)
en la raíz del repositorio:

- `lambda_handler.py` — envuelve `app.main:app` con `Mangum(app,
  lifespan="off")`, sin tocar el código de `app/`.
- `template.yaml` — plantilla SAM: runtime `python3.12`, 512 MB de
  memoria, timeout 30s, endpoints `/health` y `/analysis`.
- `medir_cold_start.py` — ejecuta `sam local invoke` N veces (cada
  invocación levanta un contenedor Docker nuevo, por lo que cada corrida
  es, por diseño, una ejecución en frío), y calcula mínimo, mediana, P95 y
  máximo tanto de `Init Duration` como de `Duration`.

**No se desplegó a una cuenta real de AWS** en este incremento — toda la
medición se hizo localmente con `sam local invoke`, que emula el entorno
real de ejecución de Lambda (`public.ecr.aws/lambda/python:3.12-rapid-x86_64`)
usando Docker. Esto respeta
[R-TEC-05](../arc42/02-restricciones.md) (sin tarjeta de crédito) y evita
crear una cuenta de AWS solo para esta comparación.

**Para reproducir:**

```bash
cd serverless-prototype
Copy-Item -Recurse ..\app .\app   # copia local, no versionada (ver .gitignore)
sam build --use-container
python medir_cold_start.py --runs 15
```

**Limitación conocida** (declarada también en el docstring de
`medir_cold_start.py`): esto mide el cold start "de aplicación" (arranque
del intérprete + imports + construcción de la app dentro del contenedor
local), no el cold start "de infraestructura" real de AWS (aprovisionamiento
de red, descarga de la imagen desde el servicio Lambda real, etc.), que no
puede reproducirse sin desplegar a una cuenta real.

## Resultados medidos (15 corridas, evento `GET /health`)

| Métrica | Init Duration (ms) | Duration (ms) |
|---|---|---|
| Mínimo | 0.1 | 17,596.5 |
| Mediana | 0.1 | 18,183.1 |
| **P95** | **0.1** | **20,005.9** |
| Máximo | 0.2 | 21,638.1 |

Datos completos en `serverless-prototype/cold_start_results.csv` (no
versionado, reproducible con el comando de arriba).

**Interpretación:** el `Init Duration` que reporta AWS como "cold start"
oficial es prácticamente nulo. El costo real de la primera ejecución está
en `Duration`, porque `trafilatura` (extracción de contenido desde URL) se
importa dentro del handler en cada invocación fría, no al nivel del
módulo. Un cliente real experimentaría este `Duration` como parte de la
latencia total de la petición, sea o no que AWS lo llame oficialmente
"cold start".

## Comparación contra Q-01

| | Medido |
|---|---|
| Límite de Q-01 | P95 ≤ 3,000 ms |
| Render (operación normal) | Cumple — respuestas en el orden de milisegundos, ver `docs/despliegue.md` |
| Lambda (prototipo, ejecución fría) | **No cumple** — P95 = 20,005.9 ms, 6.7 veces el límite |

## Costo y punto de quiebre de la capa gratuita

Con 512 MB de memoria y ~20s de duración por invocación (10 GB-segundo por
invocación):

- La capa gratuita de Lambda incluye 1,000,000 de invocaciones/mes **y**
  400,000 GB-segundo/mes de cómputo. El límite que se alcanza primero es
  el de cómputo: **400,000 ÷ 10 = 40,000 invocaciones/mes**, muy por
  debajo del millón que anuncia la capa gratuita.
- Tras superar ese punto, el costo marginal es de aproximadamente
  **$0.000367 por invocación** (cómputo + invocación), es decir, unos
  $3.67 por cada 10,000 invocaciones adicionales.
- Render, en su plan Free, no cobra por invocación sino por horas de
  cómputo del servicio (750h/mes incluidas); superar eso requiere pasar
  al plan Starter, de pago (ver [docs/costos.md](../costos.md)).

Detalle completo de la comparación de costos en
[docs/costos.md](../costos.md).

## Decisión

Se mantiene **Render** como plataforma de despliegue de `verifacts-api`.
Lambda queda descartado para esta pieza en su forma actual, porque:

1. Incumple Q-01 por un margen amplio (6.7×) en ejecución fría.
2. La causa (import pesado de `trafilatura` dentro del handler) es
   corregible en principio, pero requeriría reestructurar el módulo
   `Content` para separar la extracción de URL en un import perezoso o
   fuera del handler — trabajo no trivial que excede el alcance de este
   reto de corte.
3. El punto de quiebre de la capa gratuita (40,000 invocaciones/mes) es
   más bajo de lo que sugiere la publicidad de AWS, por el peso de esta
   dependencia específica.

## Procedimiento de reversión

Como el prototipo nunca se desplegó a una cuenta real de AWS, no existe
infraestructura en la nube que revertir. El procedimiento de reversión
"en el peor caso" (si en el futuro se decidiera desplegar Lambda a una
cuenta real y hubiera que revertir a Render) sería:

1. `sam delete --stack-name verifacts-lambda` (elimina el stack de
   CloudFormation creado por SAM, incluida la función y el API Gateway
   asociado).
2. Confirmar que `verifacts-api` en Render sigue activo (no se tocaría en
   ningún momento durante una prueba de Lambda, ya que son plataformas
   independientes).
3. Restaurar `ALLOWED_ORIGINS` y `VITE_API_BASE_URL` en `verifacts-web`
   (Render) a la URL de `verifacts-api` (Render), si se hubieran cambiado
   temporalmente para apuntar a una URL de API Gateway.
4. No hay cambios de esquema de base de datos que revertir, porque el
   prototipo usa `/tmp` (efímero) y nunca comparte estado con
   `data/verifacts.db` de Render.

## Consecuencias

- **Positivas:** queda documentado con evidencia medida, no solo teórica,
  por qué Render sigue siendo la opción correcta para esta pieza; el
  hallazgo sobre el costo real de imports pesados en funciones serverless
  es reutilizable si en el futuro se evalúa serverless para otra pieza
  (por ejemplo, un trabajo programado de reentrenamiento del modelo ML).
- **Negativas:** el prototipo (`serverless-prototype/`) queda en el
  repositorio sin desplegarse, como evidencia y no como código productivo;
  si se quisiera reintentar Lambda en el futuro, habría que invertir en
  optimizar los imports antes de que sea viable.

## Escenarios relacionados

- [Q-01 — Tiempo de respuesta del análisis](../escenarios-de-calidad.md#q-01--tiempo-de-respuesta-del-análisis)

## Decisiones relacionadas

- [ADR-0004 — Plataforma de despliegue y forma de la infraestructura como código](0004-plataforma-despliegue.md)