---
title: SPS 空间伪谱 (Spatial Pseudo-Spectrum)
type: concept
created: 2026-06-21
updated: 2026-06-21
tags:
  - intermediate-representation
  - doa-estimation
  - music
  - likelihood
sources:
  - CRNN DOAnet 2017
  - ISSL 2022
  - MIMO-DoAnet 2022
related:
  - [[wiki_array/concepts/MUSIC 算法]]
  - [[wiki_array/concepts/DOA 波达方向估计]]
---

# SPS 空间伪谱 (Spatial Pseudo-Spectrum)

## 定义

**SPS (空间伪谱)** 是一种似然向量/图谱，每个元素对应一个候选 DOA 方向的声源存在概率。广泛用于深度学习的 DOA 估计中，作为网络的**中间表示**或**最终输出**。

## 两种 SPS 范式

### 1. MUSIC-like SPS (回归目标)

DOAnet 风格：网络输出连续值 SPS，训练目标是用 MUSIC 计算的"真实" SPS：

$$S(\phi, \lambda) \in \mathbb{R}^+$$

- 非负实数值
- 峰值对应声源方向
- 损失用 MSE (回归)

### 2. Likelihood-based SPS (似然编码)

ISSL / MIMO-DoAnet 风格：每个方向编码为高斯分布似然：

$$p(\theta_i) = \max_{\theta' \in \mathcal{Y}} \left\{ \exp\left(-\frac{d(\theta_i, \theta')^2}{\sigma^2}\right) \right\}$$

- 在 GT 角度处形成**高斯峰**
- $\sigma$ 控制波束宽度（通常对应 ~30° 半宽）
- 支持多源叠加（多个高斯峰）

## 优势

| 特性 | 说明 |
|---|---|
| **任意声源数** | 似然向量天然支持任意数量的峰值 |
| **可解释** | 可视化每个方向的可能性 |
| **灵活后处理** | 峰值检测 / 阈值 / 迭代提取 |

## 后处理方式

| 方法 | 代表论文 |
|---|---|
| 阈值 (threshold=0.5) | DOAnet, He et al. |
| Top-L 选取 (已知 L) | Chakrabarty 2018 |
| 迭代减法 + 二分类器 | [[ISSL 2022]] |
| 多输出分离 | [[MIMO-DoAnet 2022]] |

→ [[MUSIC 算法]]
→ [[DOA 波达方向估计]]
