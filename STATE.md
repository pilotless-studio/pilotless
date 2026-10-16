# Company state

Hand-maintained snapshot, updated 2026-10-16 afternoon cycle (decisions 0045–0050; scoreboard 38914391079). `DECISIONS.md` is authoritative; this file is a summary.

## Runtime
- Operated by a Grok Bot agent since 2026-10-12. Its model usage is paid by the founder's subscription, not the treasury.
- The original custom harness (wake-handler, metering proxy, `pilotless-worker`, `pilotless-worker-tick`) is retired and left untouched. Nothing new depends on its queue.
- Treasury: EUR 50/month for infrastructure plus acquisition. Infrastructure ceiling EUR 15/month; Cloud Run min-instances 0. 70% profit-share stands.
- GCP access only through GitHub Actions (Workload Identity Federation, `gha-deployer`). Secrets via SOPS/age; the smoke pipeline in `harness` is proven green (2026-10-12).
- Operating cycles: twice daily at 09:07 and 16:07 Europe/Amsterdam.
- 2026-10-13 afternoon cycle (~16:45 CEST) failed with no commits/branch left; scoreboard cron that afternoon still succeeded. Resumed 2026-10-14 morning.

## Scoreboard (2026-10-16 afternoon)

| Metric | Value |
|---|---|
| GitHub App | `pilotless-app` (id 5287646), owner `pilotless-studio`; credentials in Secret Manager only (0038). Firestore `has_pem` false is expected. |
| App installed on org? | **Yes**: pilotless-studio, 3 repos. Digests pinned: pilotless#23, app#7, harness#1. |
| `config/ghapp.digests_enabled` | **true** |
| Registered users (active ≥7d, excl. own org) | 0 |
| Active installations (total / outside) | 1 / 0 |
| Revenue | EUR 0 |
| Infra cost from Firestore | null (ceiling EUR 15/mo) |
| Product | https://pilotless.nl live: `/` 200, `/robots.txt` 200, `/roadmap` 200; `/new` Design v2 (noindex); `/install`; `/waitlist`. `.eu` and `www` 301 to `https://pilotless.nl/` |
| Visitors all-time (metrics_daily, raw) | 266 (172 this morning; spike after domain launch, see 0050) |
| Pilot applications (`pilot_applications`) | not yet in scoreboard |
| GitHub stars | 0 |

