from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: str = Field(..., description="Oil India professional email address")
    full_name: str = Field(..., description="Full name of engineer or officer")
    role: str = Field(default="Drilling Engineer", description="Role e.g. Drilling Engineer, Superintendent, Geologist")
    asset_field: str = Field(default="Assam Shelf", description="Operational field e.g. Nahorkatiya, Baghjan, Moran, Jorajan")

class UserRegister(UserBase):
    password: str = Field(..., min_length=6, description="Account password (min 6 characters)")

class UserLogin(BaseModel):
    email: str = Field(..., description="Account email")
    password: str = Field(..., description="Account password")

class UserResponse(UserBase):
    id: str
    is_active: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class TokenData(BaseModel):
    email: Optional[str] = None
    user_id: Optional[str] = None
    role: Optional[str] = None
