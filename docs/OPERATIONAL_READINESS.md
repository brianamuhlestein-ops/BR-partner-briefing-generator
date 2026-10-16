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

## Remaining measurements

- Measure cold and warm source-bundle collection with one and four forecasters
  against deployed GOM, GFC, CME, and HEL services.
- Exercise SQLite conflict recovery with the deployed shared-volume topology.
  Move authored state to an operations database before running multiple API
  replicas, because SQLite and local atomic files do not coordinate replicas.
- Confirm Product Launcher's idempotency behavior under a lost response in a
  disposable end-to-end environment.
- Review the tracked 42.9 MB Gannon social-media reference PDF and 14.5 MB
  aurora image with the product owner before any asset retention change; both
  are current reference or exercise inputs and were not proven disposable.
- Record lazy-loading or bundle-splitting as a UI performance option. The
  current production build passes but reports a 552 KB JavaScript chunk and a
  689 KB CSS chunk.
