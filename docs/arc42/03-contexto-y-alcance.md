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




---

# 8. `docs/arc42/04-estrategia-de-solucion.md`

Esta es una de las correcciones **más importantes de S3**.

El problema actual es que tenían "alta cohesión", "bajo acoplamiento", etc., pero eso son principios generales, no tácticas concretas asociadas a Q-01…Q-05.

Reemplaza el contenido completo por:

```markdown
# arc42 — Sección 4: Estrategia de solución

## 4.1 Estilo arquitectónico seleccionado

VeriFacts utilizará un **monolito modular**.

La aplicación se ejecutará como una única unidad, pero estará organizada
internamente mediante módulos con responsabilidades claramente delimitadas.

Los módulos iniciales son:

- API.
- Content.
- Analysis.
- Scoring.

La elección busca equilibrar evolución, mantenibilidad, rendimiento y
simplicidad de operación.

---

## 4.2 Relación entre escenarios y tácticas

Las tácticas se seleccionan a partir de los escenarios de calidad definidos en:

[Escenarios de calidad](../escenarios-de-calidad.md)

| Escenario | Atributo | Táctica | Aplicación | Costo aceptado |
|---|---|---|---|---|
| [Q-01](../escenarios-de-calidad.md#q-01-tiempo-de-respuesta-del-análisis) | Rendimiento | Control de tamaño de entrada + medición P95 | Se limita inicialmente el contenido a 10.000 caracteres y se mide el tiempo de análisis | Algunos contenidos grandes deberán procesarse posteriormente o dividirse |
| [Q-02](../escenarios-de-calidad.md#q-02-incorporación-de-un-nuevo-analizador) | Escalabilidad | Encapsulación de variación / Strategy | Los analizadores comparten un contrato común dentro de `Analysis` | Se introduce una abstracción adicional |
| [Q-03](../escenarios-de-calidad.md#q-03-modificación-de-una-regla) | Mantenibilidad | Encapsulación de la variación | Cada regla de análisis estará aislada de las demás | Mayor cantidad de archivos y módulos |
| [Q-04](../escenarios-de-calidad.md#q-04-comprensión-del-resultado) | Usabilidad | Presentación progresiva | El resultado principal se presenta antes de los detalles | Requiere más diseño de interfaz |
| [Q-05](../escenarios-de-calidad.md#q-05-repetibilidad-del-resultado) | Confiabilidad | Pipeline determinista | Una misma entrada y configuración producen el mismo resultado | Se limitan inicialmente fuentes externas no deterministas |

---

## 4.3 Q-01 — Rendimiento

### Táctica

Se utilizará un límite inicial de tamaño para el contenido y se medirá el tiempo
de procesamiento utilizando P95.

### Aplicación

Los textos superiores al límite inicial no entrarán directamente al pipeline
completo.

La métrica principal será:

**P95 ≤ 3 segundos.**

### Costo

Un límite de entrada puede impedir procesar contenidos demasiado grandes en
una sola operación.

---

## 4.4 Q-02 — Escalabilidad

### Táctica

Se utilizará encapsulación de variación mediante un contrato común para los
analizadores.

Conceptualmente:

```text
Analysis
|
+-- Analyzer
|
+-- RuleAnalyzer
+-- NLPAnalyzer
+-- MLAnalyzer
