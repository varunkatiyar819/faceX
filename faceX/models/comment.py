from pydantic import BaseModel
from typing import Optional
import time

class commentRequest(BaseModel):
    comment_id: int
    comment: str
    modified_at: Optional[str] = time.strftime("%Y:%m:%d %H:%M:%S")

class commentResponse(commentRequest):
    post_id: int
    user_id: int
    pass

class commentUpdate(BaseModel):
    comment_id: int
    comment: str = ""
    modified_at: Optional[str] = time.strftime("%Y:%m:%d %H:%M:%S")

class commentDeleteResponse(BaseModel):
    post_id: int
    user_id: int
    comment_id: int
    modified_at: Optional[str] = time.strftime("%Y:%m:%d %H:%M:%S")


