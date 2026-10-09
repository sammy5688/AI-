# 「初心」配樂 第二版：讓聲音更像真實樂器
# 鋼琴：三弦微差、琴弦非諧和性、琴槌聲、兩段式衰減；弦樂群：多聲部合奏與緩慢開合的濾波；
# 演奏：時間與力道的人性化；空間：分頻衰減的音樂廳殘響；母帶：輕壓縮、軟飽和、限幅。
import numpy as np, json, wave
from scipy import signal
SR, DUR = 44100, 52.0
N = int(SR * DUR)
L = np.zeros(N); R = np.zeros(N)          # 鋼琴與鈴
PL = np.zeros(N); PR = np.zeros(N)        # 弦樂群（另外處理濾波）
rng = np.random.default_rng(11)
f = lambda m: 440.0 * 2 ** ((m - 69) / 12)

def put(bufL, bufR, sig, t0, pan=0.0):
    i = int(round(t0 * SR))
    if i < 0: sig = sig[-i:]; i = 0
    j = min(N, i + len(sig))
    if j <= i: return
    s = sig[:j - i]; a = (pan + 1) * np.pi / 4
    bufL[i:j] += s * np.cos(a); bufR[i:j] += s * np.sin(a)

# ---------- 鋼琴 ----------
def piano(m, vel=.5, length=None):
    f0 = f(m)
    length = length or float(np.clip(7.5 * (261.6 / f0) ** .5, 3.0, 9.0))
    n = int(length * SR); t = np.arange(n) / SR
    B = 4e-5 * (f0 / 130) ** 1.3                      # 琴弦的非諧和性（高次泛音略偏高）
    tau0 = float(np.clip(5.5 * (261.6 / f0) ** .7, 1.2, 9.0))
    bright = .75 + .9 * vel
    out = np.zeros(n)
    for k in range(1, 26):
        fk = k * f0 * np.sqrt(1 + B * k * k)
        if fk > 9000: break
        amp = np.sin(np.pi * k * .118) ** 2 / k ** (1.55 - .55 * bright)   # 琴槌敲在弦長 1/8.5 處
        tau = tau0 / (1 + .32 * (k - 1) ** 1.15)
        env = .62 * np.exp(-t / (tau * .18)) + .38 * np.exp(-t / tau)     # 先快後慢的兩段衰減
        strings = 3 if k < 8 else 2
        for s in range(strings):                       # 同一個鍵的幾根弦，音高差一點點，產生自然的起伏
            det = 1 + (s - (strings - 1) / 2) * .0009 * rng.uniform(.6, 1.4)
            out += amp / strings * env * np.sin(2 * np.pi * fk * det * t + rng.uniform(0, 6.28))
    hn = int(.012 * SR)                                # 琴槌的敲擊聲
    hammer = rng.standard_normal(hn) * np.exp(-np.arange(hn) / (hn / 4))
    hammer = signal.lfilter(*signal.butter(2, min(.9, (900 + 2600 * vel) / (SR / 2))), hammer)
    out[:hn] += hammer * .05 * vel
    out *= np.minimum(1, t / .0025)
    out *= np.minimum(1, np.maximum(0, (length - t) / .4))
    return out * vel * .2

def human(t, vel, tj=.014, vj=.08):
    return t + rng.normal(0, tj), float(np.clip(vel * (1 + rng.normal(0, vj)), .05, 1))

def chord_roll(notes, t0, vel, spread=.09):          # 和弦由低到高輕輕滾開
    for i, m in enumerate(sorted(notes)):
        tt, vv = human(t0 + i * spread * rng.uniform(.7, 1.3), vel * (1 - .08 * i))
        put(L, R, piano(m, vv), tt, pan=(m - 64) / 40)

# ---------- 玻璃鈴（愛心、漣漪）：柔和的鐘琴音色 ----------
def glass(m, vel=.3, length=4.5):
    f0 = f(m); n = int(length * SR); t = np.arange(n) / SR
    s = np.zeros(n)
    for r, a, d in [(1, 1, 2.2), (2.0, .25, 1.0), (3.01, .12, .6), (4.16, .06, .35)]:
        s += a * np.sin(2 * np.pi * f0 * r * t + rng.uniform(0, 6.28)) * np.exp(-t / d)
    return s * np.minimum(1, t / .004) * vel * .13

# ---------- 弦樂群 ----------
def ensemble(m, length, amp, bright_curve, voices=5):
    n = int(length * SR); t = np.arange(n) / SR
    out = np.zeros(n)
    for v in range(voices):
        cents = rng.uniform(-9, 9) + 4 * np.sin(2 * np.pi * rng.uniform(.12, .3) * t + rng.uniform(0, 6))
        ph = 2 * np.pi * np.cumsum(f(m) * 2 ** (cents / 1200)) / SR + rng.uniform(0, 6.28)
        saw = np.zeros(n)
        for k in range(1, 40):
            if k * f(m) > 4500: break
            saw += np.sin(k * ph) / k
        out += saw
    env = np.minimum(1, t / 1.6) * np.minimum(1, np.maximum(0, (length - t) / 1.8))
    return out / voices * env * amp

