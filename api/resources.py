from datetime import datetime, timezone
from pathlib import Path

import falcon

from api.config import get_settings
from api.http import collection_response, item_response, read_json, result_response
from api.persistence import (
    RecordRevisionConflict,
    create_draft_record,
    create_social_graphics_draft_record,
    get_draft_record,
    get_email_briefing_document,
    get_social_graphics_draft_record,
    get_social_graphics_export_record,
    save_generated_output,
    save_email_briefing_document,
    save_social_graphics_export_record,
    update_draft_record,
    update_social_graphics_draft_record,
)
from api.science.briefing_logic import (
    derive_from_master,
    generate_html_preview,
    generate_pdf_output,
    get_active_alert_context,
    get_active_icao_advisory_context,
    get_briefing_types,
    get_template,
    get_template_version,
    validate_draft_payload,
)
from api.social_graphics import build_export_artifacts, validate_social_graphics_scene
from api.runtime import runtime_status


SETTINGS = get_settings()
TEMPLATES_DIR = Path(SETTINGS["templates_dir"])
GENERATED_DIR = Path(SETTINGS["generated_dir"])


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


def require_draft(draft_id: str) -> dict:
    draft = get_draft_record(draft_id)
    if not draft:
        raise falcon.HTTPNotFound(description=f"Draft '{draft_id}' was not found.")
    return draft


def require_social_graphics_draft(draft_id: str) -> dict:
    draft = get_social_graphics_draft_record(draft_id)
    if not draft:
        raise falcon.HTTPNotFound(description=f"Social graphics draft '{draft_id}' was not found.")
    return draft


def require_social_graphics_export(export_id: str) -> dict:
    export_record = get_social_graphics_export_record(export_id)
    if not export_record:
        raise falcon.HTTPNotFound(description=f"Social graphics export '{export_id}' was not found.")
    return export_record


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


class BriefingTypesResource:
    def on_get(self, req: falcon.Request, resp: falcon.Response) -> None:
        resp.media = collection_response(get_briefing_types())


class TemplateResource:
    def on_get(self, req: falcon.Request, resp: falcon.Response, briefing_type: str) -> None:
        resp.media = item_response(get_template(briefing_type, TEMPLATES_DIR))


class TemplateVersionResource:
    def on_get(
        self,
        req: falcon.Request,
        resp: falcon.Response,
        briefing_type: str,
        version: str,
    ) -> None:
        resp.media = item_response(get_template_version(briefing_type, version, TEMPLATES_DIR))


class DraftCollectionResource:
    def on_post(self, req: falcon.Request, resp: falcon.Response) -> None:
        payload = read_json(req)
        validation = validate_draft_payload(payload, TEMPLATES_DIR)
        if not validation["valid"]:
            raise falcon.HTTPBadRequest(description=validation["message"])
        try:
            draft = create_draft_record(payload)
        except (RuntimeError, ValueError) as exc:
            raise falcon.HTTPBadRequest(description=str(exc)) from exc
        resp.status = falcon.HTTP_201
        resp.set_header("ETag", f'"{draft["record_version"]}"')
        resp.media = item_response(draft)


class DraftResource:
    def on_get(self, req: falcon.Request, resp: falcon.Response, draft_id: str) -> None:
        draft = require_draft(draft_id)
        resp.set_header("ETag", f'"{draft["record_version"]}"')
        resp.media = item_response(draft)

    def on_patch(self, req: falcon.Request, resp: falcon.Response, draft_id: str) -> None:
        current = require_draft(draft_id)
        expected_version = _if_match_version(req)
        payload = read_json(req)
        merged = {
            "briefing_type": current["briefing_type"],
            "template_version": current["template_version"],
            "sections": payload.get("sections", current["sections"]),
        }
        validation = validate_draft_payload(merged, TEMPLATES_DIR)
        if not validation["valid"]:
            raise falcon.HTTPBadRequest(description=validation["message"])
        try:
            updated = update_draft_record(
                draft_id,
                payload,
                expected_version=expected_version,
            )
        except RecordRevisionConflict as exc:
            _revision_conflict(req, resp, exc)
            return
        if updated is None:
            raise falcon.HTTPNotFound(description=f"Draft '{draft_id}' was not found.")
        resp.set_header("ETag", f'"{updated["record_version"]}"')
        resp.media = item_response(updated)


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


