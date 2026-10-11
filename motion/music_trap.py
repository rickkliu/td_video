#!/usr/bin/env python3
"""Txn Banking 广告配乐 v6 —— 暗黑极简 Trap/Bass 版（120 BPM，F 小调，半拍感）
结构：每 2 秒一个 boom-boom-BAP cell；军鼓天然落在 6/8/10/.../20/22/24s，
与大字砸落时刻完全重合。808 贝斯带滑音，高潮前镲片 32 分滚奏。
纯器乐、无人声。用法: python3 music.py zh|en  ->  music_zh.wav / music_en.wav
（上一版 tech-house 备份于 music_house.py / music_house_*.wav）"""
import math
import sys
import wave

import numpy as np

LANG = (sys.argv[1] if len(sys.argv) > 1 else 'zh').lower()
SR = 44100
DUR = 31.5
N = int(DUR * SR)
BPM = 120
BEAT = 60 / BPM          # 0.5s
S16 = BEAT / 4           # 0.125s
S32 = BEAT / 8           # 0.0625s
rng = np.random.default_rng(21)

# F 小调音高表
NOTE = {
    'F1': 43.65, 'Ab1': 51.91, 'Bb1': 58.27, 'C2': 65.41, 'G2': 98.0, 'F2': 87.31,
    'F3': 174.61, 'Ab3': 207.65, 'Bb3': 233.08, 'C4': 261.63, 'Db4': 277.18,
    'Eb4': 311.13, 'F4': 349.23, 'G4': 392.0, 'Ab4': 415.30, 'Bb4': 466.16,
    'C5': 523.25, 'Eb5': 622.25,
}
PAD_CH = {                       # 各 4 秒区域的铺底和弦
    'F':  ['F3', 'Ab3', 'C4'],
    'Ab': ['Ab3', 'C4', 'Eb4'],
    'Bb': ['Bb3', 'Db4', 'F4'],
    'C':  ['C4', 'Eb4', 'G4'],
}
STAB_CH = {                      # 军鼓位置的和弦 stab
    'F':  ['F3', 'Ab3', 'C4'],
    'Ab': ['Ab3', 'C4', 'Eb4'],
    'Bb': ['Bb3', 'Db4', 'F4'],
    'C':  ['C4', 'Eb4', 'G4'],
}
SLAM_CH = [['F3', 'Ab3', 'C4'], ['Ab3', 'C4', 'F4'], ['C4', 'F4', 'Ab4']]   # 砸字三连和弦上行

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


# ---------- 合成器 ----------
def kick8(f0, tail=0.85, glide_from=None):
    """808 风格底鼓：硬音头 + 定音低频尾（可滑音）"""
    n = int((0.05 + tail) * SR)
    tt = np.arange(n) / SR
    m = min(n, int(0.055 * SR))
    ta = tt[:m]
    att = np.zeros(n)
    att[:m] = (1.8 * np.sin(2 * np.pi * (58 + 130 * np.exp(-ta * 90)) * ta) * np.exp(-ta * 42)
               + 0.45 * rng.standard_normal(m) * np.exp(-ta * 320))
    if glide_from is not None:
        freq = glide_from + (f0 - glide_from) * (1 - np.exp(-tt * 16))
    else:
        freq = np.full(n, f0)
    sub = np.sin(2 * np.pi * np.cumsum(freq) / SR) * np.exp(-np.maximum(tt - 0.02, 0) * 1.9)
    x = att + sub
    x[:int(0.004 * SR)] *= np.linspace(0, 1, int(0.004 * SR))
    return np.tanh(x * 1.3) * 0.93


def sub_pulse(f0, dur=0.5):
    n = int(dur * SR); tt = np.arange(n) / SR
    x = np.sin(2 * np.pi * f0 * tt) * np.exp(-tt * 2.2)
    return np.tanh(x * 1.2)


def snare():
    n = int(0.20 * SR); tt = np.arange(n) / SR
    x = (rng.standard_normal(n) - mvavg(rng.standard_normal(n), 20)) * env_exp(n, 24)
    x += 0.8 * np.sin(2 * np.pi * 190 * tt) * env_exp(n, 40)
    x += 0.4 * np.sin(2 * np.pi * 330 * tt) * env_exp(n, 55)
    return x * 0.95


