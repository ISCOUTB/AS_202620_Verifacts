# C4 — Nivel 2: Contenedores de VeriFacts

## Descripción

El diagrama de contenedores muestra las unidades desplegables/ejecutables
que componen VeriFacts y cómo se comunican. En este incremento existen
**tres** contenedores en ejecución: la aplicación FastAPI (monolito
modular), la base de datos SQLite, y la interfaz web (React + Vite).

## Leyenda

| Notación | Significado |
|---|---|
| Rectángulo con "[Contenedor: ...]" | Unidad desplegable/ejecutable |
| Flecha continua (`-->`) | Comunicación o dependencia **implementada** |
| Flecha punteada (`-.->`) | Comunicación o dependencia **prevista, no implementada** |
| Texto "(previsto, no implementado)" dentro de un nodo | El contenedor existe en el diseño pero aún no tiene código ejecutable |

## Diagrama

```mermaid
flowchart TB
    U[Usuario<br/>persona]

    subgraph VF[VeriFacts]
        FE["Interfaz web<br/>[Contenedor: React / TypeScript / Vite]<br/>Implementado — puerto 5173"]
        API["Aplicación VeriFacts<br/>[Contenedor: Python / FastAPI]<br/>Monolito modular: API, Content,<br/>Analysis, Scoring — puerto 8000"]
        DB[("Base de datos<br/>[Contenedor: SQLite]<br/>Implementado")]
    end

    W[Sitio web externo]

    U -->|HTTP| FE
    FE -->|HTTP/JSON vía fetch,<br/>habilitado con CORS| API
    U -->|HTTP directo,<br/>docs interactivos| API
    API -->|Lee/escribe, implementado| DB
    API -.->|Solicita contenido, previsto| W
```

## Contenedores

| Contenedor | Tecnología | Estado | Descripción |
|---|---|---|---|
| Interfaz web | React 18 + TypeScript + Vite | **Implementado** | Formulario de análisis, panel de resultado y consulta del historial paginado. No contiene lógica de negocio: solo llama a la API pública (`frontend/src/api/client.ts`) |
| Aplicación VeriFacts | Python 3.11 + FastAPI + Uvicorn | **Implementado** | Expone la API HTTP; internamente organizada en los módulos `API`, `Content`, `Analysis`, `Scoring` (ver [Sección 5 — Vista de bloques](../arc42/05-vista-de-bloques.md)); habilita CORS para el origen de la interfaz web (`app/main.py`) |
| Base de datos | SQLite | **Implementado** | Persistencia del historial de análisis (`app/persistence/repository.py`): id, contenido normalizado, score, clasificación, factores, fecha de creación |

## Nota sobre el estado actual

Hoy existen tres puntos de entrada verificables sobre la API HTTP: el
esqueleto de disponibilidad (`GET /health`), el corte vertical completo de
análisis (`POST /analysis`, con persistencia real en SQLite), y el
historial paginado (`GET /analysis`, `GET /analysis/{id}`), tal como se
documenta en el
[corte vertical ejecutable del README](../../README.md#corte-vertical-ejecutable)
y en la [Sección 6 — Vista de ejecución](../arc42/06-vista-de-ejecucion.md).
La interfaz web consume los tres desde el navegador; el único elemento del
diagrama que sigue siendo previsto, sin código, es la extracción de
contenido desde un sitio web externo cuando el usuario envía una URL.

Ver también el diagrama de Nivel 1: [C4 — Contexto](01-contexto.md) y el de
Nivel 3: [C4 — Componentes](03-componentes.md).
