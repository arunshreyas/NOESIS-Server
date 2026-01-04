from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


_ENV_FILE = (Path(__file__).resolve().parents[2] / ".env")


class Settings(BaseSettings):
    DATABASE_URL: str
    REDIRECT_URL: str | None = None

    GOOGLE_CLIENT_ID: str | None = None
    GOOGLE_CLIENT_SECRET: str | None = None
    GOOGLE_REDIRECT_URI: str | None = None

    GITHUB_CLIENT_ID: str | None = None
    GITHUB_CLIENT_SECRET: str | None = None
    GITHUB_REDIRECT_URI: str | None = None

    DISCORD_CLIENT_ID: str | None = None
    DISCORD_CLIENT_SECRET: str | None = None
    DISCORD_REDIRECT_URI: str | None = None

    model_config = SettingsConfigDict(env_file=str(_ENV_FILE))


settings = Settings()
