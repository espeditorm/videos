"""Folha de contato: um quadro por plano (meio do plano), 960x540."""
import json, subprocess, sys, os, cv2, numpy as np
cues = json.load(open('cues.json'))
f0 = [s['f0'] for s in cues['shots']] + [2160]
which = sys.argv[2] if len(sys.argv) > 2 else 'mid'
frames = [(a + b) // 2 if which == 'mid' else (a + 2 if which == 'start' else b - 3) for a, b in zip(f0[:-1], f0[1:])]
sel = [int(x) for x in sys.argv[3].split(',')] if len(sys.argv) > 3 else range(43)
frames = [frames[i] for i in sel]
ex, pn = 'sheet_exr', 'sheet_png'
lst = ','.join(map(str, frames))
subprocess.run(['xvfb-run', '-a', 'blender', '-b', 'harbor.blend', '-P', 'render_list.py', '--', 'states.pkl', ex, lst, '960', '540'], check=True, capture_output=True)
for f in frames:
    if os.path.exists(f'{pn}/f{f:04d}.png'): os.remove(f'{pn}/f{f:04d}.png')
    subprocess.run(['python3', 'inkpaint.py', 'states.pkl', ex, pn, str(f), str(f + 1)], check=True, capture_output=True)
ims = []
for i, f in zip(sel, frames):
    im = cv2.resize(cv2.imread(f'{pn}/f{f:04d}.png'), (480, 270))
    cv2.putText(im, f"{i + 1} {cues['shots'][i]['name']} f{f}", (6, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 255), 2)
    ims.append(im)
while len(ims) % 4: ims.append(np.zeros_like(ims[0]))
cv2.imwrite(sys.argv[1], np.vstack([np.hstack(ims[i:i + 4]) for i in range(0, len(ims), 4)]))
