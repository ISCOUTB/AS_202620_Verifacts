
# Propiedad de datos por módulo · VeriFact

| Módulo / Contexto | Datos que posee | Dueño único de escritura | Quién puede leer |
|---|---|---|---|
| Ingesta y Presentación | Ninguno persistente (solo validación en memoria) | — | — |
| Análisis de Contenido | Reglas, pesos y umbrales de clasificación (configuración, no en base de datos) | Análisis de Contenido | Análisis de Contenido |
| Historial de Análisis | Tabla de análisis guardados: fecha, contenido, score, clasificación, factores | Historial de Análisis | Ingesta (solo lectura, a través de Historial) |

## Cómo verificarlo contra el código real

1. Abre el archivo donde vive el endpoint de análisis (la ruta que recibe el texto/URL).
2. Busca si ese archivo importa el modelo de SQLAlchemy de la tabla de historial y le hace `add`/`commit` directamente.
3. Si lo hace, **el dueño único no se está respetando todavía** — dos módulos (Análisis y lo que sea que exponga esa ruta) tienen permiso de escritura sobre el mismo dato. Esa es una violación real, no hipotética, y va en `docs/violaciones-modularidad.md`.
4. Si en cambio existe una clase tipo `HistorialRepository` o `AnalysisRepository` que es la única que toca la tabla, y el endpoint solo le pasa el resultado ya calculado, entonces esta tabla ya refleja la realidad del código y solo hay que dejar constancia de eso.
