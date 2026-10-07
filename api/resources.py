from datetime import datetime, timezone

import falcon

from api.config import get_settings
from api.http import item_response, read_json
from api.persistence import (
    RecordRevisionConflict,
    get_email_briefing_document,
    save_email_briefing_document,
)
from api.runtime import runtime_status


def _if_match_version(req: falcon.Request) -> int:
    raw = str(req.get_header("If-Match") or "").strip()
    if not raw:
        raise falcon.HTTPPreconditionRequired(
            title="Precondition Required",
            description="If-Match with the current record version is required.",
        )
    normalized = raw.removeprefix("W/").strip().strip('"')
    try:
        version = int(normalized)
    except ValueError as exc:
        raise falcon.HTTPBadRequest(
            description="If-Match must contain an integer version."
        ) from exc
    if version < 0:
        raise falcon.HTTPBadRequest(description="If-Match version must be non-negative.")
    return version


def _revision_conflict(
    req: falcon.Request,
    resp: falcon.Response,
    exc: RecordRevisionConflict,
) -> None:
    resp.status = falcon.HTTP_409
    resp.set_header("ETag", f'"{exc.latest_version}"')
    resp.media = {
        "status": "error",
        "error": {
            "code": "revision_conflict",
            "message": "This record changed after it was loaded. Reload before saving again.",
            "details": {"latest_version": exc.latest_version},
        },
        "request_id": str(getattr(req.context, "request_id", "") or ""),
    }


class HealthResource:
    def on_get(self, req: falcon.Request, resp: falcon.Response) -> None:
        runtime = runtime_status()
        resp.media = {
            "status": runtime["status"],
            "service": get_settings()["service_name"],
            "timeUtc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "runtime": runtime,
        }


class RuntimeNowResource:
    def on_get(self, req: falcon.Request, resp: falcon.Response) -> None:
        status = runtime_status()
        if status["status"] != "ok":
            resp.status = falcon.HTTP_503
        resp.media = status


class EmailBriefingDocumentResource:
    _allowed_kinds = {"core", "tailored", "social"}

    def _validate_kind(self, briefing_kind: str) -> None:
        if briefing_kind not in self._allowed_kinds:
            raise falcon.HTTPBadRequest(
                description=f"Unsupported email briefing kind '{briefing_kind}'."
            )

    def on_get(self, req: falcon.Request, resp: falcon.Response, briefing_kind: str) -> None:
        self._validate_kind(briefing_kind)
        document = get_email_briefing_document(briefing_kind)
        if document is None:
            raise falcon.HTTPNotFound(
                description=f"Saved email briefing '{briefing_kind}' was not found."
            )
        resp.set_header("ETag", f'"{document["record_version"]}"')
        resp.media = item_response(document)

    def on_put(self, req: falcon.Request, resp: falcon.Response, briefing_kind: str) -> None:
        self._validate_kind(briefing_kind)
        expected_version = _if_match_version(req)
        payload = read_json(req, allow_empty=False)
        document = payload.get("document")
        if not isinstance(document, dict):
            raise falcon.HTTPBadRequest(
                description="Email briefing payload requires a JSON object named 'document'."
            )
        try:
            saved = save_email_briefing_document(
                briefing_kind,
                document,
                expected_version=expected_version,
            )
        except RecordRevisionConflict as exc:
            _revision_conflict(req, resp, exc)
            return
        resp.set_header("ETag", f'"{saved["record_version"]}"')
        resp.media = item_response(saved)
