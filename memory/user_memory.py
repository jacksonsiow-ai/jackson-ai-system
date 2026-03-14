from __future__ import annotations

from memory.database import Database


class UserMemory:
    def __init__(self, db: Database) -> None:
        self.db = db

    def save_memory(self, key: str, value: str) -> None:
        self.db.execute(
            """
            INSERT INTO user_memory (memory_key, memory_value, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(memory_key)
            DO UPDATE SET memory_value=excluded.memory_value, updated_at=CURRENT_TIMESTAMP
            """,
            (key.strip(), value.strip()),
        )

    def get_memory(self, key: str) -> str | None:
        row = self.db.fetch_one(
            "SELECT memory_value FROM user_memory WHERE memory_key = ?", (key.strip(),)
        )
        return row["memory_value"] if row else None

    def list_memory(self) -> list[dict]:
        rows = self.db.fetch_all(
            "SELECT memory_key, memory_value, updated_at FROM user_memory ORDER BY memory_key"
        )
        return [dict(r) for r in rows]
