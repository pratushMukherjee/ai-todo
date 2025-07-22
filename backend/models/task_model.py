from pydantic import BaseModel
from typing import Optional

class TaskCreate(BaseModel):
    title: str
    start: Optional[str] = None
    end: Optional[str] = None
    priority: Optional[int] = None
    urgency: Optional[int] = None
    feedback: Optional[str] = None

class TaskOut(TaskCreate):
    id: int
    is_done: bool

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    start: Optional[str] = None
    end: Optional[str] = None
    priority: Optional[int] = None
    urgency: Optional[int] = None
    feedback: Optional[str] = None
    is_done: Optional[bool] = None
