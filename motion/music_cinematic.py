#!/usr/bin/env python3
"""Txn Banking 广告配乐 v7 —— 事件驱动混合配乐（cinematic hybrid + 驱动节拍）
核心理念：不是"背景音乐"，而是每一个画面动作都有同帧音效——
  文字逐字出现 -> tick ；数字滚动计数 -> 急促滴答；卡片落位 -> whoosh+impact+shimmer；
  折线绘制 -> 上扬扫频+节点tick+终点ding；转场 -> whoosh；砸字 -> 反镲+深潜+和弦。
加上 5-24.5s 的四踩驱动节拍与深侧链。纯器乐。
用法: python3 music.py zh|en  ->  music_zh.wav / music_en.wav
（历史版本: music_house.py / music_trap.py）"""
import math
import sys
import wave

import numpy as np

LANG = (sys.argv[1] if len(sys.argv) > 1 else 'zh').lower()
SR = 44100
DUR = 31.5
N = int(DUR * SR)
BPM = 120
BEAT = 0.5
S16 = 0.125
S32 = 0.0625
rng = np.random.default_rng(31)

NOTE = {
    'F1': 43.65, 'Ab1': 51.91, 'C2': 65.41, 'Db2': 69.30, 'Eb2': 77.78,
    'F2': 87.31, 'Ab2': 103.83, 'Bb2': 116.54, 'C3': 130.81, 'Db3': 138.59,
    'Eb3': 155.56, 'G3': 196.0, 'F3': 174.61, 'Ab3': 207.65, 'Bb3': 233.08,
    'C4': 261.63, 'Db4': 277.18, 'Eb4': 311.13, 'F4': 349.23, 'G4': 392.0,
    'Ab4': 415.30, 'Bb4': 466.16, 'C5': 523.25, 'Db5': 554.37, 'Eb5': 622.25,
    'F5': 698.46,
}
CH = {
    'Fm': ['F3', 'Ab3', 'C4'],
    'Db': ['Db4', 'F4', 'Ab4'],
    'Ab': ['Ab3', 'C4', 'Eb4'],
    'Eb': ['Eb4', 'G4', 'Bb4'],
}
# 每 4 秒和声区域（5.0 起）：Fm Db Ab Eb Fm —— 经典小调史诗进行
REGIONS = [('Fm', 5.0), ('Db', 9.0), ('Ab', 13.0), ('Eb', 17.0), ('Fm', 21.0)]
SLAM_CH = [['F3', 'Ab3', 'C4'], ['Db4', 'F4', 'Ab4'], ['Ab3', 'C4', 'Eb4']]   # 20/22/24 砸字和弦

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


# ================= 合成器 =================
def kick():
    n = int(0.42 * SR); tt = np.arange(n) / SR
    f = 44 + 150 * np.exp(-tt * 26)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * env_exp(n, 6.0)
    click = rng.standard_normal(n) * 0.20 * env_exp(n, 240)
    sub = np.sin(2 * np.pi * 56 * tt) * env_exp(n, 26) * 0.5
    return np.tanh((body + click + sub) * 2.0) * 0.9


def snare():
    n = int(0.20 * SR); tt = np.arange(n) / SR
    x = (rng.standard_normal(n) - mvavg(rng.standard_normal(n), 20)) * env_exp(n, 24)
    x += 0.8 * np.sin(2 * np.pi * 190 * tt) * env_exp(n, 40)
    x += 0.4 * np.sin(2 * np.pi * 330 * tt) * env_exp(n, 55)
    return x * 0.95


def clap():
    n = int(0.22 * SR); tt = np.arange(n) / SR
    x = rng.standard_normal(n) - mvavg(rng.standard_normal(n), 24)
    burst = np.exp(-tt * 48) + 0.6 * np.exp(-((tt - 0.010) ** 2) / 1.6e-5) + 0.45 * np.exp(-((tt - 0.021) ** 2) / 1.6e-5)
    return x * burst * env_exp(n, 14)


