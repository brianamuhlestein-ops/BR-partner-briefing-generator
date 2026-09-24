from __future__ import annotations

import io
import json

import pytest
from falcon import testing

from api.run_api import create_app
from api.synopsis import cme_context


def _context(*, mode="operational", scenario=None, lifecycle="reviewed", partial=False):
    return {
        "schema": "swift-cme-sa-display-context-v1",
        "context_id": "cme-sa-assessment-1-r1",
        "runtime": {"mode": mode, "scenario": scenario, "effective_at_utc": "2026-09-24T12:00:00Z"},
        "lifecycle": {"state": lifecycle, "revision": 1, "reviewed_at_utc": "2026-09-24T12:00:00Z",
                      "superseded_by_context_id": None},
        "quality": {"status": "usable", "available": True, "stale": False, "partial": partial},
        "narrative_facts": [{"fact_id": "arrival-1", "kind": "cme_arrival_window"}],
        "provenance": {"sources": [{"source_type": "wsa_enlil"}]},
        "cme_analysis": {
            "assessment": {
                "assessment_id": "assessment-1", "revision_id": "R01",
                "nominal_arrival_utc": "2026-09-25T12:00:00Z",
                "arrival_window_start_utc": "2026-09-25T06:00:00Z",
                "arrival_window_end_utc": "2026-09-25T18:00:00Z",
            },
            "evidence_agreement": {"modeled_member_count": 3},
        },
    }


def _response(context):
    return io.BytesIO(json.dumps({"status": "ok", "item": context}).encode())


def _runtime(monkeypatch, *, mode="operational", scenario=None):
    monkeypatch.setenv("SYNOPSIS_CME_CONTEXT_URL", "http://cme/context")
    monkeypatch.setattr(cme_context, "runtime_status", lambda: {
        "status": "ok", "data_source": mode, "scenario": scenario, "now_utc": "2026-09-24T12:00:00Z"
    })


def test_synopsis_cme_context_preserves_reviewed_evidence(monkeypatch):
    _runtime(monkeypatch)
    monkeypatch.setattr(cme_context, "urlopen", lambda *args, **kwargs: _response(_context()))
    item = cme_context.reviewed_cme_context()
    assert item["source"]["context_id"] == "cme-sa-assessment-1-r1"
    assert item["assessment"]["nominal_arrival_utc"] == "2026-09-25T12:00:00Z"
    assert item["evidence_ref"]["revision"] == "1"
    assert item["provenance"]["sources"][0]["source_type"] == "wsa_enlil"


@pytest.mark.parametrize("change", ["replay", "partial", "working", "expired"])
def test_synopsis_cme_context_rejects_ineligible_source(monkeypatch, change):
    _runtime(monkeypatch)
    context = _context(mode="replay" if change == "replay" else "operational",
                       lifecycle="working" if change == "working" else "reviewed",
                       partial=change == "partial")
    if change == "expired":
        context["cme_analysis"]["assessment"].update(
            arrival_window_start_utc="2026-09-23T06:00:00Z",
            nominal_arrival_utc="2026-09-23T12:00:00Z",
            arrival_window_end_utc="2026-09-23T18:00:00Z",
        )
    monkeypatch.setattr(cme_context, "urlopen", lambda *args, **kwargs: _response(context))
    with pytest.raises(cme_context.CmeContextInvalidError):
        cme_context.reviewed_cme_context()


def test_synopsis_cme_context_route(monkeypatch):
    _runtime(monkeypatch)
    monkeypatch.setattr(cme_context, "urlopen", lambda *args, **kwargs: _response(_context()))
    result = testing.TestClient(create_app()).simulate_get(
        "/api/v1/space-weather-summary/source-context/cme-sa"
    )
    assert result.status_code == 200
    assert result.json["item"]["schema"] == "swift-synopsis-cme-source-context-v1"
