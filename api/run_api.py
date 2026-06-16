import os
import sys
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import falcon
from waitress import serve

from api.config import get_settings
from api.errors import register_error_handlers
from api.middleware import CorsMiddleware
from api.persistence import initialize_storage
from api.routes import register_routes


def create_app() -> falcon.App:
    initialize_storage()
    app = falcon.App(middleware=[CorsMiddleware()])
    register_routes(app)
    register_error_handlers(app)
    return app


app = application = create_app()


if __name__ == "__main__":
    settings = get_settings()
    serve(app, host=settings["host"], port=settings["port"])
