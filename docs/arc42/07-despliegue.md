# arc42 — Sección 7: Despliegue

## 7.1 Infraestructura actual

VeriFacts se despliega en **Render** (render.com), en el plan gratuito, sin
tarjeta de crédito (ver restricción [R-TEC-01](02-restricciones.md) y
[R-TEC-05](02-restricciones.md)). La infraestructura se define como código
en [`render.yaml`](../../render.yaml), versionado en la raíz del
repositorio y aplicado mediante la función Blueprint de Render. La
alternativa de usar Terraform se evaluó y se documentó en
[ADR-0004](../adr/0004-plataforma-despliegue.md).

```text
┌──────────────────────────────────────────────────────────────────────────┐
│                              Render (nube)                                │
│                                                                            │
│  ┌───────────────────────────┐         ┌───────────────────────────┐    │
│  │  verifacts-web             │         │  verifacts-api             │    │
│  │  (Static Site)             │  HTTP   │  (Web Service, Docker)     │    │
│  │  Frontend React            │────────▶│  uvicorn / app.main:app    │    │
│  │  https://verifacts-web.    │         │  Puerto 8000                │    │
│  │  onrender.com               │         │  /health · /metrics         │    │
│  └───────────────────────────┘         └──────────────┬─────────────┘    │
│                                                          │                  │
│                                                          ▼                  │
│                                          ┌───────────────────────────┐    │
│                                          │  data/verifacts.db (SQLite)│    │
│                                          │  dentro del contenedor —   │    │
│                                          │  no persistente entre       │    │
│                                          │  redeploys (plan gratuito) │    │
│                                          └───────────────────────────┘    │
└──────────────────────────────────────────────────────────────────────────┘
```

La imagen se construye a partir del [`Dockerfile`](../../Dockerfile)
versionado en la raíz del repositorio: instala las dependencias de
`requirements.txt`, copia `app/` y `run.py`, corre como usuario no root
(`appuser`), y expone un `HEALTHCHECK` sobre `/health`.

La aplicación se configura por variables de entorno (`HOST`, `PORT`,
`LOG_LEVEL`, `ALLOWED_ORIGINS`, `VERIFACTS_DATA_DIR`, `VITE_API_BASE_URL`;
ver [`.env.example`](../../.env.example)) para poder correr igual en local
y en despliegue — localmente con `python run.py` como hasta ahora, o en el
contenedor construido por el `Dockerfile`.

El backend expone logs estructurados en JSON
([`app/observability.py`](../../app/observability.py)) y una métrica
consultable en formato Prometheus (`GET /metrics`), verificables tanto en
`docker logs` local como desde la URL pública. El detalle de cada
requisito de despliegue y cómo comprobarlo está en
[`docs/despliegue.md`](../despliegue.md), y la estimación de costos en
[`docs/costos.md`](../costos.md).

## 7.2 Infraestructura de integración continua

GitHub Actions ejecuta las pruebas automatizadas y la construcción/
verificación de la imagen Docker en cada `push` y `pull request`, definido
en [`.github/workflows/tests.yml`](../../.github/workflows/tests.yml):

```text
Push / PR
   │
   ▼
GitHub Actions (runner ubuntu-latest)
   │
   ├─ Job "Tests"
   │    ├─ Checkout del repositorio
   │    ├─ Configurar Python 3.12
   │    ├─ pip install -r requirements.txt
   │    └─ PYTHONPATH=. pytest
   │
   └─ Job "Build y smoke test de la imagen" (depende de "Tests")
        ├─ docker build -t verifacts:ci .
        ├─ docker run -d -p 8000:8000 verifacts:ci
        ├─ Esperar /health (hasta 60s)
        ├─ Verificar /metrics
        └─ Mostrar logs estructurados del contenedor
```

El resultado de cada ejecución es consultable desde la pestaña **Actions**
del repositorio; la evidencia de la corrida más reciente en verde se cita
en la [tabla de aspectos](../aspectos.md) y en
[`docs/despliegue.md`](../despliegue.md).

## 7.3 Despliegue previsto (fuera del alcance actual)

Este incremento resuelve el despliegue accesible desde internet, la
infraestructura como código, el pipeline con verificación de la imagen
Docker, y la observabilidad básica (logs, métrica, health check). Quedan
fuera de este alcance, previstos para incrementos posteriores:

- Migración de SQLite a un motor con soporte de concurrencia y persistencia
  real (por ejemplo PostgreSQL), dado que el plan gratuito de Render no
  ofrece disco persistente y los datos se reinician en cada redeploy — ver
  [`docs/costos.md`](../costos.md).
- Despliegue automático desde el pipeline (actualmente `autoDeploy: false`
  en `render.yaml`; el despliegue se dispara manualmente desde el panel de
  Render).
- Medición formal del P95 de latencia con carga simulada (ver escenario
  [Q-01](../escenarios-de-calidad.md)), a partir de la instrumentación ya
  expuesta en `/metrics`.

Ver también [C4 — Contenedores](../c4/02-contenedores.md) y
[Sección 9 — Decisiones arquitectónicas](09-decisiones-arquitectonicas.md).