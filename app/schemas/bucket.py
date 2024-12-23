from pydantic import BaseModel
from datetime import datetime
from typing import ClassVar

class BucketBase(BaseModel):
    id: ClassVar[int]
    bucket_name: str
    files_count: int
    owner: str
    created_at: datetime
    updated_at: datetime
    size_bytes: int

    class Config:
        from_attributes = True
class BucketCreate(BucketBase):
    pass

class BucketResponse(BucketBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
