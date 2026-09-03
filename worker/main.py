# pilotless worker v2 - self-extending harness. Runs as a Cloud Run Job.
# Claims the oldest queued task in Firestore. A task with a `shell` field is run
# verbatim with no model call; anything else is handed to a model through the
# metering proxy, whose bash blocks are executed in /workspace. Transcript, diff
# and token usage are written back. See bootstrap/worker_v2 for the change log.
import os, re, datetime, subprocess, requests
from google.cloud import firestore

VERSION = 2
DB      = firestore.Client()
BASE    = os.environ['PROXY_BASE_URL'].rstrip('/')
TOKEN   = os.environ['PROXY_TOKEN']
WS      = os.environ.get('WORKSPACE', '/workspace')
MAXSTEP = int(os.environ.get('MAX_STEPS', '16'))
MAXTASK = int(os.environ.get('MAX_TASKS', '5'))
NOW     = lambda: datetime.datetime.now(datetime.timezone.utc)

SYSTEM = '''You are a worker agent for pilotless, a one-founder automated company.
You run inside a Cloud Run Job as root, with gcloud authenticated as
pilotless-agent@pilotless-workspace.iam.gserviceaccount.com, a writable workspace
at /workspace, and network access.

PROTOCOL. Reply with at most one ```bash fenced block per message; it is executed
in /workspace and its combined stdout+stderr is returned to you. Repeat until the
task is done, then reply with the literal token <<DONE>> plus a one-paragraph
summary and no bash block. You have a hard cap of %d steps; budget for it.

RULES, in order of authority:
1. Cost is the binding constraint. The whole company lives on EUR 50/month covering
   infrastructure, advertising and every token you and I spend. Prefer free tiers,
   short outputs and few steps. Never leave a paid resource running that nothing
   needs. Never poll in a loop.
2. Never mislead a user, in any copy you write, ever.
3. Do not touch the control project or billing; you have no rights there and
   attempting it is a failure, not a workaround.
4. Leave state behind: write what you did and what you concluded back into
   Firestore before you finish. If it is not written down it did not happen.
5. If the task is underspecified, do the smallest useful version of it and say
   plainly in your summary what you did not do.
6. Never print a secret into your output. Everything you print is stored.''' % MAXSTEP


class ProxyError(Exception):
    def __init__(self, code, text):
        Exception.__init__(self, 'proxy %d: %s' % (code, text[:1500]))
        self.code = code


def bash(cmd, timeout=1800):
    try:
        p = subprocess.run(['bash', '-lc', cmd], cwd=WS, capture_output=True,
                           text=True, timeout=timeout)
        return 'exit=%d\n%s' % (p.returncode, ((p.stdout or '') + (p.stderr or ''))[-8000:])
    except subprocess.TimeoutExpired:
        return 'exit=TIMEOUT after %ds' % timeout


def meter(u, model):
    inc = firestore.Increment
    DB.collection('usage').document(NOW().strftime('%Y-%m')).set({
        'input_tokens': inc(int(u.get('input_tokens', 0) or 0)),
        'output_tokens': inc(int(u.get('output_tokens', 0) or 0)),
        'cache_read_tokens': inc(int(u.get('cache_read_input_tokens', 0) or 0)),
        'cache_write_tokens': inc(int(u.get('cache_creation_input_tokens', 0) or 0)),
        'calls': inc(1), 'updated': NOW(), 'last_model': model}, merge=True)


def mint(task_id, cap_eur):
    try:
        md = ('http://metadata.google.internal/computeMetadata/v1/instance/'
              'service-accounts/default/identity?audience=' + BASE)
        idt = requests.get(md, headers={'Metadata-Flavor': 'Google'}, timeout=30).text.strip()
        r = requests.post(BASE + '/admin/tokens', headers={'Authorization': 'Bearer ' + idt},
                          json={'task_id': task_id, 'cap_eur': cap_eur}, timeout=60)
        r.raise_for_status()
        return r.json().get('token') or TOKEN
    except Exception as e:
        print('mint failed (%s); using stored token' % e)
        return TOKEN