def hat(open_=False):
    n = int((0.22 if open_ else 0.05) * SR)
    x = rng.standard_normal(n) - mvavg(rng.standard_normal(n), 8)
    return x * env_exp(n, 8 if open_ else 100)


def stab(freqs, dur=0.5):
    n = int(dur * SR); tt = np.arange(n) / SR
    x = np.zeros(n)
    for f in freqs:
        x += 2 * ((tt * NOTE[f] * 1.003) % 1.0) - 1 + 2 * ((tt * NOTE[f] * 0.997) % 1.0) - 1
    x = mvavg(x / (len(freqs) * 2), 10)
    return x * np.clip(tt / 0.003, 0, 1) * np.exp(-tt * 5.0)


def bell(f):
    """暗色铃铛主音色"""
    n = int(0.95 * SR); tt = np.arange(n) / SR
    x = (np.sin(2 * np.pi * f * tt)
         + 0.38 * np.sin(2 * np.pi * f * 2.01 * tt)
         + 0.14 * np.sin(2 * np.pi * f * 2.76 * tt))
    x *= np.exp(-tt * 4.6)
    x[:int(0.003 * SR)] *= np.linspace(0, 1, int(0.003 * SR))
    return np.tanh(x * 1.1) * 0.8


def pad(freqs, dur):
    n = int(dur * SR); tt = np.arange(n) / SR
    x = np.zeros(n)
    for f in freqs:
        x += np.sin(2 * np.pi * NOTE[f] * tt) + 0.35 * np.sin(2 * np.pi * NOTE[f] * 1.007 * tt)
    a = np.clip(tt / 0.5, 0, 1) * np.clip((dur - tt) / 0.6, 0, 1)
    return mvavg(x / len(freqs), 8) * a


def riser(dur):
    n = int(dur * SR); tt = np.arange(n) / SR
    x = rng.standard_normal(n) - mvavg(rng.standard_normal(n), 14)
    return mvavg(x, 3) * ((tt / dur) ** 2)


def impact(gain=1.0):
    n = int(1.4 * SR); tt = np.arange(n) / SR
    f = 150 * np.exp(-tt * 9) + 40
    sub = np.sin(2 * np.pi * np.cumsum(f) / SR) * env_exp(n, 3.0)
    air = mvavg(rng.standard_normal(n), 6) * env_exp(n, 3.6)
    return (sub + 0.3 * air) * gain


def subdrop():
    """砸字瞬间的下坠低频"""
    n = int(0.55 * SR); tt = np.arange(n) / SR
    f = 110 * np.exp(-tt * 7) + 36
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * env_exp(n, 5.5)
    x += 0.12 * (rng.standard_normal(n) - mvavg(rng.standard_normal(n), 10)) * env_exp(n, 40)
    return np.tanh(x * 1.6)


# ---------- 编排 ----------
# 每 2 秒一个 cell（5.0 起，共 10 个）：kick(t0) kick(t0+0.5) SNARE(t0+1.0) kick(t0+1.5)
# 军鼓时间 = 6,8,10,...,24 —— 20/22/24 正是砸字时刻
CELL_BASS = [                                        # (音A, 音B) 每区域 2 个 cell
    ('F1', 'F1'), ('F1', 'F2'),                      # 5-9   F
    ('Ab1', 'Ab1'), ('Ab1', 'F2'),                   # 9-13  Ab
    ('Bb1', 'Bb1'), ('Bb1', 'F2'),                   # 13-17 Bb
    ('C2', 'C2'), ('C2', 'G2'),                      # 17-21 C（属功能）
    ('F1', 'F1'), ('F1', 'F2'),                      # 21-25 F（解决）
]
REGIONS = ['F', 'F', 'Ab', 'Ab', 'Bb', 'Bb', 'C', 'C', 'F', 'F']   # 每 cell 的和声区域

kick_times = []
cell_starts = np.arange(5.0, 25.0, 2.0)
for k, t0 in enumerate(cell_starts):
    A, B = CELL_BASS[k]
    kick_times += [t0, t0 + 0.5, t0 + 1.5]

# 铺底（区域和弦，每 cell 一次）
for k, t0 in enumerate(cell_starts):
    add(pad(PAD_CH[REGIONS[k]], 2.1), t0, gain=0.13 if t0 >= 9.5 else 0.10)
add(pad(PAD_CH['F'], 5.0), 0.0, gain=0.09)                       # 开场
add(pad(PAD_CH['F'], 7.0), 24.5, gain=0.15)                      # 结尾

