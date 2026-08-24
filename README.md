# VeriFacts

## Sistema inteligente para análisis de información digital

**Asignatura:** Arquitectura de Software
**Proyecto:** VeriFacts
**Organización:** ISCOUTB
**Repositorio:** https://github.com/ISCOUTB/AS_202620_Verifacts

## Integrantes

* Pedro Jose Castro Blanquicett
* Cristian Cardeno

---

# 1. Descripción del proyecto

VeriFacts es una aplicación orientada al análisis de contenidos digitales para identificar indicadores asociados a posibles casos de desinformación.

El usuario podrá introducir un texto o una URL y obtener un resultado compuesto por una puntuación de riesgo, una clasificación y una explicación de los factores detectados.

VeriFacts no pretende determinar de manera absoluta si una información es verdadera o falsa. El objetivo es proporcionar indicadores que ayuden al usuario a realizar una evaluación inicial y crítica del contenido.

---

# 2. Problema

La circulación masiva de información en Internet dificulta que los usuarios puedan determinar rápidamente la confiabilidad de determinados contenidos.

Algunas publicaciones pueden presentar lenguaje sensacionalista, afirmaciones absolutas, ausencia de fuentes verificables u otras características que dificultan su evaluación.

La verificación manual requiere consultar diferentes fuentes y analizar el contenido, lo cual puede consumir tiempo.

VeriFacts busca automatizar una parte de esta evaluación mediante diferentes mecanismos de análisis.

---

# 3. Objetivo

Diseñar e implementar una aplicación web modular capaz de analizar contenidos digitales, identificar indicadores asociados a posibles casos de desinformación y presentar un resultado interpretable acompañado de una explicación.

---

# 4. Estado actual

El proyecto se encuentra actualmente en la etapa de diseño y validación de la arquitectura.

La arquitectura seleccionada es un **monolito modular**.

El repositorio contiene un esqueleto ejecutable de la aplicación, pero todavía no contiene la lógica completa del análisis de desinformación.

Actualmente se puede:

* iniciar la aplicación;
* comprobar que la API está disponible;
* ejecutar una prueba automatizada;
* validar la estructura inicial de los módulos.

---

# 5. Arquitectura

## Estilo arquitectónico

Se seleccionó **monolito modular** después de comparar:

* arquitectura por capas;
* arquitectura hexagonal;
* monolito modular.

La decisión está registrada en:

[ADR-0001 — Usar monolito modular](docs/adr/0001-estilo-arquitectonico.md)

## Módulos iniciales

```text
VeriFacts
│
├── API
│
├── Content
│
├── Analysis
│
└── Scoring
```

### API

Recibe y coordina las solicitudes externas.

### Content

Se encargará de representar y procesar el contenido recibido mediante texto o URL.

### Analysis

Contendrá los mecanismos de análisis, inicialmente basados en reglas y posteriormente ampliables con técnicas de procesamiento de lenguaje natural o Machine Learning.

### Scoring

Se encargará de transformar los resultados del análisis en una puntuación y clasificación.

---

# 6. Documentación arquitectónica

## arc42

* [Sección 1 — Introducción y objetivos](docs/arc42/01-introduccion-y-objetivos.md)
* [Sección 2 — Restricciones](docs/arc42/02-restricciones.md)
* [Sección 3 — Contexto y alcance](docs/arc42/03-contexto-y-alcance.md)
* [Sección 4 — Estrategia de solución](docs/arc42/04-estrategia-de-solucion.md)

## Calidad

* [Escenarios de calidad](docs/escenarios-de-calidad.md)
* [Árbol de utilidad](docs/arbol_utilidad.md)
* [Aspectos arquitectónicos](docs/aspectos.md)
* [Restricciones](docs/restricciones.md)
* [Matriz comparativa de estilos](docs/matriz-estilos.md)

## Contexto

* [C4 — Contexto](docs/c4/contexto.md)

## Decisiones arquitectónicas

* [ADR-0001 — Usar monolito modular](docs/adr/0001-estilo-arquitectonico.md)

## Inteligencia Artificial

* [Registro de uso de IA](docs/ia.md)

## Información del equipo

* [Equipo](EQUIPOS.md)

---

# 7. Estructura del repositorio

```text
AS_202620_Verifacts/
│
├── README.md
├── EQUIPOS.md
├── requirements.txt
├── run.py
│
├── .github/
│   └── workflows/
│       └── tests.yml
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py
│   │
│   └── modules/
│       ├── __init__.py
│       ├── analysis/
│       ├── content/
│       └── scoring/
│
├── tests/
│   ├── __init__.py
│   └── test_health.py
│
└── docs/
    ├── arc42/
    ├── c4/
    ├── adr/
    ├── escenarios-de-calidad.md
    ├── arbol_utilidad.md
    ├── aspectos.md
    ├── restricciones.md
    └── ia.md
```

---

# 8. Tecnologías actuales

## Backend y esqueleto ejecutable

* Python 3.11+
* FastAPI
* Uvicorn

## Pruebas

* Pytest
* HTTPX

## Calidad y colaboración

