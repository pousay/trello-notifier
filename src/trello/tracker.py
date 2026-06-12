"""Concrete Trello board event tracker."""

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
            datetime.fromisoformat(last_raw.replace("Z", "+00:00"))
            if last_raw
            else None
        ),
    )


class TrelloEventTracker(AbstractEventTracker):
    """
    Polls a Trello board for changes and emits structured events.

    Strategy
    --------
    - On ``initialise()``, fetch the current action log and record the newest
      action id as our cursor.  No events are emitted.
    - On each ``poll()``, fetch actions *after* the cursor, parse them into
      ``TrelloEvent`` objects, and advance the cursor.
    """

    def __init__(self, client: TrelloClient) -> None:
        self._client = client
        self._snapshot: BoardSnapshot = BoardSnapshot()
        self._board_url: str = ""

    # ── AbstractEventTracker implementation ─────────────────────────────────

    async def initialise(self) -> None:
        """Record the current board state without emitting events."""
        await self._refresh_snapshot()
        actions = await self._client.get_actions(limit=1)
        if actions:
            self._snapshot.last_action_id = actions[0]["id"]
            logger.debug(
                "Cursor initialised at action %s", self._snapshot.last_action_id
            )
        else:
            logger.debug("No previous actions found; cursor is empty.")

    async def poll(self) -> list[TrelloEvent]:
        """Return events that occurred since the last poll."""
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
        """Fetch lists and cards from Trello and update the in-memory snapshot."""
        board_data = await self._client.get_board()
        print(f"\n\n\t{board_data}\n\n")
        self._board_url = board_data["shortUrl"]

        raw_lists = await self._client.get_lists()
        lists: dict[str, TrelloList] = {
            lst["id"]: TrelloList(
                id=lst["id"], name=lst["name"], closed=lst.get("closed", False)
            )
            for lst in raw_lists
        }

        raw_cards = await self._client.get_cards()
        cards: dict[str, TrelloCard] = {
            c["id"]: _parse_card(c, lists) for c in raw_cards
        }

        self._snapshot.lists = lists
        self._snapshot.cards = cards

    def _parse_action(self, action: dict) -> Optional[TrelloEvent]:
        """Map a raw Trello action dict to a ``TrelloEvent``."""
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
        card_url = (
            self._snapshot.cards.get(
                card_id, TrelloCard(id=card_id, name=card_name, list_id="")
            ).short_url
            or ""
        )

        # Assigned members from snapshot
        assignees = self._snapshot.cards.get(
            card_id, TrelloCard(id=card_id, name=card_name, list_id="")
        ).members

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
                to_list_id = card_data.get(
                    "idList", data.get("listAfter", {}).get("id", "")
                )
                from_name = (
                    data.get("listBefore", {}).get("name")
                    or self._snapshot.lists.get(
                        from_list_id, TrelloList(id=from_list_id, name=from_list_id)
                    ).name
                )
                to_name = (
                    data.get("listAfter", {}).get("name")
                    or self._snapshot.lists.get(
                        to_list_id, TrelloList(id=to_list_id, name=to_list_id)
                    ).name
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
                    **base_kwargs,
                    event_type=EventType.TASK_UPDATED,
                    card_desc=", ".join(changed_fields),  # surfaced as "changed fields"
                )

        return None
