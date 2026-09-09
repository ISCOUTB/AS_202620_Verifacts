# VeriFacts

Sistema inteligente para análisis de información digital

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

- recepción de una solicitud HTTP, normalización de contenido, análisis basado en reglas, cálculo de puntuación/clasificación y persistencia del resultado;
- consulta del historial de análisis previos, paginado;
- consulta de un análisis puntual por su identificador.

Actualmente se puede:

- iniciar el backend (`python run.py`) y el frontend (`npm run dev`);
- comprobar que la API está disponible (`GET /health`), incluyendo un indicador visual de conexión en la interfaz;
- enviar un texto para análisis desde la interfaz web y recibir puntuación, clasificación y factores (`POST /analysis`), con el resultado persistido en SQLite;
- consultar el historial de análisis pasados desde la interfaz (`GET /analysis`, paginado) y ver el detalle de uno (`GET /analysis/{id}`);
- ejecutar las pruebas automatizadas del backend (local y en GitHub Actions).

# 5. Arquitectura

## Estilo arquitectónico

Se seleccionó monolito modular después de comparar:

- arquitectura por capas;
- arquitectura hexagonal;
- monolito modular.

La decisión está registrada en:

[ADR-0001 — Usar monolito modular](docs/adr/0001-estilo-arquitectonico.md)

Explicación extendida, con comparación detallada frente a las alternativas y
trazabilidad hasta cada escenario de calidad, en:
[Decisiones arquitectónicas explicadas](docs/decisiones-arquitectonicas.md)

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

**Content** — Normaliza y valida el contenido recibido mediante texto o URL.

**Analysis** — Contiene los mecanismos de análisis; hoy `RuleAnalyzer` (reglas), ampliable con NLP o Machine Learning (ver [Registro de uso de IA](docs/ia.md)).

**Scoring** — Transforma los hallazgos del análisis en una puntuación y clasificación.

**Persistencia** — Guarda y recupera los resultados de cada análisis (SQLite).

Detalle completo de responsabilidades y trazabilidad con el código en la [Sección 5 — Vista de bloques](docs/arc42/05-vista-de-bloques.md).

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
- [Decisiones arquitectónicas explicadas](docs/decisiones-arquitectonicas-explicadas.md)

## Modelo C4

- [C4 — Nivel 1: Contexto](docs/c4/01-contexto.md)
- [C4 — Nivel 2: Contenedores](docs/c4/02-contenedores.md)
- [C4 — Nivel 3: Componentes](docs/c4/03-componentes.md)

## Decisiones arquitectónicas

- [ADR-0001 — Usar monolito modular](docs/adr/0001-estilo-arquitectonico.md)

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
│       └── tests.yml
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
│   └── test_history.py
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
    │   └── 0001-estilo-arquitectonico.md
    ├── escenarios-de-calidad.md
    ├── arbol-utilidad.md
    ├── aspectos.md
    ├── matriz-estilos.md
    ├── mapa-contextos.md
    ├── propiedad-datos.md
    ├── decisiones-arquitectonicas-explicadas.md
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

## Frontend

- React 18
- TypeScript
- Vite

## Pruebas

- Pytest
- HTTPX (usado internamente por `TestClient`)

## Calidad y colaboración

- Git
- GitHub
- GitHub Actions
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

# Corte vertical ejecutable

Las secciones 13 a 19 documentan, paso a paso, los recorridos de extremo a extremo que hoy son ejecutables en VeriFacts: arrancar el backend, arrancar el frontend, y verificar los tres flujos (disponibilidad, análisis con persistencia, historial) tanto desde la interfaz web como con las pruebas automatizadas. Ver también su descripción arquitectónica en [Sección 6 — Vista de ejecución](docs/arc42/06-vista-de-ejecucion.md) y su trazabilidad hasta la evidencia de prueba en las filas **A-00** a **A-04** de la [tabla de aspectos](docs/aspectos.md).

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

