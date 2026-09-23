#!/usr/bin/env python3
"""Check generated article structure and local deployable-site links."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import re
ROOT=Path(__file__).resolve().parents[1]
class Page(HTMLParser):
    def __init__(self):super().__init__();self.ids=[];self.links=[];self.images=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:self.ids.append(a['id'])
        if 'href' in a:self.links.append(a['href'])
        if 'src' in a:self.links.append(a['src'])
        if tag=='img':self.images.append(a)
errors=[];parsed={}
for path in list(ROOT.glob('*.html'))+list((ROOT/'writing').glob('*.html')):
    p=Page();p.feed(path.read_text());parsed[path.resolve()]=p
    if len(p.ids)!=len(set(p.ids)):errors.append(f'{path.name}: duplicate IDs')
for path,p in parsed.items():
    for link in p.links:
        u=urlsplit(link)
        if u.scheme or u.netloc:continue
        target=((ROOT/unquote(u.path[len('/portfolio/'):])).resolve() if u.path.startswith('/portfolio/') else (path.parent/unquote(u.path)).resolve()) if u.path else path
        if target.is_dir():target=target/'index.html'
        if not target.exists():errors.append(f'{path.relative_to(ROOT)}: missing {link}')
        elif u.fragment and target in parsed and unquote(u.fragment) not in parsed[target].ids:
            errors.append(f'{path.relative_to(ROOT)}: missing anchor {link}')
article=ROOT/'writing/measuring-a-galaxy-cluster.html';text=article.read_text();p=parsed[article.resolve()]
assert len(re.findall(r'class="equation"',text))==30
assert 'data-math-static="3.2.1"' in text
assert not re.search(r'<g[^>]*data-mml-node="merror"',text)
assert 'MATHPLACEHOLDER' not in text and '<!-- FIGURE:' not in text
assert len(re.findall('id="ref-',text))==14
assert all(a.get('alt') for a in p.images)
assert all(f'id="fig-{x}"' in text for x in ['scene','profiles','response'])
assert not re.search(r'<script[^>]+src="https?://',text)
assert not re.search(r'<link[^>]+(?:font|stylesheet)[^>]+href="https?://',text)
assert 'Derivation companion' not in (ROOT/'writing.html').read_text()
assert not (ROOT/'content/cluster-derivations.md').exists()
if errors:raise SystemExit('\n'.join(errors))
print(f'PASS: {len(parsed)} pages, local links/anchors, 30 equations, 14 references, all figure alt text, no remote runtime dependencies, no companion article.')
