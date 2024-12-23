from pydantic import BaseModel, ConfigDict
from datetime import datetime

class BucketSchema(BaseModel):
    id: int
    bucket_name: str
    owner: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class BucketBase(BaseModel):
    bucket_name: str
    owner: str
    model_config = ConfigDict(from_attributes=True)

class BucketCreate(BucketBase):
    model_config = ConfigDict(from_attributes=True)

class BucketResponse(BucketBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
