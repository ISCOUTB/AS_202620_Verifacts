# Escenarios de calidad — VeriFacts

Cada escenario se describe mediante fuente, estímulo, artefacto, entorno,
respuesta y medida.

---

# Q-01 — Tiempo de respuesta del análisis

**Atributo:** Rendimiento

### Fuente

Usuario final.

### Estímulo

El usuario envía un texto de hasta 10.000 caracteres.

### Artefacto

Pipeline de análisis de VeriFacts.

### Entorno

Aplicación ejecutándose localmente con un usuario concurrente.

### Respuesta

El sistema procesa el contenido y presenta el resultado al usuario.

### Medida

El P95 del tiempo total de análisis deberá ser menor o igual a 3 segundos.

**Impacto:** Alto  
**Riesgo técnico:** Alto  
**Prioridad:** Muy alta

### Decisión relacionada

La táctica aplicada se encuentra en
[arc42 sección 4](arc42/04-estrategia-de-solucion.md#q-01--rendimiento).

### Evidencia

Pendiente — el pipeline `POST /analysis` ya existe (ver
[tests/test_analysis.py](../tests/test_analysis.py)), pero todavía no hay
una medición formal de P95. Próximo paso natural para cerrar este escenario.

---

# Q-02 — Incorporación de un nuevo analizador

**Atributo:** Escalabilidad

### Fuente

Equipo de desarrollo.

### Estímulo

Se requiere incorporar una nueva regla o mecanismo de análisis.

### Artefacto

Módulo `Analysis`.

### Entorno

Desarrollo local, manteniendo la interfaz y persistencia existentes.

### Respuesta

El nuevo analizador se incorpora sin modificar la interfaz ni la persistencia.

### Medida

La incorporación deberá limitarse al módulo `Analysis` y sus pruebas, sin
modificar los módulos `API`, `Content` o `Scoring`.

**Impacto:** Alto  
**Riesgo técnico:** Alto  
**Prioridad:** Muy alta

### Decisión relacionada

Este escenario motiva directamente la selección del monolito modular.

[ADR-0001 — Usar monolito modular](adr/0001-estilo-arquitectonico.md).

### Evidencia

`RuleAnalyzer` (`app/modules/analysis/analyzer.py`) se incorporó sin tocar
`API`, `Content` ni `Scoring`; verificado end-to-end en
[tests/test_analysis.py](../tests/test_analysis.py). Ver fila **A-01** en la
[tabla de aspectos](aspectos.md). El mismo principio de bajo acoplamiento se
verificó de nuevo al incorporar el frontend como cliente HTTP independiente,
sin modificar `Content`, `Analysis` ni `Scoring` — ver fila **A-04**.

---

# Q-03 — Modificación de una regla

**Atributo:** Mantenibilidad

### Fuente

Desarrollador.

### Estímulo

Se solicita modificar una regla existente.

### Artefacto

Regla específica dentro de `Analysis`.

### Entorno

Desarrollo local con las pruebas existentes.

### Respuesta

El desarrollador modifica la regla sin cambiar otros módulos no relacionados.

### Medida

El cambio deberá estar limitado a la regla y sus pruebas y no deberá producir
regresiones en las pruebas existentes.

**Impacto:** Alto  
**Riesgo técnico:** Medio-alto  
**Prioridad:** Alta

### Decisión relacionada

La táctica correspondiente está documentada en
[arc42 sección 4](arc42/04-estrategia-de-solucion.md#q-03--mantenibilidad).

### Evidencia

Pendiente — falta una prueba que module una regla existente de
`RuleAnalyzer` (por ejemplo, el umbral de mayúsculas) y confirme que
`tests/test_health.py`, `tests/test_analysis.py` y `tests/test_history.py`
siguen en verde. Ver fila **A-02** en la [tabla de aspectos](aspectos.md).

---

# Q-04 — Comprensión del resultado

**Atributo:** Usabilidad

### Fuente

Usuario sin conocimientos técnicos.

### Estímulo

El usuario utiliza VeriFacts por primera vez.

### Artefacto

Interfaz y resultado del análisis.

### Entorno

Prototipo local.

### Respuesta

El usuario introduce el contenido, ejecuta el análisis y comprende la
clasificación obtenida.

### Medida

Al menos 4 de 5 usuarios de prueba deberán completar el flujo sin asistencia
y explicar correctamente el significado básico del resultado.

**Impacto:** Alto  
**Riesgo técnico:** Medio  
**Prioridad:** Alta

### Decisión relacionada

La táctica correspondiente está documentada en
[arc42 sección 4](arc42/04-estrategia-de-solucion.md#q-04--usabilidad).

### Evidencia

Pendiente — la interfaz web (`frontend/`) ya existe y presenta el resultado
en lenguaje simple (puntuación, clasificación y factores, sin terminología
técnica de NLP/ML), pero la medida definida requiere una prueba de usuario
real (4 de 5 completando el flujo sin asistencia), que todavía no se ha
ejecutado. La existencia de la interfaz es condición necesaria, no evidencia
suficiente por sí sola.

---

# Q-05 — Repetibilidad del resultado

**Atributo:** Confiabilidad

### Fuente

Usuario o analista.

### Estímulo

Se envía el mismo contenido dos o más veces bajo la misma configuración.

### Artefacto

Pipeline de análisis de VeriFacts.

### Entorno

Aplicación ejecutándose localmente, sin cambios de configuración entre ejecuciones.

### Respuesta

El sistema produce el mismo resultado (puntuación y clasificación) para la misma entrada.

### Medida

100% de coincidencia en el resultado ante entradas idénticas y configuración idéntica.

**Impacto:** Alto  
**Riesgo técnico:** Bajo  
**Prioridad:** Alta

### Decisión relacionada

[ADR-0001 — Usar monolito modular](adr/0001-estilo-arquitectonico.md).

### Evidencia

`RuleAnalyzer` (`app/modules/analysis/analyzer.py`) se modificó ampliando el
conjunto `absolute_words`; el cambio se limitó a ese archivo y no afectó
`API`, `Content` ni `Scoring`. Verificado en
[tests/test_rule_modification.py](../tests/test_rule_modification.py), que
además confirma que `tests/test_health.py` y `tests/test_analysis.py` siguen
en verde. Ver fila **A-02** en la [tabla de aspectos](aspectos.md).
