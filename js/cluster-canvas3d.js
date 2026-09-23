/* A small CPU-projected 3D viewer, so rotation also works without WebGL.
 * Coordinates remain x/y in arcminutes and z in redshift, with independent axis
 * scaling. Nodes carry probabilities; no interpolation or inference is done.
 */
'use strict';
window.ClusterCanvas3D = (()=>{
 let canvas,ctx,points=[],range=[.58,.94],palette=[],yaw=-.65,pitch=.4,projected=[],handler=null;
 let width=600,height=420,cloud=false,drag=null,moved=false;
 const el=id=>document.getElementById(id);
 function project(x,y,z) {
  const a=Math.cos(yaw)*x-Math.sin(yaw)*y,b=Math.sin(yaw)*x+Math.cos(yaw)*y;
  const depth=Math.cos(pitch)*b-Math.sin(pitch)*z, vertical=Math.sin(pitch)*b+Math.cos(pitch)*z;
  const scale=Math.min(width/3.25,height/3.65)/(1+.12*depth);
  return {x:width*.50+scale*a,y:height*.5-scale*vertical,d:depth};
 }
 function draw() {
  if(!canvas)return;
  width=canvas.parentElement.clientWidth;height=Math.min(490,Math.max(365,width*.73));
  const ratio=window.devicePixelRatio||1;
  canvas.width=width*ratio;canvas.height=height*ratio;canvas.style.width=width+'px';canvas.style.height=height+'px';
  ctx.setTransform(ratio,0,0,ratio,0,0);ctx.clearRect(0,0,width,height);
  const ink=getComputedStyle(canvas).color;
  ctx.strokeStyle=ink;ctx.fillStyle=ink;ctx.lineWidth=1;
  const corners=[];
  for(let i=0;i<8;i++)corners.push(project(i&1?1:-1,i&2?1:-1,i&4?1:-1));
  ctx.globalAlpha=.22;
  for(let i=0;i<8;i++)for(const bit of [1,2,4])if(!(i&bit)){
   const a=corners[i],b=corners[i|bit];ctx.beginPath();ctx.moveTo(a.x,a.y);ctx.lineTo(b.x,b.y);ctx.stroke();
  }
  projected=[];
  for(const p of points) {
   if(p.z<range[0]||p.z>range[1])continue;
   const a=project(p.x/6,p.y/6,(p.z-(range[0]+range[1])/2)*2/(range[1]-range[0]));
   projected.push({...a,i:p.i,p:p.p});
  }
  projected.sort((a,b)=>b.d-a.d);
  for(const p of projected) {
   ctx.globalAlpha=cloud?.24:(p.p===2?.20:.8);ctx.fillStyle=palette[p.p];
   const rad=cloud?1.8:(p.p===2?1.6:3.1);
   ctx.beginPath();
   if(p.p===1&&!cloud){ctx.moveTo(p.x,p.y-rad*1.25);ctx.lineTo(p.x+rad,p.y+rad);ctx.lineTo(p.x-rad,p.y+rad);ctx.closePath();}
   else ctx.arc(p.x,p.y,rad,0,2*Math.PI);
   ctx.fill();
  }
  ctx.globalAlpha=1;ctx.fillStyle=ink;ctx.font='12px Arial, sans-serif';ctx.textAlign='center';
  const labels=[[-0,-1.18,-1.1,'x [arcmin]: −6 to +6'],[-1.18,0,-1.1,'y [arcmin]: −6 to +6'],[-1.15,-1.15,0,`z: ${range[0].toFixed(2)}–${range[1].toFixed(2)}`]];
  for(const [x,y,z,text] of labels){const p=project(x,y,z);ctx.fillText(text,Math.max(74,Math.min(width-74,p.x)),Math.max(15,Math.min(height-8,p.y)));}
  el('canvas-rotation').value=Math.round(yaw*180/Math.PI);el('canvas-tilt').value=Math.round(pitch*180/Math.PI);
  el('canvas-rotation-out').value=Math.round(yaw*180/Math.PI)+'°';el('canvas-tilt-out').value=Math.round(pitch*180/Math.PI)+'°';
  el('canvas-view-status').textContent=cloud?`${projected.length.toLocaleString()} quadrature nodes in this display window; 25 nodes with weight 1/25 per full galaxy PDZ. Other hosts are not drawn in this cloud view.`:`${projected.length.toLocaleString()} simulated galaxy positions in this display window. The sample itself is unchanged.`;
 }
 function init(onSelect) {
  canvas=el('scene-canvas');ctx=canvas.getContext('2d');handler=onSelect;
  ['canvas-rotation','canvas-tilt'].forEach(id=>el(id).addEventListener('input',()=>{yaw=Number(el('canvas-rotation').value)*Math.PI/180;pitch=Number(el('canvas-tilt').value)*Math.PI/180;draw();}));
  el('canvas-reset').addEventListener('click',()=>{yaw=-.65;pitch=.4;draw();});
  canvas.addEventListener('pointerdown',e=>{drag={x:e.clientX,y:e.clientY,yaw,pitch};moved=false;canvas.setPointerCapture(e.pointerId);});
  canvas.addEventListener('pointermove',e=>{
   if(!drag)return;const dx=e.clientX-drag.x,dy=e.clientY-drag.y;
   if(Math.hypot(dx,dy)>3)moved=true;
   yaw=Math.max(-Math.PI,Math.min(Math.PI,drag.yaw+dx*.008));pitch=Math.max(-1.25,Math.min(1.25,drag.pitch-dy*.008));draw();
  });
  canvas.addEventListener('pointerup',e=>{
   if(drag&&!moved){const r=canvas.getBoundingClientRect(),x=e.clientX-r.left,y=e.clientY-r.top;let best=null,dist=64;
    for(const p of projected){const d=(p.x-x)**2+(p.y-y)**2;if(d<dist){best=p;dist=d;}}
    if(best&&handler)handler(best.i);
   }drag=null;
  });
  canvas.addEventListener('pointercancel',()=>{drag=null;});
  canvas.addEventListener('keydown',e=>{if(!['ArrowLeft','ArrowRight','ArrowUp','ArrowDown'].includes(e.key))return;e.preventDefault();
   if(e.key==='ArrowLeft')yaw-=.1;if(e.key==='ArrowRight')yaw+=.1;if(e.key==='ArrowUp')pitch+=.08;if(e.key==='ArrowDown')pitch-=.08;
   yaw=Math.max(-Math.PI,Math.min(Math.PI,yaw));pitch=Math.max(-1.25,Math.min(1.25,pitch));draw();});
  new ResizeObserver(()=>{if(!el('scene-canvas-view').hidden)draw();}).observe(canvas.parentElement);
 }
 function render(data,zrange,colors,isCloud,onSelect) {
  if(!canvas)init(onSelect);points=data;range=zrange;palette=colors;cloud=isCloud;draw();
  el('canvas-legend').innerHTML='';
  [...new Set(points.map(p=>p.p))].sort().forEach(p=>{
    const span=document.createElement('span');span.style.color=palette[p];span.textContent=(p===1?'▲ ':'● ')+['Primary host','Aligned halo','Other hosts'][p];el('canvas-legend').append(span);
  });
 }
 return {render,draw};
})();
