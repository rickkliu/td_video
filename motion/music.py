#!/usr/bin/env python3
"""Txn Banking 广告配乐 v9 —— Cinematic Orchestral（电影级品牌片配乐）
专业广告配乐的做法：一条主题旋律贯穿全片，配器逐层生长——
  S1 钢琴独奏动机 → S2 +心跳大鼓+定音鼓 → S3 +弦乐拨奏节奏+竖琴
  → S4 +钢琴琶音+渐强 → S5 全编制高潮（弦乐主题+铜管+四踩大鼓）
  → S6 终章：小调旅程解决到 F 大调光明终止式。
事件同步音效保留（v7 确认过的好东西），但全部换成 orchestral 质感。
纯器乐，无采样。用法: python3 music.py zh|en
（历史: music_house / music_trap / music_cinematic / music_deephouse）"""
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
rng = np.random.default_rng(9)

NOTE = {
    'F1': 43.65, 'Ab1': 51.91, 'C2': 65.41, 'Db2': 69.30, 'Eb2': 77.78,
    'F2': 87.31, 'Ab2': 103.83, 'Bb2': 116.54, 'C3': 130.81, 'Db3': 138.59,
    'Eb3': 155.56, 'G3': 196.0, 'A3': 220.0, 'F3': 174.61, 'Ab3': 207.65,
    'Bb3': 233.08, 'C4': 261.63, 'Db4': 277.18, 'Eb4': 311.13, 'F4': 349.23,
    'G4': 392.0, 'Ab4': 415.30, 'A4': 440.0, 'Bb4': 466.16, 'C5': 523.25,
    'Db5': 554.37, 'Eb5': 622.25, 'F5': 698.46, 'Ab5': 830.61, 'C6': 1046.5,
    'F6': 1396.9,
}
CH = {
    'Fm':  ['F3', 'Ab3', 'C4'],
    'Db':  ['Db4', 'F4', 'Ab4'],
    'Ab':  ['Ab3', 'C4', 'Eb4'],
    'Eb':  ['Eb4', 'G4', 'Bb4'],
    'FM':  ['F3', 'A3', 'C4'],          # 终章大调（picardy）
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


# ================= 交响音色 =================
def strings(freqs, dur, gain=1.0, attack=0.35, release=0.6):
    """弦乐群：detuned saw 合唱 + 低通 + 慢包络 + 轻微震音"""
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
    """弦乐拨奏/断奏——节奏推进层"""
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
    """钢琴：泛音衰减 + 槌噪声"""
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
    """大鼓：深正弦下坠 + 皮肤瞬态 + 壳共鸣"""
    n = int(0.5 * SR); tt = np.arange(n) / SR
    f = 56 + 95 * np.exp(-tt * 28)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 6.5)
    skin = (rng.standard_normal(n) - mvavg(rng.standard_normal(n), 10)) * np.exp(-tt * 55) * 0.45
    shell = 0.28 * np.sin(2 * np.pi * 175 * tt) * np.exp(-tt * 22)
    return (body + skin + shell) * 0.9 * gain


def timp(f, gain=1.0):
    """定音鼓：有音高的鼓"""
    n = int(0.65 * SR); tt = np.arange(n) / SR
    f_t = f * (1 + 0.45 * np.exp(-tt * 38))
    x = np.sin(2 * np.pi * np.cumsum(f_t) / SR) * np.exp(-tt * 4.5)
    x += 0.3 * np.sin(2 * np.pi * f * 1.5 * tt) * np.exp(-tt * 8)
    x += 0.35 * (rng.standard_normal(n) - mvavg(rng.standard_normal(n), 12)) * np.exp(-tt * 65)
    return x * gain


def brass(freqs, dur=0.9, gain=1.0):
    """铜管：saw 堆叠 + 起音滤波扫频（暗→亮）"""
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
    """大锣：不谐和低频轰鸣长衰减"""
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
    """木琴短音——数字滚动/轻事件（优雅不吵）"""
    n = int(0.30 * SR); tt = np.arange(n) / SR
    x = np.sin(2 * np.pi * f * tt) * np.exp(-tt * 18)
    x += 0.35 * np.sin(2 * np.pi * f * 4.0 * tt) * np.exp(-tt * 42)
    x += 0.15 * np.sin(2 * np.pi * f * 9.2 * tt) * np.exp(-tt * 60)
    k = min(int(0.002 * SR), n)
    x[:k] *= np.linspace(0, 1, k)
    return x * 0.5 * gain


