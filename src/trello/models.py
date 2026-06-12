"""Pydantic models for Trello domain objects."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, HttpUrl


class EventType(str, Enum):
    """Supported Trello event categories."""

    NEW_TASK = "new_task"
    TASK_DELETED = "task_deleted"
    TASK_MOVED = "task_moved"
    TASK_UPDATED = "task_updated"


class TrelloMember(BaseModel):
    """A Trello workspace member."""

    id: str
    full_name: str
    username: str


class TrelloCard(BaseModel):
    """Snapshot of a Trello card."""

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
    """A column / list on a Trello board."""

    id: str
    name: str
    closed: bool = False


class TrelloEvent(BaseModel):
    """A detected change on the Trello board."""

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
    """Full state of a board at a point in time."""

    cards: dict[str, TrelloCard] = Field(default_factory=dict)
    lists: dict[str, TrelloList] = Field(default_factory=dict)
    # last processed Trello action id
    last_action_id: Optional[str] = None
