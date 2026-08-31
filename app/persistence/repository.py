from pathlib import Path
import sqlite3


BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
DATABASE_PATH = DATA_DIR / "verifacts.db"


def _get_connection() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row

    return connection


def initialize_database() -> None:
    """Crea la tabla de análisis si no existe."""
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
    """Guarda un análisis y retorna su ID."""
    initialize_database()

    factors_text = " | ".join(factors)

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
            factors_text,
        ),
    )

    connection.commit()

    analysis_id = cursor.lastrowid

    connection.close()

    return int(analysis_id)


def get_analysis(analysis_id: int) -> dict | None:
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

    if isinstance(result.get("factors"), str):
        result["factors"] = [
            factor.strip()
            for factor in result["factors"].split(" | ")
            if factor.strip()
        ]

    return result