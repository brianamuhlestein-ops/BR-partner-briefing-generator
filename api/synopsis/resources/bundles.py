from __future__ import annotations

import falcon

from api.synopsis.persistence import BundleStore
from api.synopsis.services.bundles import BundleInputError, BundleService


class SourceBundleCollectionResource:
    def __init__(self, service: BundleService, store: BundleStore) -> None:
        self.service = service
        self.store = store

    def on_get(self, req: falcon.Request, resp: falcon.Response) -> None:
        limit = _limit(req.get_param("limit"))
        items = self.store.list(limit=limit)
        resp.status = falcon.HTTP_200
        resp.media = {"status": "ok", "items": items, "total": len(items), "limit": limit}

    def on_post(self, req: falcon.Request, resp: falcon.Response) -> None:
        body = req.media if req.content_length not in (None, 0) else {}
        if not isinstance(body, dict):
            raise BundleInputError("Request body must be a JSON object")
        context_ids = body.get("context_ids")
        if context_ids is not None and not isinstance(context_ids, dict):
            raise BundleInputError("context_ids must be an object keyed by application slug")
        bundle = self.service.create_bundle(
            cutoff_at_utc=_optional_string(body.get("cutoff_at_utc")),
            context_ids={str(key): str(value) for key, value in (context_ids or {}).items()},
            actor_id=str(body.get("actor_id") or "summary-builder-service"),
            actor_type=str(body.get("actor_type") or "service"),
        )
        resp.status = falcon.HTTP_201
        resp.location = f"/api/v1/space-weather-summary/source-bundles/{bundle['bundle_id']}"
        resp.media = {"status": "ok", "item": bundle}


class SourceBundleResource:
    def __init__(self, store: BundleStore) -> None:
        self.store = store

    def on_get(self, req: falcon.Request, resp: falcon.Response, bundle_id: str) -> None:
        resp.status = falcon.HTTP_200
        resp.media = {"status": "ok", "item": self.store.read(bundle_id)}


def _limit(value: str | None) -> int:
    if value is None:
        return 25
    try:
        limit = int(value)
    except ValueError as exc:
        raise BundleInputError("limit must be an integer") from exc
    if not 1 <= limit <= 250:
        raise BundleInputError("limit must be between 1 and 250")
    return limit


def _optional_string(value) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None
