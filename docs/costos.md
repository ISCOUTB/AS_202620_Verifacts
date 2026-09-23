# Estimación de costo mensual

> Nota: no fue posible ubicar la «Guía de despliegue y costos» mencionada en el enunciado dentro de los materiales del curso. Esta estimación sigue un criterio estándar de costeo en la nube (identificar recursos, tarifa de cada uno, uso esperado y supuestos), aplicado a la infraestructura real desplegada.

## Infraestructura desplegada

| Recurso | Plataforma | Plan |
|---|---|---|
| `verifacts-api` (Web Service, Docker) | Render | Free |
| `verifacts-web` (Static Site) | Render | Free |

## Supuestos

- Tráfico esperado: uso académico, bajo volumen (decenas de peticiones por día durante la evaluación, no tráfico de producción real).
- Sin disco persistente: se usa SQLite dentro del contenedor efímero (`VERIFACTS_DATA_DIR=/data`), que se reinicia en cada redeploy. Se decidió así para mantener el costo en $0; si se requiriera persistencia real, el costo cambiaría (ver "Escenario con persistencia" más abajo).
- El repositorio de origen es público, por lo que no aplica costo de almacenamiento privado de código.
- No se configuró un dominio propio (se usa el subdominio gratuito `.onrender.com`).
- No hay despliegue automático desde el pipeline (`autoDeploy: false`); los despliegues se disparan manualmente, sin costo adicional de cómputo por builds automáticos.

## Estimación

| Concepto | Plan | Costo mensual |
|---|---|---|
| `verifacts-api` (Web Service) | Free | $0 |
| `verifacts-web` (Static Site) | Free | $0 |
| Ancho de banda saliente | Incluido en el plan Free (100 GB/mes) | $0, mientras no se exceda |
| **Total estimado** | | **$0/mes** |

## Limitación conocida del plan gratuito

El plan Free de Render "duerme" el servicio `verifacts-api` tras un período de inactividad. La primera petición después de ese período puede tardar hasta 50 segundos en responder, mientras el servicio despierta. Esto no representa un costo monetario, pero sí una limitación de disponibilidad a tener en cuenta.

## Escenario con persistencia (fuera del alcance actual)

Si se necesitara que los datos de `verifacts.db` sobrevivan entre redeploys, la opción más simple es agregar un disco persistente al servicio `verifacts-api`, lo cual requiere pasar del plan Free al plan **Starter** de Render (de pago). El costo exacto depende del tamaño del disco y debe confirmarse en la página de precios de Render al momento de aplicarlo, ya que estas tarifas pueden cambiar.