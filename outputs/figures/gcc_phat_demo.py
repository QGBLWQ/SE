"""
GCC-PHAT vs Direct Cross-Correlation Visual Demo
=================================================
Shows step-by-step: waveforms → FFT → cross-correlation → GCC-PHAT
"""
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import stft

plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['figure.dpi'] = 120

# ============================================================
# Parameters
# ============================================================
fs = 16000              # sample rate
freqs = [500, 1500, 3000]  # 3 frequencies mixed
duration = 0.025        # 25 ms
tau_true = 4            # true delay in samples
noise_std = 0.15        # noise level

# ============================================================
# Generate Signals
# ============================================================
t = np.arange(0, duration, 1 / fs)
N = len(t)  # 400 samples

# Clean multi-tone signal
s1_clean = np.sum([np.sin(2 * np.pi * f * t) for f in freqs], axis=0)
# Normalize
s1_clean /= np.max(np.abs(s1_clean))

# Mic2: delayed version
s2_clean = np.sum([np.sin(2 * np.pi * f * (t - tau_true / fs)) for f in freqs], axis=0)
s2_clean /= np.max(np.abs(s2_clean))

# Add noise
np.random.seed(42)
s1 = s1_clean + noise_std * np.random.randn(N)
s2 = s2_clean + noise_std * np.random.randn(N)

# ============================================================
# Plot 1: Time-domain waveforms
# ============================================================
fig, axes = plt.subplots(2, 3, figsize=(16, 9))
fig.suptitle("GCC-PHAT vs Direct Cross-Correlation — Full Pipeline Demo",
             fontsize=16, fontweight='bold', y=0.98)

# --- Row 1, Col 1: Both waveforms ---
ax = axes[0, 0]
time_ms = t * 1000
ax.plot(time_ms, s1, alpha=0.85, lw=1.2, label='Mic 1', color='#2196F3')
ax.plot(time_ms, s2, alpha=0.85, lw=1.2, label='Mic 2', color='#FF5722')
ax.set_xlabel('Time (ms)')
ax.set_ylabel('Amplitude')
ax.set_title('Time-Domain Waveforms\n(Mic 1 vs Mic 2, τ = %d samples)' % tau_true)
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)

# --- Row 1, Col 2: Zoomed delay view ---
ax = axes[0, 1]
zoom_start = 100
zoom_end = 180
ax.plot(time_ms[zoom_start:zoom_end], s1[zoom_start:zoom_end],
        'o-', markersize=6, lw=2, label='Mic 1', color='#2196F3')
ax.plot(time_ms[zoom_start:zoom_end], s2[zoom_start:zoom_end],
        's--', markersize=6, lw=2, label='Mic 2', color='#FF5722')
# Mark the delay visually
ax.annotate('', xy=(time_ms[zoom_start + 15 + tau_true], s1[zoom_start + 15]),
            xytext=(time_ms[zoom_start + 15], s1[zoom_start + 15]),
            arrowprops=dict(arrowstyle='->', color='red', lw=2))
ax.text(time_ms[int(zoom_start + 15 + tau_true / 2)], s1[zoom_start + 15] + 0.15,
        'τ', fontsize=14, color='red', fontweight='bold', ha='center')
ax.set_xlabel('Time (ms)')
ax.set_title('Zoomed: Mic 2 delayed by τ')
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)

# --- Row 1, Col 3: Signal composition ---
ax = axes[0, 2]
f_axis_plot = np.fft.rfftfreq(N, 1 / fs)
S_mag = np.abs(np.fft.rfft(s1_clean))
ax.stem(f_axis_plot, S_mag / np.max(S_mag), linefmt='#4CAF50', markerfmt='o', basefmt=' ',
        label='Clean Mic 1')
ax.set_xlim(0, 5000)
ax.set_xlabel('Frequency (Hz)')
ax.set_ylabel('Normalized Magnitude')
ax.set_title('Frequency Components of Signal\n(3 tones: 500 + 1500 + 3000 Hz)')
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)

# ============================================================
# Plot 2: FFT — Magnitude & Phase
# ============================================================
ax_mag = axes[1, 0]
ax_phase = axes[1, 1]

S1 = np.fft.rfft(s1)
S2 = np.fft.rfft(s2)
freqs_fft = np.fft.rfftfreq(N, 1 / fs)

# Magnitude
ax_mag.semilogy(freqs_fft, np.abs(S1), lw=1.2, alpha=0.8, label='Mic 1 |FFT|', color='#2196F3')
ax_mag.semilogy(freqs_fft, np.abs(S2), lw=1.2, alpha=0.8, label='Mic 2 |FFT|', color='#FF5722',
               linestyle='--')
