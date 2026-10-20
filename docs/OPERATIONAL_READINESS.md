# Partner Briefing Generator operational readiness

Date: 2026-10-16. Scope: four-forecaster request behavior, persistence,
delivery safety, worker need, and retained data. This is engineering readiness
evidence, not content or scientific validation.

## Execution boundary

Partner Briefing Generator is request driven. A forecaster explicitly saves an
email briefing, collects a source bundle, generates a deterministic draft,
reviews a Synopsis, or sends a reviewed candidate to Product Launcher. None of
these operations is a scheduled ingest, recurring science calculation, or
long-running retry queue. A standalone worker is not justified by the current
workload.

Identical read-only requests to the shared HEL replay session, GOM or GFC
context producers, and reviewed CME context now share only work that is
currently in progress. Completed responses are not cached. A later request
therefore observes the current operational data or replay clock. Each caller
receives an independent response object.

## Persistence and delivery boundary

The email briefing records and shared Synopsis workspace use SQLite WAL mode,
a five-second busy timeout, optimistic versions, `If-Match`, and HTTP 409
conflicts. Synopsis reviews are immutable by workspace version. Source bundles
and generated drafts are immutable JSON records written to a temporary file,
flushed to disk, and atomically linked into place. Readers cannot observe a
partially written record.

Product delivery remains synchronous because it is a deliberate forecaster
action. The reviewed Synopsis ID is the Product Launcher idempotency key, and a
confirmed receipt is stored before subsequent calls return it. A failed or
timed-out call retains the reviewed Synopsis and can be retried safely against
Product Launcher's idempotent candidate endpoint. Durable unattended delivery
would require a governed queue and worker; that lifecycle does not exist in the
current product contract.

The repository contains two ignored 77,824-byte local SQLite files. Both pass
SQLite integrity checks and contain no authored email, workspace, review, or
receipt rows. They remain in place because one is the local-development default
and the other is the Compose bind-mount database. The external Synopsis volume
and all tracked Gannon briefing, graphic, and social-media assets were left
untouched.

## Verification

- 42 API tests passed.
- Four simultaneous identical HEL, producer-context, and CME-context reads
  each produced one mocked upstream request and isolated caller responses.
- Existing tests confirm optimistic authoring conflicts, immutable review,
  replay separation and rewind behavior, and idempotent delivery receipts.
- Six UI tests and the production UI build passed.
- Python compilation, Compose validation, and Git diff checks passed.
- Renaming the internal HTTP helper removed a standard-library name collision;
  the full `python -m pytest api` collection now succeeds.

No UI, authoring sequence, product content, science rule, public route, response
contract, replay selection, or persistence record was changed.

## Bounded browser and delivery check — 2026-10-20

The built UI/proxy and production four-thread Waitress API were exercised with
one and four independent Edge browser contexts. Test authoring used a private
Windows bind-mounted SQLite database and separate Docker volume for immutable
Synopsis files, matching the local storage arrangement. Normal records, the
13 existing Synopsis files, and the HEL session were preserved. This establishes
behavior on this local single-process topology, not an untested deployment's
shared filesystem or multiple API replicas.

- Three single-user saves/reloads retained exact text. Four competing saves
  produced one winner and three 409s; every browser retained its own narrative
  and displayed an actionable conflict. Explicit reload retrieved the winner.
- A newer draft did not modify its earlier review. An older browser could not
  review the superseded workspace version. Core email writes independently
  produced one winner and three 409s. SQLite integrity passed in WAL mode.
- Real source-bundle collection at the existing 18Z replay clock took 109–174 ms
  for one caller and 159–221 ms for four. These include missing/ineligible
  evidence, not successful complete scientific bundles. “Cold” means a freshly
  started briefing process; upstream/OS caches were not cleared.
- The retained GOM context uses the session ID as scenario and reports partial,
  degraded quality; GFC's retained replay forecast is later than the cutoff;
  CME has no reviewed context. The application rejected these as expected.
  Successful collection/draft generation was checked separately with explicit
  synthetic context fixtures, without editing normal source exports.
- Four overlapping fixture collectors shared each active upstream read but
  retained four distinct bundles/drafts. Read-back contents matched. An injected
  producer outage or ten-second timeout left saved/reviewed text unchanged;
  an independent email read completed in 47 ms during the timeout. HEL outage
  safely blocked clock-dependent Synopsis operations and recovered on retry.
- A real private PostgreSQL Launcher accepted a reviewed candidate, then the
  test relay closed the connection before the briefing app received the result.
  This exposed an uncaught `RemoteDisconnected`/`OSError`, previously a generic
  500. Delivery now catches transport `OSError` and returns the existing 503
  message that the review is retained and retry is safe. No delivery protocol
  or idempotency key changed.
- Four retries yielded one candidate, one revision, zero issues, and exact
  reviewed product text. API restart preserved the review and receipt; later
  retries reused the receipt without resending. Delivery used only private
  operational-mode instances with synthetic wording; normal replay-to-live
  delivery remained disabled. Replay/exercise guards were not bypassed.
- 43 API tests passed on Windows; all eight Synopsis integration tests passed
  in the rebuilt Linux image. Six UI tests and the production build passed.
  Browser checks had no JavaScript exceptions. Test containers, network, volume,
  and private SQLite files were removed. No new service, UI, science, schema,
  route, deployment setting, or worker was added.

Full measurements, resource limits and experiment evidence are in the suite's
`docs/PARTNER_BRIEFING_READINESS_2026-10-20.md` and
`docs/evidence/partner-briefing-workflow-2026-10-20.json`.

## Remaining operational decisions

- Repeat storage/conflict and representative complete-source measurements on
  the intended deployment filesystem. Choose the operations database and shared
  immutable-file storage before multiple API replicas; separate local files do
  not provide replica coordination.
- Refresh/create eligible producer context exports for the chosen replay
  cutoff before claiming complete native-source coverage. Do not relax scenario,
  quality, cutoff or reviewed-context checks to fill a briefing.
- Review the tracked 42.9 MB Gannon social-media reference PDF and 14.5 MB
  aurora image with the product owner before any asset retention change; both
  are current reference or exercise inputs and were not proven disposable.
- Record lazy-loading or bundle-splitting as a UI performance option. The
  current production build passes but reports a 552 KB JavaScript chunk and a
  689 KB CSS chunk.
