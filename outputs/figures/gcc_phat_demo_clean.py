"""
GCC-PHAT vs 直接互相关 — 精简版可视化
======================================
目标：看懂三种找 τ 的方法的区别
"""
import numpy as np
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.dpi'] = 100

# ============================================================
# 1. 造信号：两路麦克风，人为延迟 5 个采样点
# ============================================================
fs = 16000
f_list = [800, 2000, 3500]   # 3 个频率混合（宽带 → PHAT 才能展示优势）
tau_true = 5

t = np.arange(0, 0.03, 1 / fs)  # 30ms ≈ 480 采样点
N = len(t)

s1_clean = np.sum([np.sin(2 * np.pi * f * t) for f in f_list], axis=0)
s1_clean /= np.max(np.abs(s1_clean))
s2_clean = np.sum([np.sin(2 * np.pi * f * (t - tau_true / fs)) for f in f_list], axis=0)
s2_clean /= np.max(np.abs(s2_clean))

# 加高斯噪声
np.random.seed(42)
noise_level = 0.3
s1 = s1_clean + noise_level * np.random.randn(N)
s2 = s2_clean + noise_level * np.random.randn(N)

# ============================================================
# 2. 计算三种方法
# ============================================================

# --- 方法 1：直接互相关 ---
corr_direct = np.correlate(s1, s2, mode='full')
corr_direct /= np.max(np.abs(corr_direct))
lags_direct = np.arange(-N + 1, N)
lag_direct = np.argmax(corr_direct) - N + 1

# --- 方法 2：GCC-PHAT ---
# 用 2N 点 FFT 做线性卷积（等价于 mode='full' 的互相关）
M = 2 * N
S1 = np.fft.fft(s1, n=M)
S2 = np.fft.fft(s2, n=M)
G = S1 * np.conj(S2)              # 互功率谱
G_PHAT = G / (np.abs(G) + 1e-8)   # PHAT 加权：幅度→1，只留相位
corr_phat = np.fft.ifft(G_PHAT)
corr_phat_abs = np.abs(corr_phat)
corr_phat_abs /= np.max(corr_phat_abs)

# 处理循环移位：ifft 输出 [0..M-1]，后半段是负 lag
corr_phat_abs = np.fft.fftshift(corr_phat_abs)  # 零 lag 移到中心
lags_phat = np.arange(-N, N)                     # 对称的 lag 轴（中心=0）
idx_phat = np.argmax(corr_phat_abs)
lag_phat = lags_phat[idx_phat]

# --- FFT 分析（用 rfft，只看正频率）---
S1_r = np.fft.rfft(s1)
S2_r = np.fft.rfft(s2)
freqs_r = np.fft.rfftfreq(N, 1 / fs)
dphi = np.angle(S2_r) - np.angle(S1_r)
dphi = np.arctan2(np.sin(dphi), np.cos(dphi))  # wrap 到 [-π, π]

# ============================================================
# 3. 画图
# ============================================================
fig, axes = plt.subplots(2, 2, figsize=(13, 9))
fig.suptitle("三种方法找 τ（时延）——从波形到 GCC-PHAT\n"
             f"信号: {f_list} Hz 混合 + 高斯噪声,  真实 τ = {tau_true} 采样点",
             fontsize=14, fontweight='bold')

# --- 图 2.1：两路波形（前 60 个点）---
ax = axes[0, 0]
show_n = 60
ax.plot(t[:show_n] * 1000, s1[:show_n], 'o-', markersize=5, lw=1.5,
        label='Mic1', color='#2196F3')
ax.plot(t[:show_n] * 1000, s2[:show_n], 's--', markersize=5, lw=1.5,
        label='Mic2 (晚 %d 采样点)' % tau_true, color='#FF5722')
mid = 20
ax.annotate('', xy=(t[mid + tau_true] * 1000, s2[mid + tau_true]),
            xytext=(t[mid] * 1000, s1[mid]),
            arrowprops=dict(arrowstyle='<->', color='red', lw=2.5))
ax.text(t[mid + 2] * 1000, s1[mid] + 0.3, 'τ', fontsize=16,
        color='red', fontweight='bold')
ax.set_xlabel('时间 (ms)')
ax.set_ylabel('幅度')
ax.set_title('两路麦克风波形（前 3.75ms）\nMic2 明显比 Mic1 晚到')
ax.legend(loc='upper right')
ax.grid(True, alpha=0.3)

