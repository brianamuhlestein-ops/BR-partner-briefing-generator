from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource

from api.synopsis.config import Settings


class ContractConfigurationError(RuntimeError):
    pass


def _load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractConfigurationError(f"Unable to load contract artifact {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ContractConfigurationError(f"Contract artifact must contain a JSON object: {path}")
    return payload


class ContractCatalog:
    def __init__(self, settings: Settings) -> None:
        self.registry = _load_json(settings.registry_path)
        registry_schema = _load_json(settings.registry_schema_path)
        bundle_schema = _load_json(settings.bundle_schema_path)
        draft_schema = _load_json(settings.draft_schema_path)
        common_schema = _load_json(settings.common_context_schema_path)
        context_schemas = {
            "geomagnetic-observations-monitor": _load_json(settings.observations_schema_path),
            "geomagnetic-forecast-console": _load_json(settings.forecast_schema_path),
        }

        for schema in [
            registry_schema,
            bundle_schema,
            draft_schema,
            common_schema,
            *context_schemas.values(),
        ]:
            Draft202012Validator.check_schema(schema)

        common_registry = Registry().with_resource(
            common_schema["$id"],
            Resource.from_contents(common_schema),
        )
        self.registry_validator = Draft202012Validator(
            registry_schema,
            format_checker=FormatChecker(),
        )
        self.registry_validator.validate(self.registry)
        self.bundle_validator = Draft202012Validator(
            bundle_schema,
            format_checker=FormatChecker(),
        )
        self.draft_validator = Draft202012Validator(
            draft_schema,
            format_checker=FormatChecker(),
        )
        self.context_validators = {
            slug: Draft202012Validator(
                schema,
                registry=common_registry,
                format_checker=FormatChecker(),
            )
            for slug, schema in context_schemas.items()
        }
        self.applications = list(self.registry["applications"])
        self.applications_by_slug = {
            item["application_slug"]: item for item in self.applications
        }

    def context_errors(self, application_slug: str, context: dict[str, Any]) -> list[str]:
        validator = self.context_validators[application_slug]
        return [
            f"{'.'.join(str(part) for part in error.absolute_path) or '$'}: {error.message}"
            for error in sorted(validator.iter_errors(context), key=lambda item: list(item.absolute_path))
        ]

    def validate_bundle(self, bundle: dict[str, Any]) -> None:
        self.bundle_validator.validate(bundle)

    def validate_draft(self, draft: dict[str, Any]) -> None:
        self.draft_validator.validate(draft)
