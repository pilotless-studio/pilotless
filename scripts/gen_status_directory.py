#!/usr/bin/env python3
"""Regenerate docs/status/: one weekly status page per tracked public repository.

Reads only what GitHub publishes, through the documented API. Run weekly by
.github/workflows/weekly-directory.yml with the repository's own GITHUB_TOKEN.
Extra repositories can be added to docs/status/requested.json (a JSON list of
"owner/name" strings) - that file is how a repository claimed on the landing
page gets a page here.
"""
import os, json, datetime, pathlib, urllib.request

TOKEN = os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN') or ''
API = 'https://api.github.com'
LANDING = 'https://pilotless-web-o53cqe2tiq-ew.a.run.app/install?src=directory.a2'
ACTION_DOCS = 'https://github.com/pilotless-studio/pilotless#status-action'
REPO = 'https://github.com/pilotless-studio/pilotless'
BASE = ['sveltejs/svelte', 'vitejs/vite', 'withastro/astro', 'prisma/prisma', 'supabase/supabase',
        'tailwindlabs/tailwindcss', 'denoland/deno', 'tiangolo/fastapi', 'pydantic/pydantic',
        'duckdb/duckdb', 'pola-rs/polars', 'ollama/ollama', 'grafana/grafana',
        'hashicorp/terraform', 'apache/airflow', 'dbt-labs/dbt-core', 'n8n-io/n8n', 'appwrite/appwrite',
        'astral-sh/ruff', 'astral-sh/uv', 'biomejs/biome', 'oven-sh/bun', 'tauri-apps/tauri', 'nestjs/nest',
        'drizzle-team/drizzle-orm', 'langchain-ai/langchain', 'huggingface/transformers', 'excalidraw/excalidraw',
        'immich-app/immich', 'zed-industries/zed']


def get(path, q=''):
    req = urllib.request.Request(API + path + q, headers={
        'Authorization': 'Bearer ' + TOKEN,
        'Accept': 'application/vnd.github+json',
        'User-Agent': 'pilotless-status/0.4'})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode())
    except Exception as e:
        print('WARN', path, repr(e)[:120])
        return None


