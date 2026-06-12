from abc import ABC, abstractmethod
from typing import List, Dict


class EventSource(ABC):
    @abstractmethod
    def fetch_raw_actions(self, limit: int = 10) -> List[Dict]:
        raise NotImplementedError

    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError
