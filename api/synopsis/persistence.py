from __future__ import annotations

import json
import os
import re
import uuid
from pathlib import Path
from typing import Any


BUNDLE_ID_PATTERN = re.compile(r"^ssb-[A-Za-z0-9._:-]+$")
DRAFT_ID_PATTERN = re.compile(r"^swd-[A-Za-z0-9._:-]+$")


class BundleNotFoundError(LookupError):
    pass


class DraftNotFoundError(LookupError):
    pass


class BundleStore:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def write(self, bundle: dict[str, Any]) -> Path:
        bundle_id = str(bundle.get("bundle_id") or "")
        target = self._path(bundle_id)
        if target.exists():
            raise FileExistsError(f"Bundle already exists: {bundle_id}")
        temporary = self.root / f".{bundle_id}.{uuid.uuid4().hex}.tmp"
        try:
            with temporary.open("x", encoding="utf-8", newline="\n") as stream:
                json.dump(bundle, stream, indent=2, ensure_ascii=False)
                stream.write("\n")
                stream.flush()
                os.fsync(stream.fileno())
            os.link(temporary, target)
        finally:
            temporary.unlink(missing_ok=True)
        return target

    def read(self, bundle_id: str) -> dict[str, Any]:
        path = self._path(bundle_id)
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except FileNotFoundError as exc:
            raise BundleNotFoundError(bundle_id) from exc
        if not isinstance(payload, dict):
            raise ValueError(f"Stored bundle is not a JSON object: {bundle_id}")
        return payload

    def list(self, *, limit: int = 25) -> list[dict[str, Any]]:
        records = []
        for path in self.root.glob("ssb-*.json"):
            try:
                bundle = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            if not isinstance(bundle, dict) or not bundle.get("bundle_id"):
                continue
            records.append(
                {
                    "bundle_id": bundle["bundle_id"],
                    "state": bundle.get("state"),
                    "created_at_utc": bundle.get("created_at_utc"),
                    "cutoff_at_utc": bundle.get("cutoff_at_utc"),
                    "runtime": bundle.get("runtime"),
                    "source_count": len(bundle.get("sources") or []),
                    "fact_count": len(bundle.get("fact_ledger") or []),
                    "href": f"/api/v1/space-weather-summary/source-bundles/{bundle['bundle_id']}",
                }
            )
        records.sort(key=lambda item: (item.get("created_at_utc") or "", item["bundle_id"]), reverse=True)
        return records[:limit]

    def _path(self, bundle_id: str) -> Path:
        if not BUNDLE_ID_PATTERN.fullmatch(bundle_id):
            raise BundleNotFoundError(bundle_id)
        return self.root / f"{bundle_id}.json"


class DraftStore:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def write(self, draft: dict[str, Any]) -> Path:
        draft_id = str(draft.get("draft_id") or "")
        target = self._path(draft_id)
        if target.exists():
            raise FileExistsError(f"Draft already exists: {draft_id}")
        temporary = self.root / f".{draft_id}.{uuid.uuid4().hex}.tmp"
        try:
            with temporary.open("x", encoding="utf-8", newline="\n") as stream:
                json.dump(draft, stream, indent=2, ensure_ascii=False)
                stream.write("\n")
                stream.flush()
                os.fsync(stream.fileno())
            os.link(temporary, target)
        finally:
            temporary.unlink(missing_ok=True)
        return target

    def read(self, draft_id: str) -> dict[str, Any]:
        path = self._path(draft_id)
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except FileNotFoundError as exc:
            raise DraftNotFoundError(draft_id) from exc
        if not isinstance(payload, dict):
            raise ValueError(f"Stored draft is not a JSON object: {draft_id}")
        return payload

    def list(self, *, limit: int = 25) -> list[dict[str, Any]]:
        records = []
        for path in self.root.glob("swd-*.json"):
            try:
                draft = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            if not isinstance(draft, dict) or not draft.get("draft_id"):
                continue
            records.append(
                {
                    "draft_id": draft["draft_id"],
                    "state": draft.get("state"),
                    "revision": draft.get("revision"),
                    "created_at_utc": draft.get("created_at_utc"),
                    "bundle_id": (draft.get("source_bundle") or {}).get("bundle_id"),
                    "href": f"/api/v1/space-weather-summary/drafts/{draft['draft_id']}",
                }
            )
        records.sort(key=lambda item: (item.get("created_at_utc") or "", item["draft_id"]), reverse=True)
        return records[:limit]

    def _path(self, draft_id: str) -> Path:
        if not DRAFT_ID_PATTERN.fullmatch(draft_id):
            raise DraftNotFoundError(draft_id)
        return self.root / f"{draft_id}.json"
