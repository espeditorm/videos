#!/usr/bin/env python3
"""Roll channel or per-video DNA. Seeded from os.urandom; never pick by hand.
usage: roll_dna.py channel [--name NAME] [--lock key=value ...] [--reroll key ...]
       roll_dna.py video   [--topic T]      (checks library/log.json, last 5)"""
import os, sys, json, random, colorsys, argparse, datetime
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DNA = os.path.join(ROOT, 'dna.json'); LOG = os.path.join(ROOT, 'library', 'log.json')

PALETTES = {
 'Dusty Dawn':      {'dusty blue-grey':'#7d8ca3','slate teal':'#3f6e75','warm beige':'#e6d3b3','navy':'#1f2a48','soft purple':'#8f7bb8'},
 'Desert Clay':     {'terracotta':'#c3623f','sand':'#e4cfa3','sage green':'#8fa77f','deep cocoa':'#4a2e24','mustard':'#d7a531'},
 'Nordic Frost':    {'ice blue':'#bcd9e8','pale stone grey':'#d6d6d0','pine green':'#2f5d4a','charcoal':'#2e3135','berry red':'#a3324a'},
 'Retro Mint':      {'mint':'#a8dcc5','cream':'#f5ecd7','coral':'#ec7a62','deep teal':'#1d5a5c','burgundy':'#7a2836'},
 'Ink and Ochre':   {'ochre':'#cc8e2e','warm off-white':'#f3ebdc','indigo':'#2f3a6b','rust':'#a9472a','olive':'#7a7a3a'},
 'Dusk Arcade':     {'deep plum':'#4a2545','muted cyan':'#6fb3b8','dusty magenta':'#b5578a','midnight blue':'#1c2340','warm butter yellow':'#f2d17a'},
 'Forest Paper':    {'moss':'#7d8f4e','kraft beige':'#d5bd94','forest green':'#2e4a33','plum':'#6b3a5a','cream':'#f4ecd8'},
 'Candy Slate':     {'slate grey':'#5d6673','peach':'#f5b79a','lilac':'#bba6d9','butter yellow':'#f5dc85','sea teal':'#3f9a93'},
 'Harbour':         {'navy':'#1e2f4d','sail white':'#f4f1e8','brick red':'#b23a2e','sea-glass green':'#9ccbb4','rope tan':'#c9a271'},
 'Citrus Concrete': {'concrete grey':'#a3a29e','lime':'#b5d23a','tangerine':'#f08a2c','graphite':'#34373b','sky blue':'#7cc0e8'},
}
DUSTY_DAWN_CODE = dict(ink='#2b2d42',alert='#d62828',warm='#f4a261',highlight='#f6b93b',success='#2fb37a',dark='#1f2a48',
  headlineA='#e2552f',headlineB='#5b3fa6',label='#8a8c9c',card='#ffffff',transition='#f4f1fb')

CHANNEL = {
 'palette': list(PALETTES),
 'character_build': ['Big round heads, dot eyes, small bodies',
   'Tall pill-shaped bodies, oval heads, solid-shape eyebrows that carry the emotion',
   'Chunky rounded-square heads, stubby legs, wide shoulders',
   'Long thin limbs, small heads, oversized hands and shoes',
   'Egg-shaped heads with no nose, big blocky hair shapes, tiny feet',
   'Bean bodies where head and torso are one shape, dot eyes set wide'],
 'font': ['Montserrat 900','Poppins 800','Archivo Black','Anton','Bebas Neue','Rubik 800','Barlow Condensed 800',
          'Lexend 800','Outfit 800','Fredoka 700','Unbounded 800','Sora 800'],
 'card_style': ['rounded','square-offset','pill-strip','paper-note','die-cut'],
 'hud_position': ['top-left','top-right','bottom-left','top-strip'],
 'tag_style': ['dot-line-pill','curved-arrow','bracket','flag','triangle-pointer'],
 'text_entry': ['typing','word-pop','mask-slide-up','drop-bounce'],
 'motion': ['Bouncy','Snappy','Floaty','Punchy'],
 'camera': ['slow-push','handheld-drift','snap-zoom','parallax'],
 'shot_transition': ['push-horizontal','push-vertical','circle-iris','diagonal-slats','zoom-through'],
 'chapter_transition': ['blob-splat','paint-swipe','shutter-bars','ink-drop','page-curl'],
 'narrator': ['deep warm US documentary','crisp British documentary','calm warm female documentary',
              'energetic younger US explainer','dry deadpan storyteller','gravelly older storyteller'],
 'music': ['soft piano and pulses','light lo-fi beats','warm orchestral strings','minimal electronic','acoustic plucks','synthwave pads'],
 'host': ['none','recurring host','mascot animal','mascot object with a face'],
 'intro_sting': ['name-on-board','host-presents-title','chapter-transition-banner'],
 'outro_sting': ['host-waves','name-board-swings-in','motif-final-state'],
}
VIDEO = {
 'script_shape': ['chronological story','countdown of reasons','mystery that opens on the ending','myth vs reality',
                  'one day in the life','"what if" escalation','follow the money'],
 'hook': ['a shocking number','a direct question to the viewer','a scene already mid-action','a common belief to break',
          'a tiny detail that turns out huge'],
 'motif': ['map the story keeps returning to','counter that keeps climbing in the plates','one prop in every chapter',
           'big chapter number stamped on each chapter\'s first plate','side character who reacts to every twist'],
 'thumbnail': ['face left, object right','two characters facing off','one huge object with a tiny character','before and after split'],
}
PLAYFUL_FONTS = {'Fredoka 700','Unbounded 800'}
# Host presence is needed by the host stings
HOST_STINGS_IN = {'host-presents-title'}; HOST_STINGS_OUT = {'host-waves'}

