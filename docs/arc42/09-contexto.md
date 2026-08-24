# C4 — Contexto de VeriFacts
## Descripción

El diagrama de contexto identifica a VeriFacts como sistema principal y
muestra los actores y sistemas externos que interactúan con él.

## Diagrama

flowchart LR

    U[Usuario]
    V[VeriFacts]
    W[Sitio web externo]
    G[GitHub]
    S[SonarCloud]

    U -->|Introduce texto o URL| V
    V -->|Solicita contenido| W
    W -->|Devuelve contenido| V

    G -->|Almacena código y cambios| V
    G -->|Envía código para análisis| S
    S -->|Devuelve resultados de calidad| G
