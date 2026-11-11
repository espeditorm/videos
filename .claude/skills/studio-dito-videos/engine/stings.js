// Studio Dito stings — built once at setup, reused by every video.
// Intro  (host-presents-title, 2.8 s): the host walks into the home study and presents the episode title,
//        which pops word by word onto the study's own blank board.
// Outro  (motif-final-state, 3.6 s): a paint swipe reveals the study; the episode's signature motif is shown
//        in its final state (opts.motif draws it), the channel name lands on the board, the host waves.
// Usage inside BUILD():  const d=STING.intro(0,'WHY TRAINS RUN ON TIME');  ...  STING.outro(tEnd,{motif:fn});
(function(){
const HOME_BOARD=window.HOME_BOARD||[0,0,0,0];   // set from library/stings/home.json by page.py
window.STING={
  INTRO:2.8, OUTRO:3.6,
  intro(t0,title,opts={}){
    const E=ENG,G=E.G,C=E.C; const words=title.toUpperCase().split(/\s+|(?<=-)(?=\S)/).map(w=>w.trim()).filter(Boolean);
    // split the title over at most 2 lines
    // greedy wrap into lines of ~12 characters (max 3 lines), so the title fills the board big
    const lines=[]; let cur='';
    const join=(a,b)=>a.endsWith('-')?a+b:a+' '+b;
    for(const w of words){ if(cur && join(cur,w).length>12 && lines.length<2){ lines.push(cur); cur=w; } else cur=cur?join(cur,w):w; }
    lines.push(cur);
    const tWalkEnd=t0+0.85, tTitle=t0+0.95;
    E.ev(t0+0.02,'whoosh',0.6); E.ev(tWalkEnd,'pop',0.7); G.writeEvents(tTitle,lines); E.ev(tTitle+0.9,'ding',0.5);
    const B=HOME_BOARD, hx=B[0]-170, fy=window.HOME_FLOOR||980, hh=window.HOME_HOST_H||470;
    S(t0,(t,sh)=>{
      E.plate(t,sh,'home',[1.0,960,540],[1.045,960,520],()=>{
        G.write(t,tTitle,[B[0]+B[2]*0.06,B[1]+B[3]*0.12,B[2]*0.88,B[3]*0.76],lines,{color:C.ink,maxPx:130});
        if(t<tWalkEnd) E.figure(t,'host_side_walk',{x:hx,y:fy,h:hh,t0:t0,seed:3,walk:{from:-220,to:hx,t0:t0,t1:tWalkEnd}});
        else E.puppet(t,'host',{x:hx,y:fy,h:hh*1.0,t0:tWalkEnd-0.05,seed:3,pose:[[-9,'rest'],[tWalkEnd+0.05,'present']],talk:[[tTitle,tTitle+1.4]]});
      },{});
    },{cut:'hard'});
    return this.INTRO;
  },
  outro(t0,opts={}){
    const E=ENG,G=E.G,C=E.C,name=(opts.name||DNA.channel_name).toUpperCase();
    window.CHAPTER(t0+0.2);                         // paint swipe covers the cut into the study
    const tName=t0+0.55, tWave=t0+0.4;
    E.ev(t0,'whoosh',0.7); G.writeEvents(tName,[name]); E.ev(tName+0.6,'thud',0.6); E.ev(tWave,'pop',0.6);
    const B=HOME_BOARD, fy=window.HOME_FLOOR||980, hh=window.HOME_HOST_H||470;
    S(t0+0.2,(t,sh)=>{
      E.plate(t,sh,'home',[1.05,960,520],[1.0,960,540],()=>{
        G.write(t,tName,[B[0]+B[2]*0.06,B[1]+B[3]*0.08,B[2]*0.88,B[3]*0.5],[name],{color:C.ink,maxPx:150});
        E.figure(t,'host_wave',{x:B[0]+B[2]+170,y:fy,h:hh,t0:tWave,hop:true,seed:5,rock:0.04});
      });
      if(opts.motif) opts.motif(t,t0);               // the episode's motif in its final state (screen space)
      G.stamp(t,tName+0.55,B[0]+B[2]/2,B[1]+B[3]*0.74,'THE END',{px:60});
    },{cut:'hard'});
    return this.OUTRO;
  },
};
})();
