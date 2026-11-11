# Legenda palavra por palavra (ASS): versão vertical 1080x1920 e versão original 1920x1080
# uso: python3 legenda.py [vertical|original] [gray.raw]
import json, os, re, sys
import numpy as np
MODE = sys.argv[1] if len(sys.argv) > 1 else 'vertical'
W = json.load(open('audio/palavras.json'))
F = json.load(open('audio/frases.json'))
def ts(t): t = max(0, t); h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60; return f"{h}:{m:02d}:{s:05.2f}"
clean = lambda w: re.sub(r'[.,:;]', '', w).upper()
# blocos curtos dentro de cada frase: até 3 palavras ou ~18 caracteres
chunks, sent_of, i = [], [], 0
for fi, f in enumerate(F):
    n = len(f['s'].split()); ws = W[i:i + n]; i += n
    cur = []
    for k, w in enumerate(ws):
        cur.append(w)
        txt = ' '.join(clean(x['w']) for x in cur)
        nxt = ws[k + 1] if k + 1 < len(ws) else None
        brk = (w['w'][-1] in ',:?' or len(cur) >= 3 or len(txt) >= 16 or nxt is None) and not (w['w'] in ('Jim', 'Black') and nxt is not None)
        if brk: chunks.append(cur); sent_of.append(fi); cur = []
GOLD, WHITE = '&H008AD9FF&', '&H00FFFFFF&'
# original 16:9: para cada frase, legenda embaixo ou em cima, onde a faixa estiver mais livre
POS = {}
if MODE == 'original':
    raw = np.fromfile(sys.argv[2], np.uint8).reshape(-1, 270, 480).astype(np.float32)
    def busy(t0, t1, y0, y1):
        fr = raw[int(t0 * 10):max(int(t0 * 10) + 1, int(t1 * 10))]
        b = fr[:, y0:y1, :]
        return float((np.abs(np.diff(b, axis=2)) > 12).mean())
    for fi, f in enumerate(F):
        bot, top = busy(f['t0'], f['t1'], 228, 268), busy(f['t0'], f['t1'], 2, 42)
        POS[fi] = 'top' if bot > .065 and top < .01 else 'bottom'   # faixa baixa (y 1016-1068) livre das pílulas do vídeo; sobe só se embaixo estiver lotado
        print(f"{f['t0']:6.2f} {POS[fi]:6s} bot={bot:.3f} top={top:.3f} {f['s'][:40]}")
ev = []
for ci, ch in enumerate(chunks):
    end_chunk = ch[-1]['t1'] + .12
    nxt = chunks[ci + 1][0]['t0'] if ci + 1 < len(chunks) else 1e9
    end_chunk = min(max(end_chunk, ch[-1]['t1']), nxt)
    place = ''
    if MODE == 'original':
        place = '{\\an2\\pos(960,1070)}' if POS[sent_of[ci]] == 'bottom' else '{\\an8\\pos(960,30)}'
    for wi, w in enumerate(ch):
        a = w['t0']; b = ch[wi + 1]['t0'] if wi + 1 < len(ch) else end_chunk
        parts = [('{\\c' + (GOLD if j == wi else WHITE) + '}') + clean(x['w']) for j, x in enumerate(ch)]
        pop = '{\\fscx112\\fscy112\\t(0,120,\\fscx100\\fscy100)}' if wi == 0 else ''
        ev.append(f"Dialogue: 0,{ts(a)},{ts(b)},Leg,,0,0,0,,{place}{pop}{' '.join(parts)}")
if MODE == 'vertical':
    res, styles = (1080, 1920), """Style: Leg,Fredoka Bold,80,&H00FFFFFF,&H00FFFFFF,&H00281406,&H80281406,0,0,0,0,100,100,4,0,1,9,4,8,60,60,1270,1
Style: Topo,Fredoka Bold,44,&H00E6D88F,&H00FFFFFF,&H61281406,&H61281406,0,0,0,0,100,100,7,0,3,18,0,8,60,60,330,1"""
    extra = [f"Dialogue: 0,{ts(0.2)},{ts(70)},Topo,,0,0,0,,{{\\fad(400,0)}}" + os.environ.get("TOPO", "")] if os.environ.get("TOPO") else []
    out = 'legenda_vertical.ass'
else:
    res, styles = (1920, 1080), "Style: Leg,Fredoka Bold,54,&H00FFFFFF,&H00FFFFFF,&H00281406,&H80281406,0,0,0,0,100,100,3,0,1,7,3,2,60,60,40,1"
    extra = []; out = 'legenda_original.ass'
head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {res[0]}
PlayResY: {res[1]}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
{styles}

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
open(out, 'w', encoding='utf-8').write(head + '\n'.join(extra + ev) + '\n')
# SRT por frase (sem ponto final), útil como legenda separada
def srt(t): return f"{int(t//3600):02d}:{int(t%3600//60):02d}:{int(t%60):02d},{int(round((t%1)*1000)):03d}".replace(',1000', ',999')
with open('legenda.srt', 'w', encoding='utf-8') as fh:
    for k, f in enumerate(F, 1): fh.write(f"{k}\n{srt(f['t0'])} --> {srt(f['t1'] + .15)}\n{f['s'].rstrip('.')}\n\n")
print(len(chunks), 'blocos', len(ev), 'eventos', out)
