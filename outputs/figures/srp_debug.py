"""SRP-PHAT debug — 宽带信号 + 正确符号"""
import numpy as np
from scipy.signal import butter, filtfilt

fs = 16000; c = 343; d = 0.04
theta_true = 30
theta_rad = np.radians(theta_true)
dur = 0.1
t = np.arange(0, dur, 1/fs)
N = len(t)

# 宽带源信号
np.random.seed(42)
src = np.random.randn(N)
b, a = butter(4, [400/(fs/2), 4000/(fs/2)], btype='band')
src = filtfilt(b, a, src)
src /= np.std(src)

# mic 0 at x=0, mic 1 at x=d
# tau = -x*sin(θ)/c: mic 1 closer → negative delay → signal EARLIER
tau0, tau1 = 0, -d * np.sin(theta_rad) / c

def delay_sig(sig, tau, fs):
    """线性插值延迟"""
    s = tau * fs
    si = int(np.floor(s))
    sf = s - si
    out = np.roll(sig, -si)
    if sf != 0:
        out = (1-abs(sf))*out + abs(sf)*np.roll(out, -1)
    return out

s0_clean = delay_sig(src, tau0, fs)
s1_clean = delay_sig(src, tau1, fs)
np.random.seed(42)
s0 = s0_clean + 0.05 * np.random.randn(N)
s1 = s1_clean + 0.05 * np.random.randn(N)

# 直接互相关验证
corr = np.correlate(s0, s1, mode='full')
corr /= np.max(np.abs(corr))
lag = np.argmax(corr) - N + 1
exp_lag = abs(tau1) * fs
print(f"Direct XC lag: {lag},  expected ~{exp_lag:.1f}")
print("(s1 EARLIER than s0 → positive lag means s0 delayed relative to s1)")

# GCC-PHAT + SRP-PHAT
Nfft = 512
start = N//4
seg0, seg1 = s0[start:start+Nfft], s1[start:start+Nfft]
X0 = np.fft.fft(seg0)
X1 = np.fft.fft(seg1)
freqs = np.fft.fftfreq(Nfft, 1/fs)

mask = (freqs > 400) & (freqs < 4500)
fm = freqs[mask]
G = X0 * np.conj(X1)
Gph = G / (np.abs(G) + 1e-8)

scores = {}
for th in range(-90, 91, 5):
    th_r = np.radians(th)
    tau_t = d * np.sin(th_r) / c
    # FIXED: + sign (matches SRP-PHAT formula)
    phase_t = np.exp(1j * 2 * np.pi * fm * tau_t)
    scores[th] = np.real(np.sum(Gph[mask] * phase_t))

# 标准化 & 找最大值
s_arr = np.array(list(scores.values()))
s_arr /= np.max(np.abs(s_arr))
best = list(scores.keys())[np.argmax(s_arr)]
print(f"\nTop scores:")
for th in sorted(scores, key=lambda x: scores[x], reverse=True)[:5]:
    print(f"  θ={th:3d}°: {scores[th]:.1f}")
print(f"\nBest: θ={best}°  (true={theta_true}°)")
