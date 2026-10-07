from __future__ import annotations

import falcon

from api.synopsis.config import Settings
from api.synopsis.persistence import BundleStore, DraftStore
from api.synopsis.resources.bundles import SourceBundleCollectionResource, SourceBundleResource
from api.synopsis.resources.drafts import DraftCollectionResource, DraftResource
from api.synopsis.resources.health import HealthResource
from api.synopsis.services.bundles import BundleService
from api.synopsis.services.drafts import DraftService


API_PREFIX = "/api/v1/space-weather-summary"


def register_routes(
    app: falcon.App,
    *,
    include_root_health: bool = True,
    settings: Settings,
    service: BundleService,
    store: BundleStore,
    draft_service: DraftService,
    draft_store: DraftStore,
) -> None:
    health = HealthResource(settings)
    if include_root_health:
        app.add_route("/health", health)
    app.add_route(
        f"{API_PREFIX}/source-bundles",
        SourceBundleCollectionResource(service, store),
    )
    app.add_route(
        f"{API_PREFIX}/source-bundles/{{bundle_id}}",
        SourceBundleResource(store),
    )
    app.add_route(
        f"{API_PREFIX}/drafts",
        DraftCollectionResource(draft_service, draft_store),
    )
    app.add_route(
        f"{API_PREFIX}/drafts/{{draft_id}}",
        DraftResource(draft_store),
    )