# ---------- colour maths ----------
def h2rgb(h): h=h.lstrip('#'); return tuple(int(h[i:i+2],16)/255 for i in (0,2,4))
def rgb2h(c): return '#'+''.join('%02x'%round(max(0,min(1,v))*255) for v in c)
def lum(h):
    def f(v): return v/12.92 if v<=0.03928 else ((v+0.055)/1.055)**2.4
    r,g,b=map(f,h2rgb(h)); return 0.2126*r+0.7152*g+0.0722*b
def contrast(a,b):
    la,lb=sorted((lum(a),lum(b)),reverse=True); return (la+0.05)/(lb+0.05)
def hls(h): return colorsys.rgb_to_hls(*h2rgb(h))
def from_hls(h,l,s): return rgb2h(colorsys.hls_to_rgb(h%1,max(0,min(1,l)),max(0,min(1,s))))
def hue_deg(h): return hls(h)[0]*360
def hue_gap(a,b): d=abs(hue_deg(a)-hue_deg(b))%360; return min(d,360-d)
def darken_until(c, bg, target):
    h,l,s=hls(c)
    while contrast(c,bg)<target and l>0.02: l-=0.01; c=from_hls(h,l,s)
    return c
def mix(a,b,t): A,B=h2rgb(a),h2rgb(b); return rgb2h([A[i]*(1-t)+B[i]*t for i in range(3)])

def code_colours(name):
    if name=='Dusty Dawn': return dict(DUSTY_DAWN_CODE)
    P=list(PALETTES[name].values())
    by_l=sorted(P,key=lum); darkest,lightest=by_l[0],by_l[-1]
    card=mix(lightest,'#ffffff',0.75)
    ink=darken_until(from_hls(hls(darkest)[0],0.18,min(0.45,hls(darkest)[2])),card,7.5)
    dark=from_hls(hls(darkest)[0],min(0.2,hls(darkest)[1]),hls(darkest)[2])
    def nearest(target_deg, sat_min=0.35):
        cands=[c for c in P if hls(c)[2]>=sat_min] or P
        return min(cands,key=lambda c:min(abs(hue_deg(c)-target_deg)%360,360-abs(hue_deg(c)-target_deg)%360))
    def at_hue(deg,l,s): return from_hls(deg/360,l,s)
    # alert: red family, pulled from palette if one is near red, else a palette-tuned red
    r=nearest(5); rd=hue_deg(r); rd=rd if min(rd,360-rd)<=22 else 3
    alert=darken_until(at_hue(rd,0.47,0.72),card,4.8)
    # accents on a fixed hue ladder (red -> orange -> yellow -> green) so each pair is >=30 deg apart;
    # saturation/lightness borrowed from the palette's own mood
    ps=sum(hls(c)[2] for c in P)/len(P); sat=max(0.62,min(0.85,ps+0.35))
    ah=hue_deg(alert); ah=ah-360 if ah>180 else ah
    ah=min(ah,-4); alert=darken_until(at_hue(ah,0.47,0.72),card,4.8)   # crimson side of red leaves room for a true yellow
    warm=at_hue(ah+31,0.6,sat); hi=at_hue(ah+62,0.58,sat); succ=at_hue(150,0.42,sat*0.8)
    # headlines: palette colours with real colour (not yellow: darkened yellow turns to mud),
    # preferring mid lightness, two clearly different hues; darkened until white caps read
    def score(c): h,l,s_=hls(c); return s_-abs(l-0.42)
    pool=[c for c in P if not 38<=hue_deg(c)<=78 and hls(c)[2]>0.15] or P
    pool=sorted(pool,key=score,reverse=True); base_a=pool[0]; rest=[c for c in pool[1:] if hue_gap(c,base_a)>40]
    hA=darken_until(base_a,'#ffffff',4.6)
    hB=darken_until(rest[0] if rest else from_hls(hls(base_a)[0]+0.5,0.35,0.5),'#ffffff',4.6)
    label=from_hls(hls(ink)[0],0.58,0.08)
    trans=mix(lightest,'#ffffff',0.55)
    out=dict(ink=ink,alert=alert,warm=warm,highlight=hi,success=succ,dark=dark,headlineA=hA,headlineB=hB,label=label,card=card,transition=trans)
    return out

