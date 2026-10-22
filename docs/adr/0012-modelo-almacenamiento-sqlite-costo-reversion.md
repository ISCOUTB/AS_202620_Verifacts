# ADR-0012: Modelo de almacenamiento en SQLite — decisión de datos más costosa de revertir

- Estado: Aceptado
- Fecha: 2026-10-21
- Decisor: Equipo VeriFacts
- Relación: complementa el [ADR-0011](0011-historial-registro-unico-sin-propietario.md) (historial sin propietario), el [ADR-0001](0001-estilo-arquitectonico.md) (monolito modular) y el [ADR-0009](0009-decision-extraccion-modulo-analisis.md) (no extracción). Formaliza la identificación y comparación de la decisión de datos con mayor costo de reversión, exigida en la revisión S12.

## Contexto

La revisión S12 requiere identificar cuál es la **decisión de persistencia o modelo de datos más costosa
de revertir**, argumentar por qué es la más costosa frente a las demás y cuantificar el esfuerzo de
migración. En VeriFacts todas las decisiones de datos confluyen en una sola tabla `analyses` dentro de un
archivo SQLite, escrita exclusivamente por `app/persistence/repository.py`
([propiedad de datos](../propiedad-datos.md)).

Las cinco decisiones de datos vigentes son:

1. **Motor de persistencia:** SQLite embebido, archivo único en un volumen.
2. **Forma del dato `factors`:** texto separado por `" | "` (no JSON, no tabla relacional).
3. **Identificador público:** entero autoincremental (`INTEGER PRIMARY KEY AUTOINCREMENT`), expuesto en
   la API (`/analysis/{id}`) y en el contrato `openapi.yaml`.
4. **Contenido completo almacenado:** el campo `content` guarda el texto íntegro analizado (escrito por
   el usuario o extraído de una URL).
5. **Historial global sin propietario:** el registro no tiene campo de usuario, sesión ni organización;
   es de solo adición (no hay `UPDATE` ni `DELETE`).

## Decisión

Se identifica la **combinación de las decisiones 4 y 5** (contenido completo sin propietario) como la
**decisión de datos más costosa de revertir**. Se mantiene el modelo actual y se acepta el costo de
reversión como riesgo conocido, documentado en [arc42 §11](../arc42/11-riesgos-y-deuda-tecnica.md)
(MF-08).

## Comparación del costo de reversión

La siguiente tabla compara las cinco decisiones de datos, ordenadas de mayor a menor costo de reversión.
El costo se estima en esfuerzo de desarrollo (horas-persona), impacto en el contrato público de la API,
necesidad de migración de datos existentes y riesgo de pérdida de información.

