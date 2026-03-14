# Jackson AI Assistant (Version 1)

Version 1 is a practical, modular Telegram assistant for Jackson Siow. It supports:
- Telegram chat replies powered by OpenAI
- Task management (add/list/complete)
- CRM and meeting notes storage/retrieval
- Reminder scheduling with APScheduler
- Long-term memory storage in SQLite

## Project structure

```text
bot/
ai/
memory/
crm/
tasks/
scheduler/
services/
main.py
requirements.txt
README.md
.env.example
```

## 1) Install dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 2) Set up environment variables

```bash
cp .env.example .env
```

Fill in:
- `OPENAI_API_KEY`
- `TELEGRAM_BOT_TOKEN`

## 3) Run the bot

```bash
python main.py
```

The app will create `assistant.db` automatically on first run.

## 4) Basic usage examples

### General chat
- `help me plan tomorrow`

### Tasks
- `add task send proposal to Umah`
- `show my tasks`
- `mark task 1 complete`

### Reminders
- `remind me tomorrow 2pm to follow up RE&S`

### CRM / meeting memory
- `met RE&S today and they want CRM demo next Monday`
- `save this note for Koufu: discussed outlet rollout timeline`
- `what did I discuss with RE&S last time`

### Long-term user memory
- `save memory preferred_name=Jackson`
- `get memory preferred_name`

## Design notes for Version 1

- Router is keyword-based and intentionally simple to keep behavior transparent and easy to extend.
- Data is persisted in SQLite with structured tables for tasks, reminders, notes, and user memory.
- Reminder scheduler checks pending reminders every 30 seconds while the app is running.
- Architecture is split by domain so future expansion into specialized bots (sales, quotation, project, research, internal team) is straightforward.
