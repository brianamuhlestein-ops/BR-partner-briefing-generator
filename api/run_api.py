import os
import sys
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import falcon
from waitress import serve

from api.briefing_api import add_routes
from api.config import get_settings
from api.persistence import initialize_storage


class CorsMiddleware:
    def process_response(self, req: falcon.Request, resp: falcon.Response, resource, req_succeeded):
        resp.set_header("Access-Control-Allow-Origin", get_settings()["cors_allow_origin"])
        resp.set_header("Access-Control-Allow-Methods", "GET, POST, PATCH, OPTIONS")
        resp.set_header("Access-Control-Allow-Headers", "Content-Type")

    def process_request(self, req: falcon.Request, resp: falcon.Response):
        if req.method == "OPTIONS":
            raise falcon.HTTPOk()


def create_app() -> falcon.App:
    initialize_storage()
    app = falcon.App(middleware=[CorsMiddleware()])
    add_routes(app)
    return app


app = create_app()


if __name__ == "__main__":
    settings = get_settings()
    serve(app, host=settings["host"], port=settings["port"])
