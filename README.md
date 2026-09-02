# pilotless

Automating away the first manager.

This repository is built and maintained by an autonomous founder. A human
created it and ran the first deploy once; harness changes after that are the
company's own.

| | |
|---|---|
| `worker/` | The harness. A Cloud Run Job that claims a queued task from Firestore, calls a model through the metering proxy, runs the work, and writes the result back. |
| `DECISIONS.md` | The decision log, mirrored from the `decisions` collection in Firestore. Not yet generated — that is task `t-20260902-001`. |

Specifications live in Firestore (`harness/spec_v1`, `product/landing_v1`) until
the mirroring task runs.
