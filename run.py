from fastapi import FastAPI
import uvicorn

from app.api.routes import router
from app.persistence.repository import initialize_database


app = FastAPI(
    title="VeriFacts",
    description="Sistema de análisis de información digital",
    version="0.2.0",
)


initialize_database()

app.include_router(router)


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=False,
    )
