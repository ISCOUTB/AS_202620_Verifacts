"""Broker en memoria con semántica de entrega AL MENOS UNA VEZ.

Simula lo que importa para verificar propiedades (no es un broker real):
- un mensaje se entrega y queda "en vuelo" hasta recibir `ack`;
- si no hay `ack` antes del `visibility_timeout`, se REENTREGA (duplicado);
- `nack` reprograma con backoff exponencial; al agotar `max_attempts` pasa
  a la cola de mensajes fallidos (DLQ) con el motivo;
- fallos inyectables: publicación duplicada y `ack` perdido.
"""
from __future__ import annotations

import json
import random
from dataclasses import dataclass, field

from .telemetry import Telemetry


@dataclass(frozen=True)
class RetryPolicy:
    max_attempts: int = 4
    base_delay: float = 1.0
    factor: float = 2.0
    max_delay: float = 30.0
    jitter: float = 0.0  # fracción +/- del retraso; 0 en pruebas, 0.2 recomendado en producción

    def delay(self, attempt: int, rng: random.Random | None = None) -> float:
        raw = min(self.max_delay, self.base_delay * self.factor ** (attempt - 1))
        if self.jitter and rng is not None:
            raw *= 1 + rng.uniform(-self.jitter, self.jitter)
        return raw


@dataclass
class Delivery:
    raw: str
    attempt: int
    published_at: float
    deadline: float = 0.0
    message_id: str = ""
    correlation_id: str = ""


@dataclass
class _Entry:
    raw: str
    published_at: float
    available_at: float
    attempt: int = 0
    deadline: float | None = None


@dataclass
class DeadLetter:
    raw: str
    reason: str
    attempts: int
    message_id: str = ""


def _ids(raw: str) -> tuple[str, str]:
    """Extrae ids para el log aunque el mensaje esté mal formado."""
    try:
        body = json.loads(raw)
        return str(body.get("message_id", "")), str(body.get("correlation_id", ""))
    except (json.JSONDecodeError, AttributeError):
        return "", ""


class InMemoryBroker:
    def __init__(
        self,
        clock,
        telemetry: Telemetry,
        policy: RetryPolicy | None = None,
        visibility_timeout: float = 30.0,
        rng: random.Random | None = None,
    ) -> None:
        self._clock = clock
        self._telemetry = telemetry
        self.policy = policy or RetryPolicy()
        self._visibility_timeout = visibility_timeout
        self._rng = rng or random.Random(0)
        self._queue: list[_Entry] = []
        self._in_flight: dict[int, _Entry] = {}
        self._next_tag = 0
        self.dlq: list[DeadLetter] = []
        self._duplicate_next_publish = False
        self._lose_next_ack = False

    # --- fallos inyectables -------------------------------------------------
    def duplicate_next_publish(self) -> None:
        self._duplicate_next_publish = True

    def lose_next_ack(self) -> None:
        self._lose_next_ack = True

    # --- productor ----------------------------------------------------------
    def publish(self, raw: str) -> None:
        copies = 2 if self._duplicate_next_publish else 1
        self._duplicate_next_publish = False
        message_id, correlation_id = _ids(raw)
        for _ in range(copies):
            now = self._clock.now()
            self._queue.append(_Entry(raw=raw, published_at=now, available_at=now))
            self._telemetry.count("published")
            self._telemetry.emit(
                "published", message_id=message_id, correlation_id=correlation_id
            )

    # --- consumidor ---------------------------------------------------------
    def _requeue_expired(self) -> None:
        now = self._clock.now()
        for tag in [t for t, e in self._in_flight.items() if e.deadline <= now]:
            entry = self._in_flight.pop(tag)
            entry.deadline = None
            entry.available_at = now
            self._queue.append(entry)
            message_id, correlation_id = _ids(entry.raw)
            self._telemetry.count("redelivered_after_timeout")
            self._telemetry.emit(
                "redelivery_after_timeout",
                message_id=message_id,
                correlation_id=correlation_id,
                attempt=entry.attempt,
            )

    def poll(self) -> Delivery | None:
        self._requeue_expired()
        now = self._clock.now()
        ready = [e for e in self._queue if e.available_at <= now]
        if not ready:
            return None
        entry = min(ready, key=lambda e: e.available_at)
        self._queue.remove(entry)
        entry.attempt += 1
        entry.deadline = now + self._visibility_timeout
        tag = self._next_tag
        self._next_tag += 1
        self._in_flight[tag] = entry
        message_id, correlation_id = _ids(entry.raw)
        delivery = Delivery(
            raw=entry.raw,
            attempt=entry.attempt,
            published_at=entry.published_at,
            deadline=entry.deadline,
            message_id=message_id,
            correlation_id=correlation_id,
        )
        delivery._tag = tag  # type: ignore[attr-defined]
        self._telemetry.count("delivered")
        self._telemetry.emit(
            "delivered",
            message_id=message_id,
            correlation_id=correlation_id,
            attempt=entry.attempt,
        )
        return delivery

    def ack(self, delivery: Delivery) -> None:
        if self._lose_next_ack:
            self._lose_next_ack = False
            self._telemetry.emit(
                "ack_lost",
                message_id=delivery.message_id,
                correlation_id=delivery.correlation_id,
            )
            return  # el mensaje sigue en vuelo y se reentregará al vencer el timeout
        self._in_flight.pop(delivery._tag, None)  # type: ignore[attr-defined]

    def nack(self, delivery: Delivery, reason: str) -> None:
        """Fallo recuperable: reintento con backoff o DLQ si se agotaron los intentos."""
        entry = self._in_flight.pop(delivery._tag)  # type: ignore[attr-defined]
        if entry.attempt >= self.policy.max_attempts:
            self._to_dlq(entry, f"retries_exhausted: {reason}")
            return
        delay = self.policy.delay(entry.attempt, self._rng)
        entry.deadline = None
        entry.available_at = self._clock.now() + delay
        self._queue.append(entry)
        self._telemetry.count("retry_scheduled")
        self._telemetry.emit(
            "retry_scheduled",
            message_id=delivery.message_id,
            correlation_id=delivery.correlation_id,
            attempt=entry.attempt,
            delay_s=round(delay, 3),
            reason=reason,
        )

    def dead_letter(self, delivery: Delivery, reason: str) -> None:
        """Fallo no recuperable: directo a la DLQ, sin reintentos."""
        entry = self._in_flight.pop(delivery._tag)  # type: ignore[attr-defined]
        self._to_dlq(entry, reason)

    def _to_dlq(self, entry: _Entry, reason: str) -> None:
        message_id, correlation_id = _ids(entry.raw)
        self.dlq.append(
            DeadLetter(entry.raw, reason, entry.attempt, message_id=message_id)
        )
        self._telemetry.count("dead_lettered")
        self._telemetry.emit(
            "dead_lettered",
            message_id=message_id,
            correlation_id=correlation_id,
            attempt=entry.attempt,
            reason=reason,
        )

    def redrive_dlq(self) -> int:
        """Operación manual: devuelve los mensajes de la DLQ a la cola principal."""
        moved = len(self.dlq)
        for letter in self.dlq:
            now = self._clock.now()
            self._queue.append(_Entry(letter.raw, published_at=now, available_at=now))
            self._telemetry.emit("redriven", message_id=letter.message_id)
        self.dlq.clear()
        return moved

    # --- apoyo para simular el paso del tiempo ------------------------------
    def next_event_time(self) -> float | None:
        times = [e.available_at for e in self._queue]
        times += [e.deadline for e in self._in_flight.values() if e.deadline is not None]
        return min(times) if times else None
