from pydantic import BaseModel, HttpUrl
from datetime import datetime
from typing import Optional, ClassVar

class StoredFileBase(BaseModel):
    id: ClassVar[int]
    filename: str
    url: HttpUrl
    owner_id: int
    created_at: datetime
    updated_at: datetime
    size_bytes: int
    bucket_id: int
    extensions: str

    class Config:
        from_attributes = True

class StoredFileCreate(StoredFileBase):
    pass

class StoredFileResponse(StoredFileBase):
    id: int
    filename: str
    url: str
    created_at: datetime
    size_bytes: int

    class Config:
        from_attributes = True
