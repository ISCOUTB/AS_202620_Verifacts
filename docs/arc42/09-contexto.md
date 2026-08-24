# C4 — Contexto de VeriFacts

## Descripción

El diagrama presenta VeriFacts dentro de su entorno y muestra las personas y
sistemas externos que interactúan con el sistema.

## Diagrama

```mermaid
flowchart LR

    U[Usuario]
    V[VeriFacts]
    W[Sitio web externo]
    G[GitHub]
    S[SonarCloud]

    U -->|Introduce texto o URL| V
    V -->|Solicita contenido| W
    W -->|Devuelve contenido| V

    G -->|Almacena código y cambios| S
