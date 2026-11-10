# Legenda palavra por palavra (ASS) para a versão vertical 1080x1920
import json, re
W = json.load(open('audio/palavras.json'))
F = json.load(open('audio/frases.json'))
def ts(t): t = max(0, t); h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60; return f"{h}:{m:02d}:{s:05.2f}"
clean = lambda w: re.sub(r'[.,:;]', '', w).upper()
# blocos curtos dentro de cada frase: até 3 palavras ou ~18 caracteres
chunks, i = [], 0
for f in F:
    n = len(f['s'].split()); ws = W[i:i + n]; i += n
    cur = []
    for k, w in enumerate(ws):
        cur.append(w)
        txt = ' '.join(clean(x['w']) for x in cur)
        nxt = ws[k + 1] if k + 1 < len(ws) else None
        brk = (w['w'][-1] in ',:?' or len(cur) >= 3 or len(txt) >= 16 or nxt is None) and not (w['w'] == 'Jim' and nxt is not None)
        if brk: chunks.append(cur); cur = []
GOLD, WHITE = '&H008AD9FF&', '&H00FFFFFF&'
ev = []
for ci, ch in enumerate(chunks):
    end_chunk = ch[-1]['t1'] + .12
    nxt = chunks[ci + 1][0]['t0'] if ci + 1 < len(chunks) else 1e9
    end_chunk = min(max(end_chunk, ch[-1]['t1']), nxt)
    for wi, w in enumerate(ch):
        a = w['t0']; b = ch[wi + 1]['t0'] if wi + 1 < len(ch) else end_chunk
        parts = [('{\\c' + (GOLD if j == wi else WHITE) + '}') + clean(x['w']) for j, x in enumerate(ch)]
        pop = '{\\fscx112\\fscy112\\t(0,120,\\fscx100\\fscy100)}' if wi == 0 else ''
        ev.append(f"Dialogue: 0,{ts(a)},{ts(b)},Leg,,0,0,0,,{pop}{' '.join(parts)}")
head = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Leg,Fredoka Bold,80,&H00FFFFFF,&H00FFFFFF,&H00281406,&H80281406,0,0,0,0,100,100,4,0,1,9,4,8,60,60,1270,1
Style: Topo,Fredoka Bold,44,&H00E6D88F,&H00FFFFFF,&H61281406,&H61281406,0,0,0,0,100,100,7,0,3,18,0,8,60,60,330,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
top = f"Dialogue: 0,{ts(0.2)},{ts(70)},Topo,,0,0,0,,{{\\fad(400,0)}}HAVAÍ · 13 DE JANEIRO DE 2018"
open('legenda_vertical.ass', 'w', encoding='utf-8').write(head + top + '\n' + '\n'.join(ev) + '\n')
print(len(chunks), 'blocos', len(ev), 'eventos')
