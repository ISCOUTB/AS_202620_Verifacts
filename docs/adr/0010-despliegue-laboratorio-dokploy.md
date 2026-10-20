# ADR-0010: Desplegar el sistema de referencia en el servidor del laboratorio (Dokploy) con un único dominio

- Estado: Aceptado
- Fecha: 2026-10-19
- Decisor: Equipo VeriFacts
- Relación: complementa el [ADR-0004](0004-plataforma-despliegue.md) y el [ADR-0008](0008-mantener-render-mitigar-arranque-frio.md); no los reemplaza.

## Contexto

El curso habilitó una plataforma de despliegue en el servidor del laboratorio, gestionada con
Dokploy. Hasta ahora el sistema se desplegaba en Render (plan Free, ADR-0004), con dos
limitaciones documentadas:

- Sin disco persistente: el historial de `verifacts.db` se pierde en la inactividad o en un
  redespliegue ([persistencia-render.md](../evidencia/persistencia-render.md)).
- Arranque en frío: la primera petición tras 20 minutos sin tráfico tardó ≈22,4 s frente al
  umbral de 3 s de [Q-01](../escenarios-de-calidad.md#q-01--tiempo-de-respuesta-del-análisis)
  ([ADR-0008](0008-mantener-render-mitigar-arranque-frio.md)).

La restricción [R-TEC-05](../arc42/02-restricciones.md) (sin costo y sin tarjeta de crédito)
sigue vigente.

## Decisión

1. El despliegue de referencia pasa a ser el **servidor del laboratorio**, gestionado con
   Dokploy: proyecto `verifacts`, entorno `production`, servicio de tipo Compose `sistema`,
   definido por [`deploy/compose.lab.yaml`](../../deploy/compose.lab.yaml) en la rama `master`.
   URL: <http://verifacts-sistema-ju3vi7-444522-144-24-4-187.sslip.io>
2. El compose declara **dos servicios**:
   - `api`: el backend FastAPI, construido con el [`Dockerfile`](../../Dockerfile) de la raíz.
   - `web`: el frontend compilado y servido por nginx
     ([`frontend/Dockerfile`](../../frontend/Dockerfile),
     [`frontend/nginx.conf`](../../frontend/nginx.conf)).
3. **Un solo dominio.** Solo `web` se expone (puerto 80). nginx sirve la interfaz y reenvía
   `/analysis`, `/health` y `/metrics` al servicio `api` por la red interna del compose. El
   frontend se compila con `VITE_API_BASE_URL` vacía, de modo que llama a rutas relativas.
4. **Persistencia.** SQLite vive en el volumen nombrado `verifacts_data`, montado en `/data`
   (`VERIFACTS_DATA_DIR=/data`), que sobrevive a los redespliegues.
5. **Despliegue automático** en cada `push` a `master` (Autodeploy, trigger On Push).
6. **Configuración** por variables de entorno del panel (`LOG_LEVEL`, `ALLOWED_ORIGINS`);
   ninguna es un secreto y no se versiona ningún `.env`.
7. **Render no se retira** por este ADR: queda como despliegue secundario y su documentación se
   conserva ([despliegue.md](../despliegue.md), [costos.md](../costos.md)).

## Alternativas consideradas

| Alternativa | Motivo |
|---|---|
| Dos dominios, uno por servicio (como en `render.yaml`) | Descartada: exige un segundo host, habilitar CORS y fijar la URL de la API al compilar el frontend. |
| Un solo contenedor con la API sirviendo los archivos estáticos | Descartada: obliga a modificar `app/main.py` y mezcla responsabilidades de presentación y API. |
| Dokploy como aplicación simple (solo `Dockerfile`) | Descartada: se necesitan dos servicios y un volumen declarados en un archivo versionado. |
| Seguir solo en Render | Descartada: no ofrece persistencia gratuita y tiene arranque en frío medido. |
| HTTPS con certificado | No disponible por ahora: el dominio `sslip.io` no soporta SSL. Queda como mejora si se asigna un dominio con certificado. |

## Consecuencias

**Positivas**

- El historial persiste entre redespliegues, a diferencia de Render.
- Los contenedores permanecen encendidos, por lo que no se espera el arranque en frío de Render
  (no medido todavía; ver Verificación).
- La infraestructura es código versionado en el repositorio (`deploy/compose.lab.yaml`, los dos
  `Dockerfile` y `frontend/nginx.conf`).
- Sin costo y sin tarjeta, cumpliendo R-TEC-05.
- Al usar un único origen no hay dependencia de CORS entre interfaz y API.

**Negativas y limitaciones**

- **Solo HTTP, sin cifrado.** El dominio `sslip.io` no soporta SSL. Mitigación: la aplicación no
  guarda datos personales ([R-DAT-01](../arc42/02-restricciones.md)). Pasar a HTTPS solo requiere
  asignar un dominio con certificado en la pestaña Domains y activar HTTPS, sin cambios de código.
- **Un solo servidor y sin réplicas:** la disponibilidad depende del laboratorio.
- **Sin copias de seguridad del volumen.** Dokploy ofrece Volume Backups, pero no están configurados.
- **Cada push a `master` dispara un despliegue, incluso los parciales.** Observado el 2026-10-19: el
  commit que añadió `frontend/Dockerfile` (`f721a9d`) se desplegó antes de existir `nginx.conf` y
  falló; los commits siguientes lo corrigieron. Mitigación: subir los cambios de despliegue en un
  solo push o acotar los *Watch Paths* en Dokploy.
- El nombre de host incluye la IP pública del servidor; si esta cambia, cambia la URL.
- `/metrics` y `/health` quedan accesibles públicamente a través del proxy, igual que en Render.

## Relación con los escenarios de calidad

- [Q-01](../escenarios-de-calidad.md#q-01--tiempo-de-respuesta-del-análisis): el arranque en frío
  del ADR-0008 era propio de Render. En el laboratorio no se espera, pero tampoco está medido; se
  registrará en `docs/evidencia/` con el mismo payload de 10.000 caracteres. nginx añade un salto
  de proxy a cada petición.
- [Q-05](../escenarios-de-calidad.md#q-05--repetibilidad-del-resultado): la persistencia en volumen
  permite recuperar los análisis guardados tras un redespliegue (por verificar, ver abajo).

## Commits de implementación

- `feb7a56` — Add Docker Compose configuration for VeriFacts (`deploy/compose.lab.yaml`)
- `f721a9d` — Add Dockerfile for frontend build and serve
- `d576276` — Add Nginx configuration for frontend server
- `02fc29b` — Add .dockerignore to exclude specific files

## Verificación

| Comprobación | Estado |
|---|---|
| `GET /` devuelve la interfaz (título «VeriFacts — Análisis de contenido») | Comprobado el 2026-10-19 |
| Despliegues en Dokploy en estado Done (`d576276`, `02fc29b`) | Comprobado el 2026-10-19 |
| `GET /health` desde fuera de la universidad (datos móviles) | ⏳ Completar en [despliegue.md](../despliegue.md) |
| `POST /analysis` a través del proxy nginx | ⏳ Completar en [despliegue.md](../despliegue.md) |
| Persistencia tras un redespliegue | ⏳ Completar en [despliegue.md](../despliegue.md) |
