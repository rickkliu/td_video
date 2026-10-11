#!/usr/bin/env python3
"""Txn Banking 广告配乐 v8 —— Minimal Deep House（克制 · 优雅 · 律动）
思路：保留 v7 的"事件同步音效"骨架（观众仍能感到画面在发声），
但把力度全面收敛——去掉军鼓/重击/下潜轰炸，换成：
  圆润深底鼓（少量）+ 深圆贝斯 + 温暖电钢和弦 + 轻柔 tick/whoosh/铃音。
砸字点改为"柔和重音"（深鼓 + 柔和和弦 pluck），同步但不轰炸。
适合现代科技公司（Stripe/Linear 风）的克制质感。纯器乐。
用法: python3 music.py zh|en  ->  music_zh.wav / music_en.wav
（历史: music_house.py tech-house / music_trap.py 808 / music_cinematic.py 事件轰炸版）"""
import math
import sys
import wave

import numpy as np

LANG = (sys.argv[1] if len(sys.argv) > 1 else 'zh').lower()
SR = 44100
DUR = 31.5
N = int(DUR * SR)
BPM = 120
BEAT = 60.0 / BPM                 # 0.5085
S8 = BEAT / 2
S16 = BEAT / 4
rng = np.random.default_rng(88)

NOTE = {
    'F1': 43.65, 'Ab1': 51.91, 'C2': 65.41, 'Db2': 69.30, 'Eb2': 77.78,
    'F2': 87.31, 'Ab2': 103.83, 'Bb2': 116.54, 'C3': 130.81, 'Db3': 138.59,
    'Eb3': 155.56, 'G3': 196.0, 'F3': 174.61, 'Ab3': 207.65, 'Bb3': 233.08,
    'C4': 261.63, 'Db4': 277.18, 'Eb4': 311.13, 'F4': 349.23, 'G4': 392.0,
    'Ab4': 415.30, 'Bb4': 466.16, 'C5': 523.25, 'Db5': 554.37, 'Eb5': 622.25,
    'F5': 698.46, 'Ab5': 830.61, 'C6': 1046.5,
}
CH = {
    'Fm':  ['F3', 'Ab3', 'C4'],
    'Db':  ['Db4', 'F4', 'Ab4'],
    'Ab':  ['Ab3', 'C4', 'Eb4'],
    'Eb':  ['Eb4', 'G4', 'Bb4'],
    'Bbm': ['Bb3', 'Db4', 'F4'],
    'Csus': ['C4', 'F4', 'G4'],
}
# 和声区域：Fm -> Db -> Ab -> Eb -> Fm（8 拍一块，跟随场景）
REGIONS = [('Fm', 5.0), ('Db', 9.5), ('Ab', 14.0), ('Eb', 19.0), ('Fm', 24.5)]

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


def region_chord(t):
    ch = 'Fm'
    for name, ts in REGIONS:
        if t >= ts:
            ch = name
    return ch


# ================= 温和音色 =================
def kick_soft():
    """圆润深底鼓：无click，正弦下坠，柔和音头"""
    n = int(0.34 * SR); tt = np.arange(n) / SR
    f = 42 + 62 * np.exp(-tt * 20)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * env_exp(n, 7.0)
    head = np.sin(2 * np.pi * 180 * tt) * env_exp(n, 90) * 0.12
    return (body + head) * 0.85


def kick_ghost():
    """更轻的底鼓（ghost）"""
    return kick_soft() * 0.45


def rim():
    """rimshot 质感的轻击（代替军鼓/拍手）"""
    n = int(0.09 * SR); tt = np.arange(n) / SR
    x = (rng.standard_normal(n) - mvavg(rng.standard_normal(n), 12)) * env_exp(n, 70)
    x += 0.5 * np.sin(2 * np.pi * 620 * tt) * env_exp(n, 90)
    return x * 0.4


def hat(open_=False):
    n = int((0.16 if open_ else 0.045) * SR)
    x = rng.standard_normal(n) - mvavg(rng.standard_normal(n), 8)
    return x * env_exp(n, 9 if open_ else 110) * 0.5


def shaker():
    """沙锤（16分，很轻）"""
    n = int(0.04 * SR)
    x = rng.standard_normal(n) - mvavg(rng.standard_normal(n), 5)
    return x * env_exp(n, 120) * 0.35


def bass_round(fr, dur=0.42):
    """深圆贝斯：低通正弦+微量二次谐波，慢包络"""
    n = int(dur * SR); tt = np.arange(n) / SR
    x = np.sin(2 * np.pi * fr * tt) + 0.16 * np.sin(2 * np.pi * 2 * fr * tt)
    a = np.clip(tt / 0.012, 0, 1) * np.exp(-tt * 3.4)
    return np.tanh(x * 1.1) * a * 0.85


def epiano(freqs, dur=1.2, bright=1.0):
    """温暖电钢和弦（Rhodes 风）"""
    n = int(dur * SR); tt = np.arange(n) / SR
    x = np.zeros(n)
    for f in freqs:
        base = NOTE[f]
        x += (np.sin(2 * np.pi * base * tt)
              + 0.4 * np.sin(2 * np.pi * base * 2 * tt) * np.exp(-tt * 3)
              + 0.18 * np.sin(2 * np.pi * base * 3.01 * tt) * np.exp(-tt * 5) * bright)
    a = np.clip(tt / 0.015, 0, 1) * np.exp(-tt * 1.7)
    return mvavg(x / len(freqs), 3) * a * 0.8


def pluck(fr, dur=0.5):
    """柔和拨弦 pluck（砸字重音/点缀）"""
    n = int(dur * SR); tt = np.arange(n) / SR
    x = (np.sin(2 * np.pi * fr * tt)
         + 0.5 * np.sin(2 * np.pi * fr * 2 * tt) * np.exp(-tt * 8)
         + 0.2 * np.sin(2 * np.pi * fr * 3.02 * tt) * np.exp(-tt * 12))
    x *= np.clip(tt / 0.004, 0, 1) * np.exp(-tt * 4.5)
    return x * 0.8


def bell(f, dur=1.0, gain=1.0):
    n = int(dur * SR); tt = np.arange(n) / SR
    x = (np.sin(2 * np.pi * f * tt) + 0.32 * np.sin(2 * np.pi * f * 2.01 * tt)
         + 0.10 * np.sin(2 * np.pi * f * 2.76 * tt))
    x *= np.exp(-tt * 3.8)
    x[:int(0.004 * SR)] *= np.linspace(0, 1, int(0.004 * SR))
    return x * 0.7 * gain


def pad(freqs, dur, gain=1.0):
    n = int(dur * SR); tt = np.arange(n) / SR
    x = np.zeros(n)
    for f in freqs:
        x += np.sin(2 * np.pi * NOTE[f] * tt) + 0.3 * np.sin(2 * np.pi * NOTE[f] * 1.006 * tt)
    a = np.clip(tt / 0.8, 0, 1) * np.clip((dur - tt) / 1.0, 0, 1)
    return mvavg(x / len(freqs), 10) * a * gain


def subnote(f, dur, gain=1.0):
    n = int(dur * SR); tt = np.arange(n) / SR
    x = np.sin(2 * np.pi * f * tt) * np.exp(-tt * 1.3)
    x[:int(0.008 * SR)] *= np.linspace(0, 1, int(0.008 * SR))
    return x * gain


def tick(pitch=1.0, gain=1.0):
    """轻柔滴答（逐字/计数）——v7 同款但减半力度"""
    n = int(0.026 * SR); tt = np.arange(n) / SR
    x = np.sin(2 * np.pi * 2100 * pitch * tt) * env_exp(n, 300)
    x += (rng.standard_normal(n) - mvavg(rng.standard_normal(n), 5)) * env_exp(n, 500) * 0.3
    return x * 0.30 * gain


def whoosh(dur=0.6, gain=1.0):
    """柔和噪声滑（转场）——去高频嘶叫，暖化"""
    n = int(dur * SR); tt = np.arange(n) / SR
    x = rng.standard_normal(n) - mvavg(rng.standard_normal(n), 12)
    x = mvavg(x, 6)
    env = (tt / dur) ** 2.4
    return x * env * 0.45 * gain


