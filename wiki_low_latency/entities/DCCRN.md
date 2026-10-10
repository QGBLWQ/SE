---
title: DCCRN
type: entity
created: 2026-09-16
updated: 2026-09-16
tags:
  - model
  - speech-enhancement
  - complex-spectrogram
  - phase-aware
  - recurrent
  - low-latency-reference
sources:
  - [[wiki_low_latency/sources/2020/DCCRN Low-Latency Direction 2020]]
related:
  - [[wiki_low_latency/concepts/2008.00264-complex-phase-enhancement]]
  - [[wiki_low_latency/entities/DPCRN]]
  - [[wiki_low_latency/entities/GCFSnet]]
  - [[wiki_low_latency/index]]
---

# DCCRN

## 简洁定义

DCCRN（Deep Complex Convolution Recurrent Network）是在 CRN 编解码器与 LSTM 时序建模中显式引入复数运算的单通道语音增强模型。它用复数卷积、复数归一化和复数循环建模 noisy complex spectrum，并预测复数掩蔽或复数谱，从而同时处理幅度与相位关系。

## 任务与结构

| 项目 | 论文设置 |
|---|---|
| 输入/输出 | noisy waveform → complex STFT → complex mask/complex spectrum → enhanced waveform |
| 主干 | complex convolutional encoder + recurrent bottleneck + decoder |
| 复数操作 | 实部/虚部交叉乘法、复数归一化，可选 complex LSTM |
| 规模参考 | DCCRN 约 3.7M 参数；不同 DNS 配置另有差异 |
| 时延参考 | 25 ms window、6.25 ms hop；DNS 提交配置报告约 37.5 ms look-ahead |

## 低时延审计

DCCRN 是相位感知和实时增强的重要基线，但原论文的高分配置并不等同于本方向约 2 ms strict-causal 系统。论文报告的 PC 单帧时间与 look-ahead 只约束特定配置，未覆盖目标 SoC 上的 RTF 分布、p99 deadline、I/O buffer、峰值 RAM 或 capture-to-playback 延迟。

## 论文证据（仅本地 PDF）

| PDF 位置 | 直接证据 |
|---|---|
| p. 2 | Figure 1/2 与 Eq. (1)-(9) 给出 complex convolution、CRN 结构和复数掩蔽关系 |
| p. 3 | 复数网络配置、模型规模和训练设置 |
| p. 4 | WSJ0/DNS 结果、DCCRN 变体对比与实时配置 |

论文未提供目标硬件上的端到端 deadline 统计、量化后质量/功耗和低 SNR 人声保留分数；这些字段应在复现或新系统中单独补测。

## 关键消融

论文比较了普通 CRN、DCCRN 的复数卷积/复数 LSTM 变体以及不同掩蔽形式。结果支持：复数交互能改善相位感知建模，但更高的相位建模能力仍可能伴随 speech over-suppression，不能只看 PESQ 或单次平均推理时间。

## 关联页面

- [[wiki_low_latency/sources/2020/DCCRN Low-Latency Direction 2020]]
- [[wiki_low_latency/concepts/2008.00264-complex-phase-enhancement]]
- [[wiki_low_latency/entities/DPCRN]]
- [[wiki_low_latency/entities/GCFSnet]]
- [Local PDF](../../raw/papers/low_latency_causal_se/2008.00264.pdf)
