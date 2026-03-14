from __future__ import annotations

import logging
from typing import Any

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from ai.openai_client import OpenAIClient
from crm.crm_manager import CRMManager
from memory.user_memory import UserMemory
from scheduler.reminder_scheduler import ReminderManager, ReminderScheduler
from services.parsers import parse_get_memory_key, parse_memory_command, parse_reminder_request
from services.router import MessageRouter
from tasks.task_manager import TaskManager

logger = logging.getLogger(__name__)


class TelegramAssistantBot:
    def __init__(
        self,
        token: str,
        ai_client: OpenAIClient,
        task_manager: TaskManager,
        crm_manager: CRMManager,
        reminder_manager: ReminderManager,
        user_memory: UserMemory,
    ) -> None:
        self.ai_client = ai_client
        self.task_manager = task_manager
        self.crm_manager = crm_manager
        self.reminder_manager = reminder_manager
        self.user_memory = user_memory
        self.router = MessageRouter()

        self.reminder_scheduler = ReminderScheduler(
            reminder_manager=self.reminder_manager,
            send_callback=self._send_reminder_from_scheduler,
        )

        self.application = (
            Application.builder()
            .token(token)
            .post_init(self._on_startup)
            .post_shutdown(self._on_shutdown)
            .build()
        )
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

    async def _on_startup(self, application: Application) -> None:
        logger.info("Starting reminder scheduler...")
        self.reminder_scheduler.start()

    async def _on_shutdown(self, application: Application) -> None:
        logger.info("Stopping reminder scheduler...")
        self.reminder_scheduler.shutdown()

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text(
            "Hi Jackson! I'm your V1 assistant. "
            "You can ask me to manage tasks, reminders, CRM notes, and general chat."
        )

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not update.message:
            return

        text = update.message.text or ""
        chat_id = update.effective_chat.id

        route = self.router.route(text)
        response = await self._handle_route(route.intent, route.payload, chat_id)
        await update.message.reply_text(response)

    async def _handle_route(self, intent: str, payload: dict[str, Any], chat_id: int) -> str:
        if intent == "add_task":
            title = payload.get("title")
            if not title:
                return "Please provide a task title. Example: add task send proposal to Umah"
            task_id = self.task_manager.add_task(title)
            return f"✅ Task added (#{task_id}): {title}"

        if intent == "list_tasks":
            tasks = self.task_manager.list_tasks()
            if not tasks:
                return "You have no tasks yet."
            lines = ["📝 Your tasks:"]
            for task in tasks:
                status = "✅" if task["status"] == "completed" else "🔲"
                lines.append(f"{status} {task['id']}. {task['title']}")
            return "\n".join(lines)

        if intent == "complete_task":
            ok = self.task_manager.complete_task(payload["task_id"])
            return "✅ Task marked complete." if ok else "Task not found."

        if intent == "add_reminder":
            parsed = parse_reminder_request(payload["text"])
            if parsed.remind_at is None:
                return (
                    "I couldn't understand the reminder time. "
                    "Try: remind me tomorrow 2pm to follow up RE&S"
                )
            reminder_id = self.reminder_manager.add_reminder(parsed.reminder_text, parsed.remind_at, chat_id)
            return f"⏰ Reminder saved (#{reminder_id}) for {parsed.remind_at}."

        if intent == "save_client_note":
            client_name = payload["client_name"]
            note = payload.get("note", "")
            if not note:
                return "Use: save this note for <client>: <your note>"
            note_id = self.crm_manager.save_client_note(client_name, note)
            return f"📌 Saved client note (#{note_id}) for {client_name}."

        if intent == "save_meeting_note":
            note = payload["note"]
            note_id = self.crm_manager.save_meeting_note("General meeting", note)
            return f"📒 Meeting note saved (#{note_id})."

        if intent == "get_client_notes":
            client_name = payload["client_name"]
            notes = self.crm_manager.get_client_notes(client_name)
            if not notes:
                return f"No notes found for {client_name}."
            lines = [f"📂 Notes for {client_name}:"]
            for n in notes[:5]:
                lines.append(f"- {n['created_at']}: {n['note']}")
            return "\n".join(lines)

        if intent == "save_memory":
            parsed = parse_memory_command(payload["text"])
            if not parsed:
                return "Use: save memory key=value"
            key, value = parsed
            self.user_memory.save_memory(key, value)
            return f"🧠 Saved memory '{key}'."

        if intent == "get_memory":
            key = parse_get_memory_key(payload["text"])
            if not key:
                return "Use: get memory key"
            value = self.user_memory.get_memory(key)
            return f"🧠 {key} = {value}" if value else f"No memory found for '{key}'."

        context = self._build_context_for_ai()
        return self.ai_client.chat(payload.get("text", ""), context=context)

    def _build_context_for_ai(self) -> str:
        memory_items = self.user_memory.list_memory()
        if not memory_items:
            return "No saved long-term memory yet."
        return "\n".join([f"{item['memory_key']}: {item['memory_value']}" for item in memory_items])

    async def _send_reminder_from_scheduler(self, chat_id: int, text: str) -> None:
        await self.application.bot.send_message(chat_id=chat_id, text=text)

    def run(self) -> None:
        logger.info("Starting Telegram bot polling...")
        self.application.run_polling()