def riser(dur, gain=1.0):
    n = int(dur * SR); tt = np.arange(n) / SR
    x = rng.standard_normal(n) - mvavg(rng.standard_normal(n), 16)
    return mvavg(x, 4) * ((tt / dur) ** 2) * 0.35 * gain


def thud(gain=1.0):
    """柔和深击（代替 impact）：低正弦衰减，无空气爆"""
    n = int(0.8 * SR); tt = np.arange(n) / SR
    f = 95 * np.exp(-tt * 12) + 38
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * env_exp(n, 4.5)
    return x * 0.55 * gain


def sweep_up(dur=1.5, gain=1.0):
    """折线跟随上扬（更轻）"""
    n = int(dur * SR); tt = np.arange(n) / SR
    f = 320 + 700 * (tt / dur) ** 1.7
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.4
    a = np.clip(tt / 0.2, 0, 1) * np.clip((dur - tt) / 0.15, 0, 1)
    return x * a * 0.32 * gain


def shimmer(root='F4', gain=1.0):
    deg = ['F4', 'Ab4', 'C5', 'F5', 'Ab5', 'C6']
    i0 = deg.index(root) if root in deg else 0
    return [(bell(NOTE[f], 0.6, 1.0), j * 0.05) for j, f in enumerate(deg[i0:i0 + 3])] if i0 < 3 else [(bell(NOTE[deg[3]], 0.6), 0)]


# ================= 编排 =================
# 事件时刻表（与 render.js 严格对齐）
SCENE_T = [0.0, 5.0, 9.5, 14.0, 19.0, 24.5]
SLAMS = [20.0, 22.0, 24.0]
CARDS = [10.65, 10.95, 11.25]
NUMS = [5.85, 6.35, 6.85]
SLAM_PLUCKS = [['F3', 'Ab3', 'C4'], ['Db4', 'F4', 'Ab4'], ['C4', 'F4', 'G4']]

beat_grid = np.arange(SCENE_T[1], 24.5, BEAT)          # 5.0-24.5 每拍
kick_placements = []                                    # 侧链后叠加

# ---------- S1 0-5.5 數位浪潮 ----------
add(pad(CH['Fm'], 5.6), 0.0, gain=0.12)
add(subnote(NOTE['F1'], 5.0), 0.1, gain=0.26)
for i in range(6):                                       # 标题逐字轻tick
    add(tick(1.0 + i * 0.05, 0.7), 0.25 + i * 0.055, pan=-0.1 + i * 0.04, gain=0.55)
add(whoosh(0.5), 0.75, gain=0.6)
for i, (bf, bl) in enumerate([('F2', 'F4'), ('Ab2', 'Ab4'), ('C3', 'C5')]):  # 三关键词
    t = 2.30 + i * 0.28
    add(subnote(NOTE[bf], 1.2), t, gain=0.20)
    add(bell(NOTE[bl], 1.0), t, pan=-0.12 + i * 0.12, gain=0.13)
add(riser(1.6), 3.4, gain=0.55)
add(pluck(NOTE['C5'], 0.6), 4.9, gain=0.16)              # 进节拍前一记轻拨弦

# ---------- 转场 whoosh（柔） ----------
for ts in SCENE_T[1:]:
    add(whoosh(0.6), ts - 0.55, gain=0.5)

# ---------- 节拍层 5.0-24.5：deep house 四踩（柔） ----------
for i, t in enumerate(beat_grid):
    if t in SLAMS:
        continue                                           # 砸字拍由砸字层独占
    g = 0.80 if t < 9.5 else 0.88
    kick_placements.append((t, g))
# ghost 底鼓在反拍/切分点缀（deep house shuffle 感）
for t in np.arange(SCENE_T[1] + 1.5, 24.0, 2.0):
    kick_placements.append((t, 0.30))
# 2/4 拍轻 rim（代替军鼓拍手）
for ct in np.arange(SCENE_T[1] + 1.0, 24.0, 2.0):
    if ct in SLAMS:
        continue
    add(rim(), ct, gain=0.55)
    add(hat(True), ct - S8, pan=0.1, gain=0.30)          # rim 前反拍开镲
