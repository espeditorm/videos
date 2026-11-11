#!/usr/bin/env python3
"""Free voice route: Kokoro TTS -> pause trim -> faster-whisper word times -> words.js
usage: voice.py script.txt outdir [--voice am_onyx] [--speed 1.0]
script.txt: chapters separated by a line '---' (0.5 s pause kept there). Speaker tags not needed.
Writes outdir/voice.wav (24 kHz mono, 0.3 s lead-in) and outdir/words.js (window.WORDS=[{w,s,e}]) and diff report."""
import os, sys, re, json, argparse, difflib, numpy as np, soundfile as sf
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS=os.path.join(ROOT,'work','models')
SR=24000

def tts(text, voice, speed):
    from kokoro_onnx import Kokoro
    k=Kokoro(os.path.join(MODELS,'kokoro-v1.0.onnx'),os.path.join(MODELS,'voices-v1.0.bin'))
    a,sr=k.create(text,voice=voice,speed=speed,lang='en-us'); assert sr==SR; return a.astype(np.float32)

def trim_pauses(a, maxp=0.24, keep=0.16, thr_db=-42):
    fr=int(0.01*SR); n=len(a)//fr; e=np.array([np.sqrt(np.mean(a[i*fr:(i+1)*fr]**2)+1e-12) for i in range(n)])
    db=20*np.log10(e+1e-9); quiet=db<thr_db; out=[]; i=0
    while i<n:
        if quiet[i]:
            j=i
            while j<n and quiet[j]: j+=1
            dur=(j-i)*0.01
            if dur>maxp and i>0 and j<n: out.append(a[i*fr:i*fr+int(keep*SR)])
            else: out.append(a[i*fr:j*fr])
            i=j
        else: out.append(a[i*fr:(i+1)*fr]); i+=1
    out.append(a[n*fr:]); return np.concatenate(out)

def words_from_whisper(wav):
    from faster_whisper import WhisperModel
    m=WhisperModel('small.en',device='cpu',compute_type='int8',download_root=MODELS)
    # pass a 16 kHz float array: avoids PyAV API drift in faster_whisper.decode_audio
    import subprocess
    raw=subprocess.run(['ffmpeg','-loglevel','error','-i',wav,'-f','f32le','-ac','1','-ar','16000','-'],capture_output=True).stdout
    audio=np.frombuffer(raw,np.float32).copy()
    segs,_=m.transcribe(audio,word_timestamps=True,beam_size=5,vad_filter=False)
    W=[]
    for s in segs:
        for w in s.words: W.append(dict(w=w.word.strip(),s=round(w.start,3),e=round(w.end,3)))
    return W

NUM={'eighteen forty':'1840'}
def num2words_light(s):
    # whisper writes numbers as digits; compare in digit form
    try:
        from word2number import w2n
    except Exception: w2n=None
    return s
def norm(s): return re.sub(r"[^a-z0-9' ]","",s.lower())
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('script'); ap.add_argument('outdir'); ap.add_argument('--voice',default='am_onyx'); ap.add_argument('--speed',type=float,default=1.0)
    a=ap.parse_args(); os.makedirs(a.outdir,exist_ok=True)
    chapters=[c.strip() for c in open(a.script).read().split('\n---\n') if c.strip()]
    parts=[np.zeros(int(0.3*SR),np.float32)]
    for i,c in enumerate(chapters):
        au=trim_pauses(tts(' '.join(c.split()),a.voice,a.speed))
        parts.append(au)
        if i<len(chapters)-1: parts.append(np.zeros(int(0.5*SR),np.float32))
    audio=np.concatenate(parts); wav=os.path.join(a.outdir,'voice.wav'); sf.write(wav,audio,SR)
    W=words_from_whisper(wav)
    open(os.path.join(a.outdir,'words.js'),'w').write('window.WORDS='+json.dumps(W)+';\nwindow.VOICE_DUR='+str(round(len(audio)/SR,3))+';\n')
    # diff against script
    sw=norm(' '.join(chapters)).split(); ww=[norm(w['w']) for w in W]
    # numbers: treat a digit token in whisper as matching any run of number words in the script
    NW=set('zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen twenty thirty forty fifty sixty seventy eighty ninety hundred thousand million billion and'.split())
    sw2=[];i=0
    while i<len(sw):
        if sw[i] in NW and sw[i]!='and':
            j=i
            while j<len(sw) and sw[j] in NW: j+=1
            sw2.append('#'); i=j
        else: sw2.append(sw[i]); i+=1
    sw=sw2; ww=['#' if re.fullmatch(r"[0-9][0-9,.]*",w) else w for w in ww]
    sm=difflib.SequenceMatcher(None,sw,ww); bad=[(op,' '.join(sw[i1:i2]),' '.join(ww[j1:j2])) for op,i1,i2,j1,j2 in sm.get_opcodes() if op!='equal']
    rep={'duration':round(len(audio)/SR,2),'words':len(W),'wpm':round(len(sw)/(len(audio)/SR)*60),'match':round(sm.ratio(),3),'diffs':bad}
    json.dump(rep,open(os.path.join(a.outdir,'voice_report.json'),'w'),indent=1); print(json.dumps(rep,indent=1))
if __name__=='__main__': main()
