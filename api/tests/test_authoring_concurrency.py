import os
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Barrier
from unittest.mock import patch

from falcon import testing

from api.persistence import (
    RecordRevisionConflict,
    create_draft_record,
    create_social_graphics_draft_record,
    get_draft_record,
    get_email_briefing_document,
    get_social_graphics_draft_record,
    initialize_storage,
    save_email_briefing_document,
    update_draft_record,
    update_social_graphics_draft_record,
)
from api.run_api import create_app


class AuthoringConcurrencyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        root = Path(self.temporary_directory.name)
        self.environment = patch.dict(
            os.environ,
            {
                "DATABASE_PATH": str(root / "briefings.db"),
                "GENERATED_DIR": str(root / "generated"),
            },
        )
        self.environment.start()
        initialize_storage()

    def tearDown(self) -> None:
        self.environment.stop()
        self.temporary_directory.cleanup()

    @staticmethod
    def _race(first, second) -> list[tuple[str, object]]:
        barrier = Barrier(2)

        def run(operation):
            barrier.wait()
            try:
                return "saved", operation()
            except RecordRevisionConflict as exc:
                return "conflict", exc.latest_version

        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [executor.submit(run, operation) for operation in (first, second)]
            return [future.result(timeout=10) for future in futures]

    def test_simultaneous_email_document_writes_keep_one_authoritative_version(self):
        created = save_email_briefing_document(
            "core", {"subject": "initial"}, expected_version=0
        )
        self.assertEqual(created["record_version"], 1)

        outcomes = self._race(
            lambda: save_email_briefing_document(
                "core", {"subject": "writer-a"}, expected_version=1
            ),
            lambda: save_email_briefing_document(
                "core", {"subject": "writer-b"}, expected_version=1
            ),
        )

        self.assertEqual([kind for kind, _ in outcomes].count("saved"), 1)
        self.assertEqual([kind for kind, _ in outcomes].count("conflict"), 1)
        self.assertEqual(get_email_briefing_document("core")["record_version"], 2)

    def test_simultaneous_draft_updates_reject_the_stale_writer(self):
        draft = create_draft_record({"sections": {"summary": "initial"}})
        outcomes = self._race(
            lambda: update_draft_record(
                draft["draft_id"],
                {"sections": {"summary": "writer-a"}},
                expected_version=1,
            ),
            lambda: update_draft_record(
                draft["draft_id"],
                {"sections": {"summary": "writer-b"}},
                expected_version=1,
            ),
        )

        self.assertEqual([kind for kind, _ in outcomes].count("saved"), 1)
        self.assertEqual([kind for kind, _ in outcomes].count("conflict"), 1)
        self.assertEqual(get_draft_record(draft["draft_id"])["record_version"], 2)

    def test_simultaneous_social_draft_updates_reject_the_stale_writer(self):
        draft = create_social_graphics_draft_record(
            {"template_id": "landscape", "scene": {"headline": "initial"}}
        )
        outcomes = self._race(
            lambda: update_social_graphics_draft_record(
                draft["draft_id"],
                {"scene": {"headline": "writer-a"}},
                expected_version=1,
            ),
            lambda: update_social_graphics_draft_record(
                draft["draft_id"],
                {"scene": {"headline": "writer-b"}},
                expected_version=1,
            ),
        )

        self.assertEqual([kind for kind, _ in outcomes].count("saved"), 1)
        self.assertEqual([kind for kind, _ in outcomes].count("conflict"), 1)
        self.assertEqual(
            get_social_graphics_draft_record(draft["draft_id"])["record_version"], 2
        )

    def test_email_api_requires_and_enforces_if_match(self):
        client = testing.TestClient(create_app())
        endpoint = "/api/v1/partner-briefing/email-briefings/core"

        missing = client.simulate_put(endpoint, json={"document": {"subject": "missing"}})
        self.assertEqual(missing.status_code, 428)

        created = client.simulate_put(
            endpoint,
            headers={"If-Match": '"0"'},
            json={"document": {"subject": "first"}},
        )
        self.assertEqual(created.status_code, 200)
        self.assertEqual(created.headers["ETag"], '"1"')
        self.assertEqual(created.json["item"]["record_version"], 1)

        stale = client.simulate_put(
            endpoint,
            headers={"If-Match": '"0"', "X-Request-ID": "stale-briefing"},
            json={"document": {"subject": "stale"}},
        )
        self.assertEqual(stale.status_code, 409)
        self.assertEqual(stale.headers["ETag"], '"1"')
        self.assertEqual(stale.json["error"]["code"], "revision_conflict")
        self.assertEqual(stale.json["request_id"], "stale-briefing")

        fetched = client.simulate_get(endpoint)
        self.assertEqual(fetched.headers["ETag"], '"1"')
        self.assertEqual(fetched.json["item"]["document"]["subject"], "first")

    def test_cors_advertises_the_authoring_precondition(self):
        client = testing.TestClient(create_app())
        response = client.simulate_options(
            "/api/v1/partner-briefing/email-briefings/core",
            headers={"Origin": "http://localhost:5180"},
        )

        self.assertEqual(response.status_code, 204)
        self.assertIn("PUT", response.headers["Access-Control-Allow-Methods"])
        self.assertIn("If-Match", response.headers["Access-Control-Allow-Headers"])


if __name__ == "__main__":
    unittest.main()
