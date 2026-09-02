# Baton worker v1 - minimal self-extending harness. Runs as a Cloud Run Job.
# Claims the oldest queued task in Firestore, hands it to a model through the
# metering proxy, executes the bash the model returns, writes transcript and
# diff back onto the task doc, and meters token usage into usage/<yyyy-mm>.
import os, re, subprocess, datetime, requests
from google.cloud import firestore

DB      = firestore.Client()
BASE    = os.environ['PROXY_BASE_URL'].rstrip('/')
TOKEN   = os.environ['PROXY_TOKEN']
WS      = os.environ.get('WORKSPACE', '/workspace')
MAXSTEP = int(os.environ.get('MAX_STEPS', '20'))
NOW     = lambda: datetime.datetime.now(datetime.timezone.utc)

SYSTEM = '''You are a worker agent for Baton, a one-founder automated company.
You run inside a Cloud Run Job as root, with gcloud authenticated as the
project service account, a writable workspace at /workspace, and network access.

PROTOCOL. Reply with at most one ```bash fenced block per message; it is executed
in /workspace and its combined stdout+stderr is returned to you. Repeat until the
task is done, then reply with the literal token <<DONE>> plus a one-paragraph
summary and no bash block. You have a hard cap of %d steps; budget for it.

RULES, in order of authority:
1. Cost is the binding constraint. The whole company lives on EUR 50/month
   covering infrastructure, advertising and every token you and I spend. Prefer
   free tiers, small models and short outputs. Never leave a paid resource running
   that nothing needs. Never poll in a loop.
2. Never mislead a user, in any copy you write, ever.
3. Do not touch the control project or billing; you have no rights there and
   attempting it is a failure, not a workaround.
4. Leave state behind: write what you did and what you concluded back into
   Firestore before you finish. If it is not written down it did not happen.
5. If the task is underspecified, do the smallest useful version of it and say
   plainly in your summary what you did not do.''' % MAXSTEP

def chat(messages, model, max_tokens=2000):
    # The proxy's dialect is unknown to me at authoring time, so try the common
    # shapes in order and remember which one worked.
    body = {'model': model, 'messages': messages, 'max_tokens': max_tokens}
    hdrs = {'Authorization': 'Bearer ' + TOKEN, 'x-api-key': TOKEN,
            'anthropic-version': '2023-06-01', 'Content-Type': 'application/json'}
    last = None
    for path in ('/v1/chat/completions', '/chat/completions', '/v1/messages'):
        r = requests.post(BASE + path, headers=hdrs, json=body, timeout=600)
        last = r
        if r.status_code in (404, 405):
            continue
        r.raise_for_status()
        j = r.json()
        if 'choices' in j:
            text = j['choices'][0]['message']['content']
        else:
            text = ''.join(b.get('text', '') for b in j.get('content', []))
        return text, j.get('usage', {}) or {}
    raise RuntimeError('proxy rejected every shape: %s %s' % (last.status_code, last.text[:300]))

def bash(cmd):
    p = subprocess.run(['bash', '-lc', cmd], cwd=WS, capture_output=True,
                       text=True, timeout=1800)
    return 'exit=%d\n%s' % (p.returncode, ((p.stdout or '') + (p.stderr or ''))[-8000:])

def meter(u):
    inc = firestore.Increment
    DB.collection('usage').document(NOW().strftime('%Y-%m')).set({
        'prompt_tokens': inc(u.get('prompt_tokens', u.get('input_tokens', 0)) or 0),
        'completion_tokens': inc(u.get('completion_tokens', u.get('output_tokens', 0)) or 0),
        'calls': inc(1), 'updated': NOW()}, merge=True)

def claim():
    for d in DB.collection('tasks').where('status', '==', 'queued').order_by('created_at').limit(1).stream():
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

def run(ref, t):
    model = t.get('model') or os.environ.get('DEFAULT_MODEL', '')
    msgs = [{'role': 'system', 'content': SYSTEM},
            {'role': 'user', 'content': t['prompt']}]
    log = []
    for step in range(MAXSTEP):
        text, usage = chat(msgs, model, int(t.get('max_tokens', 2000)))
        meter(usage)
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
    diff = bash('git -C %s diff HEAD --stat 2>/dev/null; git -C %s log --oneline -3 2>/dev/null' % (WS, WS))
    ref.update({'status': 'done', 'finished_at': NOW(),
                'log': log[-40:], 'diff': diff[:8000]})

def main():
    for _ in range(10):                      # bounded: never an infinite loop
        ref, t = claim()
        if not ref:
            print('queue empty'); return
        try:
            run(ref, t)
        except Exception as e:
            ref.update({'status': 'error', 'error': str(e)[:2000], 'finished_at': NOW()})

main()