ax_mag.set_xlim(0, 5000)
ax_mag.set_xlabel('Frequency (Hz)')
ax_mag.set_ylabel('Magnitude (log scale)')
ax_mag.set_title('FFT Magnitude Spectrum\n(Mic 1 vs Mic 2 — nearly identical)')
ax_mag.legend(fontsize=8)
ax_mag.grid(True, alpha=0.3)

# Phase
ax_phase.plot(freqs_fft, np.angle(S1), lw=1.2, alpha=0.8, label='Mic 1 phase φ1', color='#2196F3')
ax_phase.plot(freqs_fft, np.angle(S2), lw=1.2, alpha=0.8, label='Mic 2 phase φ2', color='#FF5722',
             linestyle='--')
ax_phase.set_xlim(0, 5000)
ax_phase.set_xlabel('Frequency (Hz)')
ax_phase.set_ylabel('Phase (rad)')
ax_phase.set_title('FFT Phase Spectrum\n(Phase DIFFERENCE encodes τ !)')
ax_phase.legend(fontsize=8)
ax_phase.grid(True, alpha=0.3)

# --- Row 2, Col 1: Phase Difference ---
ax_dphi = axes[1, 2]
delta_phi = np.angle(S2) - np.angle(S1)
# Wrap to [-π, π]
delta_phi = np.arctan2(np.sin(delta_phi), np.cos(delta_phi))

# Theoretical: Δφ = 2πf * τ/fs
theo_phi = 2 * np.pi * freqs_fft * tau_true / fs
theo_phi = np.arctan2(np.sin(theo_phi), np.cos(theo_phi))  # wrap

ax_dphi.plot(freqs_fft, delta_phi, 'o', markersize=4, alpha=0.7, label='Measured Δφ',
             color='#4CAF50')
ax_dphi.plot(freqs_fft, theo_phi, '-', lw=2, alpha=0.8, label='Theory: 2πf·τ', color='#9C27B0')
ax_dphi.set_xlim(0, 5000)
ax_dphi.set_xlabel('Frequency (Hz)')
ax_dphi.set_ylabel('Phase Difference (rad)')
ax_dphi.set_title('Phase Difference Δφ = φ2 - φ1\n(Linear with frequency → encodes τ)')
ax_dphi.legend(fontsize=8)
ax_dphi.grid(True, alpha=0.3)

plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.savefig('F:\\paper\\work!\\outputs\\figures\\gcc_phat_p1_waveform_fft.png',
            dpi=200, bbox_inches='tight')
plt.close()
print("Part 1 saved: waveforms + FFT")

# ============================================================
# Plot 3: Cross-Correlation Comparison
# ============================================================
fig, axes = plt.subplots(1, 3, figsize=(16, 5))
fig.suptitle("Cross-Correlation vs GCC-PHAT — Peak Sharpness Comparison",
             fontsize=15, fontweight='bold')

lags = np.arange(-N + 1, N)

# --- Direct Cross-Correlation ---
ax = axes[0]
corr_direct = np.correlate(s1, s2, mode='full')
corr_direct /= np.max(np.abs(corr_direct))
lag_direct = np.argmax(corr_direct) - N + 1

ax.plot(lags, corr_direct, lw=1.5, color='#2196F3')
ax.axvline(x=lag_direct, color='red', linestyle='--', lw=2,
           label=f'estimated τ = {lag_direct}')
ax.axvline(x=tau_true, color='green', linestyle=':', lw=2,
           label=f'true τ = {tau_true}')
ax.set_xlim(-20, 20)
ax.set_xlabel('Lag (samples)')
ax.set_ylabel('Normalized Correlation')
ax.set_title('Direct Cross-Correlation\nnp.correlate(s1, s2)')
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)

