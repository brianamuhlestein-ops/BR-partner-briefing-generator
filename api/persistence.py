import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from api.config import get_settings, open_database
from api.runtime import temporal_snapshot


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def initialize_storage() -> None:
    database_path = Path(get_settings()["database_path"])
    database_path.parent.mkdir(parents=True, exist_ok=True)
    Path(get_settings()["generated_dir"]).mkdir(parents=True, exist_ok=True)
    with open_database() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS drafts (
                draft_id TEXT PRIMARY KEY,
                briefing_type TEXT NOT NULL,
                template_version TEXT NOT NULL,
                sections_json TEXT NOT NULL,
                status TEXT NOT NULL
            )
            """
        )
        existing_columns = {
            row["name"] for row in connection.execute("PRAGMA table_info(drafts)").fetchall()
        }
        draft_columns = {
            "issue_time_utc": "TEXT",
            "valid_dates_json": "TEXT NOT NULL DEFAULT '[]'",
            "runtime_mode": "TEXT NOT NULL DEFAULT 'operational'",
            "replay_scenario": "TEXT",
            "created_at": "TEXT",
            "updated_at": "TEXT",
        }
        for column_name, definition in draft_columns.items():
            if column_name not in existing_columns:
                connection.execute(f"ALTER TABLE drafts ADD COLUMN {column_name} {definition}")
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS generated_outputs (
                output_id INTEGER PRIMARY KEY AUTOINCREMENT,
                draft_id TEXT NOT NULL,
                output_json TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS social_graphics_drafts (
                draft_id TEXT PRIMARY KEY,
                template_id TEXT NOT NULL,
                scene_json TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS social_graphics_exports (
                export_id TEXT PRIMARY KEY,
                draft_id TEXT,
                template_id TEXT NOT NULL,
                scene_json TEXT NOT NULL,
                base_image_path TEXT NOT NULL,
                variants_json TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS email_briefing_documents (
                briefing_kind TEXT PRIMARY KEY,
                document_json TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        connection.commit()


def _row_to_draft(row: sqlite3.Row | None) -> dict | None:
    if row is None:
        return None
    return {
        "draft_id": row["draft_id"],
        "briefing_type": row["briefing_type"],
        "template_version": row["template_version"],
        "sections": json.loads(row["sections_json"]),
        "status": row["status"],
        "issue_time_utc": row["issue_time_utc"],
        "valid_dates": json.loads(row["valid_dates_json"] or "[]"),
        "runtime_mode": row["runtime_mode"],
        "replay_scenario": row["replay_scenario"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def _row_to_social_graphics_draft(row: sqlite3.Row | None) -> dict | None:
    if row is None:
        return None
    return {
        "draft_id": row["draft_id"],
        "template_id": row["template_id"],
        "scene": json.loads(row["scene_json"]),
        "status": row["status"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def _row_to_social_graphics_export(row: sqlite3.Row | None) -> dict | None:
    if row is None:
        return None
    return {
        "export_id": row["export_id"],
        "draft_id": row["draft_id"],
        "template_id": row["template_id"],
        "scene": json.loads(row["scene_json"]),
        "base_image_path": row["base_image_path"],
        "variants": json.loads(row["variants_json"]),
        "created_at": row["created_at"],
    }


def create_draft_record(payload: dict) -> dict:
    temporal = temporal_snapshot(payload.get("issue_time_utc"))
    now = _utc_now()
    draft = {
        "draft_id": str(uuid4()),
        "briefing_type": payload.get("briefing_type", "master"),
        "template_version": payload.get("template_version", "v1"),
        "sections": payload.get("sections", {}),
        "status": payload.get("status", "draft"),
        **temporal,
        "created_at": now,
        "updated_at": now,
    }
    with open_database() as connection:
        connection.execute(
            """
            INSERT INTO drafts
            (draft_id, briefing_type, template_version, sections_json, status,
             issue_time_utc, valid_dates_json, runtime_mode, replay_scenario, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                draft["draft_id"],
                draft["briefing_type"],
                draft["template_version"],
                json.dumps(draft["sections"]),
                draft["status"],
                draft["issue_time_utc"],
                json.dumps(draft["valid_dates"]),
                draft["runtime_mode"],
                draft["replay_scenario"],
                draft["created_at"],
                draft["updated_at"],
            ),
        )
        connection.commit()
    return draft


def get_draft_record(draft_id: str) -> dict | None:
    with open_database() as connection:
        row = connection.execute(
            """
            SELECT draft_id, briefing_type, template_version, sections_json, status,
                   issue_time_utc, valid_dates_json, runtime_mode, replay_scenario, created_at, updated_at
            FROM drafts WHERE draft_id = ?
            """,
            (draft_id,),
        ).fetchone()
    return _row_to_draft(row)


