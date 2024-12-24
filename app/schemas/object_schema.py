from pydantic import BaseModel, HttpUrl, ConfigDict, Field
from datetime import datetime

class ObjectBase(BaseModel):
    """Base model for S3 objects."""
    object_key: str
    owner_id: int
    owner_name: str
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class ObjectStorage(BaseModel):
    """Model representing object's storage information."""
    download_url: HttpUrl = Field(..., description="Download URL for the object")
    size: int = Field(..., description="Size of the object in bytes")
    bucket_id: int
    bucket_name: str
    extension: str = Field(None, description="File extension")
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class ObjectMetadata(BaseModel):
    """Model representing object's metadata."""
    id: int
    created_at: datetime
    updated_at: datetime
    file_storage_path: str
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class ObjectCreate(ObjectBase):
    """Model for creating S3 objects."""
    # Дополнительные поля, специфичные для создания объекта, если нужны.
    pass

class ObjectResponse(ObjectBase, ObjectStorage, ObjectMetadata):
    """Model for S3 object response."""
    # При желании можно указать порядок полей в ответе
    model_config = ConfigDict(from_attributes=True, populate_by_name=True, json_schema_extra={"description": "S3 Object Response Model"})