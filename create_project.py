#!/usr/bin/env python3
"""
Project scaffolding script for Trello-Telegram Bot.
Run this script to generate the full project structure.
"""

import os
import stat

PROJECT_NAME = "trello_telegram_bot"

FILES = {}

# ── .gitignore ────────────────────────────────────────────────────────────────
FILES[".gitignore"] = """\
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
dist/
*.egg-info/
.eggs/

# Virtual environments
.venv/
venv/
env/

# Environment variables
.env
.env.*
!.env.example

# Logs
logs/
*.log

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Testing
.pytest_cache/
.coverage
htmlcov/

# mypy
.mypy_cache/
"""

# ── LICENSE ───────────────────────────────────────────────────────────────────
FILES["LICENSE"] = """\
MIT License

Copyright (c) 2026

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

# ── README.md ─────────────────────────────────────────────────────────────────
FILES["README.md"] = """\
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
source .venv/bin/activate      # Windows: .venv\\Scripts\\activate
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
"""

# ── .env.example ──────────────────────────────────────────────────────────────
FILES[".env.example"] = """\
# Telegram
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

# Trello
TRELLO_API_KEY=your_trello_api_key_here
TRELLO_API_TOKEN=your_trello_api_token_here
TRELLO_BOARD_ID=your_board_id_here
TRELLO_WORKSPACE=your_workspace_slug_here

# Polling
POLL_INTERVAL_SECONDS=30

# Logging
LOG_LEVEL=INFO
"""

# ── requirements.txt ──────────────────────────────────────────────────────────
FILES["requirements.txt"] = """\
aiogram==3.7.0
aiohttp==3.9.5
pydantic==2.7.1
pydantic-settings==2.3.1
python-dotenv==1.0.1
flake8==7.0.0
"""

# ── main.py ───────────────────────────────────────────────────────────────────
FILES["main.py"] = """\
#!/usr/bin/env python3
\"\"\"Entry point for the Trello Telegram Bot.\"\"\"

import asyncio
import logging

from src.config import get_settings
from src.bot.app import create_bot
from src.scheduler import PollingScheduler
from src.trello.tracker import TrelloEventTracker
from src.trello.client import TrelloClient

logger = logging.getLogger(__name__)


def setup_logging(level: str) -> None:
    \"\"\"Configure root logger with both console and file handlers.\"\"\"
    import os
    os.makedirs("logs", exist_ok=True)

    fmt = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    date_fmt = "%Y-%m-%d %H:%M:%S"
    formatter = logging.Formatter(fmt, datefmt=date_fmt)

    root = logging.getLogger()
    root.setLevel(getattr(logging, level.upper(), logging.INFO))

    console = logging.StreamHandler()
    console.setFormatter(formatter)
    root.addHandler(console)

    file_handler = logging.FileHandler("logs/bot.log", encoding="utf-8")
    file_handler.setFormatter(formatter)
    root.addHandler(file_handler)


async def main() -> None:
    \"\"\"Bootstrap and run the bot + polling scheduler concurrently.\"\"\"
    settings = get_settings()
    setup_logging(settings.log_level)

    logger.info("Starting Trello Telegram Bot...")
    logger.info(
        "Board: %s | Poll interval: %ss",
        settings.trello_board_id,
        settings.poll_interval_seconds,
    )

    trello_client = TrelloClient(
        api_key=settings.trello_api_key,
        api_token=settings.trello_api_token,
        board_id=settings.trello_board_id,
    )

    tracker = TrelloEventTracker(client=trello_client)

    bot, dp = create_bot(settings=settings, trello_client=trello_client)

    scheduler = PollingScheduler(
        tracker=tracker,
        bot=bot,
        chat_id=settings.telegram_chat_id,
        interval=settings.poll_interval_seconds,
    )

    async with bot.session:
        await asyncio.gather(
            dp.start_polling(bot),
            scheduler.run(),
        )


if __name__ == "__main__":
    asyncio.run(main())
"""

# ── src/__init__.py ───────────────────────────────────────────────────────────
FILES["src/__init__.py"] = '"""Trello Telegram Bot package."""\n'

# ── src/config.py ─────────────────────────────────────────────────────────────
FILES["src/config.py"] = """\
\"\"\"Application configuration via pydantic-settings.\"\"\"

