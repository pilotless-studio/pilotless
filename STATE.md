# Company state

Hand-maintained snapshot, updated 2026-11-05 morning (decisions through 0058; scoreboard run [41857027349](https://github.com/pilotless-studio/app/actions/runs/41857027349) from 2026-11-04 15:22 UTC). `DECISIONS.md` is authoritative; this file is a summary.

## Runtime
- Operated by a Grok Bot agent since 2026-10-12, paid by the founder's subscription, not the treasury. Since 2026-10-22 work runs one task at a time to keep usage lean.
- The original custom harness runtime is retired and left untouched.
- Treasury: EUR 50/month for infrastructure plus acquisition. Infrastructure ceiling EUR 15/month; Cloud Run min-instances 0.
- GCP access only through GitHub Actions (`gha-deployer`, WIF). Secrets in Secret Manager or SOPS, never Firestore.
- All traffic, including GitHub App webhooks and callbacks, goes through Bunny (`pilotless.nl`); Bunny is a DPA sub-processor.
- Merge policy: `app` and `harness` are private on GitHub Free (no branch protection), so their PRs merge only on green CI. `pilotless` main requires the `tests` check (app id 15368, strict, enforce_admins off). Decision 0055 supersedes 0054 and does not weaken that. The status directory is published to GitHub Pages and is not pushed to `main`.

## Scoreboard (run 41857027349, 2026-11-04)

| Metric | Value |
|---|---|
| Registered users (active ≥7d, excl. own org) | 1, the founder's kadima-tech org (dogfooding, installed 2026-10-25). Real outside users: 0 |
| Revenue | EUR 0 |
| Infra cost | not readable from Firestore (ceiling EUR 15/mo) |
| Active installations (total / outside own org) | 2 / 1 (kadima-tech, founder) |
| Site | `pilotless.nl` 200, `/app/signin` 303 (checked 2026-11-05 morning) |
| Visitors all-time (metrics_daily) | 1261 |

## Day-60 gate (2026-11-01): PASSED (0058)

| | window 1 (10-05..10-18) | window 2 (10-19..11-01) |
|---|---|---|
| confirmed visitors | 17 | 29 |

Window 2 channels: direct 24, referral 3, search 1, header 1. Weak, self-reported evidence; no registrations.

## Today (2026-11-05 cycle)
- Usage: weekly limit 3.2% (reset 2026-11-11 09:43 CET), on pace, so two packages.
- Health: site 200, `/app/signin` 303; app (scoreboard, weekly digest 2026-11-02, admin), pilotless (weekly status) and harness workflows green. No founder replies on #29 and #10.
- Usage finding (last 7 days): a polling routine "Watch Pilotless issue replies" runs about 100 times a week and costs about 2x this operating cycle. It is not one of the CEO's routines; flagged to the founder to replace with an event trigger or pause.
- Package 1 (Engineering), token reduction: a non-AI GitHub Action that runs before the cycle and writes one compact health summary (site and sign-in status codes, latest conclusion per scheduled workflow in app/pilotless/harness, new non-bot comments on `escalation` issues, scoreboard headline numbers), so the cycle reads one file instead of several API calls and logs. Why: founder's standing top priority (2026-10-31); every later cycle gets cheaper. Done when merged on green CI and one dispatched run's output matches this morning's manual check.
- Package 2 (Marketing), conversion toward day 90: final copy for the homepage install CTA (app#89). Why: day 90 measures registrations and the homepage has no install path; copy is the blocker. Done when the copy (headline, button label, one supporting line, target URL) is posted on app#89; Engineering implements in a later slot.
- Not needed today: SEO, Market Research, Sales, Design, QA.

## Backlog (prioritised)
1. Token reduction per cycle (founder priority 2026-10-31): non-AI health-check Action (package 1 today), then a wake-only-on-change hook, tighter briefs, replaced polling routines. Report findings to Groktimus Prime when done.
2. Homepage install CTA (app#89): copy from Marketing today, then Engineering. Converts visitors to installs for the day-90 gate (2026-12-01, registrations).
3. Phase 3 Slack connector (app#109, harness#21, paused for usage).
4. app#68, app#32 MCP follow-ups.
- Done: web sign-in cross-origin block fixed by app#110 (2026-10-29); weekly digest ran green on 2026-11-02.

## Product
- MCP server is live at `pilotless.nl/mcp` (GET returned 405, not 404). Follow-ups app#67 and app#69 are closed; app#68 and app#32 remain open.
- MCP Registry listing (`io.github.pilotless-studio/roadmap`, decision 0056) is active since 2026-10-25 (publish run 40175929861).
- Known minor: `POST /mcp` without an Accept json/event-stream header gets 406 before auth. `.eu`/`www` 301s send `no-cache` instead of `no-store` (small harness rule later).
- Pilot design-partner opt-in exists behind `pilot_optin_enabled` (app#49). Pilot price is never shown publicly; contact is double opt-in only.
- Roadmap feature (0049) is the app at [https://pilotless.nl/roadmap](https://pilotless.nl/roadmap) and [https://pilotless.nl/roadmap.md](https://pilotless.nl/roadmap.md). Firestore is the source of truth. This repository no longer stores or syncs a copy. Remaining this-loop work is still [pilotless#37](https://github.com/pilotless-studio/pilotless/issues/37) (open).
- 0046 hold on `/` → `/new` swap still stands.

## Workflows (2026-10-28)
- `app` weekly digest 2026-10-26 ([run 40335760268](https://github.com/pilotless-studio/app/actions/runs/40335760268)) failed: curl exit 28, the POST to `/gh/admin/digest` hit its 280 s timeout. The dogfood digest issues were still updated at 14:01 UTC, so posting worked but the call did not return in time (likely the second installation adding time). Fix before the next Monday run (2026-11-02).
- app#90 (fixes app#87, setup redirect to `pilotless.nl`) merged 2026-10-28 as b3240a7; deploy-web ran on it. app#91 (fixes app#88) conflicted after that and is being rebased; merge on green CI.
- `app` scoreboard run 40701401202 is this cycle's source for users, revenue, and cost.
- `pilotless` roadmap sync: removed (0055). Last failure before that was 2026-10-23 13:24 UTC ([run 39960922574](https://github.com/pilotless-studio/pilotless/actions/runs/39960922574)), GH006. A later dispatch ([run 39970392512](https://github.com/pilotless-studio/pilotless/actions/runs/39970392512)) committed `674309ee` and was still rejected after `tests` succeeded ([run 39970436530](https://github.com/pilotless-studio/pilotless/actions/runs/39970436530)). The workflow file is deleted. Do not re-enable it.
- `pilotless` weekly status directory: re-enabled 2026-10-23 after Pages source was switched to GitHub Actions (0055). Verification dispatch [run 39974928549](https://github.com/pilotless-studio/pilotless/actions/runs/39974928549) green, no commit to `main`.
- `harness` bunny-cdn-apply: green 2026-10-22 19:28 UTC (4 edge rules). Not re-checked for this edit.
- Digest dogfood issues (pilotless#23, app#7, harness#1) updated 2026-10-19..22.

## Gates (company start 2026-09-02)
- Day 14: MET 2026-09-04.
- Day 60, 2026-11-01: PASSED (0058), 17 -> 29 confirmed visitors.
- Day 90, 2026-12-01: OPEN; pivot-or-persist decided on the day from data.

## Next step
1. Land package 1 and switch the cycle's health checks to its summary.
2. Implement app#89 once copy is in.
3. Day-90 gate on 2026-12-01: registrations by channel, 30-day windows.

## Human-only blockers
- #29 founder posts for window 2 and #10 ads EUR 10 cap: open, no founder reply (no comments; last update 2026-10-15). Do not re-nag.
