import json
from datetime import datetime, timezone
from pathlib import Path

from api.config import get_settings, open_database


class RecordRevisionConflict(RuntimeError):
    def __init__(self, *, latest_version: int) -> None:
        super().__init__("The record changed after it was loaded.")
        self.latest_version = latest_version


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def initialize_storage() -> None:
    database_path = Path(get_settings()["database_path"])
    database_path.parent.mkdir(parents=True, exist_ok=True)
    with open_database() as connection:
        connection.execute("PRAGMA journal_mode = WAL")
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS email_briefing_documents (
                briefing_kind TEXT PRIMARY KEY,
                document_json TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        email_columns = {
            row["name"]
            for row in connection.execute("PRAGMA table_info(email_briefing_documents)").fetchall()
        }
        if "record_version" not in email_columns:
            connection.execute(
                "ALTER TABLE email_briefing_documents "
                "ADD COLUMN record_version INTEGER NOT NULL DEFAULT 1"
            )
        connection.commit()


def get_email_briefing_document(briefing_kind: str) -> dict | None:
    with open_database() as connection:
        row = connection.execute(
            """
            SELECT briefing_kind, document_json, updated_at, record_version
            FROM email_briefing_documents
            WHERE briefing_kind = ?
            """,
            (briefing_kind,),
        ).fetchone()
    if row is None:
        return None
    return {
        "briefing_kind": row["briefing_kind"],
        "document": json.loads(row["document_json"]),
        "updated_at": row["updated_at"],
        "record_version": int(row["record_version"]),
    }


def save_email_briefing_document(
    briefing_kind: str,
    document: dict,
    *,
    expected_version: int,
) -> dict:
    updated_at = _utc_now()
    with open_database() as connection:
        if expected_version == 0:
            cursor = connection.execute(
                """
                INSERT INTO email_briefing_documents
                    (briefing_kind, document_json, updated_at, record_version)
                VALUES (?, ?, ?, 1)
                ON CONFLICT(briefing_kind) DO NOTHING
                """,
                (briefing_kind, json.dumps(document), updated_at),
            )
        else:
            cursor = connection.execute(
                """
                UPDATE email_briefing_documents
                SET document_json = ?, updated_at = ?, record_version = record_version + 1
                WHERE briefing_kind = ? AND record_version = ?
                """,
                (json.dumps(document), updated_at, briefing_kind, expected_version),
            )
        if cursor.rowcount != 1:
            latest = connection.execute(
                "SELECT record_version FROM email_briefing_documents WHERE briefing_kind = ?",
                (briefing_kind,),
            ).fetchone()
            raise RecordRevisionConflict(
                latest_version=int(latest["record_version"]) if latest is not None else 0
            )
        connection.commit()
    return {
        "briefing_kind": briefing_kind,
        "document": document,
        "updated_at": updated_at,
        "record_version": expected_version + 1,
    }