# 镲片：段落加密 + 高潮前 32 分滚奏
for t in np.arange(2.0, 5.0, 0.5):                                # 开场铺垫
    add(hat(False), t, pan=0.15, gain=0.055)
for t in np.arange(5.0, 14.0, 0.25):                              # 主歌 8 分
    add(hat(False), t, pan=0.16 if (t * 4) % 2 else -0.16, gain=0.105)
for t in np.arange(14.0, 24.5, S16):                              # 渐强-高潮 16 分
    g = 0.115 + (0.03 if t >= 19.0 else 0.015)
    if abs((t / 0.5) % 2 - 1) < 0.01:
        g += 0.02
    add(hat(False), t, pan=0.16 if (t * 8) % 2 else -0.16, gain=g)
for t in np.arange(5.5, 24.0, 1.0):                               # 反拍开镲
    add(hat(True), t, pan=0.10, gain=0.12 if t >= 19.0 else 0.09)
for st in [19.75, 21.75, 23.75]:                                  # 砸字前 32 分滚奏
    for i in range(8):
        add(hat(False), st + i * S32, pan=0.2 if i % 2 else -0.2, gain=0.07 + 0.022 * i)
for t in np.arange(25.0, 29.0, 0.5):                              # 尾奏稀疏
    add(hat(False), t, pan=0.12, gain=0.045)

# 军鼓（每 cell 的 BAP；20/22/24 即砸字）+ 主歌和弦 stab
slam_sounds = []          # 砸字层：最后叠加，保证砸字瞬间对比最大


def add_slam(sig, t0, pan=0.0, gain=1.0):
    slam_sounds.append((sig, t0, pan, gain))


for k, t0 in enumerate(cell_starts):
    ts = t0 + 1.0
    peak = ts >= 19.0
    if peak:
        add_slam(snare(), ts, gain=0.74)
    else:
        add(snare(), ts, gain=0.48)
        add(stab(STAB_CH[REGIONS[k]]), ts, pan=0.0, gain=0.15)
# 18.25-19.0 军鼓滚奏推高潮
for j, st in enumerate(np.arange(18.25, 19.0, S16)):
    add(snare(), st, pan=(-0.2 if j % 2 else 0.2), gain=0.12 + 0.32 * (j / 6.0))

# 砸字层：下坠低频 + 上行和弦 + 冲击底鼓（20/22/24，与画面大字同帧）
for j, st in enumerate([20.0, 22.0, 24.0]):
    add_slam(subdrop(), st, gain=0.70)
    add_slam(stab(SLAM_CH[j], 0.55), st, gain=0.38)
    add_slam(kick8(NOTE['F1'], tail=0.3), st, gain=0.95)


# 808 主线（cell 内 A A _ B）——放在侧链之后统一叠加
def place_kicks():
    for k, t0 in enumerate(cell_starts):
        A, B = CELL_BASS[k]
        peak = t0 >= 19.0
        g = 1.0 if peak else 0.92
        tail = 0.85
        if peak:
            tail = 0.55
            if (t0 + 0.5) in (19.5, 21.5, 23.5):
                tail = 0.22           # 砸字前一脚收短，给砸字让出对比
        add(kick8(NOTE[A], tail=tail), t0, gain=g)
        add(kick8(NOTE[A], tail=tail), t0 + 0.5, gain=0.97 * g)
        add(kick8(NOTE[B], tail=tail, glide_from=NOTE[A] if B != A else None), t0 + 1.5, gain=0.95 * g)


# 铃铛主音色：开场琶音 -> 主歌点缀 -> 高潮 hook -> 尾奏回声
for t, f, g in [(1.0, 'F4', 0.14), (1.5, 'Ab4', 0.14), (2.0, 'C5', 0.15),
                (3.0, 'Eb5', 0.15), (3.5, 'C5', 0.14), (4.0, 'Ab4', 0.13)]:
    add(bell(NOTE[f]), t, pan=-0.1, gain=g)
for k, t0 in enumerate(cell_starts):                              # 主歌点缀
    if t0 >= 19.0:
        break
    f = 'F4' if k % 2 == 0 else 'Ab4'
    add(bell(NOTE[f]), t0 + 0.75, pan=0.12, gain=0.10)
