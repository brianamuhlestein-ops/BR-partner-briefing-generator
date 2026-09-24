from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import falcon

from api.runtime import runtime_status


class CmeContextUnavailableError(RuntimeError):
    pass


class CmeContextInvalidError(ValueError):
    pass


def _utc(value: Any) -> datetime:
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError as exc:
        raise CmeContextInvalidError("CME context contains an invalid UTC timestamp.") from exc
    if parsed.tzinfo is None:
        raise CmeContextInvalidError("CME context timestamps must include a UTC offset.")
    return parsed.astimezone(timezone.utc)


def reviewed_cme_context() -> dict[str, Any]:
    url = os.getenv("SYNOPSIS_CME_CONTEXT_URL", "").strip()
    if not url:
        raise CmeContextUnavailableError("The Synopsis CME reviewed-context URL is not configured.")
    try:
        with urlopen(Request(url, headers={"Accept": "application/json"}, method="GET"), timeout=10) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
        raise CmeContextUnavailableError(f"Unable to load reviewed CME context: {exc}") from exc
    if not isinstance(payload, dict):
        raise CmeContextInvalidError("CME Display returned a non-object response.")
    context = payload.get("item", payload)
    if not isinstance(context, dict):
        raise CmeContextInvalidError("CME Display did not return a reviewed context item.")
    _validate(context)
    return _project(context)


def _validate(context: dict[str, Any]) -> None:
    local = runtime_status()
    if local.get("status") != "ok":
        raise CmeContextUnavailableError("Synopsis runtime is not valid.")
    if context.get("schema") != "swift-cme-sa-display-context-v1":
        raise CmeContextInvalidError("Unexpected CME context schema.")
    lifecycle = context.get("lifecycle") or {}
    quality = context.get("quality") or {}
    source_runtime = context.get("runtime") or {}
    if lifecycle.get("state") not in {"reviewed", "approved"} or lifecycle.get("superseded_by_context_id"):
        raise CmeContextInvalidError("CME context is not the current reviewed assessment.")
    if (quality.get("status") != "usable" or not quality.get("available")
            or quality.get("stale") or quality.get("partial")):
        raise CmeContextInvalidError("CME context is unavailable, stale, partial, or degraded.")
    if source_runtime.get("mode") != local["data_source"] or source_runtime.get("scenario") != local.get("scenario"):
        raise CmeContextInvalidError("CME context runtime or replay scenario does not match Synopsis.")
    assessment = (context.get("cme_analysis") or {}).get("assessment") or {}
    required = ("assessment_id", "revision_id", "nominal_arrival_utc",
                "arrival_window_start_utc", "arrival_window_end_utc")
    if not context.get("context_id") or any(not assessment.get(key) for key in required):
        raise CmeContextInvalidError("CME context lacks reviewed assessment identity or timing.")
    start = _utc(assessment["arrival_window_start_utc"])
    nominal = _utc(assessment["nominal_arrival_utc"])
    end = _utc(assessment["arrival_window_end_utc"])
    if not start <= nominal <= end:
        raise CmeContextInvalidError("CME arrival timing is internally inconsistent.")
    if end < _utc(local["now_utc"]):
        raise CmeContextInvalidError("CME arrival window has expired.")


def _project(context: dict[str, Any]) -> dict[str, Any]:
    analysis = context["cme_analysis"]
    assessment = analysis["assessment"]
    return {
        "schema": "swift-synopsis-cme-source-context-v1",
        "source": {
            "application": "cme-sa-display",
            "context_id": context["context_id"],
            "revision": context["lifecycle"]["revision"],
            "reviewed_at_utc": context["lifecycle"].get("reviewed_at_utc"),
        },
        "runtime": context["runtime"],
        "assessment": assessment,
        "narrative_facts": context.get("narrative_facts") or [],
        "evidence_agreement": analysis.get("evidence_agreement"),
        "provenance": context.get("provenance") or {},
        "evidence_ref": {
            "kind": "reviewed_cme_context",
            "record_id": context["context_id"],
            "revision": str(context["lifecycle"]["revision"]),
        },
    }


class CmeContextResource:
    def on_get(self, req: falcon.Request, resp: falcon.Response) -> None:
        del req
        try:
            item = reviewed_cme_context()
        except CmeContextUnavailableError as exc:
            raise falcon.HTTPServiceUnavailable(description=str(exc)) from exc
        except CmeContextInvalidError as exc:
            raise falcon.HTTPFailedDependency(description=str(exc)) from exc
        resp.media = {"status": "ok", "item": item}