# Mark peak width at half max
peak_val = corr_direct[np.argmax(corr_direct)]
half_max = peak_val / 2
above = np.where(corr_direct > half_max)[0]
if len(above) > 0:
    width = above[-1] - above[0] - 2 * (N - 1)
    ax.text(0.05, 0.12, f'Peak width: ~{abs(width)} samples',
            transform=ax.transAxes, fontsize=9, color='#666',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

# --- GCC-PHAT ---
ax = axes[1]
S1_full = np.fft.fft(s1, n=2 * N)
S2_full = np.fft.fft(s2, n=2 * N)
G = S1_full * np.conj(S2_full)
eps = 1e-6
G_PHAT = G / (np.abs(G) + eps)
corr_phat = np.fft.ifft(G_PHAT)
corr_phat = np.fft.fftshift(corr_phat)  # center at zero lag
corr_phat_real = np.real(corr_phat)
corr_phat_real /= np.max(np.abs(corr_phat_real))
lag_phat = np.argmax(np.abs(corr_phat_real)) - N

lags_phat = np.arange(-N, N)
ax.plot(lags_phat, corr_phat_real, lw=1.5, color='#FF5722')
ax.axvline(x=lag_phat, color='red', linestyle='--', lw=2,
           label=f'estimated τ = {lag_phat}')
ax.axvline(x=tau_true, color='green', linestyle=':', lw=2,
           label=f'true τ = {tau_true}')
ax.set_xlim(-20, 20)
ax.set_xlabel('Lag (samples)')
ax.set_ylabel('Normalized Correlation')
ax.set_title('GCC-PHAT\n(FFT → normalize magnitude → IFFT)')
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)

# --- Side-by-side overlay ---
ax = axes[2]
ax.plot(lags, corr_direct, lw=1.5, alpha=0.7, label='Direct X-Corr', color='#2196F3')
ax.plot(lags_phat, corr_phat_real, lw=1.5, alpha=0.7, label='GCC-PHAT', color='#FF5722')
ax.axvline(x=tau_true, color='green', linestyle=':', lw=2, label=f'true τ = {tau_true}')
ax.set_xlim(-20, 20)
ax.set_xlabel('Lag (samples)')
ax.set_ylabel('Normalized Correlation')
ax.set_title('Overlay Comparison\n(GCC-PHAT peak is SHARPER)')
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('F:\\paper\\work!\\outputs\\figures\\gcc_phat_p2_correlation.png',
            dpi=200, bbox_inches='tight')
plt.close()
print("Part 2 saved: cross-correlation comparison")

# ============================================================
# Plot 4: STFT visualization
# ============================================================
fig, axes = plt.subplots(2, 2, figsize=(14, 8))
fig.suptitle("STFT: Time-Frequency Decomposition", fontsize=15, fontweight='bold')

f_stft, t_stft, Z1 = stft(s1, fs=fs, nperseg=128, noverlap=96)
f_stft, t_stft, Z2 = stft(s2, fs=fs, nperseg=128, noverlap=96)

# Magnitude spectrogram Mic1
ax = axes[0, 0]
im = ax.pcolormesh(t_stft * 1000, f_stft, 20 * np.log10(np.abs(Z1) + 1e-10),
                   shading='gouraud', cmap='inferno')
ax.set_ylabel('Frequency (Hz)')
ax.set_xlabel('Time (ms)')
ax.set_title('Magnitude Spectrogram — Mic 1')
ax.set_ylim(0, 5000)
plt.colorbar(im, ax=ax, label='dB', shrink=0.8)

# Phase spectrogram Mic1
ax = axes[0, 1]
im = ax.pcolormesh(t_stft * 1000, f_stft, np.angle(Z1),
                   shading='gouraud', cmap='twilight', vmin=-np.pi, vmax=np.pi)
ax.set_ylabel('Frequency (Hz)')
ax.set_xlabel('Time (ms)')
ax.set_title('Phase Spectrogram — Mic 1 (φ1)')
ax.set_ylim(0, 5000)
plt.colorbar(im, ax=ax, label='Phase (rad)', shrink=0.8)

# Phase difference spectrogram
ax = axes[1, 0]
dphi_stft = np.angle(Z2) - np.angle(Z1)
dphi_stft = np.arctan2(np.sin(dphi_stft), np.cos(dphi_stft))
im = ax.pcolormesh(t_stft * 1000, f_stft, dphi_stft,
                   shading='gouraud', cmap='RdBu_r', vmin=-np.pi, vmax=np.pi)
ax.set_ylabel('Frequency (Hz)')
ax.set_xlabel('Time (ms)')
ax.set_title('Phase DIFFERENCE Δφ(t,f) = φ2 - φ1\n(Same color = same τ = same θ)')
ax.set_ylim(0, 5000)
plt.colorbar(im, ax=ax, label='Δφ (rad)', shrink=0.8)

# GCC-PHAT heatmap over time (pseudo multi-frame)
ax = axes[1, 1]
# Show GCC-PHAT computed on sliding windows to show time-evolution
hop = 32
win_len = 128
n_frames = (N - win_len) // hop + 1
gcc_frames = np.zeros((n_frames, 2 * win_len))
for i in range(n_frames):
    start = i * hop
    w1 = s1[start:start + win_len] * np.hanning(win_len)
    w2 = s2[start:start + win_len] * np.hanning(win_len)
    S1w = np.fft.fft(w1, n=2 * win_len)
    S2w = np.fft.fft(w2, n=2 * win_len)
    Gw = S1w * np.conj(S2w)
    Gw /= np.abs(Gw) + 1e-6
    gcc_frames[i] = np.abs(np.fft.fftshift(np.fft.ifft(Gw)))

