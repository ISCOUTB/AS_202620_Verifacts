# arc42 — Sección 3: Contexto y alcance

## 3.1 Contexto de negocio

VeriFacts se encuentra dentro del contexto de consumo y evaluación de
información digital.

El usuario proporciona un contenido que desea analizar y recibe indicadores
que pueden ayudarle a determinar si necesita realizar una revisión adicional.

---

## 3.2 Actores

| Actor | Interacción |
|---|---|
| Usuario final | Introduce texto o URL y consulta el resultado |
| Estudiante | Utiliza el sistema como apoyo para evaluar contenidos |
| Docente | Utiliza el sistema como recurso educativo |
| Analista | Utiliza el resultado como señal para priorizar revisión |

---

## 3.3 Sistemas externos

| Sistema | Interacción |
|---|---|
| Sitio web externo | Proporciona contenido cuando se analiza una URL |
| GitHub | Gestiona código fuente y colaboración |
| GitHub Actions | Ejecuta las pruebas automatizadas en cada push |
| SonarCloud | Analiza la calidad del código |

---

## 3.4 Límites del sistema

### Dentro de VeriFacts

- Interfaz web.
- API.
- Recepción de contenido.
- Extracción.
- Análisis.
- Puntuación.
- Persistencia.
- Historial.

### Fuera de VeriFacts

- Sitios web externos.
- GitHub / GitHub Actions.
- SonarCloud.
- Verificación humana de hechos.

---

## 3.5 Contexto técnico

El usuario interactúa con VeriFacts mediante la interfaz web, que a su vez
llama a la API HTTP.

El contenido puede introducirse directamente o mediante una URL. El sistema
procesa el contenido y genera el resultado.

```text
Usuario
   |
   | Introduce texto o URL
   v
Interfaz web (React)
   |
   | HTTP/JSON
   v
API (VeriFacts)
   |
   | Solicita contenido (si es una URL)
   v
Sitio web externo
```

El diagrama equivalente en notación C4 (Nivel 1 — Contexto) se encuentra en
[C4 — Contexto](../c4/01-contexto.md), y el de contenedores (interfaz web,
API y base de datos) en [C4 — Contenedores](../c4/02-contenedores.md).

---

## 3.6 Alcance de este incremento

Este incremento documenta y ejecuta **tres** recorridos de extremo a
extremo sobre el backend, más una interfaz web que los consume a todos.
Todos están descritos con detalle en la
[Sección 6 — Vista de ejecución](06-vista-de-ejecucion.md) y guiados paso a
paso en el [README](../../README.md#corte-vertical-ejecutable):

1. **Comprobación de disponibilidad** (`GET /health`): atraviesa únicamente
   el módulo `API`.
2. **Análisis de contenido** (`POST /analysis`): atraviesa `API → Content →
   Analysis → Scoring → Persistencia`. El texto recibido se normaliza en
   `Content`, se evalúa con `RuleAnalyzer` en `Analysis`, se transforma en
   puntuación y clasificación en `Scoring`, y el resultado se guarda y puede
   recuperarse desde `Persistencia` (SQLite).
3. **Historial de análisis** (`GET /analysis`, `GET /analysis/{id}`):
   atraviesa `API → Persistencia`, paginado por fecha de creación
   descendente.

La **interfaz web** (React + TypeScript + Vite, `frontend/`) es un cliente
HTTP de estos tres flujos — ver
[Sección 6.4](06-vista-de-ejecucion.md#64-la-interfaz-web-como-cliente-de-los-tres-escenarios).
No contiene lógica de negocio propia ni accede directamente a la base de
datos.

Lo que **no** está implementado todavía dentro de este alcance:

- Extracción de contenido a partir de una URL (`Content` solo normaliza
  texto recibido directamente).
- Analizadores basados en NLP o Machine Learning (`Analysis` solo tiene
  `RuleAnalyzer`; ver [Registro de uso de IA](../ia.md)).
- Filtro o búsqueda dentro del historial (solo pagina por fecha).
