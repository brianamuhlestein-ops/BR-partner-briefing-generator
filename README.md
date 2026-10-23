# Briefing & Synopsis

As of 2026-09-14, this application also owns the former Summary Builder evidence
engine and the new Synopsis workspace. The standalone Summary Builder deployment
is retired. Existing partner briefing routes remain stable; the additional
`/api/v1/space-weather-summary` routes run in this API process.

The Synopsis tab collects reviewed source contexts, prepares cited suggested
text, and saves a forecaster-edited workspace with optimistic concurrency.
`GET /api/v1/space-weather-summary/source-context/cme-sa` reads the configured
`SYNOPSIS_CME_CONTEXT_URL` and accepts only usable, current, reviewed CME
assessments whose runtime and replay scenario match Synopsis. Saves are working
state, not issuance. The former Impact & Risk Matrix is now a read-only reference
in Sector Risk Dashboard; manual risk scoring is removed.

Docker retains the existing summary evidence volume under its original name.
For a fresh deployment, create it once with
`docker volume create br-space-weather-summary-builder_summary_runtime`.
The external volume is deliberately not removed by `docker compose down -v`.
Native deployments may set `SUMMARY_BUILDER_DATA_ROOT` to the former evidence
directory to preserve existing bundles and drafts. Source contracts are mounted
from the suite and geomagnetic applications as documented in Compose.

Partner Briefing Generator is a SWIFT briefing and communications prototype for turning operational space-weather context into partner-ready products. It combines a Falcon API, a Vue/Vuetify workspace, SQLite-backed briefing storage, replay fixtures, and client-side PDF/social-graphics export workflows.

## Current Purpose

The app is intended to support:

- IDSS impact and risk evaluation by partner sector
- core distribution and partner-tailored briefing authoring
- replay-aware May 2024 exercise briefings and media products
- social graphic composition from reviewed product JSON
- client-side PDF and PNG preview/export

## Stack

Backend:

- Python
- Falcon API
- Waitress local server
- SQLite for local briefing persistence

Frontend:

- Vue 3
- TypeScript
- Vite
- Vuetify
- HTML/CSS social-product composition with html2canvas PNG export
- MDI icon font

## Repository Layout

```text
api/
  app.py                       WSGI import entrypoint
  run_api.py                   Falcon app factory and local server entrypoint
  routes.py                    route registration and public API prefixes
  middleware.py                CORS middleware
  errors.py                    production-safe unexpected error handling
  http.py                      shared request parsing helpers
  resources.py                 thin Falcon route resources
  config.py                    local settings and SQLite location
  persistence.py               saved briefing-document storage
docs/                          STPI and IDSS reference material
  exercise/gannon/             tracked testbed briefings, JSON, and graphics
graphics_library/              source visual assets and logos
ui/                            Vue/Vuetify frontend
runtime-data/                  writable container data (database is created here)
email_briefing.db              native-development SQLite runtime database
```

## Runtime Data

Native development persistence uses `email_briefing.db` at the repository root.
Docker persistence uses `runtime-data/email_briefing.db`. Both database files are
local runtime state and are created automatically by the API. On startup, the app
creates the `email_briefing_documents` table if needed. Synopsis source bundles,
drafts, reviewed products, and delivery receipts use the separate Synopsis
stores described in `docs/SYNOPSIS_API.md` and `docs/SYNOPSIS_PRODUCT.md`.

The May 2024 testbed library is not stored in the runtime database. Its briefing
JSON, product JSON, and graphics are tracked under `docs/exercise/gannon/` and are
bundled into the UI image. A fresh checkout therefore includes the complete
exercise catalog even before a forecaster saves a working document.

### Shared authoring boundary

Saved briefing documents use optimistic concurrency. Item reads expose
`record_version` and an `ETag`; every `PUT` must send that version in `If-Match`.
A stale writer receives
`409 revision_conflict`, so another user's newer work is never silently
overwritten. A new saved email document is created with `If-Match: "0"`.

SQLite runs in WAL mode with a write wait and is supported for multiple users
through one API deployment on one host. The database file must remain on local
storage. PostgreSQL is required before running multiple API replicas, placing
the database on shared/network storage, or treating this app as a horizontally
scaled production service. Generated outputs and social exports are append-only.

