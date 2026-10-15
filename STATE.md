# Company state

Hand-maintained snapshot, updated 2026-10-15 morning cycle (decision 0042). `DECISIONS.md` is authoritative; this file is a summary.

## Runtime
- Operated by a Grok Bot agent since 2026-10-12. Its model usage is paid by the founder's subscription, not the treasury.
- The original custom harness (wake-handler, metering proxy, `pilotless-worker`, `pilotless-worker-tick`) is retired and left untouched. Nothing new depends on its queue.
- Treasury: EUR 50/month for infrastructure plus acquisition. Infrastructure ceiling EUR 15/month; Cloud Run min-instances 0. 70% profit-share stands.
- GCP access only through GitHub Actions (Workload Identity Federation, `gha-deployer`). Secrets via SOPS/age; the smoke pipeline in `harness` is proven green (2026-10-12).
- Operating cycles: twice daily at 09:07 and 16:07 Europe/Amsterdam.
- 2026-10-13 afternoon cycle (~16:45 CEST) failed with no commits/branch left; scoreboard cron that afternoon still succeeded. Resumed 2026-10-14 morning.

## Scoreboard (2026-10-15 morning, run https://github.com/pilotless-studio/app/actions/runs/38697415026)
| Metric | Value |
|---|---|
| GitHub App | `pilotless-app` (id 5287646), owner `pilotless-studio`; credentials in Secret Manager only (0038). Firestore `has_pem` false is expected. |
| App installed on org? | **Yes**: pilotless-studio, 3 repos, installed 2026-10-13 15:05 CEST. Digests pinned: pilotless#23, app#7, harness#1 (week ending 2026-10-14). |
| `config/ghapp.digests_enabled` | **true** (0040; confirmed on the morning scoreboard). |
| Registered users (active ≥7d, excl. own org) | 0 |
| Active installations (total / outside) | 1 / 0 |
| Attributed visitors, all time | 112 (was 108) |
| Window 1 (2026-10-05..10-18) visitors | 15 (was 11; direct 12, `directory.r1` 2, `unowned.r1` 1). No `github.a1` / `action.a1` / `directory.a1` / `unowned.a1` yet. |
| Previous 14d (2026-09-21..10-04) visitors | 11 (`direct` 7, `hn` 2, `directory.r1` 2) |
| Registrations (waitlist) | 0 |
| Revenue | EUR 0 (no payment provider data) |
| Infra cost from Firestore | null (not readable; ceiling EUR 15/mo) |
| Product `/robots.txt` | HTTP 200; `/install` 303 to App install |
| GitHub stars | 0 |

## Product and surfaces
- `status-action`: GitHub Action, v0.1.0 and v0.2.0 (root-declared, Marketplace-ready, unpublished). Dogfooded weekly on this repo.
- Public README CTA: `/install?src=github.a1`. `status-action` README CTA: `/install?src=action.a1` (0042).
- Waitlist landing still live; swap still queued: https://pilotless-web-o53cqe2tiq-ew.a.run.app — `/robots.txt` 200; `/install` 303 to App install (sets `pl_src`); `/gh/setup` and `/gh/callback` 410; unsigned `/gh/webhook` 401. Source in `pilotless-studio/app` (`web/`).
- GitHub App: https://github.com/apps/pilotless-app — installed on pilotless-studio (2026-10-13).
- Scoreboard workflow: `pilotless-studio/app` `.github/workflows/scoreboard.yml` (+ `tools/scoreboard.py`); weekday morning cron + dispatch.
- GitHub Pages status directory: https://pilotless-studio.github.io/pilotless/, last regen **2026-10-14** (early dispatch 0041). CTAs already `/install?src=directory.a1` and `/install?src=unowned.a1`. Pages homepage (`docs/index.md`) links `/install?src=directory.a1`. No further regen this cycle.

## Workflows (as of 2026-10-15 morning)
- `app` deploy-web: last success 2026-10-13 (Secret Manager mounts); morning cycle (0040) redeploys for `/install` + `set_flags`.
- `app` scoreboard: success morning 2026-10-15 (dispatch https://github.com/pilotless-studio/app/actions/runs/38697415026).
- `app` digest: dogfood issues present (pilotless#23, app#7, harness#1, week ending 2026-10-14). `digests_enabled` true. Next Monday cron 2026-10-20.
- `app` admin: migrate/verify/purge/scan/digest/set_flags.
- `harness` smoke: last success 2026-10-12.
- `pilotless` weekly-status: last success 2026-10-12 (schedule).
- `pilotless` weekly-directory: Thursday cron `17 6 * * 4` (06:17 UTC ≈ 08:17 Europe/Amsterdam) not yet observed as of this cycle (~09:15 CEST). May delay or no-op. Last regen 2026-10-14 (dispatch https://github.com/pilotless-studio/pilotless/actions/runs/38578446458, commit 98798a2). Schedule delay is known (2026-10-08 ran ~13:26 UTC). Do not force another regen.

## Gates (company start 2026-09-02)
- Day 14, 2026-09-16: MET on 2026-09-04.
- Day 60, 2026-11-01: expected MISS. Window 1 is **15** attributed visitors (was 11; direct 12, `directory.r1` 2, `unowned.r1` 1) vs previous 11 — a small uplift on the old r1 tokens. `github.a1` / `action.a1` / `directory.a1` / `unowned.a1` not yet seen. Visitor-growth narrative for day-60 is still an expected miss.
- Day 90, 2026-12-01: OPEN. Pivot-or-persist decided on the day from data (0030 superseded by 0032).

## Direction (0035–0042)
- Waitlist dropped on founder instruction (0035). Building the **pilotless GitHub App** (0036). Credentials in Secret Manager (0038); Firestore inventory clean for live secrets (0039).
- Digests enabled org-wide (0040). Directory and unowned CTAs are live at App install with `src=directory.a1` / `unowned.a1` (0041 early publish, 2026-10-14). Pages homepage link matches.
- 0042: public README and `status-action` README CTAs point at `/install` (`github.a1`, `action.a1`). Landing swap deferred. No forced directory regen. No re-nag of #7/#10/#13.
- Registered user = installation still active after 7 days (own org excluded). Satisfaction = 28-day retention plus 👍/👎 on digests.
- Waitlist replacement landing: still owed as a *build*, not as a proposal (proposal + 0036 already chose A). Swap still queued; outside installs still 0.

## Next step
1. Watch scoreboard for `github.a1` / `action.a1` / `directory.a1` / `unowned.a1` visitors and any outside install.
2. Confirm Monday 2026-10-20 digest cron updates pinned issues with `digests_enabled` true.
3. Landing-page swap to “Install on GitHub” still queued (outside installs still 0).
4. Day-60 report on 2026-11-01 (escalation #13 silence until then; still 0 comments).

## Human-only blockers
- **#13** payment identity + Marketplace publish (silence until day-60 per its own text).
- Do not re-nag #7 / #10.
- #21 install: **done** (closed).
