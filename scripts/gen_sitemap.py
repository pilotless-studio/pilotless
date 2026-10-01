#!/usr/bin/env python3
"""Write docs/sitemap.xml and docs/urls.txt from whatever markdown is in docs/.

Jekyll renders foo.md as foo.html and index.md as the directory root, so the
URLs here are the URLs a crawler will actually be able to fetch.
"""
import pathlib, datetime

BASE = 'https://pilotless-studio.github.io/pilotless/'


def main():
    docs = pathlib.Path('docs')
    urls = []
    for p in sorted(docs.rglob('*.md')):
        rel = p.relative_to(docs).as_posix()
        if rel.endswith('README.md'):
            continue
        if rel == 'index.md':
            u = ''
        elif rel.endswith('/index.md'):
            u = rel[:-len('index.md')]
        else:
            u = rel[:-3] + '.html'
        urls.append(BASE + u)
    today = datetime.date.today().isoformat()
    x = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        x.append('  <url><loc>' + u + '</loc><lastmod>' + today + '</lastmod></url>')
    x.append('</urlset>')
    (docs / 'sitemap.xml').write_text('\n'.join(x) + '\n')
    (docs / 'urls.txt').write_text('\n'.join(urls) + '\n')
    print('SITEMAP urls', len(urls))


if __name__ == '__main__':
    main()
