#!/usr/bin/env python3
"""BEA Technology Division — TRUST vision ad score (Nike-style cinematic hybrid).
Structure locked to render_trust.js timeline (41.2s, 120 BPM):
  0-1.0 heartbeat -> 1.0/2.5/4.0 hook hits -> 5.65 IT'S -> 6.15 TRUST. full hit
  -> letter section 9.3-25.9 (roots F-Ab-C-Eb-F rising, layers grow per letter)
  -> 30.05..32.05 montage T-R-U-S-T five hits -> 32.65 lock swell
  -> 34.2 sign-off F-major tutti -> warm outro, fade 39.7.
Output: music_trust.wav (used by both zh/en videos)."""
import math
import wave

import numpy as np

SR = 44100
DUR = 41.2
N = int(DUR * SR)
BPM = 120
BEAT = 0.5
S16 = 0.125
rng = np.random.default_rng(42)

NOTE = {
    'F1': 43.65, 'Ab1': 51.91, 'C2': 65.41, 'Db2': 69.30, 'Eb2': 77.78,
    'F2': 87.31, 'Ab2': 103.83, 'Bb2': 116.54, 'C3': 130.81, 'Db3': 138.59,
    'Eb3': 155.56, 'F3': 174.61, 'Ab3': 207.65, 'Bb3': 233.08, 'C4': 261.63,
    'Db4': 277.18, 'Eb4': 311.13, 'G4': 392.0, 'A3': 220.0, 'F4': 349.23,
    'Ab4': 415.30, 'Bb4': 466.16, 'C5': 523.25, 'Db5': 554.37, 'Eb5': 622.25,
    'F5': 698.46, 'Ab5': 830.61, 'C6': 1046.5,
}
CH = {
    'Fm': ['F3', 'Ab3', 'C4'],
    'Ab': ['Ab3', 'C4', 'Eb4'],
    'Cm': ['C4', 'Eb4', 'G4'],
    'Eb': ['Eb4', 'G4', 'Bb4'],
    'FM': ['F3', 'A3', 'C4'],
    'FM8': ['F2', 'F3', 'A3', 'C4', 'F4'],
}

L = np.zeros(N)
R = np.zeros(N)


def mvavg(x, k):
    if k < 2:
        return x
    return np.convolve(x, np.ones(k) / k, mode='same')


def add(sig, t0, pan=0.0, gain=1.0):
    i = int(t0 * SR)
    if i >= N or i < 0:
        return
    n = min(len(sig), N - i)
    if n <= 0:
        return
    ang = (pan + 1) * 0.25 * math.pi
    L[i:i + n] += sig[:n] * gain * math.cos(ang)
    R[i:i + n] += sig[:n] * gain * math.sin(ang)


def env_exp(n, k):
    return np.exp(-np.arange(n) / SR * k)


# ---------- instruments (from v9 palette) ----------
def strings(freqs, dur, gain=1.0, attack=0.35, release=0.6):
    n = int(dur * SR); tt = np.arange(n) / SR
    x = np.zeros(n)
    for f in freqs:
        base = NOTE[f]
        for det in (-0.007, -0.0023, 0.0023, 0.007):
            fr = base * (1 + det)
            ph = rng.uniform(0, 1.0)
            x += 2 * ((tt * fr / SR + ph) % 1.0) - 1
    x /= (len(freqs) * 4)
    x = mvavg(x, 7)
    x += 0.012 * (rng.standard_normal(n) - mvavg(rng.standard_normal(n), 8))
    a = np.clip(tt / attack, 0, 1) ** 1.6 * np.clip((dur - tt) / release, 0, 1) ** 1.1
    a *= 1 + 0.05 * np.sin(2 * np.pi * 0.9 * tt + rng.uniform(0, 6.28))
    return x * a * gain


def stac(freqs, gain=1.0, dur=0.20):
    n = int(dur * SR); tt = np.arange(n) / SR
    x = np.zeros(n)
    for f in freqs:
        base = NOTE[f]
        for det in (-0.005, 0.005):
            x += 2 * ((tt * base * (1 + det) / SR + rng.uniform(0, 1)) % 1.0) - 1
    x /= (len(freqs) * 2)
    x = mvavg(x, 6)
    a = np.clip(tt / 0.012, 0, 1) * np.exp(-tt * 16)
    return x * a * gain


