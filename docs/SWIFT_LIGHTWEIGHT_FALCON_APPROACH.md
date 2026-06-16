# SWIFT Lightweight Falcon Approach

This document defines the lightweight Falcon approach for SWIFT applications. It is intended as a shared guiding standard for developers working across the application suite.

The goal is not to force every application into a heavy framework or a large rewrite. The goal is to make each Falcon backend easier to understand, operate, document, and connect to the rest of the SWIFT ecosystem.

Implementation tracking for the completed Sunspot Classification Studio, Geomagnetic Observations Monitor, and Synoptic Map Workbench refactors is maintained in [SWIFT_FALCON_REFACTOR_PROGRESS.md](./SWIFT_FALCON_REFACTOR_PROGRESS.md).

## Guiding Principle

Every SWIFT Falcon app should be small enough to work on independently, but familiar enough that a developer can open any app and quickly understand:

- where the application starts
- where routes are registered
- what route namespace the app owns
- how JSON requests and responses are handled
- how errors are returned
- where operational outputs are produced
- which routes are stable contracts versus internal support routes

This approach favors consistency, clarity, and controlled migration over broad rewrites.

## What "Lightweight" Means

Lightweight does not mean informal. It means each app adopts a simple, repeatable shape without requiring a large shared platform layer.

The approach should provide:

- one obvious Falcon app factory
- one route registration location
- one CORS strategy
- one health endpoint
- one JSON response style
- one error response style
- clear route prefixes
- documented externally consumed routes

The approach should avoid:

- rewriting mature apps all at once
- hiding simple logic behind unnecessary abstractions
- forcing every endpoint into OpenAPI before the contract is stable
- creating permanent duplicate route systems
- changing active frontend routes without moving the caller in the same pass or documenting a short transition
- introducing ecosystem-wide dependencies before individual apps are mature

## Standard App Shape

Each Falcon app should expose a clear startup pattern:

```python
def create_app() -> falcon.App:
    app = falcon.App(middleware=[CorsMiddleware()])
    register_routes(app)
    register_error_handlers(app)
    return app


app = application = create_app()
```

For small apps, this can live in `api/app.py`.

For larger apps, prefer:

```text
api/
  app.py or run_api.py
  routes.py
  middleware.py
  errors.py
  http.py
  resources/
  services/
```

The important part is not the exact filenames. The important part is that startup, routes, HTTP helpers, resources, and business logic are not tangled together.

## Route Prefixes

Each app should have:

```text
GET /health
```

Application APIs should use:

```text
/api/v1/{domain}/...
```

Examples:

```text
/api/v1/active-regions/...
/api/v1/coronagraph/...
/api/v1/geomagnetic/...
/api/v1/synoptic/...
/api/v1/products/...
/api/v1/handoffs/...
/api/v1/verification/...
```

Prefer one public route for each capability. If an older route is already used by the UI, either keep that route as canonical for now or migrate the UI to the new route in the same refactor. Do not create parallel canonical and legacy route trees. A temporary bridge is an exception for a named blocker, not a default refactor step, and it needs an owner plus a removal date before it is merged.

## Resource Naming

Routes should generally use nouns:

```text
/products
/events
/drafts
/handoffs
/snapshots
/runs
```

Action routes are acceptable when the endpoint performs a workflow step rather than representing a simple resource:

```text
/drafts/{draft_id}/derive
/drafts/{draft_id}/preview
/runs/{run_id}/rebuild
/alerts/{alert_id}/issue
```

Avoid adding new mixed naming styles such as underscores in one app and hyphens in another. Prefer hyphenated URL segments for new public routes.

## JSON Responses

Use `resp.media` for JSON.

Preferred collection response:

```json
{
  "status": "ok",
  "items": [],
  "total": 0
}
```

Preferred single-item response:

```json
{
  "status": "ok",
  "item": {}
}
```

Preferred command/workflow response:

```json
{
  "status": "ok",
  "result": {}
}
```

Existing endpoints can keep their current response shape while they remain canonical. Do not add a second response shape for the same capability just because a new route prefix was introduced.

## Error Responses

Expected client errors should use Falcon HTTP exceptions:

```python
raise falcon.HTTPBadRequest(
    title="Bad Request",
    description="Missing required query parameter: date",
)
```

Unexpected server errors should use a shared app-level handler:

```json
{
  "status": "error",
  "error": {
    "code": "internal_error",
    "message": "An unexpected server error occurred."
  }
}
```

Tracebacks should be logged server-side, not returned to the browser in production responses.

## Request Parsing

Apps should use a small helper for JSON body parsing and validation.

