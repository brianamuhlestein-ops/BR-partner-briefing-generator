from __future__ import annotations

from uuid import uuid4

import falcon


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
