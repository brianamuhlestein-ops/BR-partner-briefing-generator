from __future__ import annotations

import logging

import falcon

from api.synopsis.persistence import BundleNotFoundError, DraftNotFoundError
from api.synopsis.services.bundles import BundleInputError
from api.synopsis.services.drafts import DraftInputError


LOGGER = logging.getLogger(__name__)


def _error(req: falcon.Request, resp: falcon.Response, status: str, code: str, message: str) -> None:
    resp.status = status
    resp.media = {
        "status": "error",
        "error": {"code": code, "message": message},
        "request_id": req.context.request_id,
    }


def handle_input_error(req, resp, error: BundleInputError, params) -> None:
    _error(req, resp, falcon.HTTP_400, "invalid_bundle_request", str(error))


def handle_not_found(req, resp, error: BundleNotFoundError, params) -> None:
    _error(req, resp, falcon.HTTP_404, "source_bundle_not_found", f"Source bundle not found: {error}")


def handle_draft_not_found(req, resp, error: DraftNotFoundError, params) -> None:
    _error(req, resp, falcon.HTTP_404, "summary_draft_not_found", f"Summary draft not found: {error}")


def handle_draft_input_error(req, resp, error: DraftInputError, params) -> None:
    _error(req, resp, falcon.HTTP_400, "invalid_draft_request", str(error))


def handle_uncaught(req, resp, error: Exception, params) -> None:
    LOGGER.exception("Unhandled Summary Builder API exception")
    _error(req, resp, falcon.HTTP_500, "internal_error", "An unexpected server error occurred.")


def register_error_handlers(app: falcon.App, *, include_generic: bool = True) -> None:
    app.add_error_handler(BundleInputError, handle_input_error)
    app.add_error_handler(BundleNotFoundError, handle_not_found)
    app.add_error_handler(DraftNotFoundError, handle_draft_not_found)
    app.add_error_handler(DraftInputError, handle_draft_input_error)
    if include_generic:
        app.add_error_handler(Exception, handle_uncaught)
