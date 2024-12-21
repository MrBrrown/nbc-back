from sqlalchemy import Column, Integer, String, DateTime
from models.BaseModel import base_model

class Bucket(base_model):
    __tablename__ = 'bucket'
    id = Column(Integer, primary_key=True,autoincrement=True)
    bucket_name = Column(String, nullable=False)
    owner = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)