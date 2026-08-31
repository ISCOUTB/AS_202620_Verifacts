from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_analysis_vertical_slice() -> None:
    response = client.post(
        "/analysis",
        json={
            "text": "ESTA NOTICIA ES TOTALMENTE CIERTA!!! Todos deben compartirla!!!"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] > 0
    assert data["score"] == 50
    assert data["classification"] == "Riesgo medio"

    assert "Lenguaje sensacionalista" in data["factors"]
    assert "Uso excesivo de mayúsculas" in data["factors"]
    assert "Afirmación absoluta" in data["factors"]
