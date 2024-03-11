from pydantic import BaseModel, EmailStr
from typing import Optional
import time

class voteRequest(BaseModel):
    post_id: int
    dir: int #1 means liked 0 stands for neutral

class voteResponse(voteRequest):
    user_id: int
