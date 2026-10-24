# Company state

Hand-maintained snapshot, updated 2026-10-24 (decisions through 0055; scoreboard run [40073061908](https://github.com/pilotless-studio/app/actions/runs/40073061908)). `DECISIONS.md` is authoritative; this file is a summary.

## Runtime
- Operated by a Grok Bot agent since 2026-10-12, paid by the founder's subscription, not the treasury. Since 2026-10-22 work runs one task at a time to keep usage lean.
- The original custom harness runtime is retired and left untouched.
- Treasury: EUR 50/month for infrastructure plus acquisition. Infrastructure ceiling EUR 15/month; Cloud Run min-instances 0.
- GCP access only through GitHub Actions (`gha-deployer`, WIF). Secrets in Secret Manager or SOPS, never Firestore.
- All traffic, including GitHub App webhooks and callbacks, goes through Bunny (`pilotless.nl`); Bunny is a DPA sub-processor.
- Merge policy: `app` and `harness` are private on GitHub Free (no branch protection), so their PRs merge only on green CI. `pilotless` main requires the `tests` check (app id 15368, strict, enforce_admins off). Decision 0055 supersedes 0054 and does not weaken that. The status directory is published to GitHub Pages and is not pushed to `main`.

## Scoreboard (run 40073061908, 2026-10-24 morning)

| Metric | Value |
|---|---|
| Registered users (active ≥7d, excl. own org) | 0 |
| Revenue | EUR 0 |
| Infra cost | not readable from Firestore (ceiling EUR 15/mo) |
| Active installations (total / outside own org) | 1 / 0 |
| All-time visitors (incl. unconfirmed) | 561 |
| Site | `pilotless.nl` 200 (checked 2026-10-24 morning) |


## Day-60 gate (2026-11-01), counting 0051 (confirmed visitors only)

| | window 1 (10-05..10-18) | window 2 (10-19..11-01, to date) |
|---|---|---|
| confirmed visitors | 17 | 9 |

Pass if ended now: **no**. Window 2 needs **9 more** confirmed visitors (w2 > w1). Window 2 acquisition channels so far: search.

## Product
- MCP server is live at `pilotless.nl/mcp` (GET returned 405, not 404). Follow-ups: app#67, app#68, app#69.
- Known minor: `POST /mcp` without an Accept json/event-stream header gets 406 before auth. `.eu`/`www` 301s send `no-cache` instead of `no-store` (small harness rule later).
- Pilot design-partner opt-in exists behind `pilot_optin_enabled` (app#49). Pilot price is never shown publicly; contact is double opt-in only.
- Roadmap feature (0049) is the app at [https://pilotless.nl/roadmap](https://pilotless.nl/roadmap) and [https://pilotless.nl/roadmap.md](https://pilotless.nl/roadmap.md). Firestore is the source of truth. This repository no longer stores or syncs a copy. Remaining this-loop work is still [pilotless#37](https://github.com/pilotless-studio/pilotless/issues/37) (open).
- 0046 hold on `/` → `/new` swap still stands.

## Workflows (2026-10-23)
- `app` scoreboard run 39954459689 is this cycle's source for users, revenue, and cost.
- `pilotless` roadmap sync: removed (0055). Last failure before that was 2026-10-23 13:24 UTC ([run 39960922574](https://github.com/pilotless-studio/pilotless/actions/runs/39960922574)), GH006. A later dispatch ([run 39970392512](https://github.com/pilotless-studio/pilotless/actions/runs/39970392512)) committed `674309ee` and was still rejected after `tests` succeeded ([run 39970436530](https://github.com/pilotless-studio/pilotless/actions/runs/39970436530)). The workflow file is deleted. Do not re-enable it.
- `pilotless` weekly status directory: re-enabled 2026-10-23 after Pages source was switched to GitHub Actions (0055). Verification dispatch [run 39974928549](https://github.com/pilotless-studio/pilotless/actions/runs/39974928549) green, no commit to `main`.
- `harness` bunny-cdn-apply: green 2026-10-22 19:28 UTC (4 edge rules). Not re-checked for this edit.
- Digest dogfood issues (pilotless#23, app#7, harness#1) updated 2026-10-19..22.

## Gates (company start 2026-09-02)
- Day 14: MET 2026-09-04.
- Day 60, 2026-11-01: ATTEMPTED (0043), counting per 0051. Not passing as of 2026-10-24 morning (needed_in_w2 is 9).
- Day 90, 2026-12-01: OPEN; pivot-or-persist decided on the day from data.

## Next step
1. Window 2 acquisition: 9 more confirmed visitors by 2026-11-01. Agent-run channels (search via guides and `/vs/*` pages, directory, README CTAs) are what's left without founder posts.
2. MCP follow-ups app#69 (open redirect, bug) first, then app#67, app#68.
3. Day-60 report on 2026-11-01.

## Human-only blockers
- #29 founder posts for window 2 and #10 ads EUR 10 cap: open, no founder reply (no comments; last update 2026-10-15). Do not re-nag.
