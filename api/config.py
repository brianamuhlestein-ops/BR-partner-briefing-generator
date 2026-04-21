from pathlib import Path
import sqlite3


BASE_DIR = Path(__file__).resolve().parent.parent


def get_settings() -> dict:
    database_path = BASE_DIR / "email_briefing.db"
    return {
        "host": "127.0.0.1",
        "port": 8089,
        "repo_root": BASE_DIR,
        "database_path": database_path,
        "database_url": f"sqlite:///{database_path.as_posix()}",
        "templates_dir": BASE_DIR / "api" / "science" / "templates",
        "generated_dir": BASE_DIR / "generated",
        "cors_allow_origin": "*",
    }


def open_database() -> sqlite3.Connection:
    connection = sqlite3.connect(get_settings()["database_path"])
    connection.row_factory = sqlite3.Row
    return connection