# 8 分踩镲（轻）+ 14 后加沙锤 16 分
for t in np.arange(SCENE_T[1], 24.5, S8):
    add(hat(False), t, pan=0.14 if (t / S8) % 2 else -0.14, gain=0.20)
for t in np.arange(14.0, 24.5, S16):
    if (t / S16) % 2 == 1:
        add(shaker(), t, pan=-0.1, gain=0.5)
# 深圆贝斯：每拍正拍，跟区域根音（砸字拍让位给砸字 sub）
for t in np.arange(SCENE_T[1], 24.5, BEAT):
    if t in SLAMS:
        continue
    root = {'Fm': 'F2', 'Db': 'Db2', 'Ab': 'Ab2', 'Eb': 'Eb2'}[region_chord(t)]
    add(bass_round(NOTE[root]), t, gain=0.42)
# 电钢和弦 stab：每 2 拍一次反拍（砸字拍让位给砸字和弦）
for t in np.arange(SCENE_T[1] + 1.0, 24.4, 2.0):
    if t in SLAMS:
        continue
    ch = region_chord(t)
    add(epiano(CH[ch], 1.0), t, pan=-0.08, gain=0.26)
# 铺底
for name, ts in REGIONS:
    add(pad(CH[name], 4.6), ts, gain=0.12)

# ---------- S2 数字滚动：轻 thud + 滴答 ----------
for i, st in enumerate(NUMS):
    add(thud(0.8), st)
    add(bell(NOTE[['F4', 'Ab4', 'C5'][i]], 0.8), st, pan=-0.12 + i * 0.12, gain=0.13)
    for j in range(12):
        p = j / 11
        add(tick(0.95 + p * 0.7, 0.6), st + 0.06 + p * 0.9, pan=0.08, gain=0.4 + p * 0.2)

# ---------- S3 卡片：whoosh + 轻thud + shimmer ----------
for i, root in enumerate(['F4', 'Ab4', 'C5']):
    st = CARDS[i]
    add(whoosh(0.45), st - 0.42, pan=-0.15 + i * 0.15, gain=0.5)
    add(thud(0.95), st)
    kick_placements.append((st, 0.5))
    for sig, off in shimmer(root):
        add(sig, st + 0.02 + off, pan=0.15 - i * 0.15, gain=0.13)

# ---------- S4 chip + 折线 ----------
for i in range(3):
    add(tick(1.1 + i * 0.1, 0.8), 14.9 + i * 0.2, pan=-0.06 + i * 0.06, gain=0.7)
add(sweep_up(1.5), 15.3, gain=0.85)
for i, t in enumerate([15.45, 15.73, 16.02, 16.30]):
    add(tick(1.2 + i * 0.14, 0.8), t, pan=0.06, gain=0.6)
add(bell(NOTE['F5'], 0.9), 16.72, pan=0.05, gain=0.20)   # 终点 ding（轻）
add(whoosh(0.5), 16.15, gain=0.45)
# 17.5-19 一小段柔和琶音（准备进高潮）
arp = ['F4', 'Ab4', 'C5', 'Eb5']
for i, t in enumerate(np.arange(17.0, 19.0, S16)):
    add(pluck(NOTE[arp[i % 4]], 0.3), t, pan=(-0.18 if i % 2 else 0.18), gain=0.09 + 0.03 * ((t - 17) / 2))
add(riser(1.8), 17.4, gain=0.7)

# ---------- S5 承諾：柔和高潮 + 砸字"柔和重音" ----------
add(thud(1.0), 19.0)
# 柔和 pluck hook（一条简单旋律线，克制）
HOOK = [(19.0, 'C5'), (19.5, 'Ab4'), (20.0, 'F4'), (21.0, 'C5'), (21.5, 'Eb5'),
        (22.0, 'Db5'), (23.0, 'C5'), (23.5, 'Ab4'), (24.0, 'F4')]
for t, f in HOOK:
    add(pluck(NOTE[f], 0.55), t, pan=-0.1 if int(t * 2) % 2 else 0.1, gain=0.17)
