from datetime import datetime
from pydantic import BaseModel, field_validator
from typing  import Optional

class UploadedFile(BaseModel):
    id: Optional[int] = None
    session_id:str
    name:str
    created_at:datetime = datetime.now()
    edited_at:Optional[datetime] = None

    @field_validator("edited_at", mode="before")
    def _fill_edited_at(cls, v, info):
        if v is None:
            return info.data.get("created_at")
        
        return v
