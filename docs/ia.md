# Registro de uso de IA — VeriFacts

## Propósito

Este documento registra el uso de herramientas de Inteligencia Artificial
durante el desarrollo del proyecto, y las decisiones de aceptación o rechazo
relacionadas con su uso, tanto como herramienta de apoyo documental como
componente potencial del propio producto VeriFacts.

## Bitácora de uso de IA (por interacción)

| Fecha | Herramienta | Propósito | Resumen del Prompt (Entrada) | Resultado obtenido | Validación |
|---|---|---|---|---|---|
| Semana 1–2 (ago 2026) | Claude (Anthropic) | Redactar los 5 escenarios de calidad y reorganizar la estructura mínima del curso | "Completar Q-01 a Q-05 con las 6 partes cada uno; crear docs/arc42/, docs/c4/, docs/ia.md" | `escenarios-de-calidad.md`, `arbol-utilidad.md`, `aspectos.md` (versión inicial), `ia.md`, reorganización de carpetas | Aceptado — revisado por el equipo e incorporado al repo tras confirmar estructura |
| Semana 3 (ago 2026) | Claude (Anthropic) | Ligar tácticas concretas de arc42 §4 a cada escenario y enlazar ADR desde aspectos.md | "Reescribir 4-estrategia-de-solucion.md con una táctica nombrada por escenario; enlazar aspectos.md con el ADR" | `04-estrategia-de-solucion.md` reescrito; enlaces cruzados aspectos↔ADR | Aceptado — se verificaron los anchors manualmente |
| Semana 4 · S4 (~24–31 ago 2026) | Claude (Anthropic) | Rehacer la tabla de aspectos a 8 columnas; diagnosticar `pytest` exit code 2 en CI; limpiar `__pycache__`/duplicados | "aspectos.md no usa las 8 columnas del curso; el CI falla con exit code 2; hay archivos `(1).py`" | `aspectos.md` con 8 columnas exactas; `.github/workflows/tests.yml` corregido a `python -m pytest -q`; `.gitignore` + `git rm --cached` | Parcial — corregido en código, pero pendiente confirmar run verde en Actions (evidencia real no verificada aún) |
| Corte vertical backend (ago–sep 2026) | Claude (Anthropic) | Implementar `POST /analysis` con persistencia SQLite de extremo a extremo | "Implementar el corte vertical completo: Content → Analysis → Scoring → Persistencia, con prueba end-to-end" | `routes.py`, `repository.py`, `analyzer.py`, `service.py`, `test_analysis.py` | Aceptado — validado con `pytest` en sandbox antes de entregar (2 passed) |
| Extensión backend (sep 2026) | Claude (Anthropic) | Agregar extracción por URL, endpoints `GET /analysis/{id}` y `GET /analysis` paginado, migración segura de esquema | "Agregar `source_type`/`created_at` sin perder datos existentes; texto o URL mutuamente excluyentes" | Migración con `PRAGMA table_info` + `ALTER TABLE`; `trafilatura` en el módulo Content | Aceptado — validado en sandbox antes de entrega |
| Pipeline ML (sep 2026) | Claude (Anthropic) | Añadir `MLAnalyzer` como complemento de `RuleAnalyzer`, sin reemplazarlo | "TF-IDF + Logistic Regression sobre el Spanish Fake News Corpus, degradación controlada si falta el modelo, toggle por variable de entorno" | `MLAnalyzer`, script de entrenamiento (modelo no versionado), registro en `ia.md` del rechazo de LLM como clasificador | Aceptado — documentado el motivo técnico del rechazo de LLM en `ia.md` |
| S6 (~sep 2026) | Claude (Anthropic) | Modelo de dominio y contextos delimitados exigidos en retroalimentación | "Agregar lenguaje ubicuo y contextos delimitados a 08-conceptos-transversales.md" | `mapa-contextos.md`, `propiedad-datos.md`, actualización de `08-conceptos-transversales.md` | Aceptado — integrado en la documentación arc42 |
| 8 sep 2026 | Claude (Anthropic) | Verificar si el repositorio cumple con la ficha de evaluación más reciente | "¿Lo que tengo actualmente cumple o no según esta última revisión?" | Verificación en vivo: repo devuelve 404 en GitHub, confirmando el hallazgo del corrector | Confirmado — acción urgente pendiente del equipo, no de la IA |
