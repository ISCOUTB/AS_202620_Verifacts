# arc42 — Sección 7: Despliegue

## 7.1 Infraestructura actual

VeriFacts, en este incremento, se despliega **localmente**: no existe un
entorno de producción ni infraestructura cloud (ver restricción
[R-TEC-01](02-restricciones.md)).

```text
┌─────────────────────── Máquina local del desarrollador ───────────────────┐
│                                                                             │
│   ┌──────────────────────────┐        ┌──────────────────────────────┐    │
│   │ Proceso Python            │       │ Archivo data/verifacts.db     │    │
│   │ (uvicorn / app.main:app)  │──────▶│ (SQLite)                      │    │
│   │ Puerto 127.0.0.1:8000     │        └──────────────────────────────┘    │
│   └──────────────────────────┘                                             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

Un único proceso (arrancado con `python run.py`, ver
[README](../../README.md#corte-vertical-ejecutable)) sirve la API HTTP y lee/
escribe el archivo SQLite en `data/verifacts.db`. No hay balanceo de carga,
réplicas ni contenedores de infraestructura (Docker, Kubernetes) en este
incremento.

## 7.2 Infraestructura de integración continua

GitHub Actions ejecuta las pruebas automatizadas en cada `push` y `pull
request`, definido en `.github/workflows/tests.yml`:

```text
Push / PR
   │
   ▼
GitHub Actions (runner ubuntu-latest)
   │
   ├─ Checkout del repositorio
   ├─ Configurar Python 3.11
   ├─ pip install -r requirements.txt
   └─ python -m pytest -q
```

El resultado de cada ejecución es consultable desde la pestaña **Actions**
del repositorio; la evidencia de la corrida más reciente en verde se cita en
la [tabla de aspectos](../aspectos.md).

## 7.3 Despliegue previsto (fuera del alcance actual)

El contenedor de interfaz web (React) y una eventual migración de SQLite a
un motor con soporte de concurrencia (por ejemplo PostgreSQL) forman parte
de la arquitectura objetivo, pero no de este incremento — ver
[C4 — Contenedores](../c4/02-contenedores.md) y
[Sección 9 — Decisiones pendientes de registrar](09-decisiones-arquitectonicas.md#próximas-decisiones-pendientes-de-registrar).
