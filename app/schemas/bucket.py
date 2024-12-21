from pydantic import BaseModel
from datetime import datetime

class Bucket(BaseModel):
    id: int
    bucket_name: str
    owner: str
    created_at: datetime

    class Config:
        orm_mode = True