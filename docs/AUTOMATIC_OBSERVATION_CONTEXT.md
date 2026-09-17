# Automatic observation context for narratives

Geomagnetic Observations Monitor persists a 24-hour context every five minutes
without requiring an operator or open browser. The narrative builder reads these
immutable snapshots using `/api/v1/geomagnetic/context/exports` and the ID-specific
detail route. Creating the source bundle and draft remains in Partner Briefing
Generator; capturing context does not create or send a briefing.

The shared source registry revision 2 allows `working` observation context up to
600 seconds before the narrative cutoff. Automatic observations remain explicitly
unreviewed. Forecast guidance must still be reviewed or approved. Existing schema,
quality, source runtime/scenario and supersession eligibility checks remain active.
The briefing source bundle records the selected snapshot IDs and content hashes.

The local monitor currently uses fake data while Partner Briefing Generator uses
operational mode. Retrieval and schema validation work, but operational narrative
selection correctly rejects this runtime mismatch. Test fixtures verify successful
automatic-observation-to-narrative generation with aligned runtime modes.
