from __future__ import annotations

import logging
import os

from dotenv import load_dotenv

from ai.openai_client import OpenAIClient
from bot.telegram_bot import TelegramAssistantBot
from crm.crm_manager import CRMManager
from memory.database import Database
from memory.user_memory import UserMemory
from scheduler.reminder_scheduler import ReminderManager
from tasks.task_manager import TaskManager


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)


def main() -> None:
    load_dotenv()

    openai_api_key = os.getenv("OPENAI_API_KEY")
    telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")

    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY is missing. Add it to your .env file.")
    if not telegram_token:
        raise ValueError("TELEGRAM_BOT_TOKEN is missing. Add it to your .env file.")

    db = Database("assistant.db")
    ai_client = OpenAIClient(api_key=openai_api_key)
    task_manager = TaskManager(db)
    crm_manager = CRMManager(db)
    reminder_manager = ReminderManager(db)
    user_memory = UserMemory(db)

    bot = TelegramAssistantBot(
        token=telegram_token,
        ai_client=ai_client,
        task_manager=task_manager,
        crm_manager=crm_manager,
        reminder_manager=reminder_manager,
        user_memory=user_memory,
    )
    bot.run()


if __name__ == "__main__":
    main()
