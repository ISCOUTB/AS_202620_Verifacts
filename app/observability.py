import json
import logging
import os
import sys
import time
import uuid
from collections import defaultdict
from datetime import datetime, timezone
from threading import Lock

from fastapi import APIRouter, FastAPI, Request
from fastapi.responses import PlainTextResponse

LOGGER_NAME = "verifacts"
DURATION_BUCKETS = (0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0)
UNMATCHED_PATH = "unmatched"


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.fromtimestamp(
                record.created, timezone.utc
            ).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        payload.update(getattr(record, "fields", {}))

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(payload, ensure_ascii=False)


def configure_logging() -> logging.Logger:
    logger = logging.getLogger(LOGGER_NAME)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)

    logger.setLevel(os.environ.get("LOG_LEVEL", "INFO").upper())
    logger.propagate = False

    return logger


def _escape_label(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


class Metrics:
    def __init__(self) -> None:
        self._lock = Lock()
        self._requests: dict[tuple[str, str, int], int] = defaultdict(int)
        self._bucket_counts: dict[tuple[str, str], list[int]] = defaultdict(
            lambda: [0] * len(DURATION_BUCKETS)
        )
        self._duration_sum: dict[tuple[str, str], float] = defaultdict(float)
        self._duration_count: dict[tuple[str, str], int] = defaultdict(int)

    def observe(self, method: str, path: str, status: int, duration: float) -> None:
        key = (method, path)

        with self._lock:
            self._requests[(method, path, status)] += 1
            self._duration_sum[key] += duration
            self._duration_count[key] += 1

            counts = self._bucket_counts[key]
            for index, upper_bound in enumerate(DURATION_BUCKETS):
                if duration <= upper_bound:
                    counts[index] += 1

    def render(self) -> str:
        lines = [
            "# HELP verifacts_http_requests_total Peticiones HTTP recibidas.",
            "# TYPE verifacts_http_requests_total counter",
        ]

        with self._lock:
            for (method, path, status), total in sorted(self._requests.items()):
                lines.append(
                    "verifacts_http_requests_total"
                    f'{{method="{_escape_label(method)}",'
                    f'path="{_escape_label(path)}",status="{status}"}} {total}'
                )

            lines.extend(
                [
                    "# HELP verifacts_http_request_duration_seconds "
                    "Latencia de las peticiones HTTP.",
                    "# TYPE verifacts_http_request_duration_seconds histogram",
                ]
            )

            for key in sorted(self._duration_count):
                method, path = key
                labels = (
                    f'method="{_escape_label(method)}",'
                    f'path="{_escape_label(path)}"'
                )
                counts = self._bucket_counts[key]

                for upper_bound, count in zip(DURATION_BUCKETS, counts):
                    lines.append(
                        "verifacts_http_request_duration_seconds_bucket"
                        f'{{{labels},le="{upper_bound}"}} {count}'
                    )

                total = self._duration_count[key]
                lines.append(
                    "verifacts_http_request_duration_seconds_bucket"
                    f'{{{labels},le="+Inf"}} {total}'
                )
                lines.append(
                    "verifacts_http_request_duration_seconds_sum"
                    f"{{{labels}}} {self._duration_sum[key]:.6f}"
                )
                lines.append(
                    "verifacts_http_request_duration_seconds_count"
                    f"{{{labels}}} {total}"
                )

        return "\n".join(lines) + "\n"


METRICS = Metrics()

metrics_router = APIRouter()


@metrics_router.get("/metrics", include_in_schema=False)
def read_metrics() -> PlainTextResponse:
    return PlainTextResponse(
        METRICS.render(),
        media_type="text/plain; version=0.0.4; charset=utf-8",
    )


def install_observability(app: FastAPI) -> None:
    logger = configure_logging()

    @app.middleware("http")
    async def observe_requests(request: Request, call_next):
        request_id = request.headers.get("x-request-id") or uuid.uuid4().hex
        started = time.perf_counter()
        status_code = 500

        try:
            response = await call_next(request)
            status_code = response.status_code
            response.headers["X-Request-ID"] = request_id
            return response
        finally:
            duration = time.perf_counter() - started
            route = request.scope.get("route")
            path = getattr(route, "path", UNMATCHED_PATH)

            METRICS.observe(request.method, path, status_code, duration)
            logger.info(
                "request",
                extra={
                    "fields": {
                        "request_id": request_id,
                        "method": request.method,
                        "path": request.url.path,
                        "route": path,
                        "status": status_code,
                        "duration_ms": round(duration * 1000, 2),
                    }
                },
            )

    app.include_router(metrics_router)
    