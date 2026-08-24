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
| GitHub Actions | Ejecuta las pruebas automatizadas en cada push |
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
- GitHub / GitHub Actions.
- SonarCloud.
- Verificación humana de hechos.

---

## 3.5 Contexto técnico

El usuario interactúa con VeriFacts mediante la interfaz.

El contenido puede introducirse directamente o mediante una URL. El sistema
procesa el contenido y genera el resultado.

```text
Usuario
   |
   | Introduce texto o URL
   v
VeriFacts
   |
   | Solicita contenido (si es una URL)
   v
Sitio web externo
```

El diagrama equivalente en notación C4 (Nivel 1 — Contexto) se encuentra en
[C4 — Contexto](../c4/01-contexto.md).

---

## 3.6 Alcance de este incremento

Este incremento documenta y ejecuta el corte vertical descrito en el
[README](../../README.md#corte-vertical-ejecutable): recepción de una
solicitud HTTP a través del módulo `API` y respuesta de disponibilidad
(`/health`). Los módulos `Content`, `Analysis` y `Scoring` están definidos
arquitectónicamente (ver [Sección 5 — Vista de bloques](05-vista-de-bloques.md))
pero aún no contienen lógica de negocio.
