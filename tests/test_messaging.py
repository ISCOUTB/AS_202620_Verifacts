"""Pruebas del prototipo de mensajería (taller S13). No tocan `app/` ni data/verifacts.db."""
import json
import pathlib

import pytest

from experiments.messaging.broker import InMemoryBroker, RetryPolicy
from experiments.messaging.consumer import AnalysisConsumer, ResultStore, Worker
from experiments.messaging.contract import (
    AnalysisRequested,
    ContractError,
    IncompatibleSchemaError,
    make_idempotency_key,
)
from experiments.messaging.simulators import (
    ManualClock,
    PermanentFetchError,
    ScriptedFetcher,
    TransientFetchError,
)
from experiments.messaging.telemetry import Telemetry

TEXT = "ESTA NOTICIA ES TOTALMENTE CIERTA!!! Todos deben compartirla!!!"
URL = "https://ejemplo.test/nota"


def build(script=None, max_attempts=4):
    clock = ManualClock()
    telemetry = Telemetry(clock)
    broker = InMemoryBroker(clock, telemetry, RetryPolicy(max_attempts=max_attempts))
    store = ResultStore()
    fetcher = ScriptedFetcher(script or {})
    worker = Worker(broker, AnalysisConsumer(store, fetcher, telemetry, clock), telemetry, clock)
    return clock, telemetry, broker, store, fetcher, worker


# --- 1. Contrato y compatibilidad -------------------------------------------
def test_contrato_ida_y_vuelta():
    message = AnalysisRequested.new("texto", TEXT)
    assert AnalysisRequested.from_json(message.to_json()) == message


def test_cambio_menor_con_campo_nuevo_sigue_siendo_compatible():
    body = json.loads(AnalysisRequested.new("texto", TEXT).to_json())
    body["schema_version"] = "1.7"
    body["priority"] = "alta"  # campo opcional añadido por un productor más nuevo
    clock, telemetry, broker, store, _, worker = build()
    broker.publish(json.dumps(body))
    worker.run_until_idle()
    assert store.count() == 1 and not broker.dlq


def test_cambio_mayor_va_a_dlq_sin_reintentos():
    body = json.loads(AnalysisRequested.new("texto", TEXT).to_json())
    body["schema_version"] = "2.0"
    with pytest.raises(IncompatibleSchemaError):
        AnalysisRequested.from_json(json.dumps(body))
    clock, telemetry, broker, store, _, worker = build()
    broker.publish(json.dumps(body))
    worker.run_until_idle()
    assert store.count() == 0
    assert len(broker.dlq) == 1 and broker.dlq[0].attempts == 1
    assert broker.dlq[0].reason.startswith("contract:")


def test_campo_obligatorio_ausente_es_error_de_contrato():
    body = json.loads(AnalysisRequested.new("texto", TEXT).to_json())
    del body["idempotency_key"]
    with pytest.raises(ContractError):
        AnalysisRequested.from_json(json.dumps(body))


# --- 2/3. Duplicados e idempotencia -----------------------------------------
def test_publicacion_duplicada_produce_un_solo_efecto():
    clock, telemetry, broker, store, _, worker = build()
    broker.duplicate_next_publish()
    message = AnalysisRequested.new("texto", TEXT)
    broker.publish(message.to_json())
    worker.run_until_idle()

    assert store.count() == 1
    result = store.get(message.idempotency_key)
    assert (result["score"], result["classification"]) == (50, "Riesgo medio")
    assert telemetry.counters["delivered"] == 2
    assert telemetry.counters["processed"] == 1
    assert telemetry.counters["duplicates_skipped"] == 1


def test_mismo_pedido_con_otro_message_id_se_deduplica_por_clave_de_idempotencia():
    clock, telemetry, broker, store, _, worker = build()
    first = AnalysisRequested.new("texto", TEXT)
    second = AnalysisRequested.new("texto", "  " + TEXT + " ")  # el usuario reenvía
    assert first.message_id != second.message_id
    assert first.idempotency_key == second.idempotency_key
    broker.publish(first.to_json())
    broker.publish(second.to_json())
    worker.run_until_idle()
    assert store.count() == 1
    assert telemetry.counters["duplicates_skipped"] == 1


def test_carrera_entre_consumidores_no_duplica_el_efecto(monkeypatch):
    """Otro consumidor inserta entre exists() y el INSERT: gana la clave primaria."""
    clock, telemetry, broker, store, _, worker = build()
    message = AnalysisRequested.new("texto", TEXT)
    store.insert_if_absent(message.idempotency_key, message, 50, "Riesgo medio", [], 1)
    monkeypatch.setattr(store, "exists", lambda key: False)  # el chequeo previo "no ve" al otro
    broker.publish(message.to_json())
    worker.run_until_idle()

    assert store.count() == 1
    assert telemetry.counters["duplicates_skipped"] == 1
    assert telemetry.counters["processed"] == 0


