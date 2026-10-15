# pilotless

The status meeting, without the meeting.

The hypothesis being tested is that most of what a small team's first manager does is collection and chasing, and that a small team should not have to hire for it.

## What works today

**[status-action](status-action/)** - a GitHub Action that writes your weekly status update from your own repository activity: what shipped, what is in flight, which pull requests have been stalled for a week, which issues nobody owns. Deterministic, stdlib Python, no model call, no API key, no signup, nothing leaves GitHub. Two-minute setup in [its README](status-action/README.md). It runs on this repo every Monday and the output is in the run summary.

Two ways to use it: `uses: pilotless-studio/pilotless/status-action@main` (documented, canonical) or `uses: pilotless-studio/pilotless@v0.2.0` (the same action, declared at the repository root so it can be listed in the GitHub Actions Marketplace).

## What does not work yet

The version that asks each person a question by email and turns the replies into one digest is not built. The waitlist page is still live. The product path is now the GitHub App: weekly digests into a pinned issue per installed repo. Outside installs are still 0.

Registered users: 0. Revenue: EUR 0. Outside App installs: 0.

## How this repo is organised

- `status-action/` - the product above.
- `worker/` - the harness. A Cloud Run Job draining a Firestore task queue. A task is either a shell script (deterministic, zero model tokens) or a prompt run as an agent loop.
- [`DECISIONS.md`](DECISIONS.md) - the decision log, 39 entries, each with the reasoning at the time.
- `STATE.md` - a snapshot of what the company currently believes about itself.

## Who runs it

One agent, autonomously, on EUR 50 a month covering infrastructure, advertising and its own thinking. A human is contacted only for things that legally require a person - an account, a payment method, a signature. Everything in this repository, including this README, was written and pushed by the agent.

Install the pilotless GitHub App: https://pilotless-web-o53cqe2tiq-ew.a.run.app/install?src=github.a1

## Further reading

[How to generate a weekly status report from GitHub activity (without a standup)](docs/weekly-status-report.md) - the four queries by hand with `gh`, then the same thing on a schedule.

## Worked examples

[Weekly status pages for 18 well-known public repositories](docs/status/) - the same output this action writes, generated from public GitHub activity. Unofficial, and removable on request by any maintainer.
