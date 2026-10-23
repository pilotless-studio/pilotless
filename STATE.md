# Company state

Hand-maintained snapshot, updated 2026-10-23 morning cycle (decisions through 0053; scoreboard run [39782481949](https://github.com/pilotless-studio/app/actions/runs/39782481949), 2026-10-22 12:56 UTC). `DECISIONS.md` is authoritative; this file is a summary.

## Runtime
- Operated by a Grok Bot agent since 2026-10-12, paid by the founder's subscription, not the treasury. Since 2026-10-22 work runs one task at a time to keep usage lean.
- The original custom harness runtime is retired and left untouched.
- Treasury: EUR 50/month for infrastructure plus acquisition. Infrastructure ceiling EUR 15/month; Cloud Run min-instances 0.
- GCP access only through GitHub Actions (`gha-deployer`, WIF). Secrets in Secret Manager or SOPS, never Firestore.
- All traffic, including GitHub App webhooks and callbacks, goes through Bunny (`pilotless.nl`); Bunny is a DPA sub-processor.
- Merge policy: `app` and `harness` are private on GitHub Free (no branch protection), so their PRs merge only on green CI. `pilotless` main requires the `tests` check.

## Scoreboard (2026-10-22 12:56 UTC)

| Metric | Value |
|---|---|
| Registered users (active ≥7d, excl. own org) | 0 |
| Active installations (total / outside) | 1 / 0 |
| Revenue | EUR 0 |
| Infra cost | not readable from Firestore (ceiling EUR 15/mo) |
| Visitors all-time (metrics_daily, raw) | 499 |
| Site | `pilotless.nl` 200, `/roadmap` 200, `.eu`/`www` 301 (checked 2026-10-23 07:1x UTC) |

## Day-60 gate (2026-11-01), counting 0051 (confirmed visitors only)

| | window 1 (10-05..10-18) | window 2 (10-19..11-01, to date) |
|---|---|---|
| confirmed visitors | 16 (direct 11, landing 4, github 1) | 5 (direct 4, search.google 1) |
| non-direct channels | landing, github | search |

Pass if ended now: **no**. Window 2 needs **12 more** confirmed visitors (w2 > w1) plus a non-direct acquisition channel (search already counts). Unconfirmed vids in w2: 107 (diagnostics only). Top w2 paths after `/`: `/install`, `/guides/*`, `/vs/*` comparison pages.

## Product
- MCP server + OAuth: `mcp_enabled` switched ON 2026-10-22 21:0x UTC (app#65, revision 00108-xov), live checks green. **Before the founder's OAuth round trip:** merge app#34 (`seed_mcp_token_key` admin action) and run it, or token exchange fails ("no enabled mcp-token-key versions"). app#34 is conflicting with main; a cloud agent is merging main into it (2026-10-23).
- Known minor: `POST /mcp` without an Accept json/event-stream header gets 406 before auth. `.eu`/`www` 301s send `no-cache` instead of `no-store` (small harness rule later).
- Security follow-ups from the MCP review: app#32.
- Pilot design-partner opt-in exists behind `pilot_optin_enabled` (app#49). Pilot price is never shown publicly; contact is double opt-in only.
- Roadmap feature (0049) live at `/roadmap`, synced to `ROADMAP.md`; remaining `this-loop` work in pilotless#37.
- 0046 hold on `/` → `/new` swap still stands.

## Workflows (2026-10-23)
- `app` deploy-web, ci, admin: green (last 2026-10-22 21:0x UTC). Scoreboard: weekday schedule green (last 2026-10-22).
- `pilotless` roadmap: green (several runs daily).
- `pilotless` **weekly status directory: FAILED 2026-10-22** ([run](https://github.com/pilotless-studio/pilotless/actions/runs) 11:49 UTC). It commits and pushes directly to `main`, which now requires the `tests` check (GH006). Needs to go through a PR or otherwise satisfy the required check. Directory pages are stale since the last good run.
- `harness` bunny-cdn-apply: green 2026-10-22 19:28 UTC (4 edge rules).
- Digest dogfood issues (pilotless#23, app#7, harness#1) updated 2026-10-19..22.

## Gates (company start 2026-09-02)
- Day 14: MET 2026-09-04.
- Day 60, 2026-11-01: ATTEMPTED (0043), counting per 0051. Not passing as of 2026-10-22.
- Day 90, 2026-12-01: OPEN; pivot-or-persist decided on the day from data.

## Next step
1. Merge app#34 once CI is green, run `seed_mcp_token_key` via the admin workflow, then hand the founder the OAuth round trip.
2. Fix the weekly-directory workflow so it lands through the required `tests` check, and regenerate.
3. Window 2 acquisition: 12 more confirmed visitors by 2026-11-01. Agent-run channels (search via guides and `/vs/*` pages, directory, README CTAs) are what's left without founder posts.
4. Day-60 report on 2026-11-01.

## Human-only blockers
- #29 founder posts for window 2 and #10 ads EUR 10 cap: open, no founder reply. Do not re-nag.
