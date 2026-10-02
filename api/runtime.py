from __future__ import annotations

import json
import os
import re
from datetime import datetime, timedelta, timezone
from typing import Any
from urllib.request import Request, urlopen


def parse_utc_iso(value: str | None) -> datetime | None:
    text = str(value or "").strip()
    if not text:
        return None
    if text.endswith("Z"):
        text = f"{text[:-1]}+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return None
    return parsed.astimezone(timezone.utc).replace(second=0, microsecond=0)


def format_utc_z(value: datetime) -> str:
    return value.astimezone(timezone.utc).replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")


def exercise() -> bool:
    return bool(os.getenv("SWIFT_EXERCISE_CATALOGUE_URL", "").strip())


def source_mode() -> str:
    if exercise():
        return "exercise"
    configured = os.getenv("PARTNER_BRIEFING_SOURCE_MODE", "live").strip().lower()
    if configured not in {"live", "gannon"}:
        raise RuntimeError("PARTNER_BRIEFING_SOURCE_MODE must be live or gannon")
    return configured


def data_source() -> str:
    return "replay" if source_mode() in {"gannon", "exercise"} else "operational"


def hel_session() -> dict[str, Any]:
    base = os.getenv("SWIFT_REPLAY_CATALOG_URL", "").strip().rstrip("/")
    session_id = os.getenv("SWIFT_REPLAY_SESSION_ID", "").strip()
    if not base or not re.fullmatch(r"[A-Za-z0-9_-]{1,80}", session_id):
        raise RuntimeError("Gannon replay requires SWIFT_REPLAY_CATALOG_URL and SWIFT_REPLAY_SESSION_ID")
    with urlopen(Request(f"{base}/replay-sessions/{session_id}", headers={"Accept": "application/json"}), timeout=15) as response:
        session = json.load(response)
    if session.get("event_id") != "gannon-2024":
        raise RuntimeError("HEL session is not a Gannon replay session")
    return session


def system_now_utc() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def effective_now_utc() -> datetime:
    mode = source_mode()
    if mode == "live":
        return system_now_utc()
    if mode == "gannon":
        replay_now = parse_utc_iso(hel_session().get("clock_utc"))
        if replay_now is None:
            raise RuntimeError("HEL replay clock is invalid")
        return replay_now
    replay_now = parse_utc_iso(os.getenv("PARTNER_EXERCISE_NOW_UTC"))
    if replay_now is None:
        raise RuntimeError("Synthetic briefing exercise requires PARTNER_EXERCISE_NOW_UTC")
    return replay_now


def valid_dates(issue_time: datetime) -> list[str]:
    issue_date = issue_time.astimezone(timezone.utc).date()
    return [(issue_date + timedelta(days=offset)).isoformat() for offset in range(3)]


def runtime_status() -> dict[str, Any]:
    configured_source = source_mode()
    system_now = system_now_utc()
    errors: list[str] = []
    try:
        effective_now = effective_now_utc()
    except (OSError, ValueError, RuntimeError) as exc:
        effective_now = None
        errors.append(str(exc))
    is_exercise = configured_source == "exercise"
    return {
        "exercise_delivery_enabled": is_exercise and bool(os.getenv("SYNOPSIS_EXERCISE_LAUNCHER_URL", "").strip()),
        "status": "ok" if not errors else "configuration_error",
        "now_utc": format_utc_z(effective_now) if effective_now else None,
        "system_utc": format_utc_z(system_now),
        "data_source": data_source(),
        "source_mode": configured_source,
        "data_kind": "synthetic" if is_exercise else None,
        "exercise_workspace_url": os.getenv("PARTNER_BRIEFING_EXERCISE_WORKSPACE_URL", "").strip() or None,
        "operational_workspace_url": os.getenv("PARTNER_BRIEFING_OPERATIONAL_WORKSPACE_URL", "").strip() or None,
        "source": data_source(),
        "clock_source": "exercise_environment_utc" if is_exercise else "swift_replay_session" if configured_source == "gannon" else "operational_system_utc",
        "scenario": "gannon-2024" if configured_source == "gannon" else "briefing-exercise" if is_exercise else None,
        "replay_now_env": "PARTNER_EXERCISE_NOW_UTC" if is_exercise else "SWIFT_REPLAY_SESSION_ID" if configured_source == "gannon" else None,
        "invalid_replay_now_env": [],
        "ignored_replay_clock_env": [],
        "warnings": [],
        "configuration_errors": errors,
    }


def temporal_snapshot(issue_time_value: str | None = None) -> dict[str, Any]:
    status = runtime_status()
    if status["status"] != "ok":
        raise RuntimeError(" ".join(status["configuration_errors"]))
    issue_time = parse_utc_iso(issue_time_value) if issue_time_value else effective_now_utc()
    if issue_time is None:
        raise ValueError("issue_time_utc must be a valid UTC ISO timestamp")
    return {
        "issue_time_utc": format_utc_z(issue_time),
        "valid_dates": valid_dates(issue_time),
        "runtime_mode": status["data_source"],
        "replay_scenario": status["scenario"],
    }