from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    \"\"\"All runtime configuration loaded from environment / .env file.\"\"\"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Telegram
    telegram_bot_token: str = Field(..., description="Telegram bot token from BotFather")
    telegram_chat_id: int = Field(..., description="Target Telegram chat/group ID")

    # Trello
    trello_api_key: str = Field(..., description="Trello REST API key")
    trello_api_token: str = Field(..., description="Trello OAuth token")
    trello_board_id: str = Field(..., description="Trello board ID")
    trello_workspace: str = Field("", description="Trello workspace slug (optional)")

    # Polling
    poll_interval_seconds: int = Field(30, ge=10, description="Seconds between polls")

    # Logging
    log_level: str = Field("INFO", description="Logging level")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    \"\"\"Return cached Settings instance.\"\"\"
    return Settings()
"""

# ── src/scheduler.py ──────────────────────────────────────────────────────────
FILES["src/scheduler.py"] = """\
\"\"\"Async polling scheduler that bridges the Trello tracker and Telegram bot.\"\"\"

import asyncio
import logging

from aiogram import Bot

from src.trello.base import AbstractEventTracker
from src.trello.models import TrelloEvent, EventType
from src.bot.formatters import format_event
from src.bot.keyboards import done_keyboard

logger = logging.getLogger(__name__)


class PollingScheduler:
    \"\"\"Polls the Trello tracker at a fixed interval and dispatches messages.\"\"\"

    def __init__(
        self,
        tracker: AbstractEventTracker,
        bot: Bot,
        chat_id: int,
        interval: int = 30,
    ) -> None:
        self._tracker = tracker
        self._bot = bot
        self._chat_id = chat_id
        self._interval = interval

    async def run(self) -> None:
        \"\"\"Run the polling loop indefinitely.\"\"\"
        logger.info("Polling scheduler started (interval=%ss)", self._interval)

        # Initialise snapshot — establishes baseline, fires no notifications
        await self._tracker.initialise()
        logger.info("Tracker initialised — watching for new events only.")

        while True:
            await asyncio.sleep(self._interval)
            try:
                events: list[TrelloEvent] = await self._tracker.poll()
                for event in events:
                    await self._dispatch(event)
            except Exception:
                logger.exception("Error during poll cycle")

    async def _dispatch(self, event: TrelloEvent) -> None:
        \"\"\"Send a single event notification to Telegram.\"\"\"
        text = format_event(event)
        markup = done_keyboard()
        try:
            await self._bot.send_message(
                chat_id=self._chat_id,
                text=text,
                parse_mode="HTML",
                reply_markup=markup,
                disable_web_page_preview=True,
            )
            logger.info(
                "Dispatched event type=%s card=%s",
                event.event_type.value,
                event.card_name,
            )
        except Exception:
            logger.exception("Failed to send event notification for card %s", event.card_name)
"""

# ── src/trello/__init__.py ────────────────────────────────────────────────────
FILES["src/trello/__init__.py"] = '"""Trello integration package."""\n'

# ── src/trello/models.py ──────────────────────────────────────────────────────
FILES["src/trello/models.py"] = """\
\"\"\"Pydantic models for Trello domain objects.\"\"\"

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, HttpUrl


class EventType(str, Enum):
    \"\"\"Supported Trello event categories.\"\"\"

    NEW_TASK = "new_task"
    TASK_DELETED = "task_deleted"
    TASK_MOVED = "task_moved"
    TASK_UPDATED = "task_updated"


class TrelloMember(BaseModel):
    \"\"\"A Trello workspace member.\"\"\"

    id: str
    full_name: str
    username: str


class TrelloCard(BaseModel):
    \"\"\"Snapshot of a Trello card.\"\"\"

    id: str
    name: str
    desc: str = ""
    list_id: str
    list_name: str = ""
    members: list[TrelloMember] = Field(default_factory=list)
    short_url: str = ""
    due: Optional[datetime] = None
    closed: bool = False
    last_activity: Optional[datetime] = None


