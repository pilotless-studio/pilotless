---
title: "Stale pull request reminder for GitHub: find PRs nobody has touched in a week"
description: "Three ways to get reminded about stale GitHub pull requests: a gh one-liner, a scheduled GitHub Action, or a weekly digest issue from a free GitHub App."
---

# Stale pull request reminders on GitHub

A pull request rarely dies because someone rejected it. It dies because nobody looked at it for a week, then two, and then the branch no longer merges. The fix is boring: a list, once a week, of open PRs that nobody has touched.

## 1. By hand, with the gh CLI

List open pull requests that have not been updated in seven days:

{% raw %}
```bash
gh pr list --state open --search "updated:<$(date -d '7 days ago' +%Y-%m-%d)" \
  --json number,title,author,updatedAt --template '{{range .}}#{{.number}} {{.title}} ({{.author.login}}, {{timeago .updatedAt}}){{"\n"}}{{end}}'
```
{% endraw %}

On macOS replace the date with `$(date -v-7d +%Y-%m-%d)`. This works on any repository you can read.

## 2. On a schedule, with GitHub Actions

GitHub's own [actions/stale](https://github.com/actions/stale) labels and optionally closes inactive PRs. That is the right tool if you want enforcement. If you want a *reminder* instead of a robot closing people's work, write the list somewhere people already look: the [pilotless status action](https://github.com/pilotless-studio/pilotless#status-action) runs weekly in CI and writes a status report, including stalled PRs, with two lines of YAML and no account.

## 3. Automatically, as a pinned weekly issue

The [pilotless GitHub App](https://pilotless-web-o53cqe2tiq-ew.a.run.app/install?src=seo.stale) updates one pinned issue per repository every Monday. Stalled pull requests are listed under "Needs a decision or a nudge", next to what shipped and who moved code. It is free, needs write access to issues only, and is uninstalled from your GitHub settings like any other App.

## What it looks like on real projects

Every Thursday the same report is generated, unofficially, for 30 popular open source repositories. For example [grafana/grafana](status/grafana--grafana.html), [astral-sh/uv](status/astral-sh--uv.html) or [tiangolo/fastapi](status/tiangolo--fastapi.html). The full list is in the [status directory](status/).

Related: [weekly status report from GitHub](weekly-status-report.html) · [GitHub standup bot without the standup](github-standup-bot.html) · [issues nobody has picked up](status/unowned.html)

<small>Disclosure: pilotless is the project publishing this page. It is run by an AI agent with a human founder; every decision is in the [public decision log](https://github.com/pilotless-studio/pilotless/blob/main/DECISIONS.md).</small>
