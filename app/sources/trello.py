import requests
import logging
from typing import List, Dict

from app.config import settings
from app.core.source import EventSource

logger = logging.getLogger(__name__)


class TrelloSource(EventSource):
    BASE_URL = "https://api.trello.com/1"

    def name(self) -> str:
        return "Trello"

    def fetch_raw_actions(self, limit: int = 10) -> List[Dict]:
        url = f"{self.BASE_URL}/boards/{settings.TRELLO_BOARD_ID}/actions"

        params = {
            "key": settings.TRELLO_API_KEY,
            "token": settings.TRELLO_TOKEN,
            "limit": limit,
            "filter": "all",
        }

        logger.info("Fetching Trello actions...")

        res = requests.get(url, params=params, timeout=10)
        res.raise_for_status()

        return res.json()