class TrelloList(BaseModel):
    \"\"\"A column / list on a Trello board.\"\"\"

    id: str
    name: str
    closed: bool = False


class TrelloEvent(BaseModel):
    \"\"\"A detected change on the Trello board.\"\"\"

    event_type: EventType
    card_id: str
    card_name: str
    card_url: str = ""
    card_desc: str = ""

    # Who triggered the event
    actor: Optional[TrelloMember] = None

    # Who is assigned / mentioned
    assignees: list[TrelloMember] = Field(default_factory=list)

    # For move events
    from_list: Optional[str] = None
    to_list: Optional[str] = None

    # Metadata
    occurred_at: datetime = Field(default_factory=datetime.utcnow)
    board_url: str = ""

    # Raw action id so we can deduplicate
    action_id: str = ""


class BoardSnapshot(BaseModel):
    \"\"\"Full state of a board at a point in time.\"\"\"

    cards: dict[str, TrelloCard] = Field(default_factory=dict)
    lists: dict[str, TrelloList] = Field(default_factory=dict)
    # last processed Trello action id
    last_action_id: Optional[str] = None
"""

# ── src/trello/base.py ────────────────────────────────────────────────────────
FILES["src/trello/base.py"] = """\
\"\"\"Abstract base class for board event trackers.

Designed to be reusable across projects — swap out the concrete implementation
to track Jira, Asana, GitHub Projects, etc.
\"\"\"

from abc import ABC, abstractmethod

from src.trello.models import TrelloEvent, BoardSnapshot


class AbstractEventTracker(ABC):
    \"\"\"Contract that all board event trackers must satisfy.\"\"\"

    @abstractmethod
    async def initialise(self) -> None:
        \"\"\"
        Establish an initial snapshot of the board state.

        Called once at startup. Implementations MUST NOT emit events here —
        the purpose is only to record the current state so that subsequent
        calls to ``poll()`` can compute a diff.
        \"\"\"

    @abstractmethod
    async def poll(self) -> list[TrelloEvent]:
        \"\"\"
        Compare current board state to the stored snapshot.

        Returns a list of events that occurred since the last call.
        The internal snapshot must be updated after each call so that
        events are not reported twice.
        \"\"\"

    @abstractmethod
    async def get_snapshot(self) -> BoardSnapshot:
        \"\"\"Return the current (latest fetched) board snapshot.\"\"\"
"""

# ── src/trello/client.py ──────────────────────────────────────────────────────
FILES["src/trello/client.py"] = """\
\"\"\"Low-level async Trello REST API client.\"\"\"

import logging
from typing import Any, Optional

import aiohttp

logger = logging.getLogger(__name__)

_BASE = "https://api.trello.com/1"


