from datetime import datetime, timezone
from pathlib import Path

import falcon

from api.config import get_settings
from api.http import collection_response, item_response, read_json, result_response
from api.persistence import (
    create_draft_record,
    create_social_graphics_draft_record,
    get_draft_record,
    get_social_graphics_draft_record,
    get_social_graphics_export_record,
    save_generated_output,
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
        resp.media = {
            "status": runtime_status()["status"],
            "service": get_settings()["service_name"],
            "timeUtc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "runtime": runtime_status(),
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
        resp.media = item_response(draft)


class DraftResource:
    def on_get(self, req: falcon.Request, resp: falcon.Response, draft_id: str) -> None:
        resp.media = item_response(require_draft(draft_id))

    def on_patch(self, req: falcon.Request, resp: falcon.Response, draft_id: str) -> None:
        current = require_draft(draft_id)
        payload = read_json(req)
        merged = {
            "briefing_type": current["briefing_type"],
            "template_version": current["template_version"],
            "sections": payload.get("sections", current["sections"]),
        }
        validation = validate_draft_payload(merged, TEMPLATES_DIR)
        if not validation["valid"]:
            raise falcon.HTTPBadRequest(description=validation["message"])
        resp.media = item_response(update_draft_record(draft_id, payload))


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
        resp.media = item_response(create_social_graphics_draft_record(payload))


class SocialGraphicsDraftResource:
    def on_get(self, req: falcon.Request, resp: falcon.Response, draft_id: str) -> None:
        resp.media = item_response(require_social_graphics_draft(draft_id))

    def on_patch(self, req: falcon.Request, resp: falcon.Response, draft_id: str) -> None:
        payload = read_json(req)
        validation = validate_social_graphics_scene(payload.get("scene"))
        if not validation["valid"]:
            raise falcon.HTTPBadRequest(description=validation["message"])
        resp.media = item_response(update_social_graphics_draft_record(draft_id, payload))


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
