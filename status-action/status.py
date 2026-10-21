# pilotless status - writes a repo's weekly status update from its own activity.
# stdlib only. No model call and no API key: it uses the token the runner already gives it.
import collections, datetime, json, os, urllib.error, urllib.parse, urllib.request

TOK = os.environ.get('GH_TOKEN', '')
REPO = os.environ.get('GH_REPO', '')
DAYS = int((os.environ.get('DAYS') or '7').strip() or '7')
OUT = (os.environ.get('OUT') or 'summary').lower()
PREFIX = (os.environ.get('TITLE_PREFIX') or 'Weekly status').strip()
API = 'https://api.github.com'
NOW = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0)
# Fixed window: the DAYS whole UTC days before today's 00:00 UTC, so two runs on the
# same day report the same numbers regardless of the time they ran.
END = NOW.replace(hour=0, minute=0, second=0)
SINCE = END - datetime.timedelta(days=DAYS)
SINCE_S = SINCE.strftime('%Y-%m-%dT%H:%M:%SZ')
END_S = END.strftime('%Y-%m-%dT%H:%M:%SZ')
WARN = []

def call(path, params=None, method='GET', body=None):
    url = API + path
    if params:
        url = url + '?' + urllib.parse.urlencode(params)
    data = json.dumps(body).encode('utf-8') if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers={
        'Authorization': 'Bearer ' + TOK,
        'Accept': 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28',
        'Content-Type': 'application/json',
        'User-Agent': 'pilotless-status'})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

def safe(path, params=None):
    try:
        out = call(path, params)
        return out if isinstance(out, list) else []
    except Exception as e:
        WARN.append(path + ' -> ' + str(e))
        return []

# 10 pages x 100 items. Commits already use this cap; the directory generator uses the
# same cap for merged pull requests.
MAX_PAGES = 10

def safe_all(path, params, pages=None, stop=None, info=None):
    # Page through results (up to pages*100). None means the count is unknown: a failed
    # page must not be reported as a real, smaller number.
    # stop(item) -> True keeps this page and stops. Results sorted newest-updated first
    # can stop once the last row is older than the window; a short page always stops.
    # info['complete'] is True when a short page ended the list. info['capped'] is True
    # when the page cap was hit on a full page that did not trip stop (a lower bound).
    if pages is None:
        pages = MAX_PAGES
    out, capped, complete = [], False, False
    for n in range(1, pages + 1):
        try:
            page = call(path, dict(params, per_page=100, page=n))
        except Exception as e:
            WARN.append(path + ' -> ' + str(e))
            return None
        if not isinstance(page, list):
            return None
        out += page
        if len(page) < 100:
            complete = True
            break
        if stop and stop(page[-1]):
            break
        if n == pages:
            capped = True
    if info is not None:
        info['capped'] = capped
        info['complete'] = complete
    return out

