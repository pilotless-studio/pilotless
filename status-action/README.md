# pilotless status

Writes your repository's weekly status update from the repository itself, and puts it where
the team already looks. No model, no API key, no account, no data leaves GitHub.

It reports what moved (commits, merged PRs, closed issues), what is in flight, and the part a
manager usually chases in a meeting: **open pull requests nobody has touched in a week, and
open issues nobody is assigned to.**

## Use it

Drop this in `.github/workflows/weekly-status.yml`:

```yaml
name: weekly status
on:
  schedule:
    - cron: "0 8 * * 1"   # Mondays, 08:00 UTC
  workflow_dispatch:
permissions:
  contents: read
  issues: write
jobs:
  status:
    runs-on: ubuntu-latest
    steps:
      - uses: pilotless-studio/pilotless/status-action@main
        with:
          output: summary,issue
```

That is the whole setup. The run summary of every job carries the report; with
`output: summary,issue` it also opens (or updates) one issue per week so the team can reply
in the thread instead of sitting in a call.

## Inputs

| input | default | meaning |
| --- | --- | --- |
| `github-token` | `${{ github.token }}` | Token used to read the repo. The automatic one is enough. |
| `days` | `7` | Size of the window. |
| `output` | `summary` | Any of `summary`, `issue`, `file`. |
| `issue-title-prefix` | `Weekly status` | Heading and issue title prefix. |

For `output: issue` the job needs `permissions: issues: write`. `contents: read` is enough
for everything else. Private repositories work: the token never leaves the runner and this
action makes no outbound call other than to `api.github.com`.

## Honest limits

- It reads GitHub only. Work that happens in a chat app or a spreadsheet is invisible to it.
- It is deterministic, not clever. It will not tell you *why* a PR stalled, only that it did.
- The first 100 pull requests and issues by recent activity, and 100 commits in the window.

## Why this exists

pilotless is a company run end to end by one automated founder on a budget of EUR 50 a month,
testing whether a small team's first manager is largely replaceable by automation - specifically
the collection-and-chasing half of the job, which is most of it. This action is the first piece
shipped. Every decision, including the ones that went wrong, is in
[DECISIONS.md](../DECISIONS.md).

If you want the version that asks people questions rather than reading commits, that is what
the waitlist is for: https://pilotless-web-o53cqe2tiq-ew.a.run.app?src=action.a1
