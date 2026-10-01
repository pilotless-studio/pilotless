#!/usr/bin/env python3
"""Tell IndexNow (Bing, DuckDuckGo, Yandex, Seznam) that these pages changed.

No account, no key exchange, no human: ownership is proved by serving the key
back from the site itself. Runs after every weekly regeneration.
"""
import json, pathlib, urllib.request, urllib.error

KEY = '7f3c1d9e4b2a86f05c3d1e7a9b4f2c68'
HOST = 'pilotless-studio.github.io'
LOC = 'https://pilotless-studio.github.io/pilotless/' + KEY + '.txt'


def main():
    urls = [u.strip() for u in pathlib.Path('docs/urls.txt').read_text().split('\n') if u.strip()]
    body = {'host': HOST, 'key': KEY, 'keyLocation': LOC, 'urlList': urls}
    req = urllib.request.Request('https://api.indexnow.org/IndexNow', data=json.dumps(body).encode(),
                                 headers={'Content-Type': 'application/json; charset=utf-8', 'User-Agent': 'pilotless/0.5'}, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=30) as f:
            print('INDEXNOW', f.status, len(urls), 'urls')
    except urllib.error.HTTPError as e:
        print('INDEXNOW_ERR', e.code, e.read().decode()[:300])
    except Exception as e:
        print('INDEXNOW_EX', repr(e)[:200])


if __name__ == '__main__':
    main()
