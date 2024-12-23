from pydantic import BaseModel, HttpUrl, ConfigDict
from datetime import datetime

class FileBase(BaseModel):
    filename: str
    url: HttpUrl
    owner_id: int
    model_config = ConfigDict(from_attributes=True)

class FileCreate(FileBase):
    model_config = ConfigDict(from_attributes=True)

class FileResponse(FileBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
