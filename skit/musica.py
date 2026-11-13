# Trilha original gerada em código (sem licença de terceiros): lo-fi leve e brincalhona,
# pad quente + pluck tipo marimba + baixo redondo + bip de computador de vez em quando.
# python musica.py [duração_s]  -> assets/musica.wav
import sys, numpy as np, soundfile as sf
SR = 48000; BPM = 92; BEAT = 60 / BPM
DUR = float(sys.argv[1]) if len(sys.argv) > 1 else 50
N = int(DUR * SR) + SR
rng = np.random.default_rng(3)
nota = lambda m: 440 * 2 ** ((m - 69) / 12)
mix = np.zeros((N, 2))

def add(sig, t, pan=0.0, g=1.0):
    i = int(t * SR); j = min(i + len(sig), N)
    if i >= N: return
    s = sig[: j - i] * g
    mix[i:j, 0] += s * np.sqrt(0.5 * (1 - pan)); mix[i:j, 1] += s * np.sqrt(0.5 * (1 + pan))

def env(n, a, d, s=0.0):
    t = np.arange(n) / SR
    return np.minimum(t / a, 1) * (s + (1 - s) * np.exp(-t / d))

def pluck(f, dur=0.9):  # marimba macia: seno + 4º harmônico curto
    n = int(dur * SR); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * f * t) + 0.25 * np.sin(2 * np.pi * 4 * f * t) * np.exp(-t / 0.05)) * env(n, 0.004, 0.28)

def pad(fs, dur):  # acorde com leve detune, filtrado no "olho"
    n = int(dur * SR); t = np.arange(n) / SR; s = np.zeros(n)
    for f in fs:
        for dt in (-0.12, 0.12):
            s += np.sin(2 * np.pi * (f + dt) * t + rng.uniform(0, 6)) + 0.18 * np.sin(4 * np.pi * (f + dt) * t)
    e = np.minimum(t / 0.6, 1) * np.minimum((dur - t) / 0.6, 1)
    return s / len(fs) * e

def baixo(f, dur):
    n = int(dur * SR); t = np.arange(n) / SR
    return np.tanh(1.5 * np.sin(2 * np.pi * f * t)) * env(n, 0.01, 0.5, 0.35)

def kick():
    n = int(0.35 * SR); t = np.arange(n) / SR
    return np.sin(2 * np.pi * (48 + 70 * np.exp(-t / 0.03)) * t) * np.exp(-t / 0.12)

def chiado():  # hi-hat suave
    n = int(0.06 * SR); x = rng.standard_normal(n); x = np.diff(np.concatenate([[0], x]))
    return x * np.exp(-np.arange(n) / SR / 0.015)

def bip(f):  # bip de computador antigo (onda quadrada curta)
    n = int(0.09 * SR); t = np.arange(n) / SR
    return np.sign(np.sin(2 * np.pi * f * t)) * env(n, 0.002, 0.03) * 0.5

# progressão: Fmaj7 - Em7 - Dm7 - G7sus (2 compassos cada)
CH = [[53, 57, 60, 64], [52, 55, 59, 62], [50, 53, 57, 60], [55, 60, 62, 65]]
BX = [41, 40, 38, 43]
ARP = [[65, 69, 72, 76], [64, 67, 71, 74], [62, 65, 69, 72], [67, 72, 74, 77]]
bar = 4 * BEAT; t = 0.0; k = 0
while t < DUR:
    c = k % 4
    add(pad([nota(m) for m in CH[c]], 2 * bar + 0.3), t, 0, 0.11)
    for b in range(2):
        tb = t + b * bar
        add(baixo(nota(BX[c]), BEAT * 1.5), tb, 0, 0.22); add(baixo(nota(BX[c] + 7), BEAT * 0.9), tb + 2.5 * BEAT, 0, 0.16)
        if k >= 1 or b == 1:
            for q in range(4): add(kick(), tb + q * BEAT, 0, 0.30 if q % 2 == 0 else 0.18)
            for q in range(8): add(chiado(), tb + q * BEAT / 2 + 0.01 * rng.standard_normal(), 0.3, 0.05 if q % 2 else 0.025)
        # arpejo marimba com swing leve
        pat = [0, 2, 1, 3, 2, 1, 3, 2]
        for q, p in enumerate(pat):
            if rng.random() < 0.82:
                add(pluck(nota(ARP[c][p])), tb + q * BEAT / 2 + (0.035 if q % 2 else 0), -0.35 + 0.7 * rng.random(), 0.16)
    if k % 2 == 1:  # bipinhos de computador no fim de cada ciclo
        for q, m in enumerate([84, 88, 91]): add(bip(nota(m)), t + 2 * bar - BEAT + q * 0.12, 0.5, 0.05)
    t += 2 * bar; k += 1

# "sala": eco curto estéreo + leve saturação e fade
out = mix.copy()
for d, g in [(0.083, 0.18), (0.131, 0.12), (0.197, 0.08)]:
    s = int(d * SR); out[s:, 0] += mix[:-s, 1] * g; out[s:, 1] += mix[:-s, 0] * g
out = np.tanh(out * 1.2) / 1.2
out = out[: int(DUR * SR)]
fade = np.ones(len(out)); fi, fo = int(1.0 * SR), int(2.5 * SR)
fade[:fi] = np.linspace(0, 1, fi); fade[-fo:] = np.linspace(1, 0, fo)
out *= fade[:, None]; out = out / np.abs(out).max() * 0.7
import os; os.makedirs("assets", exist_ok=True)
sf.write("assets/musica.wav", out.astype(np.float32), SR)
print("ok", DUR, "s")
