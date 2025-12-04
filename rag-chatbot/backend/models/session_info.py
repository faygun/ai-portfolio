from pydantic import BaseModel

class SessionInfo(BaseModel):
    id: str
    title:str
    user_id:str