def harp_note(f, gain=1.0):
    """竖琴：亮而干净的拨弦"""
    n = int(1.1 * SR); tt = np.arange(n) / SR
    x = (np.sin(2 * np.pi * f * tt)
         + 0.4 * np.sin(2 * np.pi * f * 2.0 * tt) * np.exp(-tt * 6)
         + 0.15 * np.sin(2 * np.pi * f * 3.0 * tt) * np.exp(-tt * 10))
    x *= np.exp(-tt * 3.0)
    k = min(int(0.002 * SR), n)
    x[:k] *= np.linspace(0, 1, k)
    return x * 0.5 * gain


def harp_gliss(root='F4', gain=1.0):
    """竖琴上行滑奏——卡片落位的光感"""
    deg = ['F4', 'Ab4', 'C5', 'F5', 'Ab5', 'C6']
    i0 = deg.index(root) if root in deg else 0
    seq = deg[i0:i0 + 4] if i0 <= 2 else deg[2:6]
    return [(harp_note(NOTE[f]), j * 0.055) for j, f in enumerate(seq)]


def cin_whoosh(dur=0.6, gain=1.0):
    """弦乐感转场滑音：噪声 + 呼吸包络"""
    n = int(dur * SR); tt = np.arange(n) / SR
    x = rng.standard_normal(n) - mvavg(rng.standard_normal(n), 12)
    x = mvavg(x, 5)
    env = (tt / dur) ** 2.3
    return x * env * 0.5 * gain


def riser_cin(dur=1.7, gain=1.0):
    """电影渐强：上行滑音弦乐 + 噪声涌起 + 心跳加速"""
    n = int(dur * SR); tt = np.arange(n) / SR
    f0 = 174.61 * 2 ** ((tt / dur) * 0.58)          # F3 向上滑 ~半八度
    x = np.sin(2 * np.pi * np.cumsum(f0) / SR) * 0.45
    x += np.sin(2 * np.pi * np.cumsum(f0 * 1.5) / SR) * 0.15
    x += (rng.standard_normal(n) - mvavg(rng.standard_normal(n), 14)) * ((tt / dur) ** 2.1) * 0.55
    a = np.clip(tt / 0.18, 0, 1) * np.clip((dur - tt) / 0.04, 0, 1)
    return np.tanh(x * a * 1.2) * 0.55 * gain


def sweep_up(dur=1.5, gain=1.0):
    """折线跟随：弦乐上行"""
    n = int(dur * SR); tt = np.arange(n) / SR
    f = 262 * 2 ** ((tt / dur) ** 1.5 * 1.3)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.5
    x += (rng.standard_normal(n) - mvavg(rng.standard_normal(n), 20)) * 0.18
    a = np.clip(tt / 0.18, 0, 1) * np.clip((dur - tt) / 0.12, 0, 1)
    return x * a * 0.5 * gain


# ================= 编排 =================
SCENE_T = [0.0, 5.0, 9.5, 14.0, 19.0, 24.5]
SLAMS = [20.0, 22.0, 24.0]
NUMS = [5.85, 6.35, 6.85]
CARDS = [10.65, 10.95, 11.25]
slam_chords = [CH['Fm'], CH['Db'], ['F3', 'A3', 'C4', 'F4']]   # 砸字3 用 F 大调，预告终章光明
slam_lead = ['C5', 'F5', 'C5']                      # 砸字处旋律音：上行到顶点再收
slam_sub = ['F1', 'Db2', 'F1']

# ---------- S1 0-5.5 數位浪潮：钢琴独奏主题 ----------
add(strings(CH['Fm'], 5.5, gain=0.15, attack=1.6, release=0.9), 0.0)          # 弦乐远垫渐入
add(sub(NOTE['F1'], 5.0, 0.30), 0.1)
MOTIF = [(1.0, 'F4', 1.6), (2.30, 'Ab4', 1.1), (2.58, 'C5', 1.1), (2.86, 'Db5', 1.4),
         (3.65, 'C5', 1.0), (4.15, 'Ab4', 0.9), (4.55, 'F4', 0.7)]
