from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from models.base_model import base_model
from datetime import datetime

class File(base_model):
    __tablename__ = "file"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    url = Column(String, unique=True, index=True, nullable=False)
    owner_id = Column(Integer, ForeignKey("user.id"))
    created_at = Column(DateTime, default=datetime)

    owner = relationship("User", back_populates="files")
