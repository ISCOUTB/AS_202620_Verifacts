from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel, model_validator

from app.modules.analysis.service import analyze_content
from app.modules.content.service import extract_from_url, normalize_content
from app.modules.scoring.service import calculate_score, classify_score
from app.persistence.repository import (
    count_analyses,
    get_analysis,
    list_analyses,
    save_analysis,
)


router = APIRouter()

MIN_LIMIT = 1
MAX_LIMIT = 100


class AnalysisRequest(BaseModel):
    text: str | None = None
    url: str | None = None

    @model_validator(mode="after")
    def check_exactly_one_source(self) -> "AnalysisRequest":
        has_text = bool(self.text and self.text.strip())
        has_url = bool(self.url and self.url.strip())

        if has_text and has_url:
            raise ValueError("Envía solo 'text' o solo 'url', no ambos.")
        if not has_text and not has_url:
            raise ValueError("Debes enviar 'text' o 'url'.")

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
    if request.url:
        source_type = "url"
        try:
            raw_content = extract_from_url(request.url)
        except ValueError as error:
            raise HTTPException(
                status_code=400,
                detail=str(error),
            ) from error
    else:
        source_type = "texto"
        raw_content = request.text or ""

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

    return AnalysisResponse(
        id=analysis_id,
        score=score,
        classification=classification,
        factors=factors,
        source_type=source_type,
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
    response: Response,
    limit: int = 20,
    offset: int = 0,
) -> list[AnalysisSummary]:
    if limit < MIN_LIMIT or limit > MAX_LIMIT:
        raise HTTPException(
            status_code=400,
            detail=f"El límite debe estar entre {MIN_LIMIT} y {MAX_LIMIT}.",
        )
    if offset < 0:
        raise HTTPException(
            status_code=400,
            detail="El desplazamiento debe ser mayor o igual a 0.",
        )

    items = list_analyses(limit=limit, offset=offset)

    # Cabecera adicional (no forma parte del cuerpo, que debe ser una lista
    # plana por contrato) para que un cliente pueda paginar mostrando
    # totales, sin romper la forma de la respuesta que esperan los tests.
    response.headers["X-Total-Count"] = str(count_analyses())

    return [AnalysisSummary(**item) for item in items]
