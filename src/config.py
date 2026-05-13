# src/config.py
import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# Project root — works on Windows regardless of where you run from
BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    # --- Anthropic ---
    anthropic_api_key: str = ""

    # --- Gmail OAuth2 ---
    gmail_client_id: str = ""
    gmail_client_secret: str = ""

    # --- Agent behaviour ---
    poll_interval_seconds: int = 300        # how often to check inbox
    allow_auto_send: bool = False           # SAFETY: never send without approval
    allow_auto_label: bool = True           # safe low-risk action, on by default
    allow_auto_flag: bool = True            # safe low-risk action, on by default

    # --- Storage ---
    db_path: Path = BASE_DIR / "data" / "agent.db"
    token_path: Path = BASE_DIR / "token.json"
    credentials_path: Path = BASE_DIR / "credentials.json"
    log_path: Path = BASE_DIR / "logs" / "agent.log"

    # --- Data retention ---
    retention_days: int = 30               # auto-purge after N days

    # --- LLM ---
    claude_model: str = "claude-sonnet-4-20250514"
    max_tokens: int = 500

    # --- Console ---
    console_port: int = 8000
    console_host: str = "127.0.0.1"        # local only, never expose externally

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

# Single shared instance — import this everywhere
settings = Settings()

# Ensure required directories exist (Windows-safe)
settings.db_path.parent.mkdir(parents=True, exist_ok=True)
settings.log_path.parent.mkdir(parents=True, exist_ok=True)