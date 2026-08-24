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
[arc42 sección 4](arc42/04-estrategia-de-solucion.md#43-q-01--rendimiento).

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
[arc42 sección 4](arc42/04-estrategia-de-solucion.md#45-q-03--mantenibilidad).
