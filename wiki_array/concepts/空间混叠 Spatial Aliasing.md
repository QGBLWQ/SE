---
title: 空间混叠 Spatial Aliasing
type: concept
created: 2026-06-21
updated: 2026-06-21
tags:
  - spatial-aliasing
  - array-processing
  - fundamental
sources:
  - STFT相位图与相位信息
related:
  - [[wiki_array/concepts/STFT相位图与相位信息]]
  - [[wiki_array/concepts/DOA 波达方向估计]]
---

# 空间混叠 Spatial Aliasing

## 定义

**空间混叠 (Spatial Aliasing)** 是麦克风阵列处理中的基本限制：当阵元间距 $d$ 大于信号半波长 $\lambda/2$ 时，不同方向的声源可能产生**相同的相位差**，导致 DOA 估计出现角度模糊。

## 物理原理

两个相邻麦克风收到来自方向 $\theta$ 的平面波时，相位差为：

$$\Delta\phi = 2\pi f \cdot \frac{d \sin\theta}{c} = \frac{2\pi d}{\lambda} \sin\theta$$

当 $\Delta\phi > \pi$（即 $\frac{2\pi d}{\lambda} \sin\theta > \pi$）时，相位差超过 $2\pi$ 范围，多个 $\theta$ 产生相同的 $\Delta\phi \pmod{2\pi}$：

$$\sin\theta_1 = \sin\theta_2 + \frac{k\lambda}{d}, \quad k \in \mathbb{Z}$$

## 空间 Nyquist 准则

$$d \leq \frac{\lambda_{\min}}{2} = \frac{c}{2f_{\max}}$$

| 频率 | $\lambda/2$ | 允许间距 |
|---|---|---|
| 1 kHz | 17 cm | ≤ 17 cm |
| 4 kHz | 4.3 cm | ≤ 4.3 cm |
| 8 kHz | 2.1 cm | ≤ 2.1 cm |

## 对相位图 CNN 的影响

[[STFT相位图与相位信息|STFT 相位图]] 使用全频带相位信息：
- **低频**：无混叠，但空间分辨率低（相位差小）
- **高频**：空间分辨率高，但混叠导致多解
- CNN 可通过**跨频率学习**来解决模糊性——不同频率的混叠模式不同，联合信息可消歧

这也是为什么**跨频率的卷积**（如 2×2 filter）在单声源场景下有用，但多声源场景下需要改为 2×1（参 [[Multi-Speaker CNN DOA 2018|多声源 CNN]]）。

## 实际设计权衡

| 阵元间距 | 优势 | 劣势 |
|---|---|---|
| 大 | 空间分辨率高 | 高频混叠 |
| 小 | 无混叠 | 空间分辨率低 |
| 非均匀 | 折中 | 设计复杂 |

→ [[STFT相位图与相位信息]]
→ [[DOA 波达方向估计]]
