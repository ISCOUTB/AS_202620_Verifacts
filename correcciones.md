# Correcciones aplicadas — VeriFacts

Registro de las observaciones recibidas en la retroalimentación semanal y su estado de corrección en el repositorio.

**Equipo:** Pedro Jose Castro Blanquicett, Cristian Cardeno, Julian Samuel Cabeza Pena
**Repositorio:** https://github.com/ISCOUTB/AS_202620_Verifacts

---

## Semanas 1 y 2

| Observación del profesor | Estado | Corrección aplicada |
|---|---|---|
| Los 5 escenarios de calidad del PDF de entrega no estaban en el repositorio. | ✅ Corregido | `docs/escenarios-de-calidad.md` con Q-01 a Q-05, cada uno en sus 6 partes (fuente, estímulo, artefacto, entorno, respuesta, medida numérica). |
| Priorizar el árbol de utilidad por impacto y riesgo (era lista plana de atributos). | 🔴 Pendiente | `docs/arbol-utilidad.md` sigue siendo un árbol de refinamiento sin anotación explícita de impacto/riesgo por rama. Falta anotar cada hoja con Alto/Medio/Bajo. |
| Tabla de aspectos con las 8 columnas del curso y enlaces hasta la evidencia (era narrativa). | ✅ Corregido | `docs/aspectos.md` reescrita con exactamente ID · Aspecto · Requisito · C4 · ADR · Código · Pruebas · Evidencia. Fila A-00 navegable de punta a punta. |
| Leyenda en el C4 y dos tensiones de calidad enfrentadas en la ficha del problema. | 🔴 Pendiente | Los diagramas C4 (`docs/c4/01` y `02`) no tienen leyenda de notación. La ficha del problema (Sección 1) no declara explícitamente 2 tensiones de calidad (ej. rendimiento vs. explicabilidad). |
| Registro de IA como uso real (qué se usó, qué se rechazó y por qué). | ✅ Corregido | `docs/ia.md` reescrito con 4 registros formato Aceptado/Rechazado/Pendiente, cada uno con motivo técnico. |
| Los tres integrantes con commits en el repositorio. | 🔴 Pendiente | Julian Samuel Cabeza Pena sigue sin commits en el historial (`git shortlog -sne`). Acción del equipo, no de documentación. |
| Estructura mínima: `docs/arc42/`, `docs/c4/`, `docs/ia.md` en minúsculas. | ✅ Corregido | Reorganizado: `docs/arc42/` (secciones numeradas), `docs/c4/01-contexto.md` y `02-contenedores.md`, `docs/ia.md` en minúsculas. |

---

## Semana 3

| Observación del profesor | Estado | Corrección aplicada |
|---|---|---|
| Completar arc42 §4 con tácticas concretas ligadas a Q-01…Q-05 (eran principios genéricos). | ✅ Corregido | `docs/arc42/04-estrategia-de-solucion.md` reescrita: una subsección por escenario (4.3 a 4.7) con tácticas nombradas (encapsular la variación, reducir el acoplamiento, proveer retroalimentación, etc.) y su aplicación concreta en el código. |
| Rehacer `docs/matriz-estilos.md` contra las ramas del árbol de utilidad, escenario por escenario. | ✅ Corregido | Verificado: el documento ya compara los 3 estilos contra Q-01–Q-05 con análisis por escenario. No requirió reescritura adicional. |
| Enlazar el ADR desde `docs/aspectos.md` y desde el escenario que lo motiva; convertir `docs/IA.md` en registro de uso. | ✅ Corregido | `aspectos.md` y `escenarios-de-calidad.md` (Q-02) enlazan a `docs/adr/0001-estilo-arquitectonico.md`. `docs/ia.md` reescrito como registro aceptado/rechazado. |
| Documentar el comando único de arranque en el README y acomodar `docs/c4/`. | ✅ Corregido | README sección 13 documenta `python run.py`; se agregó encabezado "Corte vertical ejecutable". `docs/c4/` ya contiene `01-contexto.md` y `02-contenedores.md`. |
| Contribución: los tres integrantes deben aparecer en el historial antes del corte 1. | 🔴 Pendiente | Mismo hallazgo que S1/S2 — sigue sin resolverse. |

