# Synopsis evidence API

This capability is hosted by Briefing & Synopsis (API 8089, UI 5180).
The existing versioned summary namespace and schema names are retained.
The collection/draft contracts below preserve the original evidence behavior.

# Source Bundle API

Status: local first-slice implementation

## Collection

`POST /api/v1/space-weather-summary/source-bundles` creates one immutable
bundle. A minimal operational request is:

```json
{
  "cutoff_at_utc": "2026-08-14T22:00:00Z",
  "actor_id": "operations.forecaster",
  "actor_type": "forecaster"
}
```

When `cutoff_at_utc` is omitted, the service uses current UTC. `actor_type` is
`forecaster` or `service` and defaults to the Summary Builder service identity.

The collector reads each producer's existing immutable export collection,
orders eligible candidates by generation time, and retrieves the latest valid
context at or before the cutoff. Collection is read-only: it does not cause a
producer application to create a new context.

A caller may pin exact records:

```json
{
  "cutoff_at_utc": "2026-08-14T22:00:00Z",
  "context_ids": {
    "geomagnetic-observations-monitor": "gom-20260814T220000Z-24h-r1",
    "geomagnetic-forecast-console": "gfc-20260814T210000Z-approved-r1"
  },
  "actor_id": "operations.forecaster",
  "actor_type": "forecaster"
}
```

Any key outside those two registered slugs returns `400 invalid_bundle_request`.

## Eligibility

A selected context must:

- validate against the exact schema registered for its application;
- be `reviewed` or `approved` and not superseded;
- report usable, available, non-stale, and complete quality;
- be generated at or before the cutoff;
- match Summary Builder's operational or replay runtime and replay scenario;
- satisfy its role-specific validity rule; and
- expose non-experimental producer-selected narrative facts.

Observations must cover the cutoff. Forecast guidance must extend beyond the
cutoff. If the newest candidate is ineligible, automatic selection examines
older candidates in descending generation order.

## Outcomes

The API returns `201 Created` for both durable outcomes:

- `ready`: both contexts are selected and the fact ledger is available;
- `needs_attention`: a required source is missing, invalid, mismatched, or
  superseded, and the fact ledger is empty.

`needs_attention` is an auditable workflow record, not an HTTP transport
failure. Producer connection problems and validation findings appear in
`collection_errors` and the per-source `errors` array.

The service does not perform narrative generation from a needs-attention
bundle.

## Integrity and Persistence

Each selected context receives a SHA-256 digest of its RFC 8785 canonical JSON.
The bundle digest covers the ordered `sources` and `fact_ledger` arrays using
the same canonicalization. Bundle records are written once under
`runtime-data/source-bundles/`; there is no update or delete route.

The create response sets `Location` to the immutable detail route. Collection
and detail reads use:

```http
GET /api/v1/space-weather-summary/source-bundles?limit=25
GET /api/v1/space-weather-summary/source-bundles/{bundle_id}
```

The `limit` range is 1 through 250.

## Replay

Set:

```text
SUMMARY_BUILDER_RUNTIME_MODE=replay
SUMMARY_BUILDER_REPLAY_SCENARIO=may_2024_geomagnetic_storm
```

Both selected contexts must carry the same replay mode and scenario. An
operational/replay mixture is persisted as `needs_attention` and cannot expose
a narration ledger.


# Deterministic Draft API

Status: local first-slice implementation

`POST /api/v1/space-weather-summary/drafts` creates an immutable revision-one
draft from one `ready` source bundle:

```json
{
  "bundle_id": "ssb-20260814T220000Z-example",
  "actor_id": "operations.forecaster",
  "actor_type": "forecaster"
}
```

The service rejects `needs_attention` bundles. It also requires at least one
eligible Observations Monitor fact and one eligible Forecast Console fact.

The first template produces:

- `current_conditions` sentences from Observations Monitor facts;
- `forecast` sentences from Forecast Console facts; and
- a `limitations` section only when a ready future bundle contains an eligible
  limitation fact.

Every sentence contains one or more `support_fact_ids` that must resolve to the
frozen bundle ledger. The source bundle ID and integrity hash are copied into
the draft. Sentence order follows the deterministic ledger order.

Generation metadata is explicitly:

```json
{
  "method": "deterministic_template",
  "template_version": "geomagnetic-deterministic-v1",
  "prompt_template_id": null,
  "model": null,
  "settings": {}
}
```

No LLM, prompt, or external model endpoint is used in this slice. The template
does not derive new science; it renders producer-owned values, units, times,
confidence, and labels.

Create, list, and detail routes are:

```http
POST /api/v1/space-weather-summary/drafts
GET  /api/v1/space-weather-summary/drafts?limit=25
GET  /api/v1/space-weather-summary/drafts/{draft_id}
```

Draft edits, revisions, model-assisted alternatives, review, and approval are
not implemented yet.
