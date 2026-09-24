import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import falcon
from waitress import serve

from api.config import get_settings
from api.errors import register_error_handlers
from api.middleware import CorsMiddleware, RequestContextMiddleware
from api.persistence import initialize_storage
from api.routes import register_routes


def create_app() -> falcon.App:
    initialize_storage()
    app = falcon.App(middleware=[RequestContextMiddleware(), CorsMiddleware()])
    register_routes(app)
    register_error_handlers(app)
    from api.synopsis.app import create_app as install_synopsis
    from api.synopsis.workspace import WorkspaceResource, ReviewResource, DeliveryResource
    from api.synopsis.exercise import ExerciseResource
    from api.synopsis.cme_context import CmeContextResource
    app.add_route('/api/v1/space-weather-summary/exercise', ExerciseResource())
    app.add_route('/api/v1/space-weather-summary/source-context/cme-sa', CmeContextResource())
    install_synopsis(existing_app=app)
    app.add_route('/api/v1/space-weather-summary/workspace', WorkspaceResource())
    app.add_route('/api/v1/space-weather-summary/reviewed', ReviewResource())
    app.add_route('/api/v1/space-weather-summary/deliver', DeliveryResource())
    return app


app = application = create_app()


if __name__ == "__main__":
    settings = get_settings()
    serve(app, host=settings["host"], port=settings["port"])
