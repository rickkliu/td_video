#!/usr/bin/env python3
"""Txn Banking 广告配乐 v5 —— 唱字版（120 BPM，F 小调，tech-house 律动）
核心思路：所有重音严格落在字幕砸落的同一时刻（20.0 / 22.0 / 24.0s 等），
并用 espeak-ng 人声采样（粤语/英语）"唱"出关键词，形成人声即节奏的钩子。
用法: python3 music.py zh|en  ->  music_zh.wav / music_en.wav"""
import math
import subprocess
import sys
import wave

import numpy as np

LANG = (sys.argv[1] if len(sys.argv) > 1 else 'zh').lower()
USE_VOX = False   # 人声唱字开关（当前关闭：纯器乐版）
SR = 44100
DUR = 31.5
N = int(DUR * SR)
BPM = 120
BEAT = 60 / BPM          # 0.5s
S16 = BEAT / 4           # 0.125s
rng = np.random.default_rng(11)

# F 小调和声
F2, Ab2, Bb2, C3 = 87.31, 103.83, 116.54, 130.81
F3, Ab3, C4, Eb4, G4, F4, Ab4, Bb4, C5 = 174.61, 207.65, 261.63, 311.13, 392.0, 349.23, 415.30, 466.16, 523.25
STAB_CH = [[F3, Ab3, C4, Eb4], [Ab3, C4, Eb4, G4]]          # Fm7 / Abmaj7
BASS_ALT = [[F2, F2, Ab2, C3], [F2, F2, Bb2, Ab2]]
SLAM_CH = [[F3, Ab3, C4], [Ab3, C4, F4], [C4, F4, Ab4]]     # 砸字和弦：Fm 转位上行
LEAD = [F4, Ab4, Bb4, C5, Bb4, Ab4, F4, Eb4]

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
def kick():
    n = int(0.40 * SR); tt = np.arange(n) / SR
    f = 46 + 130 * np.exp(-tt * 24)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * env_exp(n, 6.5)
    click = rng.standard_normal(n) * 0.22 * env_exp(n, 220)     # 更硬的音头
    sub = np.sin(2 * np.pi * 58 * tt) * env_exp(n, 30) * 0.5    # 并行低频冲击
    return np.tanh((body + click + sub) * 2.2) * 0.9


def hat(open_=False):
    n = int((0.24 if open_ else 0.055) * SR)
    x = rng.standard_normal(n) - mvavg(rng.standard_normal(n), 8)
    return x * env_exp(n, 7 if open_ else 95)


def shaker():
    n = int(0.05 * SR)
    x = rng.standard_normal(n) - mvavg(rng.standard_normal(n), 16)
    return mvavg(x, 2) * env_exp(n, 140)


def snare():
    n = int(0.19 * SR); tt = np.arange(n) / SR
    x = (rng.standard_normal(n) - mvavg(rng.standard_normal(n), 20)) * env_exp(n, 26)
    x += 0.7 * np.sin(2 * np.pi * 196 * tt) * env_exp(n, 42)
    return x * 0.9


def clap():
    n = int(0.22 * SR); tt = np.arange(n) / SR
    x = rng.standard_normal(n) - mvavg(rng.standard_normal(n), 24)
    burst = np.exp(-tt * 48) + 0.6 * np.exp(-((tt - 0.010) ** 2) / 1.6e-5) + 0.45 * np.exp(-((tt - 0.021) ** 2) / 1.6e-5)
    return x * burst * env_exp(n, 14)


def bass(fr, dark=0.0):
    n = int(0.24 * SR); tt = np.arange(n) / SR
    saw = mvavg(2 * ((tt * fr) % 1.0) - 1, int(1 + 16 * dark))
    x = 0.6 * saw + 0.95 * np.sin(2 * np.pi * fr * tt)
    return np.tanh(x * 1.4) * np.clip(tt / 0.004, 0, 1) * env_exp(n, 9)


def stab(freqs, dur=0.4):
    n = int(dur * SR); tt = np.arange(n) / SR
    x = np.zeros(n)
    for f in freqs:
        x += 2 * ((tt * f * 1.003) % 1.0) - 1 + 2 * ((tt * f * 0.997) % 1.0) - 1
    x = mvavg(x / (len(freqs) * 2), 10)
    return x * np.clip(tt / 0.003, 0, 1) * np.exp(-tt * 4.5)


def pluck(fr):
    n = int(0.40 * SR); tt = np.arange(n) / SR
    x = (2 * ((tt * fr * 1.004) % 1.0) - 1) * 0.5 + (2 * ((tt * fr * 0.996) % 1.0) - 1) * 0.5
    return mvavg(x, 5) * np.clip(tt / 0.002, 0, 1) * env_exp(n, 15)


def pad(freqs, dur):
    n = int(dur * SR); tt = np.arange(n) / SR
    x = np.zeros(n)
    for f in freqs:
        x += np.sin(2 * np.pi * f * tt) + 0.35 * np.sin(2 * np.pi * f * 1.007 * tt)
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
    """砸字瞬间的下坠低频——人耳能感到的『咚』"""
    n = int(0.55 * SR); tt = np.arange(n) / SR
    f = 110 * np.exp(-tt * 7) + 36
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * env_exp(n, 5.5)
    x += 0.12 * (rng.standard_normal(n) - mvavg(rng.standard_normal(n), 10)) * env_exp(n, 40)
    return np.tanh(x * 1.6)


# ---------- 人声采样（espeak-ng） ----------
VOX_DIR = '/tmp/vox'


def make_vox():
    if LANG == 'zh':
        v = 'yue'   # BEA 是香港银行，繁体字幕 -> 粤语
        spec = {
            's1':   (v, 138, 42, '被看見，被守護，被信任'),
            'c1':   (v, 150, 60, '支付'),
            'c2':   (v, 150, 63, '現金管理'),
            'c3':   (v, 150, 57, '貿易融資'),
            'p1':   (v, 138, 58, '順暢'),
            'p2':   (v, 138, 63, '自然'),
            'p3':   (v, 158, 68, '與時俱進'),
            'hey':  (v, 175, 74, '嘿'),
        }
    else:
        v = 'en-us'
        spec = {
            's1':   (v, 126, 46, 'Seen. Safeguarded. Trusted.'),
            'c1':   (v, 148, 58, 'Payments'),
            'c2':   (v, 152, 62, 'Cash Management'),
            'c3':   (v, 152, 56, 'Trade Finance'),
            'p1':   (v, 132, 56, 'Smooth'),
            'p2':   (v, 132, 61, 'Natural'),
            'p3':   (v, 148, 66, 'Always current'),
            'hey':  (v, 175, 72, 'Hey'),
        }
    spec['team1'] = ('en-us', 128, 52, 'Transaction Banking')
    spec['team2'] = ('en-us', 132, 57, 'Applications Team')
    out = {}
    for name, (voice, speed, pitch, text) in spec.items():
        path = f'{VOX_DIR}/{LANG}_{name}.wav'
        subprocess.run(['espeak-ng', '-v', voice, '-s', str(speed), '-p', str(pitch),
                        '-a', '185', '-w', path, text], check=True)
        with wave.open(path) as wf:
            assert wf.getframerate() == 22050
            d = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float64) / 32768.0
        d = np.interp(np.arange(0, len(d), 22050 / SR), np.arange(len(d)), d)   # 重采样到 44.1k
        # 去首尾静音
        idx = np.where(np.abs(d) > 0.04 * np.abs(d).max())[0]
        if len(idx):
            a, b = max(0, idx[0] - int(0.008 * SR)), min(len(d), idx[-1] + int(0.06 * SR))
            d = d[a:b]
        # FFT 带通 170-8500Hz（去掉隆隆声与嘶声）
        X = np.fft.rfft(d)
        fr = np.fft.rfftfreq(len(d), 1 / SR)
        g = np.ones_like(fr)
        g[fr < 170] = np.clip((fr[fr < 170] - 130) / 40, 0, 1)
        g[fr > 8500] = np.clip((9000 - fr[fr > 8500]) / 500, 0, 1)
        d = np.fft.irfft(X * g[:len(X)], len(d))
        d = np.tanh(d * 1.7)                       # 轻饱和 -> 更"电子人声"
        d *= 0.9 / max(np.abs(d).max(), 1e-6)
        n_in, n_out = int(0.008 * SR), int(0.07 * SR)
        if len(d) > n_in + n_out:
            d[:n_in] *= np.linspace(0, 1, n_in)
            d[-n_out:] *= np.linspace(1, 0, n_out)
        out[name] = d
    return out


