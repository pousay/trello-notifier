# Trello Telegram Bot 🤖

A professional Telegram bot that monitors a Trello board and sends real-time
notifications about card changes — new tasks, moves, updates, and deletions.

---

## Features

- 🔔 Detects **future** Trello events only (ignores history before first run)
- 📋 Tracks: **new cards**, **moved cards**, **updated cards**, **deleted cards**
- 👤 Shows who performed the action and who is assigned
- 🔗 Includes a direct link to the Trello board
- ✅ Inline **Done** button to dismiss notifications
- 📡 `/status` — check if the bot is running
- 📦 `/all` — list every card on the board
- 🃏 `/card <name>` — show all tasks in a specific list/card

---

## Project Structure

```
trello_telegram_bot/
├── src/
│   ├── bot/
│   │   ├── __init__.py
│   │   ├── handlers/
│   │   │   ├── __init__.py
│   │   │   ├── commands.py      # /status, /all, /card
│   │   │   └── callbacks.py     # Inline keyboard callbacks
│   │   ├── keyboards.py         # Inline keyboard builders
│   │   └── formatters.py        # Message formatters
│   ├── trello/
│   │   ├── __init__.py
│   │   ├── base.py              # Abstract event tracker
│   │   ├── client.py            # Trello API client
│   │   ├── models.py            # Pydantic models
│   │   └── tracker.py           # Concrete Trello tracker
│   ├── config.py                # Settings via pydantic-settings
│   └── scheduler.py             # Polling scheduler
├── logs/                        # Log files (auto-created)
├── .env.example
├── .gitignore
├── LICENSE
├── README.md
├── requirements.txt
└── main.py
```

---

## Setup

### 1. Clone & install dependencies

```bash
git clone <repo-url>
cd trello_telegram_bot
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

| Variable | Description |
|---|---|
| `TELEGRAM_BOT_TOKEN` | From [@BotFather](https://t.me/BotFather) |
| `TELEGRAM_CHAT_ID` | Target chat/group ID |
| `TRELLO_API_KEY` | From https://trello.com/app-key |
| `TRELLO_API_TOKEN` | OAuth token from Trello |
| `TRELLO_BOARD_ID` | Board ID from the board URL |
| `POLL_INTERVAL_SECONDS` | How often to check (default: 30) |

### 3. Get Trello credentials

1. Go to https://trello.com/app-key — copy your **API Key**
2. On the same page, click "Generate a Token" — copy the **Token**
3. Find your **Board ID** from the board URL:
   `https://trello.com/b/<BOARD_ID>/board-name`

### 4. Run

```bash
python main.py
```

---

## Bot Commands

| Command | Description |
|---|---|
| `/status` | Check if bot and Trello connection are healthy |
| `/all` | List all cards on the board grouped by list |
| `/card <name>` | Show details of cards matching the given name |

---

## Linting

```bash
flake8 src/ main.py --max-line-length=100
```

---

## Requirements

- Python 3.11+
- Telegram bot token
- Trello API key + token
