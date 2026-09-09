from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, model_validator

from app.modules.analysis.service import analyze_content
from app.modules.content import service as content_service
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
    text: str | None = None
    url: str | None = None

    @model_validator(mode="after")
    def validate_text_or_url(self) -> "AnalysisRequest":
        if self.text is not None and self.url is not None:
            raise ValueError("No se pueden proporcionar texto y URL al mismo tiempo.")
        if self.text is None and self.url is None:
            raise ValueError("Debe proporcionar texto o una URL.")
        return self


class AnalysisResponse(BaseModel):
    id: int
    score: int
    classification: str
    factors: list[str]
    source_type: str
    created_at: str | None = None


class AnalysisSummary(BaseModel):
    id: int
    content: str
    score: int
    classification: str
    factors: list[str]
    source_type: str
    created_at: str | None = None


@router.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/analysis", response_model=AnalysisResponse)
def create_analysis(request: AnalysisRequest) -> AnalysisResponse:
    source_type = "texto"
    raw_content = ""

    if request.url is not None:
        source_type = "url"
        html = content_service.trafilatura.fetch_url(request.url)
        if not html:
            raise HTTPException(
                status_code=400,
                detail="No se pudo descargar la URL.",
            )
        extracted = content_service.trafilatura.extract(html)
        if not extracted:
            raise HTTPException(
                status_code=400,
                detail="No se pudo extraer contenido de la URL.",
            )
        raw_content = extracted
    else:
        raw_content = request.text  # type: ignore[assignment]

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

    stored = get_analysis(analysis_id)
    created_at = stored["created_at"] if stored else None
    st_type = stored.get("source_type", source_type) if stored else source_type

    return AnalysisResponse(
        id=analysis_id,
        score=score,
        classification=classification,
        factors=factors,
        source_type=st_type,
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


@router.get("/analysis", response_model=list[AnalysisSummary])
def read_analyses(
    limit: int = Query(default=20),
    offset: int = Query(default=0),
) -> list[AnalysisSummary]:
    if limit < 1:
        raise HTTPException(
            status_code=400,
            detail="El límite debe ser mayor o igual a 1.",
        )
    if offset < 0:
        raise HTTPException(
            status_code=400,
            detail="El desplazamiento debe ser mayor o igual a 0.",
        )

    items = list_analyses(limit=limit, offset=offset)

    return [AnalysisSummary(**item) for item in items]