VOX = make_vox() if USE_VOX else {}


def rs(x, f):
    """变速变调（f>1 = 升调缩短）"""
    return np.interp(np.arange(0, len(x), f), np.arange(len(x)), x)


duck_events = []   # (t0, depth, recover_s) —— 人声出现时压低伴奏


def vox(name, t0, gain=0.4, pitch=1.0, pan=0.0, wet=0.20, duck=0.75, rec=0.35):
    """放置人声：干声 + 八度垫底 + 3/16 乒乓回声"""
    if not USE_VOX:
        return
    x = VOX[name]
    if pitch != 1.0:
        x = rs(x, pitch)
    if len(x) < 64:
        return
    add(x, t0, pan=pan, gain=gain)
    add(rs(x, 0.5), t0, pan=pan, gain=gain * 0.35)          # 低八度层，加厚
    for k in range(1, 4):                                    # 3/16 回声
        add(x, t0 + S16 * 3 * k, pan=-pan if k % 2 else pan, gain=gain * wet * (0.72 ** (k - 1)))
    duck_events.append((t0, duck, rec))


# ---------- 伴奏编排 ----------
# 场景切换: 5.0 / 9.5 / 14.0 / 19.0 / 24.5 —— 全部在 120BPM 网格上
kick_times = list(np.arange(0.5, 24.01, BEAT)) + [25.0, 26.0, 27.0, 28.0]   # 24.5 后半拍

duck = np.ones(N)                       # 侧链泵动（跟底鼓）
w = int(0.20 * SR)
for kt in kick_times:
    i = int(kt * SR); n = min(w, N - i)
    if n > 0:
        duck[i:i + n] *= (1 - 0.60 * np.exp(-np.arange(n) / SR * 13))   # 更深 -> 泵感更强

# 16 分踩镲（带摇摆）+ 反拍开镲
b = 0.5
while b < 24.5:
    for k in range(4):
        tt = b + k * S16
        if k in (1, 3):
            tt += S16 * 0.22
        if tt >= 24.5:
            continue
        peak = 19.0 <= tt < 24.5
        build = 14.0 <= tt < 19.0
        if tt >= 1.0:
            g = 0.115 + (0.03 if k == 2 else 0) + (0.025 if (peak or build) else 0)
            add(hat(False), tt, pan=0.16 if k % 2 == 0 else -0.16, gain=g)
        if k == 2 and tt >= 5.0:
            g = 0.20 if peak else (0.14 if tt >= 10.0 else 0.11)
            add(hat(True), tt, pan=0.10, gain=g)
        if k in (1, 3) and tt >= 14.0:
            add(shaker(), tt, pan=-0.24 if k == 1 else 0.24, gain=0.10)
    b += BEAT

# 2/4 拍：拍手 + 军鼓叠加（更有火力）
def clap_snare():
    c, s = clap(), snare()
    m = max(len(c), len(s))
    cp, sp = np.zeros(m), np.zeros(m)
    cp[:len(c)], sp[:len(s)] = c, s
    return cp + 0.55 * sp


for ct in np.arange(5.0, 24.0, 1.0):
    add(clap_snare(), ct, gain=0.46)

# 18.25-19.0 军鼓滚奏（推向砸字高潮）
for j, st in enumerate(np.arange(18.25, 19.0, S16)):
    add(snare(), st, pan=(-0.2 if j % 2 else 0.2), gain=0.10 + 0.30 * (j / 6.0))

# 反拍滚动贝斯
for t8 in np.arange(2.75, 24.01, BEAT):
    bar_i = int(t8 / 2.0)
    idx = int(round(((t8 % 2.0) - 0.25) / 0.5))
    note = BASS_ALT[bar_i % 2][min(idx, 3)]
    if bar_i % 4 == 3 and idx == 3:
        note *= 2
    dark = max(0.0, min(1.0, (5.0 - t8) / 2.5))
    peak = 19.0 <= t8 < 24.5
    add(bass(note, dark), t8, gain=0.52 if peak else 0.46)

