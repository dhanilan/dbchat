from functools import lru_cache
from fastapi import FastAPI
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Awesome API"
    admin_email: str
    items_per_user: int = 50
    db_url: str = "mongodb://localhost:27017/fastapi"

    model_config = SettingsConfigDict(env_file=".env")



@lru_cache
def get_settings():
    return Settings()

settings:Settings = get_settings()