# ========== 編曲（旋律與對拍點與上一版相同）==========
chords = [(0, 5.2, [38, 50, 57, 62, 66]), (5.0, 10.2, [35, 47, 54, 62, 66]),
          (10, 13.7, [31, 43, 50, 59, 62]), (13.5, 17.2, [38, 50, 57, 62, 66]), (17, 21.2, [33, 45, 52, 61, 64]),
          (21, 26.2, [35, 47, 54, 62, 66]), (26, 31.2, [31, 43, 50, 59, 62]),
          (31, 34.2, [31, 43, 50, 59, 62]), (34, 37.2, [33, 45, 52, 61, 64]), (37, 39.7, [35, 47, 54, 62, 66]), (39.5, 42.2, [33, 45, 52, 61, 64]),
          (42, 52, [38, 50, 57, 62, 66, 69])]
# 弦樂：每個和弦一層（不含最低音）
for a, b, notes in chords:
    for k, m in enumerate(notes[1:]):
        put(PL, PR, ensemble(m, b - a + 1.8, .018 if m < 55 else .03, None), a - .3, pan=(k - 1.8) * .35)
# 鋼琴左手：每個和弦進來時，輕輕彈出低音與和弦
for a, b, notes in chords:
    if a < 1: a = .6
    tt, vv = human(a + .05, .24)
    put(L, R, piano(notes[0] + 12, vv), tt, pan=-.25)
    chord_roll(notes[1:3], a + .35, .22, .14)

# 右手旋律
mel = [(1.0, 66), (2.2, 69), (3.2, 74, .62), (4.6, 73), (5.6, 71), (6.4, 69, .52), (7.4, 66), (8.6, 64), (9.4, 66),
       (11.0, 74), (12.4, 76), (13.6, 78, .55), (15.5, 76), (17.0, 74, .55), (18.0, 73), (19.5, 69),
       (22.0, 71, .48), (23.2, 69), (26.8, 66, .48), (27.8, 67), (28.8, 69), (30.0, 71),
       (36.0, 78, .66), (37.4, 81, .7), (38.6, 79), (39.8, 78), (40.8, 76),
       (42.4, 74), (43.6, 78), (44.0, 81, .62), (45.4, 78), (46.6, 76), (47.0, 74, .55), (48.4, 73), (49.6, 74, .6)]
for e in mel:
    tt, vv = human(e[0], e[2] if len(e) > 2 else .4)
    put(L, R, piano(e[1], vv), tt, pan=(e[1] - 70) / 35)
chord_roll([38, 50, 57, 62], 49.55, .4, .11)                  # 結尾和弦

# 「初心」出現：一聲清亮的鈴
put(L, R, glass(81, .4), 3.2, .1); put(L, R, glass(86, .35), 44.0, .15)
# 第二段：每顆愛心亮起
pent = [74, 76, 78, 81, 83, 86, 88]
for i, tm in enumerate(sorted(json.load(open('times.json')))):
    tt, vv = human(10 + tm + .15, .15 + .07 * (i % 3 == 0), .01, .15)
    put(L, R, glass(pent[(i * 3) % 7], vv), tt, float(rng.uniform(-.7, .7)))
# 第三段：漣漪
for k in range(6):
    put(L, R, glass([86, 81, 83, 81, 86, 78][k], .26), 21 + 2.6 + 1.5 * k, -.35 if k % 2 else .35)
# 第四段：愛心升空的上行琶音（略微加快，像往上飛）
arp = {0: [55, 59, 62, 67, 71, 74, 79], 1: [57, 61, 64, 69, 73, 76, 81], 2: [59, 62, 66, 71, 74, 78, 83]}
tcur = 32.0
for i in range(16):
    c = 0 if tcur < 34 else (1 if tcur < 37 else 2)
    tt, vv = human(tcur, .2 + .018 * i, .01)
    put(L, R, piano(arp[c][i % 7], vv), tt, pan=((i % 7) - 3) * .18)
    tcur += .46 - .012 * i
# 第四段：大提琴旋律線（有揉弦、慢慢漲起來）
def cello(m, t0, length, amp):
    n = int(length * SR); t = np.arange(n) / SR
    vib = 7 * np.sin(2 * np.pi * 5.2 * t) * np.minimum(1, t / 1.2)
    ph = 2 * np.pi * np.cumsum(f(m) * 2 ** (vib / 1200)) / SR
    s = sum(np.sin(k * ph) / k ** 1.3 for k in range(1, 18))
    s = signal.lfilter(*signal.butter(2, 1400 / (SR / 2)), s)
    env = np.minimum(1, t / (length * .45)) ** 1.5 * np.minimum(1, np.maximum(0, (length - t) / .9))
    put(PL, PR, s * env * amp, t0, -.2)
for m, t0, ln in [(43, 31.4, 3.0), (45, 34.2, 3.0), (47, 37.0, 2.8), (45, 39.6, 2.8), (50, 42.2, 7.5)]:
    cello(m, t0, ln, .05)

