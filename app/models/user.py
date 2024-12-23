from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship

from models.base_model import base_model
from datetime import datetime

class User(base_model):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime)
    email = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    files = relationship("File", back_populates="owner")