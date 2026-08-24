# arc42 — Sección 3: Contexto y alcance

## 3.1 Contexto de negocio

VeriFacts se encuentra dentro del contexto de consumo y evaluación de
información digital.

El usuario proporciona un contenido que desea analizar y recibe indicadores
que pueden ayudarle a determinar si necesita realizar una revisión adicional.

---

## 3.2 Actores

| Actor | Interacción con VeriFacts |
|---|---|
| Usuario final | Introduce texto o URL y consulta el resultado |
| Estudiante | Utiliza el sistema como apoyo para evaluar contenidos |
| Docente | Utiliza el sistema como recurso educativo |
| Analista | Utiliza el resultado como señal para priorizar revisión |

---

## 3.3 Sistemas externos

| Sistema externo | Relación |
|---|---|
| Sitio web externo | Puede proporcionar contenido cuando el usuario introduce una URL |
| GitHub | Gestiona el código y la colaboración del equipo |
| SonarCloud | Analiza la calidad del código durante el desarrollo |

---

## 3.4 Límites del sistema

### Dentro de VeriFacts

- Interfaz.
- API.
- Recepción de contenido.
- Extracción de contenido.
- Análisis.
- Puntuación.
- Persistencia.

### Fuera de VeriFacts

- Sitios web consultados.
- GitHub.
- SonarCloud.
- Procesos humanos de verificación de hechos.

---

## 3.5 Contexto técnico

El usuario interactúa con VeriFacts mediante la interfaz web.

La aplicación recibe directamente el texto o utiliza una URL para obtener
contenido externo.

Posteriormente el contenido es procesado por los mecanismos de análisis y se
genera un resultado.

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
