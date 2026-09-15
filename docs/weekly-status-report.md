# How to generate a weekly status report from GitHub activity (without a standup)

A weekly status meeting usually exists to answer four questions:

1. What shipped?
2. What is in flight?
3. What has stalled?
4. What is waiting on a decision, and from whom?

A repository already knows the answer to the first three. You can pull them in about a minute.

## By hand, with the `gh` CLI

```bash
WEEK_AGO=$(date -d "7 days ago" +%F)   # macOS: date -v-7d +%F

# shipped: pull requests merged in the last 7 days
gh pr list --state merged --search "merged:>=$WEEK_AGO" --json number,title,mergedAt

# in flight: open pull requests
gh pr list --state open --json number,title,updatedAt,isDraft

# stalled: open pull requests nobody has touched in a week
gh pr list --state open --search "updated:<$WEEK_AGO" --json number,title,updatedAt

# unowned: open issues with no assignee
gh issue list --state open --search "no:assignee" --json number,title,createdAt
```

Paste the four lists into a document, then add the two or three things a repository cannot know - a customer call, a decision someone owes you, a hire - and the meeting has nothing left to do.

## On a schedule, with this action

The same four queries, run every Monday, written into an issue:

```yaml
# .github/workflows/weekly-status.yml
name: weekly status
on:
  schedule:
    - cron: "0 8 * * MON"
  workflow_dispatch:
permissions:
  contents: read
  issues: write
  pull-requests: read
jobs:
  status:
    runs-on: ubuntu-latest
    steps:
      - uses: pilotless-studio/pilotless/status-action@main
```

For the available inputs and their defaults, read [`status-action/action.yml`](../status-action/action.yml) - it is short, and it is the only source of truth.

What it does *not* do, deliberately: it calls no language model, needs no API key, creates no account, and sends nothing to anyone. It runs on the `GITHUB_TOKEN` your own workflow already has, and the report stays in your repository.

## What a report like this cannot know

- Work that never touches the repository.
- Whether a merged pull request was the right thing to build.
- *Why* something stalled. The report names the stall and who can clear it; a human still has to clear it.

That boundary is the whole idea. Automate the part that is bookkeeping, and leave people the part that is judgement.

## Honest status of this project

This action works and is used weekly on this repository - the output is in the Issues tab. Everything else is early: as of 2026-09-15 there are 0 registered users and 0 revenue, and this document is one of the first attempts to be found at all. The running log of every decision, including the ones that went badly, is in [`DECISIONS.md`](../DECISIONS.md), and the waitlist for the hosted version is at <https://pilotless-web-o53cqe2tiq-ew.a.run.app/?src=github.r1>.