def when(s):
    try:
        return datetime.datetime.strptime(s or '', '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=datetime.timezone.utc)
    except Exception:
        return NOW

def age(s):
    return int((NOW - when(s)).total_seconds() // 86400)

def who(c):
    a = c.get('author') or {}
    if a.get('login'):
        return a['login']
    return ((c.get('commit') or {}).get('author') or {}).get('name') or 'unknown'

def ttl(x, n=70):
    t = (x.get('title') or '').strip().replace(chr(10), ' ')
    return t[:n] + ('...' if len(t) > n else '')

def link(x):
    return '[#' + str(x.get('number')) + '](' + str(x.get('html_url')) + ')'

def before_since(item):
    # Newest-updated first. Creating or closing an issue bumps updated_at, so a row
    # updated before SINCE cannot have been opened or closed in [SINCE, END).
    return when(item.get('updated_at')) < SINCE

def opened_closed_phrase():
    # [SINCE, END) is the fixed UTC-day window (END is today's 00:00 UTC, not the run time).
    info = {}
    recent = safe_all('/repos/' + REPO + '/issues', {
        'state': 'all', 'sort': 'updated', 'direction': 'desc', 'since': SINCE_S,
    }, stop=before_since, info=info)
    if recent is None:
        return '**issue data unavailable this week**', [], [], [], False
    issues = [i for i in recent if 'pull_request' not in i]
    opened = [i for i in issues if SINCE <= when(i.get('created_at')) < END]
    closed = [i for i in issues if i.get('closed_at') and SINCE <= when(i['closed_at']) < END]
    if info.get('capped'):
        text = '**at least ' + str(len(closed)) + ' issues closed**, at least ' + str(len(opened)) + ' opened'
    else:
        text = '**' + str(len(closed)) + ' issues closed**, ' + str(len(opened)) + ' opened'
    return text, issues, opened, closed, True

def load_pulls():
    # Same stop as issues: a PR merged in [SINCE, END) was updated at merge time.
    # Stalled PRs are older than that, so the stalled count is a total only when a
    # short page ends the whole list.
    info = {}
    pulls = safe_all('/repos/' + REPO + '/pulls', {
        'state': 'all', 'sort': 'updated', 'direction': 'desc',
    }, stop=before_since, info=info)
    return (pulls or []), info, pulls is not None

def load_openish():
    # Oldest-updated first. age() is versus run time, the same clock the unowned
    # filter uses. Once the last row was touched in the last 14 days, later pages
    # are newer and cannot be quiet for 14 days.
    info = {}
    rows = safe_all('/repos/' + REPO + '/issues', {
        'state': 'open', 'sort': 'updated', 'direction': 'asc',
    }, stop=lambda i: age(i.get('updated_at')) < 14, info=info)
    return (rows or []), info, rows is not None

def summary_line(commits_ok, n_commits, n_authors, pulls_ok, n_merged, pulls_capped, issue_text):
    if commits_ok:
        head = '**' + str(n_commits) + ' commits** by ' + str(n_authors) + ' people'
    else:
        head = '**commit data unavailable this week**'
    if not pulls_ok:
        merged_bit = '**PR data unavailable this week**'
    elif pulls_capped:
        merged_bit = '**at least ' + str(n_merged) + ' PRs merged**'
    else:
        merged_bit = '**' + str(n_merged) + ' PRs merged**'
    return head + ', ' + merged_bit + ', ' + issue_text + '.'

def main():
    if not REPO:
        raise SystemExit('GH_REPO is empty: set it to owner/name')

    commits = safe_all('/repos/' + REPO + '/commits', {'since': SINCE_S, 'until': END_S})
    commits_ok = commits is not None
    commits = commits or []
    pulls, pull_info, pulls_ok = load_pulls()
    issue_text, issues, opened_i, closed_i, issues_ok = opened_closed_phrase()
    openish, open_info, open_ok = load_openish()

    authors = collections.Counter(who(c) for c in commits)
    merged = [p for p in pulls if p.get('merged_at') and SINCE <= when(p['merged_at']) < END]
    open_pr = [p for p in pulls if p.get('state') == 'open']
    inflight = [p for p in open_pr if age(p.get('updated_at')) < 7]
    stalled = [p for p in open_pr if age(p.get('updated_at')) >= 7]
    unowned = [i for i in openish if 'pull_request' not in i and not i.get('assignees') and age(i.get('updated_at')) >= 14]

    L = []
    L.append('## ' + PREFIX + ': ' + REPO)
    L.append('')
    L.append('_' + SINCE.strftime('%Y-%m-%d') + ' to ' + (END - datetime.timedelta(days=1)).strftime('%Y-%m-%d') + ' (' + str(DAYS) + ' full days, UTC). Written from repository activity by [pilotless status](https://github.com/pilotless-studio/pilotless). No model, no API key, no signup._')
    L.append('')
    L.append(summary_line(commits_ok, len(commits), len(authors), pulls_ok, len(merged), pull_info.get('capped'), issue_text))
    L.append('')
    if merged:
        L.append('### Shipped')
        for p in merged[:8]:
            L.append('- ' + link(p) + ' ' + ttl(p) + ' - ' + str((p.get('user') or {}).get('login', '?')))
        if len(merged) > 8:
            L.append('- ...and ' + str(len(merged) - 8) + ' more')
        L.append('')
    if inflight:
        L.append('### In flight')
        for p in inflight[:8]:
            L.append('- ' + link(p) + ' ' + ttl(p) + ' - touched ' + str(age(p.get('updated_at'))) + 'd ago')
        L.append('')
    if stalled or unowned:
        L.append('### Needs a decision or a nudge')
        for p in stalled[:8]:
            L.append('- ' + link(p) + ' ' + ttl(p) + ' - open PR, no activity for ' + str(age(p.get('updated_at'))) + ' days')
        for i in unowned[:8]:
            L.append('- ' + link(i) + ' ' + ttl(i) + ' - open issue, nobody assigned, quiet ' + str(age(i.get('updated_at'))) + ' days')
        L.append('')
    if closed_i:
        L.append('### Closed')
        for i in closed_i[:8]:
            L.append('- ' + link(i) + ' ' + ttl(i))
        L.append('')
    if authors:
        L.append('### Who moved code')
        L.append(', '.join(a + ' (' + str(n) + ')' for a, n in authors.most_common()))
        L.append('')
    if commits_ok and pulls_ok and issues_ok and not (commits or merged or open_pr or issues):
        L.append('Nothing moved in this window. No commits, no pull requests, no issue activity.')
        L.append('')
    L.append('---')
    if not pulls_ok:
        stalled_bit = 'stalled pull request count unavailable'
    elif pull_info.get('complete'):
        stalled_bit = str(len(stalled)) + ' stalled pull requests'
    else:
        # Early stop keeps merged totals honest and leaves older stalled PRs unlisted.
        stalled_bit = str(len(stalled)) + ' stalled pull requests (capped at the pages fetched)'
    if not open_ok:
        unowned_bit = 'unowned issue count unavailable'
    elif open_info.get('capped'):
        unowned_bit = 'at least ' + str(len(unowned)) + ' issues nobody owns'
    else:
        unowned_bit = str(len(unowned)) + ' issues nobody owns'
    L.append('The chase list above is what a status meeting is usually for: ' + stalled_bit + ' and ' + unowned_bit + '.')
    if WARN:
        L.append('')
        L.append('<details><summary>' + str(len(WARN)) + ' API call(s) failed - the report above is partial</summary>')
        L.append('')
        for w in WARN[:6]:
            L.append('- `' + w.replace('`', '') + '`')
        L.append('')
        L.append('</details>')
    md = chr(10).join(L)

    if 'issue' in OUT:
        t = PREFIX + ': week of ' + SINCE.strftime('%Y-%m-%d')
        found = None
        for i in safe('/repos/' + REPO + '/issues', {'state': 'open', 'per_page': 100}):
            if i.get('title') == t and 'pull_request' not in i:
                found = i
                break
        try:
            if found:
                call('/repos/' + REPO + '/issues/' + str(found['number']), method='PATCH', body={'body': md})
                print('updated issue #' + str(found['number']))
            else:
                n = call('/repos/' + REPO + '/issues', method='POST', body={'title': t, 'body': md})
                print('opened issue #' + str(n.get('number')))
        except Exception as e:
            print('issue write failed: ' + str(e))

    path = os.environ.get('REPORT_PATH') or 'pilotless-status.md'
    if 'file' in OUT:
        open(path, 'w').write(md + chr(10))
    sp = os.environ.get('GITHUB_STEP_SUMMARY')
    if 'summary' in OUT and sp:
        open(sp, 'a').write(md + chr(10))
    go = os.environ.get('GITHUB_OUTPUT')
    if go:
        open(go, 'a').write('report=' + path + chr(10))
    print(md)
    for w in WARN:
        print('warning: ' + w)

if __name__ == '__main__':
    main()
