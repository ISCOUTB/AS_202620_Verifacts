# Despliegue de VeriFacts

## Despliegue de referencia: servidor del laboratorio (Dokploy)

**URL del sistema (interfaz y API):** http://verifacts-sistema-ju3vi7-444522-144-24-4-187.sslip.io

Decisión y alternativas en el [ADR-0010](adr/0010-despliegue-laboratorio-dokploy.md). Un solo dominio:
nginx sirve la interfaz y reenvía `/analysis`, `/health` y `/metrics` a la API.

| Requisito | Dónde está en el repositorio | Cómo se comprobó |
|---|---|---|
| URL accesible desde fuera de la universidad | http://verifacts-sistema-ju3vi7-444522-144-24-4-187.sslip.io | `GET /` devolvió la interfaz el 2026-10-19; desde datos móviles: ⏳ completar |
| Infraestructura como código versionada | `deploy/compose.lab.yaml`, `Dockerfile`, `frontend/Dockerfile`, `frontend/nginx.conf`, `.dockerignore`, `frontend/.dockerignore` | Servicio Compose `sistema` en Dokploy (proyecto `verifacts`, entorno `production`) construido desde `master`; despliegues `d576276` y `02fc29b` en estado Done |
| Pipeline en verde | `.github/workflows/tests.yml` (jobs `Tests` y `Build y smoke test de la imagen`) | Runs en verde en GitHub Actions tras cada push a `master` |
| Health check | `GET /health` en `app/api/routes.py`; `HEALTHCHECK` en `Dockerfile` y `frontend/Dockerfile`; `depends_on: service_healthy` en el compose | ⏳ completar con hora y código HTTP (ver comandos abajo) |
| Logs estructurados | `app/observability.py` (`JsonFormatter`, middleware `observe_requests`) | Una línea JSON por petición, visible en la pestaña Logs del servicio en Dokploy |
| Métrica consultable | `GET /metrics` (formato Prometheus) en `app/observability.py` | ⏳ completar con hora y código HTTP |
| Protección de secretos | `.gitignore` (ignora `.env`, `*.pem`, `*.key`), `.env.example` sin valores reales | Ningún secreto está versionado; las variables del panel (`LOG_LEVEL`, `ALLOWED_ORIGINS`) no son secretas |
| Persistencia | Volumen `verifacts_data` en `deploy/compose.lab.yaml` | ⏳ completar tras la prueba de redespliegue (ver abajo) |
| Despliegue automático | Autodeploy, trigger On Push sobre `master` | Cada push a `master` genera un despliegue en la pestaña Deployments |
| Estimación de costo mensual | `docs/costos.md` | Ver el documento |

### Configuración por variables de entorno (laboratorio)

| Variable | Uso | Valor en despliegue |
|---|---|---|
| `LOG_LEVEL` | Nivel de logs | `INFO` |
| `ALLOWED_ORIGINS` | Orígenes CORS permitidos | `http://verifacts-sistema-ju3vi7-444522-144-24-4-187.sslip.io` |
| `VERIFACTS_DATA_DIR` | Carpeta de `verifacts.db` | `/data` (fijada en el compose, volumen persistente) |
| `VITE_API_BASE_URL` | URL de la API usada por el frontend | vacía (rutas relativas; la define el compose como argumento de build) |

Ninguna de estas variables es un secreto. `HOST` y `PORT` los fija el `Dockerfile` de la API (`0.0.0.0` y `8000`).

### Comprobaciones con evidencia verificable (laboratorio)

Ejecutar desde CMD (con datos móviles para comprobar el acceso externo) y completar la columna Resultado con la hora y el código reales:

| Comprobación | Comando | Resultado |
|---|---|---|
| Raíz accesible | `curl -sS -o NUL -w "http=%{http_code} tiempo=%{time_total}s" http://verifacts-sistema-ju3vi7-444522-144-24-4-187.sslip.io/` | Interfaz devuelta el 2026-10-19 (título «VeriFacts — Análisis de contenido»); código y tiempo: ⏳ |
| Health check | `curl -sS -w " health=%{http_code}" http://verifacts-sistema-ju3vi7-444522-144-24-4-187.sslip.io/health` | ⏳ |
| Análisis a través del proxy | `curl -sS -X POST http://verifacts-sistema-ju3vi7-444522-144-24-4-187.sslip.io/analysis -H "Content-Type: application/json" -d "{\"text\":\"ESTA NOTICIA ES TOTALMENTE CIERTA!!! Todos deben compartirla!!!\"}"` | ⏳ (esperado: `score` 50, «Riesgo medio») |
| Métrica | `curl -sS http://verifacts-sistema-ju3vi7-444522-144-24-4-187.sslip.io/metrics` | ⏳ |
| Persistencia | 1) `POST /analysis` y anotar el `id`; 2) pulsar Deploy en Dokploy; 3) `GET http://verifacts-sistema-ju3vi7-444522-144-24-4-187.sslip.io/analysis/<id>` | ⏳ (esperado: el registro sigue existiendo) |
| Logs estructurados | Pestaña Logs del servicio `sistema` en Dokploy | ⏳ pegar una línea JSON real |

### Limitaciones conocidas

- Solo HTTP: el dominio `sslip.io` no soporta SSL (ver ADR-0010). En el celular, abrir con `http://` (ver más abajo).
- El nombre de host incluye la IP pública del servidor.
- Los pushes parciales a `master` generan despliegues intermedios fallidos (ejemplo: `f721a9d`).

