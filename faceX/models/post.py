from pydantic import BaseModel
from typing import Optional
import time

class postDetailsRequest(BaseModel):
    post_id: int
    category: str
    title: str
    content: str
    image: Optional[str] = ""
    created_at: Optional[str] = time.strftime("%Y:%m:%d %H:%M:%S")

class postCreatedResponse(postDetailsRequest):
    owner_id: int

class postUpdateRequest(BaseModel):
    category: str = ""
    title: str = ""
    content: str = ""
    image: Optional[str] = ""

class DeletepostResponse(BaseModel):
    post_id: int
    category: str
    title: str
    timestramp: str

