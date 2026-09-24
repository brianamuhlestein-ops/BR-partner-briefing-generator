from __future__ import annotations

import hashlib
import uuid
from datetime import datetime, timezone
from typing import Any, Callable

import rfc8785

from api.synopsis.config import Settings
from api.synopsis.contracts import ContractCatalog
from api.synopsis.persistence import BundleStore
from api.synopsis.producer_client import ProducerClient, ProducerRequestError


class BundleInputError(ValueError):
    pass


def parse_utc(value: Any) -> datetime:
    try:
        parsed = datetime.fromisoformat(str(value or "").replace("Z", "+00:00"))
    except ValueError as exc:
        raise BundleInputError(f"Invalid UTC timestamp: {value}") from exc
    if parsed.tzinfo is None:
        raise BundleInputError(f"Timestamp must include a timezone: {value}")
    return parsed.astimezone(timezone.utc)


def format_utc(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(rfc8785.dumps(value)).hexdigest()


class BundleService:
    def __init__(
        self,
        *,
        settings: Settings,
        contracts: ContractCatalog,
        producer_client: ProducerClient,
        store: BundleStore,
        now: Callable[[], datetime] | None = None,
    ) -> None:
        self.settings = settings
        self.contracts = contracts
        self.producer_client = producer_client
        self.store = store
        self.now = now or (lambda: datetime.now(timezone.utc))

    def create_bundle(
        self,
        *,
        cutoff_at_utc: str | None,
        context_ids: dict[str, str] | None,
        actor_id: str,
        actor_type: str,
    ) -> dict[str, Any]:
        cutoff = parse_utc(cutoff_at_utc) if cutoff_at_utc else self.now().astimezone(timezone.utc)
        created_at = self.now().astimezone(timezone.utc)
        context_ids = context_ids or {}
        unexpected = set(context_ids) - set(self.contracts.applications_by_slug)
        if unexpected:
            raise BundleInputError(
                f"context_ids contains applications outside the registry: {', '.join(sorted(unexpected))}"
            )
        if actor_type not in {"forecaster", "service"}:
            raise BundleInputError("actor_type must be 'forecaster' or 'service'")
        actor_id = actor_id.strip()
        if not actor_id:
            raise BundleInputError("actor_id is required")

        source_records = []
        collection_errors = []
        selected_contexts: dict[str, dict[str, Any]] = {}
        for application in self.contracts.applications:
            slug = application["application_slug"]
            context, status, errors = self._select_context(
                application=application,
                cutoff=cutoff,
                explicit_context_id=context_ids.get(slug),
            )
            source_records.append(
                self._source_record(
                    application=application,
                    context=context,
                    status=status,
                    errors=errors,
                    retrieved_at=created_at,
                )
            )
            if context is not None and status == "selected":
                selected_contexts[slug] = context
            for error in errors:
                collection_errors.append(
                    {
                        "application_slug": slug,
                        "code": error["code"],
                        "message": error["message"],
                        "retryable": bool(error.get("retryable")),
                    }
                )

        checks = self._consistency_checks(source_records)
        state = "ready" if all(item["status"] != "fail" for item in checks) else "needs_attention"
        fact_ledger = (
            self._fact_ledger(selected_contexts)
            if state == "ready" and not collection_errors
            else []
        )
        digest_content = {"fact_ledger": fact_ledger, "sources": source_records}
        bundle = {
            "schema": "swift-summary-source-bundle-v1",
            "bundle_id": self._bundle_id(cutoff),
            "registry_id": self.contracts.registry["registry_id"],
            "registry_version": self.contracts.registry["version"],
            "template_id": self.contracts.registry["summary_template"]["template_id"],
            "state": state,
            "created_at_utc": format_utc(created_at),
            "cutoff_at_utc": format_utc(cutoff),
            "created_by": {"actor_id": actor_id, "actor_type": actor_type},
            "runtime": {
                "mode": self.settings.runtime_mode,
                "effective_at_utc": format_utc(cutoff),
                "scenario": self.settings.replay_scenario,
                "source_clock": "replay_clock" if self.settings.runtime_mode == "replay" else "server_utc",
            },
            "sources": source_records,
            "collection_errors": collection_errors,
            "consistency_checks": checks,
            "fact_ledger": fact_ledger,
            "integrity": {
                "algorithm": "sha256",
                "canonicalization": "rfc8785",
                "digest_scope": "sources_and_fact_ledger",
                "sha256": canonical_sha256(digest_content),
            },
        }
        self.contracts.validate_bundle(bundle)
        self.store.write(bundle)
        return bundle

    def _select_context(
        self,
        *,
        application: dict[str, Any],
        cutoff: datetime,
        explicit_context_id: str | None,
    ) -> tuple[dict[str, Any] | None, str, list[dict[str, Any]]]:
        slug = application["application_slug"]
        if explicit_context_id:
            try:
                context = self.producer_client.get_export(slug, explicit_context_id)
            except ProducerRequestError as exc:
                return None, "missing", [self._request_error(exc)]
            errors = self._eligibility_errors(application, context, cutoff)
            return (context, "selected", []) if not errors else (None, "invalid", errors)

        try:
            candidates = self.producer_client.list_exports(slug)
        except ProducerRequestError as exc:
            return None, "missing", [self._request_error(exc)]

        candidates.sort(
            key=lambda item: str(item.get("generated_at_utc") or ""),
            reverse=True,
        )
        validation_errors: list[dict[str, Any]] = []
        for candidate in candidates:
            context_id = str(candidate.get("context_id") or "").strip()
            if not context_id:
                continue
            try:
                generated_at = parse_utc(candidate.get("generated_at_utc"))
            except BundleInputError:
                continue
            if generated_at > cutoff:
                continue
            try:
                context = self.producer_client.get_export(slug, context_id)
            except ProducerRequestError as exc:
                validation_errors.append(self._request_error(exc))
                continue
            errors = self._eligibility_errors(application, context, cutoff)
            if not errors:
                return context, "selected", []
            validation_errors.extend(errors)

        if validation_errors:
            return None, "invalid", validation_errors
        return None, "missing", [
            {
                "code": "eligible_context_not_found",
                "message": f"No eligible {slug} context exists at or before the cutoff.",
                "retryable": True,
            }
        ]

    def _eligibility_errors(
        self,
        application: dict[str, Any],
        context: dict[str, Any],
        cutoff: datetime,
    ) -> list[dict[str, Any]]:
        slug = application["application_slug"]
        errors = [
            {"code": "context_schema_invalid", "message": message, "retryable": False}
            for message in self.contracts.context_errors(slug, context)
        ]
        if errors:
            return errors

        lifecycle = context["lifecycle"]
        accepted = application["selection_policy"]["accepted_lifecycle_states"]
        if lifecycle["state"] not in accepted:
            errors.append(
                {
                    "code": "lifecycle_not_eligible",
                    "message": f"Context lifecycle {lifecycle['state']} is not eligible under this source's selection policy.",
                    "retryable": False,
                }
            )
        if lifecycle.get("superseded_by_context_id") or lifecycle["state"] == "superseded":
            errors.append(
                {
                    "code": "context_superseded",
                    "message": "Context has been superseded.",
                    "retryable": False,
                }
            )
        generated_at = parse_utc(context["generated_at_utc"])
        if generated_at > cutoff:
            errors.append(
                {
                    "code": "context_after_cutoff",
                    "message": "Context was generated after the requested cutoff.",
                    "retryable": False,
                }
            )
        runtime = context["runtime"]
        if runtime["mode"] != self.settings.runtime_mode:
            errors.append(
                {
                    "code": "runtime_mode_mismatch",
                    "message": (
                        f"Context runtime {runtime['mode']} does not match "
                        f"Summary Builder runtime {self.settings.runtime_mode}."
                    ),
                    "retryable": False,
                }
            )
        if runtime.get("scenario") != self.settings.replay_scenario:
            errors.append(
                {
                    "code": "runtime_scenario_mismatch",
                    "message": "Context replay scenario does not match Summary Builder.",
                    "retryable": False,
                }
            )
        quality = context["quality"]
        if (
            quality["status"] != "usable"
            or not quality["available"]
            or quality["stale"]
            or quality["partial"]
        ):
            errors.append(
                {
                    "code": "context_quality_not_eligible",
                    "message": "Context quality must be usable, available, non-stale, and complete.",
                    "retryable": False,
                }
            )
        window = context["valid_window"]
        start = parse_utc(window["start_utc"])
        end = parse_utc(window["end_utc"])
        requirement = application["selection_policy"]["valid_window_requirement"]
        if requirement == "recent_observations_before_cutoff":
            # Observations end when captured; never claim coverage into the future.
            max_age = application["selection_policy"]["maximum_age_seconds"]
            valid_window = start <= end <= cutoff and 0 <= (cutoff - end).total_seconds() <= max_age
        elif requirement == "contains_cutoff":
            valid_window = start <= cutoff <= end
        else:
            valid_window = end > cutoff
        if not valid_window:
            errors.append(
                {
                    "code": "valid_window_not_eligible",
                    "message": f"Context does not satisfy {requirement}.",
                    "retryable": False,
                }
            )
        return errors

    def _source_record(
        self,
        *,
        application: dict[str, Any],
        context: dict[str, Any] | None,
        status: str,
        errors: list[dict[str, Any]],
        retrieved_at: datetime,
    ) -> dict[str, Any]:
        base = {
            "application_slug": application["application_slug"],
            "role": application["role"],
            "required": True,
            "status": status,
            "context_schema": application["context_schema"],
        }
        if context is None or status != "selected":
            return {
                **base,
                "context_id": None,
                "source_sha256": None,
                "href": None,
                "retrieved_at_utc": None,
                "generated_at_utc": None,
                "valid_window": None,
                "runtime": None,
                "lifecycle_state": None,
                "errors": [
                    {"code": error["code"], "message": error["message"]}
                    for error in errors
                ],
            }
        context_id = context["context_id"]
        window = context["valid_window"]
        return {
            **base,
            "context_id": context_id,
            "source_sha256": canonical_sha256(context),
            "href": application["routes"]["export_detail"].replace(
                "{context_id}", context_id
            ),
            "retrieved_at_utc": format_utc(retrieved_at),
            "generated_at_utc": context["generated_at_utc"],
            "valid_window": {
                "start_utc": window["start_utc"],
                "end_utc": window["end_utc"],
            },
            "runtime": {
                key: context["runtime"].get(key)
                for key in ("mode", "effective_at_utc", "scenario", "source_clock")
            },
            "lifecycle_state": context["lifecycle"]["state"],
            "errors": [],
        }

    def _consistency_checks(self, sources: list[dict[str, Any]]) -> list[dict[str, Any]]:
        slugs = [source["application_slug"] for source in sources]
        selected = [source for source in sources if source["status"] == "selected"]
        all_selected = len(selected) == len(sources)

        def check(check_id: str, passed: bool, success: str, failure: str) -> dict[str, Any]:
            return {
                "check_id": check_id,
                "status": "pass" if passed else "fail",
                "message": success if passed else failure,
                "source_applications": slugs,
            }

        runtime_aligned = all_selected and all(
            source["runtime"]["mode"] == self.settings.runtime_mode for source in selected
        )
        scenario_aligned = all_selected and all(
            source["runtime"].get("scenario") == self.settings.replay_scenario
            for source in selected
        )
        return [
            check("required_sources", all_selected, "Both required sources are selected.", "A required source is unavailable."),
            check("schema_allowlist", all_selected, "Both contexts match the schema allowlist.", "Schema eligibility is incomplete or invalid."),
            check("runtime_mode_alignment", runtime_aligned, "Runtime modes align.", "Runtime modes do not align."),
            check("scenario_alignment", scenario_aligned, "Replay scenarios align.", "Replay scenarios do not align."),
            check("cutoff_compliance", all_selected, "Both contexts comply with the cutoff.", "Cutoff compliance is incomplete."),
            check("valid_window_coverage", all_selected, "Both role-specific validity rules pass.", "Validity coverage is incomplete."),
            check("lifecycle_eligibility", all_selected, "Both lifecycle states are eligible.", "Lifecycle eligibility is incomplete."),
            check("quality_eligibility", all_selected, "Both contexts have eligible quality.", "Quality eligibility is incomplete."),
            check("supersession_status", all_selected, "Neither context is superseded.", "Supersession status is incomplete."),
        ]

    def _fact_ledger(self, contexts: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
        fields = (
            "kind",
            "label",
            "value",
            "unit",
            "status",
            "valid_at_utc",
            "valid_window",
            "confidence",
            "source_type",
            "evidence_links",
            "narrative_priority",
            "experimental",
            "not_for_alerting",
        )
        ledger = []
        for application in self.contracts.applications:
            slug = application["application_slug"]
            context = contexts[slug]
            for fact in context.get("narrative_facts") or []:
                if (
                    not isinstance(fact, dict)
                    or fact.get("experimental")
                    or fact.get("not_for_alerting")
                    or fact.get("narrative_priority") == "excluded"
                ):
                    continue
                producer_fact_id = str(fact.get("fact_id") or "").strip()
                if not producer_fact_id:
                    continue
                ledger.append(
                    {
                        "ledger_fact_id": f"{slug}:{producer_fact_id}",
                        "source_application": slug,
                        "source_context_id": context["context_id"],
                        "producer_fact_id": producer_fact_id,
                        **{field: fact.get(field) for field in fields},
                    }
                )
        return ledger

    @staticmethod
    def _request_error(error: ProducerRequestError) -> dict[str, Any]:
        return {"code": error.code, "message": error.message, "retryable": error.retryable}

    @staticmethod
    def _bundle_id(cutoff: datetime) -> str:
        stamp = cutoff.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        return f"ssb-{stamp}-{uuid.uuid4().hex[:12]}"
