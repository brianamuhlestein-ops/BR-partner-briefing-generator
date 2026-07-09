# Partner Briefing API Development Guide

This app follows the SWIFT lightweight Falcon approach in
[`SWIFT_LIGHTWEIGHT_FALCON_APPROACH.md`](./SWIFT_LIGHTWEIGHT_FALCON_APPROACH.md).
Keep backend changes small, explicit, and easy to trace from startup to route to
resource to service logic.

## Backend Shape

```text
api/
  app.py                 WSGI import entrypoint
  run_api.py             local server entrypoint and create_app()
  routes.py              route registration and public route prefixes
  middleware.py          CORS middleware
  errors.py              app-level unexpected-error handling
  http.py                shared request parsing helpers
  resources.py           thin Falcon resource classes
  persistence.py         SQLite storage
  social_graphics.py     social-graphics export services
  science/
    briefing_logic.py    briefing templates, derivation, previews
    templates/           JSON template contracts
```

`create_app()` is the start of the backend. It initializes local storage,
installs CORS middleware, registers routes, and registers error handlers.

## Route Rules

The intended public API prefix is:

```text
/api/v1/partner-briefing
```

The root health route is:

```text
GET /health
```

Register partner briefing API routes only under this prefix. This is a new app,
so avoid duplicate route trees.

## Adding An Endpoint

1. Add or update application logic in the service module that owns the behavior:
   `api/science/briefing_logic.py`, `api/social_graphics.py`, `api/persistence.py`,
   or a new focused service module.
2. Add a thin resource class in `api/resources.py`.
3. Parse JSON bodies with `api.http.read_json()`.
4. Raise Falcon HTTP exceptions for expected client errors.
5. Register the route once under `PUBLIC_PREFIX` in `api/routes.py`.
6. Update this guide or the README route table when the stable route surface
   changes.

## Response And Error Conventions

Use `resp.media` for JSON responses. Collection endpoints return:

```json
{ "status": "ok", "items": [], "total": 0 }
```

Single-item endpoints return:

```json
{ "status": "ok", "item": {} }
```

Workflow endpoints return:

```json
{ "status": "ok", "result": {} }
```

Expected validation and lookup failures should use Falcon exceptions such as
`falcon.HTTPBadRequest` and `falcon.HTTPNotFound`. Unexpected exceptions are
handled by `api/errors.py` and returned as a production-safe JSON envelope.

## CORS And Configuration

CORS lives in `api/middleware.py` and is configured from environment variables:

```text
CORS_ALLOW_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
CORS_ALLOW_METHODS=GET,POST,PATCH,OPTIONS
CORS_ALLOW_HEADERS=Content-Type,Accept,X-Request-ID
```

Local server settings can be changed with:

```text
API_HOST=127.0.0.1
API_PORT=8089
SERVICE_NAME=partner-briefing-api
DATABASE_PATH=email_briefing.db
GENERATED_DIR=generated
```

In Docker, the API binds to `0.0.0.0`, keeps SQLite under
`/srv/partner-briefing/data/email_briefing.db`, and writes generated graphics to
`/srv/partner-briefing/generated`. The UI container serves the production build
with nginx and proxies `/api` to the API service.

## Current Stable Route Surface

```text
GET  /health
GET  /api/v1/partner-briefing/briefing-types
GET  /api/v1/partner-briefing/templates/{briefing_type}
GET  /api/v1/partner-briefing/templates/{briefing_type}/versions/{version}
POST /api/v1/partner-briefing/drafts
GET  /api/v1/partner-briefing/drafts/{draft_id}
PATCH /api/v1/partner-briefing/drafts/{draft_id}
POST /api/v1/partner-briefing/drafts/{draft_id}/derive
POST /api/v1/partner-briefing/drafts/{draft_id}/preview
POST /api/v1/partner-briefing/drafts/{draft_id}/pdf
POST /api/v1/partner-briefing/social-graphics/drafts
GET  /api/v1/partner-briefing/social-graphics/drafts/{draft_id}
PATCH /api/v1/partner-briefing/social-graphics/drafts/{draft_id}
POST /api/v1/partner-briefing/social-graphics/exports
GET  /api/v1/partner-briefing/social-graphics/exports/{export_id}/assets/{variant_id}
GET  /api/v1/partner-briefing/context/alerts/active
GET  /api/v1/partner-briefing/context/advisories/icao/active
```
