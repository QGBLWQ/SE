---
title: TDOA 到达时延差
type: concept
created: 2026-06-21
updated: 2026-06-21
tags:
  - doa-estimation
  - fundamental
  - time-delay
sources:
  - SSL Survey 2021
  - GCC-PHAT 广义互相关
related:
  - [[wiki_array/concepts/GCC-PHAT 广义互相关]]
  - [[wiki_array/concepts/DOA 波达方向估计]]
  - [[wiki_array/concepts/SRP-PHAT]]
---

# TDOA 到达时延差 (Time Difference of Arrival)

## 定义

**TDOA** 是声源信号到达不同麦克风的**时间差**，是 DOA 估计最基本的物理量之一。给定 TDOA $\tau$，DOA 可通过几何关系直接求解。

## 基本几何

对于间距 $d$ 的麦克风对，平面波从 $\theta$ 入射：

$$\tau = \frac{d \sin\theta}{c}, \quad \hat{\theta} = \arcsin\left(\frac{c \cdot \tau}{d}\right)$$

- $c \approx 343$ m/s (声速)
- 仅 $\tau$ 的信息即可解出 $\theta$
- 近场需考虑球面波前（距离+角度）

## TDOA 估计方法

| 方法 | 原理 | 鲁棒性 |
|---|---|---|
| **GCC-PHAT** | 互相关 + 相位白化 | 中等 |
| 直接互相关 | 时域互相关 | 差 |
| LMS 自适应 | 自适应滤波 | 中 |
| 深度学习 | DNN 直接从波形/特征回归 | **强** |

→ [[GCC-PHAT 广义互相关]]

## 多麦克风推广

多麦克风 $(M>2)$ 的场景有 $M(M-1)/2$ 个麦克风对，可以：
- 各对独立估计 → 加权平均/投票
- 联合估计：SRP-PHAT 扫描全空间

→ [[SRP-PHAT]]

## TDOA 的限制

| 问题 | 说明 |
|---|---|
| **混响** | 早期反射产生虚假相关峰 |
| **噪声** | 低 SNR 掩盖真实峰值 |
| **多声源** | 多个相关峰难以对应 |
| **空间混叠** | 高频 $d > \lambda/2$ 产生歧义 |

这些限制直接驱动了从 TDOA → 子空间方法 (MUSIC) → 深度学习方法的演进。
