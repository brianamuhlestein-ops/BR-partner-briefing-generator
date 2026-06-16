import base64
import json
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from uuid import uuid4

from PIL import Image, ImageOps


VARIANT_SPECS = [
    ("landscape", "Landscape 1920x1080", (1920, 1080)),
    ("square", "Square 1080x1080", (1080, 1080)),
    ("portrait", "Portrait 1080x1350", (1080, 1350)),
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def validate_social_graphics_scene(scene: dict) -> dict:
    if not isinstance(scene, dict):
        return {"valid": False, "message": "Scene payload must be an object."}

    required_keys = {"version", "templateId", "width", "height", "elements"}
    missing = required_keys.difference(scene.keys())
    if missing:
        return {
            "valid": False,
            "message": f"Scene payload is missing required keys: {', '.join(sorted(missing))}.",
        }

    if not isinstance(scene.get("elements"), list):
        return {"valid": False, "message": "Scene elements must be a list."}

    return {"valid": True, "message": "ok"}


def decode_base_png(base_png: str) -> Image.Image:
    if not isinstance(base_png, str) or "," not in base_png:
        raise ValueError("Base PNG must be a data URL string.")

    _, encoded = base_png.split(",", 1)
    image_bytes = base64.b64decode(encoded)
    return Image.open(BytesIO(image_bytes)).convert("RGBA")


def build_export_artifacts(
    payload: dict,
    generated_root: Path,
) -> dict:
    export_id = str(uuid4())
    created_at = utc_now()
    export_dir = generated_root / "social_graphics" / export_id
    export_dir.mkdir(parents=True, exist_ok=True)

    scene = payload["scene"]
    scene_path = export_dir / "scene.json"
    scene_path.write_text(json.dumps(scene, indent=2), encoding="utf-8")

    base_image = decode_base_png(payload["base_png"])
    base_image_path = export_dir / "base_1920x1080.png"
    base_image.save(base_image_path, format="PNG")

    variants = []
    for variant_id, label, size in VARIANT_SPECS:
        variant_image = ImageOps.fit(
            base_image,
            size,
            method=Image.Resampling.LANCZOS,
            centering=(0.5, 0.5),
        )
        variant_path = export_dir / f"{variant_id}_{size[0]}x{size[1]}.png"
        variant_image.save(variant_path, format="PNG")
        variants.append(
            {
                "variant_id": variant_id,
                "label": label,
                "width": size[0],
                "height": size[1],
                "path": str(variant_path),
                "url": (
                    "/api/v1/partner-briefing/social-graphics/"
                    f"exports/{export_id}/assets/{variant_id}"
                ),
            }
        )

    return {
        "export_id": export_id,
        "draft_id": payload.get("draft_id"),
        "template_id": payload["template_id"],
        "scene": scene,
        "base_image_path": str(base_image_path),
        "variants": variants,
        "created_at": created_at,
    }
