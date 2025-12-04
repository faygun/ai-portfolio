from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional

class MessageInfo(BaseModel):
    id: Optional[str] = None
    session_id: Optional[str] = None
    question: str
    answer: Optional[str] = None
    created_at: datetime = datetime.now()
    edited_at:Optional[datetime] = None

    @field_validator("edited_at", mode="before")
    def _fill_edited_at(cls, v, info):
        if v is None:
            return info.data.get("created_at")
        
        return v
