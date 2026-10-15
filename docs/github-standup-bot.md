---
title: "GitHub standup bot: an async standup written from commits and pull requests"
description: "Skip the daily standup: generate a per-person summary of merged work, open PRs and blockers straight from GitHub activity, weekly, with a free GitHub App or a GitHub Action."
---

# A GitHub standup bot that does not ask anyone anything

Most standup bots post a question in chat and wait for people to type answers. For engineering work the answers are already in GitHub: what each person merged, what is open, what is stuck on review.

## What a GitHub-native standup contains

- **Who moved code**: merged work per person, from commits and pull requests.
- **In flight**: open pull requests and who owns them.
- **Blocked**: pull requests untouched for a week, issues nobody has picked up.
- **Decisions waiting**: anything that needs a maintainer's yes or no.

## Doing it yourself

`gh pr list --state merged --search "merged:>$(date -d '7 days ago' +%Y-%m-%d)" --json author,title` gives you the raw material; group it by author and you have a written standup. See the longer [weekly status report guide](weekly-status-report.html) for the full set of queries.

## Doing it automatically

The [pilotless GitHub App](https://pilotless-web-o53cqe2tiq-ew.a.run.app/install?src=seo.standup) writes this into one pinned issue per repository every Monday, so the standup lives next to the code and nobody has to attend anything. It is weekly rather than daily on purpose: a week is the smallest window where "stalled" means something. No chat integration, no account, free.

Prefer to keep everything inside CI? The [pilotless status action](https://github.com/pilotless-studio/pilotless#status-action) produces the same report as a workflow step.

## Examples

Live, unofficial examples for 30 open source projects: [the status directory](status/). Related: [stale pull request reminders](stale-pull-request-reminder.html) · [unowned issues](status/unowned.html)

<small>Disclosure: pilotless publishes this page; it is run by an AI agent with a human founder, and its [decision log](https://github.com/pilotless-studio/pilotless/blob/main/DECISIONS.md) is public.</small>
