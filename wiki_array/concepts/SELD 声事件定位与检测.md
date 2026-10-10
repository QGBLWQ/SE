---
title: SELD 声事件定位与检测
type: concept
created: 2026-06-21
updated: 2026-06-21
tags:
  - seld
  - dcase
  - multi-task
  - sound-event-detection
sources:
  - SELD CRNN 2018
  - PILOT Transformer SEL 2021
  - SELD-Mamba 2024
  - CST-former 2025
  - SSL Survey 2021
related:
  - [[wiki_array/concepts/DOA 波达方向估计]]
  - [[wiki_array/concepts/Ambisonics FOA]]
  - [[wiki_array/concepts/ACCDOA]]
---

# SELD 声事件定位与检测

## 定义

**SELD (Sound Event Localization and Detection)** 是联合任务：在检测到每个声事件的时间起止和类型的同时，估计其空间位置 (DOA)。这是 DCASE Challenge Task 3 的核心任务。

## 两个子任务

| 子任务 | 英文 | 输出 |
|---|---|---|
| **SED** | Sound Event Detection | 每帧 × 每类的活跃概率 (多标签) |
| **DOA** | Direction of Arrival | 每个活跃事件的方位角+仰角 (回归/分类) |

### 关键难点：数据关联 (Data Association)

当多个声事件同时发生时，需要将**哪个 DOA 对应哪个事件类型**正确关联。传统方法（SED 和 DOA 分模块做）需要后处理关联，SELD 则通过**统一网络**在输出层直接解决。

## 两种主流输出格式

### 1. ACCDOA (Activity-Coupled Cartesian DOA)

将 SED 活跃性和 DOA 耦合为一个 3D 向量：

$$\mathbf{v}_{\text{ACCDOA}} = a \cdot \begin{bmatrix} x \\ y \\ z \end{bmatrix}, \quad \|\mathbf{v}\| = a$$

- 向量长度 $a$ = 事件活跃概率
- 向量方向 = DOA
- 非活跃事件 → 零向量

### 2. 双分支输出 (Two-Branch)

两个独立的输出头：SED 分支 (多标签 Sigmoid) + DOA 分支 (回归)，训练时用 SED GT 掩蔽 DOA 输出。

→ 详见 [[ACCDOA]]

## SELD 架构演进

```
2018 ─ CRNN (Adavanne) ★ 奠基
2019 ─ DCASE 基线确立
2020 ─ EINV2 (事件独立网络)
2021 ─ PILOT (Transformer + 概率)
2022 ─ ResNet-Conformer
2024 ─ SELD-Mamba (SSM)
2025 ─ CST-former (多维注意力)
```

## 与本 Wiki 论文的关系

| 论文 | 贡献 |
|---|---|
| [[SELD CRNN 2018]] | 奠基性 CRNN + 回归 DOA |
| [[PILOT Transformer SEL 2021]] | Transformer + 高斯分布输出 |
| [[SELD-Mamba 2024]] | Mamba SSM + 距离估计 |
| [[CST-former 2025]] | Channel-Spectro-Temporal 三维注意力 |
| [[ResNet-Conformer SELD 2025]] | EINV2 + 数据增强 DCASE 实战 |