---

## Semana 4 · S4

| Observación del profesor | Estado | Corrección aplicada |
|---|---|---|
| El corte vertical al cierre solo cubría `GET /health`, sin lógica ni persistencia. | 🔴 Pendiente | Sigue siendo el único corte vertical ejecutable. Implementar Content/Analysis/Scoring queda fuera del alcance de este incremento documental — es trabajo de código para el corte 1. |
| `docs/aspectos.md` no usa las 8 columnas del curso (falta la cadena requisito-C4-ADR-código). | ✅ Corregido | Reescrita con las 8 columnas exactas: ID · Aspecto · Requisito · C4 · ADR · Código · Pruebas · Evidencia. Fila A-00 navegable completa; A-01/A-02 marcadas "Pendiente" honestamente desde Código en adelante. |
| La URL del run de CI citada en `aspectos.md` daba 404; no había runs visibles. | 🟡 Parcial | `.github/workflows/tests.yml` creado y corregido para usar `python -m pytest -q`. `aspectos.md` ya no cita una URL rota, remite a "ver run en Actions". Falta que el equipo haga push y pegue la URL real del run en verde. |
| Limpiar `__pycache__/`, `*.pyc`, archivos duplicados «(1).py» y PDFs en la raíz. | 🟡 Parcial | Se corrigieron `__init__.py` mal nombrados (scoring, tests) y se agregó `.gitignore` + `git rm --cached` de `__pycache__`. El archivo `resumen-entrega.pdf` sigue en la raíz del repo (ver pendiente abajo). |
| Sigue pendiente desde S1: que el tercer integrante aparezca en el historial de commits. | 🔴 Pendiente | Sin resolver — acción exclusiva del equipo. |

---


## Semana 11 · S11 (Modos de fallo, Idempotencia y Decisión de Extracción)

| Observación del profesor | Estado | Corrección aplicada |
|---|---|---|
| **Correspondencia entre mitigaciones declaradas e implementadas:** La tabla habla de timeout estricto de 4 s, 504/422 y WAL en SQLite como hechos, pero en código no están configurados. Falta declarar honestamente qué está implementado y qué pendiente. | ✅ Corregido | Se incorporó la columna «Estado real en el código» en [`docs/entregas/entrega-modos-fallo-idempotencia-adr.md`](docs/entregas/entrega-modos-fallo-idempotencia-adr.md) y la columna «Estado» en [`docs/arc42/11-riesgos-y-deuda-tecnica.md`](docs/arc42/11-riesgos-y-deuda-tecnica.md), declarando honestamente MF-01, MF-03 y MF-05 como *Pendiente*, MF-02 y MF-04 como *Parcial*, y MF-06 como *Implementado*. |
| **arc42 sección 11 con los modos de fallo:** El archivo 11 del repo contenía el glosario (`11-glosario.md`); no existía sección de riesgos que incorporara MF-01 a MF-06. | ✅ Corregido | El glosario fue trasladado a [`docs/arc42/12-glosario.md`](docs/arc42/12-glosario.md) y se creó [`docs/arc42/11-riesgos-y-deuda-tecnica.md`](docs/arc42/11-riesgos-y-deuda-tecnica.md) estructurando formalmente la matriz de modos de fallo, probabilidad, impacto, estado real y plan de cierre. |
| **Filas de aspectos afectadas por la integración al día:** La tabla `docs/aspectos.md` solo llegaba hasta la Semana 10 (ADR-0008); faltaba incorporar ADR-0009 y la resiliencia S11. | ✅ Corregido | Se incorporó la fila **A-08** (*Resiliencia de la integración externa (URL) y modos de fallo*) en [`docs/aspectos.md`](docs/aspectos.md) con las 8 columnas completas, enlazando a [ADR-0009](docs/adr/0009-decision-extraccion-modulo-analisis.md) y `tests/test_url_ingestion.py`. |
| **ADR aceptados no reescritos:** En `docs/adr/0003-integracion-sincrona.md` se añadió contenido al final sin adenda fechada formal. | ✅ Corregido | Se formalizó el encabezado `## Adenda (2026-09-23) — Implementación` en [`docs/adr/0003-integracion-sincrona.md`](docs/adr/0003-integracion-sincrona.md) (y en ADR-0001 a ADR-0004), preservando la decisión inmutable original. |
| **Registro de IA al día para la semana:** `docs/ia.md` llegaba solo hasta S9; faltaba el registro del periodo S11. | ✅ Corregido | Se agregaron las interacciones semanales de S11 en [`docs/ia.md`](docs/ia.md) y la sección consolidada de propuestas Aceptadas, Corregidas y Rechazadas con motivo técnico. |
| **Sin credenciales en repositorio ni historial:** El barrido histórico no pudo completarse en la evaluación remota. | ✅ Corregido | Se documentó el barrido exhaustivo en [`docs/evidencia/revision-secretos-s12.md`](docs/evidencia/revision-secretos-s12.md) sobre los 327 commits del árbol completo con expresiones regulares sin hallazgos de secretos. |

