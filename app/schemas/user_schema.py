from pydantic import BaseModel, EmailStr, ConfigDict, Field
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """Base model for user data."""
    username: str = Field(..., min_length=3, max_length=50, description="User's unique username")
    email: EmailStr = Field(..., description="User's email address")
    model_config = ConfigDict(from_attributes=True, json_schema_extra={"description": "User Base Model"})


class UserMetadata(BaseModel):
    """Model for user metadata."""
    id: int
    created_at: datetime
    is_active: bool
    model_config = ConfigDict(from_attributes=True, json_schema_extra={"description": "User Metadata Model"})


class UserCreate(UserBase):
    """Model for creating a new user."""

    password: str = Field(..., min_length=6, description="User's password")


class UserUpdate(BaseModel):
    """Model for updating user data."""
    username: Optional[str] = Field(None, min_length=3, max_length=50, description="User's unique username")
    email: Optional[EmailStr] = Field(None, description="User's email address")
    password: Optional[str] = Field(None, min_length=6, description="User's password")
    is_active: Optional[bool] = Field(None, description="User's active status")
    model_config = ConfigDict(from_attributes=True, json_schema_extra={"description": "User Update Model"})


class UserResponse(UserBase, UserMetadata):
    """Model for user response."""
    pass


class Token(BaseModel):
    """Model for authentication token."""
    access_token: str = Field(..., description="Access token value")
    token_type: str = Field(..., description="Type of the token")
    model_config = ConfigDict(json_schema_extra={"description": "Authentication Token Model"})


class TokenData(BaseModel):
    """Model for token data."""
    username: Optional[str] = Field(None, description="Username embedded in the token")
    model_config = ConfigDict(json_schema_extra={"description": "Token Data Model"})