PEAK_MELODY = ['F4', 'Ab4', 'C5', 'Bb4', 'Ab4', 'F4', 'G4', 'Ab4', 'Bb4', 'C5', 'Eb5']
for i, f in enumerate(PEAK_MELODY):                               # 高潮 hook（19.0-24.0 每拍）
    add(bell(NOTE[f]), 19.0 + i * 0.5, pan=(-0.18 if i % 2 else 0.18), gain=0.22)
for t, f, g in [(25.05, 'Ab4', 0.17), (25.5, 'F4', 0.17), (26.5, 'C5', 0.14),
                (27.5, 'Ab4', 0.12), (29.0, 'F4', 0.11)]:         # 尾奏回声（对齐团队名揭示）
    add(bell(NOTE[f]), t, pan=0.0, gain=g)

# 渐强段 16 分琶音（14-19）
arp = ['F3', 'Ab3', 'C4', 'Eb4']
for i, t in enumerate(np.arange(14.0, 19.0, S16)):
    add(bell(NOTE[arp[i % 4]]), t, pan=(-0.22 if i % 2 else 0.22), gain=0.075 + 0.02 * ((t - 14) / 5))

# 开场低频脉冲 + riser/冲击
for t in [1.0, 2.0, 3.0, 4.0]:
    add(sub_pulse(NOTE['F1']), t, gain=0.30)
add(riser(1.6), 3.4, gain=0.20)
add(riser(1.7), 17.3, gain=0.34)
for it, g in [(5.0, 0.5), (9.5, 0.55), (14.0, 0.5), (19.0, 0.85), (24.5, 0.8)]:
    add(impact(g), it)

# ---------- 混音 ----------
# 侧链：跟底鼓轻压（让 808 主导低频）
duck = np.ones(N)
w = int(0.16 * SR)
for kt in kick_times:
    i = int(kt * SR); n = min(w, N - i)
    if n > 0:
        duck[i:i + n] *= (1 - 0.42 * np.exp(-np.arange(n) / SR * 15))

L *= duck
R *= duck

segenv = np.ones(N)


def setg(a, b, g):
    segenv[int(a * SR):min(int(b * SR), N)] = g


setg(0, 5.0, 0.84)
setg(5.0, 9.5, 0.96)
setg(9.5, 14.0, 1.0)
setg(14.0, 19.0, 1.05)
setg(19.0, 24.5, 1.12)
setg(24.5, 31.5, 0.90)
segenv = mvavg(segenv, int(0.08 * SR))
L *= segenv
R *= segenv

place_kicks()                                    # 808 不受侧链影响，最后叠加

# 砸字前 90ms 快速压低（经典 trap pre-drop dip），砸字层随后全量砸入
dip = np.ones(N)
for st in [20.0, 22.0, 24.0]:
    a, b = int((st - 0.09) * SR), int(st * SR)
    if b > a:
        dip[a:b] = np.minimum(dip[a:b], np.linspace(1.0, 0.42, b - a))
L *= dip
R *= dip
for sig, t0, pan, gn in slam_sounds:
    add(sig, t0, pan=pan, gain=gn)

L = np.tanh(L * 1.12)
R = np.tanh(R * 1.12)

n_fade = int(1.3 * SR)
fade = np.ones(N)
fade[N - n_fade:] = np.linspace(1, 0, n_fade) ** 0.8
fade[:int(0.25 * SR)] = np.linspace(0, 1, int(0.25 * SR))
L *= fade
R *= fade

TARGET_RMS = 0.20
rms0 = float(np.sqrt(np.mean((0.5 * (L + R)) ** 2)))
g = TARGET_RMS / max(rms0, 1e-6)
pk = max(np.abs(L).max(), np.abs(R).max())
if pk * g > 0.97:
    g = 0.97 / pk
L *= g
R *= g

out = f'/workspace/ad_video/motion/music_{LANG}.wav'
stereo = np.empty(N * 2, dtype=np.int16)
stereo[0::2] = np.clip(L * 32767, -32768, 32767).astype(np.int16)
stereo[1::2] = np.clip(R * 32767, -32768, 32767).astype(np.int16)
with wave.open(out, 'wb') as wf:
    wf.setnchannels(2)
    wf.setsampwidth(2)
    wf.setframerate(SR)
    wf.writeframes(stereo.tobytes())

print(f'wrote {out}  lang={LANG} peak={max(abs(L).max(), abs(R).max()):.3f} rms={float(np.sqrt(np.mean((0.5*(L+R))**2))):.3f}')