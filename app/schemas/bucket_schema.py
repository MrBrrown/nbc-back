from typing import Optional

from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

class BucketBase(BaseModel):
    """Base model for bucket data."""
    bucket_name: str = Field(
        ...,
        description="Name of the bucket",
        min_length=3,
        max_length=63,
        pattern=r"^[a-z0-9]([-a-z0-9]*[a-z0-9])?$",  # Simplified bucket name pattern
    )
    owner_id: int = Field(..., description="ID of the bucket owner")
    owner_name: str = Field(None, description="Username of the bucket owner")
    model_config = ConfigDict(from_attributes=True, json_schema_extra={"description": "Bucket Base Model"})

class BucketMetadata(BaseModel):
    """Model for bucket metadata."""
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True, json_schema_extra={"description": "Bucket Metadata Model"})

class BucketStatistics(BaseModel):
    """Model for bucket statistics."""
    file_count: Optional[int] = Field(None, description="Number of files in the bucket")
    size: Optional[int] = Field(None, description="Total size of files in the bucket in bytes")
    model_config = ConfigDict(from_attributes=True, json_schema_extra={"description": "Bucket Statistics Model"})

class BucketCreate(BucketBase):
    """Model for creating a new bucket."""
    pass

class BucketResponse(BucketBase, BucketMetadata, BucketStatistics):
    """Model for bucket response."""
    pass