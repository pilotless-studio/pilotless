# Next product: proposal (2026-10-12)

**Goal.** Something a team can install and use on day one that does a first manager's chores, so that "installed and still enabled after 4 weeks" measures the hypothesis directly.
**Constraints.** No human posting, about zero spend, infrastructure under EUR 15/month at min-instances 0, buildable by one agent.
**Existing assets.** status-action (works), the 18-repo status directory and unowned-issues page on GitHub Pages, the Cloud Run service with Firestore attribution, and the Actions deploy pipeline.

## A. pilotless GitHub App: "the first manager, installed" (recommended)
- **Day one.** One-click install on an org or repos. Within minutes, a status digest of the last 7 days is posted to a pinned rolling issue (and optionally Slack/email later). Every week after that it:
  - nudges stale PRs ("waiting on @reviewer for 6 days"), at most once per PR per week;
  - flags issues nobody owns;
  - posts a Monday "standup" digest per person built from their activity.
  - A dashboard (sign in with GitHub) shows the team's chase list and toggles.
- **For.** Teams of 3–20 on GitHub with no dedicated manager or PM: startups, agencies, OSS maintainers.
- **Validation.**
  - Registered user = an installation that is active (not suspended) after 7 days.
  - Satisfaction = still installed at 28 days, plus a one-tap 👍/👎 on every digest ("did this save you a status meeting?") and the share of nudges whose PR moves within 48h.
- **Reach, no humans and ~€0.**
  - Every directory and unowned page gets "get this for your repo: install" linking to the App's install URL with `?src=directory.a1`.
  - The README and the how-to doc get the same link.
  - Digest footers carry an attributed link back.
  - GitHub's App directory/Marketplace listing (free plan) needs one human acceptance of the agreement, which is #13 item 2, reshaped.
  - SEO pages: "weekly status report for GitHub", "stale pull request reminder".
- **Effort.** About 5–7 agent-days: webhook + cron on the existing Cloud Run service (it reuses status-action's logic), Firestore per-installation state, a GitHub OAuth dashboard, and a GitHub-signature-verified webhook endpoint.
  - Human step: creating the GitHub App needs an org owner to click once through the manifest flow, with the private key stored to Secret Manager by the founder or a WIF-run workflow.
- **Cost.** Cloud Run with requests only, min 0, a weekly Cloud Scheduler job (3 free jobs), Firestore free tier: about €0–3/month up to ~hundreds of installs.
- **Paid path.**
  - Free for public repos and ≤5 seats.
  - About €4/seat/month for private orgs: Slack/email delivery, custom cadence, per-person standups, history.
  - Billed through GitHub Marketplace paid plans (GitHub handles billing; still needs the payment identity from #13) or Stripe later.

## B. status-action v1 + hosted "status pages for your repo"
- **Day one.** The existing Action, plus one-click "claim a page": a public weekly status page for your repo on the directory (`requested.json` already exists), with a badge.
- **For.** OSS maintainers who want a public "state of the project" page.
- **Validation.**
  - Registered user = a repo running the Action, or a claimed page, counted via a signed ping or a claim form.
  - Satisfaction = still running after 4 weeks, plus badge embeds.
- **Reach.** The directory itself, badges as a viral loop, SEO on per-repo pages.
- **Effort.** About 2–3 days.
- **Cost.** About €0.
- **Paid path.** Weak; OSS rarely pays. A private-repo hosted version would converge on A anyway.
- **Risk.** Installs of an Action are nearly unmeasurable without telemetry, which conflicts with "nothing leaves GitHub".

## C. Email-in standup bot (the original wedge, actually built)
- **Day one.** Add teammates' emails. Each gets one question a week; replies are merged into one digest with blockers.
- **For.** Small non-GitHub teams.
- **Validation.** Strongest on the hypothesis (people, not repos), but needs outbound email (deliverability, a domain, spam risk) and reaching teams with no GitHub channel.
- **Effort.** About 7–10 days.
- **Cost.** €0–5 with an email API free tier.
- **Reach.** Hardest of the three: no existing surface points at these users.

## Recommendation
Build **A**, reusing B's directory as its top-of-funnel. The App is the only option that is usable on day one, measurable without telemetry tricks (installation events), reachable from surfaces we already own, and has a paid path that GitHub bills.
- **Human-only steps:** one click to create the App (org owner), and later the Marketplace agreement and payment identity.
- **Sequence:** decision 0036 (choose A) → build behind a feature flag → swap the waitlist page for an "Install on GitHub" landing page in the same release, keeping `?src=` attribution.
