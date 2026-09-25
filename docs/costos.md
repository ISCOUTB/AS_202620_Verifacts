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
## Comparación de despliegue para la pieza "API" (reto de corte)

Se comparó el despliegue actual de `verifacts-api` en Render (Web Service
sobre Docker) contra un prototipo serverless con AWS Lambda + Mangum,
medido localmente con AWS SAM CLI (`sam local invoke`, 15 corridas por
pieza — ver [ADR-0005](adr/0005-comparacion-lambda-render.md) para el
detalle completo, incluidos comandos y resultados).

| | Render (actual) | AWS Lambda (prototipo) |
|---|---|---|
| Sin tarjeta de crédito | Sí (plan Free) | Sí (capa gratuita, sin desplegar a cuenta real en este incremento) |
| P95 medido | Milisegundos en operación normal (ver `docs/despliegue.md`); ~50s solo tras inactividad prolongada | **20,005.9 ms** (ejecución en frío, 15 corridas) |
| Cumple Q-01 (P95 ≤ 3s) | Sí, en operación normal | **No** — 6.7 veces el límite |
| Memoria configurada | N/A (contenedor Free, límites de Render) | 512 MB |
| GB-segundo por invocación | N/A | ~10 GB-s (512 MB × 20s) |
| Punto de quiebre de la capa gratuita | N/A (Render Free: 750h/mes de cómputo, no por invocación) | **~40,000 invocaciones/mes** (limitado por cómputo: 400,000 GB-s ÷ 10 GB-s, no por las 1,000,000 invocaciones que anuncia la capa gratuita) |
| Costo tras superar la capa gratuita | Requiere upgrade a plan Starter (de pago, precio a confirmar en render.com/pricing) | ≈ $0.000367 por invocación adicional (cómputo + invocación); ejemplo: 10,000 invocaciones extra ≈ $3.67 |

**Causa técnica del resultado:** `trafilatura` (usada para extraer contenido
de una URL) se importa dentro del handler en cada invocación fría, en vez
de al nivel del módulo. Eso hace que el costo real de "arrancar en frío"
no aparezca en el `Init Duration` que reporta AWS (0.1 ms, prácticamente
nulo), sino en la duración de la propia ejecución (`Duration`, ~18-20s),
que si se factura, sí se cobra.

**Decisión:** se mantiene Render para `verifacts-api`. Ver
[ADR-0005](adr/0005-comparacion-lambda-render.md).