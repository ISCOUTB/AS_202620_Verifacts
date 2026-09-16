**Asignatura:** Arquitectura de Software
**Proyecto:** VeriFacts
**Organización:** ISCOUTB
**Repositorio:** https://github.com/ISCOUTB/AS_202620_Verifacts

## Integrantes

- Pedro Jose Castro Blanquicett
- Cristian David Cardeno Gulloso

Usuarios de GitHub y detalle de roles en [Equipo.md](Equipo.md).

# 1. Descripción del proyecto

VeriFacts es una aplicación orientada al análisis de contenidos digitales para identificar indicadores asociados a posibles casos de desinformación.

El usuario podrá introducir un texto o una URL y obtener un resultado compuesto por una puntuación de riesgo, una clasificación y una explicación de los factores detectados.

VeriFacts no pretende determinar de manera absoluta si una información es verdadera o falsa. El objetivo es proporcionar indicadores que ayuden al usuario a realizar una evaluación inicial y crítica del contenido.

# 2. Problema

La circulación masiva de información en Internet dificulta que los usuarios puedan determinar rápidamente la confiabilidad de determinados contenidos.

Algunas publicaciones pueden presentar lenguaje sensacionalista, afirmaciones absolutas, ausencia de fuentes verificables u otras características que dificultan su evaluación.

La verificación manual requiere consultar diferentes fuentes y analizar el contenido, lo cual puede consumir tiempo.

VeriFacts busca automatizar una parte de esta evaluación mediante diferentes mecanismos de análisis.

# 3. Objetivo

Diseñar e implementar una aplicación web modular capaz de analizar contenidos digitales, identificar indicadores asociados a posibles casos de desinformación y presentar un resultado interpretable acompañado de una explicación.

# 4. Estado actual

El proyecto se encuentra actualmente en la etapa de desarrollo del prototipo, sobre una arquitectura ya validada.

La arquitectura seleccionada es un monolito modular, con una interfaz web (React) como cliente HTTP separado.

El repositorio contiene tres cortes verticales completos y ejecutables, más una interfaz web que los consume:

- recepción de una solicitud HTTP (texto o URL), normalización/extracción de contenido, análisis basado en reglas, cálculo de puntuación/clasificación y persistencia del resultado;
- consulta del historial de análisis previos, paginado;
- consulta de un análisis puntual por su identificador.

Actualmente se puede:

- iniciar el backend (`python run.py`) y el frontend (`npm run dev`);
- comprobar que la API está disponible (`GET /health`), incluyendo un indicador visual de conexión en la interfaz;
- enviar un texto **o una URL** para análisis desde la interfaz web y recibir puntuación, clasificación y factores (`POST /analysis`), con el resultado persistido en SQLite;
- consultar el historial de análisis pasados desde la interfaz (`GET /analysis`, paginado) y ver el detalle de uno (`GET /analysis/{id}`);
- ejecutar las pruebas automatizadas del backend, incluyendo una prueba de modificación localizada de una regla (Q-03) y una prueba de contrato de la API (S7), local y en GitHub Actions.

# 5. Arquitectura

## Estilo arquitectónico

Se seleccionó monolito modular después de comparar:

- arquitectura por capas;
- arquitectura hexagonal;
- monolito modular.

La decisión está registrada en:

[ADR-0001 — Usar monolito modular](docs/adr/0001-estilo-arquitectonico.md)

Los tres contextos delimitados del dominio (Ingesta y Presentación, Análisis
de Contenido, Historial de Análisis — ver
[mapa de contextos](docs/mapa-contextos.md)) se mantuvieron sin cambios tras
el corte 1, pese a la incorporación del frontend y la ampliación de
`Analysis`. La justificación está en:

[ADR-0002 — Contextos sin cambios tras el corte 1](docs/adr/0002-contextos-sin-cambios.md)

Ambas fronteras de integración (Frontend↔API y API↔sitio externo) se
mantienen síncronas; la justificación está en:

[ADR-0003 — Mantener integración síncrona en las dos fronteras actuales](docs/adr/0003-integracion-sincrona.md)

