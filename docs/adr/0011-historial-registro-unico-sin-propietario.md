# ADR-0011: Historial como registro único, solo de adición y sin propietario, en SQLite

- Estado: Aceptado
- Fecha: 2026-10-20
- Decisor: Equipo VeriFacts
- Relación: complementa el [ADR-0001](0001-estilo-arquitectonico.md), el [ADR-0003](0003-integracion-sincrona.md) y el [ADR-0009](0009-decision-extraccion-modulo-analisis.md). Registra una decisión que ya está en el código (commit `3544894`) y evalúa su costo de reversión.

## Contexto

La revisión S12 pide identificar la decisión de datos **más costosa de revertir**. En VeriFacts los
datos viven en una tabla `analyses` de SQLite, escrita únicamente por `app/persistence/repository.py`
(regla de propiedad de datos en [propiedad-datos.md](../propiedad-datos.md), verificada por
`tests/test_boundaries.py`). Las decisiones de datos vigentes son:

1. **Motor:** SQLite embebido, en un archivo dentro de un volumen.
2. **Forma del dato:** `factors` se guarda como texto separado por `" | "`.
3. **Identificador:** entero autoincremental, expuesto en la API (`/analysis/{id}`).
4. **Contenido:** se guarda el texto completo analizado (escrito por el usuario o extraído de una URL).
5. **Propiedad:** el registro no tiene dueño ni sesión; el historial es global y de solo adición
   (el código no hace `UPDATE` ni `DELETE` sobre análisis).

## Decisión

Se mantiene el modelo actual: **un historial global, de solo adición y sin propietario, en un único
archivo SQLite**, y se reconoce que la decisión más costosa de revertir es la **4 + 5 combinadas**:
guardar el contenido completo sin dueño.

## Costo de reversión de cada decisión

| Decisión | Qué habría que cambiar | Costo | Por qué |
|---|---|---|---|
| Motor SQLite → otro motor | Solo `repository.py` y una migración de una tabla | Bajo a medio | El acceso a SQL está encerrado en un módulo y las pruebas de frontera impiden que otros lo toquen. |
| `factors` como texto con `" | "` → tabla o JSON | `repository.py` y una migración de filas | Bajo | La API no cambia: el contrato devuelve `list[str]`. |
| Identificador entero público → UUID | Contrato `openapi.yaml` 1.0.0, frontend, pruebas de contrato y todos los `id` ya citados | Medio a alto | Rompe el contrato con los clientes y obliga a migrar los identificadores existentes. |
| **Contenido completo sin propietario** | Definir retención, decidir qué datos ya guardados se borran o anonimizan, añadir identidad y asociar los registros nuevos | **Alto** | No se puede atribuir un dueño a los registros anteriores, y lo que ya se publicó por la API no se puede retirar de quien lo leyó. Cada día que pasa aumenta lo que habría que depurar. |

## Alternativas consideradas

| Alternativa | Motivo |
|---|---|
| Guardar solo la huella (hash) y los factores, sin el texto | Habría evitado el costo, pero el historial dejaría de mostrar qué se analizó (objetivo OBJ-01 y la interfaz actual). |
| Historial por sesión o usuario desde el inicio | Exige autenticación, que está fuera del alcance académico ([R-ORG-03](../arc42/02-restricciones.md)). |
| No persistir nada | Pierde el historial y la prueba de persistencia ([Q-05](../escenarios-de-calidad.md#q-05--repetibilidad-del-resultado)). |

## Consecuencias

**Positivas**

- Esquema mínimo y una sola tabla: bajo costo operativo y de comprensión.
- Solo adición: no hay conflictos de actualización; cada registro es inmutable tras crearse.
- Un solo módulo escribe (propiedad de datos clara).

**Negativas y riesgos aceptados**

- Cualquier visitante puede leer el texto que enviaron otros (riesgo MF-08 en
  [arc42 §11](../arc42/11-riesgos-y-deuda-tecnica.md)); los `id` consecutivos permiten recorrerlos.
- Choca con [R-DAT-01](../arc42/02-restricciones.md) (evitar datos personales innecesarios).
- SQLite en un solo nodo: no hay réplicas ni escritura concurrente a gran escala (MF-04, MF-10).

## Disparadores de reevaluación

Esta decisión se reevalúa si ocurre alguna de estas condiciones:

1. Se añade autenticación o identidad de usuario.
2. El sistema se despliega con más de un proceso o réplica.
3. Se define una política de retención o una petición de borrado de datos.
4. El historial se usa fuera del entorno de prueba con personas reales.

## Mitigación inmediata (pendiente)

Mientras no haya identidad, la opción de menor costo es **no devolver `content` en `GET /analysis`**
(solo puntuación, clasificación, factores y fecha) y limitar su lectura por `id`. Cambia el contrato
(`openapi.yaml`), por lo que requiere una versión nueva del contrato y de las pruebas de contrato.

## Relación con los escenarios

- [Q-05](../escenarios-de-calidad.md#q-05--repetibilidad-del-resultado): la persistencia permite recuperar el análisis por `id`.
- Garantías de consistencia de cada operación: [arc42 §8.6](../arc42/08-conceptos-transversales.md#86-consistencia-de-datos).
