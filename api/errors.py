import logging

import falcon


LOGGER = logging.getLogger(__name__)


def handle_uncaught_exception(
    req: falcon.Request,
    resp: falcon.Response,
    ex: Exception,
    params: dict,
) -> None:
    LOGGER.exception("Unhandled API exception")
    resp.status = falcon.HTTP_500
    resp.media = {
        "status": "error",
        "error": {
            "code": "internal_error",
            "message": "An unexpected server error occurred.",
        },
        "request_id": req.context.request_id,
    }


def register_error_handlers(app: falcon.App) -> None:
    app.add_error_handler(Exception, handle_uncaught_exception)