class TrelloClient:
    \"\"\"Thin async wrapper around the Trello REST API.\"\"\"

    def __init__(self, api_key: str, api_token: str, board_id: str) -> None:
        self._auth = {"key": api_key, "token": api_token}
        self._board_id = board_id
        self._session: Optional[aiohttp.ClientSession] = None

    # ── Session lifecycle ───────────────────────────────────────────────────

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def close(self) -> None:
        \"\"\"Close the underlying HTTP session.\"\"\"
        if self._session and not self._session.closed:
            await self._session.close()

    # ── Generic request helper ──────────────────────────────────────────────

    async def _get(self, path: str, **params: Any) -> Any:
        \"\"\"Perform a GET request and return parsed JSON.\"\"\"
        session = await self._get_session()
        url = f"{_BASE}{path}"
        query = {**self._auth, **params}
        async with session.get(url, params=query) as resp:
            resp.raise_for_status()
            return await resp.json()

    # ── Board-level endpoints ───────────────────────────────────────────────

    async def get_board(self) -> dict[str, Any]:
        \"\"\"Fetch board metadata.\"\"\"
        return await self._get(f"/boards/{self._board_id}")

    async def get_lists(self) -> list[dict[str, Any]]:
        \"\"\"Fetch all open lists on the board.\"\"\"
        return await self._get(
            f"/boards/{self._board_id}/lists",
            filter="open",
        )

    async def get_cards(self) -> list[dict[str, Any]]:
        \"\"\"Fetch all open cards with member info.\"\"\"
        return await self._get(
            f"/boards/{self._board_id}/cards",
            filter="open",
            members="true",
            member_fields="fullName,username",
            fields="id,name,desc,idList,shortUrl,due,closed,dateLastActivity",
        )

    async def get_actions(
        self,
        since: Optional[str] = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        \"\"\"
        Fetch board action log.

        Parameters
        ----------
        since:
            A Trello action ID. When provided only actions *after* this id
            are returned.
        limit:
            Maximum number of actions to return (max 1000).
        \"\"\"
        params: dict[str, Any] = {
            "filter": "createCard,updateCard,deleteCard",
            "limit": limit,
            "memberCreator": "true",
            "memberCreator_fields": "fullName,username",
        }
        if since:
            params["since"] = since
        return await self._get(f"/boards/{self._board_id}/actions", **params)

    async def get_members(self) -> list[dict[str, Any]]:
        \"\"\"Fetch all board members.\"\"\"
        return await self._get(
            f"/boards/{self._board_id}/members",
            fields="fullName,username",
        )

    async def get_card(self, card_id: str) -> dict[str, Any]:
        \"\"\"Fetch a single card.\"\"\"
        return await self._get(
            f"/cards/{card_id}",
            members="true",
            member_fields="fullName,username",
            fields="id,name,desc,idList,shortUrl,due,closed,dateLastActivity",
        )
"""

# ── src/trello/tracker.py ─────────────────────────────────────────────────────
FILES["src/trello/tracker.py"] = """\
\"\"\"Concrete Trello board event tracker.\"\"\"

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Optional

from src.trello.base import AbstractEventTracker
from src.trello.client import TrelloClient
from src.trello.models import (
    BoardSnapshot,
    EventType,
    TrelloCard,
    TrelloEvent,
    TrelloList,
    TrelloMember,
)

logger = logging.getLogger(__name__)


def _parse_member(raw: dict) -> TrelloMember:
    return TrelloMember(
        id=raw["id"],
        full_name=raw.get("fullName", raw.get("full_name", "Unknown")),
        username=raw.get("username", ""),
    )


def _parse_card(raw: dict, lists: dict[str, TrelloList]) -> TrelloCard:
    list_id = raw.get("idList", "")
    list_name = lists[list_id].name if list_id in lists else ""
    members = [_parse_member(m) for m in raw.get("members", [])]
    due_raw = raw.get("due")
    last_raw = raw.get("dateLastActivity")
    return TrelloCard(
        id=raw["id"],
        name=raw["name"],
        desc=raw.get("desc", ""),
        list_id=list_id,
        list_name=list_name,
        members=members,
        short_url=raw.get("shortUrl", ""),
        due=datetime.fromisoformat(due_raw.replace("Z", "+00:00")) if due_raw else None,
        closed=raw.get("closed", False),
        last_activity=(
            datetime.fromisoformat(last_raw.replace("Z", "+00:00")) if last_raw else None
        ),
    )


class TrelloEventTracker(AbstractEventTracker):
    \"\"\"
    Polls a Trello board for changes and emits structured events.

    Strategy
    --------
    - On ``initialise()``, fetch the current action log and record the newest
      action id as our cursor.  No events are emitted.
    - On each ``poll()``, fetch actions *after* the cursor, parse them into
      ``TrelloEvent`` objects, and advance the cursor.
    \"\"\"

    def __init__(self, client: TrelloClient) -> None:
        self._client = client
        self._snapshot: BoardSnapshot = BoardSnapshot()
        self._board_url: str = ""

    # ── AbstractEventTracker implementation ─────────────────────────────────

    async def initialise(self) -> None:
        \"\"\"Record the current board state without emitting events.\"\"\"
        await self._refresh_snapshot()
        actions = await self._client.get_actions(limit=1)
        if actions:
            self._snapshot.last_action_id = actions[0]["id"]
            logger.debug("Cursor initialised at action %s", self._snapshot.last_action_id)
        else:
            logger.debug("No previous actions found; cursor is empty.")

    async def poll(self) -> list[TrelloEvent]:
        \"\"\"Return events that occurred since the last poll.\"\"\"
        actions = await self._client.get_actions(
            since=self._snapshot.last_action_id,
            limit=100,
        )
        if not actions:
            return []

        # Actions are newest-first; reverse so we process chronologically
        actions = list(reversed(actions))

        # Advance cursor to the newest action we received
        self._snapshot.last_action_id = actions[-1]["id"]

        # Refresh snapshot so we have up-to-date list names etc.
        await self._refresh_snapshot()

        events: list[TrelloEvent] = []
        for action in actions:
            event = self._parse_action(action)
            if event:
                events.append(event)

        logger.info("Poll complete: %d new event(s)", len(events))
        return events

    async def get_snapshot(self) -> BoardSnapshot:
        return self._snapshot

    # ── Internal helpers ─────────────────────────────────────────────────────

    async def _refresh_snapshot(self) -> None:
        \"\"\"Fetch lists and cards from Trello and update the in-memory snapshot.\"\"\"
        board_data = await self._client.get_board()
        self._board_url = (
            f"https://trello.com/b/{board_data['shortLink']}/{board_data['name']}"
        )

        raw_lists = await self._client.get_lists()
        lists: dict[str, TrelloList] = {
            lst["id"]: TrelloList(id=lst["id"], name=lst["name"], closed=lst.get("closed", False))
            for lst in raw_lists
        }

        raw_cards = await self._client.get_cards()
        cards: dict[str, TrelloCard] = {
            c["id"]: _parse_card(c, lists) for c in raw_cards
        }

        self._snapshot.lists = lists
        self._snapshot.cards = cards

    def _parse_action(self, action: dict) -> Optional[TrelloEvent]:
        \"\"\"Map a raw Trello action dict to a ``TrelloEvent``.\"\"\"
        action_type = action.get("type", "")
        data = action.get("data", {})
        creator_raw = action.get("memberCreator", {})

        actor: Optional[TrelloMember] = None
        if creator_raw:
            actor = TrelloMember(
                id=creator_raw["id"],
                full_name=creator_raw.get("fullName", "Unknown"),
                username=creator_raw.get("username", ""),
            )

        card_data = data.get("card", {})
        card_id = card_data.get("id", "")
        card_name = card_data.get("name", "Unknown card")
        card_url = self._snapshot.cards.get(card_id, TrelloCard(
            id=card_id, name=card_name, list_id=""
        )).short_url or ""

        # Assigned members from snapshot
        assignees = self._snapshot.cards.get(card_id, TrelloCard(
            id=card_id, name=card_name, list_id=""
        )).members

        date_raw = action.get("date", "")
        occurred_at = (
            datetime.fromisoformat(date_raw.replace("Z", "+00:00"))
            if date_raw
            else datetime.now(tz=timezone.utc)
        )

        base_kwargs = dict(
            card_id=card_id,
            card_name=card_name,
            card_url=card_url,
            card_desc=card_data.get("desc", ""),
            actor=actor,
            assignees=assignees,
            occurred_at=occurred_at,
            board_url=self._board_url,
            action_id=action.get("id", ""),
        )

        if action_type == "createCard":
            list_name = data.get("list", {}).get("name", "")
            return TrelloEvent(
                event_type=EventType.NEW_TASK,
                to_list=list_name,
                **base_kwargs,
            )

        if action_type == "deleteCard":
            return TrelloEvent(
                event_type=EventType.TASK_DELETED,
                **base_kwargs,
            )

        if action_type == "updateCard":
            old_data = data.get("old", {})

            # Moved between lists
            if "idList" in old_data:
                from_list_id = old_data.get("idList", "")
                to_list_id = card_data.get("idList", data.get("listAfter", {}).get("id", ""))
                from_name = (
                    data.get("listBefore", {}).get("name")
                    or self._snapshot.lists.get(from_list_id, TrelloList(
                        id=from_list_id, name=from_list_id
                    )).name
                )
                to_name = (
                    data.get("listAfter", {}).get("name")
                    or self._snapshot.lists.get(to_list_id, TrelloList(
                        id=to_list_id, name=to_list_id
                    )).name
                )
                return TrelloEvent(
                    event_type=EventType.TASK_MOVED,
                    from_list=from_name,
                    to_list=to_name,
                    **base_kwargs,
                )

            # General update (name, desc, due, etc.)
            changed_fields = list(old_data.keys())
            if changed_fields:
                return TrelloEvent(
                    event_type=EventType.TASK_UPDATED,
                    card_desc=", ".join(changed_fields),  # surfaced as "changed fields"
                    **base_kwargs,
                )

        return None
"""

# ── src/bot/__init__.py ───────────────────────────────────────────────────────
FILES["src/bot/__init__.py"] = '"""Telegram bot package."""\n'

# ── src/bot/app.py ────────────────────────────────────────────────────────────
FILES["src/bot/app.py"] = """\
\"\"\"Bot and dispatcher factory.\"\"\"

import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from src.config import Settings
from src.trello.client import TrelloClient
from src.bot.handlers import register_handlers

logger = logging.getLogger(__name__)


def create_bot(settings: Settings, trello_client: TrelloClient) -> tuple[Bot, Dispatcher]:
    \"\"\"Instantiate and configure the bot and dispatcher.\"\"\"
    bot = Bot(
        token=settings.telegram_bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()
    register_handlers(dp, trello_client=trello_client)
    logger.info("Bot and dispatcher ready.")
    return bot, dp
"""

# ── src/bot/handlers/__init__.py ──────────────────────────────────────────────
FILES["src/bot/handlers/__init__.py"] = """\
\"\"\"Handler registration.\"\"\"

from aiogram import Dispatcher

from src.trello.client import TrelloClient
from src.bot.handlers.commands import build_commands_router
from src.bot.handlers.callbacks import build_callbacks_router


def register_handlers(dp: Dispatcher, trello_client: TrelloClient) -> None:
    \"\"\"Attach all routers to the dispatcher.\"\"\"
    dp.include_router(build_commands_router(trello_client))
    dp.include_router(build_callbacks_router())
"""

# ── src/bot/handlers/commands.py ─────────────────────────────────────────────
FILES["src/bot/handlers/commands.py"] = """\
\"\"\"Command handlers: /status, /all, /card.\"\"\"

import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from src.trello.client import TrelloClient
from src.trello.models import TrelloList

logger = logging.getLogger(__name__)


def build_commands_router(trello_client: TrelloClient) -> Router:
    \"\"\"Return a router with all command handlers bound to ``trello_client``.\"\"\"
    router = Router(name="commands")

    @router.message(Command("status"))
    async def cmd_status(message: Message) -> None:
        \"\"\"Check bot and Trello API health.\"\"\"
        logger.info("/status requested by user %s", message.from_user.id if message.from_user else "?")
        try:
            board = await trello_client.get_board()
            name = board.get("name", "Unknown")
            await message.answer(
                f"✅ <b>Bot is running.</b>\\n"
                f"📋 Connected to board: <b>{name}</b>"
            )
        except Exception as exc:
            logger.exception("Trello health-check failed")
            await message.answer(f"⚠️ Bot is running but Trello check failed:\\n<code>{exc}</code>")

    @router.message(Command("all"))
    async def cmd_all(message: Message) -> None:
        \"\"\"List every open card grouped by list.\"\"\"
        logger.info("/all requested by user %s", message.from_user.id if message.from_user else "?")
        try:
            raw_lists = await trello_client.get_lists()
            raw_cards = await trello_client.get_cards()

            lists: dict[str, str] = {lst["id"]: lst["name"] for lst in raw_lists}
            grouped: dict[str, list[str]] = {name: [] for name in lists.values()}

            for card in raw_cards:
                list_name = lists.get(card["idList"], "Unknown")
                grouped.setdefault(list_name, []).append(card["name"])

            if not any(grouped.values()):
                await message.answer("📭 No open cards found on this board.")
                return

            lines = ["📋 <b>All Cards on Board</b>\\n"]
            for list_name, cards in grouped.items():
                if cards:
                    lines.append(f"\\n<b>📁 {list_name}</b>")
                    for card_name in cards:
                        lines.append(f"  • {card_name}")

            await message.answer("\\n".join(lines))
        except Exception as exc:
            logger.exception("Failed to fetch all cards")
            await message.answer(f"❌ Could not fetch cards:\\n<code>{exc}</code>")

    @router.message(Command("card"))
    async def cmd_card(message: Message) -> None:
        \"\"\"Show details of cards whose name contains the given query.\"\"\"
        logger.info("/card requested by user %s", message.from_user.id if message.from_user else "?")
        if not message.text:
            await message.answer("Usage: /card <card name>")
            return

        parts = message.text.split(maxsplit=1)
        if len(parts) < 2 or not parts[1].strip():
            await message.answer("Usage: /card <card name>")
            return

        query = parts[1].strip().lower()

        try:
            raw_lists = await trello_client.get_lists()
            raw_cards = await trello_client.get_cards()
            lists: dict[str, str] = {lst["id"]: lst["name"] for lst in raw_lists}

            matches = [c for c in raw_cards if query in c["name"].lower()]

            if not matches:
                await message.answer(f'🔍 No cards matching "<b>{query}</b>" found.')
                return

            lines = [f'🔍 <b>Cards matching "{query}"</b>\\n']
            for card in matches:
                list_name = lists.get(card["idList"], "Unknown")
                members = card.get("members", [])
                assigned = (
                    ", ".join(m.get("fullName", m.get("username", "?")) for m in members)
                    or "Unassigned"
                )
                desc = card.get("desc", "").strip()
                due = card.get("due", None)

                lines.append(f"\\n<b>🃏 {card['name']}</b>")
                lines.append(f"  📁 List: {list_name}")
                lines.append(f"  👤 Assigned: {assigned}")
                if due:
                    lines.append(f"  ⏰ Due: {due[:10]}")
                if desc:
                    lines.append(f"  📝 {desc[:120]}{'...' if len(desc) > 120 else ''}")
                lines.append(f'  🔗 <a href="{card.get("shortUrl", "")}">Open card</a>')

            await message.answer("\\n".join(lines), disable_web_page_preview=True)
        except Exception as exc:
            logger.exception("Failed to fetch card details")
            await message.answer(f"❌ Could not fetch card:\\n<code>{exc}</code>")

    return router
"""

# ── src/bot/handlers/callbacks.py ────────────────────────────────────────────
FILES["src/bot/handlers/callbacks.py"] = """\
\"\"\"Inline keyboard callback handlers.\"\"\"

import logging

from aiogram import Router
from aiogram.types import CallbackQuery

logger = logging.getLogger(__name__)

DONE_CALLBACK = "done"


def build_callbacks_router() -> Router:
    \"\"\"Return a router for inline keyboard callbacks.\"\"\"
    router = Router(name="callbacks")

    @router.callback_query(lambda c: c.data == DONE_CALLBACK)
    async def handle_done(callback: CallbackQuery) -> None:
        \"\"\"Delete the notification message when the user taps Done.\"\"\"
        logger.info(
            "Done callback from user %s on message %s",
            callback.from_user.id if callback.from_user else "?",
            callback.message.message_id if callback.message else "?",
        )
        if callback.message:
            try:
                await callback.message.delete()
            except Exception:
                logger.warning("Could not delete message; it may already be gone.")
        await callback.answer()

    return router
"""

# ── src/bot/keyboards.py ──────────────────────────────────────────────────────
FILES["src/bot/keyboards.py"] = """\
\"\"\"Reusable inline keyboard builders.\"\"\"

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from src.bot.handlers.callbacks import DONE_CALLBACK


def done_keyboard() -> InlineKeyboardMarkup:
    \"\"\"Return an inline keyboard with a single ✅ Done button.\"\"\"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Done", callback_data=DONE_CALLBACK)]
        ]
    )
