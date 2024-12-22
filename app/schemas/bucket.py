from pydantic import BaseModel
from datetime import datetime

class BucketBase(BaseModel):
    bucket_name: str
    owner: str
    class Config:
        from_attributes = True
class BucketCreate(BucketBase):
    pass

class BucketResponse(BucketBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