# 切分和弦 stab
for bar_i in range(5, 12):
    t0 = 0.5 + bar_i * 2.0
    peak = 19.0 <= t0 < 24.5
    ch = STAB_CH[(bar_i // 2) % 2]
    add(stab(ch), t0 + 0.75, pan=-0.1, gain=0.26 if peak else 0.20)
    if bar_i % 2 == 1:
        add(stab(ch), t0 + 1.75, pan=0.1, gain=0.24 if peak else 0.18)

# 高潮拨弦旋律
for i, lt in enumerate(np.arange(19.0, 24.01, BEAT)):
    p = -0.30 if i % 2 == 0 else 0.30
    add(pluck(LEAD[i % len(LEAD)]), lt, pan=p, gain=0.25)
    add(pluck(LEAD[i % len(LEAD)]), lt + S16 * 3, pan=-p, gain=0.09)

# 铺底
seg_t = 0.0
while seg_t < DUR:
    ch = STAB_CH[int(seg_t / 4.0) % 2]
    d = min(4.4, DUR - seg_t)
    if d > 0.3:
        g = 0.15 if seg_t >= 9.5 else 0.11
        if seg_t >= 24.5:
            g = 0.17
        add(pad(ch, d), seg_t, gain=g)
    seg_t += 4.0

# riser / 冲击 / 砸字下坠 + 砸字和弦
add(riser(1.5), 8.0, gain=0.22)
add(riser(1.7), 17.3, gain=0.34)
for it, g in [(5.0, 0.45), (9.5, 0.60), (14.0, 0.45), (19.0, 0.85), (24.5, 0.85)]:
    add(impact(g), it)
for j, st in enumerate([20.0, 22.0, 24.0]):
    add(subdrop(), st, gain=0.60)
    add(stab(SLAM_CH[j], 0.55), st, pan=0.0, gain=0.30)

# ---------- 人声编排（与画面文字严格同一时刻） ----------
vox('s1', 2.30, gain=0.26, pan=-0.12, wet=0.30, duck=0.85, rec=0.5)      # S1 关键词 2.3s 起依次浮现
vox('c1', 11.0, gain=0.36, pan=-0.10, wet=0.18)                          # S3 卡片 01 支付
vox('c2', 11.5, gain=0.36, pan=0.10, wet=0.18)                           # S3 卡片 02 現金管理
vox('c3', 12.0, gain=0.36, pan=0.0, wet=0.18)                            # S3 卡片 03 貿易融資
vox('hey', 16.5, gain=0.24, pan=0.2, wet=0.15, duck=0.9, rec=0.2)        # 铺垫
vox('hey', 17.5, gain=0.28, pan=-0.2, wet=0.15, duck=0.9, rec=0.2)
for k, (nm, st, pit) in enumerate([('p1', 19.95, 1.0), ('p2', 21.95, 1.0595), ('p3', 23.95, 1.1225)]):
    vox('hey', st - 0.25, gain=0.26, pan=0.15, wet=0.12, duck=0.9, rec=0.2)   # 砸字前 1/4 拍 "嘿!"
    vox(nm, st, gain=0.58, pitch=pit, pan=0.0, wet=0.24, duck=0.72, rec=0.4)  # 与大字同瞬间"唱"出
vox('team1', 25.05, gain=0.42, pan=-0.08, wet=0.26, duck=0.8, rec=0.5)   # S6 团队名两行揭示
vox('team2', 25.50, gain=0.42, pitch=1.0595, pan=0.08, wet=0.26, duck=0.8, rec=0.5)

# ---------- 混音 ----------
# 人声出现时压低伴奏（让人声穿透）
vduck = np.ones(N)
for t0, depth, rec in duck_events:
    i0 = int(t0 * SR); i1 = min(N, i0 + int(rec * SR))
    if i1 > i0:
        seg = np.linspace(depth, 1.0, i1 - i0) ** 0.7
        vduck[i0:i1] = np.minimum(vduck[i0:i1], seg)

L *= duck * vduck
R *= duck * vduck

segenv = np.ones(N)


def setg(a, b, g):
    segenv[int(a * SR):min(int(b * SR), N)] = g


setg(0, 5.0, 0.86)
setg(5.0, 9.5, 0.98)
setg(9.5, 14.0, 1.02)
setg(14.0, 19.0, 1.06)
setg(19.0, 24.5, 1.12)
setg(24.5, 31.5, 0.90)
segenv = mvavg(segenv, int(0.08 * SR))
L *= segenv
R *= segenv

for kt in kick_times:                        # 底鼓最后叠上（不受侧链影响）
    add(kick(), kt, gain=0.95 if kt < 5.0 else 1.0)

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