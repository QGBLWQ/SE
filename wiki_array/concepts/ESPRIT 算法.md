---
title: ESPRIT 算法
type: concept
created: 2026-06-21
updated: 2026-06-21
tags:
  - doa-estimation
  - subspace-method
  - traditional-method
sources:
  - SSL Survey 2021
related:
  - [[wiki_array/concepts/MUSIC 算法]]
  - [[wiki_array/concepts/DOA 波达方向估计]]
---

# ESPRIT 算法 (Estimation of Signal Parameters via Rotational Invariance Technique)

## 定义

**ESPRIT** 是由 Roy & Kailath (1989) 提出的子空间 DOA 估计方法，与 MUSIC 同为经典高分辨率算法。核心差异：ESPRIT 利用阵列的**平移不变结构**直接求解 DOA，**无需全空间谱峰搜索**。

## 核心原理

将阵列分为两个**完全相同的子阵列**，利用子阵列间的旋转不变性：

$$\mathbf{A}_2 = \mathbf{A}_1 \mathbf{\Phi}$$

其中 $\mathbf{\Phi} = \text{diag}(e^{j\omega_1}, ..., e^{j\omega_D})$ 编码了各声源的 DOA 信息（$\omega_i = 2\pi\frac{d}{\lambda}\sin\theta_i$）。

通过求解 $\mathbf{\Phi}$ 的特征值直接得到 DOA：

$$\hat{\theta}_i = \arcsin\left(\frac{\lambda \cdot \angle\phi_{ii}}{2\pi d}\right)$$

## ESPRIT vs MUSIC

| | MUSIC | ESPRIT |
|---|---|---|
| 搜索方式 | **全空间谱峰搜索** | **闭式解 (EVD)** |
| 计算量 | 大 (网格越细越慢) | 小 (无需搜索) |
| 阵列要求 | 任意几何 | **需平移不变结构** (ULA/URA) |
| 精度 | 高 (超分辨率) | 略低于 MUSIC |
| 声源数 | 需要预设 | 需要预设 |
| 混响鲁棒 | 较差 | 较差 |

## 宽带 ESPRIT

与 MUSIC 类似，宽带信号需要对每个频率子带分别处理，再融合各子带的结果。

## 在 Wiki 中的位置

ESPRIT 在 SSL 综述中被提及，但在已摄入的 19 篇深度学习论文中很少作为基线——MUSIC 和 SRP-PHAT 是更常用的对比方法。

→ [[MUSIC 算法]]
→ [[DOA 波达方向估计]]
