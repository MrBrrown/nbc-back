from sqlalchemy import Column, Integer, String, DateTime
from app.models.BaseModel import base_model

class Bucket(base_model):
    __tablename__ = 'bucket'

    id = Column(Integer, primary_key=True,autoincrement=True)
    bucket_name = Column(String, nullable=False)
    files_count = Column(Integer, nullable=False)
    owner = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    size_bytes = Column(Integer, nullable=False)

    def __repr__(self):
        return f"Bucket(id={self.id}, bucket_name={self.bucket_name}, owner={self.owner}, created_at={self.created_at})"
