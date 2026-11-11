#!/usr/bin/env python3
"""Build the render page for a video: page.py videodir assets.json shots1.js [shots2.js ...]
assets.json: {"name": "path relative to the skill root or absolute"}. Writes videodir/index.html + dna.js."""
import os, sys, json
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
vd=os.path.abspath(sys.argv[1]); assets=json.load(open(sys.argv[2])); shots=[os.path.abspath(s) for s in sys.argv[3:]]
dna=json.load(open(os.path.join(ROOT,'dna.json')))
open(os.path.join(vd,'dna.js'),'w').write('window.DNA='+json.dumps(dna)+';\n')
A={k:'file://'+(v if os.path.isabs(v) else os.path.join(ROOT,v)) for k,v in assets.items()}
rigs=sorted({os.path.join(ROOT,'library','host','rig','rig.js')}|{os.path.join(vd,'rig.js')} )
home=json.load(open(os.path.join(ROOT,'library','stings','home.json')))
A.setdefault('home','file://'+os.path.join(ROOT,home['plate']))
for k,v in {'host_side_walk':'library/host/sprites/host_side_walk.png','host_wave':'library/host/sprites/host_wave.png','host_body':'library/host/rig/host_body.png','host_head':'library/host/rig/host_head.png'}.items(): A.setdefault(k,'file://'+os.path.join(ROOT,v))
scripts=[os.path.join(vd,'dna.js')]+[r for r in rigs if os.path.exists(r)]+[os.path.join(vd,'words.js'),os.path.join(ROOT,'engine','player.js'),os.path.join(ROOT,'engine','stings.js')]+shots
html=f'''<!doctype html><html><head><meta charset=utf-8><style>html,body{{margin:0;background:#000}}canvas{{display:block}}</style></head><body>
<canvas id=c></canvas><script>window.FONT_URL={json.dumps('file://'+os.path.join(ROOT,'library','fonts','ArchivoBlack.woff2'))};window.RIG=window.RIG||{{}};window.HOME_BOARD={json.dumps(home['board'])};window.HOME_FLOOR={home['floor']};window.HOME_HOST_H={home['host_h']};</script>
{''.join(f'<script src="file://{s}"></script>' for s in scripts)}
<script>BOOT({json.dumps(A)});</script></body></html>'''
open(os.path.join(vd,'index.html'),'w').write(html); print(os.path.join(vd,'index.html'))
