# Notas de implementación — Ampliación de backend

Este documento explica **qué se construyó, por qué se construyó así, y dónde
tocar cada cosa** si en el futuro hay que modificarla. Complementa —no
reemplaza— la trazabilidad formal de `docs/aspectos.md` (filas A-04, A-05,
A-06).

## 1. Qué se agregó

| Funcionalidad | Endpoint / función | Archivo |
|---|---|---|
| Consultar un análisis por id | `GET /analysis/{id}` | `app/api/routes.py` |
| Listar análisis (paginado) | `GET /analysis?limit=&offset=` | `app/api/routes.py` |
| Analizar contenido desde una URL | `POST /analysis` con `{"url": "..."}` | `app/api/routes.py`, `app/modules/content/service.py` |
| CORS para el futuro frontend | middleware en `app/main.py` | `app/main.py` |
| Trazabilidad temporal y de origen | columnas `created_at`, `source_type` | `app/persistence/repository.py` |

**No se agregó** todavía: `MLAnalyzer`, columna `model_version`,
procesamiento NLP, ni el frontend. Quedan fuera de alcance de este
incremento a propósito (ver sección 5).

## 2. Por qué cada decisión se tomó así

### 2.1 `extract_from_url` vive en `Content`, no en `API` ni en un módulo nuevo

La Sección 5 (Vista de bloques) ya decía desde el primer incremento que
`Content` es responsable de "normalizar y validar el contenido recibido
**mediante texto o URL**" — la responsabilidad ya estaba asignada, solo
faltaba implementarla. Ponerla en otro lugar habría contradicho la
documentación existente sin necesidad.

`API` (`routes.py`) sigue sin saber nada de *cómo* se obtiene el contenido:
solo decide *cuál* función de `Content` llamar según venga `text` o `url`.
Esto respeta el concepto transversal de manejo de errores (arc42 §8.2):
`Content` lanza `ValueError`, `API` es el único que traduce eso a HTTP
(`400`).

### 2.2 `text` y `url` son mutuamente excluyentes, validados con Pydantic

Se usó un `model_validator` de Pydantic (no un `if` dentro del endpoint)
para que la validación de "debe venir exactamente uno de los dos" ocurra
**antes** de que el código de negocio se ejecute, igual que ya pasaba con
`AnalysisRequest.text` obligatorio en la versión anterior. Esto mantiene la
convención de arc42 §8.1: entradas inválidas se rechazan con `422` a nivel
de esquema, no con lógica manual repartida por el código.

### 2.3 Las pruebas de URL mockean `trafilatura`, no llaman internet de verdad

`tests/test_url_ingestion.py` usa `monkeypatch` sobre
`content_service.trafilatura.fetch_url` / `.extract` en vez de apuntar a una
URL real. Esto es deliberado: una prueba que depende de una página web real
es lenta, puede fallar por razones ajenas al código (la página cambia, se
cae, hay rate-limiting) y vuelve el pipeline de CI (`.github/workflows/tests.yml`)
no confiable — justo el tipo de problema que ya les costó una evidencia de
CI rota en S4. Si en algún momento quieren una prueba de integración real
contra internet, debe ir **separada** de la suite que corre en cada push
(por ejemplo, marcada con `@pytest.mark.integration` y excluida del target
por defecto de `pytest -q`).

### 2.4 Migración de esquema con `PRAGMA table_info`, no con una versión nueva de tabla

`repository.py` no borra ni recrea la tabla `analyses`: revisa qué columnas
existen y agrega las que falten con `ALTER TABLE ... ADD COLUMN`. Esto
significa que si ya tienen un `data/verifacts.db` local con datos de pruebas
anteriores, **no los van a perder** al correr esta versión — la primera vez
que se llame a `initialize_database()` (por ejemplo, con `python run.py`),
las columnas nuevas aparecen solas con sus valores por defecto
(`source_type='texto'`, `created_at=CURRENT_TIMESTAMP`).