| # | Decisión de datos | Qué habría que cambiar para revertirla | Migración de datos existentes | Impacto en contrato y clientes | Costo estimado | Justificación del costo |
|---|---|---|---|---|---|---|
| **4+5** | **Contenido completo sin propietario** | Definir política de retención, añadir campo de identidad (`user_id` / `session_id`), decidir qué hacer con los registros anteriores (borrar, anonimizar o atribuir), modificar la API para exigir autenticación. | **Irreversible para registros previos:** no se puede atribuir un dueño a lo ya almacenado; los datos ya expuestos por la API no pueden retirarse de quienes los leyeron. Requiere script de purgado o anonimización con decisión caso a caso. | **Alto:** nuevos campos en la respuesta, flujo de autenticación, posible versionamiento del contrato. | **Alto** (40–80 h) | **Es la más costosa porque cada día que pasa sin dueño aumenta el volumen de datos irrecuperables.** No es un cambio de esquema técnico sino una decisión de negocio con implicaciones legales (GDPR, Habeas Data). Además, no se puede automatizar: requiere decisión humana sobre cada registro. |
| **3** | Identificador entero público → UUID | Cambiar el tipo de `id` en `analyses`, actualizar `openapi.yaml` (versión nueva), frontend, pruebas de contrato y todas las referencias externas a `id`. | Script de migración para asignar UUIDs y mantener una tabla de correspondencia `old_id → uuid` durante la transición. | **Alto:** rompe todos los enlaces y bookmarks que usen el `id` numérico. Requiere versionamiento del contrato. | **Medio-alto** (20–40 h) | Afecta a todos los consumidores del API, pero es automatizable y no tiene implicaciones legales. |
| **1** | Motor SQLite → PostgreSQL u otro | Reescribir `repository.py` para usar el driver del nuevo motor; migrar el archivo SQLite a la nueva base; ajustar el despliegue (`docker-compose`, variables de entorno). | `sqlite3 .dump` → importar en el motor destino. Una sola tabla simple, sin triggers ni vistas. | **Ninguno:** el contrato HTTP no cambia; el motor es un detalle interno. | **Medio** (16–24 h) | El acceso a SQL está encapsulado en un solo módulo (`repository.py`) y las pruebas de frontera (`test_boundaries.py`) impiden que otros lo toquen. La migración de datos es directa. |
| **2** | `factors` como texto → JSON o tabla relacional | Modificar `_row_to_dict` y `save_analysis` en `repository.py`; migración de filas existentes con `UPDATE`. | Script `UPDATE analyses SET factors = json(…)` para convertir el formato. Simple y automatizable. | **Ninguno:** la API ya devuelve `factors` como `list[str]`; el formato interno no cambia el contrato. | **Bajo** (4–8 h) | Un solo punto de serialización/deserialización. La prueba `test_contract.py` garantiza que la API sigue devolviendo la misma forma. |
| **1** (variante) | Agregar réplica de lectura o caché | Añadir lógica de replicación o caché en `repository.py`; ajustar garantías de consistencia (ver [arc42 §8.6](../arc42/08-conceptos-transversales.md#86-consistencia-de-datos)). | No requiere migración: los datos existentes se leen desde la fuente original. | **Ninguno.** | **Bajo** (8–16 h) | No cambia el esquema ni el contrato; solo añade una capa de lectura. |

## Argumento: por qué 4+5 es la más costosa

1. **Acumulación irreversible.** Los registros sin dueño se acumulan desde el primer despliegue. Cada día
   que el sistema opera sin identidad de usuario, el costo de revertir crece linealmente: más registros que
   purgar, anonimizar o atribuir manualmente.

2. **Imposibilidad de atribución retroactiva.** No se puede asignar un `user_id` a un registro existente
   porque no hay forma de saber quién lo creó. A diferencia de un cambio de tipo de `id` (decisión 3), que
   se resuelve con un script de mapeo, aquí la información simplemente no existe.

3. **Datos ya expuestos.** Los textos completos almacenados han sido accesibles por `GET /analysis/{id}` y
   `GET /analysis` sin autenticación. Lo que un tercero ya leyó no se puede retirar. Esto convierte la
   reversión en un problema de gobernanza de datos, no solo de ingeniería.

4. **Impacto transversal.** Revertir esta decisión toca el esquema, la API (autenticación), el frontend
   (login), el contrato OpenAPI, las pruebas, el despliegue y la documentación. Ninguna otra decisión
   tiene un radio de impacto comparable.

## Consecuencias

### Positivas (de mantener la decisión actual)

- Esquema mínimo: una sola tabla sin índices adicionales ni tabla de usuarios.
- Sin flujo de autenticación: reduce la superficie de ataque y la complejidad del despliegue académico.
- Historial completo: el usuario puede ver qué texto analizó (OBJ-01).

### Negativas y riesgos aceptados

- Cualquier visitante puede leer el texto que enviaron otros (MF-08 en [arc42 §11](../arc42/11-riesgos-y-deuda-tecnica.md)).
- Los `id` consecutivos permiten recorrerlos programáticamente.
- Tensión con [R-DAT-01](../arc42/02-restricciones.md) (evitar datos personales innecesarios).
- El costo de reversión crece con cada registro almacenado.

## Disparadores de reevaluación

Esta decisión se reevalúa si ocurre alguna de estas condiciones:

1. Se añade autenticación o identidad de usuario al sistema.
2. Se recibe una solicitud formal de borrado de datos personales.
3. El sistema se despliega fuera del entorno académico con usuarios reales.
4. Se define una política de retención de datos.

## Mitigación inmediata recomendada

Mientras no haya identidad, la opción de menor costo es **no devolver `content` en el listado
`GET /analysis`** (solo `id`, puntuación, clasificación, factores y fecha), y limitar la lectura del
texto completo al endpoint `GET /analysis/{id}`. Esto reduce la exposición sin cambiar el esquema.
Requiere una versión nueva del contrato (`openapi.yaml` 1.1.0) y de las pruebas de contrato.

## Relación con otros documentos

- [ADR-0011](0011-historial-registro-unico-sin-propietario.md): define el modelo de historial actual.
- [arc42 §8.6](../arc42/08-conceptos-transversales.md#86-consistencia-de-datos): garantías de consistencia por operación.
- [arc42 §8.7](../arc42/08-conceptos-transversales.md#87-política-de-caché): diseño de caché.
- [arc42 §11](../arc42/11-riesgos-y-deuda-tecnica.md): riesgos MF-08 y deuda técnica.
- [Propiedad de datos](../propiedad-datos.md): un solo módulo escribe en `analyses`.
