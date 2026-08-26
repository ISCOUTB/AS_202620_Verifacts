# arc42 — Sección 5: Vista de bloques de construcción

## 5.1 Nivel 1 — Sistema completo

VeriFacts es un **monolito modular** (ver [ADR-0001](../adr/0001-estilo-arquitectonico.md)).
Se ejecuta como una única unidad desplegable, dividida internamente en cuatro
bloques con responsabilidades delimitadas.

```text
┌─────────────────────────── VeriFacts ───────────────────────────┐
│                                                                   │
│   ┌────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐  │
│   │  API   │────▶│ Content  │────▶│ Analysis │────▶│ Scoring  │  │
│   └────────┘     └──────────┘     └──────────┘     └──────────┘  │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
```

Esta vista corresponde al Nivel 2 (Contenedores/Componentes internos) del
modelo C4 — ver [C4 — Contenedores](../c4/02-contenedores.md).

---

## 5.2 Bloque: API

**Responsabilidad:** recibir y coordinar las solicitudes HTTP externas;
traducir peticiones en llamadas a los módulos internos y las respuestas de
estos en respuestas HTTP.

**Estado en este incremento:** implementado como esqueleto ejecutable.

**Ubicación en el código:** `app/api/`

**Contenido actual:**

| Elemento | Descripción |
|---|---|
| `app/main.py` | Punto de entrada de la aplicación FastAPI; registra el router |
| `app/api/routes.py` | Define las rutas; actualmente expone `GET /health` |

**Interfaz expuesta (actual):**

| Ruta | Método | Descripción |
|---|---|---|
| `/health` | GET | Confirma que el servicio está disponible |

**Interfaz prevista (pendiente):** `POST /analysis` — recibe texto o URL y
delega en `Content`.

---

## 5.3 Bloque: Content

**Responsabilidad:** representar y procesar el contenido recibido, ya sea
como texto directo o como una URL de la cual extraer el contenido.

**Estado en este incremento:** definido arquitectónicamente
(`app/modules/content/`), sin lógica implementada todavía.

**Colabora con:** `API` (recibe la solicitud) y `Analysis` (entrega el
contenido normalizado).

---

## 5.4 Bloque: Analysis

**Responsabilidad:** aplicar los mecanismos de detección de indicadores de
desinformación sobre el contenido normalizado.

**Estado en este incremento:** definido arquitectónicamente
(`app/modules/analysis/`), sin analizadores implementados todavía.

**Diseño previsto:** los analizadores compartirán un contrato común
(`Analyzer`) para permitir incorporar nuevos mecanismos sin modificar los
demás bloques — ver [Sección 4](04-estrategia-de-solucion.md#44-q-02--escalabilidad)
y el escenario [Q-02](../escenarios-de-calidad.md#q-02--incorporación-de-un-nuevo-analizador).

**Analizadores previstos:**

- `RuleAnalyzer` — reglas (sensacionalismo, mayúsculas, afirmaciones
  absolutas, ausencia de fuentes, lenguaje emocional).
- `NLPAnalyzer` — características lingüísticas mediante spaCy.
- `MLAnalyzer` — clasificación mediante scikit-learn (evaluación pendiente,
  ver [Registro de uso de IA](../ia.md)).

**Colabora con:** `Content` (recibe entrada) y `Scoring` (entrega hallazgos).

---

## 5.5 Bloque: Scoring

**Responsabilidad:** transformar los hallazgos del análisis en una
puntuación de riesgo, una clasificación y una explicación de los factores
detectados.

**Estado en este incremento:** definido arquitectónicamente
(`app/modules/scoring/`), sin lógica implementada todavía.

**Colabora con:** `Analysis` (recibe hallazgos) y `API` (entrega el
resultado final).

---

## 5.6 Trazabilidad con el código

| Bloque arquitectónico | Carpeta en el repositorio |
|---|---|
| API | `app/api/` |
| Content | `app/modules/content/` |
| Analysis | `app/modules/analysis/` |
| Scoring | `app/modules/scoring/` |

## 5.7 Pendiente para próximos incrementos

- Definir el contrato (interfaz) formal entre `API` y `Content`.
- Definir el contrato `Analyzer` dentro de `Analysis`.
- Definir el modelo de resultado que `Scoring` entrega a `API`.
- Incorporar persistencia (SQLite) como bloque adicional o sub-bloque de
  `Content`/`Scoring`.
