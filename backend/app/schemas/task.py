from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime


class TaskCreate(BaseModel):
    type: str
    task_metadata: Optional[Dict] = None


class TaskRead(BaseModel):
    id: int
    type: str
    status: str
    task_metadata: Optional[Dict]
    created_at: datetime

    class Config:
        orm_mode = True
