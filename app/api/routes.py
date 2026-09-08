from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, model_validator

from app.modules.analysis.service import analyze_content
from app.modules.content.service import extract_from_url, normalize_content
from app.modules.scoring.service import calculate_score, classify_score
from app.persistence.repository import get_analysis, list_analyses, save_analysis


router = APIRouter()


class AnalysisRequest(BaseModel):
    text: str | None = None
    url: str | None = None

    @model_validator(mode="after")
    def check_text_or_url(self) -> "AnalysisRequest":
        if not self.text and not self.url:
            raise ValueError("Debe proporcionar 'text' o 'url'.")

        if self.text and self.url:
            raise ValueError("Proporcione solo uno: 'text' o 'url', no ambos.")

        return self


class AnalysisResponse(BaseModel):
    id: int
    score: int
    classification: str
    factors: list[str]
    source_type: str


class AnalysisSummary(BaseModel):
    id: int
    content: str
    score: int
    classification: str
    factors: list[str]
    source_type: str
    created_at: str


def _to_summary(stored: dict) -> AnalysisSummary:
    return AnalysisSummary(
        id=stored["id"],
        content=stored["content"],
        score=stored["score"],
        classification=stored["classification"],
        factors=stored["factors"],
        source_type=stored["source_type"],
        created_at=stored["created_at"],
    )


@router.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/analysis", response_model=AnalysisResponse)
def create_analysis(request: AnalysisRequest) -> AnalysisResponse:
    if request.url:
        try:
            raw_content = extract_from_url(request.url)
        except ValueError as error:
            raise HTTPException(status_code=400, detail=str(error)) from error
        source_type = "url"
    else:
        raw_content = request.text
        source_type = "texto"

    try:
        content = normalize_content(raw_content)
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
        source_type=source_type,
    )

    return AnalysisResponse(
        id=analysis_id,
        score=score,
        classification=classification,
        factors=factors,
        source_type=source_type,
    )


@router.get("/analysis/{analysis_id}", response_model=AnalysisSummary)
def read_analysis(analysis_id: int) -> AnalysisSummary:
    stored = get_analysis(analysis_id)

    if stored is None:
        raise HTTPException(status_code=404, detail="Análisis no encontrado.")

    return _to_summary(stored)


@router.get("/analysis", response_model=list[AnalysisSummary])
def list_analysis(limit: int = 20, offset: int = 0) -> list[AnalysisSummary]:
    if limit < 1 or limit > 100:
        raise HTTPException(
            status_code=400, detail="limit debe estar entre 1 y 100."
        )

    if offset < 0:
        raise HTTPException(status_code=400, detail="offset no puede ser negativo.")

    rows = list_analyses(limit=limit, offset=offset)

    return [_to_summary(row) for row in rows]
