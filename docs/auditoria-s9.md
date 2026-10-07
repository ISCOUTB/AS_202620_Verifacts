# Auditoría S9 — erosión, dependencias

Fecha: 2026-09-28 (actualizada el 2026-10-01) · Estado auditado: rama `master`, commit `d2d7b5c` (más los cambios de este incremento).

Cada hallazgo indica cómo se detectó, qué se corrigió y qué queda abierto.

## 1. Erosión arquitectónica (límites de contexto y propiedad de datos de S6)

| ID | Hallazgo | Cómo se detectó | Corrección | Estado |
|---|---|---|---|---|
| E-1 | Ningún módulo accede a SQLite fuera de `app/persistence/repository.py` | `git grep -n sqlite3 -- app` solo devuelve `repository.py`; ahora lo vigila `tests/test_boundaries.py::test_sqlite3_solo_se_usa_en_el_repositorio` | Ninguna necesaria | ✅ Sin violación |
| E-2 | `app/modules/scoring/service.py` importaba `Finding` desde `app/modules/analysis/analyzer.py`, un archivo interno de otro módulo, saltándose `service.py` (convención de arc42 §8.4). Si `analyzer.py` se reorganiza (por ejemplo al añadir otro analizador), `Scoring` se rompe, contra la medida de Q-02 ("sin modificar `Scoring`") | Grafo de imports: `git grep -nE "^from app\." -- app`; ahora lo vigila `tests/test_boundaries.py::test_un_modulo_solo_importa_el_service_de_otro_modulo` | `scoring` importa `Finding` desde `app.modules.analysis.service` | ✅ Corregido |
| E-3 | Los módulos no importan `app.api` ni `app.persistence`; solo `app/api/routes.py` llama a `repository` | Mismo grafo; vigilado por `tests/test_boundaries.py::test_solo_la_api_toca_persistencia_y_los_modulos_no_conocen_la_api` | Ninguna necesaria | ✅ Sin violación |
| E-4 | Las pruebas escribían en la base real `data/verifacts.db` (mezclaban datos de prueba con datos de desarrollo) | Se ejecutó la suite y apareció `data/verifacts.db` | `tests/conftest.py` fija `VERIFACTS_DATA_DIR` a un directorio temporal | ✅ Corregido |
| E-5 | `data/verifacts.db` estuvo versionado en 7 commits (desde `2e9e48e` hasta `67f8cea`). Contenido inspeccionado: 4 filas de prueba (`"Prueba de persistencia"`, el texto de ejemplo del README, `"string"`), sin datos personales | `git log --all -- data/verifacts.db` y lectura del archivo del commit de alta | Ya no está versionado; `.gitignore` cubre `data/` y `*.db`. No se reescribe el historial: no contiene datos sensibles | ✅ Cerrado |

## 2. Coherencia entre documentos y código (afirmaciones de la IA sin respaldo)

| ID | Hallazgo | Cómo se detectó | Corrección | Estado |
|---|---|---|---|---|
| D-1 | **`MLAnalyzer` no existe en el repositorio**, pero `docs/ia.md` lo registra como "Aceptado" y `docs/adr/0002-contextos-sin-cambios.md` dice que se incorporó. Mientras tanto `docs/implementacion-backend.md`, `README.md` y arc42 §5 lo declaran pendiente | `git grep -n MLAnalyzer -- app tests requirements.txt` devuelve 0 coincidencias; `git log -S"MLAnalyzer"` solo toca documentos | `docs/ia.md` y ADR-0002 se corrigieron para reflejar el estado real | ✅ Corregido en `docs/ia.md` (fila del pipeline ML) y en una nota del ADR-0002. `MLAnalyzer` sigue pendiente |
| D-2 | La evidencia de Q-05 en `docs/escenarios-de-calidad.md` era una copia de la de Q-03, y la de Q-03 decía "Pendiente" con una frase cortada a la mitad, aunque `tests/test_rule_modification.py` existe | Lectura de las tres secciones | Reescritas las evidencias de Q-01, Q-03 y Q-05 | ✅ Corregido |
| D-3 | El índice de arc42 §9 no listaba ADR-0004, ADR-0005 ni ADR-0006 | Comparación de `docs/adr/` con la tabla | Índice completado | ✅ Corregido |
| D-4 | `.env.example` termina con una línea suelta `git status` (salida de terminal pegada por error) | `cat .env.example` | Línea eliminada | ✅ Corregido |
| D-5 | El ADR-0006 se subió como `docs/adr/ADR-0006.md` (fuera de la convención `NNNN-titulo-en-kebab-case.md`) y la auditoría quedó en la raíz, por lo que los enlaces de `aspectos.md`, README y arc42 §9 no resolvían | Revisión externa preliminar y comprobación de enlaces | Renombrado a `0006-semantica-del-resultado.md` y movida a `docs/auditoria-s9.md`; comprobador de enlaces sin errores | ✅ Corregido |
| D-6 | Las secciones «Commit de implementación» se añadieron a ADR-0001…0004 ya aceptados (commit `9430845`) sin declararlo | Revisión externa preliminar | Tabla «Enmiendas a ADR aceptados» en arc42 §9; regla: solo enmiendas con fecha que no cambien la decisión | ✅ Declarado |
| D-7 | No había un ADR de la decisión de no incorporar un componente generativo | Revisión externa preliminar | [ADR-0007](adr/0007-no-incorporar-componente-generativo.md) | ✅ Corregido |
| D-8 | SonarCloud no recibía cobertura de pruebas (el workflow no ejecutaba la suite) y el Quality Gate figuraba en rojo | `docs/despliegue.md` y el workflow `sonarcloud.yml` | El workflow ejecuta `pytest --cov` y envía `coverage.xml`. Quality Gate confirmado en VERDE (`status: OK`, 99.1 % de cobertura) | ✅ Corregido y confirmado en SonarCloud |

