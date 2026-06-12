"""Low-level async Trello REST API client."""

import logging
from typing import Any, Optional

import aiohttp

logger = logging.getLogger(__name__)

_BASE = "https://api.trello.com/1"


class TrelloClient:
    """Thin async wrapper around the Trello REST API."""

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
        """Close the underlying HTTP session."""
        if self._session and not self._session.closed:
            await self._session.close()

    # ── Generic request helper ──────────────────────────────────────────────

    async def _get(self, path: str, **params: Any) -> Any:
        """Perform a GET request and return parsed JSON."""
        session = await self._get_session()
        url = f"{_BASE}{path}"
        query = {**self._auth, **params}
        async with session.get(url, params=query) as resp:
            resp.raise_for_status()
            return await resp.json()

    # ── Board-level endpoints ───────────────────────────────────────────────

    async def get_board(self) -> dict[str, Any]:
        """Fetch board metadata."""
        return await self._get(f"/boards/{self._board_id}")

    async def get_lists(self) -> list[dict[str, Any]]:
        """Fetch all open lists on the board."""
        return await self._get(
            f"/boards/{self._board_id}/lists",
            filter="open",
        )

    async def get_cards(self) -> list[dict[str, Any]]:
        """Fetch all open cards with member info."""
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
        """
        Fetch board action log.

        Parameters
        ----------
        since:
            A Trello action ID. When provided only actions *after* this id
            are returned.
        limit:
            Maximum number of actions to return (max 1000).
        """
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
        """Fetch all board members."""
        return await self._get(
            f"/boards/{self._board_id}/members",
            fields="fullName,username",
        )

    async def get_card(self, card_id: str) -> dict[str, Any]:
        """Fetch a single card."""
        return await self._get(
            f"/cards/{card_id}",
            members="true",
            member_fields="fullName,username",
            fields="id,name,desc,idList,shortUrl,due,closed,dateLastActivity",
        )
