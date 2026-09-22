#!/usr/bin/env python3
"""Check static pages and local links. Run from any directory; no dependencies."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import re
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ('index.html', 'work.html', 'writing.html', 'about.html',
          'writing/measuring-a-galaxy-cluster.html', 'writing/cluster-derivations.html')
BASE = 'https://danbnyn.github.io/portfolio/'


class Page(HTMLParser):
    def __init__(self, path):
        super().__init__(convert_charrefs=True)
        self.path = path
        self.elements = []
        self.feed(path.read_text(encoding='utf-8'))

    def handle_starttag(self, tag, attrs):
        self.elements.append((tag, dict(attrs)))

    def select(self, tag):
        return [attrs for kind, attrs in self.elements if kind == tag]

    @property
    def ids(self):
        return [attrs['id'] for _, attrs in self.elements if 'id' in attrs]


def main():
    pages = {p.resolve(): Page(p) for p in ROOT.rglob('*.html') if '.git' not in p.parts and 'artifacts' not in p.parts}
    errors = []
    links = 0

    def require(ok, message, path):
        if not ok:
            errors.append(f'{path.relative_to(ROOT)}: {message}')

    for path, page in pages.items():
        require(len(page.select('h1')) == 1, 'expected one h1', path)
        require(len(page.select('main')) == 1, 'expected one main landmark', path)
        require(page.select('html')[0].get('lang') == 'en', 'missing English language', path)
        require(len(page.select('title')) == 1, 'missing page title', path)
        require(any(a.get('name') == 'description' and a.get('content') for a in page.select('meta')),
                'missing description', path)
        require(any(a.get('name') == 'viewport' for a in page.select('meta')), 'missing viewport', path)
        require(len(page.ids) == len(set(page.ids)), 'duplicate HTML id', path)
        require(any(a.get('class') == 'skip-link' for a in page.select('a')), 'missing skip link', path)
        relative = path.relative_to(ROOT).as_posix()
        if relative in PUBLIC:
            expected = BASE + ('' if relative == 'index.html' else relative)
            require(any(a.get('rel') == 'canonical' and a.get('href') == expected for a in page.select('link')),
                    'incorrect canonical URL', path)
            require(sum(a.get('aria-current') == 'page' for a in page.select('a')) == 1,
                    'expected one current navigation link', path)
        for tag, attrs in page.elements:
            if tag == 'img':
                require('alt' in attrs, 'image without alt text', path)
            if tag == 'a' and attrs.get('target') == '_blank':
                require('noopener' in attrs.get('rel', ''), 'new-tab link without noopener', path)
            value = attrs.get('href') if tag in ('a', 'link') else attrs.get('src')
            if value is None:
                continue
            links += 1
            require(bool(value.strip()), 'empty URL', path)
            url = urlsplit(value)
            if url.scheme or url.netloc:
                require(url.scheme in ('https', 'mailto'), f'unsupported URL: {value}', path)
                continue
            if url.path.startswith('/portfolio/'):
                target = ROOT / unquote(url.path[len('/portfolio/'):])
            elif url.path.startswith('/'):
                require(False, f'link escapes project base path: {value}', path)
                continue
            else:
                target = path.parent / unquote(url.path) if url.path else path
            target = target.resolve()
            if target.is_dir():
                target /= 'index.html'
            require(target.is_relative_to(ROOT) and target.is_file(), f'broken local link: {value}', path)
            if url.fragment and target in pages:
                require(unquote(url.fragment) in pages[target].ids, f'missing anchor: {value}', path)
        source = path.read_text(encoding='utf-8')
        require(not re.search(r'lorem ipsum|yourusername|via\.placeholder', source, re.I), 'template filler', path)

    template = pages[ROOT / 'templates/article.html']
    require(any(a.get('name') == 'robots' and 'noindex' in a.get('content', '') for a in template.select('meta')),
            'authoring template must be noindex', template.path)
    locations = [e.text for e in ET.parse(ROOT/'sitemap.xml').iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
    require(set(locations) == {BASE + ('' if p == 'index.html' else p) for p in PUBLIC},
            'sitemap must list only published pages', ROOT/'sitemap.xml')
    require((ROOT/'.nojekyll').is_file(), 'missing .nojekyll', ROOT/'index.html')
    if errors:
        print('\n'.join(errors), file=sys.stderr)
        return 1
    print(f'PASS: {len(pages)} HTML pages; {links} links/assets; metadata, landmarks, IDs and sitemap.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