Explicación extendida, con comparación detallada frente a las alternativas y
trazabilidad hasta cada escenario de calidad, en:
[Sección 9 — Decisiones arquitectónicas](docs/arc42/09-decisiones-arquitectonicas.md)

La interfaz web (React) es un **contenedor separado** del monolito modular:
consume la API HTTP como cliente externo y no forma parte de los módulos
internos descritos abajo. Ver [C4 — Contenedores](docs/c4/02-contenedores.md).

## Módulos (backend)

```text
VeriFacts (backend)
│
├── API
│
├── Content
│
├── Analysis
│
├── Scoring
│
└── Persistencia
```

**API** — Recibe y coordina las solicitudes externas.

**Content** — Normaliza el texto recibido, o lo extrae desde una URL (vía `trafilatura`).

**Analysis** — Contiene los mecanismos de análisis; hoy `RuleAnalyzer` (reglas), ampliable con NLP o Machine Learning (ver [Registro de uso de IA](docs/ia.md)).

**Scoring** — Transforma los hallazgos del análisis en una puntuación y clasificación.

**Persistencia** — Guarda y recupera los resultados de cada análisis (SQLite).

Detalle completo de responsabilidades y trazabilidad con el código en la [Sección 5 — Vista de bloques](docs/arc42/05-vista-de-bloques.md).

## Modelo de dominio

Los tres contextos delimitados del backend, sus relaciones y la propiedad de
datos por módulo están documentados en:

- [Mapa de contextos](docs/mapa-contextos.md)
- [Propiedad de datos por módulo](docs/propiedad-datos.md)
- [Violaciones de modularidad detectadas y su plan de corrección](docs/violaciones-modularidad.md)

Cada fila de la [tabla de aspectos](docs/aspectos.md) está enlazada con el
contexto del dominio al que pertenece.

## Frontend

```text
frontend/
├── src/api/          → cliente HTTP hacia el backend
├── src/components/    → formulario, resultado, historial, indicador de salud
├── src/hooks/         → estado del historial paginado
└── src/styles/        → hoja de estilos única
```

El frontend es un cliente de la API, no tiene lógica de negocio propia:
normaliza nada, no calcula puntuaciones, solo envía la solicitud y presenta
la respuesta. Toda la lógica sigue viviendo en el backend, preservando el
monolito modular como estilo arquitectónico (ver [ADR-0001](docs/adr/0001-estilo-arquitectonico.md)).

# 6. Documentación arquitectónica

## arc42

- [Sección 1 — Introducción y objetivos](docs/arc42/01-introduccion-y-objetivos.md)
- [Sección 2 — Restricciones](docs/arc42/02-restricciones.md)
- [Sección 3 — Contexto y alcance](docs/arc42/03-contexto-y-alcance.md)
- [Sección 4 — Estrategia de solución](docs/arc42/04-estrategia-de-solucion.md)
- [Sección 5 — Vista de bloques](docs/arc42/05-vista-de-bloques.md)
- [Sección 6 — Vista de ejecución](docs/arc42/06-vista-de-ejecucion.md)
- [Sección 7 — Despliegue](docs/arc42/07-despliegue.md)
- [Sección 8 — Conceptos transversales](docs/arc42/08-conceptos-transversales.md)
- [Sección 9 — Decisiones arquitectónicas](docs/arc42/09-decisiones-arquitectonicas.md)
- [Sección 10 — Requisitos de calidad](docs/arc42/10-requisitos-de-calidad.md)
- [Sección 11 — Glosario](docs/arc42/11-glosario.md)

## Calidad

- [Escenarios de calidad](docs/escenarios-de-calidad.md)
- [Árbol de utilidad](docs/arbol-utilidad.md)
- [Aspectos arquitectónicos](docs/aspectos.md)
- [Matriz comparativa de estilos](docs/matriz-estilos.md)

## Contrato de la API (S7)

- [OpenAPI 3.1 — docs/contracts/openapi.yaml](docs/contracts/openapi.yaml)
- Prueba de contrato: [tests/test_contract.py](tests/test_contract.py)
- Decisión de integración: [ADR-0003](docs/adr/0003-integracion-sincrona.md)

