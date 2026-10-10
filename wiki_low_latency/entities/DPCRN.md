---
title: DPCRN
type: entity
created: 2026-09-16
updated: 2026-09-16
tags:
  - model
  - speech-enhancement
  - complex-spectrogram
  - dual-path
  - recurrent
  - low-latency-reference
sources:
  - [[wiki_low_latency/sources/2021/DPCRN Low-Latency Direction 2021]]
related:
  - [[wiki_low_latency/concepts/2107.05429-dual-path-recurrent-context]]
  - [[wiki_low_latency/entities/DCCRN]]
  - [[wiki_low_latency/entities/On-TasNet]]
  - [[wiki_low_latency/index]]
---

# DPCRN

## 简洁定义

DPCRN（Dual-Path Convolution Recurrent Network）是在复数谱 CRN 上加入 dual-path recurrent block 的单通道语音增强模型：intra-chunk 路径沿单帧频率/通道维建模，inter-chunk 路径沿时间块递归，从而把局部谱细节和较长时间上下文分开处理。

## 任务与结构

| 项目 | 论文设置 |
|---|---|
| 输入/输出 | noisy complex STFT → complex ratio mask → enhanced complex STFT |
| 前端 | 16 kHz；25 ms window；12.5 ms hop；FFT 400；201 维复数谱 |
| 主干 | causal Conv/Transposed-Conv + 2 个 DPRNN block |
| RNN hidden | 128；约 0.8M 参数 |
| 运行时参考 | TensorFlow 单帧约 8.9 ms、约 7.45 GFLOPS（i5-6300HQ） |

## 低时延审计

作者明确用 inter-chunk LSTM 保持时间递归；intra-chunk BiLSTM 沿频率/通道维而不是未来时间帧，因此结构上支持时间因果。但 25 ms window、12.5 ms hop 和论文报告的 37.5 ms total latency 远高于本方向约 2 ms 硬约束，且单帧 timing 不是 p99 deadline 证据。

## 论文证据（仅本地 PDF）

| PDF 位置 | 直接证据 |
|---|---|
| p. 2 | Figure 1 和正文给出 CRN encoder/decoder、intra-chunk BiLSTM 与 inter-chunk LSTM 的轴向分工；论文称时间路径保证 strict causality |
| p. 3 | 25 ms window、12.5 ms hop、FFT 400、201 维 complex spectrum；2 个 DPRNN、hidden dimension 128、约 0.8M 参数 |
| p. 4, Tables 1-4 | DPCRN-2 的 WSJ0、DNSMOS、P.835 结果；约 7.45 GFLOPS 与 8.9 ms/frame |

PDF 未报告 RTF、p50/p95/p99、deadline miss、ADC/DAC、峰值 RAM/SRAM、功耗、量化部署或长流 state reset；因此这些指标不能从参数量或一次单帧时间推断。

## 关键消融

DPCRN-2 在负 SNR loss 之外加入 real/imag/magnitude spectral MSE，在 WSJ0-MUSAN 上 PESQ 2.85、STOI 92.02%、SDR 10.99 dB；降低频率分辨率并增大 intra-chunk hidden 的 DPCRN-3 质量下降，说明谱细节对人声保留重要。

## 关联页面

- [[wiki_low_latency/sources/2021/DPCRN Low-Latency Direction 2021]]
- [[wiki_low_latency/concepts/2107.05429-dual-path-recurrent-context]]
- [[wiki_low_latency/entities/DCCRN]]
- [[wiki_low_latency/sources/2023/FSB-LSTM 2023]]
- 原始证据：[Local PDF](../../raw/papers/low_latency_causal_se/2107.05429.pdf)
