#Create, Verify access token and get_current_user enable for all services
from models.login import TokenData, Token
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from routers.users import isUserPresent
from utils.config import Settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
)

# SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
# ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 30
settings = Settings()

def create_access_token(details: dict):
    print(settings)
    to_encode = details.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)

    return {"access_token": encoded_jwt, 'token_type': "bearer"}

def verify_access_token(token:Token):
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user_id: str = payload.get("user_id")
        name: str = payload.get("name")

        if user_id is None or name is None:
            raise credentials_exception

        token_data = TokenData(user_id=user_id, name=name)
    except JWTError:
        raise credentials_exception
    
    return token_data

def get_current_user(token: Token = Depends(oauth2_scheme)):
    # Verify the token if the token is valid then send the details of the user to each service
    verified_user = verify_access_token(token)
    if not verified_user:
        raise credentials_exception
    
    user = isUserPresent(verified_user.user_id)[0]
    user.pop("password")
    return user