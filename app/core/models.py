from datetime import datetime
from pydantic import BaseModel


class Event(BaseModel):
    id: str
    source: str
    title: str
    description: str | None = None
    actor: str | None = None
    created_at: datetime
