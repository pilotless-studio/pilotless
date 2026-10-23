#!/usr/bin/env python3
"""Regenerate docs/status/: one weekly status page per tracked public repository.

Reads only what GitHub publishes, through the documented API. The weekly
status directory workflow runs this on the runner and publishes the Jekyll
site to GitHub Pages. It does not commit the pages.
Extra repositories can be added to docs/status/requested.json (a JSON list of
"owner/name" strings) - that file is how a repository claimed on the landing
page gets a page here.
"""
import os, re, json, datetime, pathlib, urllib.parse, urllib.request

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


UNAVAILABLE = 'commit data unavailable this week'
MAX_PAGES = 10  # up to 1000 commits / closed PRs per repository per week


def fetch(url):
    """One API request. Returns (parsed json, next-page url) or (None, None) on any error."""
    req = urllib.request.Request(url, headers={
        'Authorization': 'Bearer ' + TOKEN,
        'Accept': 'application/vnd.github+json',
        'User-Agent': 'pilotless-status/0.5'})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            m = re.search(r'<([^>]+)>;\s*rel="next"', r.headers.get('Link') or '')
            return json.loads(r.read().decode()), (m.group(1) if m else None)
    except Exception as e:
        print('WARN', url.replace(API, '')[:100], repr(e)[:120])
        return None, None


def get(path, q=''):
    return fetch(API + path + q)[0]


def get_all(path, q='', stop=None):
    """Follow Link: rel=next up to MAX_PAGES. Returns a list, or None if any page failed
    (a partial count would be presented as a real number, so it is treated as missing).
    stop(item) -> True ends paging early once results are past the window."""
    url, items = API + path + q, []
    for _ in range(MAX_PAGES):
        page, nxt = fetch(url)
        if not isinstance(page, list):
            return None
        items += page
        if not nxt or (stop and page and stop(page[-1])):
            return items
        url = nxt
    return items


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
    # Fixed window: the seven whole UTC days before today's 00:00 UTC. Anchoring to the
    # run time made counts depend on when (and how often) the workflow ran.
    end = now.replace(hour=0, minute=0, second=0, microsecond=0)
    since = end - datetime.timedelta(days=7)
    sincez = since.strftime('%Y-%m-%dT%H:%M:%SZ')
    endz = end.strftime('%Y-%m-%dT%H:%M:%SZ')

    def age(ts):
        try:
            return (now - datetime.datetime.strptime(ts, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=datetime.timezone.utc)).days
        except Exception:
            return '?'

    index, written, failed = [], 0, []
    for full in repos:
        meta = get('/repos/' + full)
        branch = (meta or {}).get('default_branch') or ''
        # Commits are counted on the default branch only (that is what the commits API
        # returns without sha=). Name it on the page so work on other branches is not
        # mistaken for "nothing happened". If any page of commits fails (rate limit,
        # timeout, API error) the count is unknown and the page says so - never 0.
        commits = get_all('/repos/' + full + '/commits', '?since=' + sincez + '&until=' + endz + '&per_page=100' + ('&sha=' + urllib.parse.quote(branch, safe='') if branch else ''))
        pulls = get('/repos/' + full + '/pulls', '?state=open&sort=updated&direction=asc&per_page=100')
        closed = get_all('/repos/' + full + '/pulls', '?state=closed&sort=updated&direction=desc&per_page=100',
                         stop=lambda p: (p.get('updated_at') or '') < sincez)
        issues = get('/repos/' + full + '/issues', '?state=open&sort=created&direction=desc&per_page=100')
        if not isinstance(pulls, list):
            failed.append(full)
            continue
        issues = issues if isinstance(issues, list) else []
        # Only the number of distinct authors is published. Per-person names and
        # commit counts are deliberately not written to these public pages (CEO
        # privacy decision); per-person activity stays in the private digest the
        # status-action writes inside the installer's own repository.
        authors = {}
        for c in commits or []:
            a = (c.get('author') or {}).get('login') or ((c.get('commit') or {}).get('author') or {}).get('name') or 'unknown'
            authors[a] = authors.get(a, 0) + 1
        merged = [p for p in closed or [] if p.get('merged_at') and sincez <= p['merged_at'] < endz]
        stalled = [p for p in pulls if (p.get('updated_at') or '') < sincez][:5]
        unowned = [i for i in issues if not i.get('assignee') and not i.get('pull_request') and (i.get('comments') or 0) == 0][:5]
        on = ('`' + branch + '`') if branch else 'the default branch'
        if commits is None:
            ncommits, summary = UNAVAILABLE, '**' + UNAVAILABLE + '**'
        else:
            capped = len(commits) >= MAX_PAGES * 100
            ncommits = (str(len(commits)) + '+' if capped else str(len(commits))) + ' commits'
            summary = ('**' + ncommits + '** to ' + on + ' by ' + str(len(authors)) + (' person' if len(authors) == 1 else ' people')) if commits else ('**No commits** to ' + on)
            if not commits:
                ncommits = 'no commits to ' + (branch or 'the default branch')
        if closed is None:
            nmerged = 'merged pull request count unavailable'
        else:
            nmerged = ('at least ' if len(closed) >= MAX_PAGES * 100 else '') + str(len(merged)) + ' pull requests merged'
        desc = (full + ' this week: ' + ncommits + ', ' + str(len(stalled)) + ' stalled pull requests and ' + str(len(unowned)) + ' unowned issues, from public GitHub activity. Unofficial weekly status report.')
        L = ['---', 'title: "' + full + ' weekly status: stalled PRs and unowned issues"', 'description: "' + desc.replace('"', "'") + '"', '---', '',
             '[All status pages](./) · [Unowned issues across all projects](unowned.html) · [How to write a weekly status report from GitHub](../weekly-status-report.html)', '',
             '# Weekly status: ' + full, '']
        L.append('_' + since.date().isoformat() + ' to ' + (end - datetime.timedelta(days=1)).date().isoformat() + " (7 full days, UTC). Unofficial: generated from this repository's public GitHub activity by [pilotless status](" + REPO + '). Not affiliated with the project, and no information here that GitHub does not publish._')
        L.append('')
        L.append(summary + ', **' + nmerged + '**, **' + str(len(pulls)) + ' open pull requests**, **' + str(len([i for i in issues if not i.get('pull_request')])) + ' open issues** on this page of results.')
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
        index.append('- [' + full + '](' + slug + '.md) - ' + ncommits + ', ' + str(len(stalled)) + ' stalled PRs, ' + str(len(unowned)) + ' unowned issues')
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
