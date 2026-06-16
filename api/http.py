import json

import falcon


def read_json(req: falcon.Request, *, allow_empty: bool = True) -> dict:
    body = req.bounded_stream.read()
    if not body:
        if allow_empty:
            return {}
        raise falcon.HTTPBadRequest(
            title="Bad Request",
            description="Request body is required.",
        )

    try:
        payload = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise falcon.HTTPBadRequest(
            title="Bad Request",
            description="Request body must be valid JSON.",
        ) from exc

    if not isinstance(payload, dict):
        raise falcon.HTTPBadRequest(
            title="Bad Request",
            description="Request body must be a JSON object.",
        )

    return payload


def collection_response(items: list[dict]) -> dict:
    return {
        "status": "ok",
        "items": items,
        "total": len(items),
    }


def item_response(item: dict) -> dict:
    return {
        "status": "ok",
        "item": item,
    }


def result_response(result: dict) -> dict:
    return {
        "status": "ok",
        "result": result,
    }