Si de todas formas quieren empezar con una base de datos limpia (recomendado
para la sustentación, para no mostrar datos de prueba viejos), basta con
borrar la carpeta `data/` antes de correr `python run.py` — ya no está
versionada en git (ver `.gitignore` corregido en la entrega anterior).

### 2.5 No se agregó `model_version` todavía

Se decidió **no** agregar esta columna en este incremento, aunque estaba
planeada junto con `created_at` y `source_type`. Razón: hoy no existe ningún
analizador cuya versión valga la pena registrar (`RuleAnalyzer` no tiene
"versiones"). Agregar una columna que siempre va a estar vacía es deuda
técnica sin beneficio inmediato. Se deja documentado en
`docs/arc42/05-vista-de-bloques.md` §5.7 como pendiente explícito para
cuando exista `MLAnalyzer`.

### 2.6 CORS restringido a `localhost:5173` / `127.0.0.1:5173`, no `allow_origins=["*"]`

Son los puertos por defecto de un proyecto Vite en desarrollo. Se documentó
directamente en el comentario de `app/main.py` que esta lista debe
restringirse a la URL real del frontend antes de cualquier despliegue —
para que quien lea el código en el futuro no copie `"*"` a producción sin
pensarlo.

## 3. Cómo se validó antes de entregarlo

1. Se armó el proyecto completo en un entorno aislado (mismo layout que el
   repositorio real).
2. `pip install -r requirements.txt` (incluye `trafilatura`, agregado en
   esta entrega).
3. `python -m pytest -q` → **12 passed** (2 pruebas existentes sin tocar +
   10 nuevas).
4. Servidor real levantado con `python run.py`, y probado con `curl`:
   `POST /analysis` (texto), `GET /analysis/{id}` (existente e inexistente),
   `GET /analysis` (listado), validación `422` sin `text`/`url`, y preflight
   CORS (`OPTIONS` con `Origin: http://localhost:5173` → `200`).
5. Se limpiaron los archivos temporales del entorno de prueba (`data/`,
   `__pycache__/`) antes de armar la entrega — no forman parte del código.

## 4. Dónde tocar cada cosa si necesitas cambiar algo

| Quiero cambiar... | Toca este archivo | Cuidado con... |
|---|---|---|
| Qué campos acepta o devuelve la API | `app/api/routes.py` (`AnalysisRequest`, `AnalysisResponse`, `AnalysisSummary`) | Si agregas un campo a la respuesta, actualiza también `docs/aspectos.md` y el ejemplo de `README.md` sección 15 |
| Cómo se extrae contenido de una URL | `app/modules/content/service.py` (`extract_from_url`) | Los tests de `test_url_ingestion.py` mockean `content_service.trafilatura` — si cambias la librería, actualiza también los mocks |
| Reglas de análisis (agregar/modificar una) | `app/modules/analysis/analyzer.py` | Esto es exactamente el escenario Q-03 (A-02 en `aspectos.md`), que sigue pendiente de prueba — buen momento para cerrarlo |
| Columnas de la base de datos | `app/persistence/repository.py` (`initialize_database`, `_migrate_schema`) | Sigue el mismo patrón de `PRAGMA table_info` + `ALTER TABLE`, no reescribas `CREATE TABLE` a mano sin migración |
| Orígenes permitidos por CORS | `app/main.py` (`allow_origins`) | Antes de desplegar, quita `localhost`/`127.0.0.1` y pon la URL real del frontend |
| Paginación del listado | `app/api/routes.py` (`list_analysis`) y `app/persistence/repository.py` (`list_analyses`) | El límite de `limit` (1–100) está validado en `routes.py`, no en `repository.py` — si mueves la validación, no la dupliques en los dos lugares |

## 5. Explícitamente fuera de alcance de este incremento

- `MLAnalyzer` (TF-IDF + Regresión Logística) — sigue siendo el siguiente
  paso natural para `Analysis`, no para `API`.
- Procesamiento NLP (`spaCy`).
- Frontend (React + Vite) — el contrato que va a consumir ya está fijado
  por `AnalysisResponse`/`AnalysisSummary` en `routes.py`.
- Columna `model_version` (ver 2.5).
