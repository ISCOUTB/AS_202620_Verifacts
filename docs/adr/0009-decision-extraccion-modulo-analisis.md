# ADR-0009: Decisión de no extraer el módulo de Extracción y Análisis de Contenido

- Estado: Aceptado
- Fecha: 2026-10-18
- Decisores: Equipo VeriFacts (Pedro Jose Castro Blanquicett, Cristian David Cardeno)
- Relación: complementa [ADR-0001](0001-estilo-arquitectonico.md) y [ADR-0003](0003-integracion-sincrona.md); conecta con [ADR-0008](0008-mantener-render-mitigar-arranque-frio.md).

## Contexto

El sistema VeriFacts opera actualmente bajo una arquitectura de **monolito modular** en FastAPI ([ADR-0001](0001-estilo-arquitectonico.md)), desplegado como un contenedor continuo en Render ([ADR-0008](0008-mantener-render-mitigar-arranque-frio.md)). 

Dentro del pipeline principal (`POST /analysis`), coexisten tres responsabilidades:
1. **Ingesta y Extracción de Contenido (`Content`)**: Valida la entrada y, si se provee una URL, realiza web scraping sincrónico mediante `trafilatura` y normaliza el texto.
2. **Análisis Lingüístico y Puntuación (`Analysis` y `Scoring`)**: Aplica reglas heurísticas (`RuleAnalyzer`) y clasifica el riesgo de desinformación de manera puramente computacional en memoria.
3. **Persistencia e Historial (`Persistence`)**: Guarda el resultado estructurado en una base de datos relacional SQLite (`app/persistence/repository.py`).

Se evalúa la posibilidad arquitectónica de **extraer el componente de Ingesta/Extracción y Análisis como un microservicio o función serverless independiente** frente a la alternativa de **mantenerlo integrado como módulo interno** del monolito modular.

Los escenarios y restricciones rectores son:
- [Q-01 — Tiempo de respuesta del análisis](../escenarios-de-calidad.md#q-01--tiempo-de-respuesta-del-análisis): P95 ≤ 3.000 ms para textos de hasta 10.000 caracteres.
- [Q-02 — Incorporación de un nuevo analizador](../escenarios-de-calidad.md#q-02--incorporación-de-un-nuevo-analizador): Añadir capacidad analítica sin modificar módulos adyacentes.
- [R-ORG-01 y R-ORG-02](../arc42/02-restricciones.md): Equipo pequeño (2-3 desarrolladores) con tiempo limitado.
- [R-TEC-05](../arc42/02-restricciones.md): Presupuesto de infraestructura gratuito o de bajo costo (sin tarjetas ni sobrecostos operacionales).

## Decisión

**NO EXTRAER** el módulo de Extracción y Análisis a un servicio independiente. Se mantiene como un **módulo acoplado por proceso pero desacoplado lógicamente** dentro del monolito modular de VeriFacts.

La comunicación entre la API, el extractor de contenido, el analizador y el repositorio seguirá realizándose mediante llamadas a funciones en memoria dentro del mismo proceso Python.

## Criterios y Justificación Técnica

### 1. Latencia y sobrecarga de red (Q-01)
En la arquitectura actual en proceso, la invocación de `extract_from_url`, `analyze_content`, `calculate_score` y `save_analysis` toma microsegundos a nivel de transferencia de datos. Extraer el módulo a un microservicio requeriría:
- Serialización y deserialización JSON en cada salto de red.
- Latencia de red interna (15 a 45 ms adicionales por ida y vuelta dentro de la infraestructura cloud gratuita).
- Potencial arranque en frío duplicado si se desplegara en entornos serverless ([ADR-0005](0005-comparacion-lambda-render.md), [ADR-0008](0008-mantener-render-mitigar-arranque-frio.md)).

### 2. Complejidad operacional y fallos parciales (R-ORG-01, R-ORG-02)
Al mantenerse en un solo proceso:
- No existen fallos parciales de red interservicios (RPC/HTTP timeout entre backend y analizador).
- La transacción de persistencia es estrictamente local en SQLite (consistencia inmediata ACID).
- No se requiere orquestación distribuida (Saga) para mantener coherencia entre la API y el análisis.
- Se mantiene un único pipeline de integración y despliegue continuo (CI/CD) y un único contenedor Docker.

### 3. Modularidad lógica ya garantizada (Q-02)
La modularidad del sistema está protegida por fronteras de paquetes estrictas y validada automáticamente por pruebas unitarias y de arquitectura (`tests/test_boundaries.py`). La interfaz de `AnalysisService` publica únicamente tipos de datos primitivos y value objects (`Finding`), evitando acoplamientos indeseados con la base de datos o el framework web.

## Alternativas consideradas

| Alternativa | Ventajas | Desventajas / Motivo de descarte |
|---|---|---|
| **Extraer a microservicio HTTP independiente** | Escalabilidad horizontal independiente del módulo de análisis; aislamiento de fallos si el scraping satura recursos. | Introduce latencia de red adicional (perjudicando Q-01), duplica el número de contenedores y servicios en Render (excediendo el nivel gratuito de R-TEC-05) y fuerza a manejar estados distribuidos y reintentos en red. |
| **Extraer a función serverless (AWS Lambda)** | Pago exacto por uso; escalado elástico a cero ante inactividad. | Rechazada previamente en [ADR-0005](0005-comparacion-lambda-render.md) y [ADR-0008](0008-mantener-render-mitigar-arranque-frio.md): incurre en cold starts de varios segundos debido al peso de las dependencias (`trafilatura`, `fastapi`), violando el P95 de 3.000 ms. |
| **Monolito modular con worker asíncrono en proceso (Celery/RQ)** | No bloquea el event loop ante URLs lentas. | Requiere un broker de mensajes (Redis/RabbitMQ) que complica la infraestructura actual. Descartado según [ADR-0003](0003-integracion-sincrona.md) mientras el volumen no lo justifique. |
| **Mantener en monolito modular (Elegida)** | Simplicidad operativa máxima, latencia mínima en memoria, costo \$0, atomicidad transaccional local directa. | Si una extracción web toma mucho tiempo, consume un worker de Uvicorn durante ese lapso. Mitigado mediante timeouts estrictos a nivel de HTTP client. |

## Consecuencias y Límites

### Positivas
- Conserva el cumplimiento de **Q-01** con latencias locales de P95 < 220 ms en caliente.
- Mantiene bajo costo operativo (\$0 USD) y despliegue unificado en Render.
- Elimina la necesidad de transacciones distribuidas o patrones Saga complejos.

### Negativas / Riesgos aceptados
- El proceso principal de FastAPI absorbe la carga de computación de `trafilatura` y las expresiones regulares del análisis. Si múltiples solicitudes concurrentes ingresan URLs con textos gigantes, pueden competir por la CPU del contenedor único (512 MB de RAM).

## Disparadores cuantitativos de reevaluación (Triggers de Extracción)

Esta decisión de no extraer se mantendrá vigente a menos que se cumpla al menos una de las siguientes condiciones empíricas:
1. **Volumen de scraping:** Más del 40 % de las peticiones diarias usen URL y la tasa de bloqueo de workers por latencia de sitios remotos cause saturación de conexiones en Uvicorn.
2. **Carga computacional de IA/ML:** La incorporación de un modelo de Deep Learning o NLP intensivo (GPU/Torch) que aumente la huella de memoria por encima de los 512 MB del contenedor estándar de Render.
3. **Escala de equipo:** Crecimiento del equipo a múltiples squads con ritmos de despliegue divergentes.
