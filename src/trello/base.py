"""Abstract base class for board event trackers.

Designed to be reusable across projects — swap out the concrete implementation
to track Jira, Asana, GitHub Projects, etc.
"""

from abc import ABC, abstractmethod

from src.trello.models import TrelloEvent, BoardSnapshot


class AbstractEventTracker(ABC):
    """Contract that all board event trackers must satisfy."""

    @abstractmethod
    async def initialise(self) -> None:
        """
        Establish an initial snapshot of the board state.

        Called once at startup. Implementations MUST NOT emit events here —
        the purpose is only to record the current state so that subsequent
        calls to ``poll()`` can compute a diff.
        """

    @abstractmethod
    async def poll(self) -> list[TrelloEvent]:
        """
        Compare current board state to the stored snapshot.

        Returns a list of events that occurred since the last call.
        The internal snapshot must be updated after each call so that
        events are not reported twice.
        """

    @abstractmethod
    async def get_snapshot(self) -> BoardSnapshot:
        """Return the current (latest fetched) board snapshot."""
