---
title: Hybrid Continuity Loss
type: entity
created: 2026-09-16
updated: 2026-09-16
tags:
  - loss
  - speech-preservation
  - over-suppression
  - target-speaker-extraction
  - ASR
sources:
  - [[wiki_low_latency/sources/2022/Hybrid Continuity Loss 2022]]
related:
  - [[wiki_low_latency/sources/2022/Hybrid Continuity Loss 2022]]
  - [[wiki_low_latency/concepts/2203.16843-continuity-loss]]
  - [[wiki/sources/2019/Conv-TasNet - Surpassing Ideal TF Masking 2019]]
---

# Hybrid Continuity Loss

## 概述

Hybrid Continuity Loss 是 Pan、Ge 与 Li 在 2022 年提出的训练目标，用于缓解时域目标说话人提取中的 over-suppression。它把 waveform-level negative SI-SDR 与多分辨率频域 delta spectrum loss 相加：前者维持整体重建质量，后者约束幅度谱、差分谱和 acceleration 谱的时间连续性。

## 组成

$$
\mathcal{L}_{\mathrm{hybrid}}
=\mathcal{L}_{\mathrm{SI-SDR}}
+\gamma\frac{1}{M}\sum_{m=1}^{M}\mathcal{L}^{m}_{\mathrm{freq-\Delta}},
\qquad M=3,\ \gamma=1.
$$

三种分辨率使用 FFT/window/hop：

- 512 / 240 / 50；
- 1024 / 600 / 120；
- 2048 / 1200 / 240。

$\mathcal{L}_{\mathrm{freq-\Delta}}$ 由 spectrum convergence 和 log-magnitude 两项组成，每项都同时比较原始谱、差分特征 $f_D$ 和二阶 acceleration 特征 $f_A=f_D(f_D)$。差分阶数 $L=2$，其定义读取 $v(t+l)$ 与 $v(t-l)$。

## 验证平台

验证模型是音视频时域 speaker extraction：16 kHz mixture waveform 经 $C=256$、kernel 40、stride 20 的 Conv1D 编码；ResNet18 + 5 层 temporal conv 将目标唇部视频编码；二者进入 $R=6$ 个 dual-path LSTM，得到 latent mask，再经 linear + overlap-and-add 输出波形。

在 LRS2-mix 上，Hybrid loss 的 clean 结果为 SI-SDR 13.48、PESQ 3.163、STOI 0.934、audio-visual WER/CER 16.1/6.8；noisy 结果为 SI-SDR 5.12、PESQ 2.276、STOI 0.789、audio-visual WER/CER 34.5/17.7。相对于 SI-SDR loss，over-suppression MAE 下降，但 under-suppression MAE 略增。

## 低时延证据边界

该 loss 不是部署模块。其训练用的中心差分访问未来帧，且 base network 的 dual-path LSTM/global dependency 没有给出严格因果 certificate、状态缓存、运行时 p99 或硬件 deadline。迁移到本 Wiki 时，应把它当作 speech-preservation loss reference，并设计 past-only 版本再测量延迟。

## 关联

- [[wiki_low_latency/sources/2022/Hybrid Continuity Loss 2022]]
- [[wiki_low_latency/concepts/2203.16843-continuity-loss]]
- [[wiki_low_latency/entities/DPCRN]]
- [[wiki_low_latency/entities/DCCRN]]
