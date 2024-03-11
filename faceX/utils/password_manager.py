from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def encryptPassword(password:str):
    return pwd_context.hash(password)

def verifyPassword(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)