# --- 图 2.2：直接互相关 ---
ax = axes[0, 1]
ax.plot(lags_direct, corr_direct, lw=2, color='#2196F3')
ax.axvline(x=lag_direct, color='red', linestyle='--', lw=2,
           label='估计 τ = %d' % lag_direct)
ax.axvline(x=tau_true, color='green', linestyle=':', lw=3,
           label='真实 τ = %d' % tau_true)
ax.set_xlim(-15, 15)
ax.set_xlabel('位移 (采样点)')
ax.set_ylabel('归一化互相关值')
ax.set_title('方法1：直接互相关\n（峰值宽 → 噪声下不稳定）')
ax.legend(fontsize=9)
ax.grid(True, alpha=0.3)

# --- 图 2.3：FFT 幅度 + 相位差 ---
ax = axes[1, 0]
ax.fill_between(freqs_r, 0, np.abs(S1_r), alpha=0.2, color='#2196F3',
                label='Mic1 幅度谱')
ax.set_xlim(0, 5000)
ax.set_xlabel('频率 (Hz)')
ax.set_ylabel('幅度', color='#2196F3')
ax.tick_params(axis='y', labelcolor='#2196F3')

ax_phi = ax.twinx()
ax_phi.scatter(freqs_r, dphi, s=20, color='#FF5722', alpha=0.6, zorder=5,
               label='实测 Δφ')
# 理论线：Δφ = 2π·f·τ/fs
ax_phi.plot(freqs_r, 2 * np.pi * freqs_r * tau_true / fs,
            '-', color='#9C27B0', lw=2.5, alpha=0.6, label='理论线: 2πfτ')
ax_phi.set_ylabel('相位差 (rad)', color='#FF5722')
ax_phi.tick_params(axis='y', labelcolor='#FF5722')
ax_phi.set_ylim(-np.pi, np.pi)
# 只标注信号频率附近
ax_phi.axhline(y=0, color='gray', lw=0.5, alpha=0.3)

lines1, labels1 = ax.get_legend_handles_labels()
lines2, labels2 = ax_phi.get_legend_handles_labels()
ax.legend(lines1 + lines2, labels1 + labels2, fontsize=8, loc='lower right')
ax.set_title('FFT 结果：幅度谱 + 相位差\n（信号频点处 Δφ 贴近理论线，噪声频点随机散布）')
ax.grid(True, alpha=0.3)

# --- 图 2.4：GCC-PHAT vs 直接互相关（叠加对比）---
ax = axes[1, 1]
ax.plot(lags_direct, corr_direct, lw=1.5, alpha=0.4, label='直接互相关',
        color='#90CAF9')
ax.plot(lags_phat, corr_phat_abs, lw=2.5, color='#FF5722', label='GCC-PHAT')
# 标注峰值
peak_d = np.max(corr_direct)
ax.plot(lag_direct, peak_d, 'o', markersize=9, color='#90CAF9', alpha=0.7)
peak_p = corr_phat_abs[idx_phat]
ax.plot(lag_phat, peak_p, 'D', markersize=12, color='#FF5722', zorder=10)
ax.axvline(x=tau_true, color='green', linestyle=':', lw=3,
           label='真实 τ = %d' % tau_true)
ax.set_xlim(-15, 15)
ax.set_xlabel('位移 (采样点)')
ax.set_ylabel('归一化相关值')
ax.set_title('方法2：GCC-PHAT vs 直接互相关\n（对比：GCC-PHAT 峰值更尖锐）')
ax.legend(fontsize=9)
ax.grid(True, alpha=0.3)

plt.tight_layout(rect=[0, 0, 1, 0.93])
plt.savefig('gcc_phat_clean_demo.png', dpi=200, bbox_inches='tight')
plt.show()
print("=== 完成 ===")
print("信号: %s Hz 混合 + 高斯噪声 σ=%.1f" % (str(f_list), noise_level))
print("真实延迟: %d 采样点 (%.4f ms)" % (tau_true, tau_true / fs * 1000))
print("直接互相关估计: %d" % lag_direct)
print("GCC-PHAT 估计:    %d" % lag_phat)
print("图片已保存: gcc_phat_clean_demo.png")
