# Escenarios de calidad — VeriFacts

Cada escenario contiene fuente, estímulo, artefacto, entorno, respuesta y
medida verificable.

---

# Q-01 — Tiempo de respuesta del análisis

## Atributo

Eficiencia de desempeño.

## Fuente

Usuario final.

## Estímulo

El usuario envía un texto de hasta 10.000 caracteres para análisis.

## Artefacto

Pipeline de análisis de VeriFacts.

## Entorno

Aplicación ejecutándose localmente con un usuario concurrente y equipo de
desarrollo convencional.

## Respuesta

El sistema procesa el texto, ejecuta los analizadores habilitados y presenta
el resultado al usuario.

## Medida

El percentil 95 (P95) del tiempo total de análisis deberá ser menor o igual a
3 segundos para textos de hasta 10.000 caracteres.

## Prioridad

Muy alta.

## Impacto

Alto.

## Riesgo técnico

Alto.

---

# Q-02 — Incorporación de un nuevo analizador

## Atributo

Escalabilidad y mantenibilidad.

## Fuente

Equipo de desarrollo.

## Estímulo

Se requiere incorporar una nueva regla o mecanismo de análisis.

## Artefacto

Módulo `Analysis`.

## Entorno

Durante una iteración normal de desarrollo, sin modificar la interfaz ni la
persistencia.

## Respuesta

El nuevo analizador se incorpora dentro del módulo de análisis sin modificar
la interfaz de usuario ni el esquema de persistencia.

## Medida

La implementación de un nuevo analizador deberá limitarse al módulo de
análisis y sus pruebas, sin modificar los módulos `API`, `Content` o
`Scoring`.

## Prioridad

Muy alta.

## Impacto

Alto.

## Riesgo técnico

Alto.

---

# Q-03 — Modificación de una regla

## Atributo

Mantenibilidad.

## Fuente

Desarrollador.

## Estímulo

Se solicita cambiar el comportamiento de una regla existente.

## Artefacto

Regla específica dentro del módulo `Analysis`.

## Entorno

Desarrollo local con la suite de pruebas existente.

## Respuesta

El desarrollador modifica la regla sin alterar otros módulos no relacionados.

## Medida

El cambio deberá limitarse a la implementación de la regla y sus pruebas,
manteniendo las pruebas de los demás módulos sin regresiones.

## Prioridad

Alta.

## Impacto

Alto.

## Riesgo técnico

Medio-alto.

---

# Q-04 — Comprensión del resultado

## Atributo

Usabilidad.

## Fuente

Usuario sin conocimientos técnicos.

## Estímulo

El usuario utiliza VeriFacts por primera vez para analizar un texto.

## Artefacto

Interfaz de usuario y resultado del análisis.

## Entorno

Prototipo local.

## Respuesta

El usuario consigue introducir el contenido, ejecutar el análisis e
interpretar correctamente la clasificación y los factores mostrados.

## Medida

Al menos 4 de 5 usuarios de prueba deberán completar el flujo de análisis sin
asistencia y explicar correctamente el significado básico del resultado.

## Prioridad

Alta.

## Impacto

Alto.

## Riesgo técnico

Medio.

---

# Q-05 — Repetibilidad del resultado

## Atributo

Confiabilidad.

## Fuente

Usuario o sistema de pruebas.

## Estímulo

El mismo contenido se analiza repetidamente utilizando la misma configuración
y versión del sistema.

## Artefacto

Pipeline de análisis y `Scoring Engine`.

## Entorno

Misma versión de la aplicación y mismas reglas de análisis.

## Respuesta

El sistema produce los mismos factores y la misma puntuación.

## Medida

El 100 % de las ejecuciones repetidas bajo las mismas condiciones deberá
producir resultados idénticos.

## Prioridad

Alta.

## Impacto

Medio-alto.

## Riesgo técnico

Medio.
