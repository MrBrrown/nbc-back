from pydantic import BaseModel, Field, EmailStr
from typing import ClassVar
from typing import List, Optional
from datetime import datetime

class User(BaseModel):
    id: ClassVar[int]
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    created_at: datetime
    email: EmailStr


class UserCreate(User):
    pass

    # class Config:
    #     from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
