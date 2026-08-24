# arc42 — Sección 3: Contexto y alcance

## 3.1 Contexto de negocio

VeriFacts se encuentra dentro del contexto de consumo y evaluación de
información digital.

El usuario proporciona un contenido que desea analizar y recibe indicadores
que pueden ayudarle a determinar si necesita realizar una revisión adicional.

---

## 3.2 Actores

| Actor | Interacción |
|---|---|
| Usuario final | Introduce texto o URL y consulta el resultado |
| Estudiante | Utiliza el sistema como apoyo para evaluar contenidos |
| Docente | Utiliza el sistema como recurso educativo |
| Analista | Utiliza el resultado como señal para priorizar revisión |

---

## 3.3 Sistemas externos

| Sistema | Interacción |
|---|---|
| Sitio web externo | Proporciona contenido cuando se analiza una URL |
| GitHub | Gestiona código fuente y colaboración |
| SonarCloud | Analiza la calidad del código |

---

## 3.4 Límites del sistema

### Dentro de VeriFacts

- Interfaz.
- API.
- Recepción de contenido.
- Extracción.
- Análisis.
- Puntuación.
- Persistencia.

### Fuera de VeriFacts

- Sitios web externos.
- GitHub.
- SonarCloud.
- Verificación humana de hechos.

---

## 3.5 Contexto técnico

El usuario interactúa con VeriFacts mediante la interfaz.

El contenido puede introducirse directamente o mediante una URL.

El sistema procesa el contenido y genera el resultado.

```text
Usuario
   |
   | Introduce texto o URL
   v
VeriFacts
   |
   | Solicita contenido
   v
Sitio web externo
