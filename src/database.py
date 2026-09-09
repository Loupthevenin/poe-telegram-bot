import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from src.models import Watch


DATABASE_PATH = Path(os.getenv("DATABASE_PATH", "/app/data/poe_bot.db"))


def get_connection() -> sqlite3.Connection:
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row

    return connection


def init_database() -> None:
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS watches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_user_id INTEGER NOT NULL,
                league TEXT NOT NULL,
                query_id TEXT NOT NULL,
                url TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                created_at TEXT NOT NULL,
                last_event_at TEXT
            )
            """
        )

        connection.commit()


def create_watch(
    telegram_user_id: int,
    league: str,
    query_id: str,
    url: str,
) -> Watch:
    created_at = datetime.now(timezone.utc).isoformat()

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO watches (
                telegram_user_id,
                league,
                query_id,
                url,
                status,
                created_at
            )
            VALUES (?, ?, ?, ?, 'pending', ?)
            """,
            (
                telegram_user_id,
                league,
                query_id,
                url,
                created_at,
            ),
        )

        connection.commit()

        watch_id = cursor.lastrowid

    return get_watch(watch_id)


def get_watch(watch_id: int) -> Watch:
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT *
            FROM watches
            WHERE id = ?
            """,
            (watch_id,),
        ).fetchone()

    if row is None:
        raise ValueError(f"Watch {watch_id} introuvable")

    return row_to_watch(row)


def get_user_watches(telegram_user_id: int) -> list[Watch]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT *
            FROM watches
            WHERE telegram_user_id = ?
            ORDER BY id ASC
            """,
            (telegram_user_id,),
        ).fetchall()

    return [row_to_watch(row) for row in rows]


def delete_watch(
    watch_id: int,
    telegram_user_id: int,
) -> bool:
    with get_connection() as connection:
        cursor = connection.execute(
            """
            DELETE FROM watches
            WHERE id = ?
              AND telegram_user_id = ?
            """,
            (
                watch_id,
                telegram_user_id,
            ),
        )

        connection.commit()

        return cursor.rowcount > 0


def row_to_watch(row: sqlite3.Row) -> Watch:
    return Watch(
        id=row["id"],
        telegram_user_id=row["telegram_user_id"],
        league=row["league"],
        query_id=row["query_id"],
        url=row["url"],
        status=row["status"],
        created_at=datetime.fromisoformat(row["created_at"]),
        last_event_at=(
            datetime.fromisoformat(row["last_event_at"])
            if row["last_event_at"]
            else None
        ),
    )
