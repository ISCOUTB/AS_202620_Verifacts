"""Log estructurado + métricas para seguir un mensaje de productor a consumidor.

Cada evento lleva `message_id` y `correlation_id`; filtrando por cualquiera
de los dos se reconstruye el recorrido completo.
"""
from __future__ import annotations

import json
import logging
from collections import Counter

LOGGER = logging.getLogger("verifacts.messaging")


class Telemetry:
    def __init__(self, clock) -> None:
        self._clock = clock
        self.events: list[dict] = []
        self.counters: Counter[str] = Counter()
        self._e2e: list[float] = []

    def emit(self, event: str, **fields) -> None:
        record = {"ts": round(self._clock.now(), 3), "event": event, **fields}
        self.events.append(record)
        LOGGER.info(json.dumps(record, ensure_ascii=False, sort_keys=True))

    def count(self, name: str) -> None:
        self.counters[name] += 1

    def observe_end_to_end(self, seconds: float) -> None:
        self._e2e.append(seconds)

    def trace(self, message_id: str) -> list[dict]:
        return [e for e in self.events if e.get("message_id") == message_id]

    def render_metrics(self) -> str:
        lines = []
        for name in sorted(self.counters):
            lines.append(f"# TYPE verifacts_messaging_{name}_total counter")
            lines.append(f"verifacts_messaging_{name}_total {self.counters[name]}")
        if self._e2e:
            lines.append("# TYPE verifacts_messaging_end_to_end_seconds summary")
            lines.append(f"verifacts_messaging_end_to_end_seconds_count {len(self._e2e)}")
            lines.append(f"verifacts_messaging_end_to_end_seconds_sum {sum(self._e2e):.3f}")
            lines.append(f"verifacts_messaging_end_to_end_seconds_max {max(self._e2e):.3f}")
        return "\n".join(lines) + "\n"