def piano(f, dur=2.4, gain=1.0):
    n = int(dur * SR); tt = np.arange(n) / SR
    x = (np.sin(2 * np.pi * f * tt)
         + 0.55 * np.sin(2 * np.pi * f * 2.0 * tt) * np.exp(-tt * 2.2)
         + 0.30 * np.sin(2 * np.pi * f * 2.997 * tt) * np.exp(-tt * 3.5)
         + 0.14 * np.sin(2 * np.pi * f * 4.01 * tt) * np.exp(-tt * 5.5)
         + 0.07 * np.sin(2 * np.pi * f * 5.42 * tt) * np.exp(-tt * 8))
    x *= np.exp(-tt * 1.15)
    k = min(int(0.004 * SR), n)
    x[:k] *= np.linspace(0, 1, k)
    x += 0.05 * (rng.standard_normal(n) - mvavg(rng.standard_normal(n), 4)) * np.exp(-tt * 80)
    return x * 0.42 * gain


def taiko(gain=1.0):
    n = int(0.5 * SR); tt = np.arange(n) / SR
    f = 56 + 95 * np.exp(-tt * 28)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 6.5)
    skin = (rng.standard_normal(n) - mvavg(rng.standard_normal(n), 10)) * np.exp(-tt * 55) * 0.45
    shell = 0.28 * np.sin(2 * np.pi * 175 * tt) * np.exp(-tt * 22)
    return (body + skin + shell) * 0.9 * gain


def timp(f, gain=1.0):
    n = int(0.65 * SR); tt = np.arange(n) / SR
    f_t = f * (1 + 0.45 * np.exp(-tt * 38))
    x = np.sin(2 * np.pi * np.cumsum(f_t) / SR) * np.exp(-tt * 4.5)
    x += 0.3 * np.sin(2 * np.pi * f * 1.5 * tt) * np.exp(-tt * 8)
    x += 0.35 * (rng.standard_normal(n) - mvavg(rng.standard_normal(n), 12)) * np.exp(-tt * 65)
    return x * gain


def brass(freqs, dur=0.9, gain=1.0):
    n = int(dur * SR); tt = np.arange(n) / SR
    x = np.zeros(n)
    for f in freqs:
        for det in (-0.004, 0.004):
            x += 2 * ((tt * NOTE[f] * (1 + det) / SR + rng.uniform(0, 1)) % 1.0) - 1
    x /= (len(freqs) * 2)
    dark = mvavg(x, 22)
    bright = mvavg(x, 4)
    swp = np.clip(tt / 0.07, 0, 1)
    x = dark * (1 - swp) + bright * swp
    a = np.clip(tt / 0.025, 0, 1) ** 1.4 * np.exp(-tt * 2.2)
    return x * a * gain


def crash(dur=1.5, gain=1.0):
    n = int(dur * SR)
    x = rng.standard_normal(n) - mvavg(rng.standard_normal(n), 4)
    x *= np.exp(-np.arange(n) / SR * 2.4)
    return x * 0.42 * gain


def tam(dur=3.2, gain=1.0):
    n = int(dur * SR); tt = np.arange(n) / SR
    x = (np.sin(2 * np.pi * 68 * tt) + 0.5 * np.sin(2 * np.pi * 104 * tt)
         + 0.3 * np.sin(2 * np.pi * 179 * tt) + 0.2 * np.sin(2 * np.pi * 241 * tt))
    x *= np.exp(-tt * 1.1)
    x += 0.18 * (rng.standard_normal(n) - mvavg(rng.standard_normal(n), 8)) * np.exp(-tt * 1.4)
    return x * gain


def sub(f, dur, gain=1.0):
    n = int(dur * SR); tt = np.arange(n) / SR
    x = np.sin(2 * np.pi * f * tt) * np.exp(-tt * 1.4)
    k = min(int(0.008 * SR), n)
    x[:k] *= np.linspace(0, 1, k)
    return x * gain


def marimba(f, gain=1.0):
    n = int(0.30 * SR); tt = np.arange(n) / SR
    x = np.sin(2 * np.pi * f * tt) * np.exp(-tt * 18)
    x += 0.35 * np.sin(2 * np.pi * f * 4.0 * tt) * np.exp(-tt * 42)
    x += 0.15 * np.sin(2 * np.pi * f * 9.2 * tt) * np.exp(-tt * 60)
    k = min(int(0.002 * SR), n)
    x[:k] *= np.linspace(0, 1, k)
    return x * 0.5 * gain


def harp_note(f, gain=1.0):
    n = int(1.1 * SR); tt = np.arange(n) / SR
    x = (np.sin(2 * np.pi * f * tt)
         + 0.4 * np.sin(2 * np.pi * f * 2.0 * tt) * np.exp(-tt * 6)
         + 0.15 * np.sin(2 * np.pi * f * 3.0 * tt) * np.exp(-tt * 10))
    x *= np.exp(-tt * 3.0)
    k = min(int(0.002 * SR), n)
    x[:k] *= np.linspace(0, 1, k)
    return x * 0.5 * gain


