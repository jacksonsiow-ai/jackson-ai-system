from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime

from scheduler.reminder_scheduler import ReminderManager


@dataclass
class ReminderParseResult:
    reminder_text: str
    remind_at: datetime | None


def parse_reminder_request(user_text: str) -> ReminderParseResult:
    # Example: remind me tomorrow 2pm to follow up RE&S
    match = re.search(r"remind me\s+(.+?)\s+to\s+(.+)", user_text, re.IGNORECASE)
    if not match:
        return ReminderParseResult(reminder_text=user_text, remind_at=None)

    datetime_text = match.group(1).strip()
    reminder_text = match.group(2).strip()
    remind_at = ReminderManager.parse_datetime(datetime_text)
    return ReminderParseResult(reminder_text=reminder_text, remind_at=remind_at)


def parse_memory_command(user_text: str) -> tuple[str, str] | None:
    # save memory preferred_name=Jackson
    match = re.search(r"save memory\s+([^=\s]+)\s*=\s*(.+)", user_text, re.IGNORECASE)
    if not match:
        return None
    return match.group(1).strip(), match.group(2).strip()


def parse_get_memory_key(user_text: str) -> str | None:
    match = re.search(r"get memory\s+(.+)", user_text, re.IGNORECASE)
    if not match:
        return None
    return match.group(1).strip()
