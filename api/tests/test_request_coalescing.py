from __future__ import annotations

import io
import json
import os
import time
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from unittest.mock import patch

from api import runtime
from api.synopsis import cme_context, producer_client
from api.synopsis.config import load_settings
from api.synopsis.producer_client import HttpProducerClient


def _parallel(operation, workers: int = 4):
    with ThreadPoolExecutor(max_workers=workers) as executor:
        return [future.result(timeout=10) for future in [executor.submit(operation) for _ in range(workers)]]


def _counted_response(payload: dict, calls: list[int], lock: Lock):
    with lock:
        calls.append(1)
    time.sleep(0.1)
    return io.BytesIO(json.dumps(payload).encode("utf-8"))


def test_four_replay_clock_reads_share_one_active_hel_request():
    calls: list[int] = []
    lock = Lock()
    payload = {"event_id": "gannon-2024", "clock_utc": "2024-05-10T18:00:00Z"}
    environment = {
        "PARTNER_BRIEFING_SOURCE_MODE": "gannon",
        "SWIFT_REPLAY_CATALOG_URL": "http://hel/api/v1/historical-events/gannon-2024",
        "SWIFT_REPLAY_SESSION_ID": "briefing-test",
    }
    with patch.dict(os.environ, environment, clear=True), patch.object(
        runtime,
        "urlopen",
        side_effect=lambda *args, **kwargs: _counted_response(payload, calls, lock),
    ):
        results = _parallel(runtime.hel_session)

    assert len(calls) == 1
    assert results == [payload] * 4
    assert len({id(result) for result in results}) == 4


def test_four_identical_producer_reads_share_one_active_request():
    calls: list[int] = []
    lock = Lock()
    payload = {"items": [{"context_id": "gom-1"}]}
    client = HttpProducerClient(load_settings())
    with patch.object(
        producer_client,
        "urlopen",
        side_effect=lambda *args, **kwargs: _counted_response(payload, calls, lock),
    ):
        results = _parallel(lambda: client.list_exports("geomagnetic-observations-monitor"))

    assert len(calls) == 1
    assert results == [payload["items"]] * 4
    assert len({id(result[0]) for result in results}) == 4


def test_four_cme_context_reads_share_one_active_request(monkeypatch):
    calls: list[int] = []
    lock = Lock()
    context = {
        "schema": "swift-cme-sa-display-context-v1",
        "context_id": "cme-1-r1",
        "runtime": {"mode": "operational", "scenario": None},
        "lifecycle": {
            "state": "reviewed",
            "revision": 1,
            "reviewed_at_utc": "2026-10-16T12:00:00Z",
            "superseded_by_context_id": None,
        },
        "quality": {"status": "usable", "available": True, "stale": False, "partial": False},
        "cme_analysis": {
            "assessment": {
                "assessment_id": "assessment-1",
                "revision_id": "R01",
                "nominal_arrival_utc": "2026-10-17T12:00:00Z",
                "arrival_window_start_utc": "2026-10-17T06:00:00Z",
                "arrival_window_end_utc": "2026-10-17T18:00:00Z",
            },
            "evidence_agreement": {},
        },
    }
    monkeypatch.setenv("SYNOPSIS_CME_CONTEXT_URL", "http://cme/context")
    monkeypatch.setattr(
        cme_context,
        "runtime_status",
        lambda: {
            "status": "ok",
            "data_source": "operational",
            "scenario": None,
            "now_utc": "2026-10-16T12:00:00Z",
        },
    )
    monkeypatch.setattr(
        cme_context,
        "urlopen",
        lambda *args, **kwargs: _counted_response({"item": context}, calls, lock),
    )

    results = _parallel(cme_context.reviewed_cme_context)

    assert len(calls) == 1
    assert [result["source"]["context_id"] for result in results] == ["cme-1-r1"] * 4
