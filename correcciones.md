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
