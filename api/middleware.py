import falcon
from uuid import uuid4

from api.config import get_settings


MAX_REQUEST_ID_LENGTH = 128


class RequestContextMiddleware:
    def process_request(self, req: falcon.Request, resp: falcon.Response) -> None:
        supplied = (req.get_header("X-Request-ID") or "").strip()
        req.context.request_id = supplied[:MAX_REQUEST_ID_LENGTH] if supplied else str(uuid4())

    def process_response(
        self,
        req: falcon.Request,
        resp: falcon.Response,
        resource,
        req_succeeded: bool,
    ) -> None:
        resp.set_header("X-Request-ID", req.context.request_id)


class CorsMiddleware:
    def process_request(self, req: falcon.Request, resp: falcon.Response) -> None:
        if req.method == "OPTIONS":
            raise falcon.HTTPStatus(falcon.HTTP_204)

    def process_response(
        self,
        req: falcon.Request,
        resp: falcon.Response,
        resource,
        req_succeeded: bool,
    ) -> None:
        settings = get_settings()
        origin = req.get_header("Origin")
        allowed_origins = settings["cors_allow_origins"]

        if "*" in allowed_origins:
            allow_origin = "*"
        elif origin in allowed_origins:
            allow_origin = origin
        else:
            allow_origin = None

        if allow_origin:
            resp.set_header("Access-Control-Allow-Origin", allow_origin)
        resp.set_header("Access-Control-Allow-Methods", ", ".join(settings["cors_allow_methods"]))
        resp.set_header("Access-Control-Allow-Headers", ", ".join(settings["cors_allow_headers"]))
        resp.set_header("Vary", "Origin")
