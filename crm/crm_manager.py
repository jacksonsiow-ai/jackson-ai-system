from __future__ import annotations

from memory.database import Database


class CRMManager:
    def __init__(self, db: Database) -> None:
        self.db = db

    def save_client_note(self, client_name: str, note: str) -> int:
        return self.db.execute(
            "INSERT INTO client_notes (client_name, note) VALUES (?, ?)",
            (client_name.strip(), note.strip()),
        )

    def save_meeting_note(self, title: str, note: str) -> int:
        return self.db.execute(
            "INSERT INTO meeting_notes (title, note) VALUES (?, ?)",
            (title.strip(), note.strip()),
        )

    def get_client_notes(self, client_name: str) -> list[dict]:
        rows = self.db.fetch_all(
            """
            SELECT id, client_name, note, created_at
            FROM client_notes
            WHERE lower(client_name) = lower(?)
            ORDER BY id DESC
            LIMIT 10
            """,
            (client_name.strip(),),
        )
        return [dict(r) for r in rows]

    def get_recent_meeting_notes(self, title: str | None = None) -> list[dict]:
        if title:
            rows = self.db.fetch_all(
                """
                SELECT id, title, note, created_at
                FROM meeting_notes
                WHERE lower(title) LIKE lower(?)
                ORDER BY id DESC
                LIMIT 10
                """,
                (f"%{title.strip()}%",),
            )
        else:
            rows = self.db.fetch_all(
                "SELECT id, title, note, created_at FROM meeting_notes ORDER BY id DESC LIMIT 10"
            )
        return [dict(r) for r in rows]
