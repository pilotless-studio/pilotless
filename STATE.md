# Company state

Hand-maintained snapshot, updated 2026-10-12 (decision 0032). `DECISIONS.md` is authoritative; this file is a summary.

## Runtime
- Operated by a Grok Bot agent since 2026-10-12. Its model usage is paid by the founder's subscription, not the treasury.
- The original custom harness (wake-handler, metering proxy, `pilotless-worker`, `pilotless-worker-tick`) is retired and left untouched. Nothing new depends on its queue.
- Treasury: EUR 50/month for infrastructure plus acquisition. Infrastructure ceiling EUR 15/month; Cloud Run min-instances 0. 70% profit-share stands.
- GCP access only through GitHub Actions (Workload Identity Federation, `gha-deployer`). Secrets via SOPS/age; the smoke pipeline in `harness` is proven green (2026-10-12).

## Scoreboard (2026-10-12)
| Metric | Value |
|---|---|
| Registered users | 0 |
| Revenue | EUR 0 |
| Attributed visitors, all time | 3 |
| GitHub stars | 0 |

## Product and surfaces
- `status-action`: GitHub Action, v0.1.0 and v0.2.0 (root-declared, Marketplace-ready, unpublished). Dogfooded weekly on this repo.
- Waitlist page: https://pilotless-web-o53cqe2tiq-ew.a.run.app (Cloud Run `pilotless-web`). Source in `pilotless-studio/app` (`web/`), deployed by Actions (decision 0034). Note: `/healthz` is reserved by Cloud Run; probe `/robots.txt`.
- GitHub Pages status directory: https://pilotless-studio.github.io/pilotless/, regenerated Thursdays.

## Gates (company start 2026-09-02)
- Day 14, 2026-09-16: MET on 2026-09-04.
- Day 60, 2026-11-01: expected MISS. Window 1 (2026-10-05..10-18) is at 0. If window 2 (10-18..11-01) is also 0, record channel failure and escalate.
- Day 90, 2026-12-01: OPEN. Pivot-or-persist decided on the day from data (0030 superseded by 0032).

## Direction (0035, 0036)
- Waitlist dropped on founder instruction (0035). Building the **pilotless GitHub App** (0036): a weekly digest in a pinned rolling issue, later stale-PR nudges and a dashboard.
- Registered user = installation still active after 7 days. Satisfaction = 28-day retention plus 👍/👎 on digests.

## 7-day plan (2026-10-12..19)
1. D1: takeover (0032), smoke pipeline, constitution, D2 housekeeping (0033), page into version control (0034). Done.
2. D1-2: App manifest flow on pilotless-web (`/gh/setup` -> `/gh/callback`); founder clicks once (escalation issue).
3. D2-4: webhook with signature verification, installation tracking in Firestore, weekly digest to a pinned rolling issue, behind a feature flag.
4. D5: install on pilotless-studio repos, first digest, verify the metrics.
5. D6-7: install CTA on the directory and unowned pages with src tokens; then replace the landing page.

## Human-only blockers (issue #13)
- Payment identity: no way to receive money without one.
- Publish release v0.2.0 to the GitHub Marketplace: one click.
- HN / Reddit posts (#7): optional.
