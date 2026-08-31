from fastapi import FastAPI

from app.api.routes import router
from app.persistence.repository import initialize_database


app = FastAPI(
    title="VeriFacts",
    description="Sistema de análisis de información digital",
    version="0.2.0",
)


initialize_database()

app.include_router(router)
