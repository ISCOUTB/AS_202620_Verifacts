# ADR-0002: Mantener los tres contextos delimitados sin cambios tras el corte 1

- Estado: Aceptado
- Fecha: 2026-09-11
- Decisor: Equipo VeriFacts

## Contexto

Tras el corte 1 se incorporó soporte de URL (`trafilatura`), `MLAnalyzer` y
el frontend React. Esto amplió el código dentro de Análisis de Contenido y
agregó un contenedor nuevo (Interfaz web), ya documentado en
[docs/c4/02-contenedores.md](../c4/02-contenedores.md).

## Decisión

No se crean nuevos contextos delimitados. Ingesta y Presentación, Análisis
de Contenido e Historial de Análisis (ver
[docs/mapa-contextos.md](../mapa-contextos.md)) siguen siendo los tres
límites del dominio; los cambios fueron de implementación interna, no de
fronteras.

## Consecuencias

`docs/c4/03-componentes.md` refleja la correspondencia real con el código
sin requerir un cuarto contexto. Si en el futuro el frontend necesita lógica
de negocio propia (no solo presentación), este ADR deja de aplicar y debe
reemplazarse por uno nuevo.

## Commit de implementación

Esta decisión documenta el estado del mapa de contextos tras la
incorporación del frontend (`frontend/`) y del soporte de URL. Ver
[docs/mapa-contextos.md](../mapa-contextos.md) y el historial de commits en
[github.com/ISCOUTB/AS_202620_Verifacts/commits/master](https://github.com/ISCOUTB/AS_202620_Verifacts/commits/master).

## Enmienda (2026-10-07)

Nota aclaratoria: La referencia en la sección de Contexto a `MLAnalyzer`
describía una propuesta de analizador que finalmente **no fue implementada en
el repositorio** (ver [docs/auditoria-s9.md](../auditoria-s9.md), hallazgo D-1).
El motor de análisis se mantiene exclusivamente con `RuleAnalyzer` determinista
([ADR-0006](0006-semantica-del-resultado.md)) y sin componentes generativos
([ADR-0007](0007-no-incorporar-componente-generativo.md)).

