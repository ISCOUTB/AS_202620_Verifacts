import sqlite3
from typing import Any, Dict, List, Optional

DB_PATH = "verifacts.db"


def get_connection() -> sqlite3.Connection:
    """
    Crea y retorna una conexión a la base de datos SQLite.
    Configura el row_factory para acceder a las columnas por nombre.
    """
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def _migrate_schema(connection: sqlite3.Connection) -> None:
    """
    Agrega columnas nuevas a bases de datos creadas antes de esta
    ampliación, sin perder los datos ya guardados. SQLite no soporta
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
        # SQLite no permite DEFAULT CURRENT_TIMESTAMP en ALTER TABLE.
        # Agregamos la columna primero y rellenamos los registros existentes mediante UPDATE.
        connection.execute("ALTER TABLE analyses ADD COLUMN created_at TEXT")
        connection.execute(
            "UPDATE analyses SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL"
        )

    connection.commit()


def initialize_database() -> None:
    """
    Crea la tabla principal si no existe y aplica las migraciones necesarias.
    """
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                verdict TEXT NOT NULL,
                score REAL NOT NULL,
                explanation TEXT NOT NULL,
                source_type TEXT NOT NULL DEFAULT 'texto',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        _migrate_schema(connection)


def save_analysis(
    text: str,
    verdict: str,
    score: float,
    explanation: str,
    source_type: str = "texto",
) -> int:
    """
    Guarda un nuevo análisis en la base de datos y retorna su ID generado.
    """
    initialize_database()
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO analyses (text, verdict, score, explanation, source_type)
            VALUES (?, ?, ?, ?, ?)
            """,
            (text, verdict, score, explanation, source_type),
        )
        connection.commit()
        return cursor.lastrowid


def get_analysis(analysis_id: int) -> Optional[Dict[str, Any]]:
    """
    Obtiene un análisis específico por su ID. Retorna None si no existe.
    """
    initialize_database()
    with get_connection() as connection:
        cursor = connection.execute(
            """
            SELECT id, text, verdict, score, explanation, source_type, created_at
            FROM analyses
            WHERE id = ?
            """,
            (analysis_id,),
        )
        row = cursor.fetchone()
        if row is None:
            return None
        return dict(row)


def list_analyses() -> List[Dict[str, Any]]:
    """
    Retorna la lista de todos los análisis ordenados por fecha de creación descendente.
    """
    initialize_database()
    with get_connection() as connection:
        cursor = connection.execute(
            """
            SELECT id, text, verdict, score, explanation, source_type, created_at
            FROM analyses
            ORDER BY id DESC
            """
        )
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
