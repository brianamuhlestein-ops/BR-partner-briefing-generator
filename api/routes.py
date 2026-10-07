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
    app.add_route("/health", HealthResource())
    _add_partner_briefing_routes(app, PUBLIC_PREFIX)