for t, f, d in MOTIF:                                                          # 主题第一次陈述
    add(piano(NOTE[f], d + 1.0, 0.9), t, pan=-0.08)
    add(strings([f], 1.6, gain=0.05, attack=0.3), t, pan=0.1)                  # 弦乐跟旋律（轻）
for t, gf in [(2.30, 'F2'), (2.58, 'Ab2'), (2.86, 'C3')]:                      # 关键词低音支撑
    add(sub(NOTE[gf], 1.4, 0.20), t)
for t, g in [(1.0, 0.45), (2.0, 0.5), (3.0, 0.55), (4.0, 0.6), (4.5, 0.7), (4.75, 0.8)]:
    add(taiko(g), t)                                                           # 心跳渐强加速
for i in range(6):                                                             # 逐字（木琴极轻）
    add(marimba(NOTE['F6'] / (2 ** (5 - i) / 12), 0.35), 0.25 + i * 0.055, pan=-0.1 + i * 0.04)
add(cin_whoosh(0.55, 0.55), 0.75)
add(riser_cin(1.6, 0.8), 3.4)

# ---------- 转场 ----------
for ts in SCENE_T[1:]:
    add(cin_whoosh(0.6, 0.55), ts - 0.55)

# ---------- S2 5-9.5 實力數據：心跳+定音鼓进场 ----------
add(strings(CH['Db'], 4.6, gain=0.17, attack=0.5), 5.0)
for t in np.arange(5.0, 9.0, 1.0):                                             # 心跳大鼓（秒级）
    add(taiko(0.62 if t < 8.0 else 0.72), t)
for t in np.arange(5.0, 9.5, BEAT * 2):                                        # 弦乐断奏节奏（2拍一粒）
    add(stac(CH['Db'], 0.35), t)
# 钢琴动机变奏
for t, f, d in [(5.0, 'C5', 1.0), (5.5, 'Db5', 1.0), (6.0, 'C5', 0.8), (6.5, 'Ab4', 0.8),
                (7.0, 'F4', 1.4), (8.0, 'Ab4', 1.0), (8.5, 'C5', 1.4)]:
    add(piano(NOTE[f], d + 0.8, 0.75), t, pan=-0.06)
for i, (st, gf) in enumerate(zip(NUMS, ['F2', 'Ab2', 'C3'])):                  # 数字行：定音鼓上行！
    add(timp(NOTE[gf], 0.75), st)
    add(sub(NOTE[gf], 1.2, 0.22), st)
    for j in range(12):                                                        # 滚动木琴（音高上行）
        p = j / 11
        add(marimba(NOTE['C5'] * (2 ** (p * 7 / 12)), 0.30), st + 0.06 + p * 0.9, pan=0.08)
add(strings(CH['Ab'], 1.2, gain=0.16, attack=0.3, release=0.5), 8.6)           # 预备 swell

# ---------- S3 9.5-14 產品全景：弦乐节奏+竖琴 ----------
add(strings(CH['Ab'], 4.6, gain=0.24, attack=0.45), 9.5)
for t in np.arange(9.5, 14.0, BEAT):                                           # 断奏密度加倍（每拍）
    add(stac(CH['Ab'] if (t * 2) % 4 < 2 else CH['Eb'], 0.42), t)
for t in np.arange(10.0, 14.0, 1.0):
    add(taiko(0.62), t)
# 主题弦乐化（第一次交给弦乐）
for t, f, d in [(9.5, 'Ab4', 1.2), (10.0, 'C5', 1.0), (10.5, 'Db5', 1.4),
                (11.5, 'C5', 1.0), (12.0, 'Ab4', 1.0), (12.5, 'F4', 1.5)]:
    add(strings([f], d + 0.8, gain=0.14, attack=0.12, release=0.5), t, pan=0.08)
    add(piano(NOTE[f], d + 0.6, 0.55), t, pan=-0.12)
for i, (st, root) in enumerate(zip(CARDS, ['F4', 'Ab4', 'C5'])):               # 卡片：竖琴滑奏+软大鼓
    add(cin_whoosh(0.45, 0.5), st - 0.4, pan=-0.15 + i * 0.15)
    add(taiko(0.42), st)
    for sig, off in harp_gliss(root):
        add(sig, st + 0.02 + off, pan=0.15 - i * 0.15, gain=0.16)
