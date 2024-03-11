from pydantic import BaseModel, EmailStr
from typing import Optional
import time

class loginRequest(BaseModel):
    email: EmailStr
    password: str

#What would be sent back to the User.
class loginResponse(BaseModel):
    access_token: str
    token_type: str

#How will out token look need to validate that
class TokenData(BaseModel): #So at the time of decrypting the jwt we will cross verify, whether schema validation is followed
    user_id: int
    name: str

class Token(BaseModel): #So at the time of decrypting the jwt we will cross verify, whether schema validation is followed
    access_token: str
    token_type: str
    
