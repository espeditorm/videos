#!/usr/bin/env python3
"""Mix: voice + music beds (ducked) + SFX events -> two-pass loudnorm -14 LUFS / -1 dBTP.
usage: audio.py voice.wav events.json out.wav --dur D [--music a.mp3,b.mp3] [--chapters t1,t2] [--sfxdir dir]
SFX: library/sfx/<name>.wav if present (Mixkit downloads), else synthesized to match the Punchy personality.
Gate: during speech the voice sits >=15 dB over music+SFX (median of 100 ms frames); background louder than voice <1% of frames."""
import os, sys, json, argparse, subprocess, numpy as np, soundfile as sf
SR=48000; ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def load(p):
    if p.endswith('.wav'):
        a,sr=sf.read(p,dtype='float32',always_2d=True)
    else:
        raw=subprocess.run(['ffmpeg','-loglevel','error','-i',p,'-f','f32le','-ac','2','-ar',str(SR),'-'],capture_output=True).stdout
        return np.frombuffer(raw,np.float32).reshape(-1,2).copy()
    a=a if a.shape[1]==2 else np.repeat(a,2,axis=1)
    if sr!=SR:
        n=int(len(a)*SR/sr); x=np.linspace(0,len(a)-1,n); a=np.stack([np.interp(x,np.arange(len(a)),a[:,c]) for c in range(2)],1).astype(np.float32)
    return a
def env(n,a,d): t=np.arange(n)/SR; return np.minimum(1,t/a)*np.exp(-t/d)
def synth(name):
    t=lambda s:np.arange(int(s*SR))/SR; r=np.random.default_rng(abs(hash(name))%2**32)
    if name=='pop':   x=np.sin(2*np.pi*(380+900*np.exp(-t(.12)*40))*t(.12))*env(int(.12*SR),.002,.03)
    elif name=='tick':x=(r.standard_normal(int(.03*SR))*0.4+np.sin(2*np.pi*2600*t(.03)))*env(int(.03*SR),.0005,.006)*0.5
    elif name=='whoosh':
        n=int(.38*SR); w=r.standard_normal(n); k=np.sin(np.linspace(0,np.pi,n))**2
        f=np.cumsum(w); f-=np.convolve(f,np.ones(40)/40,'same'); x=f/np.abs(f).max()*k*0.8
    elif name=='thud': x=(np.sin(2*np.pi*(60+120*np.exp(-t(.35)*20))*t(.35))+0.3*r.standard_normal(int(.35*SR))*np.exp(-t(.35)*60))*env(int(.35*SR),.001,.09)
    elif name=='hit':  x=(np.sin(2*np.pi*(140+300*np.exp(-t(.25)*30))*t(.25))+0.5*r.standard_normal(int(.25*SR))*np.exp(-t(.25)*45))*env(int(.25*SR),.001,.06)
    elif name=='ding': x=(np.sin(2*np.pi*1320*t(.9))+0.4*np.sin(2*np.pi*2640*t(.9)))*env(int(.9*SR),.002,.25)*0.6
    elif name=='boing':x=np.sin(2*np.pi*(220+160*np.sin(t(.4)*30)*np.exp(-t(.4)*6))*t(.4))*env(int(.4*SR),.002,.12)
    else: x=np.zeros(10)
    x=x/max(1e-6,np.abs(x).max())*0.7; return np.stack([x,x],1).astype(np.float32)
def sfx(name,sfxdir):
    for d in [sfxdir,os.path.join(ROOT,'library','sfx')]:
        if d:
            for ext in ('.wav','.mp3'):
                p=os.path.join(d,name+ext)
                if os.path.exists(p): return load(p)
    return synth(name)
