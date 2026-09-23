#!/usr/bin/env python3
"""Export the built article as a genuinely self-contained offline HTML document."""
from pathlib import Path
import re,base64,argparse,mimetypes
ROOT=Path(__file__).resolve().parents[1]
PAGE=ROOT/'writing/measuring-a-galaxy-cluster.html'
def main(output:Path):
 html=PAGE.read_text()
 def inline_css(m):
  path=(PAGE.parent/m.group(1)).resolve()
  return '<style>\n'+path.read_text()+'\n</style>'
 html=re.sub(r'<link rel="stylesheet" href="([^\"]+)">',inline_css,html)
 def inline_js(m):
  path=(PAGE.parent/m.group(1)).resolve()
  text=path.read_text().replace('</script','<\\/script')
  # Scripts are moved to the bottom because inline `defer` is not deferred.
  scripts.append('<script>\n'+text+'\n</script>')
  return ''
 scripts=[]
 html=re.sub(r'<script defer(?:="")? src="([^\"]+)"></script>',inline_js,html)
 html=html.replace('</body>', '\n'.join(scripts)+'\n</body>')
 # All local images and article/data download links are embedded as data URIs.
 cache={}
 def embed(m):
  attr,rel=m.groups()
  if not rel.startswith('../'):return m.group(0)
  path=(PAGE.parent/rel).resolve()
  if not path.exists() or not path.is_file():return m.group(0)
  if path.suffix.lower() in ['.html']:
   return m.group(0)
  if rel not in cache:
   mime=mimetypes.guess_type(path.name)[0] or 'application/octet-stream'
   if path.suffix=='.md':mime='text/plain;charset=utf-8'
   if path.suffix=='.csv':mime='text/csv;charset=utf-8'
   cache[rel]='data:'+mime+';base64,'+base64.b64encode(path.read_bytes()).decode()
  extra=f' download="{path.name}"' if attr=='href' and path.suffix not in ['.svg','.png'] else ''
  return f'{attr}="{cache[rel]}"{extra}'
 html=re.sub(r'(href|src)="([^\"]+)"',embed,html)
 html=re.sub(r'<nav class="nav" aria-label="Primary navigation">.*?</nav>',
   '<nav class="nav" aria-label="Article navigation"><a href="#main">Article</a><a href="#data">Data</a><a href="#references">References</a></nav>',html,flags=re.S)
 html=html.replace('href="../index.html"','href="#main"')
 html=html.replace('<a href="../work.html#cluster-refinement">cluster-refinement work at the Institut d’Astrophysique de Paris</a>',
   'cluster-refinement work at the Institut d’Astrophysique de Paris')
 html=html.replace('<a href="../writing.html">All writing</a> · ','')
 if re.search(r'(?:src|href)="\.\./',html):
  raise RuntimeError('Unresolved local link in standalone document')
 output.parent.mkdir(parents=True,exist_ok=True);output.write_text(html)
 print(f'Wrote {output}: {output.stat().st_size/1e6:.2f} MB, no runtime network dependency.')
if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('output',type=Path);main(ap.parse_args().output)
