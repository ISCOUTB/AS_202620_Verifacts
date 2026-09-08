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


def _migrate_schema(connection: sqlite3.Connection) -> None:
    """
    Agrega columnas nuevas a bases de datos creadas antes de esta
    ampliacion, sin perder los datos ya guardados. SQLite no soporta
    "ADD COLUMN IF NOT EXISTS", por eso se revisa PRAGMA table_info primero.
    """
    existing_columns = {
        row["name"] for row in connection.execute("PRAGMA table_info(analyses)")
    }

    if "source_type" not in existing_columns:
        connection.execute(
            "ALTER TABLE analyses ADD COLUMN source_type TEXT NOT NULL DEFAULT 'texto'"
        )

    if "created_at" not in existing_columns:
        connection.execute(
            "ALTER TABLE analyses ADD COLUMN created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP"
        )

    connection.commit()


def initialize_database() -> None:
    """Crea la tabla de analisis si no existe y migra el esquema si hace falta."""
    connection = _get_connection()

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            score INTEGER NOT NULL,
            classification TEXT NOT NULL,
            factors TEXT NOT NULL,
            source_type TEXT NOT NULL DEFAULT 'texto',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    connection.commit()

    _migrate_schema(connection)

    connection.close()


def _deserialize_row(row: sqlite3.Row) -> dict:
    result = dict(row)

    if isinstance(result.get("factors"), str):
        result["factors"] = [
            factor.strip()
            for factor in result["factors"].split(" | ")
            if factor.strip()
        ]

    return result


def save_analysis(
    content: str,
    score: int,
    classification: str,
    factors: list[str],
    source_type: str = "texto",
) -> int:
    """Guarda un analisis y retorna su ID."""
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
            source_type
        )
        VALUES (?, ?, ?, ?, ?)
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
    """Obtiene un analisis por su ID."""
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

    return _deserialize_row(row)


def list_analyses(limit: int = 20, offset: int = 0) -> list[dict]:
    """Lista los analisis mas recientes primero, con paginacion simple."""
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

    return [_deserialize_row(row) for row in rows]
