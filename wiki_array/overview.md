---
title: 声源定位与阵列处理 Wiki 综述
type: overview
created: 2026-06-21
updated: 2026-06-21
tags:
  - doa-estimation
  - seld
  - microphone-array
  - beamforming
  - spatial-audio
  - deep-learning
---

# 声源定位与阵列处理 Wiki 综述

## 领域概述

本 Wiki 聚焦于**声源定位 (Source Localization)** 与**麦克风阵列处理 (Microphone Array Processing)**，涵盖从传统信号处理方法到深度学习端到端模型的演进路径。

### 方向分支

| 方向 | 核心任务 | 代表架构 | 论文数 |
|---|---|---|---|
| **DOA 估计** | 估计声源方位角/仰角 | CNN相位图 → CRNN → Mamba | 9 |
| **SELD** | 联合声事件检测+定位 | CRNN → Transformer → Mamba | 6 |
| **波束成形** | 空间滤波 + 源分离 | DBnet (端到端) | 1 |
| **基础模型** | 通用空间音频表示 | GRAM (MAE) | 1 |
| **视听定位** | 图像/视频中发声物体定位 | CLIP-driven | 1 |
| **综述/基准** | 评测与全景 | LOCATA, SSL Survey | 3 |

## 架构演进时间线

```
2017 ─ CNN 相位图 (Chakrabarty) ─ CRNN DOAnet (Adavanne)
2018 ─ Multi-Speaker CNN ──── SELD CRNN (奠基)
2019 ─ LOCATA Challenge
2020 ─ DBnet (端到端波束)
2021 ─ PILOT (Transformer) ─ SSL Survey ─ SLoClas DB
2022 ─ ISSL (迭代) ─ MIMO-DoAnet (多输出)
2024 ─ SELD-Mamba (SSM)
2025 ─ CST-former ─ GRAM ─ LAM ─ FA-Stateformer ─ CLIP-SSL
```

## 关键概念

- **DOA 波达方向估计**：从阵列信号估计声源入射方向
- **STFT 相位图**：多通道相位信息的二维组织，端到端空间特征学习
- **SRP-PHAT / MUSIC**：传统基线方法
- **SELD**：Sound Event Localization and Detection，联合检测+定位
- **ACCDOA**：Activity-Coupled Cartesian DOA，SED 与 DOA 的统一表示
- **W-Disjoint Orthogonality**：语音信号在 TF 域的近似不重叠性质
- **Ambisonics (FOA/HOA)**：球谐分解的阵列无关空间音频格式
- **Mamba / SSM**：状态空间模型，O(N) 复杂度的序列建模

## 当前收录

- **Source 页面**：21 篇
- **Concept 页面**：18 个
- **Entity 页面**：2 个
- **时间跨度**：2017–2025

## 待整理

- [ ] 补充 2 篇 PDF 转换失败的论文细节 (2507.01143, 2509.17247)
- [ ] 主题页：DOA 方法演进对比、SELD 架构演进