---


## Semana 12 · S12 (Consistencia, Caché, Invalidación y Decisión de Datos más Costosa)

| Observación del profesor | Estado | Corrección aplicada |
|---|---|---|
| **Tabla operación a garantía de consistencia con operaciones reales:** Solo había tabla de modos de fallo, sin matriz de consistencia por operación. | ✅ Corregido | Se incorporó en [`docs/arc42/08-conceptos-transversales.md`](docs/arc42/08-conceptos-transversales.md) (§8.6) la tabla canónica de 7 columnas (`Operación`, `Garantía requerida`, `Si el dato llega tarde...`, `Mecanismo de cumplimiento`, `Nivel de aislamiento SQLite`, `Idempotente`, `Prueba ejecutable`) mapeando `POST /analysis`, `GET /analysis/{id}`, `GET /analysis` y `GET /metrics`. |
| **Dos operaciones verificadas contra la implementación:** Sin garantía por operación no se acreditaban dos verificaciones ejecutables. | ✅ Corregido | Se implementaron 6 pruebas unitarias automatizadas en [`tests/test_consistencia.py`](tests/test_consistencia.py), contrastando visibilidad tras commit en `POST /analysis` y garantía *read-your-writes* inmutable en `GET /analysis/{id}`. |
| **Diseño de caché: qué, dónde y cuánto:** Respuesta en diseño de idempotencia no es política completa de caché; faltaba evaluar qué/dónde/duración o justificar no caché. | ✅ Corregido | Se redactó [`docs/arc42/08-conceptos-transversales.md`](docs/arc42/08-conceptos-transversales.md) (§8.7) con la matriz completa de las 3 dimensiones (qué, dónde, TTL/duración, invalidación y decisión) para 5 candidatos, justificando la no-caché en backend (P95 < 50 ms) e identificando la única caché activa en Nginx (`/assets/` con `expires 1y immutable`). |
| **Política de invalidación tras escritura:** Falta definir refresco/invalidación del historial tras crear análisis. | ✅ Corregido | Se formalizó en [`docs/arc42/08-conceptos-transversales.md`](docs/arc42/08-conceptos-transversales.md) (§8.8) la política de invalidación por recarga explícita del frontend (`history.refresh()` en `App.tsx`) y el diseño de vaciado activo tras commit antes de responder para caché del listado. |
| **ADR de la decisión de datos más costosa de revertir y su argumento/costo:** No extracción no equivale a la decisión de datos de mayor costo de reversión; falta comparar costo frente a otras decisiones. | ✅ Corregido | Se creó el [ADR-0012](docs/adr/0012-modelo-almacenamiento-sqlite-costo-reversion.md), comparando cuantitativamente las 5 decisiones de datos vigentes (horas-persona, migración, impacto en contrato) y demostrando por qué almacenar contenido completo sin propietario (decisiones 4+5) es la más costosa de revertir (40–80 h). |
| **arc42 sección 8 con consistencia y caché:** La sección 8 no reunía la estrategia de consistencia ni caché de S12. | ✅ Corregido | [`docs/arc42/08-conceptos-transversales.md`](docs/arc42/08-conceptos-transversales.md) consolidó las subsecciones §8.6 (consistencia), §8.7 (caché), §8.8 (invalidación) y §8.9 (flujo por eventos). |

---