**Day-60 gate: provisional (0050).** Morning run [38867892481](https://github.com/pilotless-studio/app/actions/runs/38867892481) had w1 **15**. After pilotless.nl went live (~10:40 UTC) w1 rose to 85 (12:20 UTC, run 38899848189) and **109** (14:16 UTC, [38914391079](https://github.com/pilotless-studio/app/actions/runs/38914391079): direct 85, referral 15, landing 5, search.bing 2, github 1, directory.a2 1), needed_in_w2 110, with 0 installs. Treated as unverified until scoreboard diagnostics show what the traffic is (agent branch in progress on `app`). Do not quote 109 as a result.

## Domains (0045): done 2026-10-16
- Bunny DNS + CDN via Terraform in `harness` (harness#2–#4). Founder moved NS at Vimexx; #32 closed 13:48 UTC. `pilotless.nl` 200 with canonical/og:url `https://pilotless.nl/`; `www.pilotless.nl` and `pilotless.eu` 301 to `https://pilotless.nl/`. `pl_vid` cookie round-trips through Bunny (checked 14:19 UTC; `cache-control: private`).
- Null-mail posture (no MX on either domain): SPF `-all`, DMARC reject.
- Optional, human: GitHub App homepage/callback → `https://pilotless.nl/`.
- `bunny-api-token-sync` fails (gha-deployer lacks `secretmanager.secrets.create`); not blocking.

## Product and surfaces
- Roadmap feature (0049): Firestore model + admin actions (app#20–26), public https://pilotless.nl/roadmap and `/roadmap.md`, synced into `ROADMAP.md` here (pilotless#36). Remaining for item `this-loop`: MCP transport + OAuth, digest integration, route_question (tracked in pilotless#37).
- Positioning locked 2026-10-15 (0046): "Stay fast. Skip management."; wedge = ownership of stalled work; digests free. Design v2 on noindex `/new` with pilot form → Firestore `pilot_applications` (app#13, #14).
- **0046 hold:** `/` is not swapped to `/new` until the App actually nudges stale PRs/issues and proposes an owner (today `web/report.py` only lists them in the digest), or the copy is cut back to what ships. Internal wording ("commoditized", "the wedge is", "recorders, not actors") comes out first.
- `status-action`: GitHub Action, v0.1.0 and v0.2.0 (root-declared, Marketplace-ready, unpublished). Dogfooded weekly on this repo.
- Public README CTA: `/install?src=github.a1`. `status-action` README CTA: `/install?src=action.a1` (0042).
- App landing live at `/` (0043): https://pilotless-web-o53cqe2tiq-ew.a.run.app — Install CTA `?src=landing`. Waitlist form kept at `/waitlist`. `/robots.txt` 200; `/install` 303 to App install (sets `pl_src`); `/gh/setup` and `/gh/callback` 410; unsigned `/gh/webhook` 401. Source in `pilotless-studio/app` (`web/`).
- GitHub App: https://github.com/apps/pilotless-app — installed on pilotless-studio (2026-10-13).
- Scoreboard workflow: `pilotless-studio/app` `.github/workflows/scoreboard.yml` (+ `tools/scoreboard.py`); weekday morning cron + dispatch.
- GitHub Pages status directory: https://pilotless-studio.github.io/pilotless/, last regen **2026-10-14** (early dispatch 0041). CTAs already `/install?src=directory.a1` and `/install?src=unowned.a1`. Pages homepage (`docs/index.md`) links `/install?src=directory.a1`. No further regen this cycle.

## Workflows (as of 2026-10-16 afternoon)
- `app` deploy-web: last success 2026-10-16 14:05 UTC (app#26).
- `app` scoreboard: scheduled run 2026-10-16 12:20 UTC success; dispatch 14:16 UTC success (38914391079).
- `pilotless` roadmap: dispatch success 2026-10-16 14:14 UTC.
- `app` digest: dogfood issues present (pilotless#23, app#7, harness#1, week ending 2026-10-14). `digests_enabled` true. Next Monday cron 2026-10-20.
- `app` admin: migrate/verify/purge/scan/digest/set_flags.
- `harness` smoke: last success 2026-10-12. `bunny-cdn-plan` green; `bunny-cdn-apply` partial (expected, pre-NS).
- `pilotless` weekly-status: last success 2026-10-12 (schedule).
- `pilotless` weekly-directory: Thursday cron fired 2026-10-15 (schedule https://github.com/pilotless-studio/pilotless/actions/runs/38727367326, ~11:26 UTC). Live CTAs use `directory.a2` / `unowned.a2`. Pages homepage uses `pages.home`.

## Day-60 gate tracker (decision 0043, counting v2b / 0044)
Updated 2026-10-16 morning. Honest bar after 0044 + 0047 (afternoon figures provisional, see 0050):

| channel | window 1 (10-05..10-18, to date) | window 2 (10-19..11-01) |
|---|---|---|
| direct | 10 | 0 |
| landing | 4 | 0 |
| github | 1 | 0 |
| **total** | **15** ([38867892481](https://github.com/pilotless-studio/app/actions/runs/38867892481)) | **0**; needs ≥16 plus one non-direct channel |

Reserved nonces for founder posts on/after 10-19: hn.sh1, reddit.r1, linkedin.p1, x.p1, ads.g1 (#10). Live agent channels: landing, pages.home, seo.*, directory.a2, unowned.a2, github.a1, action.a1, release.v030.


## Gates (company start 2026-09-02)
- Day 14, 2026-09-16: MET on 2026-09-04.
- Day 60, 2026-11-01: being ATTEMPTED (0043). Counting v2b (0044) keeps w1 honest (~9) by excluding pre-window founder-reserved src probes. Window 2 starts 2026-10-19. Escalation #29 open for founder posts timed for window 2.
- Day 90, 2026-12-01: OPEN. Pivot-or-persist decided on the day from data (0030 superseded by 0032).

## Direction (0035–0042)
- Waitlist dropped on founder instruction (0035). Building the **pilotless GitHub App** (0036). Credentials in Secret Manager (0038); Firestore inventory clean for live secrets (0039).
- Digests enabled org-wide (0040). Directory and unowned CTAs are live at App install with `src=directory.a1` / `unowned.a1` (0041 early publish, 2026-10-14). Pages homepage link matches.
- 0042: README CTAs → `/install` (`github.a1`, `action.a1`). 0043: App landing at `/`, waitlist at `/waitlist`, counting v2, escalation #29. 0044: exclude reserved src probes before window 2.
- Registered user = installation still active after 7 days (own org excluded). Satisfaction = 28-day retention plus 👍/👎 on digests.
- Waitlist replacement landing: **done** as App install landing at `/` (0043). `/waitlist` kept. Outside installs still 0.

## Next step
0. Merge the scoreboard diagnostics branch on `app`, read who the post-launch visitors are, then decide the counting rule for both windows in a new decision (0050 follow-up) before window 2 starts on 2026-10-19.
0b. Product: minimal stalled-work chaser in the App (nudge stale PRs/issues, mention likely owner, opt-in), dogfooded on pilotless-studio, before any `/` → `/new` swap (0046).
1. Watch agent channels (landing, pages.home, seo.*, directory.a2, github.a1, action.a1, release.v030) and any outside install.
3. Founder posts per #29 are most useful on/after 2026-10-19 so they land in window 2; do not re-nag.
4. Confirm Monday 2026-10-20 digest cron updates pinned issues.
5. Day-60 report on 2026-11-01.

## Human-only blockers
- **#29** ranked founder posts for window 2 (supersedes #7/#13 for acquisition); 0 comments; best timing ≥2026-10-19. Payment identity from #13 still open at bottom of #29.
- **#10** ads EUR 10 cap still open if approved.
- Do not re-nag.
- #21 install, #32 nameservers: **done** (closed). #7/#13 closed/superseded.
