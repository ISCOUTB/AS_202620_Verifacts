from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.modules.analysis.service import analyze_content
from app.modules.content.service import normalize_content
from app.modules.scoring.service import calculate_score, classify_score
from app.persistence.repository import (
    count_analyses,
    get_analysis,
    list_analyses,
    save_analysis,
)


router = APIRouter()


class AnalysisRequest(BaseModel):
    text: str


class AnalysisResponse(BaseModel):
    id: int
    score: int
    classification: str
    factors: list[str]
    created_at: str | None = None


class AnalysisSummary(BaseModel):
    id: int
    content: str
    score: int
    classification: str
    factors: list[str]
    created_at: str | None = None


class AnalysisListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    items: list[AnalysisSummary]


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

    stored = get_analysis(analysis_id)
    created_at = stored["created_at"] if stored else None

    return AnalysisResponse(
        id=analysis_id,
        score=score,
        classification=classification,
        factors=factors,
        created_at=created_at,
    )


@router.get("/analysis/{analysis_id}", response_model=AnalysisSummary)
def read_analysis(analysis_id: int) -> AnalysisSummary:
    result = get_analysis(analysis_id)

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Análisis no encontrado.",
        )

    return AnalysisSummary(**result)


@router.get("/analysis", response_model=AnalysisListResponse)
def read_analyses(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> AnalysisListResponse:
    items = list_analyses(limit=limit, offset=offset)
    total = count_analyses()

    return AnalysisListResponse(
        total=total,
        limit=limit,
        offset=offset,
        items=[AnalysisSummary(**item) for item in items],
    )
