from fastapi import FastAPI 
from app.api.v1.endpoints import analysis 
 
app = FastAPI(title="Verifacts API") 
app.include_router(analysis.router) 
 
@app.get("/health") 
async def health_check(): 
    return {"status": "ok"} 
