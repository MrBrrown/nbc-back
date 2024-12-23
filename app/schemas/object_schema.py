from pydantic import BaseModel, HttpUrl, ConfigDict, Field
from datetime import datetime

class ObjectBase(BaseModel):
    """Base model for S3 objects."""
    filename: str
    owner_id: int
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class ObjectStorage(BaseModel):
    """Model representing object's storage information."""
    url: HttpUrl
    size: int = Field(..., description="Size of the object in bytes")
    bucket_id: int
    bucket_name: str
    extension: str = Field(..., description="File extension")
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class ObjectMetadata(BaseModel):
    """Model representing object's metadata."""
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class ObjectCreate(ObjectBase):
    """Model for creating S3 objects."""
    # Дополнительные поля, специфичные для создания объекта, если нужны.
    pass

class ObjectResponse(ObjectBase, ObjectStorage, ObjectMetadata):
    """Model for S3 object response."""
    # При желании можно указать порядок полей в ответе
    model_config = ConfigDict(from_attributes=True, populate_by_name=True, json_schema_extra={"description": "S3 Object Response Model"})