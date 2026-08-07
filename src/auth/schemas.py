import uuid
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class UserCreateModel(BaseModel):
    username: str = Field(max_length=10)
    email: str = Field(max_length=40)
    password: str = Field(min_length=6)
    first_name: Optional[str]=""
    last_name: Optional[str]=""

class UserModel(BaseModel):
    uid: uuid.UUID
    username: str
    email: str
    first_name: str
    last_name: str
    is_verified: bool
    password_hash: str    
    created_at: datetime
    updated_at:datetime

class UserLoginModel(BaseModel):
    email: str = Field(max_length=40)
    password: str = Field(min_length=6)
    