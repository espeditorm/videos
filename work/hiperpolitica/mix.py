# Mixagem: voz + trilha (7 dB abaixo, sobe 5 dB no título) + efeitos alinhados pelo pico + master -14 LUFS / -2,2 dBTP
import json, os, subprocess, numpy as np, pyloudnorm as pyln, soundfile as sf
from scipy.signal import resample_poly
from scipy.ndimage import minimum_filter1d, uniform_filter1d
from scipy.signal import butter, sosfiltfilt
LP = butter(4, 9000, 'low', fs=48000, output='sos')
SR = 48000
def load(path, start=None, dur=None):
    cmd = ['ffmpeg', '-v', 'error']
    if start is not None: cmd += ['-ss', str(start)]
    if dur is not None: cmd += ['-t', str(dur)]
    cmd += ['-i', path, '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-']
    return np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, np.float32).reshape(-1, 2).copy()
db = lambda x: 10 ** (x / 20)
meter = pyln.Meter(SR)
c = json.load(open('shots/cues.json')); DUR = c['DUR']   # duração exportada pelo motor
N = int(DUR * SR); out = np.zeros((N, 2), np.float32)
TITLE = c['TITLE']   # o motor exporta C.TITLE (início do título)
voz = load('audio/voz.wav'); voz_l = meter.integrated_loudness(voz); out[:len(voz)] += voz
MUS_OFF = 65.0 - TITLE            # acorde final da faixa cai no título
MP = '../assets/music/Comfortable_Mystery_4.mp3'
if MUS_OFF >= 0: mus = load(MP, start=MUS_OFF, dur=DUR)
else:   # vídeo mais longo que a faixa: um trecho do início como introdução, emendado com crossfade de 2 s
    lead = -MUS_OFF; X = int(2 * SR); L = int(lead * SR); NN = int(DUR * SR)
    pre = load(MP, start=20, dur=lead + 2); main = load(MP, start=0, dur=DUR - lead)
    w = np.linspace(0, 1, X, dtype=np.float32)[:, None]
    pre[-X:] *= (1 - w)[-len(pre[-X:]):]; main[:X] *= w
    mus = np.zeros((NN, 2), np.float32); mus[:len(pre)] += pre[:NN]; n = min(len(main), NN - L); mus[L:L + n] += main[:n]
mus *= db(voz_l - 7 - meter.integrated_loudness(mus))
t = np.arange(len(mus)) / SR
env = np.clip(t / 1.2, 0, 1) * db(5 * np.clip((t - (TITLE - 1.0)) / 1.0, 0, 1)) * np.clip((DUR - t) / 1.6, 0, 1)
out[:len(mus)] += mus * env[:, None]
vp = np.abs(voz).max()
T = [c['multiplique'] - .3, c['historiador'] - .35, c['entender'] - .3, c['sindicatos'] - .55, c['nos'] - .3, c['redes'] - .15, c['facil1'] - .3, c['por2'] - .3, c['jager2'] - .3, c['entao'] - .3]
RW0 = c['RW0']
EV = [('pino', c['voce'] + .1, -8), ('plop_02', c['post1'], -9), ('whoosh', c['compartilha'] + .1, -7)]
EV += [('mergulho' if i % 2 == 0 else 'whoosh', t + .3, -8) for i, t in enumerate(T)]
EV += [('plop_02', c['milhoes'] + .1 * k, -14) for k in range(6)]
EV += [('revelacao', c['hiper'] + .05, -7), ('impacto', c['sem1'] + .1, -8), ('tick', c['importa'], -9), ('tick', c['organiza'], -9),
       ('pino', c['seculo'] + .05, -8), ('plop_02', c['sindicatos'], -8), ('plop_02', c['partidos'], -8), ('plop_02', c['igrejas'], -8), ('plop_02', c['clubes'], -8),
       ('clarao', c['multidoes'] + .1, -9), ('slam_01', c['muro'] + .2, -8), ('whoosh', c['despencaram'] + .1, -8), ('paper_02', c['gestao'], -10),
       ('impacto', c['crise'] + .2, -8), ('buzz', c['raiva1'] + .1, -12), ('slam_01', c['trump'], -9), ('slam_01', c['brexit'], -9),
       ('plop_02', c['hashtags'], -8), ('clarao', c['explodem'] + .1, -9), ('whoosh', c['semanas'] + .2, -9), ('bell_02', c['outro'] + .05, -8),
       ('tick', c['reuniao'], -9), ('tick', c['mensalidade'], -9), ('tick', c['anos2'], -9), ('switch_01', c['like'] + .05, -6), ('bell_02', c['segundo'], -9),
       ('tick', c['lei'], -9), ('tick', c['salario'], -9), ('tick', c['voto'], -9), ('paper_02', c['basta'], -8),
       ('plop_02', c['post2'], -9), ('pino', c['pergunte'] + .05, -9), ('rewind', RW0 + .4, -6), ('revelacao', c['TITLE'], -6)]
for name, at, g in EV:
    f = next(p for p in [f'assets/sfx/{name}.{e}' for e in ('wav', 'ogg')] if os.path.exists(p))
    x = load(f)
    x = sosfiltfilt(LP, x, axis=0).astype(np.float32)          # tira o agudo extremo que estoura no AAC
    x[:96] *= np.linspace(0, 1, 96)[:, None]
    e = np.abs(x).max(1); pk = int(np.argmax(e))
    x *= db(g) * vp / (e.max() + 1e-9)
    i0 = int(at * SR) - pk; a0, b0 = max(0, i0), min(N, i0 + len(x))
    out[a0:b0] += x[a0 - i0:b0 - i0]
# master: ganho para -14 LUFS e limitador de pico real (oversampling 4x) a -2,2 dBTP
out *= db(-14 - meter.integrated_loudness(out))
ceil = db(-3.0)
for _ in range(5):
    up = resample_poly(out, 4, 1, axis=0); pk = np.abs(up).max(1)
    g = np.minimum(1, ceil / np.maximum(pk, 1e-9))
    g = np.minimum.reduceat(g, np.arange(0, len(g), 4))[:len(out)]
    g = minimum_filter1d(g, 96); g = uniform_filter1d(g, 96)
    rel = np.copy(g); k = np.exp(-1 / (0.08 * SR))
    for i in range(1, len(rel)): rel[i] = min(g[i], rel[i - 1] * k + (1 - k))
    out *= rel[:, None]
    L = meter.integrated_loudness(out)
    if L < -14.1: out *= db(-14 - L)
    if np.abs(resample_poly(out, 4, 1, axis=0)).max() <= db(-2.9) and abs(meter.integrated_loudness(out) + 14) < .15: break
out = np.clip(out, -db(-2.9), db(-2.9))
print('LUFS', round(meter.integrated_loudness(out), 2), 'TP dB', round(20 * np.log10(np.abs(resample_poly(out, 4, 1, axis=0)).max()), 2))
sf.write('audio/mix.wav', out, SR, subtype='PCM_24')