* Git
* GitHub
* GitHub Actions
* SonarCloud

## Tecnologías previstas para etapas posteriores

* React
* TypeScript
* SQLite
* SQLAlchemy
* spaCy
* scikit-learn

Estas últimas se incorporarán progresivamente cuando se implemente la lógica funcional.

---

# 9. Requisitos para ejecutar el proyecto

Se necesita:

* Python 3.11 o superior.
* Git.
* Acceso al repositorio.

---

# 10. Clonar el repositorio

Desde una terminal:

```bash
git clone https://github.com/ISCOUTB/AS_202620_Verifacts.git
cd AS_202620_Verifacts
```

---

# 11. Crear el entorno virtual

## Windows

```bash
python -m venv .venv
```

Activarlo:

```bash
.venv\Scripts\activate
```

## Linux / macOS

```bash
python3 -m venv .venv
```

Activarlo:

```bash
source .venv/bin/activate
```

---

# 12. Instalar dependencias

Con el entorno virtual activado:

```bash
pip install -r requirements.txt
```

---

# 13. Arranque del proyecto

El proyecto se inicia con **un único comando**:

```bash
python run.py
```

Esta es la instrucción oficial de arranque del esqueleto ejecutable.

Una vez iniciado, la aplicación estará disponible en:

```text
http://127.0.0.1:8000
```

La documentación automática de FastAPI estará disponible en:

```text
http://127.0.0.1:8000/docs
```

---

# 14. Comprobación de funcionamiento

La aplicación incluye un endpoint técnico de comprobación:

```text
GET /health
```

Con el servidor ejecutándose, abrir:

```text
http://127.0.0.1:8000/health
```

La respuesta esperada es:

```json
{
  "status": "ok"
}
```

Esta ruta solamente verifica que el esqueleto ejecutable está funcionando.

No representa todavía una funcionalidad de negocio de VeriFacts.

---

# 15. Ejecutar las pruebas

Con el servidor detenido o en otra terminal, ejecutar:

```bash
pytest -q
```

La prueba actual comprueba que:

1. La aplicación puede inicializarse.
2. La ruta `/health` existe.
3. La respuesta HTTP es correcta.
4. El contenido de la respuesta coincide con el esperado.

El resultado esperado es similar a:

```text
1 passed
```

---

# 16. Integración continua

El repositorio incluye:

```text
.github/workflows/tests.yml
```

GitHub Actions ejecutará automáticamente las pruebas cuando se realice un `push` o un `pull request`.

El flujo es:

```text
Push
  ↓
GitHub Actions
  ↓
Instalar dependencias
  ↓
Ejecutar pytest
  ↓
✓ Tests
```

El resultado puede consultarse desde la pestaña **Actions** del repositorio.

---

# 17. Desarrollo actual

El esqueleto actual contiene únicamente la estructura necesaria para comenzar
el desarrollo de la arquitectura.

No se ha implementado todavía la lógica completa de:

* análisis de contenido;
* extracción de URL;
* reglas de detección;
* puntuación;
* NLP;
* Machine Learning;
* persistencia de resultados;
* interfaz final.

Estas funcionalidades se implementarán posteriormente dentro de las fronteras
arquitectónicas ya definidas.

---

# 18. Principios arquitectónicos

La implementación seguirá los siguientes criterios:

### Modularidad

Cada módulo tendrá responsabilidades claramente delimitadas.

### Bajo acoplamiento

Se evitarán dependencias innecesarias entre módulos.

### Alta cohesión

Las responsabilidades relacionadas se mantendrán juntas.

### Encapsulación de la variación

Los mecanismos que puedan cambiar, como las reglas de análisis, se mantendrán
aislados.

### Evolución gradual

La arquitectura debe permitir incorporar nuevos mecanismos de análisis sin
modificar innecesariamente los demás componentes.

---

# 19. Estado de la línea base

## Arquitectura

* [x] Comparación de estilos.
* [x] Monolito modular seleccionado.
* [x] ADR-0001.
* [x] arc42 secciones 1–4.
* [x] Árbol de utilidad.
* [x] Escenarios de calidad.
* [x] Matriz comparativa.
* [x] C4 de contexto.
* [x] Restricciones arquitectónicas.
* [x] Registro de uso de IA.

## Esqueleto

* [x] Aplicación FastAPI.
* [x] Estructura modular.
* [x] Endpoint `/health`.
* [x] Prueba automatizada.
* [x] Comando único de arranque.
* [x] GitHub Actions.

## Pendiente

* [ ] Implementar análisis de texto.
* [ ] Implementar análisis mediante URL.
* [ ] Implementar Rule Engine.
* [ ] Implementar Scoring Engine.
* [ ] Integrar procesamiento NLP.
* [ ] Evaluar Machine Learning.
* [ ] Implementar persistencia.
* [ ] Desarrollar frontend.
* [ ] Integrar el prototipo completo.

---

# 20. Repositorio

Repositorio oficial:

https://github.com/ISCOUTB/AS_202620_Verifacts

**Proyecto:** VeriFacts
**Equipo:** Pedro Jose Castro Blanquicett, Cristian Cardeno 

