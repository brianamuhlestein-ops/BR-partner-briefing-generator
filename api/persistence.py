import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from api.config import get_settings, open_database


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
    draft = {
        "draft_id": str(uuid4()),
        "briefing_type": payload.get("briefing_type", "master"),
        "template_version": payload.get("template_version", "v1"),
        "sections": payload.get("sections", {}),
        "status": payload.get("status", "draft"),
    }
    with open_database() as connection:
        connection.execute(
            "INSERT INTO drafts (draft_id, briefing_type, template_version, sections_json, status) VALUES (?, ?, ?, ?, ?)",
            (
                draft["draft_id"],
                draft["briefing_type"],
                draft["template_version"],
                json.dumps(draft["sections"]),
                draft["status"],
            ),
        )
        connection.commit()
    return draft


def get_draft_record(draft_id: str) -> dict | None:
    with open_database() as connection:
        row = connection.execute(
            "SELECT draft_id, briefing_type, template_version, sections_json, status FROM drafts WHERE draft_id = ?",
            (draft_id,),
        ).fetchone()
    return _row_to_draft(row)


def update_draft_record(draft_id: str, payload: dict) -> dict | None:
    current = get_draft_record(draft_id)
    if not current:
        return None
    updated = {
        "draft_id": draft_id,
        "briefing_type": current["briefing_type"],
        "template_version": current["template_version"],
        "sections": payload.get("sections", current["sections"]),
        "status": payload.get("status", current["status"]),
    }
    with open_database() as connection:
        connection.execute(
            "UPDATE drafts SET sections_json = ?, status = ? WHERE draft_id = ?",
            (json.dumps(updated["sections"]), updated["status"], draft_id),
        )
        connection.commit()
    return updated


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
