from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.modules.analysis.service import analyze_content
from app.modules.content.service import normalize_content
from app.modules.scoring.service import calculate_score, classify_score
from app.persistence.repository import save_analysis


router = APIRouter()


class AnalysisRequest(BaseModel):
    text: str


class AnalysisResponse(BaseModel):
    id: int
    score: int
    classification: str
    factors: list[str]


@router.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/analysis", response_model=AnalysisResponse)
def create_analysis(request: AnalysisRequest) -> AnalysisResponse:
    try:
        content = normalize_content(request.text)
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    findings = analyze_content(content)

    score = calculate_score(findings)
    classification = classify_score(score)

    factors = [
        finding.indicator
        for finding in findings
    ]

    analysis_id = save_analysis(
        content=content,
        score=score,
        classification=classification,
        factors=factors,
    )

    return AnalysisResponse(
        id=analysis_id,
        score=score,
        classification=classification,
        factors=factors,
    )