def harp_gliss(root, gain=1.0):
    deg = ['F4', 'Ab4', 'C5', 'F5', 'Ab5', 'C6']
    i0 = deg.index(root) if root in deg else 0
    seq = deg[i0:i0 + 4] if i0 <= 2 else deg[2:6]
    return [(harp_note(NOTE[f]), j * 0.055) for j, f in enumerate(seq)]


def cin_whoosh(dur=0.6, gain=1.0):
    n = int(dur * SR); tt = np.arange(n) / SR
    x = rng.standard_normal(n) - mvavg(rng.standard_normal(n), 12)
    x = mvavg(x, 5)
    env = (tt / dur) ** 2.3
    return x * env * 0.5 * gain


def riser_cin(dur=1.7, gain=1.0):
    n = int(dur * SR); tt = np.arange(n) / SR
    f0 = 174.61 * 2 ** ((tt / dur) * 0.58)
    x = np.sin(2 * np.pi * np.cumsum(f0) / SR) * 0.45
    x += np.sin(2 * np.pi * np.cumsum(f0 * 1.5) / SR) * 0.15
    x += (rng.standard_normal(n) - mvavg(rng.standard_normal(n), 14)) * ((tt / dur) ** 2.1) * 0.55
    a = np.clip(tt / 0.18, 0, 1) * np.clip((dur - tt) / 0.04, 0, 1)
    return np.tanh(x * a * 1.2) * 0.55 * gain


# ---------- arrangement ----------
# timeline constants (match render_trust.js)
HOOK = [1.0, 2.5, 4.0]
ITS = 5.65
TRUST_T = 6.15
EYEBROW = 7.05
LETTER_T = [9.30, 13.45, 17.60, 21.75, 25.90]
WORD_T = [t + 0.45 for t in LETTER_T]
PHRASE_T = [t + 1.05 for t in LETTER_T]
MONT = [30.05, 30.55, 31.05, 31.55, 32.05]
LOCK = 32.65
END_T = 34.2
PARTNER = 35.2
UNDERLINE = 36.2
FOOTER = 36.8
LOGO = 37.7

LETTER_CH = ['Fm', 'Ab', 'Cm', 'Eb', 'Fm']
LETTER_ROOT = ['F2', 'Ab2', 'C3', 'Eb3', 'F2']
LETTER_SUB = ['F1', 'Ab1', 'C2', 'Eb2', 'F1']

# ===== S1 0-5.15 hook: heartbeat + three hits =====
add(sub(NOTE['F1'], 1.0, 0.22), 0.25)
add(sub(NOTE['F1'], 0.7, 0.14), 0.75)
add(strings(CH['Fm'], 5.2, gain=0.10, attack=2.0, release=0.8), 0.0)
for i, t in enumerate(HOOK):
    g = [0.55, 0.65, 0.85][i]
    add(taiko(g), t)
    add(timp(NOTE['F2'], 0.55 if i < 2 else 0.7), t)
    add(stac(CH['Fm'], 0.30 + 0.08 * i), t)
    if i == 2:
        add(brass(CH['Fm'], 1.2, 0.20), t)
        add(crash(1.3, 0.40), t)
        add(sub(NOTE['F1'], 1.2, 0.30), t)
add(cin_whoosh(0.5, 0.4), 2.0)
add(riser_cin(1.1, 0.5), 3.0)

# ===== S2 5.15-8.8 turn =====
add(piano(NOTE['Ab4'], 1.6, 0.5), ITS)
add(taiko(0.5), TRUST_T)
add(timp(NOTE['F2'], 0.7), TRUST_T)
add(brass(CH['Fm'], 1.6, 0.24), TRUST_T)
add(strings(CH['Fm'], 2.6, gain=0.24, attack=0.12, release=0.8), TRUST_T)
add(crash(1.5, 0.42), TRUST_T)
add(sub(NOTE['F1'], 1.6, 0.32), TRUST_T)
for i in range(5):                      # TRUST letters rapid stac (typing feel)
    add(stac(CH['Fm'], 0.22), TRUST_T + i * 0.07, pan=-0.12 + i * 0.06)
add(marimba(NOTE['C6'], 0.5), EYEBROW)
# tension into letter 1
for t in np.arange(7.5, 9.3, BEAT):
    add(stac(CH['Fm'], 0.16), t)
add(taiko(0.5), 8.5)
add(riser_cin(1.0, 0.7), 8.3)

