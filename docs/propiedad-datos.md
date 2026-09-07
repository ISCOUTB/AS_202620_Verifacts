# Propiedad de datos por módulo · VeriFacts

| Módulo / Contexto | Datos que posee | Dueño único de escritura | Quién puede leer |
|---|---|---|---|
| Ingesta y Presentación | Ninguno persistente (solo validación en memoria) | — | — |
| Análisis de Contenido | Reglas, pesos y umbrales de clasificación (configuración, no en base de datos) | Análisis de Contenido | Análisis de Contenido |
| Historial de Análisis | Tabla `analyses`: id, contenido, score, clasificación, factores | Historial de Análisis | Ingesta (solo lectura, a través de Historial — endpoint aún no implementado) |

> **Nota de coherencia:** la fila de "Historial de Análisis" describía
> originalmente una columna de fecha ("fecha, contenido, score,
> clasificación, factores"). El esquema real en
> `app/persistence/repository.py` (`CREATE TABLE analyses`) **no** tiene
> todavía una columna de fecha/timestamp. Se corrige aquí para no declarar
> algo que el código aún no tiene; queda como pendiente de Base de Datos
> (agregar `created_at`, ver sección "Listo para construir" en la
> conversación con Claude).

## Cómo verificarlo contra el código real

Este proyecto **no usa SQLAlchemy** — usa `sqlite3` de la librería estándar
directamente, encapsulado en `app/persistence/repository.py`. El método de
verificación se ajusta a esa realidad:

1. Busca en todo `app/` llamadas a `sqlite3.connect(` o a `_get_connection()`
   fuera de `app/persistence/repository.py`.
   ```cmd
   findstr /s /i "sqlite3.connect" app\*.py
   ```
2. Si aparece alguna coincidencia fuera de `app/persistence/repository.py`,
   **el dueño único no se está respetando** — otro módulo tiene acceso
   directo a la base de datos. Esa es una violación real y va en
   [`docs/violaciones-modularidad.md`](violaciones-modularidad.md).
3. Si en cambio solo `app/persistence/repository.py` abre la conexión, y los
   demás módulos (como `app/api/routes.py`) solo llaman a funciones como
   `save_analysis()` o `get_analysis()` pasándoles el resultado ya
   calculado, la regla se está respetando.

## Estado verificado (auditoría de esta entrega)

Se revisó `app/api/routes.py`: `create_analysis()` importa y llama
`save_analysis()` desde `app.persistence.repository`, pero no importa
`sqlite3` ni abre conexiones propias. `app/modules/analysis/service.py` y
`app/modules/scoring/service.py` tampoco tocan la base de datos. **No se
encontraron violaciones** de propiedad de datos en el estado actual del
código revisado. El detalle de esta verificación (y el lugar para registrar
violaciones futuras) está en
[`docs/violaciones-modularidad.md`](violaciones-modularidad.md).
