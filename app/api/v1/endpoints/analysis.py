from fastapi import APIRouter, HTTPException 
from pydantic import BaseModel 
from app.persistence.repository import create_analysis, get_analysis 
 
router = APIRouter() 
 
class AnalysisRequest(BaseModel): 
    text: str 
 
@router.post("/analysis") 
async def create_analysis_endpoint(request: AnalysisRequest): 
    result = create_analysis(request.text) 
    return result 
 
@router.get("/analysis/{analysis_id}") 
async def get_analysis_endpoint(analysis_id: int): 
    result = get_analysis(analysis_id) 
    if result is None: 
        raise HTTPException(status_code=404, detail="An lisis no encontrado") 
    return result 