def chat(messages, model, token, max_tokens=1500):
    hdrs = {'x-api-key': token, 'Authorization': 'Bearer ' + token,
            'anthropic-version': '2023-06-01', 'Content-Type': 'application/json'}
    body = {'model': model, 'max_tokens': max_tokens, 'messages': messages,
            'system': [{'type': 'text', 'text': SYSTEM,
                        'cache_control': {'type': 'ephemeral'}}]}
    r = requests.post(BASE + '/v1/messages', headers=hdrs, json=body, timeout=600)
    if r.status_code == 400:                      # retry without the cache block form
        body['system'] = SYSTEM
        r = requests.post(BASE + '/v1/messages', headers=hdrs, json=body, timeout=600)
    if r.status_code >= 400:
        raise ProxyError(r.status_code, r.text)
    j = r.json()
    text = ''.join(b.get('text', '') for b in j.get('content', []) if b.get('type') == 'text')
    return text, (j.get('usage') or {})


def claim():
    q = DB.collection('tasks').where('status', '==', 'queued').order_by('created_at').limit(1)
    for d in q.stream():
        ref = d.reference

        @firestore.transactional
        def go(tx):
            s = ref.get(transaction=tx)
            if s.get('status') != 'queued':
                return None
            tx.update(ref, {'status': 'running', 'started_at': NOW()})
            return s.to_dict()

        t = go(DB.transaction())
        if t:
            return ref, t
    return None, None


def finish(ref, log, extra=None):
    diff = bash('git -C %s log --oneline -3 2>/dev/null; '
                'git -C %s show --stat HEAD 2>/dev/null | head -40' % (WS, WS), timeout=60)
    d = {'status': 'done', 'finished_at': NOW(), 'log': log[-40:], 'diff': diff[:8000]}
    if extra:
        d.update(extra)
    ref.update(d)


def run_shell(ref, t):
    out = bash(t['shell'], timeout=int(t.get('timeout', 1800)))
    finish(ref, ['[shell] ' + out], {'output': out[-8000:], 'tokens_spent': 0})


def run_model(ref, t, tid):
    model = t.get('model') or os.environ.get('DEFAULT_MODEL', 'claude-haiku-4-5')
    token = mint(tid, t['cap_eur']) if t.get('cap_eur') else TOKEN
    steps = min(int(t.get('max_steps', MAXSTEP)), MAXSTEP)
    msgs = [{'role': 'user', 'content': t['prompt']}]
    log = []
    for step in range(steps):
        text, usage = chat(msgs, model, token, int(t.get('max_tokens', 1500)))
        meter(usage, model)
        log.append('[model] ' + text)
        if '<<DONE>>' in text:
            break
        blocks = re.findall(r'```bash\n(.*?)```', text, re.S)
        if not blocks:
            log.append('[worker] no bash block and no <<DONE>>; stopping')
            break
        out = bash('\n'.join(blocks))
        log.append('[shell] ' + out)
        msgs += [{'role': 'assistant', 'content': text},
                 {'role': 'user', 'content': 'SHELL OUTPUT:\n' + out}]
        ref.update({'progress': step + 1, 'log': log[-40:]})
    finish(ref, log)


def selfupdate():
    c = {}
    try:
        d = DB.collection('harness').document('worker_code').get()
        if not d.exists:
            return
        c = d.to_dict() or {}
        if int(c.get('version', 0)) <= VERSION:
            return
        code = c.get('main_py') or ''
        if 'def main' not in code:
            raise RuntimeError('worker_code.main_py defines no main()')
        print('self-update: running worker_code version %s' % c.get('version'))
        exec(compile(code, 'worker_code', 'exec'), {'__name__': '__main__'})
        raise SystemExit(0)
    except SystemExit:
        raise
    except Exception as e:
        DB.collection('harness').document('worker_code').set(
            {'last_error': str(e)[:1500], 'failed_version': c.get('version'),
             'failed_at': NOW()}, merge=True)
        print('self-update failed, continuing on built-in v%d: %s' % (VERSION, e))


def main():
    DB.collection('harness').document('worker_status').set(
        {'version': VERSION, 'last_run': NOW()}, merge=True)
    for _ in range(MAXTASK):
        ref, t = claim()
        if not ref:
            print('queue empty')
            return
        try:
            if t.get('shell'):
                run_shell(ref, t)
            else:
                run_model(ref, t, ref.id)
        except ProxyError as e:
            ref.update({'status': 'error', 'error': str(e)[:2000], 'finished_at': NOW()})
            if e.code in (401, 402, 403, 429):
                print('proxy refuses (%d); ending execution' % e.code)
                return
        except Exception as e:
            ref.update({'status': 'error', 'finished_at': NOW(),
                        'error': ('%s: %s' % (type(e).__name__, e))[:2000]})


if __name__ == '__main__':
    selfupdate()
    main()
