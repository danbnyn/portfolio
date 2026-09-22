#!/usr/bin/env python3
"""Offline browser checks of the actual published documents.

Local CSS, JavaScript and figure images are inlined into a temporary browser
preview; the source files are never changed. This requires no network access.
Checks rendering, controls, no-JS reading and print presentation, NOT HTTP status,
live CDN availability, or a deployed site. tools/check.py checks real link paths.

pip install playwright==1.57.0
playwright install chromium
python tools/browser_check.py
Uses CHROMIUM_EXECUTABLE or system Chromium when available.
"""
from pathlib import Path
import base64
import argparse
import json
import os
import re
import shutil
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'artifacts'
PAGES = ('index.html','about.html','work.html','writing.html',
         'writing/measuring-a-galaxy-cluster.html','writing/cluster-derivations.html')


def preview(name):
    path = ROOT/name
    source = path.read_text()
    def local(value):
        target = (path.parent/value).resolve()
        if not target.is_relative_to(ROOT):
            raise ValueError('Preview asset escapes project root')
        return target
    def stylesheet(match):
        return '<style>'+local(match.group(1)).read_text()+'</style>'
    def script(match):
        return '<script>'+local(match.group(1)).read_text()+'</script>'
    def image(match):
        asset = local(match.group(1))
        mime = 'image/svg+xml' if asset.suffix=='.svg' else 'image/png'
        return 'src="data:'+mime+';base64,'+base64.b64encode(asset.read_bytes()).decode()+'"'
    source = re.sub(r'<link rel="stylesheet" href="([^"]+)"\s*/?>',stylesheet,source)
    source = re.sub(r'<script defer(?:="")? src="([^"]+)"></script>',script,source)
    source = re.sub(r'src="(\.\./assets/cluster/[^\"]+)"',image,source)
    source = re.sub(r'<link rel="icon"[^>]+>','',source)
    # Scripts inserted by set_content execute during parsing. Move our one
    # deferred enhancement after the DOM it targets for equivalent execution.
    scripts = re.findall(r'<script>[\s\S]*?</script>',source)
    source = re.sub(r'<script>[\s\S]*?</script>','',source)
    return source.replace('</body>',''.join(scripts)+'</body>')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--widths', nargs='+', type=int, default=[320,390,768,1280])
    args = parser.parse_args()
    OUT.mkdir(exist_ok=True)
    results = ['Preview method: local assets inlined; HTTP navigation and deployment not tested.']
    with sync_playwright() as p:
        executable = os.environ.get('CHROMIUM_EXECUTABLE') or shutil.which('chromium')
        browser = p.chromium.launch(**({'executable_path':executable} if executable else {}))
        results.append('Chromium '+browser.version)
        for width in args.widths:
            context = browser.new_context(viewport={'width':width,'height':900})
            for name in PAGES:
                page = context.new_page()
                page.set_default_timeout(8000)
                print(f'Checking {name} at {width}px', flush=True)
                errors = []
                page.on('pageerror',lambda error:errors.append(str(error)))
                page.set_content(preview(name), wait_until='domcontentloaded')
                assert page.locator('h1').count() == 1
                assert page.locator('nav [aria-current="page"]').count() == 1
                overflow = page.evaluate('document.documentElement.scrollWidth > innerWidth+1')
                if overflow:
                    print('OVERFLOW:',name,width,page.evaluate('''[...document.querySelectorAll('body *')].map(e=>({tag:e.tagName,cls:e.className?.baseVal??e.className,w:e.getBoundingClientRect().width,r:e.getBoundingClientRect().right})).filter(e=>e.r>innerWidth+1).slice(0,12)'''))
                assert not overflow,(name,width)
                assert not errors,errors
                page.keyboard.press('Tab')
                assert page.locator('.skip-link').evaluate('(e)=>e===document.activeElement')
                page.keyboard.press('Enter')
                assert page.locator('#main').evaluate('(e)=>e===document.activeElement')
                if name.startswith('writing/'):
                    expected = 50 if 'derivations' in name else 20
                    assert page.locator('article[data-math-static]').count() == 1
                    assert page.locator('.equation').count() == expected
                    assert page.locator('mjx-assistive-mml').count() == page.locator('mjx-container').count()
                    assert page.locator('g[data-mml-node="merror"]').count() == 0
                    bad = page.locator('.equation').evaluate_all('''es=>es.map(e=>({id:e.id,box:e.getBoundingClientRect().left,ink:e.querySelector('[data-mml-node="math"]').getBoundingClientRect().left})).filter(x=>x.ink<x.box-1)''')
                    assert not bad,(name,width,bad)
                    if width == 320:
                        scrolls = page.locator('.equation').evaluate_all('''es=>es.filter(e=>e.scrollWidth>e.clientWidth+5).map(e=>{e.scrollLeft=20; const moved=e.scrollLeft>0;e.scrollLeft=0;return moved})''')
                        assert scrolls and all(scrolls), (name, 'wide equations must scroll')
                if width in (390,1280):
                    page.screenshot(path=str(OUT/f'{Path(name).stem}-{width}.png'),full_page=not name.startswith('writing/'),timeout=8000)
                results.append(f'{name}, {width}px: no page overflow, JavaScript errors or clipped equation starts; keyboard skip link works')
                page.close()
            context.close()

        context = browser.new_context(viewport={'width':390,'height':844})
        page = context.new_page()
        page.set_default_timeout(5000)
        page.set_content(preview('writing/measuring-a-galaxy-cluster.html'), wait_until='domcontentloaded')
        figure = page.locator('[data-scene]')
        for text,target in [('Reveal host labels','scene-hosts'),('Redshift space','scene-redshift'),('On the sky','scene-sky')]:
            button = figure.get_by_role('button',name=text,exact=True)
            button.click()
            assert button.get_attribute('aria-pressed') == 'true'
            assert page.locator('#'+target).is_visible()
            assert figure.locator('.scene-panel:visible').count() == 1
        button = figure.get_by_role('button',name='Reveal host labels')
        button.focus(); page.keyboard.press('Enter')
        assert page.locator('#scene-hosts').is_visible()
        page.screenshot(path=str(OUT/'scene-mobile.png'))
        page.emulate_media(media='print')
        assert figure.locator('.scene-panel:visible').count() == 3
        page.emulate_media(media='screen')
        page.locator('.citation a').first.click()
        assert page.url.endswith('#ref-amico')
        results.append('Scene buttons, keyboard activation, print all-view fallback, reference anchors: passed')
        context.close()

        context = browser.new_context(java_script_enabled=False,viewport={'width':390,'height':844})
        page = context.new_page()
        page.set_default_timeout(5000)
        page.set_content(preview('writing/measuring-a-galaxy-cluster.html'), wait_until='domcontentloaded')
        assert page.locator('.scene-panel:visible').count() == 3
        assert page.locator('.figure-controls:visible').count() == 0
        assert page.locator('.equation > mjx-container > svg').count() == 20
        page.locator('.contents summary').click()
        assert page.locator('.contents nav').is_visible()
        page.set_content(preview('writing/cluster-derivations.html'), wait_until='domcontentloaded')
        assert page.locator('.equation > mjx-container > svg').count() == 50
        results.append('JavaScript disabled: all scene panels, native contents and all 70 numbered equations remain available')
        context.close(); browser.close()
    (OUT/('browser-results-'+'-'.join(map(str,args.widths))+'.json')).write_text(json.dumps(results,indent=2)+'\n')
    print('\n'.join(results))


if __name__=='__main__':
    main()
