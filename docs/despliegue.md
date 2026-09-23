# Despliegue — evidencia de la entrega incremental

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