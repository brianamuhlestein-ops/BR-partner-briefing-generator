# Partner Briefing API Development Guide

This app follows the SWIFT lightweight Falcon approach in
[suite API and runtime contract](https://github.com/brianamuhlestein-ops/SWIFT-Applications/blob/main/SWIFT_API_AND_RUNTIME_CONTRACTS.md).
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
  persistence.py         saved briefing-document storage
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

1. Add or update application logic in the focused service module that owns the
   behavior. Saved briefing documents belong in `api/persistence.py`; Synopsis
   logic belongs under `api/synopsis/`.
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
CORS_ALLOW_METHODS=GET,POST,PUT,PATCH,OPTIONS
CORS_ALLOW_HEADERS=Content-Type,Accept,X-Request-ID,If-Match
```

Local server settings can be changed with:

```text
API_HOST=127.0.0.1
API_PORT=8089
SERVICE_NAME=partner-briefing-api
DATABASE_PATH=email_briefing.db
```

In Docker, the API binds to `0.0.0.0` and keeps SQLite under
`/srv/partner-briefing/data/email_briefing.db`. The UI container serves the production build
with nginx and proxies `/api` to the API service.

## Current Stable Route Surface

```text
GET  /health
GET  /api/v1/partner-briefing/now
GET  /api/v1/partner-briefing/email-briefings/{briefing_kind}
PUT  /api/v1/partner-briefing/email-briefings/{briefing_kind}
```

## Shared Authoring Contract

The mutable `email_briefing_documents` records carry an integer `record_version`. Return
that version in the response item and as a quoted `ETag`. A mutation must send
the version it loaded as `If-Match`; use version `0` only when creating a saved
email document that does not exist yet. Missing preconditions return `428` and
stale writes return `409 revision_conflict` with the current version in both
the response details and `ETag`.

The compare-and-swap update belongs in `api/persistence.py`, not in a route
read-then-write sequence. SQLite WAL plus the atomic version predicate is the
supported single-host, single-API-deployment boundary. Do not deploy multiple
API replicas against this SQLite file or place it on shared storage; move the
authoritative records to PostgreSQL first.
