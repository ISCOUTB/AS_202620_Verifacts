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

**Responsabilidad:** normalizar y validar el contenido recibido antes de
entregarlo al módulo `Analysis`.

**Estado en este incremento:** implementado.

**Ubicación:** `app/modules/content/service.py`

La función `normalize_content()` elimina espacios redundantes y rechaza
contenidos vacíos.

---

## 5.4 Bloque: Analysis

**Responsabilidad:** detectar indicadores asociados a posibles señales de
desinformación mediante analizadores basados en reglas.

**Estado en este incremento:** implementado.

**Ubicación:**

- `app/modules/analysis/analyzer.py`
- `app/modules/analysis/service.py`

El primer analizador implementado es `RuleAnalyzer`, que detecta:

- lenguaje sensacionalista;
- uso excesivo de mayúsculas;
- afirmaciones absolutas.
**Analizadores previstos:**

- `RuleAnalyzer` — reglas (sensacionalismo, mayúsculas, afirmaciones
  absolutas, ausencia de fuentes, lenguaje emocional).
- `NLPAnalyzer` — características lingüísticas mediante spaCy.
- `MLAnalyzer` — clasificación mediante scikit-learn (evaluación pendiente,
  ver [Registro de uso de IA](../ia.md)).

**Colabora con:** `Content` (recibe entrada) y `Scoring` (entrega hallazgos).

---

## 5.5 Bloque: Scoring

**Responsabilidad:** transformar los hallazgos producidos por `Analysis` en
una puntuación de riesgo y una clasificación.

**Estado en este incremento:** implementado.

**Ubicación:** `app/modules/scoring/service.py`

La puntuación se limita a un máximo de 100 puntos y se clasifica como:

- Riesgo bajo: menos de 30.
- Riesgo medio: entre 30 y 59.
- Riesgo alto: 60 o más.

---

## 5.6 Bloque: Persistencia

**Responsabilidad:** almacenar los resultados de los análisis para permitir
su recuperación posterior.

**Estado en este incremento:** implementado.

**Ubicación:** `app/persistence/repository.py`

**Tecnología:** SQLite.

La persistencia almacena:

- identificador;
- contenido normalizado;
- puntuación;
- clasificación;
- factores detectados.

## 5.7 Pendiente para próximos incrementos

- Definir el contrato (interfaz) formal entre `API` y `Content`.
- Definir el contrato `Analyzer` dentro de `Analysis`.
- Definir el modelo de resultado que `Scoring` entrega a `API`.
- Incorporar persistencia (SQLite) como bloque adicional o sub-bloque de
  `Content`/`Scoring`.
