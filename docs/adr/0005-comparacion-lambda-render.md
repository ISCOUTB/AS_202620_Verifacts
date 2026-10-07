# ADR-0005 — Comparación de despliegue para la API: Render vs. AWS Lambda (reto de corte)

## Estado

Aceptado — 2026-09-25

### Contexto y Reto Operativo S10

Como parte del **Reto Operativo de la Semana 10 (S10)** de la asignatura, se
evalúa la comparación de dos alternativas de despliegue para una pieza
concreta del sistema: la **API** (`verifacts-api`), contrastando el contenedor
continuo actual en Render frente a una arquitectura Serverless en AWS Lambda.

El escenario de calidad rector es
[Q-01 — Tiempo de respuesta del análisis](../escenarios-de-calidad.md#q-01--tiempo-de-respuesta-del-análisis),
cuyo umbral exige un **P95 ≤ 3,000 ms** (3 segundos) bajo carga representativa.

### Hipótesis, variables y montaje experimental

1. **Hipótesis del reto:** La arquitectura serverless (AWS Lambda) incurre en
   una penalización de arranque en frío (*cold start*) derivada de la
   inicialización del entorno y la importación de dependencias del backend
   (`trafilatura`, `fastapi`, `pydantic`) que excede el umbral de calidad
   exigido por Q-01 (P95 ≤ 3,000 ms). Por tanto, mantener un contenedor en
   Render (Web Service continuo) garantiza el cumplimiento del escenario.
2. **Variables del experimento:**
   - **Variable independiente:** Plataforma de despliegue:
     - Alternativa A (Línea base actual): Render Web Service sobre Docker (contenedor en ejecución continua).
     - Alternativa B (Candidata): AWS Lambda con runtime Python 3.12 y 512 MB de memoria, emulada localmente con AWS SAM CLI y Mangum.
   - **Variable dependiente:** Latencia de respuesta total / duración de ejecución (`Duration` en ms).
   - **Variables controladas:**
     - Mismo código base FastAPI (`app/`).
     - Mismo runtime (Python 3.12) y asignación de memoria (512 MB).
     - Mismo cliente concurrente (1 cliente).
     - Misma operación y payload: `POST /analysis` con texto representativo de análisis (10,000 caracteres, y evento equivalente en `serverless-prototype/events/analysis_event.json`) y verificación de salud en `GET /health` (`events/health_event.json`).
3. **Umbral de decisión:** P95 ≤ 3,000 ms (criterio formal de Q-01).

## Prototipo y procedimiento (reproducible)

El prototipo vive en [`serverless-prototype/`](../../serverless-prototype/)
en la raíz del repositorio:

- `lambda_handler.py` — envuelve `app.main:app` con `Mangum(app, lifespan="off")`, sin tocar el código de `app/`.
- `template.yaml` — plantilla SAM: runtime `python3.12`, 512 MB de memoria, timeout 30s, endpoints `/health` y `/analysis`.
- `medir_cold_start.py` — ejecuta `sam local invoke` N veces (cada invocación levanta un contenedor Docker nuevo desde `public.ecr.aws/lambda/python:3.12-rapid-x86_64`, emulando un arranque en frío por diseño), calculando mínimo, mediana, P95 y máximo de `Init Duration` y `Duration`.

**No se desplegó a una cuenta real de AWS** en este incremento para respetar
[R-TEC-05](../arc42/02-restricciones.md) (sin tarjeta de crédito obligatoria).
Toda la medición se realizó con `sam local invoke`, que reproduce el entorno
oficial de Lambda.

**Para reproducir:**

```bash
cd serverless-prototype
Copy-Item -Recurse ..\app .\app   # copia local, no versionada (ver .gitignore)
sam build --use-container
python medir_cold_start.py --runs 15
python medir_cold_start.py --runs 15 --event events/analysis_event.json
```

## Resultados medidos y contraste de línea base

### 1. Medición de arranque en frío en AWS Lambda (15 corridas por evento)

Medición sobre 15 ejecuciones frías independientes (datos en `serverless-prototype/cold_start_results.csv`):

| Métrica | Init Duration (ms) | Duration Lambda (ms) |
|---|---|---|
| Mínimo | 0.1 | 17,596.5 |
| Mediana | 0.1 | 18,183.1 |
| **P95** | **0.1** | **20,005.9** |
| Máximo | 0.2 | 21,638.1 |

*Interpretación:* El `Init Duration` oficial de Lambda es mínimo (~0.1 ms).
Sin embargo, el tiempo real de respuesta que percibe el usuario (`Duration`)
está en el orden de los **18 a 21 segundos** (P95 de 20,005.9 ms), debido a que
la importación de módulos pesados (`trafilatura`, `jsonschema`, módulos de
análisis) ocurre durante el ciclo de vida de la invocación en frío.

### 2. Contraste equivalente: Línea base (Render) vs. Serverless (Lambda)

Comparación sobre la operación central de negocio (`POST /analysis` con texto y persistencia SQLite) y la verificación operativa (`GET /health`):

| Operación | Render (Línea base actual) | AWS Lambda (Cold Start) | Umbral Q-01 | Veredicto |
|---|---|---|---|---|
| `POST /analysis` (10,000 chars) | **P95 = 46.9 ms** (cómputo local, ver [medición Q-01](../evidencia/medicion-q01-q05.md)); ~250–350 ms en red Render | **P95 = 20,005.9 ms** (6.7× el umbral) | P95 ≤ 3,000 ms | **Render CUMPLE** · Lambda NO CUMPLE |
| `GET /health` | **15.18 ms** (ver log estructurado en [docs/despliegue.md](../despliegue.md)) | **P95 = 20,005.9 ms** | P95 ≤ 3,000 ms | **Render CUMPLE** · Lambda NO CUMPLE |

### 3. Límites de validez del experimento

- **Alcance de la medición serverless:** Mide el arranque en frío a nivel de
  aplicación y dependencias. En un despliegue real en nube sobre AWS, este valor
  representa una cota inferior, pues se añadirían tiempos de aprovisionamiento de
  red, VPC y API Gateway.
- **Comportamiento en Render:** En el plan Free, si el servicio no recibe
  tráfico por 15 minutos entra en reposo (observado un spin-up inicial de ~25s
  en la primera petición tras suspensión). Sin embargo, una vez en caliente, el
  100 % de las peticiones subsecuentes responden de forma continua y
  determinista en menos de 300 ms, mientras que en Lambda cualquier escalado
  concurrente o invocación tras inactividad vuelve a penalizar con ~20s.
- **Observabilidad ligada al escenario:** El cumplimiento en producción se
  vigila mediante la métrica `duration_ms` registrada por `app/observability.py`
  en cada petición HTTP y publicada en `/metrics`.

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