def test_ack_perdido_provoca_reentrega_y_el_efecto_sigue_siendo_uno():
    """Caso clave de 'al menos una vez': se procesó, pero el broker no se enteró."""
    clock, telemetry, broker, store, _, worker = build()
    message = AnalysisRequested.new("texto", TEXT)
    broker.publish(message.to_json())
    broker.lose_next_ack()
    worker.run_until_idle()

    assert store.count() == 1
    assert telemetry.counters["redelivered_after_timeout"] == 1
    assert telemetry.counters["duplicates_skipped"] == 1
    assert clock.now() == 30.0  # esperó el visibility_timeout simulado


# --- 4/5. Reintentos, backoff y DLQ -----------------------------------------
def test_politica_de_backoff_exponencial_con_tope():
    policy = RetryPolicy(base_delay=1, factor=2, max_delay=30)
    assert [policy.delay(n) for n in range(1, 8)] == [1, 2, 4, 8, 16, 30, 30]


def test_fallo_recuperable_se_recupera_con_backoff():
    clock, telemetry, broker, store, fetcher, worker = build(
        {URL: [TransientFetchError("timeout"), TransientFetchError("503"), TEXT]}
    )
    message = AnalysisRequested.new("url", URL)
    broker.publish(message.to_json())
    worker.run_until_idle()

    assert fetcher.calls[URL] == 3
    assert store.get(message.idempotency_key)["attempts"] == 3
    delays = [e["delay_s"] for e in telemetry.events if e["event"] == "retry_scheduled"]
    assert delays == [1.0, 2.0]
    assert clock.now() == 3.0
    assert not broker.dlq


def test_reintentos_agotados_terminan_en_dlq_con_motivo():
    clock, telemetry, broker, store, fetcher, worker = build(
        {URL: [TransientFetchError("timeout")]}, max_attempts=3
    )
    broker.publish(AnalysisRequested.new("url", URL).to_json())
    worker.run_until_idle()

    assert fetcher.calls[URL] == 3
    assert store.count() == 0
    assert len(broker.dlq) == 1
    assert broker.dlq[0].attempts == 3
    assert broker.dlq[0].reason.startswith("retries_exhausted: transient: timeout")


def test_fallo_permanente_va_directo_a_dlq_sin_reintentar():
    clock, telemetry, broker, store, fetcher, worker = build(
        {URL: [PermanentFetchError("404")]}
    )
    broker.publish(AnalysisRequested.new("url", URL).to_json())
    worker.run_until_idle()
    assert fetcher.calls[URL] == 1
    assert telemetry.counters["retry_scheduled"] == 0
    assert broker.dlq[0].reason == "permanent: 404"


def test_mensaje_de_dlq_se_puede_reprocesar_tras_corregir_la_causa():
    clock, telemetry, broker, store, fetcher, worker = build(
        {URL: [PermanentFetchError("403 anti-bot"), TEXT]}
    )
    message = AnalysisRequested.new("url", URL)
    broker.publish(message.to_json())
    worker.run_until_idle()
    assert len(broker.dlq) == 1 and store.count() == 0

    assert broker.redrive_dlq() == 1
    worker.run_until_idle()
    assert store.count() == 1 and not broker.dlq


# --- 6. Trazabilidad y métricas ---------------------------------------------
def test_un_mensaje_se_sigue_de_productor_a_consumidor():
    clock, telemetry, broker, store, _, worker = build(
        {URL: [TransientFetchError("timeout"), TEXT]}
    )
    message = AnalysisRequested.new("url", URL)
    other = AnalysisRequested.new("texto", "Hola mundo tranquilo")
    broker.publish(message.to_json())
    broker.publish(other.to_json())
    worker.run_until_idle()

    trace = telemetry.trace(message.message_id)
    assert [e["event"] for e in trace] == [
        "published", "delivered", "retry_scheduled", "delivered", "processed",
    ]
    assert {e["correlation_id"] for e in trace} == {message.correlation_id}
    assert trace[-1]["e2e_s"] == 1.0
    assert other.message_id not in {e["message_id"] for e in trace}

    metrics = telemetry.render_metrics()
    assert "verifacts_messaging_processed_total 2" in metrics
    assert "verifacts_messaging_retry_scheduled_total 1" in metrics
    assert "verifacts_messaging_end_to_end_seconds_count 2" in metrics


# --- Aislamiento (ADR-0013: no se incorpora al sistema) -----------------------
def test_el_prototipo_esta_aislado_de_app():
    root = pathlib.Path(__file__).resolve().parents[1] / "app"
    offenders = [
        str(path) for path in root.rglob("*.py")
        if "experiments" in path.read_text(encoding="utf-8")
    ]
    assert offenders == []


def test_clave_de_idempotencia_coincide_con_el_fallback_de_mf05():
    assert make_idempotency_key("texto", "a  b") == make_idempotency_key("texto", "a b")
    assert make_idempotency_key("url", "x") != make_idempotency_key("texto", "x")
