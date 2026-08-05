# Partner Briefing Generator

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
- Pillow for social-graphics image processing
- SQLite for local draft/export persistence

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
  persistence.py               draft/export SQLite tables
  social_graphics.py           PNG export variant generation
  science/
    briefing_logic.py          template validation, derivation, previews
    templates/                 master/discussion/ICAO/staff templates
docs/                          STPI and IDSS reference material
generated/                     runtime social-graphics outputs
graphics_library/              source visual assets and logos
ui/                            Vue/Vuetify frontend
email_briefing.db              local SQLite runtime database
```

## Runtime Data

Local persistence uses `email_briefing.db` at the repository root. On API startup, the app creates these tables if needed:

- `drafts`
- `generated_outputs`
- `social_graphics_drafts`
- `social_graphics_exports`

Generated social-graphics assets are written under:

```text
generated/social_graphics/<export_id>/
```

Each export includes the scene JSON, the submitted base PNG, and generated PNG variants.

## API

Default API URL:

```text
http://127.0.0.1:8089
```

Routes:

- `GET /health`
- `GET /api/v1/partner-briefing/now`
- `GET /api/v1/partner-briefing/briefing-types`
- `GET /api/v1/partner-briefing/templates/{briefing_type}`
- `GET /api/v1/partner-briefing/templates/{briefing_type}/versions/{version}`
- `POST /api/v1/partner-briefing/drafts`
- `GET /api/v1/partner-briefing/drafts/{draft_id}`
- `PATCH /api/v1/partner-briefing/drafts/{draft_id}`
- `POST /api/v1/partner-briefing/drafts/{draft_id}/derive`
- `POST /api/v1/partner-briefing/drafts/{draft_id}/preview`
- `POST /api/v1/partner-briefing/drafts/{draft_id}/pdf`
- `POST /api/v1/partner-briefing/social-graphics/drafts`
- `GET /api/v1/partner-briefing/social-graphics/drafts/{draft_id}`
- `PATCH /api/v1/partner-briefing/social-graphics/drafts/{draft_id}`
- `POST /api/v1/partner-briefing/social-graphics/exports`
- `GET /api/v1/partner-briefing/social-graphics/exports/{export_id}/assets/{variant_id}`
- `GET /api/v1/partner-briefing/context/alerts/active`
- `GET /api/v1/partner-briefing/context/advisories/icao/active`

## Local Development

### Docker Desktop

From the repository root, build and start the API and UI containers:

```powershell
docker compose up --build
```

Default Docker URLs:

```text
UI:  http://localhost:5179
API: http://localhost:8089
```

The UI container serves the built Vue app with nginx and proxies `/api` to the
API container. The API container persists local data through these bind mounts:

```text
./email_briefing.db -> /srv/partner-briefing/data/email_briefing.db
./generated         -> /srv/partner-briefing/generated
```

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
UI:  http://127.0.0.1:5179
API: http://127.0.0.1:8089
```

### Operational And Replay Time

The API owns the authoritative clock. Operational mode uses server UTC:

```powershell
$env:PARTNER_BRIEFING_API_DATA_SOURCE = "operational"
```

Replay mode requires an explicit UTC timestamp and never falls back to live time:

```powershell
$env:PARTNER_BRIEFING_API_DATA_SOURCE = "replay"
$env:PARTNER_BRIEFING_REPLAY_NOW_UTC = "2024-05-10T16:37:00Z"
$env:PARTNER_BRIEFING_REPLAY_SCENARIO = "may_2024_geomagnetic_storm"
docker compose up --build
```

`SWIFT_REPLAY_NOW_UTC` is supported as a suite-wide clock alias. Briefing drafts
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

The current API context feeds are placeholders:

- active SWPC alerts are represented by placeholder records
- active ICAO advisories are represented by placeholder records

Reference material lives under `docs/`, including STPI report material, SWIFT IDSS sector threshold tables, and the authoritative Gannon replay fixture. Runtime branding assets live under `ui/public/assets/visual-finder/logos/`.

## Current Maturity

Prototype.

Implemented:

- API route surface for templates, drafts, derivation, preview, and graphics export
- SQLite persistence for briefing and social-graphics records
- Vue workspace and social-graphics components
- reusable template JSON files and derivation rules
- local visual asset catalog

Known gaps:

- PDF generation is scaffolded but not implemented.
- Active alert and ICAO advisory context are placeholder data.
- Runtime clock and interface-density tests cover replay configuration and persisted responsive presentation behavior.
- Runtime SQLite and generated assets should be treated as local artifacts, not source-controlled product data.

Development guidance for keeping the Falcon API aligned with the SWIFT
lightweight structure lives in `docs/API_DEVELOPMENT_GUIDE.md`.
