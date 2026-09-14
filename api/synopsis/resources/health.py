from __future__ import annotations

from datetime import datetime, timezone

import falcon

from api.synopsis.config import Settings


class HealthResource:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def on_get(self, req: falcon.Request, resp: falcon.Response) -> None:
        resp.status = falcon.HTTP_200
        resp.media = {
            "status": "ok",
            "service": "briefing-synopsis-evidence",
            "time_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "scope": "geomagnetic-only",
            "registered_applications": [
                "geomagnetic-observations-monitor",
                "geomagnetic-forecast-console",
            ],
            "runtime_mode": self.settings.runtime_mode,
            "replay_scenario": self.settings.replay_scenario,
        }
