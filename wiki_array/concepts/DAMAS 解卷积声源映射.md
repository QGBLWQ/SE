---
title: DAMAS 解卷积声源映射
type: concept
created: 2026-06-21
updated: 2026-06-21
tags:
  - acoustic-mapping
  - deconvolution
  - beamforming
  - compressive-sensing
sources:
  - LAM Self-Supervised DOA 2025
  - SSL Survey 2021
related:
  - [[wiki_array/concepts/波束成形 Beamforming]]
  - [[wiki_array/concepts/DOA 波达方向估计]]
---

# DAMAS 解卷积声源映射 (Deconvolution Approach for the Mapping of Acoustic Sources)

## 定义

**DAMAS** 是一种后处理解卷积方法，用于从常规波束成形输出的**模糊声源图中恢复高分辨率声源分布**。它通过在空间域做迭代解卷积来补偿阵列的波束图扩展效应。

## 为什么需要 DAMAS

DAS 波束成形的输出 $\mathbf{b}$ 是真实声源分布 $\mathbf{s}$ 与阵列波束图 $\mathbf{A}$ 的卷积：

$$\mathbf{b} = \mathbf{A} \mathbf{s} + \mathbf{n}$$

- $\mathbf{b}$：DAS 输出（模糊的声源图）
- $\mathbf{A}$：阵列的点扩散函数 (PSF)，取决于阵列几何和频率
- $\mathbf{s}$：真实空间声源分布（稀疏）
- DAMAS 的目标：从 $\mathbf{b}$ 反解出 $\mathbf{s}$

## 求解方法

DAMAS 通过迭代优化求解，利用声源**空间稀疏性**：

$$\min_{\mathbf{s} \geq 0} \|\mathbf{b} - \mathbf{A}\mathbf{s}\|^2 + \lambda\|\mathbf{s}\|_1$$

- 非负约束（声源能量 ≥ 0）
- $\ell_1$ 正则化促进稀疏解
- 迭代求解器（Gauss-Seidel, PGD）

## DAMAS 在深度学习中的角色

| 方法 | DAMAS 的角色 |
|---|---|
| **DeepWave** | 用 DAMAS 标签训练 CNN，但有标签质量上限 |
| **LAM (2025)** | **自监督替代**——不用 DAMAS 标签，直接从原始数据学习 |

[[LAM Self-Supervised DOA 2025|LAM]] 的核心论点：DAMAS 生成的标签质量限制了有监督方法的上限，自监督可以直接突破这个限制。

## 局限

- **迭代计算慢**——不适合实时应用
- 收敛速度依赖初始化和参数
- 对阵列校准误差敏感

→ [[波束成形 Beamforming]]
→ [[LAM Self-Supervised DOA 2025]]
