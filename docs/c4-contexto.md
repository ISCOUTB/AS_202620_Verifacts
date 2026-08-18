 C4 — Diagrama de Contexto

## Descripción

El diagrama de contexto presenta a VeriFact como un sistema dentro de su entorno y muestra sus principales usuarios y sistemas externos.

## Actores y sistemas externos

### Usuario

Persona que utiliza VeriFact para analizar un texto o una URL y consultar el resultado.

### Sitio web externo

Página o sitio desde el cual VeriFact puede obtener contenido cuando el usuario proporciona una URL.

### GitHub

Sistema externo utilizado por el equipo para almacenar el código fuente, gestionar cambios y colaborar durante el desarrollo.

### SonarCloud

Sistema externo utilizado para analizar la calidad del código del proyecto.

---

## Diagrama

```mermaid
flowchart LR

    U[Usuario]
    V[VeriFact]
    W[Sitio web externo]
    G[GitHub]
    S[SonarCloud]

    U -->|Introduce texto o URL / consulta resultados| V

    V -->|Solicita contenido| W
    W -->|Devuelve contenido| V

    G -->|Código y cambios| V
    V -->|Integración de desarrollo| G

    G -->|Código fuente| S
    S -->|Resultados de calidad| G
