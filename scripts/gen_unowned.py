#!/usr/bin/env python3
"""One aggregated page: open issues across tracked repositories that nobody has picked up.

Reuses the repository list and the API helper from gen_status_directory.py so the
two pages can never disagree about which repositories are covered.
"""
import sys, os, datetime, pathlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_status_directory as G

LANDING = 'https://pilotless-web-o53cqe2tiq-ew.a.run.app/install?src=unowned.a2'
REPO = 'https://github.com/pilotless-studio/pilotless'


def age(now, ts):
    try:
        return (now - datetime.datetime.strptime(ts, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=datetime.timezone.utc)).days
    except Exception:
        return '?'


def main():
    now = datetime.datetime.now(datetime.timezone.utc)
    rows = []
    for full in G.BASE:
        items = G.get('/repos/' + full + '/issues', '?state=open&labels=good%20first%20issue&assignee=none&sort=created&direction=desc&per_page=5')
        tag = 'good first issue'
        if not isinstance(items, list) or not items:
            tag = 'unassigned, no replies'
            raw = G.get('/repos/' + full + '/issues', '?state=open&assignee=none&sort=created&direction=desc&per_page=20')
            items = [i for i in (raw or []) if not i.get('pull_request') and (i.get('comments') or 0) == 0][:3]
        for i in (items or []):
            if not isinstance(i, dict) or i.get('pull_request'):
                continue
            rows.append((i.get('created_at') or '', full, i, tag))
    rows.sort(reverse=True)
    L = ['---', 'title: "Good first issues nobody has picked up: unassigned open source issues this week"',
         'description: "Unassigned, unanswered issues in popular open source GitHub projects, refreshed weekly. A starting point for contributors and a triage list for maintainers."', '---', '',
         '[All status pages](./) · [Home](../)', '',
         '# Open source issues nobody has picked up', '']
    L.append('_Week of ' + now.date().isoformat() + '. ' + str(len(rows)) + ' open issues across ' + str(len(G.BASE)) + ' well-known public repositories that are unassigned and, in most cases, have had no reply yet. Regenerated every Thursday from public GitHub activity by [pilotless status](' + REPO + '). Unofficial; none of these projects is affiliated with this one._')
    L.append('')
    L.append('Every one of these is a real piece of work on a real project, sitting in a queue nobody is watching. If you are looking for somewhere to start contributing, start here. If you maintain one of these projects, this is the list a status meeting would have produced for you.')
    L.append('')
    cur = None
    for _, full, i, tag in rows:
        if full != cur:
            L += ['', '## ' + full, '']
            cur = full
        L.append('- [#' + str(i.get('number')) + '](' + (i.get('html_url') or '') + ') ' + (i.get('title') or '')[:110] + ' - opened ' + str(age(now, i.get('created_at'))) + ' days ago, ' + tag)
    L += ['', '---', '']
    L.append('Keeping this list current is one of the few genuinely useful things a manager does, and it does not need a manager. [Install the pilotless GitHub App](' + LANDING + ') and it writes the same kind of list into a pinned issue on your own repos every week.')
    L.append('')
    pathlib.Path('docs/status').mkdir(parents=True, exist_ok=True)
    pathlib.Path('docs/status/unowned.md').write_text('\n'.join(L) + '\n')
    print('UNOWNED rows', len(rows))


if __name__ == '__main__':
    main()
