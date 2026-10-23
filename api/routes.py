import falcon

from api.resources import (
    EmailBriefingDocumentResource,
    HealthResource,
    RuntimeNowResource,
)


PUBLIC_PREFIX = "/api/v1/partner-briefing"


def _add_partner_briefing_routes(app: falcon.App, prefix: str) -> None:
    app.add_route(f"{prefix}/now", RuntimeNowResource())
    app.add_route(
        f"{prefix}/email-briefings/{{briefing_kind}}",
        EmailBriefingDocumentResource(),
    )


def register_routes(app: falcon.App) -> None:
    from api import research_capture as research, research_records as exports
    app.add_route(f"{PUBLIC_PREFIX}/research-captures", exports.CollectionResource(research.APPLICATION, research.FAMILIES, research.records))
    app.add_route(f"{PUBLIC_PREFIX}/research-captures/{{capture_id}}/export", exports.ExportResource(research.APPLICATION, research.FAMILIES, research.records))
    app.add_route("/health", HealthResource())
    _add_partner_briefing_routes(app, PUBLIC_PREFIX)
