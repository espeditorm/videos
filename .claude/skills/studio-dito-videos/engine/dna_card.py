#!/usr/bin/env python3
"""Render dna.json as a one-screen DNA card PNG: dna_card.py [out.png]"""
import json, os, sys, subprocess, html
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d=json.load(open(os.path.join(ROOT,'dna.json'))); C=d['colours']
out=sys.argv[1] if len(sys.argv)>1 else os.path.join(ROOT,'library','dna_card.png')
rows=[('Palette',d['palette']),('Characters',d['character_build']),('Font',d['font']),('Card style',d['card_style']),
 ('HUD',d['hud_position']),('Tag',d['tag_style']),('Text entry',d['text_entry']),('Motion',d['motion']),('Camera',d['camera']),
 ('Shot transition',d['shot_transition']),('Chapter transition',d['chapter_transition']),('Narrator',d['narrator']),
 ('Music',d['music']),('Pace',f"{d['places_per_minute']} places/min · new thing every {d['new_every_s']} s"),('Host',d['host']),
 ('Intro sting',d['intro_sting']),('Outro sting',d['outro_sting'])]
sw=''.join(f'<div class=sw><i style="background:{v}"></i><b>{html.escape(k)}</b><span>{v}</span></div>' for k,v in d['palette_colours'].items())
cc=''.join(f'<div class=sw><i style="background:{v}"></i><b>{k}</b><span>{v}</span></div>' for k,v in C.items())
tr=''.join(f'<tr><td>{html.escape(a)}</td><td>{html.escape(str(b))}</td></tr>' for a,b in rows)
font=os.path.join(ROOT,'library','fonts','ArchivoBlack.woff2')
H=f'''<html><head><style>@font-face{{font-family:D;src:url(file://{font})}}
body{{margin:0;width:1920px;height:1080px;background:{C['transition']};font-family:D;color:{C['ink']};}}
.wrap{{padding:48px 64px;display:grid;grid-template-columns:1.15fr 1fr;gap:48px}}
h1{{margin:0 0 6px;font-size:76px;letter-spacing:1px}} .seed{{font:22px monospace;color:{C['label']}}}
.card{{background:{C['card']};border-radius:4px;box-shadow:8px 8px 0 {C['dark']};padding:22px 28px}}
table{{border-collapse:collapse;width:100%;font-size:23px}} td{{padding:6px 4px;border-bottom:2px solid {C['transition']}}}
td:first-child{{color:{C['label']};width:250px;text-transform:uppercase;font-size:18px}}
h2{{font-size:26px;margin:0 0 12px;text-transform:uppercase}} .sw{{display:flex;align-items:center;gap:12px;margin:5px 0;font-size:20px}}
.sw i{{width:54px;height:30px;border-radius:4px;display:block}} .sw span{{font:18px monospace;color:{C['label']};margin-left:auto}}
.ban{{background:{C['headlineA']};color:#fff;font-size:40px;padding:10px 22px;transform:rotate(-.02rad);display:inline-block;margin:18px 0 0}}
</style></head><body><div class=wrap><div><h1>{html.escape(d['channel_name'].upper())} · DNA</h1>
<div class=seed>seed {d['seeds'][0]['seed']} · frozen channel traits</div><br><div class=card><table>{tr}</table></div></div>
<div><div class=card><h2>Palette — {html.escape(d['palette'])}</h2>{sw}</div><br><div class=card><h2>Code colours</h2>{cc}</div>
<div class=ban>WHITE CAPS ON HEADLINE A</div></div></div></body></html>'''
p=os.path.join(ROOT,'library','dna_card.html'); open(p,'w').write(H)
subprocess.run(['node','-e',f'''const {{chromium}}=require('playwright');(async()=>{{const b=await chromium.launch();const pg=await b.newPage({{viewport:{{width:1920,height:1080}}}});
await pg.goto('file://{p}');await pg.waitForTimeout(300);await pg.screenshot({{path:'{out}'}});await b.close()}})()'''],check=True,env={**os.environ,'NODE_PATH':subprocess.check_output(['npm','root','-g'],text=True).strip()})
print(out)