La aplicación incluye un endpoint técnico de comprobación:

```
GET /health
```

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

```
POST /analysis
```

Ejemplo de solicitud (desde `http://127.0.0.1:8000/docs`, `curl`, o la
interfaz web):

```json
{
  "text": "ESTA NOTICIA ES TOTALMENTE CIERTA!!! Todos deben compartirla!!!"
}
```

Respuesta esperada:

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
  "created_at": "2026-09-08 20:10:00"
}
```

Internamente, la solicitud atraviesa `Content` (normalización) →
`Analysis` (`RuleAnalyzer`) → `Scoring` (puntuación y clasificación) →
`Persistencia` (guardado en SQLite). El detalle paso a paso está en la
[Sección 6.2 — Vista de ejecución](docs/arc42/06-vista-de-ejecucion.md#62-escenario-análisis-de-contenido-post-analysis).

# 16. Historial de análisis

Dos endpoints adicionales permiten consultar análisis pasados, usados por la
pestaña "Historial" del frontend:

```
GET /analysis?limit=20&offset=0
GET /analysis/{id}
```

El primero devuelve una página de resultados (más recientes primero) y el
total disponible, para paginar. El segundo devuelve un análisis puntual, o
`404` si el `id` no existe. Ver
[Sección 6.3 — Vista de ejecución](docs/arc42/06-vista-de-ejecucion.md#63-escenario-consulta-de-historial-get-analysis-get-analysisid).

# 17. Arranque del frontend

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

Con ambos servidores corriendo, la pestaña **Analizar** envía texto a
`POST /analysis` y anima la puntuación resultante; la pestaña **Historial**
consulta `GET /analysis` y permite expandir cada fila para ver sus factores
(`GET /analysis/{id}` se usa igual, para un caso puntual).

# 18. Ejecutar las pruebas del backend

Con el entorno virtual activado, desde la raíz del repositorio (no dentro de `tests/`), ejecutar:

```cmd
python -m pytest -q
```

**Nota:** usa siempre `python -m pytest -q` y no solo `pytest -q`. En algunos entornos de Windows, el comando corto `pytest -q` no agrega automáticamente la carpeta actual a la ruta de búsqueda de Python, lo que produce `ModuleNotFoundError: No module named 'app'`. La forma `python -m pytest -q` evita ese problema.

Las pruebas actuales comprueban:

- que la aplicación puede inicializarse;
- que la ruta `/health` existe y responde correctamente (`tests/test_health.py`);
- que `POST /analysis` normaliza, analiza, puntúa, clasifica y persiste correctamente un contenido de extremo a extremo (`tests/test_analysis.py`);
- que `GET /analysis` pagina correctamente y que `GET /analysis/{id}` devuelve el análisis correcto o `404` si no existe (`tests/test_history.py`).

El resultado esperado es similar a: `5 passed`

El frontend no tiene pruebas automatizadas todavía; se verifica manualmente
siguiendo el paso 17 y comprobando visualmente los tres flujos. Queda como
trabajo pendiente incorporar una prueba de componente (ver sección 20).

# 19. Integración continua

El repositorio incluye: `.github/workflows/tests.yml`

GitHub Actions ejecutará automáticamente las pruebas del backend cuando se realice un `push` o un `pull request`. El frontend no forma parte todavía del pipeline de CI (ver sección 20, pendientes).

El flujo es:

```
Push
↓
GitHub Actions
↓
Instalar dependencias
↓
Ejecutar python -m pytest -q
↓
✓ Tests
```

El resultado puede consultarse desde la pestaña **Actions** del repositorio;
el enlace al run más reciente en verde se cita en la
[tabla de aspectos](docs/aspectos.md).

# 20. Desarrollo actual y próximos pasos

Ya implementado dentro de las fronteras arquitectónicas definidas (ver
[Sección 5 — Vista de bloques](docs/arc42/05-vista-de-bloques.md)):

- análisis de contenido basado en reglas;
- normalización de contenido de texto;
- cálculo de puntuación y clasificación;
- persistencia de resultados (SQLite), con migración de esquema segura;
- historial de análisis paginado y consulta individual;
- interfaz web (React) que consume los tres flujos anteriores;
- corte vertical completo con pruebas automatizadas (backend).

Pendiente para próximos incrementos:

- extracción de contenido a partir de una URL;
- procesamiento NLP (spaCy);
- evaluación de Machine Learning (scikit-learn), condicionada a disponer de un dataset adecuado;
- prueba automatizada de componente para el frontend;
- incorporar el frontend al pipeline de CI (`npm run build` en GitHub Actions);
- medición formal de usabilidad para Q-04, ahora que existe una interfaz sobre la cual ejecutarla.

# 21. Principios arquitectónicos

La implementación sigue los siguientes criterios:

**Modularidad** — Cada módulo tiene responsabilidades claramente delimitadas.

**Bajo acoplamiento** — Se evitan dependencias innecesarias entre módulos. El frontend depende únicamente del contrato HTTP público, nunca de detalles internos del backend.

**Alta cohesión** — Las responsabilidades relacionadas se mantienen juntas.

**Encapsulación de la variación** — Los mecanismos que pueden cambiar, como las reglas de análisis, se mantienen aislados.

**Evolución gradual** — La arquitectura permite incorporar nuevos mecanismos de análisis, o un nuevo cliente como el frontend, sin modificar innecesariamente los demás componentes.

# 22. Estado de la línea base

## Arquitectura

- [x] Comparación de estilos.
- [x] Monolito modular seleccionado.
- [x] ADR-0001.
- [x] arc42 secciones 1–10 y 12.
- [x] Glosario (sección 12, con secciones 7 y 8 agregadas).
- [x] Árbol de utilidad.
- [x] Escenarios de calidad (Q-01 a Q-05), con anchors verificados y evidencia enlazada.
- [x] Matriz comparativa.
- [x] C4 Nivel 1 — Contexto, con leyenda.
- [x] C4 Nivel 2 — Contenedores, con leyenda y estado real (SQLite y frontend implementados).
- [x] C4 Nivel 3 — Componentes.
- [x] Restricciones arquitectónicas.
- [x] Registro de uso de IA.
- [x] Tabla de aspectos con las 8 columnas del curso y trazabilidad completa hasta Pruebas.

## Esqueleto y cortes verticales

- [x] Aplicación FastAPI.
- [x] Estructura modular.
- [x] Endpoint `GET /health`.
- [x] Endpoint `POST /analysis` con validación (Pydantic).
- [x] Endpoints `GET /analysis` y `GET /analysis/{id}` (historial).
- [x] Persistencia SQLite integrada, con migración de esquema segura.
- [x] Pruebas automatizadas del backend (5 casos).
- [x] Interfaz web (React + Vite) conectada a los tres flujos.
- [x] Comando único de arranque por servicio (`python run.py`, `npm run dev`).
- [x] GitHub Actions configurado (backend).

## Pendiente

- [ ] Prueba de modificación de una regla existente para el escenario Q-03.
- [ ] Medición formal de usabilidad (Q-04) usando la interfaz ya disponible.
- [ ] Implementar análisis mediante URL.
- [ ] Integrar procesamiento NLP.
- [ ] Evaluar Machine Learning.
- [ ] Prueba automatizada de componente para el frontend.
- [ ] Incorporar el build del frontend a GitHub Actions.
- [ ] Verificar que los tres integrantes del equipo tengan commits atribuidos correctamente en el historial.

# 23. Repositorio

Repositorio oficial:

https://github.com/ISCOUTB/AS_202620_Verifacts

**Proyecto:** VeriFacts
**Equipo:** Pedro Jose Castro Blanquicett, Cristian David Cardeno Gulloso
