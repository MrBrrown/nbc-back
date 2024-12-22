from sqlalchemy import Column, Integer, String, DateTime
from models.base_model import base_model

class Object(base_model):
    __tablename__ = 'object'
    id = Column(Integer, primary_key=True,autoincrement=True)
    object_key = Column(String, nullable=False)
    file_storage_path = Column(String, nullable=False)
    owner = Column(String, nullable=False)
    bucket = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)