## API

Default API URL:

```text
http://127.0.0.1:8089
```

Routes:

- `GET /health`
- `GET /api/v1/partner-briefing/now`
- `GET /api/v1/partner-briefing/email-briefings/{briefing_kind}`
- `PUT /api/v1/partner-briefing/email-briefings/{briefing_kind}`

The Synopsis route surface is documented in `docs/SYNOPSIS_API.md` and
`docs/SYNOPSIS_PRODUCT.md`.

## Local Development

### Docker Desktop

From the repository root, build and start the API and UI containers:

```powershell
docker compose up --build
```

Default Docker URLs:

```text
UI:  http://localhost:5180
API: http://localhost:8089
```

The UI container serves the built Vue app with nginx and proxies `/api` to the
API container. The API container persists local data through these bind mounts:

```text
./runtime-data -> /srv/partner-briefing/data
```

Mounting the directory allows SQLite to create the database on the first run.
If upgrading a checkout that has saved records in the old root database, stop
the containers and copy `email_briefing.db` to
`runtime-data/email_briefing.db` before restarting.

Optional port overrides:

```powershell
$env:EXTERNAL_UI_PORT = "5180"
$env:PARTNER_BRIEFING_API_PORT = "8090"
docker compose up --build
```

### Native

Start the API:

```powershell
python -m pip install -r api\requirements.txt
python -m api.run_api
```

Start the UI:

```powershell
cd ui
npm install
npm run dev
```

Default local URLs:

```text
UI:  http://127.0.0.1:5180
API: http://127.0.0.1:8089
```

### Operational, Replay, And Exercise Time

The API owns the authoritative clock. Operational mode uses server UTC:

```powershell
$env:PARTNER_BRIEFING_SOURCE_MODE = "live"
```

Gannon replay reads the same HEL session clock used by the rest of the suite:

```powershell
$env:PARTNER_BRIEFING_SOURCE_MODE = "gannon"
$env:SWIFT_REPLAY_CATALOG_URL = "http://localhost:8088/api/v1/historical-events/gannon-2024"
$env:SWIFT_REPLAY_SESSION_ID = "your-session-id"
docker compose up --build
```

The synthetic suite integration exercise remains explicit through
`SWIFT_EXERCISE_CATALOGUE_URL` and `PARTNER_EXERCISE_NOW_UTC`; it does not act
as another Gannon runtime. Briefing drafts
store the forecast issue-time snapshot and three derived UTC valid dates separately
from their physical `created_at` and `updated_at` audit timestamps.

The Vite dev server proxies `/api` to the API service configured in `ui/vite.config.ts`.

## Outputs

- briefing draft records in SQLite
- HTML preview payloads from saved draft sections
- scaffolded PDF response payloads
- social-graphics draft records in SQLite
- exported PNG variants:
  - landscape `1920x1080`
  - square `1080x1080`
  - portrait `1080x1350`

## External Inputs And References

Reference material lives under `docs/`, including STPI report material, SWIFT IDSS sector threshold tables, and the authoritative Gannon replay fixture. Runtime branding assets live under `ui/public/assets/visual-finder/logos/`.

## Current Maturity

Prototype.

Implemented:

- revisioned SQLite persistence for the three current briefing workspaces
- Synopsis evidence collection, review, and Product Launcher handoff
- Vue workspace and social-graphics components
- local visual asset catalog

Known gaps:

- Runtime clock and interface-density tests cover replay configuration and persisted responsive presentation behavior.
- Runtime SQLite is local application state. Exercise products that
  must ship to the testbed belong in the tracked `docs/exercise/gannon/` fixture.

Development guidance for keeping the Falcon API aligned with the SWIFT
lightweight structure lives in `docs/API_DEVELOPMENT_GUIDE.md`.

## R2O2R Evidence

Saved research records are available through the owning read-only API and the
Performance Review R2O2R Evidence tab. Selected portable exports preserve available
dependencies and declare historical gaps. See the suite
[export scope and connection inventory](../SWIFT-Applications/docs/RESEARCH_CASE_EXPORTS.md#suite-integration-closeout).
