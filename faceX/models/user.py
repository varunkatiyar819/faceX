from pydantic import BaseModel, EmailStr
from typing import Optional
import time

class UserCreatedResponse(BaseModel):
    user_id: int
    name: str
    email: EmailStr
    profession: str
    about: str
    created_at: Optional[str] = time.strftime("%Y:%m:%d %H:%M:%S")

class UserDetailsRequest(UserCreatedResponse):
    password: str
    
class UserUpdateRequest(BaseModel):
    name: Optional[str] = ""
    email: Optional[EmailStr] = "sample@example.com"
    password: Optional[str] = ""
    profession: Optional[str] = ""
    about: Optional[str] = ""

class DeleteUserResponse(BaseModel):
    user_id: int
    name: str
    email: EmailStr
    timestramp: Optional[str]

