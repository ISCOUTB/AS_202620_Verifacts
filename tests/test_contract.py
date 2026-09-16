from pathlib import Path

import yaml
from fastapi.testclient import TestClient
from jsonschema import Draft202012Validator, RefResolver

from app.main import app


client = TestClient(app)

CONTRACT_PATH = (
    Path(__file__).resolve().parents[1] / "docs" / "contracts" / "openapi.yaml"
)


def _load_contract() -> dict:
    with open(CONTRACT_PATH, encoding="utf-8") as contract_file:
        return yaml.safe_load(contract_file)


CONTRACT = _load_contract()
RESOLVER = RefResolver.from_schema(CONTRACT)


def _schema_for(name: str) -> dict:
    return CONTRACT["components"]["schemas"][name]


def _assert_matches(instance: object, schema_name: str) -> None:
    """
    Valida 'instance' contra el esquema 'schema_name' del contrato. Si el
    contrato y el código divergen, esta función hace fallar la prueba con
    el detalle exacto del campo que no coincide.
    """
    schema = _schema_for(schema_name)
    validator = Draft202012Validator(schema, resolver=RESOLVER)

    errors = sorted(validator.iter_errors(instance), key=lambda e: list(e.path))

    assert not errors, "\n".join(
        f"{list(error.path)}: {error.message}" for error in errors
    )


def test_contract_file_declares_the_four_real_endpoints() -> None:
    assert CONTRACT["openapi"].startswith("3.1")
    assert "/health" in CONTRACT["paths"]
    assert "/analysis" in CONTRACT["paths"]
    assert "/analysis/{analysis_id}" in CONTRACT["paths"]


def test_health_matches_contract() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    _assert_matches(response.json(), "HealthStatus")


def test_post_analysis_text_matches_contract() -> None:
    response = client.post(
        "/analysis",
        json={"text": "Texto de prueba de contrato."},
    )

    assert response.status_code == 200
    _assert_matches(response.json(), "AnalysisResult")


def test_post_analysis_missing_source_returns_422() -> None:
    response = client.post("/analysis", json={})

    assert response.status_code == 422


def test_post_analysis_both_sources_returns_422() -> None:
    response = client.post(
        "/analysis",
        json={"text": "algo", "url": "https://example.com"},
    )

    assert response.status_code == 422


def test_post_analysis_whitespace_only_text_returns_422() -> None:
    """
    Hallazgo real al construir este contrato (S7): docs/arc42/06 (antes de
    esta corrección) describía "si el texto queda vacío tras normalizar,
    se responde 400", asumiendo que ese texto llega hasta Content. Pero
    AnalysisRequest.check_exactly_one_source (app/api/routes.py) ya trata
    un texto solo de espacios como ausente, así que Pydantic corta la
    solicitud con 422 antes de que Content la vea. El código de 400 sigue
    existiendo en normalize_content(), pero hoy es inalcanzable por HTTP
    con 'text'; solo queda vivo del lado de 'url' cuando la extracción con
    trafilatura falla (ruta que no se prueba aquí por depender de red).
    """
    response = client.post("/analysis", json={"text": "   "})

    assert response.status_code == 422


def test_get_analysis_by_id_matches_contract() -> None:
    created = client.post(
        "/analysis",
        json={"text": "Contenido de prueba para detalle."},
    ).json()

    response = client.get(f"/analysis/{created['id']}")

    assert response.status_code == 200
    _assert_matches(response.json(), "AnalysisSummary")


def test_get_analysis_by_id_not_found_matches_contract() -> None:
    response = client.get("/analysis/999999")

    assert response.status_code == 404
    _assert_matches(response.json(), "ErrorBody")


def test_list_analysis_body_is_flat_array_matching_contract() -> None:
    """
    Contrato explícito: el cuerpo de GET /analysis es un arreglo plano de
    AnalysisSummary, NO un objeto envoltorio {"items": [...], "total": ...}.

    Esta prueba es la que habría fallado en silencio si alguien "arregla"
    el endpoint para que coincida con la descripción que tenía
    docs/arc42/06-vista-de-ejecucion.md §6.3 antes de esta corrección de
    S7 (describía un objeto envoltorio que el código nunca implementó).
    """
    client.post("/analysis", json={"text": "Contenido para el listado."})

    response = client.get("/analysis")

    assert response.status_code == 200

    body = response.json()
    assert isinstance(
        body, list
    ), "El cuerpo debe ser un arreglo plano, no un objeto envoltorio"

    for item in body:
        _assert_matches(item, "AnalysisSummary")


def test_list_analysis_exposes_total_via_header_not_body() -> None:
    response = client.get("/analysis")

    assert response.status_code == 200
    assert "X-Total-Count" in response.headers
    assert response.headers["X-Total-Count"].isdigit()


def test_list_analysis_invalid_limit_matches_contract() -> None:
    response = client.get("/analysis?limit=0")

    assert response.status_code == 400
    _assert_matches(response.json(), "ErrorBody")


def test_list_analysis_negative_offset_matches_contract() -> None:
    response = client.get("/analysis?offset=-1")

    assert response.status_code == 400
    _assert_matches(response.json(), "ErrorBody")
