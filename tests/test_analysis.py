from fastapi.testclient import TestClient

from app.main import app
from app.persistence.repository import get_analysis


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

    stored = get_analysis(data["id"])

    assert stored is not None
    assert stored["content"] == (
        "ESTA NOTICIA ES TOTALMENTE CIERTA!!! Todos deben compartirla!!!"
    )
    assert stored["score"] == 50
    assert stored["classification"] == "Riesgo medio"
