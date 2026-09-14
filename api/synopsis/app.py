from __future__ import annotations

import falcon

from api.synopsis.config import Settings, load_settings
from api.synopsis.contracts import ContractCatalog
from api.synopsis.errors import register_error_handlers
from api.synopsis.middleware import RequestContextMiddleware
from api.synopsis.persistence import BundleStore, DraftStore
from api.synopsis.producer_client import HttpProducerClient, ProducerClient
from api.synopsis.routes import register_routes
from api.synopsis.services.bundles import BundleService
from api.synopsis.services.drafts import DraftService


def create_app(
    *,
    settings: Settings | None = None,
    producer_client: ProducerClient | None = None,
    existing_app: falcon.App | None = None,
) -> falcon.App:
    settings = settings or load_settings()
    contracts = ContractCatalog(settings)
    store = BundleStore(settings.bundle_root)
    draft_store = DraftStore(settings.draft_root)
    client = producer_client or HttpProducerClient(settings)
    service = BundleService(
        settings=settings,
        contracts=contracts,
        producer_client=client,
        store=store,
    )
    draft_service = DraftService(
        contracts=contracts,
        bundle_store=store,
        draft_store=draft_store,
    )
    app = existing_app if existing_app is not None else falcon.App(middleware=[RequestContextMiddleware()])
    register_routes(
        app,
        include_root_health=existing_app is None,
        settings=settings,
        service=service,
        store=store,
        draft_service=draft_service,
        draft_store=draft_store,
    )
    register_error_handlers(app, include_generic=existing_app is None)
    return app
