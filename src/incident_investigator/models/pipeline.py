from datetime import datetime

from pydantic import BaseModel


class Pipeline(BaseModel):
    id: int
    name: str
    description: str | None
    owner: str
    schedule: str | None
    source: str | None
    destination: str | None
    created_at: datetime
