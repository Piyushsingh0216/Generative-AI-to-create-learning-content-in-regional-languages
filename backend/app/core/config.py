from pathlib import Path
from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


# ====== API KEY PLACEHOLDER ======
# OPENAI_API_KEY = "YOUR_OPENAI_API_KEY_HERE"
# =================================

# ====== API KEY PLACEHOLDER ======
# GOOGLE_TRANSLATE_API_KEY = "YOUR_API_KEY_HERE"
# =================================

# Supabase placeholders (optional)
SUPABASE_URL = "YOUR_SUPABASE_URL"
SUPABASE_KEY = "YOUR_SUPABASE_ANON_KEY"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "AI Learning Platform"
    environment: str = "development"
    debug: bool = True

    database_url: str = "sqlite:///./learning_platform.db"

    jwt_secret_key: str = "CHANGE_THIS_TO_A_LONG_RANDOM_SECRET"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440

    cors_origins: str = Field(default="http://localhost:5173,http://localhost:5174", alias="CORS_ORIGINS")

    upload_dir: str = "app/uploads"
    audio_dir: str = "app/audio"
    tesseract_cmd: Optional[str] = None

    # Optional provider fields
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4o-mini"
    google_translate_api_key: Optional[str] = None
    supabase_url: Optional[str] = None
    supabase_key: Optional[str] = None

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def upload_path(self) -> Path:
        return Path(self.upload_dir)

    @property
    def audio_path(self) -> Path:
        return Path(self.audio_dir)


settings = Settings()
