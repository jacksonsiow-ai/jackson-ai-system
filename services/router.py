from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class RouteResult:
    intent: str
    payload: dict


class MessageRouter:
    """Keyword-based V1 router for module dispatch."""

    def route(self, message: str) -> RouteResult:
        text = message.strip()
        lower = text.lower()

        if lower.startswith("add task"):
            return RouteResult("add_task", {"title": text[8:].strip()})

        if "show my tasks" in lower or lower.startswith("list tasks"):
            return RouteResult("list_tasks", {})

        complete_match = re.search(r"mark task\s+(\d+)\s+complete", lower)
        if complete_match:
            return RouteResult("complete_task", {"task_id": int(complete_match.group(1))})

        if lower.startswith("save this note for"):
            content = text[len("save this note for") :].strip()
            if ":" in content:
                client_name, note = content.split(":", 1)
                return RouteResult(
                    "save_client_note",
                    {"client_name": client_name.strip(), "note": note.strip()},
                )
            return RouteResult("save_client_note", {"client_name": content, "note": ""})

        if lower.startswith("what did i discuss with"):
            client_name = text[len("what did i discuss with") :].strip().rstrip("?")
            client_name = re.sub(r"\s+last time$", "", client_name, flags=re.IGNORECASE).strip()
            return RouteResult("get_client_notes", {"client_name": client_name})

        if "remind me" in lower:
            return RouteResult("add_reminder", {"text": text})

        if lower.startswith("met ") or "meeting" in lower:
            return RouteResult("save_meeting_note", {"note": text})

        if lower.startswith("save memory"):
            return RouteResult("save_memory", {"text": text})

        if lower.startswith("get memory"):
            return RouteResult("get_memory", {"text": text})

        return RouteResult("general_chat", {"text": text})
