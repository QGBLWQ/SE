---
title: ACCDOA 活动耦合笛卡尔 DOA
type: concept
created: 2026-06-21
updated: 2026-06-21
tags:
  - seld
  - output-format
  - dcase
sources:
  - SELD-Mamba 2024
  - ResNet-Conformer SELD 2025
  - CST-former 2025
related:
  - [[wiki_array/concepts/SELD 声事件定位与检测]]
---

# ACCDOA 活动耦合笛卡尔 DOA

## 定义

**ACCDOA (Activity-Coupled Cartesian DOA)** 是由 Shimada et al. 提出的 SELD 统一输出格式，将声事件检测 (SED) 和 DOA 估计融合为**单一 3D 向量**。

## 数学形式

$$\mathbf{v}_{\text{ACCDOA}} = a \cdot \mathbf{u}_{\text{DOA}} = a \cdot \begin{bmatrix} \cos\phi \cos\lambda \\ \sin\phi \cos\lambda \\ \sin\lambda \end{bmatrix}$$

- $a \in [0, 1]$：事件活跃概率 (来自 SED)
- $\mathbf{u}_{\text{DOA}}$：单位球面上的 DOA 方向向量
- $\|\mathbf{v}\| = a$：**向量的长度 = 活跃性，方向 = DOA**
- 非活跃事件 → $\mathbf{v} = \mathbf{0}$

## 为什么优于分离输出

| 分离输出 (SED + DOA 两个分支) | ACCDOA |
|---|---|
| 需要后处理关联 SED 和 DOA | **天然耦合**，无需关联 |
| 同类多实例难处理 | multi-ACCDOA 支持多实例 |
| SED 为空时 DOA 无意义 | 零向量直接表示无活动 |

## Multi-ACCDOA

使用 ADPIT (Auxiliary Duplicating Permutation Invariant Training) 训练，每个 track 独立输出一个 ACCDOA 向量：

$$\{\mathbf{v}_1, \mathbf{v}_2, ..., \mathbf{v}_N\}$$

- 支持**同一类声事件的多个实例**（如两个人同时说话）
- 通过置换不变训练解决 track 间顺序歧义

## 应用

| 论文 | 使用 |
|---|---|
| DCASE 2023/2024 基线 | multi-ACCDOA 标准输出 |
| [[SELD-Mamba 2024]] | SED + DOA + SDE 三任务 |
| [[ResNet-Conformer SELD 2025]] | EINV2 + multi-ACCDOA |
| [[CST-former 2025]] | ACCDOA + VTM/CTAI 优化 |

→ [[SELD 声事件定位与检测]]
