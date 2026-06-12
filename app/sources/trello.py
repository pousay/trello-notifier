import requests
import logging
from datetime import datetime
from typing import List

from app.config import settings
from app.core.models import Event
from app.core.source import EventSource

logger = logging.getLogger(__name__)


class TrelloSource(EventSource):
    BASE_URL = "https://api.trello.com/1"

    def name(self) -> str:
        return "Trello"

    def fetch_events(self, limit: int = 10) -> List[Event]:
        url = f"{self.BASE_URL}/boards/{settings.TRELLO_BOARD_ID}/actions"

        params = {
            "key": settings.TRELLO_API_KEY,
            "token": settings.TRELLO_TOKEN,
            "limit": limit,
            "filter": "all",
        }

        logger.info("Fetching Trello events")

        res = requests.get(url, params=params, timeout=10)
        res.raise_for_status()

        events = []

        for item in res.json():
            data = item.get("data", {})

            events.append(
                Event(
                    id=item["id"],
                    source=self.name(),
                    title=item.get("type", "unknown"),
                    description=data.get("card", {}).get("name"),
                    actor=item.get("memberCreator", {}).get("fullName"),
                    created_at=datetime.fromisoformat(
                        item["date"].replace("Z", "+00:00")
                    ),
                )
            )

        return events
