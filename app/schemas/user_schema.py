from pydantic import BaseModel, ConfigDict
from datetime import datetime

class User(BaseModel):
    id: int
    username: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
