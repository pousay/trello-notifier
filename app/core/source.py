from abc import ABC, abstractmethod
from typing import List
from app.core.models import Event


class EventSource(ABC):
    @abstractmethod
    def fetch_events(self, limit: int = 10) -> List[Event]:
        raise NotImplementedError

    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError
