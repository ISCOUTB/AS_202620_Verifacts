# Prototipo serverless — comparación Render vs. AWS Lambda

Este prototipo existe únicamente para medir el arranque en frío de la API
de VeriFacts en AWS Lambda, como evidencia del reto de corte. **No se
despliega a una cuenta real de AWS** — toda la medición se hace localmente
con `sam local invoke`.

Contexto completo, resultados y decisión:
[docs/adr/0005-comparacion-lambda-render.md](../docs/adr/0005-comparacion-lambda-render.md)

## Reproducir la medición

```bash
cd serverless-prototype
Copy-Item -Recurse ..\app .\app
sam build --use-container
python medir_cold_start.py --runs 15
```

Requiere: AWS SAM CLI, Docker Desktop corriendo, Python 3.