def update_draft_record(draft_id: str, payload: dict) -> dict | None:
    current = get_draft_record(draft_id)
    if not current:
        return None
    temporal = (
        temporal_snapshot(payload["issue_time_utc"])
        if "issue_time_utc" in payload
        else {
            "issue_time_utc": current["issue_time_utc"],
            "valid_dates": current["valid_dates"],
            "runtime_mode": current["runtime_mode"],
            "replay_scenario": current["replay_scenario"],
        }
    )
    updated = {
        "draft_id": draft_id,
        "briefing_type": current["briefing_type"],
        "template_version": current["template_version"],
        "sections": payload.get("sections", current["sections"]),
        "status": payload.get("status", current["status"]),
        **temporal,
        "created_at": current["created_at"],
        "updated_at": _utc_now(),
    }
    with open_database() as connection:
        connection.execute(
            """
            UPDATE drafts
            SET sections_json = ?, status = ?, issue_time_utc = ?, valid_dates_json = ?,
                runtime_mode = ?, replay_scenario = ?, updated_at = ?
            WHERE draft_id = ?
            """,
            (
                json.dumps(updated["sections"]), updated["status"], updated["issue_time_utc"],
                json.dumps(updated["valid_dates"]), updated["runtime_mode"],
                updated["replay_scenario"], updated["updated_at"], draft_id,
            ),
        )
        connection.commit()
    return updated


def get_email_briefing_document(briefing_kind: str) -> dict | None:
    with open_database() as connection:
        row = connection.execute(
            """
            SELECT briefing_kind, document_json, updated_at
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
    }


def save_email_briefing_document(briefing_kind: str, document: dict) -> dict:
    updated_at = _utc_now()
    with open_database() as connection:
        connection.execute(
            """
            INSERT INTO email_briefing_documents (briefing_kind, document_json, updated_at)
            VALUES (?, ?, ?)
            ON CONFLICT(briefing_kind) DO UPDATE SET
                document_json = excluded.document_json,
                updated_at = excluded.updated_at
            """,
            (briefing_kind, json.dumps(document), updated_at),
        )
        connection.commit()
    return {
        "briefing_kind": briefing_kind,
        "document": document,
        "updated_at": updated_at,
    }


def save_generated_output(draft_id: str, output: dict) -> dict:
    with open_database() as connection:
        cursor = connection.execute(
            "INSERT INTO generated_outputs (draft_id, output_json) VALUES (?, ?)",
            (draft_id, json.dumps(output)),
        )
        connection.commit()
    return {"output_id": cursor.lastrowid, "draft_id": draft_id, **output}


def create_social_graphics_draft_record(payload: dict) -> dict:
    now = _utc_now()
    draft = {
        "draft_id": str(uuid4()),
        "template_id": payload["template_id"],
        "scene": payload["scene"],
        "status": payload.get("status", "draft"),
        "created_at": now,
        "updated_at": now,
    }
    with open_database() as connection:
        connection.execute(
            """
            INSERT INTO social_graphics_drafts
            (draft_id, template_id, scene_json, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                draft["draft_id"],
                draft["template_id"],
                json.dumps(draft["scene"]),
                draft["status"],
                draft["created_at"],
                draft["updated_at"],
            ),
        )
        connection.commit()
    return draft


def get_social_graphics_draft_record(draft_id: str) -> dict | None:
    with open_database() as connection:
        row = connection.execute(
            """
            SELECT draft_id, template_id, scene_json, status, created_at, updated_at
            FROM social_graphics_drafts
            WHERE draft_id = ?
            """,
            (draft_id,),
        ).fetchone()
    return _row_to_social_graphics_draft(row)


def update_social_graphics_draft_record(draft_id: str, payload: dict) -> dict | None:
    current = get_social_graphics_draft_record(draft_id)
    if not current:
        return None
    updated = {
        "draft_id": draft_id,
        "template_id": payload.get("template_id", current["template_id"]),
        "scene": payload.get("scene", current["scene"]),
        "status": payload.get("status", current["status"]),
        "created_at": current["created_at"],
        "updated_at": _utc_now(),
    }
    with open_database() as connection:
        connection.execute(
            """
            UPDATE social_graphics_drafts
            SET template_id = ?, scene_json = ?, status = ?, updated_at = ?
            WHERE draft_id = ?
            """,
            (
                updated["template_id"],
                json.dumps(updated["scene"]),
                updated["status"],
                updated["updated_at"],
                draft_id,
            ),
        )
        connection.commit()
    return updated


def save_social_graphics_export_record(payload: dict) -> dict:
    export_record = {
        "export_id": payload["export_id"],
        "draft_id": payload.get("draft_id"),
        "template_id": payload["template_id"],
        "scene": payload["scene"],
        "base_image_path": payload["base_image_path"],
        "variants": payload["variants"],
        "created_at": payload["created_at"],
    }
    with open_database() as connection:
        connection.execute(
            """
            INSERT INTO social_graphics_exports
            (export_id, draft_id, template_id, scene_json, base_image_path, variants_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                export_record["export_id"],
                export_record["draft_id"],
                export_record["template_id"],
                json.dumps(export_record["scene"]),
                export_record["base_image_path"],
                json.dumps(export_record["variants"]),
                export_record["created_at"],
            ),
        )
        connection.commit()
    return export_record


def get_social_graphics_export_record(export_id: str) -> dict | None:
    with open_database() as connection:
        row = connection.execute(
            """
            SELECT export_id, draft_id, template_id, scene_json, base_image_path, variants_json, created_at
            FROM social_graphics_exports
            WHERE export_id = ?
            """,
            (export_id,),
        ).fetchone()
    return _row_to_social_graphics_export(row)
