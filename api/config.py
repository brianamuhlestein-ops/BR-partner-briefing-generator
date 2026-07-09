import os
from pathlib import Path
import sqlite3


BASE_DIR = Path(__file__).resolve().parent.parent


def _csv_setting(name: str, default: str) -> list[str]:
    value = os.environ.get(name, default)
    return [item.strip() for item in value.split(",") if item.strip()]


def get_settings() -> dict:
    database_path = Path(os.environ.get("DATABASE_PATH", BASE_DIR / "email_briefing.db"))
    generated_dir = Path(os.environ.get("GENERATED_DIR", BASE_DIR / "generated"))
    return {
        "service_name": os.environ.get("SERVICE_NAME", "partner-briefing-api"),
        "host": os.environ.get("API_HOST", "127.0.0.1"),
        "port": int(os.environ.get("API_PORT", "8089")),
        "repo_root": BASE_DIR,
        "database_path": database_path,
        "database_url": f"sqlite:///{database_path.as_posix()}",
        "templates_dir": BASE_DIR / "api" / "science" / "templates",
        "generated_dir": generated_dir,
        "cors_allow_origins": _csv_setting(
            "CORS_ALLOW_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173,http://localhost:5179,http://127.0.0.1:5179",
        ),
        "cors_allow_methods": _csv_setting(
            "CORS_ALLOW_METHODS",
            "GET,POST,PATCH,OPTIONS",
        ),
        "cors_allow_headers": _csv_setting(
            "CORS_ALLOW_HEADERS",
            "Content-Type,Accept,X-Request-ID",
        ),
    }


def open_database() -> sqlite3.Connection:
    connection = sqlite3.connect(get_settings()["database_path"])
    connection.row_factory = sqlite3.Row
    return connection
