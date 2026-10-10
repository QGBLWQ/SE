---
title: DOAnet
type: entity
created: 2026-06-21
updated: 2026-06-21
tags:
  - model
  - crnn
  - doa-estimation
  - ambisonics
  - multi-source
related:
  - [[CRNN DOAnet 2017]]
  - [[wiki_array/concepts/DOA 波达方向估计]]
  - [[wiki_array/concepts/Ambisonics FOA]]
---

# DOAnet

## 概述

DOAnet 是 Adavanne, Politis & Virtanen (2017) 提出的**首个基于 CRNN + Ambisonics 的多声源 DOA 估计网络**。它是后续 DCASE SELD 架构的技术雏形。

## 架构

```
FOA 4ch 音频 → STFT (2048-pt, 40ms Hamming, 50% overlap)
                    ↓
      Input Tensor: L×1024×8 (幅度+相位拼接)
                    ↓
      CNN (4层, 3×3 Conv, ReLU, BN, MaxPool) → L×2×N_C
                    ↓  Reshape → L×2N_C
      BiGRU (2层, tanh) → Temporal Features
                    ↓
      ┌─────────────────┐
      ↓                 ↓
   SPS 回归 (FC)    DOA 分类 (CNN+BiGRU+FC → Sigmoid)
  (中间监督)         (432 方向, 球面均匀采样)
```

## 核心特性

| 特性 | 详情 |
|---|---|
| **输入** | FOA 4ch 幅度+相位谱 |
| **中间输出** | SPS (空间伪谱，MUSIC-like) |
| **最终输出** | 432 方向 DOA (10° 分辨率, 方位+仰角) |
| **声源数** | 自动检测 (threshold=0.5) |
| **序列长度** | L=100 帧 (2s) |
| **阵列** | Ambisonics (阵列无关) |

## 意义

- 证明了 CRNN 架构对 DOA 估计的有效性
- 首次使用 Ambisonics 格式实现 3D 定位
- SPS 中间监督的思想影响了后续工作
- 直接催生了 [[SELD CRNN 2018|SELD CRNN (2018)]]

→ [[CRNN DOAnet 2017]]
