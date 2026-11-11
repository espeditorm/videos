// Studio Dito engine — one canvas, every frame is a pure function of t.
// Exposes window.seek(t), window.READY, window.END, window.EV (sound events).
// Reads window.DNA (from dna.js), window.RIG (rig.js), window.WORDS (words.js), window.SHOTS (shot files).
(function(){
const W=1920,H=1080;
const D=window.DNA, C=D.colours;
const FONT='"DNAFont"';
const cv=document.getElementById('c'); cv.width=W; cv.height=H;
const X=cv.getContext('2d');
const IMG={};      // name -> HTMLImageElement
window.EV=[];      // {t,name,gain}
window.READY=false;

// ---------------------------------------------------------------- maths
const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
const lerp=(a,b,p)=>a+(b-a)*p;
const ease={
  inOut:p=>(p=clamp(p,0,1),p<.5?2*p*p:1-Math.pow(-2*p+2,2)/2),
  out:p=>(p=clamp(p,0,1),1-Math.pow(1-p,3)),
  in:p=>(p=clamp(p,0,1),p*p*p),
};
// motion personality (DNA)
const MOT={
  Bouncy:{spring:d=>1-Math.exp(-6.5*d)*Math.cos(13*d), pop:.3, kick:.1, squash:0, exit:.25, blend:.4},
  Snappy:{spring:d=>1-Math.exp(-10*d)*Math.cos(9*d), pop:.2, kick:.07, squash:0, exit:.18, blend:.3},
  Floaty:{spring:d=>1-Math.exp(-4.5*d)*Math.cos(8*d), pop:.4, kick:.1, squash:0, exit:.25, blend:.5},
  Punchy:{spring:d=>1-Math.exp(-9*d)*Math.cos(12*d), pop:.24, kick:.16, squash:1, exit:.22, blend:.35},
}[D.motion];
function spring(d){ return d<=0?0:MOT.spring(d); }
function pop(d){ // 0->1 with overshoot over MOT.pop seconds
  if(d<=0) return 0; const p=clamp(d/MOT.pop,0,1);
  return p>=1?1:1+2.9*Math.pow(p-1,3)+1.9*Math.pow(p-1,2);
}
function kick(d){ return d<=0?0:MOT.kick*Math.exp(-9*d)*Math.sin(22*d); }
// squash & stretch on arrival -> [sx,sy]
function squash(d){
  if(!MOT.squash||d<0) return [1,1];
  const p=clamp(d/0.2,0,1), k=(1-ease.out(p));
  const s=Math.sin(d*40)*Math.exp(-14*d);           // little wobble after
  return [1+0.25*k*Math.cos(p*Math.PI)+0.04*s, 1-0.2*k*Math.cos(p*Math.PI)-0.04*s];
}
function shake(d,A){ return d<0?[0,0]:[A*Math.exp(-8*d)*Math.sin(61*d), A*Math.exp(-8*d)*Math.cos(47*d)]; }
function exitS(d){ return d<=0?1:1-ease.in(d/MOT.exit); }
// seeded hash noise
function hash(n){ n=Math.sin(n*127.1+311.7)*43758.5453; return n-Math.floor(n); }
function noise1(x,seed){ const i=Math.floor(x), f=x-i, u=f*f*(3-2*f); return lerp(hash(i+seed*17.3),hash(i+1+seed*17.3),u)*2-1; }

// ---------------------------------------------------------------- loading
function load(name,src){ return new Promise(r=>{const i=new Image(); i.onload=()=>{IMG[name]=i;r()}; i.onerror=()=>{console.error('missing',src);r()}; i.src=src;}); }

// ---------------------------------------------------------------- words / S()
// WORDS = [{w:'word',s:start,e:end}]. S('exact words',n) -> start time of nth occurrence - 0.08
function norm(s){ return s.toLowerCase().replace(/[^a-z0-9' ]/g,'').trim(); }
function at(phrase,occ=1){
  const ws=(window.WORDS||[]).map(w=>norm(w.w)); const ph=norm(phrase).split(/\s+/);
  let seen=0;
  for(let i=0;i+ph.length<=ws.length;i++){
    let ok=true; for(let j=0;j<ph.length;j++) if(ws[i+j]!==ph[j]){ok=false;break;}
    if(ok && ++seen===occ) return window.WORDS[i].s;
  }
  throw new Error('phrase not found: '+phrase+' #'+occ);
}
function atEnd(phrase,occ=1){
  const ws=(window.WORDS||[]).map(w=>norm(w.w)); const ph=norm(phrase).split(/\s+/); let seen=0;
  for(let i=0;i+ph.length<=ws.length;i++){ let ok=true; for(let j=0;j<ph.length;j++) if(ws[i+j]!==ph[j]){ok=false;break;}
    if(ok && ++seen===occ) return window.WORDS[i+ph.length-1].e; }
  throw new Error('phrase not found: '+phrase);
}
// is speaker talking at t? (spans list [[s,e],..])
function talking(spans,t){ return (spans||[]).some(([s,e])=>t>=s&&t<=e); }

// ---------------------------------------------------------------- camera
// cam = {plate, zoom, fx, fy}  fx,fy = focus in plate px. Keeps the view inside the plate.
function camMatrix(plateName,zoom,fx,fy){
  const im=IMG[plateName]; const pw=im?im.width:W, ph=im?im.height:H;
  const base=Math.max(W/pw,H/ph); const s=base*zoom;
  const vw=W/s, vh=H/s;
  const cx=clamp(fx,vw/2,pw-vw/2), cy=clamp(fy,vh/2,ph-vh/2);
  return {s, tx:W/2-cx*s, ty:H/2-cy*s, pw, ph};
}
// camera move per DNA camera language: from [z,fx,fy] to [z,fx,fy] across [t0,t1]
function camMove(t,t0,t1,a,b,extra){
  const p=ease.inOut((t-t0)/Math.max(.001,t1-t0));
  let z=lerp(a[0],b[0],p), fx=lerp(a[1],b[1],p), fy=lerp(a[2],b[2],p);
  if(D.camera==='handheld-drift'){ fx+=6*noise1(t*0.3,1); fy+=6*noise1(t*0.3,2); }
  if(D.camera==='snap-zoom' && extra && extra.snaps){ for(const s of extra.snaps){ const d=t-s; if(d>0) z*=1+0.07*spring(d)*(d<1.2?1:Math.max(0,1-(d-1.2)/0.3)); } }
  return [z,fx,fy];
}

// ---------------------------------------------------------------- text
function font(px){ return `${px}px ${FONT}`; }
function textW(s,px){ X.font=font(px); return X.measureText(s).width; }
// word-pop entry: words pop one by one at 28 units/s (34 for short tags). units = chars.
function entryText(s,x,y,px,t0,t,opts={}){
  const rate=opts.rate||(s.length<=14?34:28); const align=opts.align||'left'; const col=opts.color||C.ink;
  X.font=font(px); X.textBaseline='alphabetic'; X.fillStyle=col;
  const words=s.split(' '); const total=textW(s,px); let cx=align==='center'?x-total/2:(align==='right'?x-total:x);
  let chars=0; const sp=textW(' ',px);
  for(const w of words){
    const ww=textW(w,px); const st=t0+chars/rate; const d=t-st;
    if(d>0){
      let sx=1,sy=1,sc=pop(d);
      if(D.text_entry==='word-pop'){ X.save(); X.translate(cx+ww/2,y-px*0.35); X.scale(sc,sc); X.fillText(w,-ww/2,px*0.35); X.restore(); }
      else if(D.text_entry==='typing'){ X.fillText(w,cx,y); }
      else if(D.text_entry==='mask-slide-up'){ const p=ease.out(d/0.25); X.save(); X.beginPath(); X.rect(cx-4,y-px*1.05,ww+8,px*1.35); X.clip(); X.fillText(w,cx,y+px*(1-p)); X.restore(); }
      else { const p=spring(d); X.fillText(w,cx,y-px*1.5*(1-p)); }
    }
    chars+=w.length+1; cx+=ww+sp;
  }
  return t0+s.length/rate;
}
function entryEvents(s,t0,rate){ rate=rate||(s.length<=14?34:28); let c=0; for(const w of s.split(' ')){ ev(t0+c/rate,'tick',0.5); c+=w.length+1; } }

// ---------------------------------------------------------------- sound events
const evSeen=new Set();
function ev(t,name,gain=1){ const k=name+'@'+t.toFixed(3); if(!evSeen.has(k)){ evSeen.add(k); window.EV.push({t:+t.toFixed(3),name,gain}); } }

// ---------------------------------------------------------------- card style
function cardPath(x,y,w,h,r){ X.beginPath(); X.roundRect(x,y,w,h,r); }
function card(x,y,w,h,fill=C.card){
  const cs=D.card_style, k=D.card;
  if(cs==='square-offset'){ X.fillStyle=C.dark; cardPath(x+k.offset,y+k.offset,w,h,k.radius); X.fill(); X.fillStyle=fill; cardPath(x,y,w,h,k.radius); X.fill(); }
  else if(cs==='rounded'){ X.save(); X.shadowColor='rgba(0,0,0,'+k.shadow.alpha+')'; X.shadowBlur=k.shadow.blur; X.shadowOffsetY=k.shadow.y; X.fillStyle=fill; cardPath(x,y,w,h,k.radius); X.fill(); X.restore(); }
  else if(cs==='pill-strip'){ X.fillStyle=fill; cardPath(x,y,w,h,h/2); X.fill(); X.fillStyle=C.headlineA; X.save(); cardPath(x,y,w,h,h/2); X.clip(); X.fillRect(x,y,k.strip+h/4,h); X.restore(); }
  else if(cs==='paper-note'){ X.fillStyle=fill; X.fillRect(x,y,w,h); X.fillStyle='rgba(255,255,255,.55)'; X.fillRect(x+w/2-50,y-14,100,28); }
  else { X.fillStyle=C.dark; cardPath(x-k.border,y-k.border,w+2*k.border,h+2*k.border,14); X.fill(); X.fillStyle=fill; cardPath(x,y,w,h,8); X.fill(); }
}

// ---------------------------------------------------------------- graphics kit
const G={};
// arrival transform helper: pop + punchy squash around an anchor
function arrive(t0,t,ax,ay,fn){
  const d=t-t0; if(d<0) return; const s=pop(d); const [sx,sy]=squash(d);
  X.save(); X.translate(ax,ay); X.scale(s*sx,s*sy); X.translate(-ax,-ay); fn(d); X.restore();
}
// Board: drops 420 px on the spring and swings 0.25 rad into place. lines: [str], px
G.board=function(t,t0,x,y,w,lines,opts={}){
  const d=t-t0; if(d<0) return; const px=opts.px||56, lh=px*1.25, pad=34, h=pad*2+lines.length*lh;
  const dy=-420*(1-spring(d)); const rot=0.25*Math.exp(-5*d)*Math.cos(9*d);
  X.save(); X.translate(x+w/2,y+dy); X.rotate(rot); X.translate(-w/2,0);
  X.fillStyle=C.dark; X.fillRect(w*0.2,-90,6,90); X.fillRect(w*0.8-6,-90,6,90);   // hanging cords
  card(0,0,w,h);
  lines.forEach((s,i)=>entryText(s.toUpperCase(),w/2,pad+lh*(i+0.8),px,t0+0.35+0.3*i+ (i? lines.slice(0,i).join(' ').length/28:0),t,{align:'center'}));
  X.restore();
};
G.boardEvents=function(t0,lines){ ev(t0,'whoosh',.6); ev(t0+0.3,'pop'); let acc=0; lines.forEach((s,i)=>{ entryEvents(s,t0+0.35+0.3*i+acc/28); acc+=s.length+1; }); };
// HUD date/place card at DNA position
G.hud=function(t,t0,kind,value,slot=0){
  const d=t-t0; if(d<0) return; const w=Math.max(330,140+textW(value.toUpperCase(),44)), h=120, m=40;
  let x,y; const pos=D.hud_position;
  if(pos==='top-left'){x=m;y=m+slot*(h+20);} else if(pos==='top-right'){x=W-m-w-8;y=m+slot*(h+20);} else if(pos==='bottom-left'){x=m;y=H-m-h-8-slot*(h+20);} else {x=m+slot*(w+24);y=24;}
  const s=d<0.32?pop(d*MOT.pop/0.32):1; const [sx,sy]=squash(d);
  X.save(); X.translate(x+w/2,y+h/2); X.scale(s*sx,s*sy); X.translate(-w/2,-h/2);
  card(0,0,w,h);
  // icon
  X.save(); X.translate(62,h/2);
  if(kind==='date'){ X.fillStyle=C.warm; X.beginPath(); X.roundRect(-30,-26,60,56,8); X.fill(); X.fillStyle=C.card; X.fillRect(-22,-10,44,32); X.fillStyle=C.warm; for(let i=0;i<3;i++) X.fillRect(-16+i*13,-2,8,8); X.fillStyle=C.dark; X.fillRect(-18,-34,6,14); X.fillRect(12,-34,6,14); }
  else { X.fillStyle=C.alert; X.beginPath(); X.arc(0,-8,22,Math.PI,0); X.lineTo(0,34); X.closePath(); X.fill(); X.fillStyle=C.card; X.beginPath(); X.arc(0,-8,9,0,7); X.fill(); }
  X.restore();
  X.fillStyle=C.label; X.font=font(26); X.fillText(kind==='date'?'DATE:':'PLACE:',112,46);
  entryText(value.toUpperCase(),112,96,44,t0+0.2,t);
  X.restore();
};
G.hudEvents=function(t0,value){ ev(t0,'pop'); entryEvents(value,t0+0.2); };
// Tag (triangle-pointer): label card with a small triangle pointing at (px,py). side: 'up'|'down'|'left'|'right' = where the label sits
G.tag=function(t,t0,px,py,label,opts={}){
  const d=t-t0; if(d<0) return; const fill=opts.fill||C.ink; const fg=(fill===C.highlight||fill===C.warm||fill===C.card)?C.ink:'#ffffff';
  const fs=40, w=textW(label.toUpperCase(),fs)+48, h=72, gap=opts.gap||26, side=opts.side||'up';
  let bx=px-w/2, by=py-gap-h; if(side==='down'){by=py+gap;} if(side==='left'){bx=px-gap-w;by=py-h/2;} if(side==='right'){bx=px+gap;by=py-h/2;}
  const dExit=opts.out!=null?t-opts.out:-1; const es=exitS(dExit); if(es<=0) return;
  const p=clamp(d/0.2,0,1);
  arrive(t0,t,px,py,()=>{
    X.save(); X.translate(px,py); X.scale(es,es); X.translate(-px,-py);
    // triangle
    X.fillStyle=fill; X.beginPath();
    if(side==='up'){ X.moveTo(px-16,by+h-1); X.lineTo(px+16,by+h-1); X.lineTo(px,py-4); }
    else if(side==='down'){ X.moveTo(px-16,by+1); X.lineTo(px+16,by+1); X.lineTo(px,py+4); }
    else if(side==='left'){ X.moveTo(bx+w-1,py-16); X.lineTo(bx+w-1,py+16); X.lineTo(px-4,py); }
    else { X.moveTo(bx+1,py-16); X.lineTo(bx+1,py+16); X.lineTo(px+4,py); }
    X.fill();
    card(bx,by,w,h,fill);
    X.globalAlpha=p; X.fillStyle=fg; X.font=font(fs); X.fillText(label.toUpperCase(),bx+24,by+h/2+15); X.globalAlpha=1;
    X.restore();
  });
};
// Number card: label + big alert number rolling up
G.number=function(t,t0,x,y,label,value,opts={}){
  const d=t-t0; if(d<0) return; const roll=opts.roll||1.0, fmt=opts.fmt||(v=>Math.round(v).toLocaleString('en-US'));
  const v=value*ease.out(d/roll); const s=(opts.prefix||'')+fmt(v)+(opts.suffix||'');
  const full=(opts.prefix||'')+fmt(value)+(opts.suffix||''); const w=Math.max(textW(full,96),textW(label.toUpperCase(),28))+70, h=170;
  arrive(t0,t,x+w/2,y+h/2,()=>{ card(x,y,w,h); X.fillStyle=C.label; X.font=font(28); X.fillText(label.toUpperCase(),x+35,y+50); X.fillStyle=C.alert; X.font=font(96); X.fillText(s,x+35,y+145); });
};
// Red X over a box
G.redX=function(t,t0,cx,cy,r){
  const segs=[[[-1,-1],[1,1]],[[1,-1],[-1,1]]];
  X.save(); X.lineCap='round'; X.lineWidth=30;
  segs.forEach((sg,i)=>{ const st=t0+i*0.12, p=clamp((t-st)/0.11,0,1); if(p<=0) return;
    const [a,b]=sg; const x1=cx+a[0]*r,y1=cy+a[1]*r,x2=lerp(x1,cx+b[0]*r,p),y2=lerp(y1,cy+b[1]*r,p);
    X.strokeStyle='rgba(0,0,0,.22)'; X.beginPath(); X.moveTo(x1+5,y1+7); X.lineTo(x2+5,y2+7); X.stroke();
    X.strokeStyle=C.alert; X.beginPath(); X.moveTo(x1,y1); X.lineTo(x2,y2); X.stroke(); });
  X.restore();
};
G.redXEvents=function(t0){ ev(t0,'hit'); ev(t0+0.12,'hit',.8); };
// Stamp
G.stamp=function(t,t0,cx,cy,label,opts={}){
  const d=t-t0; if(d<0) return; const fs=opts.px||84; const w=textW(label.toUpperCase(),fs)+80, h=fs*1.6;
  const s=d<0.14?lerp(2.1,1,ease.in(d/0.14)):1+kick(d-0.14); const col=opts.color||C.alert;
  X.save(); X.translate(cx,cy); X.rotate(-0.12); X.scale(s,s); X.globalAlpha=d<0.14?ease.out(d/0.14):1;
  X.strokeStyle=col; X.lineWidth=9; X.beginPath(); X.roundRect(-w/2,-h/2,w,h,18); X.stroke();
  X.lineWidth=4; X.beginPath(); X.roundRect(-w/2+14,-h/2+14,w-28,h-28,10); X.stroke();
  X.fillStyle=col; X.font=font(fs); X.textAlign='center'; X.fillText(label.toUpperCase(),0,fs*0.36); X.restore();
};
G.stampEvents=function(t0){ ev(t0+0.13,'thud'); };
// Banner: full-width band, 92 px white caps, -0.02 rad, slides in from the left over 0.22 s
G.banner=function(t,t0,y,label,opts={}){
  const d=t-t0; if(d<0) return; const p=ease.out(d/0.22); const col=opts.color||C[D._accentKey||'headlineA'];
  const dExit=opts.out!=null?t-opts.out:-1; const ex=dExit>0?ease.in(dExit/0.22):0;
  X.save(); X.translate(-W*(1-p)+W*ex,y); X.rotate(-0.02);
  X.fillStyle=C.dark; X.fillRect(-40+8,8,W+80,150); X.fillStyle=col; X.fillRect(-40,0,W+80,150);
  X.fillStyle='#fff'; X.font=font(92); X.textAlign='center'; X.fillText(label.toUpperCase(),W/2,108); X.restore();
};
// Speech bubble with tail pointing to (tx,ty)
G.bubble=function(t,t0,x,y,text,tx,ty,opts={}){
  const d=t-t0; if(d<0) return; const fs=opts.px||44; const w=textW(text.toUpperCase(),fs)+70, h=fs*2.1;
  const dExit=opts.out!=null?t-opts.out:-1; const es=exitS(dExit); if(es<=0) return;
  arrive(t0,t,tx,ty,()=>{ X.save(); X.translate(tx,ty); X.scale(es,es); X.translate(-tx,-ty);
    X.fillStyle=C.card; X.beginPath(); X.moveTo(x+w*0.3,y+h-2); X.lineTo(tx,ty); X.lineTo(x+w*0.3+44,y+h-2); X.fill();
    card(x,y,w,h); X.fillStyle=C.card; X.beginPath(); X.moveTo(x+w*0.3+2,y+h-4); X.lineTo(tx,ty); X.lineTo(x+w*0.3+42,y+h-4); X.fill();
    entryText(text.toUpperCase(),x+35,y+h/2+fs*0.36,fs,t0+0.12,t); X.restore(); });
};
// "?" bobbing and "!" pop
G.qmark=function(t,t0,x,y){ const d=t-t0; if(d<0) return; arrive(t0,t,x,y,()=>{ X.save(); X.translate(x,y+8*Math.sin(t*3.2)); X.rotate(0.15*Math.sin(t*2.1)); X.fillStyle=C.warm; X.font=font(110); X.textAlign='center'; X.fillText('?',0,0); X.restore(); }); };
G.bang=function(t,t0,x,y){ const d=t-t0; if(d<0||d>1.4) return; const es=exitS(d-1.15); arrive(t0,t,x,y,()=>{ X.save(); X.translate(x,y); X.scale(es,es); X.rotate(0.12); X.fillStyle=C.warm; X.font=font(120); X.textAlign='center'; X.fillText('!',0,0); X.restore(); }); };
// Puff cloud
G.puff=function(t,t0,x,y,r=80){ const d=t-t0; if(d<0||d>0.6) return; const p=d/0.6; X.save(); X.fillStyle=C.card; X.globalAlpha=1-ease.in(p);
  for(let i=0;i<7;i++){ const a=i/7*Math.PI*2+0.4; const rr=r*(0.4+0.8*ease.out(p)); X.beginPath(); X.arc(x+Math.cos(a)*rr,y+Math.sin(a)*rr*0.6,r*0.45*(1-p*0.6),0,7); X.fill(); } X.restore(); };
G.speedLines=function(t,t0,t1,x,y,dir=-1){ if(t<t0||t>t1) return; X.save(); X.strokeStyle=C.card; X.lineCap='round'; X.lineWidth=8;
  for(let i=0;i<5;i++){ const ph=((t*3+i*0.23)%1); X.globalAlpha=1-ph; const yy=y-60+i*30, xx=x+dir*(40+ph*120); X.beginPath(); X.moveTo(xx,yy); X.lineTo(xx+dir*70,yy); X.stroke(); } X.restore(); };
G.vignette=function(k=0.35){ const g=X.createRadialGradient(W/2,H/2,H*0.35,W/2,H/2,H*0.95); g.addColorStop(0,'rgba(0,0,0,0)'); g.addColorStop(1,`rgba(10,8,30,${k})`); X.fillStyle=g; X.fillRect(0,0,W,H); };
G.tint=function(col,a){ X.save(); X.globalAlpha=a; X.fillStyle=col; X.fillRect(0,0,W,H); X.restore(); };
// Write words onto a blank rectangle in the plate (plate coords, drawn inside the camera transform)
G.write=function(t,t0,rect,lines,opts={}){
  const [x,y,w,h]=rect; const n=lines.length; let px=opts.px||Math.min(h/(n*1.35),opts.maxPx||90);
  for(const s of lines) while(textW(s.toUpperCase(),px)>w*0.9&&px>12) px-=2;
  const lh=h/n; let acc=0;
  lines.forEach((s,i)=>{ entryText(s.toUpperCase(),x+w/2,y+lh*i+lh/2+px*0.36,px,t0+i*0.3+acc/28,t,{align:'center',color:opts.color||C.ink}); acc+=s.length+1; });
};
G.writeEvents=function(t0,lines){ let acc=0; lines.forEach((s,i)=>{ entryEvents(s,t0+i*0.3+acc/28); acc+=s.length+1; }); };

// ---------------------------------------------------------------- characters
// contact shadow
function shadow(x,y,w){ X.save(); X.fillStyle='rgba(20,14,40,0.28)'; X.beginPath(); X.ellipse(x,y,w*0.42,w*0.08,0,0,7); X.fill(); X.restore(); }
// sprite figure (side/back/pose sheet sprites stay whole)
// opts: {x,y (feet), h (target height), t0 enter, hop, flip, walk:{from,to,t0,t1}, dark, rock}
function figure(t,img,o){
  const im=IMG[img]; if(!im) return; const d=t-(o.t0||-9); if(d<0) return;
  const s=o.h/im.height; const w=im.width*s;
  let x=o.x,y=o.y,rot=0,bob=0;
  if(o.walk){ const p=clamp((t-o.walk.t0)/(o.walk.t1-o.walk.t0),0,1); x=lerp(o.walk.from,o.walk.to,p);
    if(p>0&&p<1){ const stepLen=o.h*0.26*1.5, ph=Math.abs(x-o.walk.from)/stepLen*Math.PI; bob=Math.abs(Math.sin(ph))*o.h*0.022; rot=0.035*Math.sin(ph); } }
  const breath=1+0.009*Math.sin(2.3*t+(o.seed||0));
  const ent=spring(d); const [sx,sy]=squash(d); const hop=o.hop?Math.max(0,Math.sin(clamp(d/0.35,0,1)*Math.PI))*o.h*0.15:0;
  const es=exitS(o.out!=null?t-o.out:-1); if(es<=0) return;
  shadow(x,y,w*0.8*es);
  X.save(); X.translate(x,y-bob-hop); X.rotate(rot+(o.rock?o.rock*Math.sin(t*2):0)); X.scale((o.flip?-1:1)*ent*sx*es,breath*ent*sy*es);
  if(o.dark) X.filter=`brightness(${1-o.dark})`;
  if(o.shake){ const [a,b]=[Math.sin(t*70)*o.shake,0]; X.translate(a,b); }
  X.drawImage(im,-w/2,-o.h,w,o.h); X.restore();
}

// puppet arms: two-bone IK. Target in units of L=L1+L2 relative to the shoulder (x right, y down).
const POSES={
  down:[[-0.04,0.97],[0.04,0.97],'mitt','mitt'], rest:[[-0.1,0.9],[0.1,0.9],'mitt','mitt'],
  hips:[[-0.42,0.55],[0.42,0.55],'fist','fist'], point:[[-0.1,0.9],[0.86,-0.32],'mitt','point'],
  present:[[-0.1,0.9],[0.75,0.25],'mitt','open'], shrug:[[-0.62,0.12],[0.62,0.12],'open','open'],
  up:[[-0.32,-0.9],[0.32,-0.9],'open','open'], head:[[0.15,-0.62],[-0.15,-0.62],'open','open'],
  chin:[[-0.1,0.9],[-0.05,-0.12],'mitt','fist'], hold:[[0.42,0.45],[-0.42,0.45],'mitt','mitt'],
  wave:[[-0.1,0.9],[0.5,-0.75],'mitt','open'], stop:[[-0.1,0.9],[0.55,-0.1],'mitt','open'],
  cheer:[[-0.55,-0.75],[0.55,-0.75],'fist','fist'],
};
function ik(sx,sy,tx,ty,L1,L2,bendSign){
  let dx=tx-sx, dy=ty-sy, dist=Math.hypot(dx,dy); const maxd=L1+L2-0.5; if(dist>maxd){ dx*=maxd/dist; dy*=maxd/dist; dist=maxd; }
  const a=Math.atan2(dy,dx); const cosA=clamp((L1*L1+dist*dist-L2*L2)/(2*L1*dist),-1,1); const a1=a+bendSign*Math.acos(cosA);
  const ex=sx+Math.cos(a1)*L1, ey=sy+Math.sin(a1)*L1; return [ex,ey,sx+dx,sy+dy];
}
function hand(x,y,ang,shape,r,skin){
  X.save(); X.translate(x,y); X.rotate(ang); X.fillStyle=skin;
  if(shape==='fist'){ X.beginPath(); X.arc(0,0,r*1.05,0,7); X.fill(); }
  else if(shape==='open'){ X.beginPath(); X.ellipse(r*0.3,0,r*1.25,r*0.95,0,0,7); X.fill(); X.beginPath(); X.ellipse(-r*0.1,-r*0.95,r*0.32,r*0.55,-0.5,0,7); X.fill(); }
  else if(shape==='point'){ X.beginPath(); X.arc(0,0,r,0,7); X.fill(); X.beginPath(); X.roundRect(0,-r*0.32,r*2.1,r*0.64,r*0.32); X.fill(); }
  else { X.beginPath(); X.ellipse(r*0.2,0,r*1.15,r*0.95,0,0,7); X.fill(); X.beginPath(); X.ellipse(-r*0.1,-r*0.8,r*0.3,r*0.5,-0.4,0,7); X.fill(); }
  X.restore();
}
function rgb(a,k=1){ return `rgb(${Math.round(a[0]*k)},${Math.round(a[1]*k)},${Math.round(a[2]*k)})`; }
function drawArm(R,side,target,shape,sc,front){
  const S=R.sockets[side]; const L=R.L1+R.L2; const sgn=1;
  const tx=S.x+target[0]*L, ty=S.y+target[1]*L;
  const bend=side==='l'?-1:1;
  const [ex,ey,hx,hy]=ik(S.x,S.y,tx,ty,R.L1,R.L2,(ty<S.y?-bend:bend));
  const sleeve=front?rgb(R.sleeve):rgb(R.sleeve,0.82);
  X.lineCap='round'; X.lineJoin='round'; X.lineWidth=R.T;
  X.strokeStyle=sleeve; X.beginPath(); X.moveTo(S.x,S.y); X.lineTo(ex,ey); X.stroke();
  // forearm: sleeve to just past the elbow, then skin
  const mx=lerp(ex,hx,0.25), my=lerp(ey,hy,0.25);
  X.strokeStyle=sleeve; X.beginPath(); X.moveTo(ex,ey); X.lineTo(mx,my); X.stroke();
  X.strokeStyle=rgb(R.skin); X.lineWidth=R.T*0.82; X.beginPath(); X.moveTo(mx,my); X.lineTo(hx,hy); X.stroke();
  hand(hx,hy,Math.atan2(hy-ey,hx-ex),shape,R.T*0.62,rgb(R.skin));
}
// puppet: o={x,y(feet),h, pose:'rest' | [[t,pose],...], talk:[[s,e]], t0, seed, flip, dark, mood}
function poseAt(o,t){
  const seq=typeof o.pose==='string'?[[-99,o.pose]]:o.pose; let cur=seq[0][1], prev=cur, ts=-99;
  for(const [tt,p] of seq){ if(t>=tt){ prev=cur; cur=p; ts=tt; } }
  const k=ease.inOut((t-ts)/MOT.blend); const A=POSES[prev], B=POSES[cur];
  return { l:[lerp(A[0][0],B[0][0],k),lerp(A[0][1],B[0][1],k)], r:[lerp(A[1][0],B[1][0],k),lerp(A[1][1],B[1][1],k)], hl:k<.5?A[2]:B[2], hr:k<.5?A[3]:B[3] };
}
function puppet(t,name,o){
  const R=window.RIG[name]; const body=IMG[name+'_body'], head=IMG[name+'_head']; if(!R||!body) return;
  const d=t-(o.t0||-9); if(d<0) return; const es=exitS(o.out!=null?t-o.out:-1); if(es<=0) return;
  const sc=o.h/R.figH; const seed=o.seed||1;
  const ent=spring(d); const [sx,sy]=squash(d); const hop=o.hop?Math.max(0,Math.sin(clamp(d/0.35,0,1)*Math.PI))*o.h*0.15:0;
  let bob=0, rot=0, x=o.x;
  if(o.walk){ const p=clamp((t-o.walk.t0)/(o.walk.t1-o.walk.t0),0,1); x=lerp(o.walk.from,o.walk.to,p); if(p>0&&p<1){ const ph=t*7; bob=Math.abs(Math.sin(ph))*o.h*0.022; rot=0.035*Math.sin(ph);} }
  const breath=1+0.009*Math.sin(2.3*t+seed);
  shadow(x,o.y,R.w*sc*0.55*es);
  X.save(); X.translate(x,o.y-bob-hop); X.rotate(rot); X.scale((o.flip?-1:1)*sc*ent*sx*es, sc*ent*sy*es*breath);
  if(o.shake) X.translate(Math.sin(t*70)*o.shake/sc,0);
  if(o.dark) X.filter=`brightness(${1-o.dark})`;
  X.translate(-R.neck.x,-R.bottom);
  const P=poseAt(o,t);
  // arms behind the body when hands go behind (never in this build) — draw back-facing arms first when pose y<0? keep in front.
  X.drawImage(body,0,0);
  // head with nod
  const talkNow=talking(o.talk,t);
  const nod=talkNow?0.025*Math.sin(7*t+seed)+0.02*Math.sin(11.3*t+seed):0.025*Math.sin(2.1*t+seed);
  X.save(); X.translate(R.neck.x,R.neck.y); X.rotate(nod+(o.tilt||0)); X.translate(-R.neck.x,-R.neck.y);
  X.drawImage(head,0,0);
  // blink: every 2.7-4.2 s seeded
  let bt=hash(seed)*2, k=0; while(bt<t-0.14){ bt+=2.7+1.5*hash(seed*7+k++); }
  if(t>=bt&&t<bt+0.14){ for(const e of R.eyes){ X.fillStyle=rgb(R.skin); X.beginPath(); X.ellipse(e.x+e.w/2,e.y+e.h/2,e.w*0.75,e.h*0.75,0,0,7); X.fill(); X.strokeStyle='rgba(30,20,40,.85)'; X.lineWidth=Math.max(2,e.h*0.22); X.lineCap='round'; X.beginPath(); X.arc(e.x+e.w/2,e.y+e.h*0.25,e.w*0.55,0.25*Math.PI,0.75*Math.PI); X.stroke(); } }
  X.restore();
  // typing/drawing jitter on the right hand
  let rj=P.r; if(o.jitter&&talkNow) rj=[P.r[0]+6/R.figH*Math.sin(t*31),P.r[1]+6/R.figH*Math.cos(t*27)];
  drawArm(R,'l',P.l,P.hl,sc,true); drawArm(R,'r',rj,P.hr,sc,true);
  X.restore();
  // signs
  if(o.mood==='?') G.qmark(t,o.moodT||o.t0,x,o.y-o.h*1.12);
}

// ---------------------------------------------------------------- transitions
// shot transition: push-vertical. render(prevShot,t) & render(nextShot,t) offset vertically.
function shotTransition(t,tc,dur,drawA,drawB,kind){
  const p=ease.inOut((t-tc)/dur);
  kind=kind||D.shot_transition;
  if(kind==='push-vertical'){ X.save(); X.translate(0,-H*p); drawA(); X.restore(); X.save(); X.translate(0,H*(1-p)); drawB(); X.restore(); }
  else if(kind==='push-horizontal'){ X.save(); X.translate(-W*p,0); drawA(); X.restore(); X.save(); X.translate(W*(1-p),0); drawB(); X.restore(); }
  else if(kind==='circle-iris'){ drawA(); X.save(); X.beginPath(); X.arc(W/2,H/2,Math.hypot(W,H)/2*p,0,7); X.clip(); drawB(); X.restore(); }
  else if(kind==='diagonal-slats'){ drawA(); X.save(); X.beginPath(); for(let i=0;i<3;i++){ const q=clamp(p*1.6-i*0.3,0,1); const x0=-W*0.4+i*W*0.6; X.moveTo(x0,H); X.lineTo(x0+W*0.6*q*1.8,H); X.lineTo(x0+W*0.6*q*1.8+H*0.5,0); X.lineTo(x0+H*0.5,0);} X.clip(); drawB(); X.restore(); }
  else { drawA(); X.save(); X.globalAlpha=p; drawB(); X.restore(); }
}
// chapter transition: big paint swipe in the transition fill. 0.2 s cover, 0.2 s clear.
function chapterSwipe(t,tc){
  const d=t-(tc-0.2); if(d<0||d>0.4) return; const cover=d<0.2; const p=ease.inOut(cover?d/0.2:(d-0.2)/0.2);
  X.save(); X.fillStyle=C.transition; X.beginPath();
  const lead=cover?-W*0.3+p*(W*1.6):W*1.3, tail=cover?-W*0.4:-W*0.4+p*(W*1.8);
  // brush body with wavy edges
  const top=-60, bot=H+60;
  X.moveTo(tail,top); for(let y=top;y<=bot;y+=40){ X.lineTo(lead+40*Math.sin(y*0.013+2)+30*Math.sin(y*0.031),y); }
  for(let y=bot;y>=top;y-=40){ X.lineTo(tail+40*Math.sin(y*0.017)+25*Math.sin(y*0.041+1),y); }
  X.closePath(); X.fill();
  // bristle streaks at the leading edge
  X.fillStyle=C.transition; for(let i=0;i<9;i++){ const yy=60+i*115, len=80+60*hash(i+3); X.beginPath(); X.roundRect(lead-10+40*Math.sin(yy*0.013+2),yy,len,26,13); X.fill(); }
  X.restore();
}

// ---------------------------------------------------------------- timeline
// SHOTS: [{t0, t1, plate, cam:[[z,fx,fy],[z,fx,fy]], draw(t, ctx)} ...]  built by shot files via S().
window.ENG={X,W,H,C,D,G,IMG,ev,at,atEnd,spring,pop,kick,squash,shake,exitS,ease,lerp,clamp,figure,puppet,camMatrix,camMove,talking,entryText,textW,font,card,hash,noise1,chapterSwipe};
const shots=[]; window.SHOTLIST=shots;
// S('exact words', fn, opts) — shot starts 0.08 s before that phrase
window.S=function(phrase,fn,opts={}){ const t0=(typeof phrase==='number')?phrase:at(phrase,opts.occ||1)-0.08; shots.push({t0,fn,opts}); };
window.CHAPTER=function(phrase,opts={}){ const tc=(typeof phrase==='number')?phrase:at(phrase,opts.occ||1)-0.08; (window.CHAPTERS=window.CHAPTERS||[]).push(tc); };

function drawShot(sh,t){
  X.save(); const r=sh.fn(t,sh) ; X.restore(); return r;
}
// a shot fn draws its own plate via ENG.plate(t,...) helper:
window.ENG.plate=function(t,sh,plateName,a,b,inner,extra){
  const end=sh.t1; const [z,fx,fy]=camMove(t,sh.t0,end,a,b,extra);
  const m=camMatrix(plateName,z,fx,fy);
  X.save(); X.translate(m.tx,m.ty); X.scale(m.s,m.s);
  const im=IMG[plateName]; if(im) X.drawImage(im,0,0); else { X.fillStyle=C.dark; X.fillRect(0,0,W,H); }
  inner&&inner(m.s); X.restore();
};

function render(t){
  X.setTransform(1,0,0,1,0,0); X.fillStyle=C.dark; X.fillRect(0,0,W,H);
  let i=shots.length-1; while(i>0&&shots[i].t0>t) i--;
  const cur=shots[i]; const prev=shots[i-1];
  const TD=0.25;
  const hard=cur.opts.cut==='hard' || (window.CHAPTERS||[]).some(c=>Math.abs(c-cur.t0)<0.01);
  if(prev && t<cur.t0+TD && !hard){ shotTransition(t,cur.t0,TD,()=>drawShot(prev,t),()=>drawShot(cur,t)); }
  else drawShot(cur,t);
  for(const c of (window.CHAPTERS||[])) chapterSwipe(t,c);
  if(window.OVERLAY) window.OVERLAY(t);
}

window.seek=function(t){ render(t); return true; };
// motion-blur render: average n subframes spread over half a frame
const acc=document.createElement('canvas'); acc.width=W; acc.height=H; const AX=acc.getContext('2d');
window.seekBlur=function(t,fps=30,n=4){
  AX.clearRect(0,0,W,H);
  for(let i=0;i<n;i++){ render(t+(i/n-0.5)*(0.5/fps)); AX.globalAlpha=1/(i+1); AX.drawImage(cv,0,0); }
  AX.globalAlpha=1; X.setTransform(1,0,0,1,0,0); X.drawImage(acc,0,0); return true;
};

window.BOOT=async function(assets){
  const f=new FontFace('DNAFont',`url(${window.FONT_URL})`); await f.load(); document.fonts.add(f);
  await Promise.all(Object.entries(assets).map(([k,v])=>load(k,v)));
  if(window.BUILD) window.BUILD();
  shots.sort((a,b)=>a.t0-b.t0); for(let i=0;i<shots.length;i++) shots[i].t1=(shots[i+1]?shots[i+1].t0:window.END)+0.3;
  // dry run to collect sound events
  for(let t=0;t<window.END;t+=1/30) render(t);
  window.EV.sort((a,b)=>a.t-b.t);
  render(0); window.READY=true;
};
})();
