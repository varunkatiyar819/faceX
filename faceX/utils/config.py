from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_host: str
    database_user: str
    database_pass: str
    database_name: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    class Config:
        env_file = ".env"
