#!/usr/bin/env python3
"""Exercise the offline article at desktop/mobile sizes and without JavaScript."""
from pathlib import Path
import argparse,json,tempfile,subprocess,sys,importlib.util
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]

def main(chromium:Path,output:Path|None=None):
    if output:output.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        doc=Path(tmp)/'article.html'
        subprocess.run([sys.executable,str(ROOT/'tools/export_standalone.py'),str(doc)],check=True)
        source=doc.read_text()
        with sync_playwright() as p:
            browser=p.chromium.launch(executable_path=str(chromium),headless=True,args=['--no-sandbox'])
            context=browser.new_context(viewport={'width':1440,'height':1050})
            requested=[];errors=[]
            context.route('**/*',lambda r:(requested.append(r.request.url),r.abort()))
            page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
            page.set_content(source,wait_until='load')
            for name in ['scene','profiles','response']:
                el=page.locator(f'#fig-{name}');el.scroll_into_view_if_needed()
                page.wait_for_function('(id)=>document.getElementById(id).classList.contains("interactive-ready")',arg=f'fig-{name}')
                if output:el.screenshot(path=str(output/f'{name}-desktop.png'))
            for mode in ['sky','rsd','pdz','three','cloud']:
                page.locator(f'#scene-modes [data-mode="{mode}"]').click();page.wait_for_timeout(120)
            assert page.locator('#scene-canvas-view').is_visible()
            before=page.locator('#canvas-rotation').input_value();page.locator('#canvas-rotation').focus();page.keyboard.press('ArrowRight')
            assert page.locator('#canvas-rotation').input_value()!=before
            page.select_option('#scene-range','full')
            assert '6,975' in page.locator('#canvas-view-status').inner_text()
            if output:page.locator('#fig-scene').screenshot(path=str(output/'scene-cloud-desktop.png'))
            page.locator('#scene-modes [data-mode="pdz"]').click();page.check('#scene-others')
            assert '7,341 galaxies' in page.locator('#scene-status').inner_text()
            mass=page.evaluate('''()=>{let a=document.getElementById('scene-plot').data[0].z;return a.flat().reduce((x,y)=>x+y,0)*CLUSTER_DATA.maps.full.dx*CLUSTER_DATA.maps.full.dz}''')
            assert abs(mass-7341)<.002
            page.locator('#scene-inspector summary').click()
            page.select_option('#scene-object',str(page.evaluate('CLUSTER_DATA.examples[2].index')))
            page.wait_for_timeout(100)
            assert len(page.evaluate("document.getElementById('scene-object-plot').data[0].y"))==1601
            page.select_option('#profile-sample','broad');assert '339 halos' in page.locator('#profile-status').inner_text()
            page.locator('#profile-modes [data-mode="centres"]').click()
            assert page.evaluate("document.getElementById('profile-plot')._fullLayout.yaxis.type")=='linear'
            page.select_option('#profile-sample','narrow');assert '162 conditioning halos' in page.locator('#profile-status').inner_text()
            def amp(v):
                page.locator('#response-a').evaluate('(e,v)=>{e.value=v;e.dispatchEvent(new Event("input",{bubbles:true}))}',str(v))
                page.wait_for_function('(v)=>CLUSTER_RESPONSE_CHECK.amp===v',arg=v)
                return page.evaluate('CLUSTER_RESPONSE_CHECK')
            low=amp(0);high=amp(12)
            assert abs(low['ae']-1)<1e-9 and high['ae']>low['ae'] and high['alloc']<low['alloc']
            assert abs(high['ap']-low['ap'])<1e-12
            page.select_option('#response-range','full');again=page.evaluate('CLUSTER_RESPONSE_CHECK')
            assert abs(again['ae']-high['ae'])<1e-12
            assert abs(again['qrIntegral']-1)<1e-10
            assert page.evaluate('document.documentElement.scrollWidth-innerWidth')==0
            page.set_viewport_size({'width':390,'height':844});page.wait_for_timeout(250)
            for name in ['scene','profiles','response']:
                el=page.locator(f'#fig-{name}');el.scroll_into_view_if_needed();page.wait_for_timeout(200)
                assert page.evaluate('document.documentElement.scrollWidth-innerWidth')==0
                if output:el.screenshot(path=str(output/f'{name}-mobile.png'))
            assert not page.locator('img').evaluate_all('(es)=>es.filter(e=>e.complete&&!e.naturalWidth).length')
            assert not errors,errors
            assert not requested,requested
            context.close()
            nojs=browser.new_context(java_script_enabled=False,viewport={'width':390,'height':844})
            nojs.route('**/*',lambda r:r.abort())
            page=nojs.new_page();page.set_content(source,wait_until='load')
            assert page.locator('.equation').count()==30
            assert page.locator('mjx-container').count()>100
            for name in ['scene','profiles','response']:
                assert page.locator(f'#fig-{name} > .static-fallback').is_visible()
                assert page.locator(f'#fig-{name} > .enhance-controls:visible').count()==0
            assert page.evaluate('document.documentElement.scrollWidth-innerWidth')==0
            if output:
                page.locator('#fig-scene').scroll_into_view_if_needed();page.locator('#fig-scene').screenshot(path=str(output/'scene-no-js.png'))
            nojs.close();browser.close()
    result={'status':'pass','desktop_width':1440,'mobile_width':390,'page_overflow_px':0,'script_errors':errors,'runtime_network_requests':requested,'full_pdz_map_probability_mass':mass,'expected_mass':7341,'three_d':'CPU-projected canvas; drag, sliders and keyboard controls','response_amp_zero':low,'response_amp_twelve':high,'static_no_javascript':'30 typeset equations and all three figure groups visible','scope':'Functional smoke test, not all-browser or assistive-technology certification; no inference validation.'}
    if output:(output/'browser-results.json').write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))
if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--chromium',type=Path,required=True);ap.add_argument('--output',type=Path)
    a=ap.parse_args();main(a.chromium,a.output)