def check_colours(c):
    probs=[]
    if contrast(c['ink'],c['card'])<7: probs.append('ink/card <7:1')
    if contrast(c['alert'],c['card'])<4.5: probs.append('alert/card <4.5:1')
    for k in ('headlineA','headlineB'):
        if contrast('#ffffff',c[k])<4.5: probs.append(f'white/{k} <4.5:1')
    ks=['alert','warm','highlight','success']
    for i in range(4):
        for j in range(i+1,4):
            if hue_gap(c[ks[i]],c[ks[j]])<30: probs.append(f'{ks[i]}/{ks[j]} hue gap {hue_gap(c[ks[i]],c[ks[j]]):.0f}')
    return probs

# ---------- clash rules ----------
def clashes_channel(d):
    out=[]
    if d['font'] in PLAYFUL_FONTS and d['narrator'] in ('gravelly older storyteller','crisp British documentary') :
        out.append(('font',f"playful {d['font']} fights a {d['narrator']} narrator"))
    if d['host']=='none' and d['intro_sting'] in HOST_STINGS_IN: out.append(('intro_sting','intro needs a host but host = none'))
    if d['host']=='none' and d['outro_sting'] in HOST_STINGS_OUT: out.append(('outro_sting','outro needs a host but host = none'))
    if d['palette'] in ('Dusk Arcade',) and d['character_build'].startswith('Bean') :
        out.append(('palette','dark Dusk Arcade palette would swallow small wide-eyed bean figures at night'))
    if d['motion']=='Floaty' and d['camera']=='snap-zoom': out.append(('camera','snap zooms fight a Floaty motion personality'))
    if d['motion']=='Snappy' and d['camera']=='handheld-drift' and d['shot_transition']=='zoom-through': pass
    if d['outro_sting']=='motif-final-state': pass
    return out

def roll_channel(rng, locks, prev=None, reroll=()):
    d=dict(prev or {})
    for k,opts in CHANNEL.items():
        if k in locks: d[k]=locks[k]
        elif prev is None or k in reroll: d[k]=rng.choice(opts)
    notes=[]
    for _ in range(2):
        cl=[c for c in clashes_channel(d) if c[0] not in locks]
        if not cl: break
        for k,why in cl:
            old=d[k]; d[k]=rng.choice([o for o in CHANNEL[k] if o!=old]); notes.append(f"rerolled {k} ({old} -> {d[k]}): {why}")
    if prev is None or 'pace' in reroll:
        d['places_per_minute']=rng.randint(8,12); d['new_every_s']=round(rng.uniform(1.6,2.4),2)
    if prev is None or 'card_style' in reroll or 'card' not in d:
        d['card']={'rounded':{'radius':rng.randint(18,20),'shadow':{'blur':22,'y':8,'alpha':0.22}},
                   'square-offset':{'radius':4,'offset':8},'pill-strip':{'strip':14},
                   'paper-note':{'tilt':0.04,'tape':True},'die-cut':{'border':10}}[d['card_style']]
    d['colours']=code_colours(d['palette']); d['palette_colours']=PALETTES[d['palette']]
    probs=check_colours(d['colours'])
    return d,notes,probs

def roll_video(rng, log):
    last=log[-5:]; d={}; notes=[]
    for k,opts in VIDEO.items():
        used={v.get('picks',{}).get(k) for v in last}
        free=[o for o in opts if o not in used] or opts
        d[k]=rng.choice(free)
    return d

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('mode',choices=['channel','video'])
    ap.add_argument('--name'); ap.add_argument('--lock',nargs='*',default=[]); ap.add_argument('--reroll',nargs='*',default=[])
    a=ap.parse_args()
    seed=int.from_bytes(os.urandom(8),'big'); rng=random.Random(seed); print('seed',seed)
    if a.mode=='channel':
        prev=json.load(open(DNA)) if (a.reroll and os.path.exists(DNA)) else None
        locks=dict(x.split('=',1) for x in a.lock)
        d,notes,probs=roll_channel(rng,locks,prev,set(a.reroll))
        if a.name: d['channel_name']=a.name; d['slug']=a.name.lower().replace(' ','-')
        d.setdefault('seeds',[]).append({'seed':seed,'what':'channel' if not a.reroll else 'reroll '+','.join(a.reroll),'at':datetime.datetime.now().isoformat(timespec='seconds')})
        d['frozen']=True
        json.dump(d,open(DNA,'w'),indent=2); print(json.dumps(d,indent=2))
        for n in notes: print('NOTE',n)
        for p in probs: print('COLOUR PROBLEM',p)
    else:
        dna=json.load(open(DNA)); log=json.load(open(LOG)) if os.path.exists(LOG) else []
        d=roll_video(rng,log)
        P=dna['palette_colours']; d['accent']=rng.choice(list(P)); d['seed']=seed
        print(json.dumps(d,indent=2))
if __name__=='__main__': main()
