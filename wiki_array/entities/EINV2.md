---
title: EINV2 事件独立网络 V2
type: entity
created: 2026-06-21
updated: 2026-06-21
tags:
  - model
  - seld
  - backbone
  - conformer
  - dcase
related:
  - [[SELD-Mamba 2024]]
  - [[ResNet-Conformer SELD 2025]]
  - [[wiki_array/concepts/SELD 声事件定位与检测]]
---

# EINV2 (Event Independent Network V2)

## 概述

EINV2 是 DCASE SELD 任务中广泛使用的**骨干网络架构**。核心设计理念是"事件独立"：每个 sound event track 有独立的处理分支，通过软参数共享 (soft parameter sharing) 协作。

## 架构

```
多通道音频特征
      ↓
┌─────────────────┐
│  Conv Encoder   │ (共享)
└────────┬────────┘
         ↓
┌─────────────────┐
│  Track-wise     │ 每个 track 独立
│  Conformer      │ Conv + MHSA + FFN
│  (多分支)       │
└────────┬────────┘
         ↓
┌─────────────────┐
│  Decoder输出    │ SED / DOA / SDE (多任务)
└─────────────────┘
```

## 关键设计

| 组件 | 作用 |
|---|---|
| **Conv Encoder** | 共享的时频特征提取 |
| **Track-wise Conformer** | 每个事件 track 独立建模 |
| **Soft Parameter Sharing** | 任务间梯度互不影响但有信息交互 |
| **MHSA** | 多尺度通道间注意力 |

## 变体与改进

不同论文在 EINV2 框架上的修改：

| 论文 | 修改 |
|---|---|
| EINV2 原始 | Conv-Conformer, 2-track |
| [[SELD-Mamba 2024]] | Conformer → **BMamba** |
| [[ResNet-Conformer SELD 2025]] | + multi-scale channel attention + split-phase training |
| [[CST-former 2025]] | 另起 CST-former 架构，部分借鉴 track-wise 思路 |

## 与事件关联输出的关系

EINV2 的 track-wise 设计天然适合 **multi-ACCDOA** 输出——每个 track 输出一个 ACCDOA 向量，不同 track 覆盖不同的同时活跃事件。

→ [[SELD 声事件定位与检测]]
→ [[ACCDOA]]
