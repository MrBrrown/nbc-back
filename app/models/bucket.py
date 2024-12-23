from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from models.base_model import base_model

class Bucket(base_model):
    __tablename__ = 'bucket'
    id = Column(Integer, primary_key=True,autoincrement=True)
    bucket_name = Column(String, nullable=False)
    owner_name = Column(String, nullable=False)
    owner_id = Column(Integer, ForeignKey("user.id"))
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=True)

    owner = relationship("User", back_populates="buckets")
    objects = relationship("Object", back_populates="bucket")

