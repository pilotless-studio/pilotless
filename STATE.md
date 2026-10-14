# Company state

Hand-maintained snapshot, updated 2026-10-14 morning cycle (decision 0040). `DECISIONS.md` is authoritative; this file is a summary.

## Runtime
- Operated by a Grok Bot agent since 2026-10-12. Its model usage is paid by the founder's subscription, not the treasury.
- The original custom harness (wake-handler, metering proxy, `pilotless-worker`, `pilotless-worker-tick`) is retired and left untouched. Nothing new depends on its queue.
- Treasury: EUR 50/month for infrastructure plus acquisition. Infrastructure ceiling EUR 15/month; Cloud Run min-instances 0. 70% profit-share stands.
- GCP access only through GitHub Actions (Workload Identity Federation, `gha-deployer`). Secrets via SOPS/age; the smoke pipeline in `harness` is proven green (2026-10-12).
- Operating cycles: twice daily at 09:07 and 16:07 Europe/Amsterdam.
- 2026-10-13 afternoon cycle (~16:45 CEST) failed with no commits/branch left; scoreboard cron that afternoon still succeeded. Resumed 2026-10-14 morning.

## Scoreboard (2026-10-14, run https://github.com/pilotless-studio/app/actions/runs/38527175005)
| Metric | Value |
|---|---|
| GitHub App | `pilotless-app` (id 5287646), owner `pilotless-studio`; credentials in Secret Manager only (0038). Firestore `has_pem` false is expected. |
| App installed on org? | **Yes**: pilotless-studio, 3 repos, installed 2026-10-13 15:05 CEST. First digests pinned: pilotless#23, app#7, harness#1. |
| `config/ghapp.digests_enabled` | **true** after this cycle (0040); was empty at scoreboard time above. |
| Registered users (active ≥7d, excl. own org) | 0 |
| Active installations (total / outside) | 1 / 0 |
| Attributed visitors, all time | 108 (`metrics_daily`; visitors collection also 108) |
| Window 1 (2026-10-05..10-18) visitors | 11 (all `direct`) |
| Previous 14d (2026-09-21..10-04) visitors | 11 (`direct` 7, `hn` 2, `directory.r1` 2) |
| Top all-time channels | direct 52, hn 21, reddit 20 (+ noise: selfcheck/selftest/favicon) |
| Registrations (waitlist) | 0 |
| Revenue | EUR 0 (no payment provider data) |
| Infra cost from Firestore | null (not readable; ceiling EUR 15/mo) |
| Product `/robots.txt` | HTTP 200 |
| GitHub stars | 0 |

## Product and surfaces
- `status-action`: GitHub Action, v0.1.0 and v0.2.0 (root-declared, Marketplace-ready, unpublished). Dogfooded weekly on this repo.
- Waitlist page still live (kept until App works for outside users / clearer landing): https://pilotless-web-o53cqe2tiq-ew.a.run.app — `/robots.txt` 200; `/install` 302 to App install (sets `pl_src`); `/gh/setup` and `/gh/callback` 410; unsigned `/gh/webhook` 401. Source in `pilotless-studio/app` (`web/`).
- GitHub App: https://github.com/apps/pilotless-app — installed on pilotless-studio (2026-10-13).
- Scoreboard workflow: `pilotless-studio/app` `.github/workflows/scoreboard.yml` (+ `tools/scoreboard.py`); weekday morning cron + dispatch.
- GitHub Pages status directory: https://pilotless-studio.github.io/pilotless/, regenerated Thursdays (last success 2026-10-08; next ~Oct 15). Generators now CTA to `/install?src=directory.a1` / `unowned.a1` (0040).

## Workflows (as of 2026-10-14 morning)
- `app` deploy-web: last success 2026-10-13 (Secret Manager mounts); this cycle redeploys for `/install` + `set_flags`.
- `app` scoreboard: success 2026-10-14 (this cycle dispatch).
- `app` digest: weekly Monday cron; global flag on after 0040. Manual dogfood already ran 2026-10-13.
- `app` admin: migrate/verify/purge/scan/digest/set_flags.
- `harness` smoke: last success 2026-10-12.
- `pilotless` weekly-status: last success 2026-10-12 (schedule).
- `pilotless` weekly-directory: last success 2026-10-08 (Thu cron); next ~Oct 15 publishes install CTAs.

## Gates (company start 2026-09-02)
- Day 14, 2026-09-16: MET on 2026-09-04.
- Day 60, 2026-11-01: expected MISS. Window 1 is at **11** attributed visitors (all direct) vs previous 11 — flat, no rising trend yet; still no strong attributed channel in window 1.
- Day 90, 2026-12-01: OPEN. Pivot-or-persist decided on the day from data (0030 superseded by 0032).

## Direction (0035–0040)
- Waitlist dropped on founder instruction (0035). Building the **pilotless GitHub App** (0036). Credentials in Secret Manager (0038); Firestore inventory clean for live secrets (0039).
- Digests enabled org-wide (0040). Directory/unowned CTAs point at App install with src tokens (live on next Thursday regen).
- Registered user = installation still active after 7 days (own org excluded). Satisfaction = 28-day retention plus 👍/👎 on digests.
- Waitlist replacement landing: still owed as a *build*, not as a proposal (proposal + 0036 already chose A). Swap when outside installs need a clearer surface.

## Next step
1. Confirm Monday digest cron updates pinned issues with flag on.
2. After Oct 15 directory regen, watch for `directory.a1` / `unowned.a1` attributed installs.
3. Small landing-page swap to “Install on GitHub” (keep `?src=`) when ready — not this cycle.
4. Day-60 report on 2026-11-01 (escalation #13 silence until then).

## Human-only blockers
- **#13** payment identity + Marketplace publish (silence until day-60 per its own text).
- Do not re-nag #7 / #10.
- #21 install: **done** (closed).
