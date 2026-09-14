from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


APPLICATION_ROOT = Path(__file__).resolve().parents[2]
WORKSPACE_ROOT = APPLICATION_ROOT.parent


def _path_from_env(name: str, default: Path) -> Path:
    raw = os.getenv(name, "").strip()
    path = Path(raw) if raw else default
    if not path.is_absolute():
        path = APPLICATION_ROOT / path
    return path.resolve()


@dataclass(frozen=True)
class Settings:
    application_root: Path
    data_root: Path
    contracts_root: Path
    observations_schema_path: Path
    forecast_schema_path: Path
    observations_base_url: str
    forecast_base_url: str
    http_timeout_seconds: float
    runtime_mode: str
    replay_scenario: str | None

    @property
    def bundle_root(self) -> Path:
        return self.data_root / "source-bundles"

    @property
    def draft_root(self) -> Path:
        return self.data_root / "drafts"

    @property
    def registry_path(self) -> Path:
        return self.contracts_root / "registries" / "swift-summary-builder-application-registry-v1.json"

    @property
    def registry_schema_path(self) -> Path:
        return self.contracts_root / "schemas" / "swift-summary-builder-application-registry-v1.schema.json"

    @property
    def bundle_schema_path(self) -> Path:
        return self.contracts_root / "schemas" / "swift-summary-source-bundle-v1.schema.json"

    @property
    def draft_schema_path(self) -> Path:
        return self.contracts_root / "schemas" / "swift-space-weather-summary-draft-v1.schema.json"

    @property
    def common_context_schema_path(self) -> Path:
        return self.contracts_root / "schemas" / "swift-application-context-common-v1.schema.json"


def load_settings() -> Settings:
    contracts_root = _path_from_env(
        "SUMMARY_BUILDER_CONTRACTS_ROOT",
        WORKSPACE_ROOT / "SWIFT-Applications",
    )
    runtime_mode = os.getenv("SUMMARY_BUILDER_RUNTIME_MODE", "operational").strip().lower()
    if runtime_mode not in {"operational", "replay", "historical", "fake"}:
        raise ValueError(f"Unsupported SUMMARY_BUILDER_RUNTIME_MODE: {runtime_mode}")
    scenario = os.getenv("SUMMARY_BUILDER_REPLAY_SCENARIO", "").strip() or None
    if runtime_mode == "replay" and not scenario:
        raise ValueError("SUMMARY_BUILDER_REPLAY_SCENARIO is required in replay mode")
    if runtime_mode != "replay":
        scenario = None

    return Settings(
        application_root=APPLICATION_ROOT,
        data_root=_path_from_env("SUMMARY_BUILDER_DATA_ROOT", APPLICATION_ROOT / "runtime-data" / "synopsis"),
        contracts_root=contracts_root,
        observations_schema_path=_path_from_env(
            "SUMMARY_BUILDER_OBSERVATIONS_SCHEMA",
            WORKSPACE_ROOT
            / "AN-geomagnetic-observations-monitor"
            / "docs"
            / "api"
            / "schemas"
            / "swift-geomagnetic-observations-monitor-context-v1.schema.json",
        ),
        forecast_schema_path=_path_from_env(
            "SUMMARY_BUILDER_FORECAST_SCHEMA",
            WORKSPACE_ROOT
            / "FC-geomagnetic-forecast-console"
            / "docs"
            / "api"
            / "schemas"
            / "swift-geomagnetic-forecast-console-context-v1.schema.json",
        ),
        observations_base_url=os.getenv(
            "SUMMARY_BUILDER_OBSERVATIONS_BASE_URL",
            "http://127.0.0.1:8056",
        ).rstrip("/"),
        forecast_base_url=os.getenv(
            "SUMMARY_BUILDER_FORECAST_BASE_URL",
            "http://127.0.0.1:8066",
        ).rstrip("/"),
        http_timeout_seconds=float(os.getenv("SUMMARY_BUILDER_HTTP_TIMEOUT_SECONDS", "10")),
        runtime_mode=runtime_mode,
        replay_scenario=scenario,
    )
