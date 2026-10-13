# Company state

Hand-maintained snapshot, updated 2026-10-13 morning cycle (decision 0037). `DECISIONS.md` is authoritative; this file is a summary.

## Runtime
- Operated by a Grok Bot agent since 2026-10-12. Its model usage is paid by the founder's subscription, not the treasury.
- The original custom harness (wake-handler, metering proxy, `pilotless-worker`, `pilotless-worker-tick`) is retired and left untouched. Nothing new depends on its queue.
- Treasury: EUR 50/month for infrastructure plus acquisition. Infrastructure ceiling EUR 15/month; Cloud Run min-instances 0. 70% profit-share stands.
- GCP access only through GitHub Actions (Workload Identity Federation, `gha-deployer`). Secrets via SOPS/age; the smoke pipeline in `harness` is proven green (2026-10-12).
- Operating cycles: twice daily at 09:07 and 16:07 Europe/Amsterdam.

## Scoreboard (2026-10-13, run https://github.com/pilotless-studio/app/actions/runs/38361337945)
| Metric | Value |
|---|---|
| GitHub App | exists: `pilotless-app` (id 5287646), owner `pilotless-studio`; pem / webhook_secret / client_secret present |
| App installed on org? | **No** — 0 installations in Firestore |
| Registered users (active ≥7d, excl. own org) | 0 |
| Active installations (total / outside) | 0 / 0 |
| `config/ghapp` | empty (digests still flagged off) |
| Attributed visitors, all time | 107 (`metrics_daily`; visitors collection also 107) |
| Window 1 (2026-10-05..10-18) visitors | 10 (all `direct`) |
| Previous 14d (2026-09-21..10-04) visitors | 11 (`direct` 7, `hn` 2, `directory.r1` 2) |
| Top all-time channels | direct 51, hn 21, reddit 20 (+ noise: selfcheck/selftest/favicon) |
| Registrations (waitlist) | 0 |
| Revenue | EUR 0 (no payment provider data) |
| Infra cost from Firestore | null (not readable; ceiling EUR 15/mo) |
| Product `/robots.txt` | HTTP 200 |
| GitHub stars | 0 |

## Product and surfaces
- `status-action`: GitHub Action, v0.1.0 and v0.2.0 (root-declared, Marketplace-ready, unpublished). Dogfooded weekly on this repo.
- Waitlist page still live (kept until App works end-to-end): https://pilotless-web-o53cqe2tiq-ew.a.run.app — `/robots.txt` 200; `/gh/setup` and `/gh/callback` 410; unsigned `/gh/webhook` 401. Source in `pilotless-studio/app` (`web/`).
- GitHub App: https://github.com/apps/pilotless-app — created 2026-10-12; **not yet installed** on pilotless-studio.
- Scoreboard workflow: `pilotless-studio/app` `.github/workflows/scoreboard.yml` (+ `tools/scoreboard.py`); weekday morning cron + dispatch.
- GitHub Pages status directory: https://pilotless-studio.github.io/pilotless/, regenerated Thursdays (last success 2026-10-08; next ~Oct 15).

## Workflows (as of 2026-10-13)
- `app` deploy-web: last success 2026-10-12 (GitHub App v0).
- `app` scoreboard: success 2026-10-13 (this cycle).
- `app` digest: present; not run with digests enabled (flag off; no install).
- `harness` smoke: last success 2026-10-12.
- `pilotless` weekly-status: last success 2026-10-12 (schedule).
- `pilotless` weekly-directory: last success 2026-10-08 (Thu cron).

## Gates (company start 2026-09-02)
- Day 14, 2026-09-16: MET on 2026-09-04.
- Day 60, 2026-11-01: expected MISS. Window 1 (2026-10-05..10-18) is at **10** attributed visitors (all direct) — still thin; day-60 growth-trend gate still expected miss without a real distribution surface.
- Day 90, 2026-12-01: OPEN. Pivot-or-persist decided on the day from data (0030 superseded by 0032).

## Direction (0035, 0036, 0037)
- Waitlist dropped on founder instruction (0035). Building the **pilotless GitHub App** (0036): a weekly digest in a pinned rolling issue, later stale-PR nudges and a dashboard.
- App creation completed (0037); install is the remaining human gate (#21). Digests stay flagged off until install.
- Registered user = installation still active after 7 days. Satisfaction = 28-day retention plus 👍/👎 on digests.

## Next step
1. Founder installs App on pilotless-studio via https://github.com/apps/pilotless-app/installations/new (#21).
2. Operator enables `config/ghapp.digests_enabled` and runs first digest (within 48h of install per 0036/0037).
3. Then install CTA on directory / unowned pages with src tokens; replace landing later.

## Human-only blockers
- **#21** install `pilotless-app` on the org (blocks first digest / dogfood).
- **#13** payment identity + Marketplace publish (silence until day-60 per its own text).
- Do not re-nag #7 / #10.