def hat(open_=False):
    n = int((0.22 if open_ else 0.05) * SR)
    x = rng.standard_normal(n) - mvavg(rng.standard_normal(n), 8)
    return x * env_exp(n, 8 if open_ else 100)


def bass(fr, dur=0.24):
    n = int(dur * SR); tt = np.arange(n) / SR
    saw = mvavg(2 * ((tt * fr) % 1.0) - 1, 6)
    x = 0.55 * saw + 0.95 * np.sin(2 * np.pi * fr * tt)
    return np.tanh(x * 1.4) * np.clip(tt / 0.004, 0, 1) * env_exp(n, 9)


def stab(freqs, dur=0.5):
    n = int(dur * SR); tt = np.arange(n) / SR
    x = np.zeros(n)
    for f in freqs:
        x += 2 * ((tt * NOTE[f] * 1.003) % 1.0) - 1 + 2 * ((tt * NOTE[f] * 0.997) % 1.0) - 1
    x = mvavg(x / (len(freqs) * 2), 10)
    return x * np.clip(tt / 0.003, 0, 1) * np.exp(-tt * 5.0)


def lead(fr, dur=0.45):
    """暗色锯齿 lead（高潮 hook）"""
    n = int(dur * SR); tt = np.arange(n) / SR
    x = (2 * ((tt * fr * 1.004) % 1.0) - 1) * 0.5 + (2 * ((tt * fr * 0.996) % 1.0) - 1) * 0.5
    x = mvavg(x, 4) + 0.3 * np.sin(2 * np.pi * fr * tt)
    return np.tanh(x * 1.3) * np.clip(tt / 0.004, 0, 1) * np.exp(-tt * 3.5)