add(riser_cin(1.2, 0.6), 12.8)

# ---------- S4 14-19 核心系統：琶音+渐强 ----------
add(strings(CH['Eb'], 4.6, gain=0.22, attack=0.45), 14.0)
for t in np.arange(14.0, 14.5, BEAT):                                          # 断奏继续
    pass
for t in np.arange(14.0, 18.5, BEAT):
    add(stac(CH['Eb'], 0.32), t)
arp_notes = ['F3', 'Ab3', 'C4', 'F4']
i = 0
for t in np.arange(14.0, 18.5, S16):                                           # 钢琴 16 分琶音
    add(piano(NOTE[arp_notes[i % 4]], 0.8, 0.30), t, pan=(-0.14 if i % 2 else 0.14))
    i += 1
for t in np.arange(14.0, 19.0, BEAT):                                          # 大鼓四踩进场
    add(taiko(0.58 if t < 17.0 else 0.68), t)
for i in range(3):                                                             # chips
    add(marimba(NOTE['Ab5'] / (2 ** (2 - i) / 12), 0.5), 14.9 + i * 0.2, pan=-0.06 + i * 0.06)
add(sweep_up(1.5, 0.7), 15.3)                                                  # 折线
for i, t in enumerate([15.45, 15.73, 16.02, 16.30]):
    add(harp_note(NOTE['F5'] / (2 ** (3 - i) / 12), 0.5), t, pan=0.07)
add(piano(NOTE['F5'], 2.0, 0.6), 16.72)                                        # ▲ 终点
add(strings(['F4'], 1.0, gain=0.12, attack=0.1), 16.72, pan=0.05)
add(cin_whoosh(0.5, 0.4), 16.15)
add(riser_cin(1.8, 0.95), 17.2)
for j, st in enumerate(np.arange(18.25, 19.0, S16)):                           # 定音鼓滚奏渐强
    add(timp(NOTE['F2'], 0.28 + 0.34 * (j / 6.0)), st, pan=(-0.18 if j % 2 else 0.18))

# ---------- S5 19-24.5 承諾：全编制高潮 ----------
add(strings(CH['Fm'], 5.5, gain=0.30, attack=0.28, release=0.8), 19.0)         # 全奏弦乐
add(brass(CH['Fm'], 2.2, 0.22), 19.0)
add(taiko(0.95), 19.0)
add(timp(NOTE['F2'], 0.8), 19.0)
add(crash(1.4, 0.5), 19.0)
LEAD = [(19.0, 'F4', 1.2), (19.5, 'Ab4', 0.8), (20.0, 'C5', 1.4), (21.0, 'Db5', 1.2),
        (21.5, 'Eb5', 0.8), (22.0, 'F5', 1.8), (23.0, 'Eb5', 0.9), (23.5, 'Db5', 0.35), (24.0, 'C5', 1.6)]
for t, f, d in LEAD:                                                           # 弦乐主题全奏（lead 线）
    add(strings([f], d + 0.9, gain=0.20, attack=0.10, release=0.45), t, pan=0.1)
    add(piano(NOTE[f], d + 0.5, 0.42), t, pan=-0.14)                           # 钢琴双八度支撑
    if NOTE[f] * 2 < 800:
        add(strings([f], d + 0.7, gain=0.06, attack=0.12), t, pan=-0.05)       # 高八度叠（轻）
for t in np.arange(19.0, 24.5, BEAT):                                          # 大鼓四踩
    if t in SLAMS:
        continue
    add(taiko(0.72), t)
for t in [19.0, 21.0, 23.0]:
    add(timp(NOTE['F2'], 0.6), t)
for t in np.arange(19.0, 24.5, BEAT):
    add(stac(CH['Fm'], 0.26), t)                                               # 断奏持续
for i, st in enumerate(SLAMS):                                                 # 砸字 = 乐队全奏重击
    last = (i == 2)
    add(strings(slam_chords[i], 1.6, gain=0.34, attack=0.015, release=0.7), st)    # 弦乐重音
    add(brass(slam_chords[i], 1.1, 0.28 if last else 0.20), st)
    add(taiko(1.0), st)
    add(timp(NOTE[slam_sub[i]], 0.75), st)
    add(sub(NOTE[slam_sub[i]], 1.1, 0.34), st)
    add(crash(1.2, 0.42), st)
    if last:
        add(tam(2.4, 0.38), st)                                                 # 最后一击加大锣
    add(piano(NOTE[slam_lead[i]], 2.0, 0.55), st)                              # 旋律点：C5→F5→C5