The helper should:

- tolerate empty request bodies when the endpoint allows them
- reject non-object JSON bodies
- return clear `400 Bad Request` messages
- keep parsing behavior consistent across resources

This keeps each resource focused on workflow logic instead of repeated request boilerplate.

## CORS

Each app should use one explicit CORS middleware.

The middleware should:

- support local Vite development origins
- support configured origins through environment variables
- handle `OPTIONS` preflight requests
- set `Vary: Origin`
- avoid hard-coded production origins when possible

Suggested environment names:

```text
CORS_ALLOW_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
CORS_ALLOW_METHODS=GET,POST,PUT,PATCH,DELETE,OPTIONS
CORS_ALLOW_HEADERS=Content-Type,Accept,X-Request-ID
```

## Health Checks

Every app should provide a fast root health check:

```json
{
  "status": "ok",
  "service": "example-api",
  "timeUtc": "2026-06-15T00:00:00Z"
}
```

This endpoint should not depend on slow external services.

If deeper dependency checks are useful, expose them under a domain status route:

```text
/api/v1/{domain}/status
```

## Resources And Services

Resource classes should be thin adapters between HTTP and application logic.

They should handle:

- reading query parameters
- reading JSON bodies
- validating required request fields
- calling service functions
- assigning response status and media

They should not become the long-term home for:

- science calculations
- file-generation logic
- database persistence rules
- handoff schema construction
- data-source fetch and caching behavior

Those belong in service, science, database, or contract modules.

## Preview Versus Persist

SWIFT apps often generate products, exports, handoff files, and operational artifacts. Endpoints should clearly separate preview behavior from persistence behavior.

Recommended convention:

- `preview` returns the product content without durable writes
- `issue`, `export`, `finalize`, or `publish` may write durable outputs
- forecaster-facing text products should be returned directly when review is part of the workflow
- internal JSON should only be shown in the UI when the workflow requires it

## Documentation Expectations

Each app README should identify:

- purpose
- maturity level
- backend entrypoint
- frontend entrypoint
- route families
- data sources
- generated outputs
- persistence behavior
- known operational constraints

For mature apps, add either:

- an API contract table, or
- an OpenAPI file once the route contract is stable

Do not create OpenAPI first if the route behavior is still shifting.

## Migration Approach

Adopt this convention gradually.

1. Stabilize the current app behavior.
2. Centralize app startup and route registration.
3. Choose the public route names for the app.
4. Migrate frontend calls in the same pass when practical.
5. Normalize error handling.
6. Normalize new JSON responses.
7. Do not add parallel compatibility routes unless there is a named external blocker.
8. Document the resulting single public contract and remove any temporary bridge from the operational surface before marking the refactor complete.

The preferred migration style is small, observable improvement rather than sweeping backend renovation.

## Completed First Refactor Targets

The first completed targets for this approach are:

| App | Focus |
| --- | --- |
| `AN-sunspot-classification-studio-v0` | Route-family extraction, one clear active-region route surface, operations/SRS route clarity, and safer production error handling. |
| `AN-geomagnetic-observations-monitor-v0` | One clear geomagnetic route surface, alert/handoff route clarity, dev-only route separation, and safer production error handling. |
| `AN-synoptic-map-workbench-v0` | One clear `/api/v1/synoptic/...` route surface, centralized route registration, modular resource/service extraction, retired legacy route trees, and safer production error handling. |

Track detailed progress in [SWIFT_FALCON_REFACTOR_PROGRESS.md](./SWIFT_FALCON_REFACTOR_PROGRESS.md).

The next planned refactor wave includes CME SA Display, Geomagnetic Forecast Console, Solar Forecast Console, Historical Event Library, SunTrace, Partner Briefing Generator, and Sector Risk Dashboard. The wave plan and effort notes live in [SWIFT_FALCON_REFACTOR_PROGRESS.md](./SWIFT_FALCON_REFACTOR_PROGRESS.md).

## Definition Of Lightweight Falcon Maturity

An app is following the lightweight Falcon approach when:

- a developer can find `create_app()` immediately
- routes are registered in one obvious place
- `/health` works without external dependencies
- new public APIs use `/api/v1/{domain}/...`
- resources are thin and service logic is separated
- JSON responses use `resp.media`
- expected errors use Falcon HTTP exceptions
- unexpected errors return a production-safe JSON envelope
- CORS is explicit and configurable
- stable routes are documented
- each capability has one intended public route
- no parallel canonical/legacy route tree exists
- any temporary bridge has a named blocker, owner, and removal date

This gives SWIFT a common backend language without slowing down individual application development.
