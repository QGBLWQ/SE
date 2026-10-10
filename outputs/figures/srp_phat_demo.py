"""
SRP-PHAT 可视化 Demo（向量化版，秒出）
=====================================
4 麦 ULA, d=4cm, 宽带信号, 声源在 30°
"""
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt

plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

fs = 16000; c = 343; d = 0.04; M = 4
theta_true = 30; thr = np.radians(theta_true)
dur = 0.1; t = np.arange(0, dur, 1/fs); N = len(t)
Nfft = 512
mic_x = np.arange(M) * d  # [0, d, 2d, 3d]

# 宽带信号
np.random.seed(42)
src = np.random.randn(N)
b, a = butter(4, [400/(fs/2), 4000/(fs/2)], btype='band')
src = filtfilt(b, a, src); src /= np.std(src)

# 信号生成：tau_m = -x_m*sin(θ)/c（mic 在 +x 侧离声源更近 → 提前到达）
signals = np.zeros((M, N))
for m in range(M):
    shift = int(np.round(-mic_x[m] * np.sin(thr) / c * fs))
    signals[m] = np.roll(src, shift)
    signals[m] += 0.05 * np.random.randn(N)

# FFT
seg = signals[:, N//4:N//4+Nfft]
X = np.fft.rfft(seg, axis=1)
fr = np.fft.rfftfreq(Nfft, 1/fs)
m = (fr > 400) & (fr < 4500)
fm = fr[m]
nf = len(fm)

# 所有 mic 对的 GCC-PHAT + 预计算
pairs = [(i, j) for i in range(M) for j in range(i+1, M)]
Gph_all = np.zeros((len(pairs), nf), dtype=complex)
dx_all = np.array([mic_x[j] - mic_x[i] for i, j in pairs])  # (6,)

for p, (i, j) in enumerate(pairs):
    G = X[i] * np.conj(X[j])
    Gph_all[p] = (G[m] / (np.abs(G[m]) + 1e-8))

# 向量化 SRP-PHAT 扫描
thetas = np.arange(-90, 91, 2)        # 每 2° 扫一次
P = np.zeros(len(thetas))
for ti, th in enumerate(thetas):
    th_r = np.radians(th)
    # 每个 mic 对的理论相位: exp(-j*2πf * dx*sin(θ)/c)
    for p in range(len(pairs)):
        tau_t = dx_all[p] * np.sin(th_r) / c
        phase_t = np.exp(-1j * 2 * np.pi * fm * tau_t)
        P[ti] += np.real(np.sum(Gph_all[p] * phase_t))

P /= np.max(P)
best_idx = np.argmax(P)

# ============================================================
# 画图
# ============================================================
fig, axes = plt.subplots(1, 3, figsize=(15, 5.5))
fig.suptitle(f"SRP-PHAT 波束扫描演示 — {M}麦 ULA, d={d*100:.0f}cm, 宽带信号, 真实 θ={theta_true}°",
             fontsize=14, fontweight='bold')

# --- 图 1：阵列几何 ---
ax = axes[0]
ax.plot(mic_x * 100, np.zeros(M), 'o', markersize=22, color='#2196F3', zorder=5)
for mi in range(M):
    ax.text(mic_x[mi]*100, 0.07, f'Mic{mi+1}', ha='center', color='#1565C0', fontsize=10)
ax.annotate('', xy=(mic_x.mean()*100, 0),
            xytext=(mic_x.mean()*100 - 1.2*np.sin(thr), 1.2*np.cos(thr)),
            arrowprops=dict(arrowstyle='->', color='#FF5722', lw=2.5))
arc_r = 0.35; arc_a = np.linspace(0, thr, 30)
ax.plot(mic_x.mean()*100 - arc_r*np.sin(arc_a), arc_r*np.cos(arc_a), '-', color='#FF5722', lw=2)
ax.text(mic_x.mean()*100 - 0.18, 0.22, f'θ={theta_true}°', fontsize=12, color='#FF5722', fontweight='bold')
ax.axhline(y=0, color='gray', alpha=0.3)
ax.set_xlim(-1, 14); ax.set_ylim(-0.2, 1.4); ax.set_aspect('equal')
ax.set_xlabel('x (cm)'); ax.set_title('阵列几何 + 声源方向'); ax.grid(True, alpha=0.3)

# --- 图 2：P(θ) 扫描 ---
ax = axes[1]
ax.plot(thetas, P, lw=2.5, color='#4CAF50')
ax.axvline(x=theta_true, color='red', linestyle='--', lw=2, label=f'真实 θ={theta_true}°')
ax.plot(thetas[best_idx], P[best_idx], 'D', markersize=12, color='#FF5722', zorder=10,
        label=f'估计 θ={thetas[best_idx]}°')
ax.set_xlabel('候选角度 θ (°)'); ax.set_ylabel('归一化 P(θ)')
ax.set_title(f'SRP-PHAT 扫描功率谱\n峰值 → DOA = {thetas[best_idx]}°')
ax.legend(fontsize=10); ax.grid(True, alpha=0.3)

# --- 图 3：SRP-PHAT 工作原理 ---
ax = axes[2]
ax.axis('off')
summary = (
    "SRP-PHAT 工作原理\n"
    "══════════════════\n\n"
    "1. 对所有 mic 对 (i,j)，计算 GCC-PHAT\n"
    "    实际测量相位差 = arg(Xi·Xj*)\n"
    "    PHAT 白化: ÷|Xi·Xj*| → 只留相位\n\n"
    "2. 枚举候选角度 θ，对每个 θ：\n"
    "    理论相位差 = 2πf·(xj-xi)·sin(θ)/c\n"
    "    匹配度 = Σ 实测相位 · 理论相位\n\n"
    "3. P(θ) = 所有 mic 对 + 所有频率的\n"
    "    匹配度之和\n\n"
    "4. 峰值 → DOA 估计\n"
    "    (θ 猜对时全频段一致，\n"
    "     θ 猜错时各频段互相抵消)"
)
ax.text(0.05, 0.95, summary, fontsize=11, fontfamily='monospace',
        verticalalignment='top', transform=ax.transAxes,
        bbox=dict(boxstyle='round', facecolor='#FAFAFA', edgecolor='#333', alpha=0.9))

plt.tight_layout()
plt.savefig('srp_phat_demo.png', dpi=200, bbox_inches='tight')
print(f"真实: {theta_true}°, SRP-PHAT 估计: {thetas[best_idx]}°")
print("图片已保存: srp_phat_demo.png")