### Acceso desde el celular («conexión no privada»)

**Causa.** El dominio `sslip.io` se sirve solo por HTTP: Dokploy indica que HTTPS no tiene efecto sobre
él. Al escribir la dirección sin `http://`, o al abrir un enlace reenviado, muchos navegadores móviles
reintentan con HTTPS. El proxy (Traefik) responde entonces con su certificado por defecto, que no es
válido para el dominio, y el navegador muestra «Tu conexión no es privada». En el computador funciona
porque la dirección se abrió con `http://`.

**Solución inmediata.** Abrir siempre la dirección completa, empezando por `http://`:

```text
http://verifacts-sistema-ju3vi7-444522-144-24-4-187.sslip.io
```

Si el navegador la convierte a HTTPS, desactivar la opción de conexiones seguras o HTTPS automático
en los ajustes de privacidad del navegador, o abrirla en otro navegador.

**Solución definitiva.** Un dominio con certificado válido: pedir al profesor un subdominio que apunte
a la IP del servidor y, en Dokploy, pestaña Domains: Host = ese dominio, HTTPS activado y
Certificate = Let's Encrypt; luego Deploy. No requiere cambios de código: el compose enruta por
dominio. Registrar el cambio en el [ADR-0010](adr/0010-despliegue-laboratorio-dokploy.md).

### Evidencia de integración continua

| Workflow | Página pública | Último run en verde |
|---|---|---|
| `Tests` (incluye `Build y smoke test de la imagen`) | https://github.com/ISCOUTB/AS_202620_Verifacts/actions/workflows/tests.yml | ⏳ pegar el enlace del run |
| `SonarCloud` | https://github.com/ISCOUTB/AS_202620_Verifacts/actions/workflows/sonarcloud.yml | ⏳ pegar el enlace del run |
| Quality Gate | https://sonarcloud.io/summary/new_code?id=ISCOUTB_AS_202620_Verifacts | ⏳ anotar el estado y la fecha |

El `schedule` de `keepalive.yml` se retiró para que los runs de estos workflows sean los más recientes
del listado público.

---

## Despliegue secundario: Render

Se conserva como respaldo y como evidencia de la comparación de plataformas
([ADR-0004](adr/0004-plataforma-despliegue.md), [ADR-0008](adr/0008-mantener-render-mitigar-arranque-frio.md)).

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

### Configuración por variables de entorno

| Variable | Uso | Valor en despliegue |
|---|---|---|
| `HOST` | Interfaz de escucha | `0.0.0.0` (fijado en el `Dockerfile`) |
| `PORT` | Puerto | `8000` |
| `LOG_LEVEL` | Nivel de logs | `INFO` |
| `ALLOWED_ORIGINS` | Orígenes CORS permitidos | `https://verifacts-web.onrender.com` |
| `VERIFACTS_DATA_DIR` | Carpeta de `verifacts.db` | `/data` (dentro del contenedor; no persistente, ver `docs/costos.md`) |
| `VITE_API_BASE_URL` | URL del backend usada por el frontend | `https://verifacts-api.onrender.com` |

Ninguna de estas variables es un secreto.

### Comprobaciones con evidencia verificable

| Comprobación | Comando | Resultado |
|---|---|---|
| URL raíz accesible | `curl -sS -o NUL -w "http=%{http_code} tiempo=%{time_total}s"` `https://verifacts-api.onrender.com` | `http=404 tiempo=1.85s` (esperado: no hay ruta definida en `/`, solo en `/health`, `/analysis`, `/metrics`) — comprobado el `2026-09-24 15:40:56 -05:00` |
| Health check | `curl -sS -o NUL -w "health=%{http_code}"` `https://verifacts-api.onrender.com/health` | `health=200` — comprobado el `2026-09-24 15:41:41 -05:00` |
| Logs estructurados (línea real) | `docker logs verifacts-demo` | `{"timestamp": "2026-09-23T21:14:27.641798+00:00", "level": "INFO", "logger": "verifacts", "message": "request", "request_id": "02f9862aee584b729e482237efec2c10", "method": "GET", "path": "/health", "route": "/health", "status": 200, "duration_ms": 15.18}` |
| Secretos tomados del entorno/almacén | `git grep -n "secrets\." .github/workflows/` | `sonarcloud.yml:24: SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}` — único secreto referenciado, tomado de GitHub Secrets, no hardcodeado en el repositorio |
| Pipeline en verde (verificado vía API) | `curl -s "https://api.github.com/repos/ISCOUTB/AS_202620_Verifacts/actions/runs?per_page=10"` | Run #141 (Tests, commit `d303673`): `"conclusion": "success"`. Run #140 (Tests y SonarCloud, commit `fa86606`): ambos `"conclusion": "success"` |
| Análisis estático (SonarCloud) | Panel de SonarCloud | Proyecto `ISCOUTB_AS_202620_Verifacts`: `https://sonarcloud.io/project/overview?id=ISCOUTB_AS_202620_Verifacts` — el análisis se ejecuta en verde en cada push (ver workflow `SonarCloud` en Actions); el Quality Gate general del proyecto está en VERDE (`status: OK`, 99.1 % de cobertura de código, 0.0 % líneas duplicadas, ratings A en fiabilidad, seguridad y mantenibilidad) — verificado vía API pública (`/api/qualitygates/project_status?projectKey=ISCOUTB_AS_202620_Verifacts`) el `2026-10-07`. |
