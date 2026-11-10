# Mixagem: voz + trilha (7 dB abaixo, sobe 5 dB no título) + efeitos alinhados pelo pico + master -14 LUFS / -2,2 dBTP
import json, subprocess, numpy as np, pyloudnorm as pyln
SR = 48000; DUR = 62.5
def load(path, start=None, dur=None):
    cmd = ['ffmpeg', '-v', 'error']
    if start is not None: cmd += ['-ss', str(start)]
    if dur is not None: cmd += ['-t', str(dur)]
    cmd += ['-i', path, '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-']
    return np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, np.float32).reshape(-1, 2).copy()
db = lambda x: 10 ** (x / 20)
meter = pyln.Meter(SR)
N = int(DUR * SR); out = np.zeros((N, 2), np.float32)
cues = json.load(open('shots/cues.json'))
# voz
voz = load('audio/voz.wav'); voz_l = meter.integrated_loudness(voz)
out[:len(voz)] += voz
# trilha: acorde final (65,0 s da faixa) cai no título
MUS_OFF = 65.0 - cues['antes']
mus = load('assets/music/Comfortable_Mystery_4.mp3', start=MUS_OFF, dur=DUR)
mus *= db(voz_l - 7 - meter.integrated_loudness(mus))
t = np.arange(len(mus)) / SR
env = np.clip(t / 1.2, 0, 1)                                           # entrada
env *= db(5 * np.clip((t - (cues['antes'] - 1.0)) / 1.0, 0, 1))         # sobe 5 dB sob o título
env *= np.clip((DUR - t) / 1.8, 0, 1)                                   # saída
out[:len(mus)] += mus * env[:, None]
# efeitos: um por tipo de evento, pico alinhado ao quadro, 4-10 dB abaixo da voz
voz_peak = np.abs(voz).max()
EV = [('colapso', cues['colapsa'], -8), ('impacto', cues['explode'], -4), ('whoosh', cues['explode'] + 1.2, -9),
      ('neutrinos', cues['neutrinos'], -9), ('mergulho', cues['particulas'] + .6, -8), ('tick', cues['trilhoes'], -10),
      ('pino', cues['voce'] + .12, -7), ('whoosh', cues['pull'] + 1.4, -8), ('tick', cues['parsec'], -9),
      ('clique', cues['banana'] + .1, -8), ('tick', cues['netuno'] + .2, -9), ('tick', cues['jupiter'] + .1, -9),
      ('tick', cues['cinturao'] + .3, -9), ('letal', cues['letal'], -5), ('clarao', cues['clarao'] + .2, -7),
      ('oculos', cues['oculos'] + .12, -6), ('rewind', cues['em'] + .4, -6), ('revelacao', cues['em'] + .82, -8),
      ('whoosh', cues['podem'] + .9, -9), ('revelacao', cues['antes'], -6)]
EV += [('ponto', cues['vinte2'] + i * .035 * 3, -14) for i in range(8)]
for name, at, g in EV:
    import os
    f = 'assets/sfx/' + name + ('.wav' if os.path.exists('assets/sfx/' + name + '.wav') else '.ogg')
    x = load(f); env_ = np.abs(x).max(1); pk = int(np.argmax(env_))
    x *= db(g) * voz_peak / (env_.max() + 1e-9)
    i0 = int(at * SR) - pk
    a0, b0 = max(0, i0), min(N, i0 + len(x))
    out[a0:b0] += x[a0 - i0:b0 - i0]
# master: ganho para -14 LUFS e limitador para -2,2 dBTP (oversampling 4x para o pico real)
out *= db(-14 - meter.integrated_loudness(out))
from scipy.signal import resample_poly
ceil = db(-2.5)
for _ in range(4):
    up = resample_poly(out, 4, 1, axis=0); pk = np.abs(up).max(1)
    g = np.minimum(1, ceil / np.maximum(pk, 1e-9))
    # ganho suavizado: ataque com olhar à frente e liberação de 80 ms
    g = np.minimum.reduceat(g, np.arange(0, len(g), 4))[:len(out)]
    from scipy.ndimage import minimum_filter1d, uniform_filter1d
    g = minimum_filter1d(g, 96); g = uniform_filter1d(g, 96)
    rel = np.copy(g); k = np.exp(-1 / (0.08 * SR))
    for i in range(1, len(rel)): rel[i] = min(g[i], rel[i - 1] * k + (1 - k))
    out *= rel[:, None]
    if np.abs(resample_poly(out, 4, 1, axis=0)).max() <= ceil * 1.001: break
out *= db(-14 - meter.integrated_loudness(out)) if meter.integrated_loudness(out) < -14.2 else 1
out = np.clip(out, -ceil, ceil)
print('LUFS', round(meter.integrated_loudness(out), 2), 'TP dB', round(20 * np.log10(np.abs(resample_poly(out, 4, 1, axis=0)).max()), 2))
import soundfile as sf; sf.write('audio/mix.wav', out, SR, subtype='PCM_24')
