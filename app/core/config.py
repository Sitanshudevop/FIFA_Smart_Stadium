from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    GEMINI_API_KEY: str
    ADMIN_TOKEN: str
    GOOGLE_MAPS_API_KEY: str = ""
    SPORTS_API_KEY: str = ""
    GOOGLE_CLOUD_CREDENTIALS: str = ""
    GOOGLE_CLIENT_ID: str = ""

    class Config:
        env_file = ".env"
        extra = "ignore"


try:
    settings = Settings()
    if not settings.GEMINI_API_KEY or not settings.ADMIN_TOKEN:
        raise ValueError("Missing critical tokens")
except Exception as e:
    raise RuntimeError(f"Startup aborted: {e}. Missing critical environment variables.")
