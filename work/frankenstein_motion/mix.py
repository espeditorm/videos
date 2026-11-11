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
mus = load('../assets/music/Comfortable_Mystery_4.mp3', start=MUS_OFF, dur=DUR)
mus *= db(voz_l - 7 - meter.integrated_loudness(mus))
t = np.arange(len(mus)) / SR
env = np.clip(t / 1.2, 0, 1) * db(5 * np.clip((t - (TITLE - 1.0)) / 1.0, 0, 1)) * np.clip((DUR - t) / 1.6, 0, 1)
out[:len(mus)] += mus * env[:, None]
vp = np.abs(voz).max()
T = dict(t1=c['livro1'] - .25, t2=c['hoje1'] - .15, t3=c['escrito'] - .6, t4=c['entao'] - .2)
RW0 = c['RW0']
EV = [('impacto', c['escreveu'], -10), ('mergulho', T['t1'] + .3, -8), ('clarao', c['vida'], -5), ('impacto', c['vida'] + .1, -8),
      ('whoosh', c['consequencias'], -10), ('slam_01', c['perigosa'], -7), ('pino', c['frank2'], -8), ('impacto', c['criatura2'], -9),
      ('whoosh', c['criador'] - .1, -8), ('bell_02', c['criador'] + .4, -9), ('mergulho', T['t2'] + .3, -8), ('switch_01', c['costuras'] + .25, -9),
      ('switch_01', c['eletricidade'] + .25, -9), ('revelacao', c['inteligencias'], -8), ('whoosh', c['carro'] - .1, -9), ('tick', c['proteger'], -8),
      ('whoosh', c['algoritmo'] - .1, -9), ('slam_01', c['preconceitos'], -6), ('whoosh', c['rosto'], -9), ('tick', c['decisoes'], -9),
      ('whoosh', T['t3'] + .3, -8), ('impacto', c['aviso'], -9), ('mergulho', T['t4'] + .3, -8), ('pino', c['aliadas'], -8),
      ('slam_01', c['monstros2'] - .1, -6), ('rewind', RW0 + .4, -6), ('revelacao', TITLE, -6)]
EV += [('tick', c['algoritmo'] + .45 + i * .45, -13) for i in range(4)]
EV += [('plop_02', c['recomendacoes'] + i * .14, -16) for i in range(6)]
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
