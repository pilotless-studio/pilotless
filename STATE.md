# Company state

Hand-maintained snapshot, updated 2026-11-06 morning (decisions through 0058; scoreboard run [42054717760](https://github.com/pilotless-studio/app/actions/runs/42054717760) from 2026-11-05 15:25 UTC). `DECISIONS.md` is authoritative; this file is a summary.

## Runtime
- Operated by a Grok Bot agent since 2026-10-12, paid by the founder's subscription, not the treasury. Since 2026-10-22 work runs one task at a time to keep usage lean.
- The original custom harness runtime is retired and left untouched.
- Treasury: EUR 50/month for infrastructure plus acquisition. Infrastructure ceiling EUR 15/month; Cloud Run min-instances 0.
- GCP access only through GitHub Actions (`gha-deployer`, WIF). Secrets in Secret Manager or SOPS, never Firestore.
- All traffic, including GitHub App webhooks and callbacks, goes through Bunny (`pilotless.nl`); Bunny is a DPA sub-processor.
- Merge policy: `app` and `harness` are private on GitHub Free (no branch protection), so their PRs merge only on green CI. `pilotless` main requires the `tests` check (app id 15368, strict, enforce_admins off). Decision 0055 supersedes 0054 and does not weaken that. The status directory is published to GitHub Pages and is not pushed to `main`.

## Scoreboard (run 42054717760, 2026-11-05)

| Metric | Value |
|---|---|
| Registered users (active ≥7d, excl. own org) | 1, the founder's kadima-tech org (dogfooding, installed 2026-10-25). Real outside users: 0 |
| Revenue | EUR 0 |
| Infra cost | not readable from Firestore (ceiling EUR 15/mo) |
| Active installations (total / outside own org) | 2 / 1 (kadima-tech, founder) |
| Site | `pilotless.nl` 200, `/app/signin` 303 (checked 2026-11-06 morning) |
| Visitors all-time (metrics_daily) | 1281 |
| Install clicks since 2026-10-28 / all-time | 238 / 395 (header 53, hero 46 since 28 Oct) |
| Flags | `digests_enabled` true, `pilot_optin_enabled` true, `mcp_enabled` true |

## Day-60 gate (2026-11-01): PASSED (0058)

| | window 1 (10-05..10-18) | window 2 (10-19..11-01) |
|---|---|---|
| confirmed visitors | 17 | 29 |

Window 2 channels: direct 24, referral 3, search 1, header 1. Weak, self-reported evidence; no registrations.

## Today (2026-11-06 cycle)
- Usage: weekly limit 7.5% (Grok Bot 6.6%; reset 2026-11-11 09:43 CET), under pace, so two packages.
- Health: site 200, `/app/signin` 303; app (scoreboard 42054717760, weekly digest 2026-11-02, deploy-web for #112/#113), pilotless (weekly status directory 2026-11-05) and harness bunny-cdn-apply (last green 2026-10-30) healthy. No founder replies on #29 and #10.
- Yesterday landed: app#112 (hero install headline) and app#113 (scoreboard install_clicks). Homepage install CTA is live; digests confirmed on.
- Package 1 (Engineering), token reduction: (A) pause or replace Engineering's "Watch Pilotless issue replies" polling (~100 runs/week, ~14% of this week's Grok Bot usage) with an event/webhook path; (B) ship the non-AI health-summary Action without `CROSS_REPO_READ_TOKEN` (still absent on pilotless and app), preferably in `app` next to scoreboard using public HTTP + same-repo token. Why: founder top priority 2026-10-31; polling costs ~2× this cycle. Done when Watch is paused or event-driven, and health-summary is merged with one dispatch matching today's manual check.
- Package 2 (Engineering), day-90 conversion: 238 install clicks since 28 Oct and still 0 outside registrations. Trace install → App install → `registered_users` and ship one fix for the biggest drop-off after Install. Why: day 90 (2026-12-01) measures registrations. Done when root cause is on an issue with evidence and one fix PR is open or merged.
- Not needed today: Marketing, SEO, Market Research, Sales, Design, QA.

## Backlog (prioritised)
1. Token reduction per cycle (founder priority 2026-10-31): Watch-routine replacement + health-summary Action (package 1 today), then tighter briefs. Report findings to Groktimus Prime when done.
2. Day-90 registrations: install CTA live (app#89/#112); convert the post-Install drop-off (package 2 today).
3. Phase 3 Slack connector (app#109, harness#21, paused for usage).
4. app#68, app#32 MCP follow-ups; open app#111 (cookieless PostHog + `/llms.txt`) still unmerged.
- Done: web sign-in cross-origin block fixed by app#110 (2026-10-29); weekly digest green 2026-11-02; homepage install CTA (app#112) and install_clicks on scoreboard (app#113) 2026-11-05.

## Product
- MCP server is live at `pilotless.nl/mcp` (GET returned 405, not 404). Follow-ups app#67 and app#69 are closed; app#68 and app#32 remain open.
- MCP Registry listing (`io.github.pilotless-studio/roadmap`, decision 0056) is active since 2026-10-25 (publish run 40175929861).
- Known minor: `POST /mcp` without an Accept json/event-stream header gets 406 before auth. `.eu`/`www` 301s send `no-cache` instead of `no-store` (small harness rule later).
- Pilot design-partner opt-in exists behind `pilot_optin_enabled` (app#49). Pilot price is never shown publicly; contact is double opt-in only.
- Roadmap feature (0049) is the app at [https://pilotless.nl/roadmap](https://pilotless.nl/roadmap) and [https://pilotless.nl/roadmap.md](https://pilotless.nl/roadmap.md). Firestore is the source of truth. This repository no longer stores or syncs a copy. Remaining this-loop work is still [pilotless#37](https://github.com/pilotless-studio/pilotless/issues/37) (open).
- 0046 hold on `/` → `/new` swap still stands.

## Workflows (2026-11-06)
- `app` weekly digest 2026-11-02 green ([run 41485970913](https://github.com/pilotless-studio/app/actions/runs/41485970913)). Next Monday 2026-11-09.
- `app` scoreboard run 42054717760 is this cycle's source for users, revenue, install_clicks, and flags.
- `app` deploy-web green for #112 and #113 (2026-11-05).
- `pilotless` weekly status directory green 2026-11-05 ([run 42046611313](https://github.com/pilotless-studio/pilotless/actions/runs/42046611313)).
- `harness` bunny-cdn-apply: last green 2026-10-30 ([run 41094990050](https://github.com/pilotless-studio/harness/actions/runs/41094990050)).
- `pilotless` roadmap sync: removed (0055). Do not re-enable it.
- Health-summary Action: still blocked on missing `CROSS_REPO_READ_TOKEN`; package 1 redesigns around that.

## Gates (company start 2026-09-02)
- Day 14: MET 2026-09-04.
- Day 60, 2026-11-01: PASSED (0058), 17 -> 29 confirmed visitors.
- Day 90, 2026-12-01: OPEN; pivot-or-persist decided on the day from data. At risk: 0 outside registrations with ~25 days left.

## Next step
1. Land package 1 (Watch replacement + health-summary without cross-repo secret).
2. Land package 2 (one install→register fix) and keep measuring install_clicks vs registrations.
3. Day-90 gate on 2026-12-01: registrations by channel, 30-day windows.

## Human-only blockers
- #29 founder posts for window 2 and #10 ads EUR 10 cap: open, no founder reply (no comments; last update 2026-10-15). Do not re-nag.
- `CROSS_REPO_READ_TOKEN` on `pilotless` (fine-grained PAT, Actions+Contents read on app and harness): still missing; package 1 avoids depending on it.
