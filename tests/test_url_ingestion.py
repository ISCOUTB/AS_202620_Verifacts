from fastapi.testclient import TestClient

from app.main import app
import app.modules.content.service as content_service


client = TestClient(app)


def test_analysis_from_url(monkeypatch) -> None:
    monkeypatch.setattr(
        content_service.trafilatura, "fetch_url", lambda url: "<html>ok</html>"
    )
    monkeypatch.setattr(
        content_service.trafilatura,
        "extract",
        lambda downloaded: "SIEMPRE es una noticia sin fuentes citadas.",
    )

    response = client.post(
        "/analysis",
        json={"url": "https://ejemplo.test/articulo"},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["source_type"] == "url"
    assert "Afirmación absoluta" in data["factors"]


def test_analysis_url_fetch_failure_returns_400(monkeypatch) -> None:
    monkeypatch.setattr(content_service.trafilatura, "fetch_url", lambda url: None)

    response = client.post(
        "/analysis",
        json={"url": "https://ejemplo.test/no-existe"},
    )

    assert response.status_code == 400


def test_analysis_url_extraction_empty_returns_400(monkeypatch) -> None:
    monkeypatch.setattr(
        content_service.trafilatura, "fetch_url", lambda url: "<html></html>"
    )
    monkeypatch.setattr(content_service.trafilatura, "extract", lambda downloaded: None)

    response = client.post(
        "/analysis",
        json={"url": "https://ejemplo.test/vacio"},
    )

    assert response.status_code == 400


def test_analysis_requires_text_or_url() -> None:
    response = client.post("/analysis", json={})

    assert response.status_code == 422


def test_analysis_rejects_both_text_and_url() -> None:
    response = client.post(
        "/analysis",
        json={"text": "algo", "url": "https://ejemplo.test"},
    )

    assert response.status_code == 422
