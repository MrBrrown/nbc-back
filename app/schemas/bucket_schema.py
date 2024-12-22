from pydantic import BaseModel, ConfigDict
from datetime import datetime

class BucketSchema(BaseModel):
    id: int
    bucket_name: str
    owner: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
