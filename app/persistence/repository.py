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
            ", ".join(factors),
        ),
    )

    connection.commit()

    analysis_id = cursor.lastrowid

    connection.close()

    return int(analysis_id)


def get_analysis(analysis_id: int) -> dict[str, Any] | None:
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

    return dict(row)
def save_analysis(data):
    """
    Guarda un análisis (espera un diccionario con 'id', 'text', 'status', etc.)
    Sobrescribe si ya existe el mismo 'id'.
    """
    analyses = _load_data()
    analysis_id = str(data.get("id"))
    if not analysis_id:
        # Si no tiene id, generar uno nuevo
        next_id = str(len(analyses) + 1)
        data["id"] = next_id
        analysis_id = next_id
    analyses[analysis_id] = data
    _save_data(analyses)
    return data
