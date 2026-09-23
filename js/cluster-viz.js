/* Offline scientific figures. All plots retain static, accessible fallbacks.
 * No inference is performed here. Synthetic measurement model: see article.
 */
'use strict';
(() => {
  const D = window.CLUSTER_DATA;
  if (!D || !window.Plotly) return;
  const $ = id => document.getElementById(id);
  const sum = a => a.reduce((x,y)=>x+y,0);
  const cfg = {responsive:true, displaylogo:false, scrollZoom:false,
    modeBarButtonsToRemove:['select2d','lasso2d','autoScale2d','toggleSpikelines'],
    toImageButtonOptions:{format:'png',scale:2,filename:'cluster-diagnostic'}};
  const base = () => ({autosize:true, height:460, margin:{l:76,r:28,t:58,b:65},
    font:{family:'Arial, sans-serif',size:13},
    legend:{orientation:'h',x:0,y:1.13,font:{size:12}},
    hovermode:'closest', dragmode:'pan', uirevision:'cluster-figures'});
  function axes(x,y) {return {xaxis:{title:{text:x,standoff:15},automargin:true,zeroline:false},
    yaxis:{title:{text:y,standoff:15},automargin:true,zeroline:false}};}
  function draw(id,traces,layout) {$(id).classList.add('plot-pending');return Plotly.react($(id),traces,layout,cfg);}
  function fallbackOff(fig) {fig.classList.add('interactive-ready');}
  function safe(promise,fig) {return promise.catch(err=>{
    console.error('Figure retained its static fallback:',err); fig.classList.remove('interactive-ready');
    const s=fig.querySelector('[role=status]');if(s)s.textContent='Interactive rendering is unavailable; the static view remains below.';
  });}
  function selectButtons(container, mode) {
    $(container).querySelectorAll('button[data-mode]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.mode===mode)));
  }
  function normalCdf(x) {
    // Abramowitz–Stegun approximation, max abs error ~ 8e-8; PDF exact below.
    const sign=x<0?-1:1,a=Math.abs(x)/Math.SQRT2,t=1/(1+.3275911*a);
    const er=1-(((((1.061405429*t-1.453152027)*t)+1.421413741)*t-.284496736)*t+.254829592)*t*Math.exp(-a*a);
    return .5*(1+sign*er);
  }
  function pdf(i,z) {
    const t=D.scene.t[i],s=D.scene.sigma[i],sh=[-.25,0,.25],w=[.04,.92,.04],sc=[1.5,1,1.5];
    let norm=0,v=0;
    for(let k=0;k<3;k++) {
      const mu=t-sh[k],sd=s*sc[k];
      norm+=w[k]*(normalCdf((Math.log(4.2)-mu)/sd)-normalCdf(-mu/sd));
      const u=(Math.log1p(z)-mu)/sd;
      v+=w[k]*Math.exp(-.5*u*u)/(Math.sqrt(2*Math.PI)*sd);
    }
    return (z<0||z>3.2)?0:v/(norm*(1+z));
  }
  function trap(y,x) {let out=0;for(let j=1;j<y.length;j++)out+=(y[j]+y[j-1])*(x[j]-x[j-1])*.5;return out;}
  function interp(x,xs,ys) {
    if(x<=xs[0])return ys[0];if(x>=xs[xs.length-1])return ys[ys.length-1];
    let lo=0,hi=xs.length-1;while(hi-lo>1){let m=(lo+hi)>>1;if(xs[m]<=x)lo=m;else hi=m;}
    return ys[lo]+(ys[hi]-ys[lo])*(x-xs[lo])/(xs[hi]-xs[lo]);
  }
  function examples(select) {
    D.examples.forEach(e=>{const o=document.createElement('option');o.value=e.index;o.textContent=e.label;select.append(o);});
  }
  function objectText(i) {return `${D.groups[D.scene.p[i]]} · catalogue row ${D.scene.row[i]} · H = ${D.scene.h[i].toFixed(2)} · simulated z = ${D.scene.z[i].toFixed(4)}`;}
  let sceneMode='rsd',sceneActive=false,profileActive=false,responseActive=false;
  const sceneFig=$('fig-scene'),profileFig=$('fig-profiles'),responseFig=$('fig-response');
  let sceneClickHook=false;
  function inspectGalaxy(i) {
    const sel=$('scene-object');let opt=Array.from(sel.options).find(o=>Number(o.value)===i);
    if(!opt){opt=document.createElement('option');opt.value=i;opt.textContent='Selected: '+objectText(i);sel.append(opt);}
    sel.value=i;$('scene-inspector').open=true;inspectRender();
  }
  function sceneRender() {
    const full=$('scene-range').value==='full',others=$('scene-others').checked;
    const zr=full?[0,3.2]:[.58,.94];const s=D.scene;
    let traces=[],layout=base(),message='';
    selectButtons('scene-modes',sceneMode);
    $('scene-others').disabled=sceneMode==='cloud';
    const bg=others&&sceneMode!=='cloud';
    const total=bg?7341:279;
    const pName=p=>`${D.groups[p]} (${p===0?183:p===1?96:7062})`;
    if(sceneMode==='pdz') {
      const a=D.maps[full?'full':'near'];
      const density=a.mass[0].map((row,j)=>row.map((v,k)=>(v+a.mass[1][j][k]+(bg?a.mass[2][j][k]:0))/(a.dx*a.dz)));
      traces=[{type:'heatmap',x:a.x,y:a.z,z:density,
        colorbar:{title:{text:'PDZ density<br>per arcmin'},thickness:14,len:.82},
        hovertemplate:'x = %{x:.2f} arcmin<br>z = %{y:.3f}<br>Σ PDZ / arcmin = %{z:.2f}<extra></extra>'}];
      Object.assign(layout,axes('Eastward offset [arcmin]','Possible redshift'));
      layout.xaxis.range=[-6,6];layout.yaxis.range=zr;layout.margin.r=105;
      const mass=sum(a.mass.slice(0,bg?3:2).map(m=>sum(m.map(sum))));
      message=`${total.toLocaleString()} galaxies. Visible-window probability mass: ${mass.toFixed(1)}; full-domain mass: ${total.toLocaleString()}. Analytic PDZ bin integrals, not point estimates or independent slice counts.`;
    } else if(sceneMode==='three'||sceneMode==='cloud') {
      const cloud=sceneMode==='cloud',pts=[];
      if(cloud)D.cloud.indices.forEach((i,j)=>D.cloud.z[j].forEach(z=>pts.push({i,p:s.p[i],x:s.x[i],y:s.y[i],z})));
      else s.p.forEach((p,i)=>{if(p<2||bg)pts.push({i,p,x:s.x[i],y:s.y[i],z:s.z[i]});});
      const colors=$('scene-plot')._fullLayout.colorway;
      $('scene-plot').hidden=true;$('scene-canvas-view').hidden=false;
      $('scene-status').textContent=cloud?'279 galaxies, each represented by 25 deterministic equal-probability PDZ nodes. A cloud sums to one; nodes are not additional galaxies. Drag or use the sliders to rotate; click a node to inspect its galaxy. Axes are angular offsets and redshift, not an isotropic physical volume.':`${total.toLocaleString()} galaxies in simulation redshift space, not true real-space galaxy positions. Drag or use sliders to rotate; click a point to inspect its full synthetic PDZ. Axes are angular offsets and redshift, not an isotropic physical volume.`;
      ClusterCanvas3D.render(pts,zr,colors,cloud,inspectGalaxy);fallbackOff(sceneFig);
      return Promise.resolve();
    } else {
      const sky=sceneMode==='sky';
      for(let p=0;p<(bg?3:2);p++) {
        const ids=s.p.flatMap((v,i)=>v===p?[i]:[]);
        traces.push({type:'scatter',mode:'markers',x:ids.map(i=>s.x[i]),y:ids.map(i=>sky?s.y[i]:s.z[i]),customdata:ids,
          name:pName(p),marker:{size:p===2?3.5:7,opacity:p===2?.25:.75,symbol:p===1?'triangle-up':'circle'},
          hovertemplate:'x = %{x:.2f} arcmin<br>'+ (sky?'y = %{y:.2f} arcmin':'simulated z = %{y:.4f}')+'<br>Click to inspect full PDZ<extra>%{fullData.name}</extra>'});
      }
      Object.assign(layout,axes('Eastward offset [arcmin]',sky?'Northward offset [arcmin]':'Galaxy redshift (simulation redshift space)'));
      layout.xaxis.range=[-6,6];layout.yaxis.range=sky?[-6,6]:zr;
      message=`${total.toLocaleString()} galaxies ${bg?'from all hosts':'from the two highlighted hosts'}. Same fixed H < 24 sample; changing the redshift view only changes the zoom. Click a galaxy to inspect its full synthetic PDZ.`;
    }
    $('scene-plot').hidden=false;$('scene-canvas-view').hidden=true;
    $('scene-status').textContent=message;
    return safe(draw('scene-plot',traces,layout).then(()=>{
      fallbackOff(sceneFig);
      if(!sceneClickHook) {
        $('scene-plot').on('plotly_click',ev=>{
          const i=ev.points[0].customdata;
          if(!Number.isInteger(i))return;
          inspectGalaxy(i);
        });sceneClickHook=true;
      }
    }),sceneFig);
  }
  function inspectRender() {
    const i=Number($('scene-object').value),z=D.reference.z;
    const q=z.map(v=>pdf(i,v));const layout=base();layout.height=300;layout.margin={l:72,r:22,t:20,b:57};
    Object.assign(layout,axes('Possible redshift (full support)','Source PDZ density'));
    layout.xaxis.range=[0,3.2];layout.yaxis.rangemode='tozero';layout.showlegend=false;
    $('scene-object-status').textContent=objectText(i)+'. One normalized distribution; the simulated redshift is shown for diagnosis only.';
    return draw('scene-object-plot',[{x:z,y:q,type:'scatter',mode:'lines',name:'Full source PDZ',line:{width:2},
       hovertemplate:'z = %{x:.3f}<br>PDZ = %{y:.3f}<extra></extra>'},
       {x:[D.scene.z[i],D.scene.z[i]],y:[0,Math.max(...q)],type:'scatter',mode:'lines',line:{dash:'dot',width:1},name:'Simulated redshift',hoverinfo:'skip'}],layout);
  }
  let profileMode='projected';
  function profileRender() {
    const key=$('profile-sample').value,a=D.profiles[key],r=a.r;
    selectButtons('profile-modes',profileMode);
    let traces=[],layout=base();layout.margin.t=83;
    Object.assign(layout,axes(profileMode==='projected'?'Projected radius R / rᵥᵢᵣ':'Real-space centre separation r / rᵥᵢᵣ',
      profileMode==='projected'?'Surface density [galaxies / (h⁻¹ Mpc)²]':'Other-centre density / reference'));
    layout.xaxis={...layout.xaxis,type:'log',range:[-1,Math.log10(5)],tickvals:[.1,.2,.5,1,2,5],ticktext:['0.1','0.2','0.5','1','2','5']};
    const add=(y,name,dash='solid',width=2)=>traces.push({x:r,y,name,type:'scatter',mode:'lines+markers',line:{dash,width},marker:{size:4},
      hovertemplate:'r / rᵥᵢᵣ = %{x:.3f}<br>density = %{y:.3f}<extra>%{fullData.name}</extra>'});
    if(profileMode==='projected') {
      layout.yaxis.type='log';
      add(a.total,'Total');add(a.primary.map(v=>v>0?v:null),'Primary host','dash');add(a.env,'Complementary / external','dashdot');add(a.random,'Matched random','dot');
      // A filled closed polygon is a descriptive distribution band, not error bars.
      const bi=r.map((_,i)=>i).filter(i=>a.env_lo[i]>0);
      traces.push({x:bi.map(i=>r[i]).concat([...bi].reverse().map(i=>r[i])),y:bi.map(i=>a.env_hi[i]).concat([...bi].reverse().map(i=>a.env_lo[i])),
        type:'scatter',mode:'lines',line:{width:0},fill:'toself',opacity:.18,
        name:'External 16–84% across halos',hoverinfo:'skip'});
      $('profile-status').textContent=`${a.n} halos, equal-halo mean. Galaxy redshift-space cylinder: ±20 h⁻¹ Mpc; 12 matched random apertures per halo. The band is the external population’s across-halo spread, not an error on the mean or a measured latent-field covariance. Total = primary + complementary.`;
    } else {
      layout.yaxis.rangemode='tozero';
      add(a.centre,'Other-centre mean');
      traces.push({x:r.concat([...r].reverse()),y:a.centre_hi.concat([...a.centre_lo].reverse()),type:'scatter',mode:'lines',
        line:{width:0},fill:'toself',opacity:.18,name:'16–84% across halos',hoverinfo:'skip'});
      add(r.map(()=>1),'Reference = 1','dash',1);
      $('profile-status').textContent=`Same ${a.n} conditioning halos. Other H < 24 central galaxies are located at their host centres using true_redshift_halo. The conditioning centre is removed; zero inner-shell counts are shown on a linear vertical axis. This is not a true 3D galaxy-density profile. The reference is the central density in zₕ ± 0.025.`;
    }
    layout.shapes=[{type:'line',xref:'x',x0:1,x1:1,yref:'paper',y0:0,y1:1,line:{dash:'dot',width:1}}];
    return safe(draw('profile-plot',traces,layout).then(()=>fallbackOff(profileFig)),profileFig);
  }
  function responseRender() {
    const i=Number($('response-object').value),z=D.reference.z,pr=D.reference.p;
    const zs=Number($('response-z').value),amp=Number($('response-a').value);
    $('response-z-out').value=zs.toFixed(3);$('response-a-out').value=amp.toFixed(1);
    const qs=z.map(v=>pdf(i,v));let qr=qs.map((v,j)=>v*(1+z[j])*pr[j]);const norm=trap(qr,z);qr=qr.map(v=>v/norm);
    const integrand=qr.map((v,j)=>v*(1+amp*Math.exp(-.5*((z[j]-D.meta.aligned_z)/.018)**2)));
    const ap=.15*interp(zs,z,qr)/interp(zs,z,pr),ae=trap(integrand,z),alloc=ap/(ap+ae);
    $('response-primary').textContent=ap.toFixed(3);$('response-external').textContent=ae.toFixed(3);$('response-allocation').textContent=alloc.toFixed(3);
    $('response-status').textContent=objectText(i)+'. Increasing the external enhancement changes the competing response, not this galaxy’s PDZ. Numbers describe one illustrative parameter state, not a fitted posterior membership.';
    const layout=base();Object.assign(layout,axes('Possible redshift','Probability density / response integrand'));
    layout.margin.t=88;layout.xaxis.range=$('response-range').value==='full'?[0,3.2]:[.3,1.4];layout.yaxis.rangemode='tozero';
    layout.shapes=[{type:'line',xref:'x',x0:zs,x1:zs,yref:'paper',y0:0,y1:1,line:{dash:'dot',width:1}}];
    const traces=[{x:z,y:qs,name:'Source PDZ',type:'scatter',mode:'lines',line:{dash:'dot',width:2}},
      {x:z,y:qr,name:'Reference-weighted qᵢ',type:'scatter',mode:'lines',line:{width:2}},
      {x:z,y:integrand,name:'External integrand qᵢ × H F',type:'scatter',mode:'lines',line:{dash:'dash',width:2}}];
    window.CLUSTER_RESPONSE_CHECK={ap,ae,alloc,qsIntegral:trap(qs,z),qrIntegral:trap(qr,z),zstar:zs,amp};
    return safe(draw('response-plot',traces,layout).then(()=>fallbackOff(responseFig)),responseFig);
  }
  examples($('scene-object'));examples($('response-object'));
  $('scene-modes').querySelectorAll('button[data-mode]').forEach(b=>b.addEventListener('click',()=>{sceneMode=b.dataset.mode;sceneRender();}));
  $('scene-range').addEventListener('change',sceneRender);$('scene-others').addEventListener('change',sceneRender);
  $('scene-object').addEventListener('change',inspectRender);$('scene-inspector').addEventListener('toggle',()=>{if($('scene-inspector').open)inspectRender();});
  $('profile-modes').querySelectorAll('button[data-mode]').forEach(b=>b.addEventListener('click',()=>{profileMode=b.dataset.mode;profileRender();}));
  $('profile-sample').addEventListener('change',profileRender);
  ['response-object','response-range'].forEach(id=>$(id).addEventListener('change',responseRender));
  // One update per animation frame keeps keyboard and touch sliders responsive.
  let pending=false;const requestResponse=()=>{if(!pending){pending=true;requestAnimationFrame(()=>{pending=false;responseRender();});}};
  ['response-z','response-a'].forEach(id=>$(id).addEventListener('input',requestResponse));
  $('response-reset').addEventListener('click',()=>{$('response-z').value=D.meta.primary_z.toFixed(3);$('response-a').value=4;$('response-object').value=D.examples[0].index;responseRender();});
  document.querySelectorAll('.enhance-controls').forEach(e=>e.hidden=false);
  const activate=fig=>{
    if(fig===sceneFig&&!sceneActive){sceneActive=true;sceneRender();}
    if(fig===profileFig&&!profileActive){profileActive=true;profileRender();}
    if(fig===responseFig&&!responseActive){responseActive=true;responseRender();}
  };
  if('IntersectionObserver' in window) {
    const observer=new IntersectionObserver(entries=>entries.forEach(e=>{if(e.isIntersecting){activate(e.target);observer.unobserve(e.target);}}),{rootMargin:'400px'});
    [sceneFig,profileFig,responseFig].forEach(f=>observer.observe(f));
  } else [sceneFig,profileFig,responseFig].forEach(activate);
  window.CLUSTER_VIZ={sceneRender,profileRender,responseRender,inspectRender,pdf,trap};
})();
