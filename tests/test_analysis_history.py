from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_get_analysis_by_id_returns_created_analysis() -> None:
    created = client.post(
        "/analysis",
        json={"text": "Contenido de prueba para historial."},
    ).json()

    response = client.get(f"/analysis/{created['id']}")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == created["id"]
    assert data["content"] == "Contenido de prueba para historial."
    assert data["source_type"] == "texto"
    assert "created_at" in data


def test_get_analysis_by_id_not_found_returns_404() -> None:
    response = client.get("/analysis/999999")

    assert response.status_code == 404


def test_list_analysis_includes_created_entries() -> None:
    created = client.post(
        "/analysis",
        json={"text": "Otro contenido distinto para el listado."},
    ).json()

    response = client.get("/analysis")

    assert response.status_code == 200

    ids = [item["id"] for item in response.json()]

    assert created["id"] in ids


def test_list_analysis_rejects_invalid_limit() -> None:
    response = client.get("/analysis?limit=0")

    assert response.status_code == 400


def test_list_analysis_rejects_negative_offset() -> None:
    response = client.get("/analysis?offset=-1")

    assert response.status_code == 400