"""

# ── src/bot/formatters.py ─────────────────────────────────────────────────────
FILES["src/bot/formatters.py"] = """\
\"\"\"Human-readable Telegram message formatters for Trello events.\"\"\"

from src.trello.models import EventType, TrelloEvent

_EMOJI: dict[EventType, str] = {
    EventType.NEW_TASK: "🆕",
    EventType.TASK_DELETED: "🗑️",
    EventType.TASK_MOVED: "🔀",
    EventType.TASK_UPDATED: "✏️",
}

_LABEL: dict[EventType, str] = {
    EventType.NEW_TASK: "New Task Created",
    EventType.TASK_DELETED: "Task Deleted",
    EventType.TASK_MOVED: "Task Moved",
    EventType.TASK_UPDATED: "Task Updated",
}


def format_event(event: TrelloEvent) -> str:
    \"\"\"Render a ``TrelloEvent`` as a nicely formatted HTML message.\"\"\"
    emoji = _EMOJI[event.event_type]
    label = _LABEL[event.event_type]

    actor_name = (
        f"{event.actor.full_name} (@{event.actor.username})"
        if event.actor
        else "Unknown"
    )

    assignees_str = (
        ", ".join(
            f"{m.full_name} (@{m.username})" for m in event.assignees
        )
        if event.assignees
        else "Unassigned"
    )

    time_str = event.occurred_at.strftime("%Y-%m-%d %H:%M UTC")

    lines: list[str] = [
        f"{emoji} <b>{label}</b>",
        "",
        f"🃏 <b>Card:</b> {event.card_name}",
    ]

    if event.event_type == EventType.TASK_MOVED:
        lines.append(f"🔀 <b>From:</b> {event.from_list or '?'} → <b>To:</b> {event.to_list or '?'}")
    elif event.event_type == EventType.NEW_TASK and event.to_list:
        lines.append(f"📁 <b>List:</b> {event.to_list}")
    elif event.event_type == EventType.TASK_UPDATED and event.card_desc:
        lines.append(f"📝 <b>Changed fields:</b> {event.card_desc}")

    lines += [
        "",
        f"👤 <b>By:</b> {actor_name}",
        f"👥 <b>Assigned to:</b> {assignees_str}",
        f"🕐 <b>Time:</b> {time_str}",
    ]

    if event.card_url:
        lines.append(f'🔗 <a href="{event.card_url}">Open Card</a>')
    if event.board_url:
        lines.append(f'📋 <a href="{event.board_url}">Open Board</a>')

    return "\\n".join(lines)
