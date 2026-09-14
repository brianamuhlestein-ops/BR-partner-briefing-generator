from __future__ import annotations

import falcon

from api.synopsis.persistence import DraftStore
from api.synopsis.resources.bundles import _limit
from api.synopsis.services.drafts import DraftInputError, DraftService


class DraftCollectionResource:
    def __init__(self, service: DraftService, store: DraftStore) -> None:
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
            raise DraftInputError("Request body must be a JSON object")
        bundle_id = str(body.get("bundle_id") or "").strip()
        if not bundle_id:
            raise DraftInputError("bundle_id is required")
        draft = self.service.create_draft(
            bundle_id=bundle_id,
            actor_id=str(body.get("actor_id") or "summary-builder-service"),
            actor_type=str(body.get("actor_type") or "service"),
        )
        resp.status = falcon.HTTP_201
        resp.location = f"/api/v1/space-weather-summary/drafts/{draft['draft_id']}"
        resp.media = {"status": "ok", "item": draft}


class DraftResource:
    def __init__(self, store: DraftStore) -> None:
        self.store = store

    def on_get(self, req: falcon.Request, resp: falcon.Response, draft_id: str) -> None:
        resp.status = falcon.HTTP_200
        resp.media = {"status": "ok", "item": self.store.read(draft_id)}