def main():
    out = pathlib.Path('docs/status')
    out.mkdir(parents=True, exist_ok=True)
    repos = list(BASE)
    req = out / 'requested.json'
    if req.exists():
        try:
            for r in json.loads(req.read_text()):
                if isinstance(r, str) and '/' in r and r not in repos:
                    repos.append(r)
        except Exception as e:
            print('WARN requested.json', repr(e)[:80])
    now = datetime.datetime.now(datetime.timezone.utc)
    since = now - datetime.timedelta(days=7)
    sincez = since.strftime('%Y-%m-%dT%H:%M:%SZ')

    def age(ts):
        try:
            return (now - datetime.datetime.strptime(ts, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=datetime.timezone.utc)).days
        except Exception:
            return '?'

    index, written, failed = [], 0, []
    for full in repos:
        commits = get('/repos/' + full + '/commits', '?since=' + sincez + '&per_page=100')
        pulls = get('/repos/' + full + '/pulls', '?state=open&sort=updated&direction=asc&per_page=100')
        closed = get('/repos/' + full + '/pulls', '?state=closed&sort=updated&direction=desc&per_page=50')
        issues = get('/repos/' + full + '/issues', '?state=open&sort=created&direction=desc&per_page=100')
        if not isinstance(commits, list) or not isinstance(pulls, list):
            failed.append(full)
            continue
        closed = closed if isinstance(closed, list) else []
        issues = issues if isinstance(issues, list) else []
        # Only the number of distinct authors is published. Per-person names and
        # commit counts are deliberately not written to these public pages (CEO
        # privacy decision); per-person activity stays in the private digest the
        # status-action writes inside the installer's own repository.
        authors = {}
        for c in commits:
            a = (c.get('author') or {}).get('login') or ((c.get('commit') or {}).get('author') or {}).get('name') or 'unknown'
            authors[a] = authors.get(a, 0) + 1
        merged = [p for p in closed if p.get('merged_at') and p['merged_at'] >= sincez]
        stalled = [p for p in pulls if (p.get('updated_at') or '') < sincez][:5]
        unowned = [i for i in issues if not i.get('assignee') and not i.get('pull_request') and (i.get('comments') or 0) == 0][:5]
        ncommits = '100+' if len(commits) >= 100 else str(len(commits))
        nmerged = ('at least ' + str(len(merged))) if len(closed) >= 50 else str(len(merged))
        desc = (full + ' this week: ' + ncommits + ' commits, ' + str(len(stalled)) + ' stalled pull requests and ' + str(len(unowned)) + ' unowned issues, from public GitHub activity. Unofficial weekly status report.')
        L = ['---', 'title: "' + full + ' weekly status: stalled PRs and unowned issues"', 'description: "' + desc.replace('"', "'") + '"', '---', '',
             '[All status pages](./) · [Unowned issues across all projects](unowned.html) · [How to write a weekly status report from GitHub](../weekly-status-report.html)', '',
             '# Weekly status: ' + full, '']
        L.append('_' + since.date().isoformat() + ' to ' + now.date().isoformat() + " (7 days). Unofficial: generated from this repository's public GitHub activity by [pilotless status](" + REPO + '). Not affiliated with the project, and no information here that GitHub does not publish._')
        L.append('')
        L.append('**' + ncommits + ' commits** by ' + str(len(authors)) + ' people, **' + nmerged + ' pull requests merged**, **' + str(len(pulls)) + ' open pull requests**, **' + str(len([i for i in issues if not i.get('pull_request')])) + ' open issues** on this page of results.')
        L.append('')
        L.append('### Stalled pull requests')
        if stalled:
            L += ['Open, and untouched for seven days or more:', '']
            for p in stalled:
                L.append('- [#' + str(p.get('number')) + '](' + (p.get('html_url') or '') + ') ' + (p.get('title') or '')[:90] + ' - last touched ' + str(age(p.get('updated_at'))) + ' days ago')
        else:
            L.append('None. Every open pull request has been touched in the last seven days.')
        L.append('')
        L.append('### Issues nobody has picked up')
        if unowned:
            L += ['Open, unassigned, and with no replies yet:', '']
            for i in unowned:
                L.append('- [#' + str(i.get('number')) + '](' + (i.get('html_url') or '') + ') ' + (i.get('title') or '')[:90] + ' - opened ' + str(age(i.get('created_at'))) + ' days ago')
        else:
            L.append('None on this page of results.')
        L += ['', '---', '']
        L.append('The two lists above are what a status meeting is usually for. Nobody had to attend one to produce this page.')
        L.append('')
        L.append('If you maintain ' + full + ' and would rather this page did not exist, [open an issue](' + REPO + '/issues/new) and it will be deleted - no argument, no reply needed beyond the repository name.')
        L.append('')
        L.append('**Want this for your own repositories?** [Install the pilotless GitHub App](' + LANDING + ') — one click, then a pinned weekly status digest in each selected repo. Prefer CI-only? The [status-action](' + ACTION_DOCS + ') is still two lines of YAML with no account and nothing leaving GitHub.')
        slug = full.replace('/', '--').lower()
        (out / (slug + '.md')).write_text('\n'.join(L) + '\n')
        written += 1
        index.append('- [' + full + '](' + slug + '.md) - ' + ncommits + ' commits, ' + str(len(stalled)) + ' stalled PRs, ' + str(len(unowned)) + ' unowned issues')
    I = ['---', 'title: "Weekly status reports for ' + str(written) + ' open source GitHub repositories"',
         'description: "What shipped, which pull requests stalled and which issues nobody picked up, for ' + str(written) + ' popular open source repositories. Regenerated weekly from public GitHub data."', '---', '',
         '# Weekly status pages', '']
    I.append('What a status meeting is usually for, written from public activity instead of asked for in a meeting: what shipped this week, which pull requests have gone quiet, and which issues nobody has picked up.')
    I.append('')
    I.append('These pages are generated for well-known public repositories as a worked example of what [pilotless status](' + REPO + ') produces. They are **unofficial** - none of these projects is affiliated with this one, and nothing here is information GitHub does not already publish. They are regenerated every Thursday by [a scheduled workflow](' + REPO + '/blob/main/.github/workflows/weekly-directory.yml) in this repository. Maintainers who would rather not have a page can [open an issue](' + REPO + '/issues/new) and it will be deleted.')
    I.append('')
    I += sorted(index)
    I += ['', 'Also: [open issues nobody has picked up, across all of these](unowned.html) · guides: [weekly status report from GitHub](../weekly-status-report.html), [stale pull request reminders](../stale-pull-request-reminder.html), [a GitHub standup bot without the standup](../github-standup-bot.html).']
    I += ['', 'Last regenerated ' + now.strftime('%Y-%m-%d') + '. For your own repositories: [install the GitHub App](' + LANDING + ').']
    body = '\n'.join(I) + '\n'
    (out / 'README.md').write_text(body)
    (out / 'index.md').write_text(body)
    print('GEN written', written, 'failed', failed)
    return written, failed


if __name__ == '__main__':
    main()
