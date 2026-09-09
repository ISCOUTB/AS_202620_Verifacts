from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router


app = FastAPI(title="Verifacts API")

# Habilita el frontend (Vite, puerto 5173 por defecto) para consumir la API
# desde el navegador. Sin este middleware el navegador bloquea las
# respuestas por política de mismo origen (CORS), aunque el backend
# responda correctamente.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
