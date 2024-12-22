from pydantic import BaseModel, HttpUrl
from datetime import datetime

class FileBase(BaseModel):
    filename: str
    url: HttpUrl
    owner_id: int

class FileCreate(FileBase):
    pass

class FileResponse(FileBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