# ===== letter section 9.3-29.55: rising roots, growing layers =====
for li in range(5):
    st = LETTER_T[li]
    ch = CH[LETTER_CH[li]]
    root = NOTE[LETTER_ROOT[li]]
    last = li == 4
    # slam hit
    add(taiko(0.8 if not last else 0.95), st)
    add(timp(root, 0.7), st)
    add(strings(ch, 3.4 if not last else 3.9, gain=0.20 + 0.03 * li, attack=0.06, release=1.0), st)
    add(stac(ch, 0.30), st)
    if li >= 1:
        add(brass(ch, 1.2, 0.16 + 0.02 * li), st)
    if last:
        add(crash(1.4, 0.40), st)
        add(sub(NOTE['F1'], 1.4, 0.30), st)
    # word accent: piano
    add(piano(NOTE[['C5', 'C5', 'G4', 'Bb4', 'C5'][li]], 1.8, 0.5), WORD_T[li], pan=-0.08)
    # phrase accent: string swell
    add(strings([['F4', 'Ab4', 'C5', 'Eb5', 'F5'][li]], 1.6, gain=0.10, attack=0.25, release=0.6), PHRASE_T[li], pan=0.1)
    # riser into next letter
    if not last:
        add(riser_cin(0.9, 0.55), LETTER_T[li + 1] - 1.0)

# driving bed (density grows per letter index)
for t in np.arange(9.3, 29.5, BEAT):
    i_beat = int(round((t - 9.3) / BEAT))
    li = 0
    for k in range(5):
        if t >= LETTER_T[k]:
            li = k
    # taiko on 1 & 3 of each 2-beat
    if (t * 2) % 2 == 0:
        add(taiko(0.42 + 0.05 * li), t)
    # stac strings every beat from letter 2
    if li >= 1 and (t - LETTER_T[li]) >= 0:
        ch = CH[LETTER_CH[li]]
        add(stac(ch, 0.20 + 0.02 * li), t)
    # piano pulse 8ths from letter 3
    if li >= 2:
        add(piano(NOTE[['F3', 'Ab3', 'C4', 'Eb4', 'F4'][li]] / 2, 0.5, 0.16), t, pan=0.14)
# shaker 8ths growing
for t in np.arange(9.3, 29.5, 0.25):
    li = 0
    for k in range(5):
        if t >= LETTER_T[k]:
            li = k
    if li >= 1:
        g = 0.10 + 0.05 * li
        add((rng.standard_normal(int(0.04 * SR)) - mvavg(rng.standard_normal(int(0.04 * SR)), 5)) * env_exp(int(0.04 * SR), 120) * 0.35, t, pan=0.1 if (t * 4) % 2 else -0.1, gain=g)
# heartbeat sub through section
for t in np.arange(9.3, 29.5, 1.0):
    li = 0
    for k in range(5):
        if t >= LETTER_T[k]:
            li = k
    add(sub(NOTE[LETTER_SUB[li]], 0.9, 0.16 + 0.03 * li), t)
# roll into montage
for j, st in enumerate(np.arange(28.6, 29.55, S16)):
    add(timp(NOTE['F2'], 0.24 + 0.30 * (j / 6.0)), st, pan=(-0.18 if j % 2 else 0.18))
add(riser_cin(1.0, 0.8), 28.6)

# ===== montage 29.55-33.7: five letter hits =====
add(taiko(0.9), 29.55)
add(strings(CH['Fm'], 4.0, gain=0.20, attack=0.05, release=1.4), 29.55)
MONT_CH = [CH['Fm'], CH['Ab'], CH['Cm'], CH['Eb'], CH['Fm']]
for i, t in enumerate(MONT):
    last = i == 4
    add(stac(MONT_CH[i], 0.34), t)
    add(timp(NOTE[['F2', 'Ab2', 'C3', 'Eb3', 'F2'][i]], 0.55), t)
    add(taiko(0.6), t)
    if last:
        add(taiko(0.95), t)
        add(brass(MONT_CH[i], 1.4, 0.26), t)
        add(crash(1.3, 0.42), t)
        add(sub(NOTE['F1'], 1.5, 0.32), t)
# lock swell
add(strings(CH['Fm'], 1.1, gain=0.26, attack=0.10, release=0.3), LOCK)
add(brass(CH['Fm'], 1.0, 0.20), LOCK)
add(crash(1.0, 0.30), LOCK)
add(riser_cin(1.0, 0.85), 32.7)

