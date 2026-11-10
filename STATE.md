# Company state

Hand-maintained snapshot, updated 2026-11-10 morning (decisions through 0058; scoreboard artifact 13695628489 from run [42664508691](https://github.com/pilotless-studio/app/actions/runs/42664508691), 2026-11-09 17:26 UTC; health-summary scheduled run [42668366734](https://github.com/pilotless-studio/app/actions/runs/42668366734), 2026-11-09 17:49 UTC). `DECISIONS.md` is authoritative; this file is a summary.

## Runtime
- Operated by a Grok Bot agent since 2026-10-12, paid by the founder's subscription, not the treasury. Since 2026-10-22 work runs one task at a time to keep usage lean.
- The original custom harness runtime is retired and left untouched.
- Treasury: EUR 50/month for infrastructure plus acquisition. Infrastructure ceiling EUR 15/month; Cloud Run min-instances 0.
- GCP access only through GitHub Actions (`gha-deployer`, WIF). Secrets in Secret Manager or SOPS, never Firestore.
- All traffic, including GitHub App webhooks and callbacks, goes through Bunny (`pilotless.nl`); Bunny is a DPA sub-processor.
- Merge policy: `app` and `harness` are private on GitHub Free (no branch protection), so their PRs merge only on green CI. `pilotless` main requires the `tests` check (app id 15368, strict, enforce_admins off). Decision 0055 supersedes 0054 and does not weaken that. The status directory is published to GitHub Pages and is not pushed to `main`.

## Scoreboard (scoreboard run 42664508691, 2026-11-09 17:26 UTC)

| Metric | Value |
|---|---|
| Registered users (active ≥7d, excl. own org) | 1, the founder's kadima-tech org (dogfooding). Real outside users: 0 |
| Revenue | EUR 0 |
| Active installations (total / outside own org) | 2 / 1 (kadima-tech, founder, installed 2026-10-25); no new installation since |
| Site | `pilotless.nl` 200, `/app/signin` 303 (health-summary 2026-11-09) |
| Visitors all-time (metrics_daily) | 1530 (1333 on 2026-11-06), registrations 0 |
| Install clicks since 2026-10-28 / all-time | 290 / 447 (260 / 417 on 2026-11-06, so +30 under the human filter) |
| Setup returns since 2026-10-28 / all-time | 0 / 0 |
| Flags | `digests_enabled` true |

## Day-60 gate (2026-11-01): PASSED (0058)

| | window 1 (10-05..10-18) | window 2 (10-19..11-01) |
|---|---|---|
| confirmed visitors | 17 | 29 |

Window 2 channels: direct 24, referral 3, search 1, header 1. Weak, self-reported evidence; no registrations.

## Today (2026-11-10 cycle)
- Usage: weekly limit 1.9% (Grok Bot 1.3%; reset 2026-11-11 09:43 CET), far under pace. Cycles on 11-08 and 11-09 did not run.
- Health: health-summary now runs on schedule (first scheduled runs seen 11-07, 11-08, 11-09). Latest artifact ~15h old: site 200, signin 303, scheduled scoreboard/digest/admin success, weekly digest 2026-11-09 green, digests_enabled true, #10/#29 latest_non_bot null, harness skipped.
- Evidence change: +30 human-filtered install clicks since 11-06, still 0 setup returns and no new installation. Hypothesis (not proven): humans reach GitHub's install page and abandon, or the setup return is not recorded. The 11-07 package 1 has no PR or issue evidence yet.
- Package 1 (Engineering, re-handed): verify setup_returns end-to-end (a test install on an isolated test org or account ending on `/gh/installed?setup_action=install` increments the counter), then either fix the counter or report human click-to-GitHub numbers per day since 11-06 so Marketing can work on install-page comprehension. Done when evidence is on a new app issue and either a fix PR is open or a Marketing handoff is written. Effort medium, Fast off. QA verifies any counter fix on the exact SHA.
- Package 2 (CEO, done): STATE refresh and backlog entry for PR review.
- Roles: Engineering required; QA required only if a fix PR lands; Marketing consulted after Engineering evidence; Design and QA keep app#117 held (f1cbda9 NOT ACCEPTED / NO-GO, AC20 blocker); Market Research, Sales, SEO not applicable today (no new customer or discovery input).
- Retro: worked: scheduled health-summary removed per-cycle API reads. Failed: package 1 handoff produced no visible evidence in 3 days and two daily slots were missed. Improvement: Engineering posts package evidence on an app issue within its next session (owner Engineering, verify at the 11-11 cycle by issue link).

## Backlog (prioritised)
1. Day-90 registrations (package 1 today): after #114, prove whether humans finish GitHub install (setup_returns) and convert; then one fix or Marketing handoff.
2. Token reduction per cycle: health-summary + Watch pause done 2026-11-06; keep briefs tight; report further savings to Groktimus Prime.
3. Phase 3 Slack connector (app#109, harness#21, paused for usage).
4. app#68, app#32 MCP follow-ups.
5. Future, not urgent (Sjaak, 2026-11-07): PR review inside Pilotless for PRs that still need a human, with LLM triage (possibly Jev) deciding whether a PR needs human review at all; any automatic clearance must respect repository review rules. Overlaps with kadima-tech/autopilot Review & Merge; check reuse before building.
- Done: web sign-in cross-origin block (app#110); weekly digest green 2026-11-02; homepage install CTA (app#112); install_clicks scoreboard (app#113); human clicks + setup_returns (app#114); health-summary Action (app#115); cookieless PostHog + `/llms.txt` (app#111, 2026-11-07).

## Product
- MCP server is live at `pilotless.nl/mcp` (GET returned 405, not 404). Follow-ups app#67 and app#69 are closed; app#68 and app#32 remain open.
- MCP Registry listing (`io.github.pilotless-studio/roadmap`, decision 0056) is active since 2026-10-25 (publish run 40175929861).
- Known minor: `POST /mcp` without an Accept json/event-stream header gets 406 before auth. `.eu`/`www` 301s send `no-cache` instead of `no-store` (small harness rule later).
- Pilot design-partner opt-in exists behind `pilot_optin_enabled` (app#49). Pilot price is never shown publicly; contact is double opt-in only.
- Roadmap feature (0049) is the app at [https://pilotless.nl/roadmap](https://pilotless.nl/roadmap) and [https://pilotless.nl/roadmap.md](https://pilotless.nl/roadmap.md). Firestore is the source of truth. This repository no longer stores or syncs a copy. Remaining this-loop work is still [pilotless#37](https://github.com/pilotless-studio/pilotless/issues/37) (open).
- 0046 hold on `/` → `/new` swap still stands.
- Public site now loads cookieless PostHog pageviews (Kadima Websites project) and serves `/llms.txt` (app#111).

## Workflows (2026-11-07)
- `app` weekly digest 2026-11-02 green ([run 41485970913](https://github.com/pilotless-studio/app/actions/runs/41485970913)). Next Monday 2026-11-09.
- `app` scoreboard run 42238611508 is this cycle's source for users, revenue, install_clicks, setup_returns, and flags.
- `app` deploy-web green for #114/#115 (2026-11-06); #111 merge should trigger deploy-web.
- `pilotless` weekly status directory: last noted green 2026-11-05.
- `harness` bunny-cdn-apply: last green 2026-10-30 ([run 41094990050](https://github.com/pilotless-studio/harness/actions/runs/41094990050)).
- `pilotless` roadmap sync: removed (0055). Do not re-enable it.
- Health-summary Action: merged (app#115), scheduled runs observed daily since 2026-11-07. Use artifact first each cycle. No CROSS_REPO_READ_TOKEN wait.

## Gates (company start 2026-09-02)
- Day 14: MET 2026-09-04.
- Day 60, 2026-11-01: PASSED (0058), 17 -> 29 confirmed visitors.
- Day 90, 2026-12-01: OPEN; pivot-or-persist decided on the day from data. At risk: 0 outside registrations, 0 setup_returns, 21 days left.

## Next step
1. Land package 1 (setup_returns verify + one install-completion fix or Marketing handoff).
2. Confirm app#111 deploy-web green and `/llms.txt` live.
3. Day-90 gate on 2026-12-01: registrations by channel, 30-day windows.

## Human-only blockers
- #29 founder posts for window 2 and #10 ads EUR 10 cap: open, no founder reply (no comments; last update 2026-10-15). Do not re-nag.
- `CROSS_REPO_READ_TOKEN` is not required for health-summary; do not ask for it again for that path.
