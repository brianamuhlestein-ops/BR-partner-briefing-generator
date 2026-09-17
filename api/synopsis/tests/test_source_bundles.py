from __future__ import annotations

import copy
import json
import tempfile
import threading
import unittest
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from wsgiref.simple_server import WSGIRequestHandler, make_server

import falcon
from falcon import testing

from api.synopsis.app import create_app
from api.synopsis.config import load_settings
from api.synopsis.contracts import ContractCatalog
from api.synopsis.persistence import BundleStore
from api.synopsis.producer_client import HttpProducerClient, ProducerRequestError
from api.synopsis.services.bundles import BundleService, canonical_sha256


WORKSPACE_ROOT = Path(__file__).resolve().parents[4]
OBSERVATIONS_EXAMPLES = (
    WORKSPACE_ROOT
    / "AN-geomagnetic-observations-monitor"
    / "docs"
    / "api"
    / "examples"
    / "contexts"
)
FORECAST_EXAMPLES = (
    WORKSPACE_ROOT
    / "FC-geomagnetic-forecast-console"
    / "docs"
    / "api"
    / "examples"
    / "contexts"
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _operational_contexts() -> dict[str, list[dict[str, Any]]]:
    return {
        "geomagnetic-observations-monitor": [
            _load(
                OBSERVATIONS_EXAMPLES
                / "swift-geomagnetic-observations-monitor-context-v1.operational.example.json"
            )
        ],
        "geomagnetic-forecast-console": [
            _load(
                FORECAST_EXAMPLES
                / "swift-geomagnetic-forecast-console-context-v1.operational.example.json"
            )
        ],
    }


def _replay_contexts() -> dict[str, list[dict[str, Any]]]:
    return {
        "geomagnetic-observations-monitor": [
            _load(
                OBSERVATIONS_EXAMPLES
                / "swift-geomagnetic-observations-monitor-context-v1.replay.example.json"
            )
        ],
        "geomagnetic-forecast-console": [
            _load(
                FORECAST_EXAMPLES
                / "swift-geomagnetic-forecast-console-context-v1.replay.example.json"
            )
        ],
    }


class FakeProducerClient:
    def __init__(self, contexts: dict[str, list[dict[str, Any]]]) -> None:
        self.contexts = contexts

    def list_exports(self, application_slug: str) -> list[dict[str, Any]]:
        if application_slug not in self.contexts:
            raise ProducerRequestError("producer_unavailable", "producer unavailable", True)
        return [
            {
                "context_id": item["context_id"],
                "schema": item["schema"],
                "generated_at_utc": item["generated_at_utc"],
                "lifecycle_state": item["lifecycle"]["state"],
            }
            for item in self.contexts[application_slug]
        ]

    def get_export(self, application_slug: str, context_id: str) -> dict[str, Any]:
        for context in self.contexts.get(application_slug, []):
            if context["context_id"] == context_id:
                return copy.deepcopy(context)
        raise ProducerRequestError("context_not_found", "context not found", False)


class _ExportCollectionResource:
    def __init__(self, contexts: list[dict[str, Any]]) -> None:
        self.contexts = contexts

    def on_get(self, req: falcon.Request, resp: falcon.Response) -> None:
        items = [
            {
                "context_id": item["context_id"],
                "schema": item["schema"],
                "generated_at_utc": item["generated_at_utc"],
                "lifecycle_state": item["lifecycle"]["state"],
            }
            for item in self.contexts
        ]
        resp.media = {"status": "ok", "items": items, "total": len(items)}


class _ExportDetailResource:
    def __init__(self, contexts: list[dict[str, Any]]) -> None:
        self.contexts = {item["context_id"]: item for item in contexts}

    def on_get(
        self,
        req: falcon.Request,
        resp: falcon.Response,
        context_id: str,
    ) -> None:
        context = self.contexts.get(context_id)
        if context is None:
            raise falcon.HTTPNotFound()
        resp.media = {"status": "ok", "item": context}


class _QuietRequestHandler(WSGIRequestHandler):
    def log_message(self, format: str, *args) -> None:
        return


class LiveProducerServer:
    def __init__(self, contexts: list[dict[str, Any]]) -> None:
        app = falcon.App()
        app.add_route(
            "/api/v1/geomagnetic/context/exports",
            _ExportCollectionResource(contexts),
        )
        app.add_route(
            "/api/v1/geomagnetic/context/exports/{context_id}",
            _ExportDetailResource(contexts),
        )
        self.server = make_server(
            "127.0.0.1",
            0,
            app,
            handler_class=_QuietRequestHandler,
        )
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)

    def __enter__(self) -> str:
        self.thread.start()
        return f"http://127.0.0.1:{self.server.server_port}"

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.server.shutdown()
        self.thread.join(timeout=5)
        self.server.server_close()


class SourceBundleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.settings = replace(load_settings(), data_root=Path(self.temp_dir.name))

    def _service(
        self,
        contexts: dict[str, list[dict[str, Any]]],
        *,
        settings=None,
    ) -> tuple[BundleService, BundleStore]:
        settings = settings or self.settings
        store = BundleStore(settings.bundle_root)
        service = BundleService(
            settings=settings,
            contracts=ContractCatalog(settings),
            producer_client=FakeProducerClient(contexts),
            store=store,
            now=lambda: datetime(2026, 8, 17, 15, 0, tzinfo=timezone.utc),
        )
        return service, store

    def test_operational_collection_freezes_both_contexts_and_fact_ledger(self) -> None:
        contexts = _operational_contexts()
        service, store = self._service(contexts)
        bundle = service.create_bundle(
            cutoff_at_utc="2026-08-14T22:00:00Z",
            context_ids=None,
            actor_id="summary-builder-service",
            actor_type="service",
        )

        self.assertEqual(bundle["state"], "ready")
        self.assertEqual(
            [item["application_slug"] for item in bundle["sources"]],
            [
                "geomagnetic-observations-monitor",
                "geomagnetic-forecast-console",
            ],
        )
        self.assertEqual(len(bundle["fact_ledger"]), 4)
        self.assertEqual(store.read(bundle["bundle_id"]), bundle)
        for source in bundle["sources"]:
            context = contexts[source["application_slug"]][0]
            self.assertEqual(source["source_sha256"], canonical_sha256(context))

    def test_automatic_observations_feed_narrative_without_manual_export(self) -> None:
        contexts = _operational_contexts()
        observed = contexts["geomagnetic-observations-monitor"][0]
        observed["lifecycle"]["state"] = "working"
        observed["lifecycle"]["reviewed_at_utc"] = None
        service, _ = self._service(contexts)
        bundle = service.create_bundle(
            cutoff_at_utc="2026-08-14T22:05:00Z", context_ids=None,
            actor_id="narrative-builder", actor_type="service",
        )
        self.assertEqual(bundle["state"], "ready")
        self.assertEqual(bundle["sources"][0]["lifecycle_state"], "working")
        self.assertTrue(bundle["fact_ledger"])
        client = testing.TestClient(create_app(
            settings=self.settings, producer_client=FakeProducerClient(contexts),
        ))
        draft = client.simulate_post(
            "/api/v1/space-weather-summary/drafts",
            json={"bundle_id": bundle["bundle_id"]},
        )
        self.assertEqual(draft.status_code, 201)
        self.assertTrue(draft.json["item"]["sections"])
        stale = service.create_bundle(
            cutoff_at_utc="2026-08-14T22:10:01Z", context_ids=None,
            actor_id="narrative-builder", actor_type="service",
        )
        self.assertEqual(stale["state"], "needs_attention")
        contexts["geomagnetic-forecast-console"][0]["lifecycle"]["state"] = "working"
        unreviewed_forecast = service.create_bundle(
            cutoff_at_utc="2026-08-14T22:05:00Z", context_ids=None,
            actor_id="narrative-builder", actor_type="service",
        )
        self.assertEqual(unreviewed_forecast["state"], "needs_attention")

    def test_missing_forecast_context_needs_attention_and_blocks_ledger(self) -> None:
        contexts = _operational_contexts()
        contexts.pop("geomagnetic-forecast-console")
        service, _ = self._service(contexts)
        bundle = service.create_bundle(
            cutoff_at_utc="2026-08-14T22:00:00Z",
            context_ids=None,
            actor_id="summary-builder-service",
            actor_type="service",
        )

        self.assertEqual(bundle["state"], "needs_attention")
        self.assertEqual(bundle["fact_ledger"], [])
        forecast = bundle["sources"][1]
        self.assertEqual(forecast["status"], "missing")
        self.assertTrue(bundle["collection_errors"])

    def test_replay_collection_requires_matching_mode_and_scenario(self) -> None:
        settings = replace(
            self.settings,
            runtime_mode="replay",
            replay_scenario="may_2024_geomagnetic_storm",
        )
        service, _ = self._service(_replay_contexts(), settings=settings)
        bundle = service.create_bundle(
            cutoff_at_utc="2024-05-11T03:00:00Z",
            context_ids=None,
            actor_id="exercise.forecaster",
            actor_type="forecaster",
        )

        self.assertEqual(bundle["state"], "ready")
        self.assertEqual(bundle["runtime"]["mode"], "replay")
        self.assertEqual(bundle["runtime"]["scenario"], "may_2024_geomagnetic_storm")

    def test_runtime_mismatch_is_not_ready(self) -> None:
        service, _ = self._service(_replay_contexts())
        bundle = service.create_bundle(
            cutoff_at_utc="2024-05-11T03:00:00Z",
            context_ids=None,
            actor_id="summary-builder-service",
            actor_type="service",
        )
        self.assertEqual(bundle["state"], "needs_attention")
        self.assertTrue(
            any(error["code"] == "runtime_mode_mismatch" for error in bundle["collection_errors"])
        )

    def test_stale_context_is_not_ready(self) -> None:
        contexts = _operational_contexts()
        contexts["geomagnetic-observations-monitor"][0]["quality"].update(
            {"status": "degraded", "stale": True}
        )
        service, _ = self._service(contexts)
        bundle = service.create_bundle(
            cutoff_at_utc="2026-08-14T22:00:00Z",
            context_ids=None,
            actor_id="summary-builder-service",
            actor_type="service",
        )
        self.assertEqual(bundle["state"], "needs_attention")
        self.assertTrue(
            any(
                error["code"] == "context_quality_not_eligible"
                for error in bundle["collection_errors"]
            )
        )

    def test_superseded_context_is_not_ready(self) -> None:
        contexts = _operational_contexts()
        forecast = contexts["geomagnetic-forecast-console"][0]
        forecast["lifecycle"]["state"] = "superseded"
        forecast["lifecycle"]["superseded_by_context_id"] = "gfc-newer-context"
        service, _ = self._service(contexts)
        bundle = service.create_bundle(
            cutoff_at_utc="2026-08-14T22:00:00Z",
            context_ids=None,
            actor_id="summary-builder-service",
            actor_type="service",
        )
        self.assertEqual(bundle["state"], "needs_attention")
        self.assertTrue(
            any(error["code"] == "context_superseded" for error in bundle["collection_errors"])
        )

    def test_experimental_fact_is_not_promoted_to_ledger(self) -> None:
        contexts = _operational_contexts()
        experimental = copy.deepcopy(
            contexts["geomagnetic-observations-monitor"][0]["narrative_facts"][0]
        )
        experimental["fact_id"] = "experimental-test-fact"
        experimental["experimental"] = True
        experimental["not_for_alerting"] = True
        contexts["geomagnetic-observations-monitor"][0]["narrative_facts"].append(experimental)
        service, _ = self._service(contexts)
        bundle = service.create_bundle(
            cutoff_at_utc="2026-08-14T22:00:00Z",
            context_ids=None,
            actor_id="summary-builder-service",
            actor_type="service",
        )

        self.assertEqual(bundle["state"], "ready")
        self.assertNotIn(
            "geomagnetic-observations-monitor:experimental-test-fact",
            [item["ledger_fact_id"] for item in bundle["fact_ledger"]],
        )

    def test_api_creates_lists_and_retrieves_immutable_bundle(self) -> None:
        client = testing.TestClient(
            create_app(
                settings=self.settings,
                producer_client=FakeProducerClient(_operational_contexts()),
            )
        )
        created = client.simulate_post(
            "/api/v1/space-weather-summary/source-bundles",
            json={
                "cutoff_at_utc": "2026-08-14T22:00:00Z",
                "actor_id": "operations.forecaster",
                "actor_type": "forecaster",
            },
        )
        self.assertEqual(created.status_code, 201)
        bundle_id = created.json["item"]["bundle_id"]
        self.assertEqual(created.json["item"]["state"], "ready")

        listing = client.simulate_get("/api/v1/space-weather-summary/source-bundles")
        self.assertEqual(listing.status_code, 200)
        self.assertEqual(listing.json["total"], 1)
        self.assertEqual(listing.json["items"][0]["bundle_id"], bundle_id)

        detail = client.simulate_get(
            f"/api/v1/space-weather-summary/source-bundles/{bundle_id}"
        )
        self.assertEqual(detail.status_code, 200)
        self.assertEqual(detail.json["item"], created.json["item"])

        missing = client.simulate_get(
            "/api/v1/space-weather-summary/source-bundles/ssb-missing"
        )
        self.assertEqual(missing.status_code, 404)
        self.assertEqual(missing.json["request_id"], missing.headers["X-Request-ID"])

        traced = client.simulate_get(
            "/health", headers={"X-Request-ID": "summary-builder-test"}
        )
        self.assertEqual(traced.headers["X-Request-ID"], "summary-builder-test")

    def test_api_rejects_out_of_scope_context_id(self) -> None:
        client = testing.TestClient(
            create_app(
                settings=self.settings,
                producer_client=FakeProducerClient(_operational_contexts()),
            )
        )
        response = client.simulate_post(
            "/api/v1/space-weather-summary/source-bundles",
            json={
                "cutoff_at_utc": "2026-08-14T22:00:00Z",
                "context_ids": {"sunspot-classification-studio": "sunspot-1"},
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json["error"]["code"], "invalid_bundle_request")

    def test_http_client_collects_from_live_producer_route_stubs(self) -> None:
        contexts = _operational_contexts()
        with LiveProducerServer(contexts["geomagnetic-observations-monitor"]) as observations_url:
            with LiveProducerServer(contexts["geomagnetic-forecast-console"]) as forecast_url:
                settings = replace(
                    self.settings,
                    observations_base_url=observations_url,
                    forecast_base_url=forecast_url,
                )
                store = BundleStore(settings.bundle_root)
                service = BundleService(
                    settings=settings,
                    contracts=ContractCatalog(settings),
                    producer_client=HttpProducerClient(settings),
                    store=store,
                    now=lambda: datetime(2026, 8, 17, 15, 0, tzinfo=timezone.utc),
                )
                bundle = service.create_bundle(
                    cutoff_at_utc="2026-08-14T22:00:00Z",
                    context_ids=None,
                    actor_id="http-integration-test",
                    actor_type="service",
                )

        self.assertEqual(bundle["state"], "ready")
        self.assertEqual(len(bundle["sources"]), 2)
        self.assertEqual(len(bundle["fact_ledger"]), 4)

    def test_api_creates_cited_deterministic_draft_from_ready_bundle(self) -> None:
        client = testing.TestClient(
            create_app(
                settings=self.settings,
                producer_client=FakeProducerClient(_operational_contexts()),
            )
        )
        bundle_response = client.simulate_post(
            "/api/v1/space-weather-summary/source-bundles",
            json={"cutoff_at_utc": "2026-08-14T22:00:00Z"},
        )
        bundle = bundle_response.json["item"]
        draft_response = client.simulate_post(
            "/api/v1/space-weather-summary/drafts",
            json={
                "bundle_id": bundle["bundle_id"],
                "actor_id": "operations.forecaster",
                "actor_type": "forecaster",
            },
        )

        self.assertEqual(draft_response.status_code, 201)
        draft = draft_response.json["item"]
        self.assertEqual(draft["generation"]["method"], "deterministic_template")
        self.assertIsNone(draft["generation"]["model"])
        self.assertEqual(draft["source_bundle"]["integrity_sha256"], bundle["integrity"]["sha256"])
        available = {item["ledger_fact_id"] for item in bundle["fact_ledger"]}
        for section in draft["sections"]:
            for sentence in section["sentences"]:
                self.assertTrue(set(sentence["support_fact_ids"]) <= available)

        listing = client.simulate_get("/api/v1/space-weather-summary/drafts")
        self.assertEqual(listing.status_code, 200)
        self.assertEqual(listing.json["total"], 1)
        detail = client.simulate_get(
            f"/api/v1/space-weather-summary/drafts/{draft['draft_id']}"
        )
        self.assertEqual(detail.status_code, 200)
        self.assertEqual(detail.json["item"], draft)

    def test_api_rejects_draft_from_needs_attention_bundle(self) -> None:
        contexts = _operational_contexts()
        contexts.pop("geomagnetic-forecast-console")
        client = testing.TestClient(
            create_app(
                settings=self.settings,
                producer_client=FakeProducerClient(contexts),
            )
        )
        bundle_response = client.simulate_post(
            "/api/v1/space-weather-summary/source-bundles",
            json={"cutoff_at_utc": "2026-08-14T22:00:00Z"},
        )
        bundle = bundle_response.json["item"]
        self.assertEqual(bundle["state"], "needs_attention")

        draft_response = client.simulate_post(
            "/api/v1/space-weather-summary/drafts",
            json={"bundle_id": bundle["bundle_id"]},
        )
        self.assertEqual(draft_response.status_code, 400)
        self.assertEqual(draft_response.json["error"]["code"], "invalid_draft_request")


if __name__ == "__main__":
    unittest.main()
