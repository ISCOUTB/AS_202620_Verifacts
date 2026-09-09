from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_list_and_get_analysis() -> None:
    create_response = client.post(
        "/analysis",
        json={"text": "SIEMPRE hay que verificar todo lo que se comparte!!!"},
    )
    assert create_response.status_code == 200
    created = create_response.json()
    assert created["created_at"] is not None

    list_response = client.get("/analysis", params={"limit": 5, "offset": 0})
    assert list_response.status_code == 200
    payload = list_response.json()

    assert payload["total"] >= 1
    assert payload["limit"] == 5
    assert payload["offset"] == 0
    assert any(item["id"] == created["id"] for item in payload["items"])

    detail_response = client.get(f"/analysis/{created['id']}")
    assert detail_response.status_code == 200
    detail = detail_response.json()

    assert detail["id"] == created["id"]
    assert detail["score"] == created["score"]
    assert detail["classification"] == created["classification"]


def test_get_analysis_not_found() -> None:
    response = client.get("/analysis/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Análisis no encontrado."


def test_list_respects_pagination_bounds() -> None:
    response = client.get("/analysis", params={"limit": 1000, "offset": 0})

    assert response.status_code == 422
