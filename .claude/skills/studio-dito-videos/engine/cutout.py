#!/usr/bin/env python3
"""Chroma-key a sheet into named sprites.
usage: cutout.py sheet.png outdir [--names a,b,c] [--key green|magenta] [--min-area 4000]
Rules (see SKILL.md <rig>): background = border-connected pixels with G-max(R,B)>40 and within 110 of the
median key colour (mirrored for magenta). 2 px soft alpha band with G clamped to max(R,B)+6 inside it.
Pieces grouped by figure (dilated connectivity), specks dropped, sorted left->right, top->bottom."""
import sys, os, json, argparse
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

def key_mask(rgb, key='green'):
    r,g,b = [rgb[...,i].astype(np.int16) for i in range(3)]
    if key=='green': dom = g - np.maximum(r,b)
    else:            dom = np.minimum(r,b) - g          # magenta: R and B over G
    cand = dom > 40
    med = np.median(rgb[cand].reshape(-1,3),axis=0) if cand.any() else np.array([0,177,64])
    near = np.linalg.norm(rgb.astype(np.float32)-med,axis=2) < 110
    bgc = (cand & near).astype(np.uint8)
    # keep only components touching the border
    n,lab = cv2.connectedComponents(bgc,connectivity=4)
    edge = set(np.unique(np.concatenate([lab[0],lab[-1],lab[:,0],lab[:,-1]]))) - {0}
    bg = np.isin(lab, list(edge))
    return bg, med

def cut(rgb, key='green'):
    bg,_ = key_mask(rgb,key)
    fg = (~bg).astype(np.uint8)*255
    # 2 px soft band
    dist = cv2.distanceTransform((fg>0).astype(np.uint8),cv2.DIST_L2,3)
    alpha = np.clip(dist/2.0,0,1)
    alpha[fg==0]=0
    out = rgb.copy().astype(np.int16)
    band = (alpha>0)&(alpha<1)
    r,g,b = out[...,0],out[...,1],out[...,2]
    if key=='green':
        cap = np.maximum(r,b)+6; g[band] = np.minimum(g[band],cap[band])
        # also kill spill on the very edge ring
    else:
        cap = g+6; r[band]=np.minimum(r[band],cap[band]); b[band]=np.minimum(b[band],cap[band])
    rgba = np.dstack([np.clip(out,0,255).astype(np.uint8),(alpha*255).astype(np.uint8)])
    return rgba

def pieces(rgba, min_area=4000, join=18):
    a = (rgba[...,3]>8).astype(np.uint8)
    grown = cv2.dilate(a, np.ones((join,join),np.uint8))
    n,lab,st,_ = cv2.connectedComponentsWithStats(grown,connectivity=8)
    out=[]
    for i in range(1,n):
        x,y,w,h,area = st[i]
        m = (lab==i)&(a>0)
        if m.sum()<min_area: continue
        sub = rgba[y:y+h,x:x+w].copy(); sub[...,3] = np.where(m[y:y+h,x:x+w],sub[...,3],0)
        out.append(dict(x=int(x),y=int(y),w=int(w),h=int(h),img=sub))
    # reading order: rows by centre y (tolerance 1/4 of median height), then x
    if out:
        mh=np.median([p['h'] for p in out])
        out.sort(key=lambda p:(round((p['y']+p['h']/2)/(mh*0.6)),p['x']))
    return out

def contact(sprites, path, bg=(40,44,60)):
    cols=min(6,len(sprites)); rows=(len(sprites)+cols-1)//cols; cw,ch=320,360
    sheet=Image.new('RGB',(cols*cw,rows*ch),bg); d=ImageDraw.Draw(sheet)
    try: f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',20)
    except Exception: f=ImageFont.load_default()
    for i,(name,im) in enumerate(sprites):
        im=im.copy(); im.thumbnail((cw-20,ch-50)); x=(i%cols)*cw+(cw-im.width)//2; y=(i//cols)*ch+10
        chk=Image.new('RGB',im.size,(70,74,90)); sheet.paste(chk,(x,y)); sheet.paste(im,(x,y),im)
        d.text(((i%cols)*cw+10,(i//cols)*ch+ch-34),name,fill=(240,230,200),font=f)
    sheet.save(path)

if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('sheet'); ap.add_argument('outdir')
    ap.add_argument('--names',default=''); ap.add_argument('--key',default='green'); ap.add_argument('--min-area',type=int,default=4000)
    a=ap.parse_args(); os.makedirs(a.outdir,exist_ok=True)
    rgb=np.array(Image.open(a.sheet).convert('RGB'))
    rgba=cut(rgb,a.key); ps=pieces(rgba,a.min_area)
    names=[n for n in a.names.split(',') if n] ; sprites=[]
    for i,p in enumerate(ps):
        nm=names[i] if i<len(names) else f'piece{i:02d}'
        im=Image.fromarray(p['img'],'RGBA'); im.save(os.path.join(a.outdir,nm+'.png')); sprites.append((nm,im))
    contact(sprites,os.path.join(a.outdir,'_contact.png'))
    json.dump([{'name':(names[i] if i<len(names) else f'piece{i:02d}'),**{k:p[k] for k in 'xywh'}} for i,p in enumerate(ps)],open(os.path.join(a.outdir,'_pieces.json'),'w'),indent=1)
    print(len(ps),'pieces ->',a.outdir)
