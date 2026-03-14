from __future__ import annotations

from memory.database import Database


class TaskManager:
    def __init__(self, db: Database) -> None:
        self.db = db

    def add_task(self, title: str) -> int:
        return self.db.execute("INSERT INTO tasks (title) VALUES (?)", (title.strip(),))

    def list_tasks(self) -> list[dict]:
        rows = self.db.fetch_all(
            "SELECT id, title, status, created_at, completed_at FROM tasks ORDER BY id DESC"
        )
        return [dict(r) for r in rows]

    def complete_task(self, task_id: int) -> bool:
        row = self.db.fetch_one("SELECT id FROM tasks WHERE id = ?", (task_id,))
        if row is None:
            return False
        self.db.execute(
            """
            UPDATE tasks
            SET status = 'completed', completed_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (task_id,),
        )
        return True
