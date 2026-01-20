from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class EventCreate(BaseModel):
    title: str
    description: Optional[str] = None


class EventRead(BaseModel):
    id: int
    title: str
    description: Optional[str]
    progress: int
    status: str
    created_at: datetime

    model_config ={
        "from_attributes": True
    }

class EventStats(BaseModel):
    total_events: int
    average_gap: float
    max_gap: int
    min_gap: int
    created_at: datetime

    model_config ={
        "from_attributes": True
    }