## Modelo C4

- [C4 — Nivel 1: Contexto](docs/c4/01-contexto.md)
- [C4 — Nivel 2: Contenedores](docs/c4/02-contenedores.md)
- [C4 — Nivel 3: Componentes](docs/c4/03-componentes.md)

## Decisiones arquitectónicas

- [ADR-0001 — Usar monolito modular](docs/adr/0001-estilo-arquitectonico.md)
- [ADR-0002 — Contextos sin cambios tras el corte 1](docs/adr/0002-contextos-sin-cambios.md)
- [ADR-0003 — Integración síncrona en las dos fronteras actuales](docs/adr/0003-integracion-sincrona.md)

## Inteligencia Artificial

- [Registro de uso de IA](docs/ia.md)

## Información del equipo

- [Equipo](Equipo.md)

# 7. Estructura del repositorio

```text
AS_202620_Verifacts/
│
├── README.md
├── Equipo.md
├── requirements.txt
├── run.py
├── .gitignore
│
├── .github/
│   └── workflows/
│       ├── tests.yml
│       └── sonarcloud.yml
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py
│   │
│   ├── modules/
│   │   ├── __init__.py
│   │   ├── analysis/
│   │   │   ├── __init__.py
│   │   │   ├── analyzer.py
│   │   │   └── service.py
│   │   ├── content/
│   │   │   ├── __init__.py
│   │   │   └── service.py
│   │   └── scoring/
│   │       ├── __init__.py
│   │       └── service.py
│   │
│   └── persistence/
│       ├── __init__.py
│       └── repository.py
│
├── tests/
│   ├── __init__.py
│   ├── test_health.py
│   ├── test_analysis.py
│   ├── test_analysis_history.py
│   ├── test_rule_modification.py
│   └── test_contract.py
│
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── .env.example
│   ├── public/
│   │   └── favicon.svg
│   └── src/
│       ├── main.tsx
│       ├── App.tsx
│       ├── types.ts
│       ├── api/
│       │   └── client.ts
│       ├── components/
│       │   ├── HealthBadge.tsx
│       │   ├── AnalysisForm.tsx
│       │   ├── ResultPanel.tsx
│       │   ├── ScoreGauge.tsx
│       │   ├── ScanLine.tsx
│       │   └── HistoryLedger.tsx
│       ├── hooks/
│       │   └── useAnalysisHistory.ts
│       └── styles/
│           └── global.css
│
└── docs/
    ├── arc42/
    │   ├── 01-introduccion-y-objetivos.md
    │   ├── 02-restricciones.md
    │   ├── 03-contexto-y-alcance.md
    │   ├── 04-estrategia-de-solucion.md
    │   ├── 05-vista-de-bloques.md
    │   ├── 06-vista-de-ejecucion.md
    │   ├── 07-despliegue.md
    │   ├── 08-conceptos-transversales.md
    │   ├── 09-decisiones-arquitectonicas.md
    │   ├── 10-requisitos-de-calidad.md
    │   └── 12-glosario.md
    ├── c4/
    │   ├── 01-contexto.md
    │   ├── 02-contenedores.md
    │   └── 03-componentes.md
    ├── adr/
    │   ├── 0001-estilo-arquitectonico.md
    │   ├── 0002-contextos-sin-cambios.md
    │   └── 0003-integracion-sincrona.md
    ├── contracts/
    │   └── openapi.yaml
    ├── escenarios-de-calidad.md
    ├── arbol-utilidad.md
    ├── aspectos.md
    ├── matriz-estilos.md
    ├── mapa-contextos.md
    ├── propiedad-datos.md
    ├── violaciones-modularidad.md
    └── ia.md
```

No debe haber en el repositorio: carpetas `__pycache__/` o `node_modules/`,
archivos `*.pyc`, archivos duplicados con sufijos tipo `(1).py`, ni PDFs
sueltos en la raíz. Verificar con `git ls-files` antes de cada entrega.

# 8. Tecnologías actuales

## Backend

- Python 3.11+
- FastAPI (con `CORSMiddleware` habilitado para el frontend)
- Uvicorn
- SQLite (vía `sqlite3`, módulo estándar)
- trafilatura (extracción de contenido desde una URL)