# ========== 弦樂的明暗：隨段落開合（低通濾波截止頻率隨時間改變）==========
cut_pts = [(0, 700), (10, 900), (20, 1100), (22, 650), (31, 700), (40, 2200), (44, 2600), (52, 1500)]
def tv_lowpass(x):
    y = np.zeros_like(x); blk = 2048; zi = None
    for i in range(0, len(x), blk):
        fc = np.interp(i / SR, *zip(*cut_pts))
        b, a = signal.butter(2, fc / (SR / 2))
        if zi is None: zi = signal.lfilter_zi(b, a) * 0
        y[i:i + blk], zi = signal.lfilter(b, a, x[i:i + blk], zi=zi)
    return y
PL = tv_lowpass(PL); PR = tv_lowpass(PR)

dyn_pts = [(0, 0), (1.2, .55), (10, .6), (20, .72), (22, .5), (31, .5), (40, .95), (44, .9), (49.5, .85), (52, 0)]
g = np.interp(np.arange(N) / SR, *zip(*dyn_pts))
dryL = (L + PL) * g; dryR = (R + PR) * g

# ========== 音樂廳殘響：低頻留得久、高頻散得快 ==========
def hall_ir(seed, length=3.8):
    r = np.random.default_rng(seed); n = int(length * SR); t = np.arange(n) / SR
    ir = np.zeros(n)
    for lo, hi, t60 in [(20, 250, 2.2), (250, 1200, 2.6), (1200, 4000, 1.7), (4000, 12000, .8)]:
        b = signal.butter(2, [lo / (SR / 2), hi / (SR / 2)], 'band', output='sos')
        ir += signal.sosfilt(b, r.standard_normal(n)) * np.exp(-6.91 * t / t60)
    pre = int(.024 * SR); ir = np.concatenate([np.zeros(pre), ir])[:n]
    for d, a in [(.011, .5), (.019, .38), (.027, .3), (.041, .22), (.053, .18)]:   # 早期反射
        ir[int(d * SR) + int(r.uniform(0, 40))] += a * r.choice([-1, 1])
    ir[:int(.006 * SR)] *= np.linspace(0, 1, int(.006 * SR))
    return ir / np.sqrt(np.sum(ir ** 2))
wetL = signal.fftconvolve(dryL, hall_ir(1))[:N]; wetR = signal.fftconvolve(dryR, hall_ir(2))[:N]
mixL = .78 * dryL + .42 * wetL; mixR = .78 * dryR + .42 * wetR

# ========== 母帶：去超低頻、修整低頻與高頻、輕壓縮、軟飽和 ==========
def shelf(x, gain_db, f0, kind):                       # RBJ 擱架式等化
    A = 10 ** (gain_db / 40); w0 = 2 * np.pi * f0 / SR; al = np.sin(w0) / 2 * np.sqrt(2); c = np.cos(w0); sA = 2 * np.sqrt(A) * al
    if kind == 'low':
        b = [A*((A+1)-(A-1)*c+sA), 2*A*((A-1)-(A+1)*c), A*((A+1)-(A-1)*c-sA)]; a = [(A+1)+(A-1)*c+sA, -2*((A-1)+(A+1)*c), (A+1)+(A-1)*c-sA]
    else:
        b = [A*((A+1)+(A-1)*c+sA), -2*A*((A-1)+(A+1)*c), A*((A+1)+(A-1)*c-sA)]; a = [(A+1)-(A-1)*c+sA, 2*((A-1)-(A+1)*c), (A+1)-(A-1)*c-sA]
    return signal.lfilter(b, a, x)
for side in ('L', 'R'):
    v = globals()['mix' + side]; v = shelf(v, -5, 220, 'low'); v = shelf(v, 4.5, 2800, 'high'); globals()['mix' + side] = v
hp = signal.butter(2, 38 / (SR / 2), 'high', output='sos')
mixL = signal.sosfilt(hp, mixL); mixR = signal.sosfilt(hp, mixR)
lvl = np.sqrt(signal.lfilter([1 - np.exp(-1 / (.12 * SR))], [1, -np.exp(-1 / (.12 * SR))], (mixL ** 2 + mixR ** 2) / 2))
ref = np.percentile(lvl[lvl > 1e-6], 90)
gain = np.minimum(1, (np.maximum(lvl, 1e-9) / ref) ** (-.35))       # 2:1 左右的輕壓縮，只壓最大聲的地方
gain = np.where(lvl > ref, gain, 1)
mixL *= gain; mixR *= gain
pk = max(np.abs(mixL).max(), np.abs(mixR).max())
mixL = np.tanh(1.25 * mixL / pk) / np.tanh(1.25); mixR = np.tanh(1.25 * mixR / pk) / np.tanh(1.25)
fade = np.ones(N); fn = int(2.4 * SR); fade[-fn:] = np.linspace(1, 0, fn) ** 1.6
mixL *= fade * .89; mixR *= fade * .89
out = (np.stack([mixL, mixR], 1) * 32767).astype('<i2')
with wave.open('music2.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(out.tobytes())
print('ok')
