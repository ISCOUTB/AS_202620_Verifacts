from pathlib import Path
import sqlite3


BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
DATABASE_PATH = DATA_DIR / "verifacts.db"


def initialize_database() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(DATABASE_PATH) as connection:
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


def save_analysis(
    content: str,
    score: int,
    classification: str,
    factors: list[str],
) -> int:
    initialize_database()

    factors_text = " | ".join(factors)

    with sqlite3.connect(DATABASE_PATH) as connection:
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

        return int(cursor.lastrowid)


def get_analysis(analysis_id: int) -> dict | None:
    initialize_database()

    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.row_factory = sqlite3.Row

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

    if row is None:
        return None

    return dict(row)