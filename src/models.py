from dataclasses import dataclass
from datetime import datetime


@dataclass
class Watch:
    id: int
    telegram_user_id: int
    league: str
    query_id: str
    url: str
    status: str
    created_at: datetime
    last_event_at: datetime | None = None
