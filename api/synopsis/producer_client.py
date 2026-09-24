from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Protocol
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from api.synopsis.config import Settings


class ProducerClient(Protocol):
    def list_exports(self, application_slug: str) -> list[dict[str, Any]]: ...

    def get_export(self, application_slug: str, context_id: str) -> dict[str, Any]: ...


@dataclass
class ProducerRequestError(RuntimeError):
    code: str
    message: str
    retryable: bool

    def __str__(self) -> str:
        return self.message


class HttpProducerClient:
    def __init__(self, settings: Settings) -> None:
        self.timeout_seconds = settings.http_timeout_seconds
        self.base_urls = {
            "geomagnetic-observations-monitor": settings.observations_base_url,
            "geomagnetic-forecast-console": settings.forecast_base_url,
        }
        self.api_prefixes = {
            "geomagnetic-observations-monitor": "/api/v1/geomagnetic-monitor",
            "geomagnetic-forecast-console": "/api/v1/geomagnetic",
        }

    def list_exports(self, application_slug: str) -> list[dict[str, Any]]:
        payload = self._get(
            f"{self._base_url(application_slug)}{self._api_prefix(application_slug)}/context/exports?limit=250"
        )
        items = payload.get("items")
        if not isinstance(items, list):
            raise ProducerRequestError(
                "invalid_collection_response",
                f"{application_slug} export collection did not return an items array.",
                False,
            )
        return [item for item in items if isinstance(item, dict)]

    def get_export(self, application_slug: str, context_id: str) -> dict[str, Any]:
        encoded_id = quote(context_id, safe="")
        payload = self._get(
            f"{self._base_url(application_slug)}{self._api_prefix(application_slug)}/context/exports/{encoded_id}"
        )
        item = payload.get("item")
        if not isinstance(item, dict):
            raise ProducerRequestError(
                "invalid_context_response",
                f"{application_slug} context detail did not return an item object.",
                False,
            )
        return item

    def _base_url(self, application_slug: str) -> str:
        try:
            return self.base_urls[application_slug]
        except KeyError as exc:
            raise ProducerRequestError(
                "application_not_registered",
                f"No producer endpoint is configured for {application_slug}.",
                False,
            ) from exc

    def _api_prefix(self, application_slug: str) -> str:
        try:
            return self.api_prefixes[application_slug]
        except KeyError as exc:
            raise ProducerRequestError(
                "application_not_registered",
                f"No producer API prefix is configured for {application_slug}.",
                False,
            ) from exc

    def _get(self, url: str) -> dict[str, Any]:
        request = Request(url, headers={"Accept": "application/json"}, method="GET")
        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                body = response.read().decode("utf-8")
        except HTTPError as exc:
            raise ProducerRequestError(
                "producer_http_error",
                f"Producer returned HTTP {exc.code} for {url}.",
                500 <= exc.code < 600,
            ) from exc
        except (URLError, TimeoutError, OSError) as exc:
            raise ProducerRequestError(
                "producer_unavailable",
                f"Unable to reach producer at {url}: {exc}",
                True,
            ) from exc
        try:
            payload = json.loads(body)
        except json.JSONDecodeError as exc:
            raise ProducerRequestError(
                "invalid_json_response",
                f"Producer returned invalid JSON for {url}.",
                False,
            ) from exc
        if not isinstance(payload, dict):
            raise ProducerRequestError(
                "invalid_response",
                f"Producer returned a non-object response for {url}.",
                False,
            )
        return payload
