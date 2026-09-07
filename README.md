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

La arquitectura seleccionada es un monolito modular.

El repositorio contiene un corte vertical completo y ejecutable: recepción de una solicitud HTTP, normalización de contenido, análisis basado en reglas, cálculo de puntuación/clasificación y persistencia del resultado.

Actualmente se puede:

- iniciar la aplicación;
- comprobar que la API está disponible (`GET /health`);
- enviar un texto para análisis y recibir puntuación, clasificación y factores (`POST /analysis`), con el resultado persistido en SQLite;
- ejecutar las pruebas automatizadas (local y en GitHub Actions).

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
[Decisiones arquitectónicas explicadas](docs/decisiones-arquitectonicas-explicadas.md)

## Módulos

```text
VeriFacts
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

Detalle completo de responsabilidades y trazabilidad con el código en la [Sección 5 — Vista de bloques](docs/arc42/05-vista-de-bloques.md). La correspondencia de estos 5 bloques con los 3 contextos delimitados del dominio (Ingesta y Presentación, Análisis de Contenido, Historial de Análisis) está en [C4 — Nivel 3: Componentes](docs/c4/03-componentes.md).

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

## Modelo de dominio (S6)

- [Mapa de contextos delimitados](docs/mapa-contextos.md)
- [Propiedad de datos por módulo](docs/propiedad-datos.md)
- [Violaciones de modularidad detectadas](docs/violaciones-modularidad.md)

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
│   └── test_analysis.py
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
    │   └── 11-glosario.md
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
    ├── decisiones-arquitectonicas-explicadas.md
    ├── mapa-contextos.md
    ├── propiedad-datos.md
    ├── violaciones-modularidad.md
    └── ia.md
```

No debe haber en el repositorio: carpetas `__pycache__/`, archivos `*.pyc`,
archivos duplicados con sufijos tipo `(1).py`, PDFs sueltos en la raíz, ni la
carpeta `data/` (contiene `verifacts.db`, generada en tiempo de ejecución por
`initialize_database()` y excluida por `.gitignore`).
Verificar con `git ls-files` antes de cada entrega.

# 8. Tecnologías actuales

## Backend

- Python 3.11+
- FastAPI
- Uvicorn
- SQLite (vía `sqlite3`, módulo estándar)

## Pruebas

- Pytest
- HTTPX (usado internamente por `TestClient`)

## Calidad y colaboración

- Git
- GitHub
- GitHub Actions
- SonarCloud

## Tecnologías previstas para etapas posteriores

- React
- TypeScript
- SQLAlchemy (si se migra de `sqlite3` puro a un ORM)
- spaCy
- scikit-learn

Estas últimas se incorporarán progresivamente conforme avance el proyecto.

# 9. Requisitos para ejecutar el proyecto

Se necesita:

- Python 3.11 o superior.
- Git.
- Acceso al repositorio.

# 10. Clonar el repositorio

Desde una terminal:

```cmd
git clone https://github.com/ISCOUTB/AS_202620_Verifacts.git
cd AS_202620_Verifacts
```

# 11. Crear el entorno virtual

## Windows

```cmd
python -m venv .venv
.venv\Scripts\activate
```

# 12. Instalar dependencias

Con el entorno virtual activado:

```cmd
pip install -r requirements.txt
```

# Corte vertical ejecutable

Las secciones 13 a 17 documentan, paso a paso, los recorridos de extremo a extremo que hoy son ejecutables en VeriFacts: arrancar el servicio, confirmar que responde, enviar un contenido para análisis con persistencia real, y verificar todo con pruebas automatizadas (local y en CI). Ver también su descripción arquitectónica en [Sección 6 — Vista de ejecución](docs/arc42/06-vista-de-ejecucion.md) y su trazabilidad hasta la evidencia de prueba en las filas **A-00** a **A-03** de la [tabla de aspectos](docs/aspectos.md).

# 13. Arranque del proyecto

El proyecto se inicia con un único comando:

```cmd
python run.py
```

Esta es la instrucción oficial de arranque. Al iniciar, también se
inicializa automáticamente la base de datos SQLite (`data/verifacts.db`) si
no existe.

Una vez iniciado, la aplicación estará disponible en:
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

