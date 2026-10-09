# 「初心」配樂：D 大調，溫柔的背景長音＋類鋼琴旋律＋與畫面對拍的鈴聲
import numpy as np, json, wave, sys
SR, DUR = 44100, 52.0
N = int(SR * DUR)
L = np.zeros(N); R = np.zeros(N)
f = lambda m: 440.0 * 2 ** ((m - 69) / 12)
rng = np.random.default_rng(7)

def add(sig, t0, pan=0.0):
    i = int(t0 * SR)
    if i < 0: sig = sig[-i:]; i = 0
    j = min(N, i + len(sig))
    if i >= N or j <= i: return
    s = sig[:j - i]
    L[i:j] += s * np.sqrt((1 - pan) / 2) ; R[i:j] += s * np.sqrt((1 + pan) / 2)

def piano(m, vel=.5, dec=2.6, length=5.0):
    t = np.arange(int(length * SR)) / SR; fr = f(m); s = np.zeros_like(t)
    for h, a in [(1, 1), (2, .45), (3, .22), (4, .1), (5, .05)]:
        s += a * np.sin(2 * np.pi * fr * h * (1 + .0004 * h * h) * t) * np.exp(-t * (1 + h * .7) / dec)
    att = np.minimum(1, t / .006)
    return vel * .22 * s * att

def bell(m, vel=.3, length=5.0):
    t = np.arange(int(length * SR)) / SR; fr = f(m)
    s = np.sin(2*np.pi*fr*t)*np.exp(-t/1.8) + .35*np.sin(2*np.pi*fr*2.76*t)*np.exp(-t/.9) + .18*np.sin(2*np.pi*fr*5.4*t)*np.exp(-t/.4)
    return vel * .16 * s * np.minimum(1, t / .003)

# ---- 背景長音（和弦）----
chords = [  # (開始, 結束, 和弦音)
    (0, 5.2, [50, 62, 66, 69]), (5.0, 10.2, [47, 62, 66, 71]),          # D, Bm      回望初心
    (10, 13.7, [43, 62, 67, 71]), (13.5, 17.2, [50, 62, 66, 69]), (17, 21.2, [45, 61, 64, 69]),  # G D A  看見付出
    (21, 26.2, [47, 62, 66, 71]), (26, 31.2, [43, 62, 67, 71]),        # Bm, G      重新省思
    (31, 34.2, [43, 62, 67, 71]), (34, 37.2, [45, 61, 64, 69]), (37, 39.7, [47, 62, 66, 71]), (39.5, 42.2, [45, 61, 64, 69]),  # 再次出發
    (42, 52, [50, 62, 66, 69, 74]),                                     # D          預留時間
]
def dyn(t):  # 整體強弱：回望輕、付出漸暖、省思收、出發推高、結尾明亮後淡出
    pts = [(0, .0), (1.5, .5), (10, .55), (20, .68), (22, .45), (31, .45), (40, .9), (44, .85), (49.5, .8), (52, 0)]
    xs, ys = zip(*pts); return np.interp(t, xs, ys)
for a, b, notes in chords:
    n = int((b - a + 1.6) * SR); t = np.arange(n) / SR; T = b - a + 1.6
    env = np.minimum(1, t / 1.4) * np.minimum(1, np.maximum(0, (T - t) / 1.6))
    for k, m in enumerate(notes):
        fr = f(m); amp = (.10 if m < 55 else .055)
        s = sum(np.sin(2*np.pi*fr*d*t + rng.random()*6) for d in (0.9985, 1.0, 1.0015)) / 3
        s += .25 * np.sin(2*np.pi*fr*2*t) * (m < 55)
        add(amp * s * env * (1 + .08*np.sin(2*np.pi*.15*t + k)), a - .2, pan=(k - 1.5) * .25)

# ---- 旋律（類鋼琴）----
mel = [(1.0, 66), (2.2, 69), (3.2, 74, .7), (4.6, 73), (5.6, 71), (6.4, 69, .6), (7.4, 66), (8.6, 64), (9.4, 66),
       (11.0, 74), (12.4, 76), (13.6, 78, .6), (15.5, 76), (17.0, 74, .6), (18.0, 73), (19.5, 69),
       (22.0, 71, .55), (23.2, 69), (26.8, 66, .55), (27.8, 67), (28.8, 69), (30.0, 71),
       (36.0, 78, .7), (37.4, 81, .75), (38.6, 79), (39.8, 78), (40.8, 76),
       (42.4, 74), (43.6, 78), (44.0, 81, .7), (45.4, 78), (46.6, 76), (47.0, 74, .6), (48.4, 73), (49.6, 74, .7)]
for e in mel:
    t0, m = e[0], e[1]; v = e[2] if len(e) > 2 else .45
    add(piano(m, v), t0, pan=(m - 72) / 30)
add(piano(62, .5, 4, 6), 49.6); add(piano(50, .45, 4, 6), 49.6)     # 結尾的低音落定
add(bell(81, .45), 3.2); add(bell(86, .4), 44.0)                     # 「初心」出現時的鈴聲

# ---- 第二段：每顆愛心亮起，響起一個輕鈴（D 大調五聲音階）----
pent = [74, 76, 78, 81, 83, 86, 88]
times = sorted(json.load(open('times.json')))
for i, t in enumerate(times):
    add(bell(pent[(i * 3) % len(pent)], .16 + .1 * (i % 3 == 0)), 10 + t + .15, pan=float(rng.uniform(-.6, .6)))

# ---- 第三段：漣漪擴散時，落下水滴般的高音 ----
for k in range(6):
    add(bell([86, 81, 83, 81, 86, 78][k], .3), 21 + 2.6 + 1.5 * k, pan=(-.3 if k % 2 else .3))

# ---- 第四段：愛心升空，上行琶音 ----
arp = {0: [67, 71, 74, 79], 1: [69, 73, 76, 81], 2: [71, 74, 78, 83]}
for i in range(14):
    t0 = 32.0 + i * .42; c = 0 if t0 < 34 else (1 if t0 < 37 else 2)
    add(piano(arp[c][i % 4] - (12 if i < 4 else 0), .28 + .02 * i, 1.6, 3), t0, pan=((i % 4) - 1.5) * .3)

# ---- 強弱與殘響 ----
g = dyn(np.arange(N) / SR); L *= g; R *= g
def reverb(x, seed):
    n = int(2.8 * SR); t = np.arange(n) / SR
    ir = np.random.default_rng(seed).standard_normal(n) * np.exp(-t / .75); ir[:int(.02*SR)] = 0
    m = 1 << int(np.ceil(np.log2(len(x) + n)))
    y = np.fft.irfft(np.fft.rfft(x, m) * np.fft.rfft(ir, m), m)[:len(x)]
    return y / (np.abs(ir).sum() ** .5 * 6)
L2 = .72 * L + .45 * reverb(L, 1); R2 = .72 * R + .45 * reverb(R, 2)
fade = np.ones(N); fn = int(2.2 * SR); fade[-fn:] = np.linspace(1, 0, fn) ** 1.5
L2 *= fade; R2 *= fade
peak = max(np.abs(L2).max(), np.abs(R2).max()); L2 *= .89 / peak; R2 *= .89 / peak
out = np.stack([L2, R2], 1); out = (out * 32767).astype('<i2')
with wave.open('music.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(out.tobytes())
print('ok', out.shape[0] / SR, 's  peak', peak)
