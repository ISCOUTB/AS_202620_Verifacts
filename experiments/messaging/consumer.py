"""Consumidor idempotente del mensaje `analysis.requested`.

Garantía: la entrega es AL MENOS UNA VEZ; el efecto es UNA VEZ porque el
resultado se inserta con `INSERT OR IGNORE` sobre `idempotency_key` (clave
primaria): deduplicación y efecto ocurren en la misma sentencia atómica.
"""
from __future__ import annotations

import json
import sqlite3
from enum import Enum
from typing import Callable

from app.modules.analysis.service import analyze_content
from app.modules.content.service import normalize_content
from app.modules.scoring.service import calculate_score, classify_score

from .broker import InMemoryBroker
from .contract import AnalysisRequested, ContractError
from .simulators import PermanentFetchError, TransientFetchError
from .telemetry import Telemetry


class ResultStore:
    """Almacén SEPARADO de `data/verifacts.db`: el prototipo no toca producción."""

    def __init__(self, path: str = ":memory:") -> None:
        self._db = sqlite3.connect(path)
        self._db.execute(
            """CREATE TABLE IF NOT EXISTS async_results (
                idempotency_key TEXT PRIMARY KEY,
                message_id TEXT NOT NULL,
                correlation_id TEXT NOT NULL,
                source_type TEXT NOT NULL,
                score INTEGER NOT NULL,
                classification TEXT NOT NULL,
                factors TEXT NOT NULL,
                attempts INTEGER NOT NULL
            )"""
        )

    def exists(self, key: str) -> bool:
        row = self._db.execute(
            "SELECT 1 FROM async_results WHERE idempotency_key = ?", (key,)
        ).fetchone()
        return row is not None

    def insert_if_absent(self, key: str, message: AnalysisRequested, score: int,
                         classification: str, factors: list[str], attempts: int) -> bool:
        cursor = self._db.execute(
            "INSERT OR IGNORE INTO async_results VALUES (?,?,?,?,?,?,?,?)",
            (key, message.message_id, message.correlation_id, message.source_type,
             score, classification, json.dumps(factors, ensure_ascii=False), attempts),
        )
        self._db.commit()
        return cursor.rowcount == 1

    def count(self) -> int:
        return self._db.execute("SELECT COUNT(*) FROM async_results").fetchone()[0]

    def get(self, key: str) -> dict | None:
        row = self._db.execute(
            "SELECT score, classification, factors, attempts, message_id "
            "FROM async_results WHERE idempotency_key = ?", (key,)
        ).fetchone()
        if row is None:
            return None
        return {"score": row[0], "classification": row[1],
                "factors": json.loads(row[2]), "attempts": row[3], "message_id": row[4]}


class Outcome(Enum):
    PROCESSED = "processed"
    DUPLICATE = "duplicate_skipped"
    RETRY = "retry"
    REJECT = "reject"


class AnalysisConsumer:
    def __init__(self, store: ResultStore, fetcher: Callable[[str], str],
                 telemetry: Telemetry, clock) -> None:
        self._store = store
        self._fetcher = fetcher
        self._telemetry = telemetry
        self._clock = clock

    def process(self, message: AnalysisRequested, attempt: int,
                published_at: float) -> tuple[Outcome, str]:
        ids = {"message_id": message.message_id, "correlation_id": message.correlation_id}
        key = message.idempotency_key

        if self._store.exists(key):
            self._telemetry.count("duplicates_skipped")
            self._telemetry.emit("duplicate_skipped", attempt=attempt, **ids)
            return Outcome.DUPLICATE, "already_processed"

        try:
            raw = self._fetcher(message.source) if message.source_type == "url" else message.source
            content = normalize_content(raw)
        except TransientFetchError as error:
            return Outcome.RETRY, f"transient: {error}"
        except PermanentFetchError as error:
            return Outcome.REJECT, f"permanent: {error}"
        except ValueError as error:  # contenido vacío: reintentar no lo arregla
            return Outcome.REJECT, f"invalid_content: {error}"
        except Exception as error:  # desconocido: se trata como recuperable
            return Outcome.RETRY, f"unexpected: {type(error).__name__}: {error}"

        findings = analyze_content(content)
        score = calculate_score(findings)
        classification = classify_score(score)
        factors = [finding.indicator for finding in findings]

        inserted = self._store.insert_if_absent(
            key, message, score, classification, factors, attempt
        )
        if not inserted:  # carrera: otro consumidor ganó entre exists() e insert
            self._telemetry.count("duplicates_skipped")
            self._telemetry.emit("duplicate_skipped", attempt=attempt, **ids)
            return Outcome.DUPLICATE, "lost_race"

        elapsed = self._clock.now() - published_at
        self._telemetry.count("processed")
        self._telemetry.observe_end_to_end(elapsed)
        self._telemetry.emit(
            "processed", attempt=attempt, score=score,
            classification=classification, e2e_s=round(elapsed, 3), **ids,
        )
        return Outcome.PROCESSED, "ok"


class Worker:
    """Bucle del consumidor: traduce el resultado en ack / nack / DLQ."""

    def __init__(self, broker: InMemoryBroker, consumer: AnalysisConsumer,
                 telemetry: Telemetry, clock) -> None:
        self._broker = broker
        self._consumer = consumer
        self._telemetry = telemetry
        self._clock = clock

    def step(self) -> bool:
        delivery = self._broker.poll()
        if delivery is None:
            return False
        try:
            message = AnalysisRequested.from_json(delivery.raw)
        except ContractError as error:  # mensaje venenoso: no se reintenta
            self._broker.dead_letter(delivery, f"contract: {error}")
            return True

        outcome, reason = self._consumer.process(
            message, delivery.attempt, delivery.published_at
        )
        if outcome in (Outcome.PROCESSED, Outcome.DUPLICATE):
            self._broker.ack(delivery)
        elif outcome is Outcome.RETRY:
            self._broker.nack(delivery, reason)
        else:
            self._broker.dead_letter(delivery, reason)
        return True

    def run_until_idle(self, max_steps: int = 1000) -> None:
        """Procesa todo, avanzando el reloj simulado hasta el siguiente evento."""
        for _ in range(max_steps):
            if self.step():
                continue
            upcoming = self._broker.next_event_time()
            if upcoming is None:
                return
            self._clock.advance_to(upcoming)
        raise RuntimeError("run_until_idle excedió max_steps (posible bucle)")