Ejemplo de solicitud (desde `http://127.0.0.1:8000/docs`, o con `curl`):

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
  ]
}
```

Internamente, la solicitud atraviesa `Content` (normalización) →
`Analysis` (`RuleAnalyzer`) → `Scoring` (puntuación y clasificación) →
`Persistencia` (guardado en SQLite). El detalle paso a paso está en la
[Sección 6.2 — Vista de ejecución](docs/arc42/06-vista-de-ejecucion.md#62-escenario-análisis-de-contenido-post-analysis).

# 16. Ejecutar las pruebas

Con el entorno virtual activado, desde la raíz del repositorio (no dentro de `tests/`), ejecutar:

```cmd
python -m pytest -q
```

**Nota:** usa siempre `python -m pytest -q` y no solo `pytest -q`. En algunos entornos de Windows, el comando corto `pytest -q` no agrega automáticamente la carpeta actual a la ruta de búsqueda de Python, lo que produce `ModuleNotFoundError: No module named 'app'`. La forma `python -m pytest -q` evita ese problema.

Las pruebas actuales comprueban:

- que la aplicación puede inicializarse;
- que la ruta `/health` existe y responde correctamente (`tests/test_health.py`);
- que `POST /analysis` normaliza, analiza, puntúa, clasifica y persiste correctamente un contenido de extremo a extremo (`tests/test_analysis.py`).

El resultado esperado es similar a: `2 passed`

# 17. Integración continua

El repositorio incluye: `.github/workflows/tests.yml`

GitHub Actions ejecutará automáticamente las pruebas cuando se realice un `push` o un `pull request`.

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

# 18. Desarrollo actual y próximos pasos

Ya implementado dentro de las fronteras arquitectónicas definidas (ver
[Sección 5 — Vista de bloques](docs/arc42/05-vista-de-bloques.md)):

- análisis de contenido basado en reglas;
- normalización de contenido de texto;
- cálculo de puntuación y clasificación;
- persistencia de resultados (SQLite);
- corte vertical completo con prueba automatizada;
- modelo de dominio documentado: lenguaje ubicuo, contextos delimitados y propiedad de datos por módulo (ver [Modelo de dominio (S6)](#modelo-de-dominio-s6)).

Pendiente para próximos incrementos:

- extracción de contenido a partir de una URL;
- endpoints de lectura del historial (`GET /analysis/{id}`, `GET /analysis`);
- procesamiento NLP (spaCy);
- evaluación de Machine Learning (scikit-learn), condicionada a disponer de un dataset adecuado;
- interfaz final (React).

# 19. Principios arquitectónicos

La implementación sigue los siguientes criterios:

**Modularidad** — Cada módulo tiene responsabilidades claramente delimitadas.

**Bajo acoplamiento** — Se evitan dependencias innecesarias entre módulos.

**Alta cohesión** — Las responsabilidades relacionadas se mantienen juntas.

**Encapsulación de la variación** — Los mecanismos que pueden cambiar, como las reglas de análisis, se mantienen aislados.

**Evolución gradual** — La arquitectura permite incorporar nuevos mecanismos de análisis sin modificar innecesariamente los demás componentes.

# 20. Estado de la línea base

## Arquitectura

- [x] Comparación de estilos.
- [x] Monolito modular seleccionado.
- [x] ADR-0001.
- [x] arc42 secciones 1–11.
- [x] Glosario (sección 11), sin entradas duplicadas ni en conflicto.
- [x] Árbol de utilidad, priorizado por impacto y riesgo.
- [x] Escenarios de calidad (Q-01 a Q-05), con anchors verificados y evidencia enlazada.
- [x] Matriz comparativa.
- [x] C4 Nivel 1 — Contexto, con leyenda.
- [x] C4 Nivel 2 — Contenedores, con leyenda y estado real (SQLite implementado).
- [x] C4 Nivel 3 — Componentes, con tabla de correspondencia contra el código real.
- [x] Modelo de dominio: lenguaje ubicuo, contextos delimitados y mapa de contextos (S6).
- [x] Propiedad de datos por módulo, verificada contra `app/persistence/repository.py` (sin violaciones detectadas).
- [x] Restricciones arquitectónicas.
- [x] Registro de uso de IA.
- [x] Tabla de aspectos con las 8 columnas del curso y trazabilidad completa hasta Pruebas.

## Esqueleto y corte vertical

- [x] Aplicación FastAPI.
- [x] Estructura modular.
- [x] Endpoint `GET /health`.
- [x] Endpoint `POST /analysis` con validación (Pydantic).
- [x] Persistencia SQLite integrada.
- [x] Pruebas automatizadas del corte vertical completo.
- [x] Comando único de arranque.
- [x] GitHub Actions configurado.

## Pendiente

- [ ] Medición formal de P95 para el escenario Q-01.
- [ ] Prueba de modificación de una regla existente para el escenario Q-03.
- [ ] Implementar análisis mediante URL.
- [ ] Implementar endpoints de lectura del historial (`GET /analysis/{id}`, `GET /analysis`).
- [ ] Integrar procesamiento NLP.
- [ ] Evaluar Machine Learning.
- [ ] Desarrollar frontend.
- [ ] Integrar el prototipo completo.
- [ ] Verificar que los tres integrantes del equipo tengan commits atribuidos correctamente en el historial.
- [ ] Confirmar manualmente que el run de CI citado en `docs/aspectos.md` está en verde.
- [ ] Crear `docs/decisiones-arquitectonicas-explicadas.md` (referenciado desde este README pero aún no existe en el repositorio).
- [ ] Redactar ADR-0002 con la restricción arquitectónica específica asignada para el Corte 1.

# 21. Repositorio

Repositorio oficial:

https://github.com/ISCOUTB/AS_202620_Verifacts

**Proyecto:** VeriFacts
**Equipo:** Pedro Jose Castro Blanquicett, Cristian David Cardeno Gulloso
