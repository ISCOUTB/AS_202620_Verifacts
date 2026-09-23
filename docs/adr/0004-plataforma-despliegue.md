# ADR-0004 — Plataforma de despliegue y forma de la infraestructura como código

## Estado

Aceptado — 2026-09-22

## Contexto

El incremento de despliegue de esta semana exige una URL del sistema
accesible desde fuera de la red de la universidad, infraestructura como
código versionada, pipeline en verde, health check, logs estructurados,
métrica consultable, evidencia de protección de secretos y una estimación
de costo mensual. El equipo cuenta con un tiempo limitado (ver
[R-ORG-01](../arc42/02-restricciones.md)) y sin presupuesto ni tarjeta de
crédito asignada para infraestructura cloud (ver
[R-TEC-05](../arc42/02-restricciones.md)).

Se consultó directamente con el profesor sobre la herramienta de
infraestructura como código a usar; la respuesta confirmó flexibilidad:
"puedes usar Terraform, Docker Compose, según lo que necesiten", sin exigir
una herramienta específica.

## Decisión

Se despliega VeriFacts en **Render** (render.com), usando su función
Blueprint a partir de un archivo `render.yaml` declarativo versionado en la
raíz del repositorio, que crea dos servicios: `verifacts-api` (Web Service
sobre la imagen construida desde el `Dockerfile`) y `verifacts-web` (Static
Site para el frontend). Ambos en el plan gratuito (Free), sin disco
persistente.

## Alternativas consideradas

### Terraform (con Render u otro proveedor cloud como backend)

Terraform es la herramienta de infraestructura como código mencionada
explícitamente en el material de la asignatura sobre arquitecturas
serverless como opción para automatizar despliegue. Se evaluó usarla junto
con el proveedor oficial de Render (`render-oss/render`) para definir
`verifacts-api` y `verifacts-web` como recursos `render_web_service` y
`render_static_site`.

Se descartó para este incremento porque:
- Agrega una herramienta adicional (binario de Terraform, estado
  `.tfstate`, variables sensibles como la API key de Render) que el equipo
  debía instalar y aprender contra el tiempo disponible del incremento
  ([R-ORG-01](../arc42/02-restricciones.md), [R-ORG-02](../arc42/02-restricciones.md)).
- El enunciado de la entrega pide "infraestructura como código versionada"
  sin exigir una herramienta específica; `render.yaml` ya cumple ese
  requisito de forma declarativa y versionada, con menor curva de
  aprendizaje.
- El estado de Terraform (`.tfstate`) añade una superficie extra de manejo
  de secretos que se prefiere evitar en un proyecto académico con equipo
  reducido.

No se descarta su uso en un incremento posterior si el alcance crece
(múltiples entornos, más de un proveedor cloud, necesidad de rollback
declarativo del estado de la infraestructura).

### AWS Lambda / arquitectura serverless (FaaS)

Se consideró brevemente, dado que el material de la asignatura de esta
semana trata específicamente arquitecturas serverless. Se descartó porque:
- Requeriría envolver la aplicación FastAPI con un adaptador (por ejemplo
  `Mangum`) y migrar la persistencia de SQLite a un servicio compatible con
  el modelo efímero de Lambda (por ejemplo DynamoDB), lo cual excede el
  alcance de este incremento semanal.
- El enunciado de la entrega no exige explícitamente un despliegue
  serverless, solo una URL accesible con los demás requisitos de
  observabilidad y costo.

## Consecuencias

- **Positivas:** despliegue rápido de lograr dentro del tiempo del
  incremento; `render.yaml` es legible y se revisa igual que cualquier otro
  archivo del repositorio; no se necesita instalar herramientas adicionales
  ni gestionar un estado de infraestructura separado; el plan Free no
  requiere tarjeta de crédito, cumpliendo R-TEC-05.
- **Negativas:** sin disco persistente, los datos de `verifacts.db` no
  sobreviven a un redeploy (ver [docs/costos.md](../costos.md)); el
  servicio "duerme" tras inactividad en el plan Free, con hasta ~50 s de
  demora en la primera petición; si el proyecto necesitara multi-nube o
  múltiples entornos coordinados, Terraform sería la opción más adecuada a
  reconsiderar.

  ## Commit de implementación

`render.yaml`, `Dockerfile` y `.dockerignore` fueron introducidos en el
commit
[`fa86606`](https://github.com/ISCOUTB/AS_202620_Verifacts/commit/fa866061cb8ba654a3685fab1c5b884e71afa77b)
("infra: render.yaml como IaC del despliegue, sin disco persistente").