for i, t in enumerate([19.5, 21.5]):                                           # kicker（讓複雜變得…；第三句前留白）
    add(marimba(NOTE['Ab5'] / (2 ** (2 - i) / 12), 0.45), t)

# ---------- S6 24.5-31.5 落版：光明终止式 ----------
add(taiko(0.6), 24.5)
add(strings(CH['Fm'], 3.4, gain=0.22, attack=0.3, release=1.2), 24.5)
add(sub(NOTE['F1'], 2.0, 0.28), 24.5)
add(piano(NOTE['F4'], 2.4, 0.62), 25.05, pan=-0.08)                            # TEAM1
add(strings(['F4'], 1.6, gain=0.13, attack=0.15), 25.05, pan=-0.08)
add(piano(NOTE['Ab4'], 2.4, 0.62), 25.45, pan=0.08)                            # TEAM2
add(strings(['Ab4'], 1.6, gain=0.13, attack=0.15), 25.45, pan=0.08)
add(cin_whoosh(0.6, 0.5), 26.2)                                                # 红线
for sig, off in harp_gliss('C5'):
    add(sig, 26.6 + off, gain=0.14)                                            # tagline
# 终章：小调 → F 大调（picardy third，光明收尾）
add(taiko(0.95), 27.0)
add(tam(3.0, 0.5), 27.0)
add(strings(CH['FM8'], 4.2, gain=0.30, attack=0.06, release=2.2), 27.0)
add(brass(CH['FM'], 2.4, 0.24), 27.0)
add(piano(NOTE['F4'], 3.0, 0.6), 27.0)
add(piano(NOTE['C4'], 2.4, 0.4), 27.02)
add(sub(NOTE['F1'], 3.5, 0.42), 27.0)
add(crash(2.0, 0.45), 27.0)
for sig, off in harp_gliss('F4'):
    add(sig, 27.05 + off, gain=0.13)
add(piano(NOTE['F5'], 2.4, 0.35), 29.0)                                        # 尾声泛音
add(sub(NOTE['F1'], 1.0, 0.14), 29.0)
add(sub(NOTE['F1'], 0.9, 0.10), 30.3)

# ================= 混音 =================
# 侧链（浅）：跟大鼓/定音鼓呼吸
duck = np.ones(N)
w = int(0.24 * SR)
kt_all = [t for t in np.arange(19.0, 24.5, BEAT)] + SLAMS + [19.0, 27.0]
for kt in kt_all:
    i = int(kt * SR); n = min(w, N - i)
    if n > 0:
        duck[i:i + n] *= (1 - 0.34 * np.exp(-np.arange(n) / SR * 10))
L *= duck
R *= duck

# 分段能量：逐场生长
segenv = np.ones(N)


def setg(a, b, g):
    segenv[int(a * SR):min(int(b * SR), N)] = g


setg(0, 5.0, 0.88)
setg(5.0, 9.5, 0.92)
setg(9.5, 14.0, 0.98)
setg(14.0, 19.0, 1.05)
setg(19.0, 24.5, 1.14)
setg(24.5, 27.0, 0.96)
setg(27.0, 31.5, 0.90)
segenv = mvavg(segenv, int(0.10 * SR))
L *= segenv
R *= segenv

# 砸字前压低 -> 全奏炸开（第三击前 0.5s 深呼吸）
dip = np.ones(N)
for st in SLAMS:
    a, b = int((st - 0.08) * SR), int(st * SR)
    if b > a:
        dip[a:b] = np.minimum(dip[a:b], np.linspace(1.0, 0.62, b - a))
a, b = int(23.5 * SR), int(24.0 * SR)
if b > a:
    dip[a:b] = np.minimum(dip[a:b], np.linspace(1.0, 0.42, b - a) ** 0.6)
L *= dip
R *= dip

L = np.tanh(L * 1.05)
R = np.tanh(R * 1.05)

fade = np.ones(N)
fade[N - int(2.2 * SR):] = np.linspace(1, 0, int(2.2 * SR)) ** 0.85
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