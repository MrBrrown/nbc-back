from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from .base_model import base_model

class Object(base_model):
    __tablename__ = 'object'
    id = Column(Integer, primary_key=True,autoincrement=True)
    object_key = Column(String, nullable=False)
    file_storage_path = Column(String, nullable=False)
    owner_name = Column(String, nullable=False)
    owner_id = Column(Integer, ForeignKey("user.id"))
    bucket_name = Column(String, nullable=False)
    bucket_id = Column(Integer, ForeignKey("bucket.id"))
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    extension = Column(String, nullable=True)
    download_url = Column(String, nullable=False)
    size = Column(Integer, nullable=False)

    owner = relationship("User", back_populates="objects")
    bucket = relationship("Bucket", back_populates="objects")