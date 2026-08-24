from fastapi import FastAPI

from app.api.routes import router


app = FastAPI(
    title="VeriFacts",
    description="Sistema de análisis de información digital",
    version="0.1.0",
)

app.include_router(router)
