from pydantic import BaseModel
from datetime import datetime
from enum import Enum
from typing import Any

class TaskStatus(str, Enum):
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"

class TaskPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"

class Task(BaseModel):
    id: int
    title: str
    description: str | None = None
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
    deadline: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        from_attributes = True  # Tillader konvertering fra SQLAlchemy modeller
        json_encoders = {
            datetime: lambda dt: dt.isoformat() if dt else None
        }

    def __repr__(self):
        return f"<Task(id={self.id}, title='{self.title}', status='{self.status}')>"

    def dict(self, *args, **kwargs) -> dict[str, Any]:
        # Konverter datetime objekter til ISO format strings
        d = super().dict(*args, **kwargs)
        for field in ['deadline', 'created_at', 'updated_at']:
            if d.get(field):
                d[field] = d[field].isoformat()
        return d 