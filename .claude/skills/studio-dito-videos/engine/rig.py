#!/usr/bin/env python3
"""Turn an armless front sprite into a puppet: rig.py front.png outdir name [--sleeve-from x,y]
Writes outdir/<name>_body.png, <name>_head.png and appends to outdir/rig.js:
  RIG[name] = {w,h, neck:{x,y}, head:{x,y,w,h}, body:{...}, sockets:{l:{x,y},r:{x,y}}, eyes:[{x,y,w,h},..],
               skin:[r,g,b], sleeve:[r,g,b], L1, L2, T}
Neck = narrowest alpha row in the band under the head (35-75% of figure height for big-head builds).
Hole under the head inpainted from body colours so a nod never shows a gap."""
import sys, os, json, numpy as np, cv2
from PIL import Image

def rows_width(a):
    w=np.zeros(a.shape[0],int)
    for y in range(a.shape[0]):
        xs=np.nonzero(a[y]>128)[0]; w[y]=(xs[-1]-xs[0]+1) if len(xs) else 0
    return w

def dominant(rgb, mask, k=1):
    px=rgb[mask]
    if len(px)==0: return [128,128,128]
    q=(px//16).astype(int); keys=q[:,0]*256+q[:,1]*16+q[:,2]
    vals,cnt=np.unique(keys,return_counts=True); best=vals[np.argmax(cnt)]
    sel=px[keys==best]; return [int(v) for v in np.median(sel,axis=0)]

def find_eyes(rgb, alpha, head_box, skin):
    x0,y0,x1,y1=head_box; sub=rgb[y0:y1,x0:x1].astype(int); a=alpha[y0:y1,x0:x1]
    dark=(sub.sum(axis=2)<min(200,sum(skin)*0.55))&(a>200)
    # restrict to the face band (35-80% of the head height)
    hh=y1-y0; band=np.zeros_like(dark); band[int(hh*.35):int(hh*.8)]=1; dark&=band.astype(bool)
    n,lab,st,cen=cv2.connectedComponentsWithStats(dark.astype(np.uint8))
    blobs=[(st[i],cen[i]) for i in range(1,n) if 20<st[i][4]<0.01*hh*hh*4]
    # eye dots: roughly round, similar size, side by side
    blobs=[b for b in blobs if 0.5<b[0][2]/max(1,b[0][3])<2.0]
    blobs.sort(key=lambda b:-b[0][4]); best=None
    for i in range(len(blobs)):
        for j in range(i+1,len(blobs)):
            (si,ci),(sj,cj)=blobs[i],blobs[j]
            if abs(ci[1]-cj[1])<hh*0.08 and abs(si[4]-sj[4])<0.6*max(si[4],sj[4]) and abs(ci[0]-cj[0])>hh*0.12:
                best=(si,sj); break
        if best: break
    if not best: return []
    out=[]
    for s in sorted(best,key=lambda s:s[0]):
        pad=3; out.append(dict(x=int(x0+s[0]-pad),y=int(y0+s[1]-pad),w=int(s[2]+2*pad),h=int(s[3]+2*pad)))
    return out

def rig(path, outdir, name):
    im=np.array(Image.open(path).convert('RGBA')); H,W=im.shape[:2]
    im[im[...,3]==0,:3]=0           # never let hidden key colour leak through inpaint/filters
    rgb=im[...,:3]; al=im[...,3]
    ys=np.nonzero(al.max(axis=1)>128)[0]; top,bot=ys[0],ys[-1]; fh=bot-top
    w=rows_width(al)
    lo,hi=top+int(fh*0.35),top+int(fh*0.78)
    # the head is the widest blob in the upper part; neck = narrowest row below the head's widest row
    head_wide=top+int(np.argmax(w[top:top+int(fh*0.6)]))
    lo=max(lo,head_wide+int(fh*0.05))
    seg=w[lo:hi].astype(float); seg[seg==0]=1e9; neck_y=lo+int(np.argmin(seg))
    xs=np.nonzero(al[neck_y]>128)[0]; neck_x=int((xs[0]+xs[-1])/2)
    # body box below the neck; shoulders = widest row in the first 30% of the body
    body_top=neck_y; bw=w[body_top:bot]; sh_rows=bw[:max(3,int((bot-body_top)*0.3))]
    sh_y=body_top+int(np.argmax(sh_rows)); sxs=np.nonzero(al[sh_y]>128)[0]
    inset=int(fh*0.025)
    sockets={'l':{'x':int(sxs[0]+inset),'y':int(sh_y)},'r':{'x':int(sxs[-1]-inset),'y':int(sh_y)}}
    # colours
    head_mask=np.zeros_like(al,bool); head_mask[top:neck_y]=al[top:neck_y]>200
    warm=(rgb[...,0].astype(int)-rgb[...,2].astype(int)>40)
    skin=dominant(rgb,head_mask & warm) if (head_mask&warm).sum()>200 else dominant(rgb,head_mask)
    sl_mask=np.zeros_like(al,bool); sl_mask[sh_y:sh_y+int(fh*0.08),:]=al[sh_y:sh_y+int(fh*0.08),:]>200
    sleeve=dominant(rgb,sl_mask)
    hx=np.nonzero(al[top:neck_y].max(axis=0)>128)[0]; head_box=(int(hx[0]),int(top),int(hx[-1]+1),int(neck_y))
    eyes=find_eyes(rgb,al,head_box,skin)
    # split: head keeps rows <= neck_y + overlap ; body gets rows >= neck_y with the hole above inpainted
    ov=int(fh*0.03)
    head=im.copy(); head[neck_y+ov:]=0
    body=im.copy(); body[:neck_y]=0
    # inpaint a collar band [neck_y-ov, neck_y+ov] from body colours so the gap under a nodding head is filled
    band=np.zeros((H,W),np.uint8); band[neck_y-ov:neck_y+1]=255
    span=np.nonzero(al[min(H-1,neck_y+2)]>128)[0]              # the collar row just under the neck
    band[:, :span[0]]=0; band[:, span[-1]+1:]=0
    band[al==0]=band[al==0]*0 + band[al==0]  # (kept) inside body width only
    # only fill pixels that sit between opaque pixels of the head above and body below
    band &= ((al>0)|(np.roll(al,-ov,axis=0)>0)).astype(np.uint8)*255
    fill_src=im.copy(); fill_src[:neck_y,...,3]=0
    rgbfill=cv2.inpaint(np.ascontiguousarray(rgb),band,5,cv2.INPAINT_TELEA)
    body[band>0,:3]=rgbfill[band>0]; body[band>0,3]=255
    # crop both to bbox but keep coordinates relative to the full sprite
    os.makedirs(outdir,exist_ok=True)
    Image.fromarray(head).save(os.path.join(outdir,f'{name}_head.png'))
    Image.fromarray(body).save(os.path.join(outdir,f'{name}_body.png'))
    L=fh
    R=dict(w=W,h=H,top=int(top),bottom=int(bot),figH=int(fh),neck=dict(x=neck_x,y=int(neck_y)),head=dict(zip('xywh',[head_box[0],head_box[1],head_box[2]-head_box[0],head_box[3]-head_box[1]])),
           sockets=sockets,eyes=eyes,skin=skin,sleeve=sleeve,L1=round(0.145*L,1),L2=round(0.135*L,1),T=round(0.05*L,1),
           head_img=f'{name}_head.png',body_img=f'{name}_body.png')
    p=os.path.join(outdir,'rig.js'); txt=open(p).read() if os.path.exists(p) else 'window.RIG=window.RIG||{};\n'
    txt+=f'RIG[{json.dumps(name)}]={json.dumps(R)};\n'; open(p,'w').write(txt)
    # debug overlay
    dbg=Image.fromarray(im).convert('RGBA'); import PIL.ImageDraw as D; d=D.Draw(dbg)
    d.line([(0,neck_y),(W,neck_y)],fill=(255,0,0,255),width=2)
    for s in sockets.values(): d.ellipse([s['x']-6,s['y']-6,s['x']+6,s['y']+6],fill=(255,255,0,255))
    for e in eyes: d.rectangle([e['x'],e['y'],e['x']+e['w'],e['y']+e['h']],outline=(0,255,255,255),width=2)
    bg=Image.new('RGBA',dbg.size,(60,64,80,255)); bg.alpha_composite(dbg); bg.save(os.path.join(outdir,f'{name}_rigdebug.png'))
    print(json.dumps(R))
if __name__=='__main__': rig(*sys.argv[1:4])
