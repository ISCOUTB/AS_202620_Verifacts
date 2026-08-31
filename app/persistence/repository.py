import sqlite3
from pathlib import Path
from typing import Any

DB_PATH = Path("data/verifacts.db")


def _get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database() -> None:
    """Crea las tablas necesarias si no existen."""
    connection = _get_connection()
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            score INTEGER NOT NULL,
            classification TEXT NOT NULL,
            factors TEXT NOT NULL
        )
        """
    )
    connection.commit()
    connection.close()


def save_analysis(
    content: str,
    score: int,
    classification: str,
    factors: list[str],
) -> int:
    """Guarda un análisis en la base de datos SQLite y retorna su ID."""
    initialize_database()  # Asegura que la tabla exista antes de insertar
    connection = _get_connection()

    cursor = connection.execute(
        """
        INSERT INTO analyses (
            content,
            score,
            classification,
            factors
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            content,
            score,
            classification,
            ", ".join(factors) if isinstance(factors, list) else str(factors),
        ),
    )

    connection.commit()
    analysis_id = cursor.lastrowid
    connection.close()

    return int(analysis_id)


def get_analysis(analysis_id: int) -> dict[str, Any] | None:
    """Obtiene un análisis por su ID."""
    initialize_database()
    connection = _get_connection()

    row = connection.execute(
        """
        SELECT
            id,
            content,
            score,
            classification,
            factors
        FROM analyses
        WHERE id = ?
        """,
        (analysis_id,),
    ).fetchone()

    connection.close()

    if row is None:
        return None

    result = dict(row)
    # Convertir los factores de vuelta a lista si están almacenados como string
    if isinstance(result.get("factors"), str):
        result["factors"] = [f.strip() for f in result["factors"].split(",") if f.strip()]

    return result