# ===== sign-off 33.7-41.2: F major =====
add(taiko(0.5), 33.7)
add(strings(CH['Fm'], 0.5, gain=0.12, attack=0.05, release=0.2), 33.7)   # breath
# FULL F-major tutti at END_T
add(taiko(1.0), END_T)
add(tam(3.0, 0.5), END_T)
add(strings(CH['FM8'], 4.6, gain=0.32, attack=0.06, release=2.4), END_T)
add(brass(CH['FM'], 2.6, 0.26), END_T)
add(piano(NOTE['F4'], 3.2, 0.6), END_T)
add(piano(NOTE['C4'], 2.6, 0.4), END_T + 0.02)
add(sub(NOTE['F1'], 4.0, 0.42), END_T)
add(crash(2.2, 0.45), END_T)
add(timp(NOTE['F2'], 0.7), END_T)
# partner line
add(piano(NOTE['C5'], 2.2, 0.5), PARTNER, pan=-0.06)
add(strings(['C5'], 1.6, gain=0.10, attack=0.2), PARTNER, pan=-0.06)
# underline
add(cin_whoosh(0.6, 0.5), UNDERLINE)
# footer words
for sig, off in harp_gliss('F4'):
    add(sig, FOOTER + off, gain=0.13)
# logo
add(marimba(NOTE['C6'], 0.55), LOGO)
add(sub(NOTE['F1'], 1.2, 0.24), LOGO)
add(bell_ := (lambda f, dur=1.6: (np.sin(2 * np.pi * f * np.arange(int(dur * SR)) / SR)
                                  + 0.32 * np.sin(2 * np.pi * f * 2.01 * np.arange(int(dur * SR)) / SR))
                                  * np.exp(-np.arange(int(dur * SR)) / SR * 3.8))(NOTE['F4']), LOGO, gain=0.18)
# outro
add(piano(NOTE['F5'], 2.6, 0.35), 39.0)
add(sub(NOTE['F1'], 1.0, 0.14), 39.0)
add(strings(CH['FM'], 2.8, gain=0.14, attack=0.6, release=1.4), 38.6)

# ---------- mix ----------
duck = np.ones(N)
w = int(0.24 * SR)
for kt in [HOOK[1], HOOK[2], TRUST_T] + LETTER_T + MONT + [END_T]:
    i = int(kt * SR); n = min(w, N - i)
    if n > 0:
        duck[i:i + n] *= (1 - 0.34 * np.exp(-np.arange(n) / SR * 10))
L *= duck
R *= duck

segenv = np.ones(N)


def setg(a, b, g):
    segenv[int(a * SR):min(int(b * SR), N)] = g


setg(0, 5.15, 0.88)
setg(5.15, 9.3, 0.94)
setg(9.3, 13.45, 0.98)
setg(13.45, 17.6, 1.02)
setg(17.6, 21.75, 1.06)
setg(21.75, 25.9, 1.10)
setg(25.9, 33.7, 1.14)
setg(33.7, 41.2, 1.0)
segenv = mvavg(segenv, int(0.10 * SR))
L *= segenv
R *= segenv

# pre-slam dips
dip = np.ones(N)
for st in [TRUST_T] + LETTER_T + [END_T]:
    a, b = int((st - 0.09) * SR), int(st * SR)
    if b > a:
        dip[a:b] = np.minimum(dip[a:b], np.linspace(1.0, 0.55, b - a))
L *= dip
R *= dip

L = np.tanh(L * 1.05)
R = np.tanh(R * 1.05)

fade = np.ones(N)
fade[N - int(1.5 * SR):] = np.linspace(1, 0, int(1.5 * SR)) ** 0.85
fade[:int(0.25 * SR)] = np.linspace(0, 1, int(0.25 * SR))
L *= fade
R *= fade

TARGET_RMS = 0.205
rms0 = float(np.sqrt(np.mean((0.5 * (L + R)) ** 2)))
g = TARGET_RMS / max(rms0, 1e-6)
pk = max(np.abs(L).max(), np.abs(R).max())
if pk * g > 0.95:
    g = 0.95 / pk
L *= g
R *= g

out = '/workspace/ad_video/motion/music_trust.wav'
stereo = np.empty(N * 2, dtype=np.int16)
stereo[0::2] = np.clip(L * 32767, -32768, 32767).astype(np.int16)
stereo[1::2] = np.clip(R * 32767, -32768, 32767).astype(np.int16)
with wave.open(out, 'wb') as wf:
    wf.setnchannels(2)
    wf.setsampwidth(2)
    wf.setframerate(SR)
    wf.writeframes(stereo.tobytes())

print(f'wrote {out} peak={max(abs(L).max(), abs(R).max()):.3f} rms={float(np.sqrt(np.mean((0.5*(L+R))**2))):.3f}')