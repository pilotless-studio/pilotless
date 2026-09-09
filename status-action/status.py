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
SINCE = NOW - datetime.timedelta(days=DAYS)
SINCE_S = SINCE.strftime('%Y-%m-%dT%H:%M:%SZ')
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

if not REPO:
    raise SystemExit('GH_REPO is empty: set it to owner/name')

commits = safe('/repos/' + REPO + '/commits', {'since': SINCE_S, 'per_page': 100})
pulls = safe('/repos/' + REPO + '/pulls', {'state': 'all', 'sort': 'updated', 'direction': 'desc', 'per_page': 100})
recent = safe('/repos/' + REPO + '/issues', {'state': 'all', 'sort': 'updated', 'direction': 'desc', 'per_page': 100, 'since': SINCE_S})
openish = safe('/repos/' + REPO + '/issues', {'state': 'open', 'sort': 'updated', 'direction': 'asc', 'per_page': 100})

authors = collections.Counter(who(c) for c in commits)
merged = [p for p in pulls if p.get('merged_at') and when(p['merged_at']) >= SINCE]
open_pr = [p for p in pulls if p.get('state') == 'open']
inflight = [p for p in open_pr if age(p.get('updated_at')) < 7]
stalled = [p for p in open_pr if age(p.get('updated_at')) >= 7]
issues = [i for i in recent if 'pull_request' not in i]
opened_i = [i for i in issues if when(i.get('created_at')) >= SINCE]
closed_i = [i for i in issues if i.get('closed_at') and when(i['closed_at']) >= SINCE]
unowned = [i for i in openish if 'pull_request' not in i and not i.get('assignees') and age(i.get('updated_at')) >= 14]

L = []
L.append('## ' + PREFIX + ': ' + REPO)
L.append('')
L.append('_' + SINCE.strftime('%Y-%m-%d') + ' to ' + NOW.strftime('%Y-%m-%d') + ' (' + str(DAYS) + ' days). Written from repository activity by [pilotless status](https://github.com/pilotless-studio/pilotless). No model, no API key, no signup._')
L.append('')
L.append('**' + str(len(commits)) + ' commits** by ' + str(len(authors)) + ' people, **' + str(len(merged)) + ' PRs merged**, **' + str(len(closed_i)) + ' issues closed**, ' + str(len(opened_i)) + ' opened.')
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
if not (commits or merged or open_pr or issues):
    L.append('Nothing moved in this window. No commits, no pull requests, no issue activity.')
    L.append('')
L.append('---')
L.append('The chase list above is what a status meeting is usually for: ' + str(len(stalled)) + ' stalled pull requests and ' + str(len(unowned)) + ' issues nobody owns.')
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
