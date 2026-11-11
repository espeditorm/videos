#!/usr/bin/env python3
"""Render a page in N parallel browser processes and join: render_parallel.py index.html out.mp4 [--parts 5] [--end S]
Parts are separate files (rerun one with render.js --from/--to if it crashes), then concatenated losslessly.
Cuts land on frame boundaries, so no frame is doubled or dropped."""
import os, sys, subprocess, json, argparse
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ap=argparse.ArgumentParser(); ap.add_argument('page'); ap.add_argument('out'); ap.add_argument('--parts',type=int,default=5); ap.add_argument('--end',type=float,required=True); ap.add_argument('--fps',type=int,default=30)
a=ap.parse_args(); nf=round(a.end*a.fps); step=-(-nf//a.parts); env={**os.environ,'NODE_PATH':subprocess.check_output(['npm','root','-g'],text=True).strip()}
procs=[]; parts=[]
for i in range(a.parts):
    f0,f1=i*step,min(nf,(i+1)*step)
    if f0>=f1: break
    p=f'{a.out[:-4]}.part{i}.mp4'; parts.append(p)
    procs.append(subprocess.Popen(['node',os.path.join(ROOT,'engine','render.js'),a.page,p,'--from',str(f0/a.fps),'--to',str(f1/a.fps)],env=env))
bad=[i for i,pr in enumerate(procs) if pr.wait()!=0]
if bad: sys.exit(f'parts failed: {bad} — rerun them with render.js --from/--to')
lst=a.out+'.txt'; open(lst,'w').write(''.join(f"file '{os.path.abspath(p)}'\n" for p in parts))
subprocess.run(['ffmpeg','-loglevel','error','-y','-f','concat','-safe','0','-i',lst,'-c','copy',a.out],check=True)
print('joined',a.out)