## Frontend

- React 18
- TypeScript
- Vite

## Pruebas

- Pytest
- HTTPX (usado internamente por `TestClient`)
- PyYAML y jsonschema (cargan `docs/contracts/openapi.yaml` y validan las
  respuestas reales contra ese contrato en `tests/test_contract.py`)

## Calidad y colaboración

- Git
- GitHub
- GitHub Actions (workflows independientes para pruebas y SonarCloud)
- SonarCloud

## Tecnologías previstas para etapas posteriores

- SQLAlchemy (si se migra de `sqlite3` puro a un ORM)
- spaCy
- scikit-learn

Estas últimas se incorporarán progresivamente conforme avance el proyecto.

# 9. Requisitos para ejecutar el proyecto

Se necesita:

- Python 3.11 o superior.
- Node.js 18 o superior (incluye `npm`), para el frontend.
- Git.
- Acceso al repositorio.

# 10. Clonar el repositorio

Desde una terminal:

```cmd
git clone https://github.com/ISCOUTB/AS_202620_Verifacts.git
cd AS_202620_Verifacts
```

# 11. Crear el entorno virtual (backend)

## Windows

```cmd
python -m venv .venv
.venv\Scripts\activate
```

# 12. Instalar dependencias (backend)

Con el entorno virtual activado:

```cmd
pip install -r requirements.txt
```

Desde S7, esto incluye `pyyaml` y `jsonschema`, usadas solo por
`tests/test_contract.py` para validar respuestas contra
`docs/contracts/openapi.yaml`; no son necesarias para correr el servidor,
solo para las pruebas.

# Corte vertical ejecutable

Las secciones 13 a 20 documentan, paso a paso, los recorridos de extremo a extremo que hoy son ejecutables en VeriFacts: arrancar el backend, arrancar el frontend, verificar los tres flujos (disponibilidad, análisis con persistencia, historial) tanto desde la interfaz web como con las pruebas automatizadas, y el contrato formal que los describe. Ver también su descripción arquitectónica en [Sección 6 — Vista de ejecución](docs/arc42/06-vista-de-ejecucion.md) y su trazabilidad hasta la evidencia de prueba en las filas **A-00** a **A-05** de la [tabla de aspectos](docs/aspectos.md).

# 13. Arranque del backend

El backend se inicia con un único comando:

```cmd
python run.py
```

Esta es la instrucción oficial de arranque. Al iniciar, también se
inicializa automáticamente la base de datos SQLite (`data/verifacts.db`) si
no existe, y se aplican migraciones de esquema si faltan columnas nuevas
(ver `app/persistence/repository.py`).

Una vez iniciado, el backend estará disponible en:
http://127.0.0.1:8000

La documentación automática de FastAPI estará disponible en:
http://127.0.0.1:8000/docs

# 14. Comprobación de disponibilidad
GET /health


Con el servidor ejecutándose, abrir:
http://127.0.0.1:8000/health

La respuesta esperada es:

```json
{
  "status": "ok"
}
```

Esta ruta solamente verifica que el servicio está funcionando; no representa
todavía una funcionalidad de negocio de VeriFacts.

# 15. Análisis de contenido (corte vertical completo)

El endpoint de negocio principal es:

POST /analysis


Acepta **exactamente uno** de dos orígenes — nunca ambos, nunca ninguno —
validado antes de tocar cualquier módulo interno (`422` si no se cumple):

```json
{ "text": "ESTA NOTICIA ES TOTALMENTE CIERTA!!! Todos deben compartirla!!!" }
```

```json
{ "url": "https://ejemplo.com/una-noticia" }
```

Respuesta esperada (origen `text`):

```json
{
  "id": 1,
  "score": 50,
  "classification": "Riesgo medio",
  "factors": [
    "Lenguaje sensacionalista",
    "Uso excesivo de mayúsculas",
    "Afirmación absoluta"
  ],
  "source_type": "texto",
  "created_at": "2026-09-08 20:10:00"
}
```

