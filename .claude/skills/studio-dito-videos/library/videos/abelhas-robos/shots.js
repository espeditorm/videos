// Abelhas-robôs — Studio Dito. 4 chapters, motif: big chapter number stamped on each chapter's first plate.
window.HUD_LABELS={date:'DATA:',place:'LOCAL:'};
window.BUILD=function(){
const E=ENG,G=E.G,C=E.C,X=E.X,at=E.at,atEnd=E.atEnd;
const BUTTER=DNA.palette_colours['warm butter yellow'], CYAN=DNA.palette_colours['muted cyan'];
const W=window.WORDS, tEndV=W[W.length-1].e;
const NARR=[[W[0].s,tEndV]];                         // host = narrator: lips move while the voice runs
const ev=E.ev;

// ---------- helpers ----------
function shot(phrase,plate,a,b,inner,over,opts={}){
  S(phrase,(t,sh)=>{ X.save();
    if(opts.shake){ const [s0,A]=opts.shake; if(t>s0&&t<s0+0.7){ const [sx,sy]=E.shake(t-s0,A); X.translate(sx,sy); X.scale(1.02,1.02);} }
    E.plate(t,sh,plate,a,b,()=>inner&&inner(t,sh)); over&&over(t,sh); X.restore(); },opts);
}
// flying insect sprite: path(t)->[x,y]; wings flutter, body bob
function fly(t,img,o){
  if(t<o.t0||(o.t1!=null&&t>o.t1+0.3)) return; const im=E.IMG[img]; if(!im) return;
  const [x,y]=o.path(t); const s=o.h/im.height; const w=im.width*s;
  const es=E.exitS(o.t1!=null?t-o.t1:-1); if(es<=0) return; const ent=E.pop(t-o.t0);
  X.save(); X.translate(x,y+4*Math.sin(t*9+(o.seed||0))); X.scale((o.flip?-1:1)*ent*es,(1+0.05*Math.sin(t*70+(o.seed||0)))*ent*es);
  X.rotate(0.08*Math.sin(t*3+(o.seed||0))); if(o.dark) X.filter=`brightness(${1-o.dark})`;
  X.drawImage(im,-w/2,-o.h/2,w,o.h); X.restore();
}
const orbit=(cx,cy,rx,ry,sp,ph)=>t=>[cx+rx*Math.cos(t*sp+ph),cy+ry*Math.sin(t*sp*1.3+ph)];
const lerpPath=(x0,y0,x1,y1,t0,t1)=>t=>{const p=E.ease.inOut((t-t0)/(t1-t0));return [E.lerp(x0,x1,p),E.lerp(y0,y1,p)+30*Math.sin(t*4)];};
// motif: big chapter number stamped on the chapter's first plate (screen space, top-left area)
function chapterStamp(t,t0,n){ G.stamp(t,t0,250,230,'0'+n,{px:150,color:C.alert}); }
function chapterStampEv(t0){ G.stampEvents(t0); }
// figure clipped above a podium top (plate coords)
function behind(yCut,fn){ X.save(); X.beginPath(); X.rect(-5000,-5000,10000,5000+yCut); X.clip(); fn(); X.restore(); }

STING.intro(0,'Abelhas-robôs');

// ================= CHAPTER 1 =================
// S1 garden: imagine a world without bees
{ const t0=at('Imagina um mundo')-0.08, tGone=at('não existem mais'); chapterStampEv(t0+0.25);
  ev(t0+0.4,'pop'); ev(tGone,'boing',0.7); [0,1,2].forEach(i=>ev(tGone+0.05*i,'pop',0.5));
  shot('Imagina um mundo','p1_garden',[1.0,960,560],[1.05,900,600],t=>{
    E.puppet(t,'host',{x:760,y:985,h:520,t0:t0+0.35,hop:true,seed:3,talk:NARR,pose:[[-9,'rest'],[t0+0.6,'present'],[tGone,'shrug']]});
    [[1380,430,0],[560,380,2],[1150,330,4]].forEach(([x,y,p],i)=>{
      fly(t,'bee',{t0:t0+0.2+i*0.15,t1:tGone+0.05*i,h:90,seed:p,path:orbit(x,y,70,40,1.6,p)});
      G.puff(t,tGone+0.05*i,...orbit(x,y,70,40,1.6,p)(tGone+0.05*i),60);
    });
  },t=>chapterStamp(t,t0+0.25,1),{cut:'hard'});
}
// S2 dead garden: no buzz, no dance
{ const t0=at('sem aquele zumbido')-0.08, tD=at('sem a dança'), tFl=at('nas flores');
  ev(t0+0.3,'pop'); G.redXEvents(t0+0.9); ev(tD,'pop'); G.redXEvents(tD+0.4); ev(tFl,'pop');
  shot('sem aquele zumbido','q1_tl',[1.02,960,560],[1.1,1000,600],t=>{
    E.figure(t,'farmer',{x:1350,y:1000,h:470,t0:t0+0.2,hop:true,seed:2});
    // the bee that isn't there
    if(t>=t0+0.3){ X.save(); X.globalAlpha=0.9; fly(t,'bee',{t0:t0+0.3,h:120,seed:1,path:orbit(520,380,30,20,1.2,0)}); X.restore(); }
    G.redX(t,t0+0.9,520,380,90);
    if(t>=tD){ const im=E.IMG['flower']; if(im){ const p=E.pop(t-tD); X.save(); X.translate(980,330); X.scale(p,p); X.drawImage(im,-90,-90,180,180*im.height/im.width); X.restore(); } }
    G.redX(t,tD+0.4,980,410,90);
    G.tag(t,tFl,980,520,'SEM POLINIZAÇÃO',{side:'down',fill:C.alert});
  });
}
// S3 empty market: no vegetables or fruit
{ const t0=at('e pior sem vegetais')-0.08, tF=at('frutas');
  ev(t0+0.2,'pop'); ev(tF,'pop'); G.redXEvents(tF+0.35);
  shot('e pior sem vegetais','q1_tr',[1.05,900,560],[1.0,960,540],t=>{
    G.tag(t,t0+0.2,760,380,'VEGETAIS: 0',{side:'up',fill:C.ink});
    if(t>=tF){ const im=E.IMG['apple']; const p=E.pop(t-tF); X.save(); X.translate(1500,560); X.scale(p,p); X.drawImage(im,-90,-95,180,190); X.restore(); }
    G.redX(t,tF+0.35,1500,560,100);
  });
}
// S4 food plate: a third of the world's food
{ const t0=at('ou um terço')-0.08;
  ev(t0+0.3,'pop'); G.boardEvents(t0+0.8,['1/3']);
  shot('ou um terço','q1_br',[1.0,960,540],[1.12,860,520],t=>{
    G.tag(t,t0+0.3,700,420,'DEPENDE DAS ABELHAS',{side:'up',fill:C.alert});
  },t=>G.number(t,t0+0.8,1360,90,'dos alimentos do mundo',33,{roll:0.6,prefix:'',suffix:'%'}));
}
// S5 cinema: sounds like an apocalypse movie
{ const t0=at('Calma eu sei')-0.08, tA=at('apocalíptico');
  G.writeEvents(at('filme')-0.05,['O FIM','DAS ABELHAS']); ev(t0+0.2,'pop'); ev(tA,'boing',0.6);
  shot('Calma eu sei','q1_bl',[1.0,960,520],[1.08,980,480],t=>{
    G.write(t,at('filme')-0.05,[560,210,850,320],['O FIM','DAS ABELHAS'],{color:C.ink,maxPx:120});
    E.figure(t,'moviefan',{x:1500,y:1060,h:520,t0:t0+0.2,hop:true,seed:4,shake:t>tA&&t<tA+1.2?6:0});
    G.bang(t,tA,1500,500);
  });
}
// S6 newspaper: but it's a real concern
{ const t0=at('mas essa é uma')-0.08, tR=at('real');
  G.writeEvents(t0+0.25,['ABELHAS EM QUEDA']); G.stampEvents(tR);
  shot('mas essa é uma','q2_tl',[1.05,760,600],[1.12,700,560],t=>{
    X.save(); X.translate(745,465); X.rotate(-0.045); X.translate(-745,-465);
    G.write(t,t0+0.25,[400,400,690,130],['ABELHAS EM QUEDA'],{color:C.ink,maxPx:80}); X.restore();
  },t=>G.stamp(t,tR,1450,800,'REAL',{px:110}));
}
// S7 workshop: humanity finds a solution
{ const t0=at('Só que para cada')-0.08, tSol=at('solução'), tQ=at('E a solução');
  ev(t0+0.3,'pop'); ev(tSol,'ding',0.6); ev(tQ,'pop');
  shot('Só que para cada','q2_tr',[1.0,960,540],[1.1,1100,600],t=>{
    E.puppet(t,'host',{x:520,y:1080,h:560,t0:t0+0.2,hop:true,seed:3,talk:NARR,pose:[[-9,'rest'],[tSol,'up'],[tQ,'chin']]});
    G.bang(t,tSol,520,470);
    G.tag(t,tSol+0.2,1420,900,'SOLUÇÃO?',{side:'up',fill:C.ink});
    if(t>tQ) G.qmark(t,tQ,520,470);
  });
}
// S8 garden again: robot bees! (hard cut on the beat)
{ const t0=at('abelhas robôs')-0.08, tM=at('mini'), tP=at('polinizar plantas');
  ev(t0+0.02,'whoosh'); ev(tM,'pop'); ev(tP,'ding',0.6);
  shot('abelhas robôs','p1_garden',[1.12,1200,520],[1.04,1000,560],t=>{
    fly(t,'robobee',{t0:t0+0.1,h:120,seed:1,path:t=>t<tP?orbit(1150,420,160,60,1.4,0)(t):lerpPath(...orbit(1150,420,160,60,1.4,0)(tP),1520,690,tP,tP+0.8)(t)});
    fly(t,'robobee',{t0:t0+0.4,h:90,seed:3,path:orbit(700,330,120,50,1.8,2)});
    G.tag(t,tM,1150,330,'MINI-ROBÔ VOADOR',{side:'up',fill:C.ink});
  },t=>G.banner(t,t0+0.05,860,'ABELHAS-ROBÔS',{color:BUTTER,textColor:C.ink,out:tM-0.1}),{cut:'hard'});
}
// S9 lab: MIT researchers presented a prototype
{ const t0=at('Recentemente pesquisadores')-0.08, tMit=at('MIT apresentaram'), tPro=at('protótipo'), tVoo=at('imitar o voo');
  G.hudEvents(tMit,'MIT · EUA'); G.writeEvents(tPro,['PROTÓTIPO','ROBÔ-INSETO']); ev(tVoo,'pop');
  shot('Recentemente pesquisadores','p2_lab',[1.0,960,560],[1.06,900,520],t=>{
    const walkEnd=t0+1.3;
    if(t<walkEnd) E.figure(t,'lia_walk',{x:900,y:960,h:500,t0:t0,seed:6,walk:{from:-200,to:900,t0:t0,t1:walkEnd}});
    else E.puppet(t,'lia',{x:900,y:960,h:500,t0:walkEnd-0.05,seed:6,pose:[[-9,'rest'],[tPro,'present'],[tVoo,'point']],tilt:-0.05});
    G.write(t,tPro,[720,175,500,230],['PROTÓTIPO','ROBÔ-INSETO'],{color:BUTTER,maxPx:80});
    fly(t,'robobee',{t0:tVoo,h:80,seed:5,path:orbit(1300,520,90,40,2.2,1)});
  },t=>G.hud(t,tMit,'place','MIT · EUA'));
}
// S10 scale: lighter than a paper clip
{ const t0=at('Ele pesa menos')-0.08, tC=at('clipe de papel');
  G.writeEvents(t0+0.3,['< 1 G']); ev(tC,'pop');
  shot('Ele pesa menos','q2_bl',[1.05,760,520],[1.15,820,460],t=>{
    X.save(); X.translate(715,700); X.rotate(0.08); X.translate(-715,-700);
    G.write(t,t0+0.3,[480,630,470,140],['< 1 G'],{color:CYAN,maxPx:110}); X.restore();
    fly(t,'robobee',{t0:t0+0.15,h:110,seed:2,path:t=>[1040,190+12*Math.sin(t*3)]});
    G.tag(t,tC,960,360,'MENOS QUE UM CLIPE',{side:'up',fill:C.ink});
  });
}
// S11 stopwatch: flies for 17 minutes
{ const t0=at('consegue voar por')-0.08, t17=at('17');
  ev(t0+0.2,'tick',0.6); ev(t17,'pop');
  shot('consegue voar por','q2_br',[1.0,960,540],[1.08,900,560],t=>{
    const cx=690,cy=570,r=230, a=-Math.PI/2+Math.max(0,t-t0)*2.2;
    X.save(); X.lineCap='round'; X.strokeStyle=C.dark; X.lineWidth=14; X.beginPath(); X.moveTo(cx,cy); X.lineTo(cx+Math.cos(a)*r*0.8,cy+Math.sin(a)*r*0.8); X.stroke();
    for(let i=0;i<12;i++){ const b=i/12*Math.PI*2; X.lineWidth=6; X.beginPath(); X.moveTo(cx+Math.cos(b)*r*0.86,cy+Math.sin(b)*r*0.86); X.lineTo(cx+Math.cos(b)*r*0.96,cy+Math.sin(b)*r*0.96); X.stroke(); }
    X.fillStyle=C.alert; X.beginPath(); X.arc(cx,cy,16,0,7); X.fill(); X.restore();
    fly(t,'robobee',{t0:t0+0.2,h:100,seed:4,path:orbit(1300,330,140,50,2,0)});
  },t=>G.number(t,t17,1300,640,'tempo de voo',17,{roll:0.8,suffix:' MIN'}));
}
// S12 indoor farm: could pollinate big indoor farms
{ const t0=at('no futuro')-0.08, tF=at('fazendas indoor');
  G.writeEvents(tF,['FAZENDA INDOOR']); ev(t0+0.3,'pop');
  shot('no futuro','p5_farm',[1.0,960,560],[1.1,960,500],t=>{
    for(let i=0;i<5;i++) fly(t,'robobee',{t0:t0+0.15*i,h:60,seed:i,path:t=>[((t-t0)*260+i*400)%2100-100,620-i*70+20*Math.sin(t*2+i)]});
    E.figure(t,'lia_holdbee',{x:960,y:1010,h:470,t0:t0+0.3,hop:true,seed:6});
    G.write(t,tF,[745,285,410,180],['FAZENDA INDOOR'],{color:BUTTER,maxPx:60});
  });
}
// S13 lab again: sounds like an amazing advance
{ const t0=at('E em um mundo')-0.08, tD=at('desaparecendo'), tI=at('incrível');
  ev(tD,'pop'); G.stampEvents(tI);
  shot('E em um mundo','p2_lab',[1.08,1000,600],[1.0,960,560],t=>{
    E.puppet(t,'lia',{x:960,y:960,h:500,t0:t0+0.2,hop:true,seed:6,pose:[[-9,'hold'],[tI,'cheer']]});
    G.tag(t,tD,540,300,'ABELHAS: EM QUEDA',{side:'down',fill:C.alert});
    fly(t,'robobee',{t0:t0+0.2,h:90,seed:7,path:orbit(1300,420,100,50,2,0)});
  },t=>G.stamp(t,tI,1450,880,'AVANÇO INCRÍVEL',{px:72,color:C.success}));
}

// ================= CHAPTER 2 =================
CHAPTER('Mas aí é que entra');
// S14 TV room at night: a dark detail
{ const t0=at('Mas aí é que entra')-0.08, tS=at('sombrio'); chapterStampEv(t0+0.25);
  ev(t0+0.4,'pop'); ev(tS,'thud',0.5);
  shot('Mas aí é que entra','p3_tvroom',[1.0,960,560],[1.07,1000,600],t=>{
    E.puppet(t,'host',{x:820,y:985,h:500,t0:t0+0.35,hop:true,seed:3,talk:NARR,dark:0.25,pose:[[-9,'rest'],[tS,'chin']]});
    if(t>tS) G.qmark(t,tS,820,440);
  },t=>{ chapterStamp(t,t0+0.25,2); G.vignette(0.4); });
}
// S15 bedroom: I read the news
{ const t0=at('Assim que eu li')-0.08;
  ev(t0+0.3,'pop');
  shot('Assim que eu li','q3_tl',[1.0,700,560],[1.18,500,600],t=>{
    G.tag(t,t0+0.3,440,470,'A NOTÍCIA',{side:'up',fill:C.ink});
  },t=>G.vignette(0.35));
}
// S16 TV: the episode
{ const t0=at('lembrei do episódio')-0.08, tH=at('Hated'), tR=at('recomendo');
  ev(tH,'pop'); ev(tR,'pop'); ev(t0+0.3,'pop');
  shot('lembrei do episódio','p3_tvroom',[1.1,1300,520],[1.18,1450,480],t=>{
    X.save(); X.beginPath(); X.rect(1400,262,372,318); X.clip(); X.fillStyle='#141a33'; X.fillRect(1400,262,372,318);
    for(let i=0;i<9;i++) fly(t,'evilbee',{t0:t0,h:46,seed:i,path:t=>[1420+((t*90+i*53)%340),300+((i*67)%240)+15*Math.sin(t*3+i)]});
    X.restore();
    E.figure(t,'moviefan',{x:1120,y:1000,h:470,t0:t0+0.3,hop:true,seed:4,dark:0.25,shake:t>tH?3:0});
    G.tag(t,tH,1585,600,'EPISÓDIO DE 2016',{side:'down',fill:C.ink});
  },t=>{ G.bubble(t,tR,260,320,'RECOMENDO!',560,620,{px:46}); G.vignette(0.35); });
}
// S17 field with robot hives: robot bees made to pollinate
{ const t0=at('No episódio abelhas')-0.08, tN=at('abelhas naturais');
  ev(t0+0.3,'whoosh',0.5); ev(tN,'pop'); G.redXEvents(tN+0.4);
  shot('No episódio abelhas','q3_tr',[1.0,960,540],[1.1,1100,560],t=>{
    for(let i=0;i<6;i++) fly(t,'robobee',{t0:t0+0.2+i*0.12,h:55,seed:i,path:t=>[1700-((t-t0)*180+i*170)%1600,560-i*25+15*Math.sin(t*3+i)]});
    if(t>=tN){ fly(t,'bee',{t0:tN,h:110,seed:9,path:t=>[420,330]}); }
    G.redX(t,tN+0.4,420,330,80);
  });
}
// S18 hacker room: someone hacked the system
{ const t0=at('Só que alguém')-0.08, tS=at('o sistema');
  G.writeEvents(tS,['ACESSO','LIBERADO']); G.stampEvents(tS+0.6);
  shot('Só que alguém','q3_bl',[1.0,960,560],[1.1,900,520],t=>{
    G.write(t,tS,[750,280,350,220],['ACESSO','LIBERADO'],{color:C.alert,maxPx:56});
    E.figure(t,'hacker',{x:1500,y:1060,h:560,t0:t0+0.2,hop:true,seed:8,dark:0.15});
  },t=>{ G.stamp(t,tS+0.6,560,860,'SISTEMA INVADIDO',{px:66}); G.vignette(0.3); });
}
// S19 night street: machines turned into weapons
{ const t0=at('transformou essas máquinas')-0.08, tA=at('armas');
  ev(t0+0.2,'whoosh'); ev(tA,'hit');
  shot('transformou essas máquinas','q3_br',[1.0,960,540],[1.12,960,460],t=>{
    for(let i=0;i<14;i++) fly(t,'evilbee',{t0:t0+0.05*i,h:70+((i*13)%40),seed:i,path:t=>[((t-t0)*300+i*150)%2200-140,200+((i*97)%500)+25*Math.sin(t*4+i)]});
    G.tag(t,tA,960,700,'ARMAS',{side:'up',fill:C.alert});
  },t=>G.vignette(0.45),{shake:[tA,10]});
}
// S20 garden darkening: hope turned nightmare
{ const t0=at('O que começou')-0.08, tE=at('esperança'), tV=at('virou'), tP=at('pesadelo');
  ev(tE,'ding',0.5); ev(tV,'boing',0.6); G.stampEvents(tP);
  shot('O que começou','p1_garden',[1.0,960,540],[1.12,1100,460],t=>{
    const good=t<tV; fly(t,good?'robobee':'evilbee',{t0:t0+0.1,h:good?150:170,seed:2,path:orbit(1100,420,60,30,1.4,0)});
    G.puff(t,tV,1100,420,100);
    G.tag(t,tE,1100,560,'ESPERANÇA',{side:'down',fill:C.success,out:tV});
  },t=>{ G.tint('#1c2340',Math.min(0.55,Math.max(0,(t-tV)*0.8))); G.stamp(t,tP,620,820,'PESADELO',{px:96}); });
}

// ================= CHAPTER 3 =================
CHAPTER('Agora traz isso');
// S21 courtroom: who would be responsible?
{ const t0=at('Agora traz isso')-0.08, tE=at('E se alguém'), tQ=at('quem seria');
  chapterStampEv(t0+0.25); ev(t0+0.4,'pop'); G.writeEvents(tQ,['QUEM É','O CULPADO?']);
  shot('Agora traz isso','p4_court',[1.0,960,540],[1.06,960,500],t=>{
    E.puppet(t,'host',{x:960,y:1010,h:480,t0:t0+0.35,hop:true,seed:3,talk:NARR,pose:[[-9,'present'],[tE,'chin'],[tQ,'shrug']]});
    if(t>tE) G.qmark(t,tE,960,470);
    G.write(t,tQ,[715,75,490,230],['QUEM É','O CULPADO?'],{color:C.ink,maxPx:90});
  },t=>chapterStamp(t,t0+0.25,3));
}
// S22 factory: the manufacturer
{ const t0=at('o fabricante')-0.08;
  ev(t0+0.2,'pop'); ev(t0+0.5,'pop');
  shot('o fabricante','q4_tl',[1.0,960,560],[1.1,1000,600],t=>{
    E.figure(t,'boss',{x:1000,y:1060,h:560,t0:t0+0.15,hop:true,seed:9});
    G.tag(t,t0+0.5,1000,460,'O FABRICANTE',{side:'up',fill:C.ink});
  });
}
// S23 hacker room again: the hacker
{ const t0=at('o hacker')-0.08;
  ev(t0+0.3,'pop');
  shot('o hacker','q3_bl',[1.15,1300,600],[1.08,1200,580],t=>{
    E.figure(t,'hacker',{x:1450,y:1060,h:580,t0:t0+0.1,seed:8,dark:0.15});
    G.tag(t,t0+0.3,1450,440,'O HACKER',{side:'up',fill:C.alert});
  },t=>G.vignette(0.3));
}
// S24 gadget street: or us
{ const t0=at('ou nós')-0.08, tR=at('esquecemos dos riscos');
  ev(t0+0.3,'pop'); ev(tR,'pop');
  shot('ou nós','q4_tr',[1.0,960,560],[1.1,860,600],t=>{
    E.figure(t,'citizen',{x:760,y:1050,h:540,t0:t0+0.15,hop:true,seed:5});
    G.tag(t,t0+0.3,760,470,'NÓS',{side:'up',fill:BUTTER});
    if(t>tR) G.qmark(t,tR,930,520);
    G.tag(t,tR,1350,520,'INOVAÇÃO > RISCOS',{side:'up',fill:C.ink});
  });
}
// S25 courtroom full: and it's not just robot bees
{ const t0=at('E aqui não estou')-0.08, tA=at('abelhas robôs',3);
  G.writeEvents(t0+0.2,['FABRICANTE']); G.writeEvents(t0+0.5,['HACKER']); G.writeEvents(t0+0.8,['NÓS']); ev(tA,'pop');
  shot('E aqui não estou','p4_court',[1.08,960,640],[1.0,960,560],t=>{
    behind(655,()=>{ E.figure(t,'boss',{x:555,y:900,h:430,t0:t0+0.1,seed:9}); E.figure(t,'hacker',{x:955,y:900,h:430,t0:t0+0.25,seed:8}); E.figure(t,'citizen',{x:1365,y:900,h:410,t0:t0+0.4,seed:5}); });
    G.write(t,t0+0.2,[492,668,126,34],['FABRICANTE'],{color:C.ink,maxPx:22});
    G.write(t,t0+0.5,[892,668,126,34],['HACKER'],{color:C.ink,maxPx:22});
    G.write(t,t0+0.8,[1302,668,126,34],['NÓS'],{color:C.ink,maxPx:22});
    fly(t,'robobee',{t0:tA,h:70,seed:3,path:orbit(960,250,300,40,1.5,0)});
  });
}
// S26 crashed self-driving car
{ const t0=at('carro autônomo')-0.08;
  ev(t0+0.1,'hit'); ev(t0+0.4,'pop');
  shot('carro autônomo','q4_bl',[1.1,500,700],[1.18,450,720],t=>{
    G.puff(t,t0+0.1,520,820,90);
    G.tag(t,t0+0.4,420,560,'CARRO AUTÔNOMO',{side:'up',fill:C.alert});
  },null,{shake:[t0+0.1,9]});
}
// S27 desert drone: military use, and the list keeps growing
{ const t0=at('drone usado')-0.08, tM=at('militares'), tL=at('a lista');
  ev(t0+0.2,'whoosh',0.5); ev(tM,'pop');
  shot('drone usado','q4_br',[1.0,960,540],[1.1,1000,420],t=>{
    G.speedLines(t,t0,t0+3,700,300,1);
    G.tag(t,tM,960,560,'USO MILITAR',{side:'up',fill:C.alert});
  },t=>G.number(t,tL,80,640,'riscos na lista',12,{roll:1.2}));
}

// ================= CHAPTER 4 =================
CHAPTER('A verdade é que');
// S28 crossroads: we live in a dilemma
{ const t0=at('A verdade é que')-0.08, tD=at('dilema');
  chapterStampEv(t0+0.25); ev(t0+0.4,'pop'); G.writeEvents(tD,['PROGRESSO']); G.writeEvents(tD+0.4,['RISCO']);
  shot('A verdade é que','p6_cross',[1.0,960,560],[1.08,900,520],t=>{
    G.write(t,tD,[790,275,270,70],['PROGRESSO'],{color:C.card,maxPx:44});
    G.write(t,tD+0.4,[885,410,250,70],['RISCO'],{color:C.card,maxPx:44});
    E.puppet(t,'host',{x:960,y:1010,h:470,t0:t0+0.35,hop:true,seed:3,talk:NARR,pose:[[-9,'rest'],[tD,'shrug']]});
  },t=>chapterStamp(t,t0+0.25,4));
}
// S29 indoor farm: we need technology to solve real problems
{ const t0=at('Precisamos da tecnologia')-0.08, tX=at('extinção'), tC=at('crises alimentares');
  ev(tX,'pop'); ev(tC,'pop'); ev(t0+0.3,'pop');
  shot('Precisamos da tecnologia','p5_farm',[1.1,960,520],[1.02,960,560],t=>{
    for(let i=0;i<4;i++) fly(t,'robobee',{t0:t0+0.1*i,h:64,seed:i,path:t=>[2000-((t-t0)*240+i*480)%2100,560-i*60+20*Math.sin(t*2+i)]});
    E.figure(t,'farmer',{x:960,y:1020,h:460,t0:t0+0.3,hop:true,seed:2});
    G.tag(t,tX,520,380,'EXTINÇÃO DAS ABELHAS',{side:'down',fill:C.alert});
    G.tag(t,tC,1400,380,'CRISE ALIMENTAR',{side:'down',fill:C.alert});
  });
}
// S30 night street: the more we advance, the more exposed we are
{ const t0=at('Mas quanto mais')-0.08, tR=at('riscos que ninguém'), tN=at('ninguém sabe');
  ev(t0+0.3,'whoosh',0.5); ev(tR,'pop'); ev(tN,'pop');
  shot('Mas quanto mais','q3_br',[1.12,960,400],[1.0,960,540],t=>{
    for(let i=0;i<8;i++) fly(t,'drone',{t0:t0+0.15*i,h:60,seed:i,path:t=>[200+i*220+30*Math.sin(t+i),180+((i*53)%200)+15*Math.sin(t*2+i)]});
    G.tag(t,tR,960,640,'RISCOS SEM CONTROLE',{side:'up',fill:C.alert});
    if(t>tN) G.qmark(t,tN,960,500);
  },t=>G.vignette(0.4));
}
// S31 garden: fascinating, real potential
{ const t0=at('A ideia das')-0.08, tP=at('potencial'), tB=at('muito bem');
  ev(t0+0.3,'pop'); ev(tP,'ding',0.6); ev(tB,'pop');
  shot('A ideia das','p1_garden',[1.05,900,560],[1.0,960,540],t=>{
    for(let i=0;i<4;i++) fly(t,'robobee',{t0:t0+0.15*i,h:80,seed:i,path:orbit(300+i*420,330+(i%2)*90,60,30,1.6,i)});
    E.figure(t,'lia_amazed',{x:960,y:985,h:500,t0:t0+0.3,hop:true,seed:6});
    G.tag(t,tP,960,440,'POTENCIAL',{side:'up',fill:C.success});
    G.tag(t,tB,1450,700,'BOM PRO PLANETA',{side:'up',fill:C.success});
  });
}
// S32 crossroads again: how far can we trust technology?
{ const t0=at('Mas como em todo')-0.08, tQ=at('até que ponto');
  G.boardEvents(tQ,['ATÉ ONDE','CONFIAR?']);
  shot('Mas como em todo','p6_cross',[1.1,1200,600],[1.04,1100,580],t=>{
    E.puppet(t,'host',{x:1250,y:1010,h:470,t0:t0+0.25,hop:true,seed:3,talk:NARR,pose:[[-9,'chin'],[tQ,'shrug']]});
    if(t>tQ+0.6) G.qmark(t,tQ+0.6,1250,470);
  },t=>G.board(t,tQ,180,260,640,['ATÉ ONDE','CONFIAR?'],{px:64}));
}
// S33 TV again: technology saves, but also condemns
{ const t0=at('Porque se tem algo')-0.08, tS=at('salva'), tC=at('condena');
  ev(tS,'ding',0.6); G.stampEvents(tC);
  shot('Porque se tem algo','p3_tvroom',[1.0,1100,560],[1.08,1300,520],t=>{
    X.save(); X.beginPath(); X.rect(1400,262,372,318); X.clip(); X.fillStyle='#141a33'; X.fillRect(1400,262,372,318);
    for(let i=0;i<6;i++) fly(t,t<tC?'robobee':'evilbee',{t0:t0,h:50,seed:i,path:t=>[1440+((t*70+i*61)%320),300+((i*71)%240)+12*Math.sin(t*3+i)]});
    X.restore();
    E.puppet(t,'host',{x:880,y:985,h:500,t0:t0+0.25,hop:true,seed:3,talk:NARR,dark:0.2,pose:[[-9,'rest'],[tS,'present'],[tC,'head']]});
    G.tag(t,tS,1585,600,'SALVA',{side:'down',fill:C.success});
  },t=>{ G.stamp(t,tC,1420,900,'CONDENA',{px:100}); G.vignette(0.35); });
}

// ================= OUTRO =================
const tOut=tEndV+0.6;
STING.outro(tOut,{motif:(t,t0)=>{ for(let n=1;n<=4;n++) G.stamp(t,t0+0.7+n*0.15,170+(n-1)*175,230,'0'+n,{px:80,color:C.alert}); }});
for(let n=1;n<=4;n++) G.stampEvents(tOut+0.7+n*0.15);
window.END=tOut+STING.OUTRO;
};
