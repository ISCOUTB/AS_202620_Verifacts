import json
import logging

from fastapi.testclient import TestClient

from app.main import app
from app.observability import JsonFormatter


client = TestClient(app)


def test_metrics_endpoint_exposes_request_counter_and_histogram() -> None:
    client.get("/health")

    response = client.get("/metrics")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/plain")
    assert "verifacts_http_requests_total" in response.text
    assert 'path="/health"' in response.text
    assert "verifacts_http_request_duration_seconds_bucket" in response.text


def test_metrics_uses_route_template_not_raw_url() -> None:
    client.get("/analysis/999999")

    response = client.get("/metrics")

    assert 'path="/analysis/{analysis_id}"' in response.text
    assert "999999" not in response.text


def test_response_carries_request_id() -> None:
    response = client.get("/health", headers={"X-Request-ID": "abc-123"})

    assert response.headers["x-request-id"] == "abc-123"


def test_json_formatter_outputs_valid_json_with_extra_fields() -> None:
    record = logging.LogRecord(
        "verifacts", logging.INFO, __file__, 1, "request", None, None
    )
    record.fields = {"path": "/health", "status": 200}

    payload = json.loads(JsonFormatter().format(record))

    assert payload["message"] == "request"
    assert payload["level"] == "INFO"
    assert payload["path"] == "/health"
    assert payload["status"] == 200
    assert "timestamp" in payload
    