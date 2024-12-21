from sqlalchemy import Column, Integer, String
from models.BaseModel import base_model

class User(base_model):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True,autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)