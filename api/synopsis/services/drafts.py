from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Any, Callable

from api.synopsis.contracts import ContractCatalog
from api.synopsis.persistence import BundleStore, DraftStore
from api.synopsis.services.bundles import format_utc


class DraftInputError(ValueError):
    pass


class DraftService:
    def __init__(
        self,
        *,
        contracts: ContractCatalog,
        bundle_store: BundleStore,
        draft_store: DraftStore,
        now: Callable[[], datetime] | None = None,
    ) -> None:
        self.contracts = contracts
        self.bundle_store = bundle_store
        self.draft_store = draft_store
        self.now = now or (lambda: datetime.now(timezone.utc))

    def create_draft(
        self,
        *,
        bundle_id: str,
        actor_id: str,
        actor_type: str,
    ) -> dict[str, Any]:
        bundle = self.bundle_store.read(bundle_id)
        if bundle.get("state") != "ready":
            raise DraftInputError("A deterministic draft requires a ready source bundle")
        if actor_type not in {"forecaster", "service"}:
            raise DraftInputError("actor_type must be 'forecaster' or 'service'")
        actor_id = actor_id.strip()
        if not actor_id:
            raise DraftInputError("actor_id is required")

        sections = self._sections(bundle.get("fact_ledger") or [])
        generated_at = self.now().astimezone(timezone.utc)
        draft = {
            "schema": "swift-space-weather-summary-draft-v1",
            "draft_id": self._draft_id(generated_at),
            "revision": 1,
            "state": "drafted",
            "template_id": "geomagnetic-summary-v1",
            "source_bundle": {
                "bundle_id": bundle["bundle_id"],
                "integrity_sha256": bundle["integrity"]["sha256"],
                "href": f"/api/v1/space-weather-summary/source-bundles/{bundle['bundle_id']}",
            },
            "created_at_utc": format_utc(generated_at),
            "created_by": {"actor_id": actor_id, "actor_type": actor_type},
            "title": "Geomagnetic Conditions and Forecast Summary",
            "sections": sections,
            "generation": {
                "method": "deterministic_template",
                "template_version": "geomagnetic-deterministic-v1",
                "prompt_template_id": None,
                "model": None,
                "settings": {},
                "generated_at_utc": format_utc(generated_at),
            },
            "validation": {
                "status": "pass",
                "checked_at_utc": format_utc(generated_at),
                "findings": [],
            },
        }
        self._validate_citations(draft, bundle)
        self.contracts.validate_draft(draft)
        self.draft_store.write(draft)
        return draft

    def _sections(self, facts: list[dict[str, Any]]) -> list[dict[str, Any]]:
        grouped = {
            "current_conditions": [],
            "forecast": [],
            "limitations": [],
        }
        sentence_number = 1
        for fact in facts:
            section_id = self._section_id(fact)
            grouped[section_id].append(
                {
                    "sentence_id": f"sentence-{sentence_number:03d}",
                    "text": self._sentence_text(fact),
                    "support_fact_ids": [fact["ledger_fact_id"]],
                    "generation_method": "deterministic_template",
                    "validation_status": "pass",
                    "validation_findings": [],
                }
            )
            sentence_number += 1

        if not grouped["current_conditions"] or not grouped["forecast"]:
            raise DraftInputError(
                "A draft requires at least one eligible observation fact and one forecast fact"
            )
        headings = {
            "current_conditions": "Current Conditions",
            "forecast": "Forecast",
            "limitations": "Limitations",
        }
        return [
            {
                "section_id": section_id,
                "heading": headings[section_id],
                "sentences": grouped[section_id],
            }
            for section_id in ("current_conditions", "forecast", "limitations")
            if grouped[section_id]
        ]

    @staticmethod
    def _section_id(fact: dict[str, Any]) -> str:
        if fact.get("status") == "unavailable" or fact.get("kind") == "source_limitation":
            return "limitations"
        if fact.get("source_application") == "geomagnetic-observations-monitor":
            return "current_conditions"
        return "forecast"

    @staticmethod
    def _sentence_text(fact: dict[str, Any]) -> str:
        label = str(fact.get("label") or "Geomagnetic condition").strip()
        value = _value_text(fact.get("value"))
        unit = str(fact.get("unit") or "").strip()
        valid_at = fact.get("valid_at_utc")
        confidence = fact.get("confidence")
        kind = fact.get("kind")

        if fact.get("status") == "unavailable":
            return f"{label} is unavailable."
        if kind == "current_condition":
            suffix = "" if unit.lower() == "kp" and "kp" in label.lower() else f" {unit}" if unit else ""
            return f"{label} is {value}{suffix}."
        if kind == "threshold_crossing":
            timing = f" as of {valid_at}" if valid_at else ""
            return f"{label}: {value}{timing}."
        if kind == "forecast_peak":
            unit_text = f" {unit}" if unit else ""
            timing = f" around {valid_at}" if valid_at else ""
            confidence_text = f", with {confidence} confidence" if confidence is not None else ""
            return f"{label} is {value}{unit_text}{timing}{confidence_text}."
        if kind == "principal_driver":
            confidence_text = f", with {confidence} confidence" if confidence is not None else ""
            return f"The principal forecast driver is {value}{confidence_text}."
        suffix = f" {unit}" if unit else ""
        return f"{label}: {value}{suffix}."

    @staticmethod
    def _validate_citations(draft: dict[str, Any], bundle: dict[str, Any]) -> None:
        available = {item["ledger_fact_id"] for item in bundle["fact_ledger"]}
        cited = {
            fact_id
            for section in draft["sections"]
            for sentence in section["sentences"]
            for fact_id in sentence["support_fact_ids"]
        }
        if not cited or not cited <= available:
            raise DraftInputError("Draft citations must resolve to the selected source bundle")

    @staticmethod
    def _draft_id(generated_at: datetime) -> str:
        stamp = generated_at.strftime("%Y%m%dT%H%M%SZ")
        return f"swd-{stamp}-{uuid.uuid4().hex[:12]}"


def _value_text(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    if value is None:
        return "unavailable"
    return str(value)
