---
title: Conv-TasNet
type: entity
created: 2026-06-05
tags:
  - software
  - speech-separation
  - source-separation
  - time-domain
  - tcn
  - end-to-end
repo: https://github.com/naplab/Conv-TasNet
related:
  - "[[Conv-TasNet 2019]]"
  - "[[STFT与频谱图]]"
  - "[[掩蔽方法全景图]]"
  - "[[理想比率掩蔽 IRM]]"
  - "[[RNNoise]]"
  - "[[wiki/concepts/扩张卷积 Dilated Convolution]]"
---

# Conv-TasNet

## 概述

Conv-TasNet 是哥伦比亚大学 Mesgarani 实验室于 2019 年提出的**全卷积时域语音分离网络**，是首个**超越理想时频掩蔽（IRM/IBM/WFM）**的语音分离系统。

它完全抛弃了 STFT，直接在**原始波形域**进行分离，用可学习的卷积编码器替代 STFT，用**时序卷积网络（TCN）**替代 LSTM。

## 核心特性

| 特性 | 详情 |
|---|---|
| **采样率** | 8 kHz |
| **编码器段长** | 2 ms（16 samples）← 极短 |
| **编码器维数** | 512（过完备表示） |
| **分离模块** | TCN：8 个扩张卷积块 × 3 组重复 |
| **参数量** | 5.1M |
| **非因果 SI-SNRi** | 15.3 dB（2 说话人） |
| **因果 SI-SNRi** | 10.6 dB（2 说话人） |
| **实时处理** | 是，CPU TPF = 0.4ms |
| **超越 oracle？** | ✅ 超越 IRM, IBM, WFM |

## 架构

```
   Input waveform
        │
   ┌────▼────┐
   │ Encoder │  1-D Conv, L=2ms, 512 basis
   │  xU = w  │  Linear, no ReLU
   └────┬────┘
        │  w ∈ R^{512 × T}
   ┌────▼────┐
   │   TCN   │  Stacked dilated 1-D conv blocks
   │  masks  │  8 blocks × 3 repeats
   │   m_i   │  Depthwise separable conv
   └────┬────┘
        │  m_i ∈ R^{512 × T}
   ┌────▼────┐
   │  Mask   │  d_i = w ⊙ m_i
   └────┬────┘
        │
   ┌────▼────┐
   │ Decoder │  Transposed 1-D Conv
   │  d_i V  │
   └────┬────┘
        │
   Separated waveforms
```

## 与 RNNoise 的关键区别

| | RNNoise (2018) | Conv-TasNet (2019) |
|--|---------------|-------------------|
| **域** | STFT 频域 | **波形域** |
| **特征** | 手工设计的 BFCC | **自动学习的基函数** |
| **网络** | 215 单元 GRU | 5.1M 参数 TCN |
| **任务** | 语音增强（去噪） | 语音分离（分说话人） |
| **相位** | 不处理 | **隐式编码相位** |

## 影响力

Conv-TasNet 是一个**范式转移**性的工作，其核心思想（可学习编码器 + 时域掩蔽 + TCN）启发了后续大量工作，包括 DPRNN（2020）、SepFormer（2021）等。

## 相关资源

- 论文：[[Conv-TasNet 2019]]
- 源码：<https://github.com/naplab/Conv-TasNet>
- 音频样例：<http://naplab.ee.columbia.edu/tasnet.html>
