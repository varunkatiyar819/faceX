#Create Login Endpoint from Here.
from fastapi import APIRouter, status, Path, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from models.login import loginRequest, loginResponse
from utils.database_connect import connection
from utils.password_manager import verifyPassword
from typing import List, Annotated
from utils.oauth2 import create_access_token
router = APIRouter(
    prefix="/login",
    tags=["login"]
)

try:
    conn = connection()
except Exception:
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unable to reach Database")

def emailExists(username: str):
    query = "SELECT user_id, name, password from users where email=%s"
    cursor = conn.cursor()
    cursor.execute(query, (username, ))
    user = cursor.fetchone()
    cursor.close()

    if not user:
        return {}

    return {"user_id": user[0], "name": user[1], "password": user[2]}

@router.post("/", status_code=status.HTTP_202_ACCEPTED, response_model=loginResponse)
def login(creds: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = emailExists(creds.username)
    if not len(user):
        raise HTTPException(status_code=404, detail="Invalid Credentials")
    
    if not verifyPassword(creds.password, user["password"]):
        raise HTTPException(status_code=404, detail="Invalid Credentials")
        #return an access token if it is passed.
    user.pop("password")
    return create_access_token(user)