#!/usr/bin/env python3
"""Split a 2x2 quad plate into four 1920x1080 tiles: quad.py quad.png outdir [names tl,tr,bl,br]
Find the brightest-white row/col near the centre, walk out while the line stays >60% white, trim 6 px more,
then crop each quarter to 16:9 (centre crop) and resize to 1920x1080."""
import sys, os, numpy as np
from PIL import Image
def white_frac(a): return ((a.min(axis=-1)>232)).mean(axis=-1)
def gutter(img, axis):
    a=np.asarray(img.convert('RGB')).astype(np.int16)
    if axis==1: a=a.transpose(1,0,2)       # columns become rows
    n=a.shape[0]; lo,hi=int(n*0.4),int(n*0.6)
    fr=white_frac(a)
    c=lo+int(np.argmax(fr[lo:hi])); s=e=c
    while s>0 and fr[s-1]>0.6: s-=1
    while e<n-1 and fr[e+1]>0.6: e+=1
    return s-6, e+6
def crop169(im):
    w,h=im.size; tw=min(w,int(h*16/9)); th=int(tw*9/16)
    l=(w-tw)//2; t=(h-th)//2
    return im.crop((l,t,l+tw,t+th)).resize((1920,1080),Image.LANCZOS)
if __name__=='__main__':
    src,out=sys.argv[1],sys.argv[2]; names=(sys.argv[3].split(',') if len(sys.argv)>3 else ['tl','tr','bl','br'])
    os.makedirs(out,exist_ok=True); im=Image.open(src).convert('RGB'); W,H=im.size
    ys,ye=gutter(im,0); xs,xe=gutter(im,1)
    boxes=[(0,0,xs,ys),(xe,0,W,ys),(0,ye,xs,H),(xe,ye,W,H)]
    for nm,b in zip(names,boxes):
        crop169(im.crop(b)).save(os.path.join(out,nm+'.png'))
    print('gutters x',xs,xe,'y',ys,ye)
