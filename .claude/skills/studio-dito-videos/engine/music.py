#!/usr/bin/env python3
"""Synthesized music beds in the DNA family (warm orchestral strings): music.py out.wav seconds [--seed N] [--mood calm|tense|bright]
String-ensemble pad (detuned saws, slow bow attack, vibrato, low-pass), cello bass on the root, soft pizzicato
on the beat. Seeded key + progression so each bed differs. Used when no licensed track can be downloaded."""
import sys, argparse, numpy as np, soundfile as sf
SR=48000
PROG={'calm':[[0,4,7],[9,0,4],[5,9,0],[7,11,2]],      # I vi IV V
      'tense':[[9,0,4],[5,9,0],[0,4,7],[7,11,2,5]],   # vi IV I V7
      'bright':[[0,4,7],[7,11,2],[9,0,4],[5,9,0]]}    # I V vi IV
def saw(f,t,ph): x=(f*t+ph)%1.0; return 2*x-1
def lp(x,fc):
    a=np.exp(-2*np.pi*fc/SR); y=np.empty_like(x); s=0.0
    # vectorised-ish one-pole via scipy-free loop in chunks
    for i in range(len(x)): s=(1-a)*x[i]+a*s; y[i]=s
    return y
def bed(seconds, seed=0, mood='calm', bpm=72):
    r=np.random.default_rng(seed); key=int(r.integers(0,12)); base=146.83*2**(key/12)/2  # around D3
    beat=60/bpm; bar=4*beat; n=int(seconds*SR); t=np.arange(n)/SR; out=np.zeros(n)
    prog=PROG[mood]; nb=int(np.ceil(seconds/bar))
    for b in range(nb):
        ch=prog[b%len(prog)]; t0=b*bar; i0=int(t0*SR); i1=min(n,int((t0+bar+0.6)*SR)); tt=t[i0:i1]-t0
        env=np.minimum(1,tt/0.9)*np.minimum(1,np.maximum(0,(bar+0.6-tt)/0.8))
        vib=1+0.004*np.sin(2*np.pi*5.2*tt)
        for k,semi in enumerate(ch):
            f=base*2**((semi+12)/12)
            for d in (-0.006,0,0.007):                     # three detuned bows per note
                out[i0:i1]+=0.06*env*saw(f*(1+d)*vib,tt,r.random())
        fr=base*2**(ch[0]/12)/2                            # cello root
        out[i0:i1]+=0.12*env*np.sin(2*np.pi*fr*tt)+0.05*env*saw(fr,tt,0)
        for q in range(4):                                 # pizzicato on the beat
            pi0=i0+int(q*beat*SR); L=int(0.35*SR); pe=min(n,pi0+L)
            if pi0>=n: break
            tp=np.arange(pe-pi0)/SR; fp=base*2**((ch[q%len(ch)]+24)/12)
            out[pi0:pe]+=0.05*np.sin(2*np.pi*fp*tp)*np.exp(-tp*9)
    out=lp(out,2400)
    # stereo width: tiny delay on the right
    R=np.roll(out,int(0.011*SR)); st=np.stack([out,0.9*R+0.1*out],1)
    st/=np.abs(st).max()+1e-9; st*=0.8
    fade=int(1.5*SR); st[:fade]*=np.linspace(0,1,fade)[:,None]; st[-fade:]*=np.linspace(1,0,fade)[:,None]
    return st.astype(np.float32)
if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('out'); ap.add_argument('seconds',type=float); ap.add_argument('--seed',type=int,default=0); ap.add_argument('--mood',default='calm')
    a=ap.parse_args(); sf.write(a.out,bed(a.seconds,a.seed,a.mood),SR); print(a.out)