def frames_db(a,fr=int(0.1*SR)):
    m=a.mean(1) if a.ndim>1 else a; n=len(m)//fr
    return 20*np.log10(np.sqrt((m[:n*fr].reshape(n,fr)**2).mean(1))+1e-9)
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('voice'); ap.add_argument('events'); ap.add_argument('out'); ap.add_argument('--dur',type=float,required=True)
    ap.add_argument('--music',default=''); ap.add_argument('--chapters',default=''); ap.add_argument('--sfxdir',default=''); ap.add_argument('--music-db',type=float,default=-20)
    a=ap.parse_args(); N=int(a.dur*SR)
    v=load(a.voice); voice=np.zeros((N,2),np.float32); voice[:min(N,len(v))]=v[:N]
    # --- SFX bus, peaks aligned to event time, -6 dB while speech is active
    vdb=np.repeat(frames_db(voice),int(0.1*SR)); vdb=np.pad(vdb,(0,max(0,N-len(vdb))),constant_values=-90)[:N]
    fx=np.zeros((N,2),np.float32)
    for e in json.load(open(a.events)):
        s=sfx(e['name'],a.sfxdir); pk=int(np.argmax(np.abs(s).max(1))); st=int(e['t']*SR)-pk
        g=e.get('gain',1)*(0.5 if vdb[min(N-1,max(0,int(e['t']*SR)))]>-40 else 1.0)*0.35
        lo=max(0,st); hi=min(N,st+len(s))
        if hi>lo: fx[lo:hi]+=s[lo-st:hi-st]*g
    # --- music beds crossfaded over 3 s, ducked under the voice
    mus=np.zeros((N,2),np.float32)
    beds=[load(m) for m in a.music.split(',') if m]
    if beds:
        cuts=[0]+[int(float(c)*SR) for c in a.chapters.split(',') if c][:len(beds)-1]+[N]
        for i,b in enumerate(beds):
            s0,s1=cuts[i],cuts[i+1]; seg_len=s1-s0+3*SR; bb=np.tile(b,(seg_len//len(b)+1,1))[:seg_len]
            w=np.ones(seg_len); xf=3*SR
            if i>0: w[:xf]=np.linspace(0,1,xf)
            if i<len(beds)-1: w[-xf:]=np.linspace(1,0,xf)
            lo=max(0,s0-(xf if i>0 else 0)); seg=bb[:min(seg_len,N-lo)]*w[:min(seg_len,N-lo),None]; mus[lo:lo+len(seg)]+=seg
        mus*=10**(a.music_db/20)/max(1e-6,np.sqrt((mus**2).mean())*1.4)
        # sidechain: 30 ms attack, 0.3 s hold, 0.45 s release; -12 dB under speech
        speech=(vdb>-38).astype(float); hold=int(0.3*SR); g=np.ones(N); cur=1.0; last=-10**9
        att=np.exp(-1/(0.03*SR)); rel=np.exp(-1/(0.45*SR)); dk=10**(-12/20)
        idx=np.nonzero(speech)[0]; sp=np.zeros(N,bool); sp[idx]=True
        for i in range(N):
            if sp[i]: last=i
            tgt=dk if i-last<hold else 1.0
            cur=tgt+(cur-tgt)*(att if tgt<cur else rel); g[i]=cur
        mus*=g[:,None]
    bg=mus+fx; mix=voice+bg
    # --- gate check
    vf=frames_db(voice); bf=frames_db(bg); sp=vf>-38
    diff=(vf-bf)[sp]; med=float(np.median(diff)) if sp.any() else 99; louder=float(((bf>vf)&sp).mean()) if sp.any() else 0
    tmp=a.out+'.pre.wav'; sf.write(tmp,np.clip(mix,-1,1),SR)
    # --- two-pass loudnorm
    r=subprocess.run(['ffmpeg','-hide_banner','-i',tmp,'-af','loudnorm=I=-14:TP=-1:LRA=11:print_format=json','-f','null','-'],capture_output=True,text=True).stderr
    m=json.loads(r[r.rindex('{'):r.rindex('}')+1])
    af=f"loudnorm=I=-14:TP=-1:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true"
    subprocess.run(['ffmpeg','-loglevel','error','-y','-i',tmp,'-af',af,'-ar',str(SR),a.out],check=True); os.remove(tmp)
    rep={'voice_over_bg_median_db':round(med,1),'bg_louder_frac':round(louder,4),'gate_ok':med>=15 and louder<0.01}
    print(json.dumps(rep)); return rep
if __name__=='__main__': main()
