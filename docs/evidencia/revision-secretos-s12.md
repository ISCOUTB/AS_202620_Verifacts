# Revisión de secretos en el repositorio y su historial (S12)

- Fecha: 2026-10-20
- Alcance: **todo el historial**, 327 commits en todas las ramas, sobre el commit `3544894`.
- Método: búsqueda por patrones sobre el contenido agregado en cada commit (`git log --all -p`), sin
  limitarse a la punta de `master`.

## Comandos

```cmd
git rev-list --all --count

git log --all --name-only --pretty=format: | sort -u

git log --all -p --no-color -G"(ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|AKIA[0-9A-Z]{16}|sk-[A-Za-z0-9]{20,}|xox[baprs]-[A-Za-z0-9-]{10,}|-----BEGIN [A-Z ]*PRIVATE KEY-----)"
```

Además, una búsqueda de asignaciones literales de `password`, `secret`, `api_key` y `token` con un
valor entre comillas en las líneas añadidas.

## Resultados

| Comprobación | Resultado |
|---|---|
| Tokens de GitHub, claves de AWS, claves tipo `sk-`, tokens de Slack y claves privadas en el contenido | Sin coincidencias en los 327 commits |
| Asignaciones literales de `password`, `secret`, `api_key` o `token` | Sin coincidencias |
| `SONAR_TOKEN` | Solo se referencia como `${{ secrets.SONAR_TOKEN }}` en `sonarcloud.yml`; no hay valor en el repositorio |
| Archivos sensibles alguna vez versionados | `.env.example` y `frontend/.env.example` (plantillas sin valores reales) y `data/verifacts.db` |
| `data/verifacts.db` | Base local de pruebas que se versionó entre el 2026-09-01 y el 2026-09-09 y ya no está en el árbol (`git ls-files data` solo lista `data/.gitkeep`); `.gitignore` ignora `data/` y `*.db`. Su contenido son análisis de prueba: no contiene cadenas de credenciales |

## Controles vigentes

- `.gitignore` ignora `.env`, `.env.*` (salvo `.env.example`), `*.pem`, `*.key`, `data/` y `*.db`.
- Los secretos del pipeline (`SONAR_TOKEN`) viven en los *secrets* de GitHub.
- Las variables del despliegue en Dokploy (`LOG_LEVEL`, `ALLOWED_ORIGINS`) no son secretos.

## Límites de esta revisión

Es una búsqueda por patrones: no detecta un secreto con un formato desconocido. No se ejecutó una
herramienta especializada (por ejemplo `gitleaks`); si el equipo la ejecuta, debe registrar aquí la
versión y el resultado. Las credenciales de acceso a servicios externos que alguien comparta por
fuera del repositorio (chats, capturas) deben rotarse.
