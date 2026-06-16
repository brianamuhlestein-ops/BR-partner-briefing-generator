import json
from pathlib import Path


PHASE1_BRIEFING_TYPES = [
    {"id": "master", "label": "Master"},
    {"id": "discussion", "label": "Discussion"},
    {"id": "icao", "label": "ICAO"},
    {"id": "staff", "label": "Staff"},
]


def _load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8-sig") as stream:
        return json.load(stream)


def _load_manifest(templates_dir: Path) -> dict:
    return _load_json(templates_dir / "manifest.json")


def _normalize_briefing_type(briefing_type: str) -> str:
    normalized = (briefing_type or "").strip().lower()
    if normalized not in {item["id"] for item in PHASE1_BRIEFING_TYPES}:
        raise ValueError(f"Unsupported briefing type: {briefing_type}")
    return normalized


def _section_map(template: dict) -> dict:
    return {section["id"]: section for section in template.get("sections", [])}


def get_briefing_types() -> list[dict]:
    return PHASE1_BRIEFING_TYPES


def get_template(briefing_type: str, templates_dir: Path) -> dict:
    manifest = _load_manifest(templates_dir)
    normalized = _normalize_briefing_type(briefing_type)
    version = manifest["active_versions"].get(normalized, "v1")
    return get_template_version(normalized, version, templates_dir)


def get_template_version(briefing_type: str, version: str, templates_dir: Path) -> dict:
    normalized = _normalize_briefing_type(briefing_type)
    template = _load_json(templates_dir / f"{normalized}.json")
    return {
        "briefing_type": normalized,
        "version": version,
        "template": template,
    }


def validate_draft_payload(payload: dict, templates_dir: Path) -> dict:
    try:
        normalized = _normalize_briefing_type(payload.get("briefing_type", "master"))
        template_response = get_template(payload.get("briefing_type", normalized), templates_dir)
    except (ValueError, FileNotFoundError) as exc:
        return {"valid": False, "message": str(exc)}

    sections = payload.get("sections", {})
    if not isinstance(sections, dict):
        return {"valid": False, "message": "Draft sections must be an object."}

    allowed_sections = _section_map(template_response["template"])
    for section_id in sections:
        if section_id not in allowed_sections:
            return {
                "valid": False,
                "message": f"Section '{section_id}' is not valid for briefing type '{normalized}'.",
            }

    return {"valid": True, "message": "ok"}


def get_derivation_rules(templates_dir: Path) -> dict:
    return _load_json(templates_dir / "derivation_rules.json")


def derive_from_master(draft: dict, payload: dict, templates_dir: Path) -> dict:
    if draft["briefing_type"] != "master":
        return {
            "draft_id": draft["draft_id"],
            "status": "rejected",
            "message": "Only master drafts can derive downstream products.",
        }

    rules = get_derivation_rules(templates_dir).get("master_to_downstream", {})
    sections = payload.get("sections", draft.get("sections", {}))
    derived = {}
    for target_type, section_ids in rules.items():
        derived[target_type] = {
            section_id: sections.get(section_id)
            for section_id in section_ids
            if section_id in sections
        }

    return {
        "draft_id": draft["draft_id"],
        "status": "ready",
        "derived": derived,
    }


def generate_html_preview(draft: dict, payload: dict, templates_dir: Path) -> dict:
    template_response = get_template(draft["briefing_type"], templates_dir)
    template = template_response["template"]
    sections = payload.get("sections", draft.get("sections", {}))

    parts = [f"<h1>{template['title']}</h1>"]
    for section in template.get("sections", []):
        value = sections.get(section["id"], "")
        if section["kind"] == "probability_table":
            parts.append(f"<h2>{section['label']}</h2><pre>{json.dumps(value, indent=2)}</pre>")
        else:
            parts.append(f"<h2>{section['label']}</h2><p>{value}</p>")

    return {
        "draft_id": draft["draft_id"],
        "format": "html",
        "html": "<html><body>" + "".join(parts) + "</body></html>",
    }


def generate_pdf_output(draft: dict, payload: dict, templates_dir: Path) -> dict:
    return {
        "draft_id": draft["draft_id"],
        "format": "pdf",
        "status": "not_implemented",
        "message": "PDF generation hook is scaffolded but not implemented yet.",
        "request": payload,
    }


def get_active_alert_context() -> list[dict]:
    return [
        {
            "id": "alert-placeholder",
            "summary": "Active SWPC alerts will be normalized here.",
        }
    ]


def get_active_icao_advisory_context() -> list[dict]:
    return [
        {
            "id": "icao-placeholder",
            "summary": "Active ICAO advisories will be normalized here.",
        }
    ]
