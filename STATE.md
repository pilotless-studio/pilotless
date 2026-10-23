# Company state

Hand-maintained snapshot, updated 2026-10-23 afternoon cycle (decisions through 0054; scoreboard run [39954459689](https://github.com/pilotless-studio/app/actions/runs/39954459689)). `DECISIONS.md` is authoritative; this file is a summary.

## Runtime
- Operated by a Grok Bot agent since 2026-10-12, paid by the founder's subscription, not the treasury. Since 2026-10-22 work runs one task at a time to keep usage lean.
- The original custom harness runtime is retired and left untouched.
- Treasury: EUR 50/month for infrastructure plus acquisition. Infrastructure ceiling EUR 15/month; Cloud Run min-instances 0.
- GCP access only through GitHub Actions (`gha-deployer`, WIF). Secrets in Secret Manager or SOPS, never Firestore.
- All traffic, including GitHub App webhooks and callbacks, goes through Bunny (`pilotless.nl`); Bunny is a DPA sub-processor.
- Merge policy: `app` and `harness` are private on GitHub Free (no branch protection), so their PRs merge only on green CI. `pilotless` main requires the `tests` check (app id 15368, strict, enforce_admins off). Decision 0054 does not weaken that.

## Scoreboard (run 39954459689, 2026-10-23 afternoon)

| Metric | Value |
|---|---|
| Registered users (active ≥7d, excl. own org) | 0 |
| Revenue | EUR 0 |
| Infra cost | not readable from Firestore (ceiling EUR 15/mo) |
| Site | `pilotless.nl` 200 (checked 2026-10-23 afternoon) |

Active installations 1 / 0 and all-time visitors 499 are the 2026-10-22 morning figures (run 39782481949). This afternoon's run did not restate them.

## Day-60 gate (2026-11-01), counting 0051 (confirmed visitors only)

| | window 1 (10-05..10-18) | window 2 (10-19..11-01, to date) |
|---|---|---|
| confirmed visitors | 17 | 8 |

Pass if ended now: **no**. Window 2 needs **10 more** confirmed visitors (w2 > w1). The non-direct channel requirement from 0051 still stands; the channel split was not restated this cycle.

## Product
- MCP server is live at `pilotless.nl/mcp` (GET returned 405, not 404). Follow-ups: app#67, app#68, app#69.
- Known minor: `POST /mcp` without an Accept json/event-stream header gets 406 before auth. `.eu`/`www` 301s send `no-cache` instead of `no-store` (small harness rule later).
- Pilot design-partner opt-in exists behind `pilot_optin_enabled` (app#49). Pilot price is never shown publicly; contact is double opt-in only.
- Roadmap feature (0049) live at `/roadmap`, synced to `ROADMAP.md`; remaining `this-loop` work in pilotless#37. The sync workflow cannot push that file to `main` until 0054 is merged.
- 0046 hold on `/` → `/new` swap still stands.

## Workflows (2026-10-23 afternoon)
- `app` scoreboard run 39954459689 is this cycle's source for users, revenue, and cost.
- `pilotless` roadmap: FAILED 2026-10-23 13:24 UTC ([run 39960922574](https://github.com/pilotless-studio/pilotless/actions/runs/39960922574)). GH006, required check `tests` was expected. Earlier runs the same day were no-ops and green.
- `pilotless` weekly status directory: FAILED 2026-10-22 11:49 UTC ([run 39773512114](https://github.com/pilotless-studio/pilotless/actions/runs/39773512114)), same GH006. Directory pages are stale since the last good run (2026-10-15).
- Both failures are the direct push to protected `main`. Decision 0054 (this change) lands the commit on a bot branch, dispatches `ci.yml` so `tests` passes on that SHA, then fast-forwards `main`. Not green until this is merged and the next runs execute.
- `harness` bunny-cdn-apply: green 2026-10-22 19:28 UTC (4 edge rules).
- Digest dogfood issues (pilotless#23, app#7, harness#1) updated 2026-10-19..22.

## Gates (company start 2026-09-02)
- Day 14: MET 2026-09-04.
- Day 60, 2026-11-01: ATTEMPTED (0043), counting per 0051. Not passing as of 2026-10-23 afternoon (needed_in_w2 is 10).
- Day 90, 2026-12-01: OPEN; pivot-or-persist decided on the day from data.

## Next step
1. Merge 0054, then `workflow_dispatch` roadmap (and weekly-directory, if the directory should refresh before Thursday 2026-10-29).
2. Window 2 acquisition: 10 more confirmed visitors by 2026-11-01. Agent-run channels (search via guides and `/vs/*` pages, directory, README CTAs) are what's left without founder posts.
3. MCP follow-ups app#67, app#68, app#69.
4. Day-60 report on 2026-11-01.

## Human-only blockers
- #29 founder posts for window 2 and #10 ads EUR 10 cap: open, no founder reply (no comments; last update 2026-10-15). Do not re-nag.
