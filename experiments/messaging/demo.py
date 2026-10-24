"""Demo reproducible: `python -m experiments.messaging.demo`."""
from __future__ import annotations

import logging
import sys

from .broker import InMemoryBroker, RetryPolicy
from .consumer import AnalysisConsumer, ResultStore, Worker
from .contract import AnalysisRequested
from .simulators import ManualClock, PermanentFetchError, ScriptedFetcher, TransientFetchError
from .telemetry import LOGGER, Telemetry

TEXT = "ESTA NOTICIA ES TOTALMENTE CIERTA!!! Todos deben compartirla!!!"


def main() -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(message)s"))
    LOGGER.addHandler(handler)
    LOGGER.setLevel(logging.INFO)
    LOGGER.propagate = False

    clock = ManualClock()
    telemetry = Telemetry(clock)
    broker = InMemoryBroker(clock, telemetry, RetryPolicy(max_attempts=4))
    fetcher = ScriptedFetcher({
        "https://ejemplo.test/lento": [TransientFetchError("timeout"), TransientFetchError("503"), TEXT],
        "https://ejemplo.test/no-existe": [PermanentFetchError("404")],
    })
    worker = Worker(broker, AnalysisConsumer(ResultStore(), fetcher, telemetry, clock), telemetry, clock)

    print("== 1. URL con 2 fallos recuperables (reintento con backoff 1 s, 2 s) ==")
    recovered = AnalysisRequested.new("url", "https://ejemplo.test/lento")
    broker.publish(recovered.to_json())
    worker.run_until_idle()

    print("== 2. Publicación duplicada del mismo mensaje (idempotencia) ==")
    broker.duplicate_next_publish()
    broker.publish(AnalysisRequested.new("texto", TEXT).to_json())
    worker.run_until_idle()

    print("== 3. URL inexistente (404, fallo permanente -> DLQ sin reintentos) ==")
    broker.publish(AnalysisRequested.new("url", "https://ejemplo.test/no-existe").to_json())
    worker.run_until_idle()

    print("== 4. Mensaje con schema_version 2.0 (incompatible -> DLQ) ==")
    broker.publish(AnalysisRequested.new("texto", TEXT).to_json().replace('"1.0"', '"2.0"'))
    worker.run_until_idle()

    print("\n== Métricas ==")
    print(telemetry.render_metrics())
    print("== DLQ ==")
    for letter in broker.dlq:
        print(f"- {letter.message_id[:8]}… intentos={letter.attempts} motivo={letter.reason}")
    print(f"\n== Traza del mensaje {recovered.message_id[:8]}… ==")
    for event in telemetry.trace(recovered.message_id):
        print(f"t={event['ts']:>5}s  {event['event']}")


if __name__ == "__main__":
    main()
