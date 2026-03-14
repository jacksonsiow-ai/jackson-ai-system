from __future__ import annotations

from datetime import datetime
from typing import Awaitable, Callable

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dateutil import parser as date_parser

from memory.database import Database


class ReminderManager:
    def __init__(self, db: Database) -> None:
        self.db = db

    def add_reminder(self, message: str, remind_at: datetime, chat_id: int) -> int:
        return self.db.execute(
            "INSERT INTO reminders (message, remind_at, chat_id) VALUES (?, ?, ?)",
            (message.strip(), remind_at.isoformat(), chat_id),
        )

    def list_pending(self) -> list[dict]:
        rows = self.db.fetch_all(
            """
            SELECT id, message, remind_at, chat_id
            FROM reminders
            WHERE status = 'pending'
            ORDER BY remind_at ASC
            """
        )
        return [dict(r) for r in rows]

    def mark_sent(self, reminder_id: int) -> None:
        self.db.execute(
            "UPDATE reminders SET status='sent', sent_at=CURRENT_TIMESTAMP WHERE id = ?",
            (reminder_id,),
        )

    @staticmethod
    def parse_datetime(text: str) -> datetime | None:
        try:
            return date_parser.parse(text, fuzzy=True)
        except (ValueError, OverflowError):
            return None


class ReminderScheduler:
    """Polls reminders and sends notifications when due."""

    def __init__(
        self,
        reminder_manager: ReminderManager,
        send_callback: Callable[[int, str], Awaitable[None]],
    ):
        self.reminder_manager = reminder_manager
        self.send_callback = send_callback
        self.scheduler = AsyncIOScheduler()

    def start(self) -> None:
        self.scheduler.add_job(self._check_due_reminders, "interval", seconds=30)
        self.scheduler.start()

    def shutdown(self) -> None:
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)

    async def _check_due_reminders(self) -> None:
        now = datetime.now()
        for reminder in self.reminder_manager.list_pending():
            remind_at = datetime.fromisoformat(reminder["remind_at"])
            if remind_at <= now:
                text = f"⏰ Reminder: {reminder['message']}"
                await self.send_callback(reminder["chat_id"], text)
                self.reminder_manager.mark_sent(reminder["id"])
