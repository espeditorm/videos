// render.js page.html out.mp4 [--from s --to s --fps 30 --blur 4 --crf 17 --preview]
// Opens page in Chromium, waits READY, seeks every frame (with motion-blur subframes) and pipes PNGs to ffmpeg.
const {chromium}=require('playwright'); const {spawn}=require('child_process'); const path=require('path'); const fs=require('fs');
const a=process.argv.slice(2); const opt=(k,d)=>{const i=a.indexOf('--'+k); return i<0?d:(a[i+1]===undefined||a[i+1].startsWith('--')?true:a[i+1]);};
const page_=path.resolve(a[0]), out=a[1]; const fps=+opt('fps',30), blur=+opt('blur',4), crf=opt('crf','17');
(async()=>{
  const b=await chromium.launch({args:['--allow-file-access-from-files','--disable-web-security']});
  const p=await b.newPage({viewport:{width:1920,height:1080}});
  p.on('console',m=>{ if(m.type()==='error') console.error('[page]',m.text()); });
  p.on('pageerror',e=>console.error('[pageerror]',e.message));
  await p.goto('file://'+page_); await p.waitForFunction('window.READY===true',{timeout:120000});
  const END=await p.evaluate('window.END'); const from=+opt('from',0), to=+opt('to',END);
  fs.writeFileSync(out.replace(/\.mp4$/,'')+'.events.json',JSON.stringify(await p.evaluate('window.EV')));
  const ff=spawn('ffmpeg',['-loglevel','error','-y','-f','image2pipe','-framerate',String(fps),'-i','-','-c:v','libx264','-preset','medium','-crf',String(crf),'-pix_fmt','yuv420p',out],{stdio:['pipe','inherit','inherit']});
  const n=Math.round((to-from)*fps); const t0=Date.now();
  for(let i=0;i<n;i++){
    const t=from+i/fps;
    const png=await p.evaluate(([t,fps,blur])=>{ blur>1?window.seekBlur(t,fps,blur):window.seek(t); return document.getElementById('c').toDataURL('image/png').slice(22); },[t,fps,blur]);
    if(!ff.stdin.write(Buffer.from(png,'base64'))) await new Promise(r=>ff.stdin.once('drain',r));
    if(i%60===0) process.stderr.write(`\rframe ${i}/${n}  ${((Date.now()-t0)/1000/(i+1)*fps).toFixed(2)} s per video-second`);
  }
  ff.stdin.end(); await new Promise(r=>ff.on('close',r)); await b.close(); console.error('\ndone',out);
})();