gcc_frames /= np.max(gcc_frames)
# Center 60 lags around zero
lag_center = win_len
lag_range = 30
im = ax.imshow(gcc_frames[:, lag_center - lag_range:lag_center + lag_range].T,
               aspect='auto', origin='lower', cmap='hot',
               extent=[0, n_frames * hop / fs * 1000, -lag_range, lag_range])
ax.axhline(y=tau_true, color='green', linestyle=':', lw=2, label=f'true τ = {tau_true}')
ax.set_xlabel('Time (ms)')
ax.set_ylabel('Lag (samples)')
ax.set_title('GCC-PHAT over Time (Sliding Windows)\n(Bright line at τ = 4 — stable over time)')
ax.legend(fontsize=8)
plt.colorbar(im, ax=ax, label='Normalized |GCC-PHAT|', shrink=0.8)

plt.tight_layout()
plt.savefig('F:\\paper\\work!\\outputs\\figures\\gcc_phat_p3_stft.png',
            dpi=200, bbox_inches='tight')
plt.close()
print("Part 3 saved: STFT visualization")

# ============================================================
# Plot 5: Summary Infographic
# ============================================================
fig, ax = plt.subplots(figsize=(14, 5))
ax.axis('off')

summary = """
                            THREE WAYS TO FIND τ (and thus θ)

 ┌─────────────────────────────────────────────────────────────────────────────────┐
 │                                                                                 │
 │  1. DIRECT CROSS-CORRELATION                                                     │
 │                                                                                 │
 │     s1(t), s2(t) ──→  np.correlate(s1, s2)  ──→  argmax ──→  τ                 │
 │                            │                                                     │
 │                            └── All frequencies mixed together                    │
 │                                Low frequencies dominate (more energy there)      │
 │                                Peak is BROAD → sensitive to noise                │
 │                                                                                 │
 ├─────────────────────────────────────────────────────────────────────────────────┤
 │                                                                                 │
 │  2. GCC-PHAT                                                                     │
 │                                                                                 │
 │     s1(t), s2(t) ──→  FFT ──→  G = S1·S2* ──→  G/|G| ──→  IFFT ──→  argmax ──→ τ  │
 │                                   │            │                                  │
 │                                   └── CPS      └── DROP amplitude                │
 │                                       includes      All frequencies vote EQUALLY │
 │                                       phase diff Δφ   Peak is SHARP              │
 │                                                                                 │
 │     KEY INSIGHT: G/|G| = e^{j·Δφ}  — pure phase difference only!               │
 │                                                                                 │
 ├─────────────────────────────────────────────────────────────────────────────────┤
 │                                                                                 │
 │  3. CHAKRABARTY CNN (Deep Learning DOA)                                          │
 │                                                                                 │
 │     s1...sM ──→  STFT ──→  φ1...φM matrix  ──→  stack ──→  CNN ──→  classify θ │
 │                              │                                                    │
 │                              └── Phase-only (same idea as PHAT!)                 │
 │                                  But: keeps frequency × TIME structure           │
 │                                  CNN learns spatial patterns across all dims     │
 │                                  Naturally handles noise + reverb + multi-source │
 │                                                                                 │
 └─────────────────────────────────────────────────────────────────────────────────┘
"""

ax.text(0.02, 0.98, summary, fontsize=10, fontfamily='monospace',
        verticalalignment='top', transform=ax.transAxes,
        bbox=dict(boxstyle='round', facecolor='#FAFAFA', edgecolor='#333', alpha=0.95))

ax.set_title("Summary: Three Approaches on One Spectrum", fontsize=14, fontweight='bold', pad=20)

plt.tight_layout()
plt.savefig('F:\\paper\\work!\\outputs\\figures\\gcc_phat_p4_summary.png',
            dpi=200, bbox_inches='tight')
plt.close()
print("Part 4 saved: summary infographic")

print("\n=== ALL DONE ===")
print("Generated 4 figures:")
print("  1. gcc_phat_p1_waveform_fft.png — Waveforms + FFT Magnitude/Phase")
print("  2. gcc_phat_p2_correlation.png — Direct X-Corr vs GCC-PHAT peaks")
print("  3. gcc_phat_p3_stft.png — STFT: Magnitude, Phase, Δφ, GCC-PHAT over time")
print("  4. gcc_phat_p4_summary.png — Summary infographic")