Con origen `url`, la respuesta tiene la misma forma, con `"source_type": "url"`.

Internamente, la solicitud atraviesa `Content` (normalización o extracción
vía `trafilatura`) → `Analysis` (`RuleAnalyzer`) → `Scoring` (puntuación y
clasificación) → `Persistencia` (guardado en SQLite). El detalle paso a
paso está en la
[Sección 6.2 — Vista de ejecución](docs/arc42/06-vista-de-ejecucion.md#62-escenario-análisis-de-contenido-post-analysis).
La forma exacta de la respuesta (contrato formal) está en
[docs/contracts/openapi.yaml](docs/contracts/openapi.yaml).

# 16. Historial de análisis

Dos endpoints adicionales permiten consultar análisis pasados, usados por la
pestaña "Historial" del frontend:

GET /analysis?limit=20&offset=0
GET /analysis/{id}


El primero devuelve un **arreglo plano** de resultados (más recientes
primero); el total disponible para paginar viaja en la cabecera HTTP
`X-Total-Count`, no en el cuerpo (`frontend/src/api/client.ts` lo lee así).
El segundo devuelve un análisis puntual, o `404` si el `id` no existe. Ver
[Sección 6.3 — Vista de ejecución](docs/arc42/06-vista-de-ejecucion.md#63-escenario-consulta-de-historial-get-analysis-get-analysisid).

# 17. Contrato de la API y prueba de contrato (S7)

El contrato HTTP completo de VeriFacts — los cuatro endpoints de las
secciones 14 a 16, con sus esquemas de solicitud/respuesta, códigos de
estado y la cabecera `X-Total-Count` — está especificado de forma
ejecutable y versionada en:

[docs/contracts/openapi.yaml](docs/contracts/openapi.yaml) (OpenAPI 3.1, versión `1.0.0`)

`tests/test_contract.py` valida en cada corrida que las respuestas reales
de la API cumplen ese contrato, usando `jsonschema` contra los esquemas
declarados en el archivo anterior. Corre junto con el resto de `tests/` (ver
sección 18) y en el mismo workflow de CI (sección 19), así que un cambio
incompatible rompe el `push` antes de llegar a `master`.

Se verificó manualmente (y no quedó como código permanente) que renombrar
`score` → `risk_score` en `AnalysisResponse`/`AnalysisSummary`
(`app/api/routes.py`) hace fallar 4 de las 12 pruebas de contrato; al
revertir el cambio, las 20 pruebas del proyecto vuelven a pasar. El detalle
está en
[Sección 6.5 — Vista de ejecución](docs/arc42/06-vista-de-ejecucion.md#65-contrato-de-la-api-y-prueba-de-contrato-s7).

La decisión de mantener ambas fronteras de integración (Frontend↔API,
API↔sitio externo) síncronas, en lugar de introducir una cola de trabajos,
está registrada en
[ADR-0003](docs/adr/0003-integracion-sincrona.md).

# 18. Arranque del frontend

En una segunda terminal, con el backend ya corriendo (paso 13):

```cmd
cd frontend
npm install
npm run dev
```

El frontend estará disponible en:
http://localhost:5173

Por defecto se conecta al backend en `http://127.0.0.1:8000` (ver
`frontend/src/api/client.ts`). El backend permite esa conexión mediante
`CORSMiddleware`, configurado en `app/main.py` para el origen
`http://localhost:5173`. Si el backend corriera en otra URL, copiar
`frontend/.env.example` a `frontend/.env.local` y ajustar
`VITE_API_BASE_URL`.

Con ambos servidores corriendo, la pestaña **Analizar** envía texto o una
URL a `POST /analysis` y anima la puntuación resultante; la pestaña
**Historial** consulta `GET /analysis` y permite expandir cada fila para
ver sus factores (`GET /analysis/{id}` se usa igual, para un caso puntual).

# 19. Ejecutar las pruebas del backend

Con el entorno virtual activado, desde la raíz del repositorio (no dentro de `tests/`), ejecutar:

```cmd
python -m pytest -q
```

**Nota:** usa siempre `python -m pytest -q` y no solo `pytest -q`. En algunos entornos de Windows, el comando corto `pytest -q` no agrega automáticamente la carpeta actual a la ruta de búsqueda de Python, lo que produce `ModuleNotFoundError: No module named 'app'`. La forma `python -m pytest -q` evita ese problema.

Las pruebas actuales comprueban:

- que la aplicación puede inicializarse;
- que la ruta `/health` existe y responde correctamente (`tests/test_health.py`);
- que `POST /analysis` normaliza, analiza, puntúa, clasifica y persiste correctamente un contenido de extremo a extremo (`tests/test_analysis.py`);
- que `GET /analysis` pagina correctamente y que `GET /analysis/{id}` devuelve el análisis correcto o `404` si no existe (`tests/test_analysis_history.py`);
- que modificar una regla existente de `RuleAnalyzer` (ampliar el conjunto de palabras absolutas) es un cambio localizado que no rompe las demás pruebas (`tests/test_rule_modification.py`, evidencia de Q-03);
- que la API cumple su contrato OpenAPI en cada endpoint y código de estado (`tests/test_contract.py`, evidencia de S7 / A-05).

El resultado esperado es similar a: `20 passed`

El frontend no tiene pruebas automatizadas todavía; se verifica manualmente
siguiendo el paso 18 y comprobando visualmente los tres flujos. Queda como
trabajo pendiente incorporar una prueba de componente (ver sección 21).

# 20. Integración continua

El repositorio incluye dos workflows independientes en `.github/workflows/`:

- `tests.yml` — instala dependencias (incluidas `pyyaml` y `jsonschema` desde S7) y ejecuta las pruebas en cada `push` o `pull request`, incluyendo `tests/test_contract.py`. Es el que se cita como evidencia de CI en verde en la [tabla de aspectos](docs/aspectos.md).
- `sonarcloud.yml` — ejecuta el análisis de calidad de código con SonarCloud, de forma independiente para no bloquear la evidencia de pruebas si el análisis de Sonar falla por configuración externa.

El frontend no forma parte todavía del pipeline de CI (ver sección 21, pendientes).

El flujo del workflow de pruebas es:

Push
↓
GitHub Actions (tests.yml)
↓
Instalar dependencias
↓
Ejecutar pytest (incluye tests/test_contract.py)
↓
✓ Tests


El resultado puede consultarse desde la pestaña **Actions** del repositorio;
el enlace al run más reciente en verde del workflow **Tests** se cita en la
[tabla de aspectos](docs/aspectos.md).

# 21. Desarrollo actual y próximos pasos

Ya implementado dentro de las fronteras arquitectónicas definidas (ver
[Sección 5 — Vista de bloques](docs/arc42/05-vista-de-bloques.md)):

- análisis de contenido basado en reglas;
- normalización de contenido de texto, y extracción de contenido desde una URL (`trafilatura`);
- cálculo de puntuación y clasificación;
- persistencia de resultados (SQLite), con migración de esquema segura;
- historial de análisis paginado y consulta individual;
- interfaz web (React) que consume los tres flujos anteriores;
- corte vertical completo con pruebas automatizadas (backend), incluyendo evidencia de modificación localizada de una regla (Q-03);
- mapa de contextos, propiedad de datos por módulo y aspectos enlazados a esos contextos (S6);
- contrato de API versionado en OpenAPI 3.1, con prueba de contrato en el pipeline y ADR que justifica la integración síncrona (S7).

Pendiente para próximos incrementos:

- procesamiento NLP (spaCy);
- evaluación de Machine Learning (scikit-learn), condicionada a disponer de un dataset adecuado;
- prueba automatizada de componente para el frontend;
- incorporar el build del frontend a GitHub Actions;
- medición formal de P95 para Q-01, diferenciando origen `text` de origen `url` (ver [ADR-0003 — Deuda aceptada](docs/adr/0003-integracion-sincrona.md#deuda-aceptada));
- medición formal de usabilidad para Q-04, ahora que existe una interfaz sobre la cual ejecutarla;
- confirmar en sonarcloud.io que el token es válido y que "Automatic Analysis" está apagado, para que el workflow `sonarcloud.yml` quede en verde.

# 22. Principios arquitectónicos

La implementación sigue los siguientes criterios:

**Modularidad** — Cada módulo tiene responsabilidades claramente delimitadas.

**Bajo acoplamiento** — Se evitan dependencias innecesarias entre módulos. El frontend depende únicamente del contrato HTTP público, nunca de detalles internos del backend.

**Alta cohesión** — Las responsabilidades relacionadas se mantienen juntas.

**Encapsulación de la variación** — Los mecanismos que pueden cambiar, como las reglas de análisis, se mantienen aislados.

**Evolución gradual** — La arquitectura permite incorporar nuevos mecanismos de análisis, o un nuevo cliente como el frontend, sin modificar innecesariamente los demás componentes.

**Contrato explícito sobre acuerdo implícito** — Desde S7, la forma de la API vive en un archivo versionado (`docs/contracts/openapi.yaml`), no solo en la memoria del equipo o en prosa que puede desactualizarse; una prueba automatizada la hace cumplir.

# 23. Estado de la línea base

## Arquitectura

- [x] Comparación de estilos.
- [x] Monolito modular seleccionado.
- [x] ADR-0001.
- [x] ADR-0002 — contextos sin cambios tras el corte 1.
- [x] ADR-0003 — integración síncrona en las dos fronteras actuales.
- [x] arc42 secciones 1–10 y 12.
- [x] Glosario (sección 12, con secciones 7 y 8 agregadas).
- [x] Árbol de utilidad.
- [x] Escenarios de calidad (Q-01 a Q-05), con anchors verificados y evidencia enlazada.
- [x] Matriz comparativa.
- [x] C4 Nivel 1 — Contexto, con leyenda.
- [x] C4 Nivel 2 — Contenedores, con leyenda, estado real (SQLite y frontend implementados) y cada flecha etiquetada con protocolo y formato (S7).
- [x] C4 Nivel 3 — Componentes, con correspondencia real al código.
- [x] Restricciones arquitectónicas.
- [x] Registro de uso de IA.
- [x] Mapa de contextos y propiedad de datos por módulo.
- [x] Tabla de aspectos con las 8 columnas del curso, trazabilidad completa hasta Pruebas, y enlace explícito a los contextos del mapa de dominio.
- [x] Contrato de API en OpenAPI 3.1, versionado, en `docs/contracts/openapi.yaml` (S7).

## Esqueleto y cortes verticales

- [x] Aplicación FastAPI.
- [x] Estructura modular.
- [x] Endpoint `GET /health`.
- [x] Endpoint `POST /analysis` con validación (Pydantic), origen `text` o `url`.
- [x] Endpoints `GET /analysis` y `GET /analysis/{id}` (historial).
- [x] Persistencia SQLite integrada, con migración de esquema segura.
- [x] Pruebas automatizadas del backend (20 casos, incluyendo evidencia de Q-03 y del contrato de API).
- [x] Interfaz web (React + Vite) conectada a los tres flujos.
- [x] Comando único de arranque por servicio (`python run.py`, `npm run dev`).
- [x] GitHub Actions configurado, con workflows independientes para pruebas y SonarCloud.
- [x] Prueba de contrato en el pipeline, con comprobación manual de que falla ante un cambio incompatible (S7).

## Pendiente

- [ ] Confirmar el workflow `sonarcloud.yml` en verde (token y configuración de "Automatic Analysis" en sonarcloud.io).
- [ ] Medición formal de P95 para Q-01 (diferenciando origen `text` de origen `url`).
- [ ] Medición formal de usabilidad (Q-04) usando la interfaz ya disponible.
- [ ] Integrar procesamiento NLP.
- [ ] Evaluar Machine Learning.
- [ ] Prueba automatizada de componente para el frontend.
- [ ] Incorporar el build del frontend a GitHub Actions.

# 24. Repositorio

Repositorio oficial:

https://github.com/ISCOUTB/AS_202620_Verifacts

**Proyecto:** VeriFacts
**Equipo:** Pedro Jose Castro Blanquicett, Cristian David Cardeno Gulloso

La aplicación incluye un endpoint técnico de comprobación:
