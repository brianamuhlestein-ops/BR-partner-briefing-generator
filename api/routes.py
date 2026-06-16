import falcon

from api.resources import (
    ActiveAlertsResource,
    ActiveIcaoAdvisoriesResource,
    BriefingTypesResource,
    DeriveResource,
    DraftCollectionResource,
    DraftResource,
    HealthResource,
    PdfResource,
    PreviewResource,
    SocialGraphicsAssetResource,
    SocialGraphicsDraftCollectionResource,
    SocialGraphicsDraftResource,
    SocialGraphicsExportCollectionResource,
    TemplateResource,
    TemplateVersionResource,
)


PUBLIC_PREFIX = "/api/v1/partner-briefing"


def _add_partner_briefing_routes(app: falcon.App, prefix: str) -> None:
    app.add_route(f"{prefix}/briefing-types", BriefingTypesResource())
    app.add_route(f"{prefix}/templates/{{briefing_type}}", TemplateResource())
    app.add_route(
        f"{prefix}/templates/{{briefing_type}}/versions/{{version}}",
        TemplateVersionResource(),
    )
    app.add_route(f"{prefix}/drafts", DraftCollectionResource())
    app.add_route(f"{prefix}/drafts/{{draft_id}}", DraftResource())
    app.add_route(f"{prefix}/drafts/{{draft_id}}/derive", DeriveResource())
    app.add_route(f"{prefix}/drafts/{{draft_id}}/preview", PreviewResource())
    app.add_route(f"{prefix}/drafts/{{draft_id}}/pdf", PdfResource())
    app.add_route(f"{prefix}/social-graphics/drafts", SocialGraphicsDraftCollectionResource())
    app.add_route(f"{prefix}/social-graphics/drafts/{{draft_id}}", SocialGraphicsDraftResource())
    app.add_route(f"{prefix}/social-graphics/exports", SocialGraphicsExportCollectionResource())
    app.add_route(
        f"{prefix}/social-graphics/exports/{{export_id}}/assets/{{variant_id}}",
        SocialGraphicsAssetResource(),
    )
    app.add_route(f"{prefix}/context/alerts/active", ActiveAlertsResource())
    app.add_route(
        f"{prefix}/context/advisories/icao/active",
        ActiveIcaoAdvisoriesResource(),
    )


def register_routes(app: falcon.App) -> None:
    app.add_route("/health", HealthResource())
    _add_partner_briefing_routes(app, PUBLIC_PREFIX)
