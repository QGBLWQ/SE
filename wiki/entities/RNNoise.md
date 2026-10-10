---
title: RNNoise
type: entity
created: 2026-06-05
updated: 2026-06-05
tags:
  - software
  - noise-suppression
  - real-time
  - speech-enhancement
  - mozilla
  - open-source
repo: https://github.com/xiph/rnnoise/
demo: https://people.xiph.org/~jm/demo/rnnoise/
related:
  - [[RNNoise 2018]]
  - [[wiki/concepts/STFT与频谱图]]
  - [[wiki/concepts/语音信号与噪声模型]]
  - [[wiki/concepts/理想比率掩蔽 IRM]]
  - [[wiki/concepts/Bark尺度与临界频带]]
  - [[wiki/concepts/感知加权损失函数]]
  - [[wiki/concepts/实时与离线语音增强]]
  - [[wiki/concepts/语音增强评价指标]]
  - [[wiki/concepts/掩蔽方法全景图]]
---

# RNNoise

## 概述

RNNoise 是 Mozilla 研究员 Jean-Marc Valin 于 2018 年发布的**实时全频带语音增强库**，采用混合 DSP/深度学习架构。它以 BSD 协议开源，是目前最轻量的神经网络语音增强方案之一。

## 核心特性

| 特性         | 详情                          |
| ---------- | --------------------------- |
| **采样率**    | 48 kHz 全频带 (0–20 kHz)       |
| **延迟**     | 10 ms 帧移 + 算法延迟 ~26.5 ms    |
| **复杂度**    | ~40 Mflops                  |
| **模型大小**   | 87,503 权重（8-bit 量化后 ~85 KB） |
| **x86 占用** | ~1.3% 单核 (Haswell i7)       |
| **ARM 占用** | ~14% Cortex-A53 (树莓派 3)     |
| **依赖**     | 无外部深度学习框架（纯 C 推理）           |
| **许可证**    | BSD 3-Clause                |

## 架构

```
Input (48kHz PCM)
    │
    ▼
┌─────────────────┐
│  STFT Analysis  │  20ms Vorbis window, 50% overlap
└────────┬────────┘
         │
    ┌────▼────┐
    │ 42 维   │  BFCC(22) + ΔBFCC(6) + Δ²BFCC(6)
    │ 特征提取 │  + Pitch DCT(6) + Period(1) + Non-stat(1)
    └────┬────┘
         │
    ┌────▼────┐
    │   GRU   │  215 units, 4 hidden layers
    │ Network │  22 gains + 1 VAD
    └────┬────┘
         │
    ┌────▼────┐
    │  Bark   │  22 gains → interpolated to FFT bins
    │  Gain   │  r(k) = Σ w_b(k) · ĝ_b
    └────┬────┘
         │
    ┌────▼────┐
    │  Pitch  │  Comb filter to remove
    │ Filter  │  inter-harmonic noise
    └────┬────┘
         │
    ▼  iSTFT Synthesis  ▼
    Output (48kHz PCM)
```

## 应用场景

- **VoIP / 视频会议**：低延迟、低 CPU 占用
- **直播 / 游戏语音**：实时处理、不依赖 GPU
- **嵌入式设备**：树莓派即可运行
- **浏览器**：官方提供 JavaScript/WebAssembly 演示
- **作为基线**：后续论文中常作为 DSP+DL 混合方案的比较对象

## 与后续方法的关系

RNNoise 代表了 2018 年的"轻量混合方案"标杆。后续发展方向：

> [!note] 对比方向
> - **全深度学习**：Conv-TasNet、DPRNN 等端到端时域方案 → 更强的去噪能力，但复杂度更高
> - **复数域处理**：DCCRN、DPCRN → 保留相位信息，提升语音质量
> - **感知优化**：PercepNet → 进一步优化感知质量而非 MSE

RNNoise 的混合设计思想（DL 替代难调参的估计器，DSP 负责其余部分）至今仍是实时语音增强的重要范式。

## 相关资源

- 论文：[[RNNoise 2018]]
- 源码：<https://github.com/xiph/rnnoise/>
- 在线演示：<https://people.xiph.org/~jm/demo/rnnoise/>
