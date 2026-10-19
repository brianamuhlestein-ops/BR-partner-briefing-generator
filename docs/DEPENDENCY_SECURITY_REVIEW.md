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

## Frontend toolchain security follow-up - 2026-10-19

vite: ^7.3.1 to ^7.3.7; vitest: ^4.1.10 to ^4.1.12. Existing major-version families are retained.

A fresh before/after production build and browser baseline was captured. Clean installs with lifecycle scripts disabled and the updated production build pass. Compiled CSS content hashes match exactly. Existing guide text and available primary navigation are compared with bounded baseline API responses; external requests and writes are blocked. This does not certify complete operational/science workflows or host federation.

6 existing frontend tests pass.

The existing npm 10.9.8 resolver raised an internal `edgesOut` error during the coupled Vitest patch. An isolated npm 12.2.0 tool generated the staged lock; lock format 3 is retained and the normal npm 10.9.8 clean install/build/tests pass without a peer bypass. No global tool or CI version was changed.

Application/science/UI/style sources, Vite configuration, Dockerfiles, Compose, Nginx, ports and normal data are unchanged by this patch. No active images are rebuilt/restarted. Linux repeat coverage and the dated source rescan are recorded separately in `SWIFT-Applications/docs/evidence/frontend-toolchain-security-2026-10-19.json`; runtime image findings remain independently dated.

References: [Vite maintained-branch fixes](https://github.com/vitejs/vite/security/advisories/GHSA-rq7h-c2jc-7f22), [Vite middleware fix](https://github.com/vitejs/vite/security/advisories/GHSA-9jrq-w75r-8gcw), and [Vitest Windows follow-up](https://github.com/vitest-dev/vitest/security/advisories/GHSA-xp26-3454-mjgp).
