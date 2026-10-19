# Application dependency security review

## Shared Vue and source-map patch batch - 2026-10-19

Vue and its coupled compiler/runtime/server-renderer packages now lock 3.5.44;
source-map-js locks 1.2.2. Required compiler dependencies (Babel, entities,
PostCSS and nanoid where needed) update within compatible existing constraints.
Vite, Vuetify, API/scientific dependencies, application source and UI styling
remain unchanged. No new public route, schema or service.

This addresses [Vue server-renderer](https://github.com/advisories/GHSA-g2v6-rqmx-r4w6)
and [source-map-js](https://github.com/advisories/GHSA-68fv-2mgg-jv7q).
The Vue advisory concerns server-rendered attributes; these standalone UIs use
client rendering. Finding removal does not establish prior exploitability.

Checks: clean install with lifecycle scripts disabled, before/after production
builds, user guide open/close, and available primary navigation compared against
the same bounded baseline API responses. No new JavaScript errors. 6 existing UI tests passed.
Latest npm affected-package counts: 0 critical, 0 high, 2 moderate, 0 low. These supersede any earlier npm counts above; Python and runtime-image findings are separate.

Browser checks used an ephemeral loopback static server and blocked mutation
requests/external feeds. Stopped APIs used explicit runtime fixtures or normal
unavailable-data responses; this is not a full data/science or multiuser test.
Federated host integration remains a deployment check with Jason.

Central evidence: `SWIFT-Applications/docs/evidence/shared-ui-security-2026-10-19.json`.
Dockerfiles, Compose, bindings, Nginx and replay/authored databases are unchanged.
Existing running images retain their scan identities until explicitly rebuilt.
