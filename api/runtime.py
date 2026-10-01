from __future__ import annotations

import os
import json
import re
from datetime import datetime, timedelta, timezone
from typing import Any
from urllib.request import Request, urlopen


REPLAY_NOW_ENV_VARS = (
    "PARTNER_BRIEFING_REPLAY_NOW_UTC",
    "SWIFT_REPLAY_NOW_UTC",
)


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
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc).replace(second=0, microsecond=0)


def format_utc_z(value: datetime) -> str:
    return value.astimezone(timezone.utc).replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")


def data_source() -> str:
    source_mode = os.getenv("PARTNER_BRIEFING_SOURCE_MODE", "").strip().lower()
    if source_mode:
        if source_mode not in {"live", "gannon"}:
            raise RuntimeError("PARTNER_BRIEFING_SOURCE_MODE must be live or gannon")
        return "replay" if source_mode == "gannon" else "operational"
    configured = os.getenv("PARTNER_BRIEFING_API_DATA_SOURCE", "operational").strip().lower()
    return "replay" if configured == "replay" else "operational"


def source_mode() -> str:
    configured = os.getenv("PARTNER_BRIEFING_SOURCE_MODE", "").strip().lower()
    return configured or ("standalone_replay" if data_source() == "replay" else "live")


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


def configured_replay_now_utc() -> tuple[datetime | None, str | None]:
    for name in REPLAY_NOW_ENV_VARS:
        parsed = parse_utc_iso(os.getenv(name))
        if parsed is not None:
            return parsed, name
    return None, None


def invalid_replay_now_env_vars() -> list[str]:
    return [
        name
        for name in REPLAY_NOW_ENV_VARS
        if (os.getenv(name) or "").strip() and parse_utc_iso(os.getenv(name)) is None
    ]


def system_now_utc() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def effective_now_utc() -> datetime:
    if data_source() == "operational":
        return system_now_utc()
    if source_mode() == "gannon":
        replay_now = parse_utc_iso(hel_session().get("clock_utc"))
        if replay_now is None:
            raise RuntimeError("HEL replay clock is invalid")
        return replay_now
    replay_now, _ = configured_replay_now_utc()
    if replay_now is None:
        raise RuntimeError("Replay mode requires a valid configured replay UTC timestamp")
    return replay_now


def valid_dates(issue_time: datetime) -> list[str]:
    issue_date = issue_time.astimezone(timezone.utc).date()
    return [(issue_date + timedelta(days=offset)).isoformat() for offset in range(3)]


def runtime_status() -> dict[str, Any]:
    mode = data_source()
    configured_source = source_mode()
    system_now = system_now_utc()
    replay_now, replay_env = configured_replay_now_utc()
    invalid_envs = invalid_replay_now_env_vars()
    configured_envs = [name for name in REPLAY_NOW_ENV_VARS if (os.getenv(name) or "").strip()]
    warnings: list[str] = []
    errors: list[str] = []
    exercise = bool(os.getenv('SWIFT_EXERCISE_CATALOGUE_URL', '').strip()) and configured_source != "gannon"
    if exercise and mode != 'replay':
        errors.append('The synthetic exercise catalogue requires replay mode.')

    if mode == "operational":
        effective_now = system_now
        clock_source = "operational_system_utc"
        if configured_envs:
            warnings.append("Replay clock variables are configured but ignored in operational mode.")
        replay_env = None
    else:
        if configured_source == "gannon":
            try:
                session = hel_session()
                effective_now = parse_utc_iso(session.get("clock_utc"))
                replay_env = "SWIFT_REPLAY_SESSION_ID"
                clock_source = "swift_replay_session"
            except (OSError, ValueError, RuntimeError) as exc:
                effective_now = None
                clock_source = "configuration_error"
                errors.append(str(exc))
        else:
            effective_now = replay_now
            clock_source = "replay_environment_utc" if replay_now else "configuration_error"
            if invalid_envs:
                errors.append("One or more replay clock variables contain invalid UTC timestamps.")
            if replay_now is None:
                errors.append("Replay mode requires a valid replay UTC timestamp; system time was not used.")

    return {
        'exercise_delivery_enabled': exercise and mode == 'replay' and bool(os.getenv('SYNOPSIS_EXERCISE_LAUNCHER_URL', '').strip()),
        "status": "ok" if not errors else "configuration_error",
        "now_utc": format_utc_z(effective_now) if effective_now else None,
        "system_utc": format_utc_z(system_now),
        "data_source": mode,
        "source_mode": configured_source,
        "data_kind": "synthetic" if exercise else None,
        "exercise_workspace_url": os.getenv('PARTNER_BRIEFING_EXERCISE_WORKSPACE_URL', '').strip() or None,
        "operational_workspace_url": os.getenv('PARTNER_BRIEFING_OPERATIONAL_WORKSPACE_URL', '').strip() or None,
        "source": mode,
        "clock_source": clock_source,
        "scenario": ("gannon-2024" if configured_source == "gannon" else os.getenv("PARTNER_BRIEFING_REPLAY_SCENARIO", "").strip() or None) if mode == "replay" else None,
        "replay_now_env": replay_env,
        "invalid_replay_now_env": invalid_envs,
        "ignored_replay_clock_env": configured_envs if mode == "operational" else [],
        "warnings": warnings,
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
