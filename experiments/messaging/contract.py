"""Contrato del mensaje `verifacts.analysis.requested` y su criterio de compatibilidad.

Reglas de compatibilidad (versión semántica MAJOR.MINOR):
- Cambio compatible (sube MINOR): agregar campos OPCIONALES. El consumidor es
  un "lector tolerante": ignora los campos que no conoce.
- Cambio incompatible (sube MAJOR): quitar o renombrar un campo, cambiar su
  tipo o su significado, o volver obligatorio uno opcional. Se publica en una
  cola nueva (`analysis.requested.v2`) mientras la v1 se drena.
- Un consumidor v1 acepta cualquier 1.x y manda a la DLQ cualquier otro MAJOR.
"""
from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone

SCHEMA_NAME = "verifacts.analysis.requested"
SCHEMA_VERSION = "1.0"
SUPPORTED_MAJOR = 1
QUEUE_NAME = "analysis.requested.v1"
DLQ_NAME = "analysis.requested.v1.dlq"

REQUIRED_FIELDS = (
    "message_id",
    "correlation_id",
    "idempotency_key",
    "source_type",
    "source",
    "schema_version",
    "produced_at",
)
SOURCE_TYPES = ("url", "texto")


class ContractError(ValueError):
    """El mensaje no es JSON válido o le faltan campos obligatorios."""


class IncompatibleSchemaError(ContractError):
    """El MAJOR del mensaje no es el que entiende este consumidor."""


def make_idempotency_key(source_type: str, source: str) -> str:
    """SHA-256 de `source_type::fuente`, igual al fallback de MF-05 (entrega S11)."""
    normalized = " ".join(source.strip().split())
    return hashlib.sha256(f"{source_type}::{normalized}".encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class AnalysisRequested:
    message_id: str
    correlation_id: str
    idempotency_key: str
    source_type: str
    source: str
    produced_at: str
    schema_version: str = SCHEMA_VERSION

    @classmethod
    def new(
        cls,
        source_type: str,
        source: str,
        correlation_id: str | None = None,
    ) -> "AnalysisRequested":
        if source_type not in SOURCE_TYPES:
            raise ContractError(f"source_type inválido: {source_type!r}")
        return cls(
            message_id=uuid.uuid4().hex,
            correlation_id=correlation_id or uuid.uuid4().hex,
            idempotency_key=make_idempotency_key(source_type, source),
            source_type=source_type,
            source=source,
            produced_at=datetime.now(timezone.utc).isoformat(),
        )

    def to_json(self) -> str:
        body = {"type": SCHEMA_NAME, **self.__dict__}
        return json.dumps(body, ensure_ascii=False, sort_keys=True)

    @classmethod
    def from_json(cls, raw: str) -> "AnalysisRequested":
        try:
            body = json.loads(raw)
        except json.JSONDecodeError as error:
            raise ContractError(f"JSON inválido: {error}") from error
        if not isinstance(body, dict):
            raise ContractError("El cuerpo debe ser un objeto JSON.")

        missing = [name for name in REQUIRED_FIELDS if name not in body]
        if missing:
            raise ContractError(f"Faltan campos obligatorios: {missing}")
        if not all(isinstance(body[name], str) and body[name] for name in REQUIRED_FIELDS):
            raise ContractError("Los campos obligatorios deben ser texto no vacío.")

        major = body["schema_version"].split(".")[0]
        if major != str(SUPPORTED_MAJOR):
            raise IncompatibleSchemaError(
                f"schema_version {body['schema_version']} no compatible con v{SUPPORTED_MAJOR}"
            )
        if body["source_type"] not in SOURCE_TYPES:
            raise ContractError(f"source_type inválido: {body['source_type']!r}")

        # Lector tolerante: solo se toman los campos conocidos.
        return cls(**{name: body[name] for name in REQUIRED_FIELDS})
