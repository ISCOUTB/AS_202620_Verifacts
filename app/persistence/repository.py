from pathlib import Path
import sqlite3


BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
DATABASE_PATH = DATA_DIR / "verifacts.db"

DEFAULT_SOURCE_TYPE = "texto"


def _get_connection() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row

    return connection


def _migrate_schema(connection: sqlite3.Connection) -> None:
    """Agrega columnas nuevas a una tabla existente sin borrar datos.

    Usa PRAGMA table_info + ALTER TABLE en lugar de recrear la tabla, para
    no perder análisis ya guardados por ejecuciones anteriores.
    """
    existing_columns = {
        row["name"]
        for row in connection.execute("PRAGMA table_info(analyses)").fetchall()
    }

    if "created_at" not in existing_columns:
        connection.execute("ALTER TABLE analyses ADD COLUMN created_at TEXT")
        connection.execute(
            """
            UPDATE analyses
            SET created_at = CURRENT_TIMESTAMP
            WHERE created_at IS NULL
            """
        )

    if "source_type" not in existing_columns:
        connection.execute("ALTER TABLE analyses ADD COLUMN source_type TEXT")
        connection.execute(
            """
            UPDATE analyses
            SET source_type = ?
            WHERE source_type IS NULL
            """,
            (DEFAULT_SOURCE_TYPE,),
        )

    connection.commit()


def initialize_database() -> None:
    """Crea la tabla de análisis si no existe y aplica migraciones."""
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

    _migrate_schema(connection)

    connection.close()


def _row_to_dict(row: sqlite3.Row) -> dict:
    result = dict(row)

    if isinstance(result.get("factors"), str):
        result["factors"] = [
            factor.strip()
            for factor in result["factors"].split(" | ")
            if factor.strip()
        ]

    if not result.get("source_type"):
        result["source_type"] = DEFAULT_SOURCE_TYPE

    return result


def save_analysis(
    content: str,
    score: int,
    classification: str,
    factors: list[str],
    source_type: str = DEFAULT_SOURCE_TYPE,
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
            factors,
            source_type,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """,
        (
            content,
            score,
            classification,
            factors_text,
            source_type,
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
            factors,
            source_type,
            created_at
        FROM analyses
        WHERE id = ?
        """,
        (analysis_id,),
    ).fetchone()

    connection.close()

    if row is None:
        return None

    return _row_to_dict(row)


def list_analyses(limit: int = 20, offset: int = 0) -> list[dict]:
    """Obtiene los análisis más recientes primero, paginados."""
    initialize_database()

    connection = _get_connection()

    rows = connection.execute(
        """
        SELECT
            id,
            content,
            score,
            classification,
            factors,
            source_type,
            created_at
        FROM analyses
        ORDER BY id DESC
        LIMIT ? OFFSET ?
        """,
        (limit, offset),
    ).fetchall()

    connection.close()

    return [_row_to_dict(row) for row in rows]


def count_analyses() -> int:
    """Cuenta el total de análisis almacenados, para la paginación."""
    initialize_database()

    connection = _get_connection()

    row = connection.execute(
        "SELECT COUNT(*) AS total FROM analyses"
    ).fetchone()

    connection.close()

    return int(row["total"])
