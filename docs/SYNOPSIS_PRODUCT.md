# Synopsis product: working first pass

An isolated synthetic exercise is available through the suite [shared catalogue](../../SWIFT-Applications/testing/README.md). It runs on port 5182 with separate storage, explicit EXERCISE provenance, an editable cross-domain seed, and actual GOM/GFC adapter calls. Port 5180 retains the operational workspace.

The product crosswalk in `SWIFT-Applications/docs/reference/SWPC_Modernized_IDSS_and_Product_Services (2).docx` treats Synopsis as a routine retrospective scientific assessment. It includes recent activity, observations, interpretation, current indices, and the daily 245 MHz summary. Forecast reasoning belongs in forecast products. Edited Events, SRS, and Synoptic Map remain separate products.

This is a working product definition. Final name, identifiers, cadence, exact sections, and required source completeness remain open for iteration.

## Workflow

1. Set reporting start/cutoff in UTC. The initial 24 hours is an editable default.
2. Collect available evidence and edit the assessment. Appending suggested observations never replaces existing text.
3. Save a draft, then Save review to retain an immutable text snapshot, reporting interval, evidence references, runtime, and content hash.
4. Push the current reviewed version to Product Launcher as a review candidate. This does not issue a product. Repeated sends reuse the same candidate key.
5. Core Distribution and Partner Tailored Brief can explicitly load and preview the reviewed Synopsis, then replace their narrative with that snapshot. Briefing edits remain independent; source version metadata is retained.

Only geomagnetic adapters currently exist. Solar, particle/fluence, Edited Events, and radio sources are shown as not connected. Manual assessment is supported. Suggested text currently requires both existing geomagnetic adapters to pass their evidence checks; this is not a full multisource Synopsis generator.

## Persistence and runtime

`api/synopsis/workspace.py` uses the briefing SQLite database. `synopsis_workspaces_v2` isolates drafts by operational/replay scenario. `synopsis_reviews` retains immutable reviews; `synopsis_receipts` records confirmed candidate handoffs. If-Match protects saves and review actions against stale versions. Reporting cutoffs cannot exceed the server application clock. Replay cannot enter the operational Product Launcher queue. Clock rewind hides drafts/reviews ahead of that clock.

The old unscoped `synopsis_workspace` table is preserved, but is not automatically imported into operational mode because it has no verified runtime provenance. Recover any needed legacy narrative from that table and explicitly review it in the correct workspace.

`SYNOPSIS_PRODUCT_LAUNCHER_URL` configures delivery. `SYNOPSIS_MAX_DELIVERY_AGE_HOURS` defaults to 24 as a provisional currentness guard, not a product cadence. Reporting times are stored inside the content rather than forecast valid-start/end fields. Authentication/attribution should ultimately use the suite CAC identity; no manual forecaster-name field was introduced.

## Validation

Run API tests in the supported container environment:

```
docker compose run --rm --no-deps api python -m unittest discover -s api/tests -v
npm --prefix ui run build
```

Integration tests cover persistence, stale revisions, immutable reviews, runtime/scenario separation, clock rewind, reporting windows, candidate delivery, and safe retries. Product Launcher separately tests rejection of replay Synopsis provenance.