## 3. Dependencias que trajo el modelo

Todas las dependencias se comprobaron contra el registro (PyPI / npm) el 2026-09-28: existen, el repositorio declarado es el proyecto esperado y llevan años publicadas. Ninguna es un nombre inventado ni un typosquat.

| Paquete | Dónde | Repositorio declarado en el registro | Primera publicación | Veredicto |
|---|---|---|---|---|
| fastapi | `requirements.txt` | github.com/fastapi/fastapi | 2018 | ✅ Legítimo |
| uvicorn | `requirements.txt` | uvicorn.dev | 2017 | ✅ Legítimo |
| pytest | `requirements.txt` | docs.pytest.org | 2010 | ✅ Legítimo, **ver V-1** |
| httpx | `requirements.txt` | github.com/encode/httpx | 2019 | ✅ Legítimo |
| trafilatura | `requirements.txt` | trafilatura.readthedocs.io | 2019 | ✅ Legítimo |
| pyyaml | `requirements.txt` | pyyaml.org | 2011 | ✅ Legítimo |
| jsonschema | `requirements.txt` | github.com/python-jsonschema/jsonschema | 2012 | ✅ Legítimo, **ver V-2** |
| mangum | `serverless-prototype/requirements.txt` | github.com/Kludex/mangum | 2019 | ✅ Legítimo |
| pytest-cov | `.github/workflows/sonarcloud.yml` | github.com/pytest-dev/pytest-cov | 2010 | ✅ Legítimo |
| react, react-dom, @types/react, @types/react-dom, @vitejs/plugin-react, typescript, vite | `frontend/package.json` | repositorios oficiales de cada proyecto | 2011–2021 | ✅ Legítimos |

| ID | Hallazgo | Corrección | Estado |
|---|---|---|---|
| V-1 | `pip-audit -r requirements.txt` reporta una vulnerabilidad conocida (PYSEC-2026-1845) en `pytest 8.4.2`; la corrige `pytest 9.0.3`, que la restricción `pytest>=8,<9` impedía instalar | `requirements.txt` pasa a `pytest>=9.0.3,<10`. La suite completa pasa con pytest 9 | ✅ Corregido |
| V-2 | `tests/test_contract.py` usa `jsonschema.RefResolver`, API marcada como obsoleta (pytest lo avisa en cada corrida). Es el tipo de patrón que un modelo reproduce de su entrenamiento | No se corrige en este incremento | 🟡 Abierto (deuda técnica) |
| V-3 | `pytest-cov` se instala en `.github/workflows/sonarcloud.yml` sin fijar versión | Verificado en PyPI el 2026-10-06 (paquete legítimo de pytest-dev) | ✅ Verificado |

## 4. Credenciales

| Comprobación | Resultado |
|---|---|
| Búsqueda en archivos versionados de claves, tokens y contraseñas | Solo aparece `${{ secrets.SONAR_TOKEN }}` en `sonarcloud.yml` (referencia a GitHub Secrets, no un valor) |
| Búsqueda en todo el historial de patrones de AWS, GitHub, OpenAI, Slack y claves privadas | 0 coincidencias |
| Archivos `.env`, `.pem`, `.key` versionados | Solo `.env.example` y `frontend/.env.example`, sin valores sensibles |
| `.gitignore` | Ignora `.env`, `.env.*`, `*.pem`, `*.key` |

## 5. Higiene

- `VeriFacts-resumen-entrega-final c1.pdf` retirado de la raíz del repositorio.
- `docs/arc42/08-conceptos transversales.md` renombrado a `08-conceptos-transversales.md`; el enlace del README ya resuelve.

## Cómo repetir esta auditoría

```cmd
python -m pytest -q
pip install pip-audit
pip-audit -r requirements.txt
git grep -n "sqlite3" -- app
git grep -n "MLAnalyzer" -- app tests requirements.txt
```