"""

# ─────────────────────────────────────────────────────────────────────────────
# Scaffolding runner
# ─────────────────────────────────────────────────────────────────────────────

def create_project(root: str = PROJECT_NAME) -> None:
    """Create the full project tree under ``root``."""

    # Collect all directories we need
    dirs: set[str] = set()
    for rel_path in FILES:
        parent = os.path.dirname(rel_path)
        if parent:
            dirs.add(parent)

    # Also ensure package dirs that need __init__.py exist
    package_dirs = [
        "src",
        "src/bot",
        "src/bot/handlers",
        "src/trello",
        "logs",
    ]
    for d in package_dirs:
        dirs.add(d)

    print(f"📁 Creating project: {root}/")
    os.makedirs(root, exist_ok=True)

    for d in sorted(dirs):
        full = os.path.join(root, d)
        os.makedirs(full, exist_ok=True)
        print(f"  mkdir  {d}/")

    # Ensure logs/.gitkeep
    gitkeep = os.path.join(root, "logs", ".gitkeep")
    if not os.path.exists(gitkeep):
        open(gitkeep, "w").close()

    for rel_path, content in FILES.items():
        full_path = os.path.join(root, rel_path)
        with open(full_path, "w", encoding="utf-8") as fh:
            fh.write(content)
        print(f"  write  {rel_path}")

    # Make main.py executable
    main_path = os.path.join(root, "main.py")
    st = os.stat(main_path)
    os.chmod(main_path, st.st_mode | stat.S_IEXEC)

    print()
    print("✅ Project created successfully!")
    print()
    print("Next steps:")
    print(f"  cd {root}")
    print("  python -m venv .venv && source .venv/bin/activate")
    print("  pip install -r requirements.txt")
    print("  cp .env.example .env   # then fill in your credentials")
    print("  python main.py")


if __name__ == "__main__":
    create_project()
