# --------------------------------------------------------
# File: server/app/core/config.py
# Purpose: Application Configuration & Settings
# Responsibilities: Parses environment variables from .env and exposes them
#                   as typed Settings attributes using pydantic-settings.
# Author: Srihan Raj Guduru
# --------------------------------------------------------

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Project configuration settings loaded from environment variables and defaults.
    """
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    DATABASE_URL: str = "postgresql+asyncpg://finbro:finbro@localhost:5432/finbro"
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    CORS_ORIGINS: str = "http://localhost:3000"
    WEB3_RPC_URL: str = ""
    WEB3_PRIVATE_KEY: str = ""
    FBT_CONTRACT_ADDRESS: str = ""
    SEPOLIA_CHAIN_ID: int = 11155111
    MOCK_WEB3: bool = True

    GEMINI_API_KEY: str | None = None
    GEMINI_MODEL: str = "gemini-3.1-flash"

    DEMO_TOKEN: str = "demo-token-123"
    DEMO_USER_ID: str = "demo-user-uid"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    @property
    def use_mock_web3(self) -> bool:
        return self.MOCK_WEB3 or not self.WEB3_RPC_URL or not self.FBT_CONTRACT_ADDRESS


settings = Settings()
