# C4 — Nivel 1: Contexto de VeriFacts

## Descripción

El diagrama presenta VeriFacts dentro de su entorno y muestra las personas y
sistemas externos que interactúan con el sistema.

## Diagrama

```mermaid
flowchart LR
    U[Usuario<br/>persona]
    V[VeriFacts<br/>sistema de software]
    W[Sitio web externo<br/>sistema externo]
    G[GitHub<br/>sistema externo]
    S[SonarCloud<br/>sistema externo]

    U -->|Introduce texto o URL,<br/>consulta el resultado| V
    V -->|Solicita contenido| W
    W -->|Devuelve contenido| V
    G -->|Ejecuta análisis de calidad de código| S
    G -->|Aloja el código fuente de| V
```

## Elementos

| Elemento | Tipo | Descripción |
|---|---|---|
| Usuario | Persona | Introduce texto o una URL y consulta el resultado del análisis |
| VeriFacts | Sistema de software (este sistema) | Analiza contenidos digitales y genera indicadores de posible desinformación |
| Sitio web externo | Sistema externo | Origen del contenido cuando el usuario proporciona una URL |
| GitHub | Sistema externo | Aloja el código fuente y ejecuta GitHub Actions |
| SonarCloud | Sistema externo | Analiza la calidad del código del repositorio |

Ver también el diagrama de Nivel 2: [C4 — Contenedores](02-contenedores.md).
