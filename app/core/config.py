import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    jwt_secret: str = os.getenv("JWT_SECRET", "change-me")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    jwt_expires_minutes: int = int(os.getenv("JWT_EXPIRES_MINUTES", "30"))
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./app.db")
    storage_dir: str = os.getenv("STORAGE_DIR", "./storage/attachments")


settings = Settings()
