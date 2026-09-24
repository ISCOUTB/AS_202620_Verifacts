**URL del sistema (API):** https://verifacts-api.onrender.com
**URL del sistema (interfaz web):** https://verifacts-web.onrender.com

| Requisito | Dónde está en el repositorio | Cómo se comprobó |
|---|---|---|
| URL accesible desde fuera de la universidad | https://verifacts-api.onrender.com y https://verifacts-web.onrender.com | Probado desde datos móviles (fuera de la red de la universidad); `GET /health` respondió `{"status":"ok"}` |
| Infraestructura como código versionada | `Dockerfile`, `.dockerignore`, `render.yaml` | Blueprint aplicado en Render a partir de `render.yaml`, creando `verifacts-api` (Docker) y `verifacts-web` (Static Site) |
| Pipeline en verde | `.github/workflows/tests.yml` (jobs `Tests` y `Build y smoke test de la imagen`) | Runs en verde en GitHub Actions tras cada push a `master` |
| Health check | `GET /health` en `app/api/routes.py`; `HEALTHCHECK` en `Dockerfile` | `curl https://verifacts-api.onrender.com/health` |
| Logs estructurados | `app/observability.py` (`JsonFormatter`, middleware `observe_requests`) | Una línea JSON por petición, visible en `docker logs` local y en los logs de Render |
| Métrica consultable | `GET /metrics` (formato Prometheus) en `app/observability.py` | `curl https://verifacts-api.onrender.com/metrics` |
| Protección de secretos | `.gitignore` (ignora `.env`, `*.pem`, `*.key`), `.env.example` sin valores reales | Ningún secreto está versionado en el repositorio; variables sensibles se configuran directamente en el panel de Render |
| Estimación de costo mensual | `docs/costos.md` | Ver el documento |

## Configuración por variables de entorno

| Variable | Uso | Valor en despliegue |
|---|---|---|
| `HOST` | Interfaz de escucha | `0.0.0.0` (fijado en el `Dockerfile`) |
| `PORT` | Puerto | `8000` |
| `LOG_LEVEL` | Nivel de logs | `INFO` |
| `ALLOWED_ORIGINS` | Orígenes CORS permitidos | `https://verifacts-web.onrender.com` |
| `VERIFACTS_DATA_DIR` | Carpeta de `verifacts.db` | `/data` (dentro del contenedor; no persistente, ver `docs/costos.md`) |
| `VITE_API_BASE_URL` | URL del backend usada por el frontend | `https://verifacts-api.onrender.com` |

Ninguna de estas variables es un secreto.

## Comprobaciones con evidencia verificable

| Comprobación | Comando | Resultado |
|---|---|---|
| URL raíz accesible | `curl -sS -o NUL -w "http=%{http_code} tiempo=%{time_total}s"` `https://verifacts-api.onrender.com` | `http=404 tiempo=1.85s` (esperado: no hay ruta definida en `/`, solo en `/health`, `/analysis`, `/metrics`) — comprobado el `2026-09-24 15:40:56 -05:00` |
| Health check | `curl -sS -o NUL -w "health=%{http_code}"` `https://verifacts-api.onrender.com/health` | `health=200` — comprobado el `2026-09-24 15:41:41 -05:00` |
| Logs estructurados (línea real) | `docker logs verifacts-demo` | `{"timestamp": "2026-09-23T21:14:27.641798+00:00", "level": "INFO", "logger": "verifacts", "message": "request", "request_id": "02f9862aee584b729e482237efec2c10", "method": "GET", "path": "/health", "route": "/health", "status": 200, "duration_ms": 15.18}` |
| Secretos tomados del entorno/almacén | `git grep -n "secrets\." .github/workflows/` | `sonarcloud.yml:24: SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}` — único secreto referenciado, tomado de GitHub Secrets, no hardcodeado en el repositorio |
| Pipeline en verde (verificado vía API) | `curl -s "https://api.github.com/repos/ISCOUTB/AS_202620_Verifacts/actions/runs?per_page=10"` | Run #141 (Tests, commit `d303673`): `"conclusion": "success"`. Run #140 (Tests y SonarCloud, commit `fa86606`): ambos `"conclusion": "success"` |
| Análisis estático (SonarCloud) | Panel de SonarCloud | Proyecto `ISCOUTB_AS_202620_Verifacts`: `https://sonarcloud.io/project/overview?id=ISCOUTB_AS_202620_Verifacts` — el análisis se ejecuta en verde en cada push (ver workflow `SonarCloud` en Actions); el Quality Gate general del proyecto está en rojo. No forma parte de los 7 requisitos de esta entrega de despliegue (ver [ADR-0004](adr/0004-plataforma-despliegue.md) para el alcance de este incremento) |