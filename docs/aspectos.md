# Aspectos arquitectónicos — VeriFacts

## Aspecto principal

El aspecto arquitectónico principal seleccionado es:

**Escalabilidad mediante modularidad.**

La arquitectura debe permitir incorporar nuevos mecanismos de análisis sin
modificar significativamente los demás componentes.

## Matriz de trazabilidad

Columnas del curso: **ID · Aspecto/Preocupación · Escenario · Vista C4 ·
ADR · Ubicación en código · Medida/Criterio · Evidencia de pruebas**.

| ID | Aspecto / Preocupación | Escenario | Vista C4 | ADR | Ubicación en código | Medida / Criterio | Evidencia de pruebas |
|---|---|---|---|---|---|---|---|
| A-00 | Disponibilidad del esqueleto | [Q-05](escenarios-de-calidad.md#q-05--repetibilidad-del-resultado) | Contenedor "Aplicación VeriFacts" — [C4 Nivel 2](c4/02-contenedores.md) | [ADR-0001](adr/0001-estilo-arquitectonico.md) | `app/api/routes.py` (`GET /health`) | Responde `200 {"status":"ok"}` de forma repetible ante la misma entrada | `tests/test_health.py` — **1 passed** · CI: **[https://github.com/ISCOUTB/AS_202620_Verifacts/actions/runs/33476637583/job/99757163051]** (verificar manualmente que sigue en verde) |
| A-01 | Escalabilidad — incorporar un nuevo analizador | [Q-02](escenarios-de-calidad.md#q-02--incorporación-de-un-nuevo-analizador) | Contenedor "Aplicación VeriFacts", componente `Analysis` — [C4 Nivel 2](c4/02-contenedores.md) | [ADR-0001](adr/0001-estilo-arquitectonico.md) | `app/modules/analysis/analyzer.py` (`RuleAnalyzer`), `app/modules/analysis/service.py` | El nuevo analizador (`RuleAnalyzer`, 3 reglas) se incorporó sin modificar `API`, `Content` ni `Scoring` | `tests/test_analysis.py` — **1 passed**, valida el flujo completo usando `RuleAnalyzer` sin tocar los demás módulos |
| A-02 | Mantenibilidad — modificar una regla existente | [Q-03](escenarios-de-calidad.md#q-03--modificación-de-una-regla) | Contenedor "Aplicación VeriFacts", componente `Analysis` — [C4 Nivel 2](c4/02-contenedores.md) | [ADR-0001](adr/0001-estilo-arquitectonico.md) | `app/modules/analysis/analyzer.py` (métodos de `RuleAnalyzer`) | Modificar una regla no debe producir regresiones en las pruebas existentes | **Pendiente** — falta una prueba que module una regla existente (por ejemplo, cambiar el umbral de mayúsculas) y confirme que `test_health.py` y `test_analysis.py` siguen en verde |
| A-03 | Confiabilidad — corte vertical completo con persistencia | [Q-05](escenarios-de-calidad.md#q-05--repetibilidad-del-resultado) | Contenedores "Aplicación VeriFacts" y "Base de datos" — [C4 Nivel 2](c4/02-contenedores.md) | [ADR-0001](adr/0001-estilo-arquitectonico.md) | `app/api/routes.py` (`POST /analysis`), `app/persistence/repository.py` | La misma entrada produce el mismo `score`, `classification` y `factors`, y queda persistida y recuperable por `id` | `tests/test_analysis.py` — **1 passed**, verifica respuesta HTTP y el registro guardado vía `get_analysis()` |
| A-04 | Usabilidad / Confiabilidad — consulta de un análisis por ID | [Q-04](escenarios-de-calidad.md#q-04--comprensión-del-resultado), [Q-05](escenarios-de-calidad.md#q-05--repetibilidad-del-resultado) | Contenedores "Aplicación VeriFacts" y "Base de datos", contexto "Historial de Análisis" — [C4 Nivel 3](c4/03-componentes.md) | [ADR-0001](adr/0001-estilo-arquitectonico.md) | `app/api/routes.py` (`GET /analysis/{analysis_id}`), `app/persistence/repository.py` (`get_analysis`) | Un `id` existente devuelve `200` con el análisis completo (incluyendo `created_at`, `source_type`); un `id` inexistente devuelve `404` | `tests/test_analysis_history.py` — **2 passed** (`test_get_analysis_by_id_returns_created_analysis`, `test_get_analysis_by_id_not_found_returns_404`) |
| A-05 | Escalabilidad — listado paginado del historial | [Q-04](escenarios-de-calidad.md#q-04--comprensión-del-resultado) | Contenedores "Aplicación VeriFacts" y "Base de datos", contexto "Historial de Análisis" — [C4 Nivel 3](c4/03-componentes.md) | [ADR-0001](adr/0001-estilo-arquitectonico.md) | `app/api/routes.py` (`GET /analysis`), `app/persistence/repository.py` (`list_analyses`) | Devuelve los análisis más recientes primero; `limit` fuera de `[1,100]` u `offset` negativo devuelven `400` | `tests/test_analysis_history.py` — **3 passed** (`test_list_analysis_includes_created_entries`, `test_list_analysis_rejects_invalid_limit`, `test_list_analysis_rejects_negative_offset`) |
| A-06 | Escalabilidad — ingestión de contenido por URL | [Q-02](escenarios-de-calidad.md#q-02--incorporación-de-un-nuevo-analizador) | Contenedor "Aplicación VeriFacts", contexto "Ingesta y Presentación" — [C4 Nivel 3](c4/03-componentes.md) | [ADR-0001](adr/0001-estilo-arquitectonico.md) | `app/modules/content/service.py` (`extract_from_url`, con `trafilatura`), `app/api/routes.py` (`AnalysisRequest` acepta `text` **o** `url`) | Una URL válida se descarga, se extrae y se analiza igual que un texto (`source_type="url"`); una URL que falla al descargar o sin contenido extraíble devuelve `400`; enviar ambos o ninguno de `text`/`url` devuelve `422` | `tests/test_url_ingestion.py` — **5 passed**, con `trafilatura.fetch_url`/`extract` mockeados vía `monkeypatch` (sin depender de red real, para no volver flaky el CI) |

Solo la fila **A-02** permanece "Pendiente" en evidencia de pruebas; el resto
tiene código y prueba real citables. La columna CI de A-00 requiere
confirmar manualmente que el run enlazado sigue en verde (no se pudo
verificar por búsqueda externa; ver `correcciones.md`).

## Decisión relacionada

La decisión arquitectónica que sustenta A-00 a A-06 está registrada en:

[ADR-0001 — Usar monolito modular](adr/0001-estilo-arquitectonico.md)
(indexado también en [Sección 9](arc42/09-decisiones-arquitectonicas.md)).

## Relación

El escenario Q-02 es el escenario principal que motiva la selección del
monolito modular: A-01 (nuevo analizador) y A-06 (ingestión por URL) son dos
evidencias distintas del mismo escenario, ambas incorporadas sin modificar
`Scoring` ni `Persistencia`. El escenario Q-03 complementa la decisión
exigiendo cambios localizados en las reglas de análisis, y es el único
aspecto que sigue pendiente de prueba (A-02). El escenario Q-04
(comprensión del resultado) empieza a tener evidencia de backend con A-04 y
A-05 (consultar y listar análisis), aunque su verificación completa sigue
dependiendo de la interfaz web. El escenario Q-05 tiene ahora tres
evidencias: disponibilidad del esqueleto (A-00), repetibilidad del corte
vertical completo con persistencia (A-03), y repetibilidad de la consulta
por `id` (A-04).

Las tácticas concretas que responden a estos escenarios están documentadas
en [arc42 sección 4](arc42/04-estrategia-de-solucion.md).
