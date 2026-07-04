# backend/app/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    google_client_id: str
    google_client_secret: str
    redirect_uri: str = "http://localhost:8000/auth/callback"
    scopes: list[str] = [
        "https://www.googleapis.com/auth/gmail.readonly",
        "https://www.googleapis.com/auth/gmail.send",
        "https://www.googleapis.com/auth/gmail.modify",
    ]
    class Config:
        env_file = ".env"

settings = Settings()