# 高潮段电钢密度提高
for t in np.arange(19.0, 24.5, 1.0):
    add(epiano(CH[region_chord(t)], 0.9), t + 0.5, pan=0.1, gain=0.30)
# 砸字：深鼓 + 柔和和弦 pluck + 轻 sub（无军鼓无下潜）
for j, st in enumerate(SLAMS):
    kick_placements.append((st, 1.05))                   # 略重的深鼓
    add(pluck(NOTE[SLAM_PLUCKS[j][2]], 0.6), st, pan=-0.06, gain=0.30)
    add(epiano(SLAM_PLUCKS[j], 1.1), st, gain=0.22)
    add(subnote(NOTE['F1'], 0.8), st, gain=0.24)
    add(whoosh(0.4), st + 0.05, gain=0.35)               # 红线扫入（柔）
# 砸字前的 kicker（讓複雜變得…）轻 tick
for i, t in enumerate([19.5, 21.5, 23.5]):
    add(tick(1.25 + i * 0.08, 0.7), t, gain=0.5)

# ---------- S6 落版 ----------
add(thud(1.0), 24.5)
add(subnote(NOTE['F2'], 1.4), 25.05, gain=0.28)          # TEAM1
add(bell(NOTE['F4'], 1.1), 25.05, pan=-0.1, gain=0.13)
add(subnote(NOTE['Ab2'], 1.4), 25.45, gain=0.28)         # TEAM2
add(bell(NOTE['Ab4'], 1.1), 25.45, pan=0.1, gain=0.13)
add(whoosh(0.6), 26.2, gain=0.5)                          # 红线
for sig, off in shimmer('C5'):
    add(sig, 26.6 + off, gain=0.12)                       # tagline
add(thud(1.0), 27.0)                                      # logo 终章（柔）
add(subnote(NOTE['F1'], 2.8), 27.0, gain=0.36)
add(bell(NOTE['F4'], 1.8), 27.0, gain=0.16)
for sig, off in shimmer('F4'):
    add(sig, 27.05 + off, gain=0.10)
add(epiano(CH['Fm'], 3.5), 26.5, gain=0.20)               # 尾奏电钢长音
for t in [29.0, 30.0]:                                    # 尾声两记轻鼓
    kick_placements.append((t, 0.5))
add(pad(CH['Csus'], 4.5), 27.2, gain=0.10)

# ================= 混音 =================
# 侧链（浅）：跟每拍深鼓
duck = np.ones(N)
w = int(0.22 * SR)
all_kt = [t for t, _ in kick_placements]
for kt in all_kt:
    i = int(kt * SR); n = min(w, N - i)
    if n > 0:
        duck[i:i + n] *= (1 - 0.42 * np.exp(-np.arange(n) / SR * 11))
L *= duck
R *= duck
# 深鼓最后叠加
for t, gn in kick_placements:
    add(kick_soft(), t, gain=gn)

# 分段能量（整体平滑，高潮略抬）
segenv = np.ones(N)


def setg(a, b, g):
    segenv[int(a * SR):min(int(b * SR), N)] = g


setg(0, 5.0, 0.84)
setg(5.0, 9.5, 0.95)
setg(9.5, 14.0, 1.0)
setg(14.0, 19.0, 1.05)
setg(19.0, 24.5, 1.10)
setg(24.5, 31.5, 0.9)
segenv = mvavg(segenv, int(0.12 * SR))
L *= segenv
R *= segenv

# 轻饱和 + 淡入淡出
L = np.tanh(L * 0.95)
R = np.tanh(R * 0.95)
fade = np.ones(N)
fade[N - int(1.8 * SR):] = np.linspace(1, 0, int(1.8 * SR)) ** 0.7
fade[:int(0.3 * SR)] = np.linspace(0, 1, int(0.3 * SR))
L *= fade
R *= fade

# 目标响度更低（0.165，比 v7 低 ~1.6dB，整体克制）
TARGET_RMS = 0.165
rms0 = float(np.sqrt(np.mean((0.5 * (L + R)) ** 2)))
g = TARGET_RMS / max(rms0, 1e-6)
pk = max(np.abs(L).max(), np.abs(R).max())
if pk * g > 0.94:
    g = 0.94 / pk
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