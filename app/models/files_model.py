from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.models.BaseModel import base_model
from datetime import datetime

class StoredFile(base_model):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    url = Column(String, unique=True, index=True, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.astimezone)
    updated_at = Column(DateTime, default=datetime.astimezone)
    size_bytes = Column(Integer, nullable=False)
    bucket_id = Column(Integer, ForeignKey("bucket.id"))
    extensions = Column(String, nullable=False)

    owner = relationship("User", back_populates="files")
    bucket = relationship("Bucket", back_populates="files")

    class Config:
        from_attributes = True
