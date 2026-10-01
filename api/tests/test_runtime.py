import os
import unittest
from unittest.mock import patch

from falcon import testing

from api import runtime
from api.run_api import create_app


class RuntimeClockTests(unittest.TestCase):
    def test_request_id_is_preserved_or_generated(self):
        client = testing.TestClient(create_app())
        supplied = client.simulate_get("/health", headers={"X-Request-ID": "briefing-test"})
        self.assertEqual(supplied.headers["X-Request-ID"], "briefing-test")

        generated = client.simulate_get("/health")
        self.assertTrue(generated.headers["X-Request-ID"])

    def test_operational_mode_uses_system_utc_and_ignores_replay_clock(self):
        with patch.dict(
            os.environ,
            {
                "PARTNER_BRIEFING_API_DATA_SOURCE": "operational",
                "PARTNER_BRIEFING_REPLAY_NOW_UTC": "2024-05-10T16:37:00Z",
            },
            clear=True,
        ):
            status = runtime.runtime_status()
        self.assertEqual(status["status"], "ok")
        self.assertEqual(status["data_source"], "operational")
        self.assertEqual(status["clock_source"], "operational_system_utc")
        self.assertIsNone(status["replay_now_env"])

    def test_replay_mode_requires_a_valid_clock(self):
        with patch.dict(
            os.environ,
            {"PARTNER_BRIEFING_API_DATA_SOURCE": "replay"},
            clear=True,
        ):
            status = runtime.runtime_status()
            with self.assertRaises(RuntimeError):
                runtime.effective_now_utc()
        self.assertEqual(status["status"], "configuration_error")
        self.assertIsNone(status["now_utc"])

    def test_replay_snapshot_derives_three_utc_forecast_dates(self):
        with patch.dict(
            os.environ,
            {
                "PARTNER_BRIEFING_API_DATA_SOURCE": "replay",
                "SWIFT_REPLAY_NOW_UTC": "2024-05-10T16:37:00Z",
                "PARTNER_BRIEFING_REPLAY_SCENARIO": "may_2024",
            },
            clear=True,
        ):
            snapshot = runtime.temporal_snapshot()
        self.assertEqual(snapshot["issue_time_utc"], "2024-05-10T16:37:00Z")
        self.assertEqual(snapshot["valid_dates"], ["2024-05-10", "2024-05-11", "2024-05-12"])
        self.assertEqual(snapshot["runtime_mode"], "replay")
        self.assertEqual(snapshot["replay_scenario"], "may_2024")

    def test_gannon_mode_reads_shared_hel_session(self):
        with patch.dict(
            os.environ,
            {
                "PARTNER_BRIEFING_SOURCE_MODE": "gannon",
                "SWIFT_REPLAY_CATALOG_URL": "http://hel/api/v1/historical-events/gannon-2024",
                "SWIFT_REPLAY_SESSION_ID": "session-1",
            },
            clear=True,
        ), patch.object(runtime, "hel_session", return_value={"event_id": "gannon-2024", "clock_utc": "2024-05-10T18:00:00Z"}):
            status = runtime.runtime_status()
        self.assertEqual(status["status"], "ok")
        self.assertEqual(status["source_mode"], "gannon")
        self.assertEqual(status["clock_source"], "swift_replay_session")
        self.assertEqual(status["now_utc"], "2024-05-10T18:00:00Z")


if __name__ == "__main__":
    unittest.main()