def bell(f, dur=0.9):
    n = int(dur * SR); tt = np.arange(n) / SR
    x = (np.sin(2 * np.pi * f * tt) + 0.38 * np.sin(2 * np.pi * f * 2.01 * tt)
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


def subnote(f, dur):
    n = int(dur * SR); tt = np.arange(n) / SR
    x = np.sin(2 * np.pi * f * tt) * np.exp(-tt * 1.6)
    x[:int(0.006 * SR)] *= np.linspace(0, 1, int(0.006 * SR))
    return np.tanh(x * 1.2)


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
    n = int(0.55 * SR); tt = np.arange(n) / SR
    f = 110 * np.exp(-tt * 7) + 36
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * env_exp(n, 5.5)
    x += 0.12 * (rng.standard_normal(n) - mvavg(rng.standard_normal(n), 10)) * env_exp(n, 40)
    return np.tanh(x * 1.6)


# ---------- 事件音效（这版的灵魂） ----------
def tick(pitch=1.0, gain=1.0):
    """极短滴答——文字逐字/数字滚动"""
    n = int(0.030 * SR); tt = np.arange(n) / SR
    x = np.sin(2 * np.pi * 2300 * pitch * tt) * env_exp(n, 260)
    x += (rng.standard_normal(n) - mvavg(rng.standard_normal(n), 4)) * env_exp(n, 420) * 0.5
    return x * 0.5 * gain


def whoosh(dur=0.55, up=True, gain=1.0):
    """扫频——转场/元素飞入（up: 结尾最响，应让结尾对齐事件时刻）"""
    n = int(dur * SR); tt = np.arange(n) / SR
    x = rng.standard_normal(n) - mvavg(rng.standard_normal(n), 10)
    x = mvavg(x, 3)
    env = ((tt / dur) ** 2.2) if up else ((1 - tt / dur) ** 1.6)
    return x * env * 0.8 * gain


def shimmer(root='F4'):
    """快速上行铃铛琶音——卡片/亮点元素落位后的光感"""
    notes = [root, None, None]
    deg = ['F4', 'Ab4', 'C5', 'F5']
    i0 = deg.index(root) if root in deg else 0
    out = []
    for j, f in enumerate(deg[i0:i0 + 3]):
        b = bell(NOTE[f], 0.5)
        out.append((b, j * 0.045))
    return out


def sweep_up(dur=1.5, f0=280, f1=1150, gain=1.0):
    """上扬扫频——折线绘制跟随"""
    n = int(dur * SR); tt = np.arange(n) / SR
    f = f0 + (f1 - f0) * (tt / dur) ** 1.6
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.6
    x += (rng.standard_normal(n) - mvavg(rng.standard_normal(n), 24)) * 0.25
    a = np.clip(tt / 0.15, 0, 1) * np.clip((dur - tt) / 0.12, 0, 1)
    return np.tanh(x * a * 1.1) * 0.5 * gain


def ding():
    """终点清脆一击"""
    b = bell(NOTE['C5'], 0.6)
    b = b + bell(NOTE['F5'], 0.6) * 0.6
    return b * 0.9


# ================= 编排 =================
slam_sounds = []          # 砸字层：压低后最后叠加，对比最大


def add_slam(sig, t0, pan=0.0, gain=1.0):
    slam_sounds.append((sig, t0, pan, gain))


# ---------- S1 0-5.5 數位浪潮：低频铺底 + 逐字tick + 三关键词上行 ----------
add(pad(CH['Fm'], 5.2), 0.0, gain=0.10)
add(subnote(NOTE['F1'], 4.8), 0.15, gain=0.34)                    # 开场低频
for i, t in enumerate([1.0, 2.0, 3.0, 4.0]):                      # 心跳脉冲
    add(subnote(NOTE['F1'], 0.5), t, gain=0.16)
for i in range(6):                                                # 标题逐字 tick（0.25+0.055i）
    add(tick(1.0 + i * 0.06, 0.9), 0.25 + i * 0.055, pan=-0.1 + i * 0.04, gain=0.5)
add(whoosh(0.5, up=True), 0.85, pan=0.0, gain=0.5)                # 副标入
kw = [('F2', 'F4'), ('Ab2', 'Ab4'), ('C3', 'C5')]                 # 三关键词：低音+铃，上行
for i, (bf, bl) in enumerate(kw):
    t = 2.30 + i * 0.28
    add(subnote(NOTE[bf], 0.7), t, gain=0.30)
    add(bell(NOTE[bl], 0.8), t, pan=-0.12 + i * 0.12, gain=0.20)
add(riser(1.5), 3.5, gain=0.24)

# ---------- 转场 whoosh（5.0 左滑 / 9.5 上擦 / 14.0 上滑 / 19.0 左滑 / 24.5 上擦） ----------
for t, up in [(5.0, True), (9.5, True), (14.0, True), (19.0, True), (24.5, True)]:
    add(whoosh(0.55, up=True), t - 0.5, gain=0.6)

# ---------- 驱动节拍 5.0-24.5：四踩 + 2/4拍 + 反拍贝斯 ----------
kick_times = list(np.arange(5.0, 24.01, BEAT))
kick_placements = [(t, 0.92 if t < 9.5 else 1.0) for t in kick_times]   # 侧链之后再放
for ct in np.arange(6.0, 24.0, 1.0):
    if ct in (20.0, 22.0, 24.0):
        continue                       # 砸字拍交给砸字层
    add(clap() + 0.0, ct, gain=0.30)
    add(snare(), ct, gain=0.30)
for t in np.arange(5.0, 14.0, 0.25):                              # 8 分踩镲
    add(hat(False), t, pan=0.16 if (t * 4) % 2 else -0.16, gain=0.10)
for t in np.arange(14.0, 24.5, S16):                              # 渐强 16 分
    add(hat(False), t, pan=0.16 if (t * 8) % 2 else -0.16, gain=0.115 + (0.03 if t >= 19.0 else 0.015))
for t in np.arange(5.5, 24.0, 1.0):                               # 反拍开镲
    add(hat(True), t, pan=0.10, gain=0.13 if t >= 19.0 else 0.10)
for t8 in np.arange(5.25, 24.01, BEAT):                           # 反拍滚动贝斯（跟和弦区域）
    ch = region_chord(t8)
    root = {'Fm': 'F2', 'Db': 'Db2', 'Ab': 'Ab2', 'Eb': 'Eb2'}[ch]
    add(bass(NOTE[root]), t8, gain=0.50)

# 铺底（区域和弦）
for name, ts in REGIONS:
    add(pad(CH[name], 4.2), ts, gain=0.13)
add(pad(CH['Fm'], 5.0), 0.0, gain=0.10)
add(pad(CH['Fm'], 7.2), 24.5, gain=0.15)                          # 尾奏铺底

# ---------- S2 5.0-9.5 實力數據：数字行砸入 + 滚动滴答 ----------
for i in range(3):
    st = 5.85 + i * 0.5
    add(impact(0.52), st)                                          # 行砸入
    add(bell(NOTE[['F4', 'Ab4', 'C5'][i]], 0.7), st, pan=-0.12 + i * 0.12, gain=0.17)
    for j in range(15):                                            # 滚动滴答（音高随数值上升）
        p = j / 14
        add(tick(0.9 + p * 0.9, 0.8), st + 0.05 + p * 0.95, pan=0.1, gain=0.45 + p * 0.3)

# ---------- S3 9.5-14 產品全景：卡片逐张 whoosh+impact+shimmer ----------
for i, root in enumerate(['F4', 'Ab4', 'C5']):
    st = 10.65 + i * 0.3
    add(whoosh(0.45, up=True), st - 0.4, pan=-0.15 + i * 0.15, gain=0.42)
    add(impact(0.55), st)
    kick_placements.append((st, 0.7))
    for sig, off in shimmer(root):
        add(sig, st + 0.02 + off, pan=0.15 - i * 0.15, gain=0.16)

# ---------- S4 14.0-19 核心系統：chip tick + 折线扫频 + 终点ding ----------
for i in range(3):
    add(tick(1.1 + i * 0.12, 1.0), 14.9 + i * 0.2, pan=-0.06 + i * 0.06, gain=1.1)
add(sweep_up(1.5), 15.3, gain=0.30)                               # 折线绘制 15.3-16.8
for i, t in enumerate([15.45, 15.73, 16.02, 16.30]):              # 季度节点 tick
    add(tick(1.2 + i * 0.18, 1.0), t, pan=0.08, gain=0.8)
add(ding(), 16.72, pan=0.0, gain=0.40)                            # ▲ 節節上升
add(whoosh(0.5, up=True), 16.15, gain=0.4)                        # caption 入
# 14-19 琶音渐强
arp = ['F3', 'Ab3', 'C4', 'Eb4']
for i, t in enumerate(np.arange(14.0, 19.0, S16)):
    add(bell(NOTE[arp[i % 4]]), t, pan=(-0.22 if i % 2 else 0.22), gain=0.06 + 0.02 * ((t - 14) / 5))
add(riser(1.7), 17.3, gain=0.34)
for j, st in enumerate(np.arange(18.25, 19.0, S16)):              # 军鼓滚奏
    add(snare(), st, pan=(-0.2 if j % 2 else 0.2), gain=0.12 + 0.32 * (j / 6.0))

# ---------- S5 19-24.5 承諾：lead hook + 反镲 + 砸字三连 ----------
add(impact(0.85), 19.0)
HOOK = [(19.0, 'F4'), (19.5, 'C5'), (19.75, 'Ab4'),
        (20.25, 'Ab4'), (20.5, 'F4'), (21.0, 'Ab4'), (21.5, 'Bb4'), (21.75, 'C5'),
        (22.25, 'C5'), (22.5, 'Bb4'), (23.0, 'Ab4'), (23.5, 'G4'), (23.75, 'F4')]
for t, f in HOOK:
    add(lead(NOTE[f], 0.42), t, pan=-0.16 if int(t * 2) % 2 else 0.16, gain=0.24)
for st in [19.75, 21.75, 23.75]:                                  # 砸字前反镲（32分滚奏+上扬噪声）
    for i in range(8):
        add(hat(False), st + i * S32, pan=0.2 if i % 2 else -0.2, gain=0.07 + 0.024 * i)
    add(whoosh(0.25, up=True), st, gain=0.35)
for i, t in enumerate([19.5, 21.5, 23.5]):                        # kicker（讓複雜變得…）入
    add(tick(1.3 + i * 0.1, 1.0), t, gain=0.55)
for j, st in enumerate([20.0, 22.0, 24.0]):                       # 砸字：军鼓+下潜+和弦+底鼓
    add_slam(snare(), st, gain=0.72)
    add_slam(subdrop(), st, gain=0.70)
    add_slam(stab(SLAM_CH[j], 0.55), st, gain=0.40)
    add_slam(kick(), st, gain=1.0)
    add(whoosh(0.4, up=False), st + 0.08, gain=0.4)               # 红下划线扫入（下降感）

# ---------- S6 24.5-31.5 落版：半拍极简 + 团队名双boom + 终章 ----------
add(impact(0.8), 24.5)
add(subnote(NOTE['F2'], 1.0), 25.05, gain=0.42)                   # TEAM1 揭示
add(bell(NOTE['F4'], 0.9), 25.05, pan=-0.1, gain=0.18)
add(subnote(NOTE['Ab2'], 1.0), 25.45, gain=0.42)                  # TEAM2 揭示
add(bell(NOTE['Ab4'], 0.9), 25.45, pan=0.1, gain=0.18)
add(whoosh(0.6, up=True), 26.2, gain=0.5)                         # 红线扫入 26.2-26.8
for sig, off in shimmer('C5'):
    add(sig, 26.6 + off, gain=0.15)                               # tagline
add(impact(0.9), 27.0)                                            # logo 终章
add(subnote(NOTE['F1'], 2.6), 27.0, gain=0.5)
add(bell(NOTE['F4'], 1.6), 27.0, gain=0.22)
for sig, off in shimmer('F4'):
    add(sig, 27.05 + off, gain=0.13)
for t in [28.5, 29.5, 30.5]:                                      # 尾声稀疏脉冲
    add(subnote(NOTE['F1'], 0.6), t, gain=0.10)

# ================= 混音 =================
duck = np.ones(N)                                                 # 侧链：跟底鼓深泵
w = int(0.20 * SR)
for kt in kick_times + [20.0, 22.0, 24.0]:
    i = int(kt * SR); n = min(w, N - i)
    if n > 0:
        duck[i:i + n] *= (1 - 0.68 * np.exp(-np.arange(n) / SR * 13))
L *= duck
R *= duck

# 底鼓在侧链之后叠加（不受自身侧链压制，低频拍点完整）
for t, gn in kick_placements:
    add(kick(), t, gain=gn)

segenv = np.ones(N)


def setg(a, b, g):
    segenv[int(a * SR):min(int(b * SR), N)] = g


setg(0, 5.0, 0.80)
setg(5.0, 9.5, 0.94)
setg(9.5, 14.0, 0.98)
setg(14.0, 19.0, 1.04)
setg(19.0, 24.5, 1.10)
setg(24.5, 31.5, 0.88)
segenv = mvavg(segenv, int(0.08 * SR))
L *= segenv
R *= segenv

# 砸字前 90ms 快速压低 -> 砸字层最后砸入
dip = np.ones(N)
for st in [20.0, 22.0, 24.0]:
    a, b = int((st - 0.09) * SR), int(st * SR)
    if b > a:
        dip[a:b] = np.minimum(dip[a:b], np.linspace(1.0, 0.40, b - a))
L *= dip
R *= dip
for sig, t0, pan, gn in slam_sounds:
    add(sig, t0, pan=pan, gain=gn)

L = np.tanh(L * 1.12)
R = np.tanh(R * 1.12)

n_fade = int(1.6 * SR)
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