class DeriveResource:
    def on_post(self, req: falcon.Request, resp: falcon.Response, draft_id: str) -> None:
        draft = require_draft(draft_id)
        payload = read_json(req)
        resp.media = result_response(derive_from_master(draft, payload, TEMPLATES_DIR))


class PreviewResource:
    def on_post(self, req: falcon.Request, resp: falcon.Response, draft_id: str) -> None:
        draft = require_draft(draft_id)
        payload = read_json(req)
        resp.media = result_response(generate_html_preview(draft, payload, TEMPLATES_DIR))


class PdfResource:
    def on_post(self, req: falcon.Request, resp: falcon.Response, draft_id: str) -> None:
        draft = require_draft(draft_id)
        payload = read_json(req)
        output = generate_pdf_output(draft, payload, TEMPLATES_DIR)
        save_generated_output(draft_id, output)
        resp.media = result_response(output)


class SocialGraphicsDraftCollectionResource:
    def on_post(self, req: falcon.Request, resp: falcon.Response) -> None:
        payload = read_json(req)
        validation = validate_social_graphics_scene(payload.get("scene"))
        if not validation["valid"]:
            raise falcon.HTTPBadRequest(description=validation["message"])
        resp.status = falcon.HTTP_201
        draft = create_social_graphics_draft_record(payload)
        resp.set_header("ETag", f'"{draft["record_version"]}"')
        resp.media = item_response(draft)


class SocialGraphicsDraftResource:
    def on_get(self, req: falcon.Request, resp: falcon.Response, draft_id: str) -> None:
        draft = require_social_graphics_draft(draft_id)
        resp.set_header("ETag", f'"{draft["record_version"]}"')
        resp.media = item_response(draft)

    def on_patch(self, req: falcon.Request, resp: falcon.Response, draft_id: str) -> None:
        payload = read_json(req)
        expected_version = _if_match_version(req)
        validation = validate_social_graphics_scene(payload.get("scene"))
        if not validation["valid"]:
            raise falcon.HTTPBadRequest(description=validation["message"])
        try:
            updated = update_social_graphics_draft_record(
                draft_id,
                payload,
                expected_version=expected_version,
            )
        except RecordRevisionConflict as exc:
            _revision_conflict(req, resp, exc)
            return
        if updated is None:
            raise falcon.HTTPNotFound(
                description=f"Social graphics draft '{draft_id}' was not found."
            )
        resp.set_header("ETag", f'"{updated["record_version"]}"')
        resp.media = item_response(updated)


class SocialGraphicsExportCollectionResource:
    def on_post(self, req: falcon.Request, resp: falcon.Response) -> None:
        payload = read_json(req)
        validation = validate_social_graphics_scene(payload.get("scene"))
        if not validation["valid"]:
            raise falcon.HTTPBadRequest(description=validation["message"])
        if "base_png" not in payload:
            raise falcon.HTTPBadRequest(description="Export payload requires a base_png data URL.")

        export_record = build_export_artifacts(payload, GENERATED_DIR)
        stored = save_social_graphics_export_record(export_record)
        resp.status = falcon.HTTP_201
        resp.media = result_response({
            "export_id": stored["export_id"],
            "draft_id": stored["draft_id"],
            "created_at": stored["created_at"],
            "variants": [
                {
                    "variant_id": variant["variant_id"],
                    "label": variant["label"],
                    "width": variant["width"],
                    "height": variant["height"],
                    "url": variant["url"],
                }
                for variant in stored["variants"]
            ],
        })


class SocialGraphicsAssetResource:
    def on_get(
        self,
        req: falcon.Request,
        resp: falcon.Response,
        export_id: str,
        variant_id: str,
    ) -> None:
        export_record = require_social_graphics_export(export_id)
        variant = next(
            (item for item in export_record["variants"] if item["variant_id"] == variant_id),
            None,
        )
        if not variant:
            raise falcon.HTTPNotFound(
                description=f"Variant '{variant_id}' was not found for export '{export_id}'."
            )

        asset_path = Path(variant["path"])
        if not asset_path.exists():
            raise falcon.HTTPNotFound(description="Requested export asset is missing on disk.")

        resp.content_type = "image/png"
        resp.data = asset_path.read_bytes()


class ActiveAlertsResource:
    def on_get(self, req: falcon.Request, resp: falcon.Response) -> None:
        resp.media = collection_response(get_active_alert_context())


class ActiveIcaoAdvisoriesResource:
    def on_get(self, req: falcon.Request, resp: falcon.Response) -> None:
        resp.media = collection_response(get_active_icao_advisory_context())
