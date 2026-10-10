---
title: W-Disjoint Orthogonality 语音 W 分离正交性
type: concept
created: 2026-06-21
updated: 2026-06-21
tags:
  - speech
  - time-frequency
  - sparsity
  - multi-speaker
sources:
  - Multi-Speaker CNN DOA 2018
  - SSL Survey 2021
related:
  - [[wiki_array/concepts/STFT相位图与相位信息]]
  - [[wiki_array/concepts/DOA 波达方向估计]]
---

# W-Disjoint Orthogonality (WDO)

## 定义

**W-Disjoint Orthogonality (W 分离正交性)** 是语音信号在时频域的一个重要性质：在合适的 STFT 分辨率下，两个同时说话人的语音在**单个 TF bin 上几乎不重叠**。

> 由 Rickard & Yilmaz (2002) 提出。W 代表来自 Wigner-Ville 分布的启发。

## 数学描述

对于两个语音源 $s_1(t)$ 和 $s_2(t)$，设其 STFT 为 $S_1(n,k)$ 和 $S_2(n,k)$：

$$S_1(n,k) \cdot S_2(n,k) \approx 0, \quad \forall (n,k)$$

即在每个 TF bin 上，最多只有一个源占主导。

## 在 Chakrabarty 多声源 CNN 中的关键应用

WDO 是 Charkrabarty & Habets (2018) 实现**用噪声信号训练多声源 DOA**的根本前提：

### 问题

两个声源的混合信号在时域叠加 → 每个 TF bin 的相位是两路信号相位的非线性组合 → CNN 难以学习。

### WDO 解决方案

1. 分别生成 DOA=$\theta_1$ 和 $\theta_2$ 的单声源噪声训练信号
2. 沿时间轴拼接两个信号的 STFT
3. **逐频率子带**随机打乱时间帧（所有麦克风同步打乱）
4. 打乱后每个 TF bin 的相位仍来自**单一方向**

```
原始: [θ₁帧|θ₁帧|...] [θ₂帧|θ₂帧|...]
打乱: [θ₂帧|θ₁帧|θ₂帧|θ₁帧|...]
结果: 每帧 ~50% θ₁ + 50% θ₂, 但每个TF bin纯!
```

### 为什么有效

- WDO 保证语音的 TF 表示稀疏 → 每个 TF bin ≈ 单源主导
- CNN 学到的是**空间相位关系**，而非混合模式
- 噪声训练数据用 WDO 方法生成，天然匹配语音的 TF 稀疏特性

## 边界条件

| 条件 | WDO 成立程度 |
|---|---|
| 16 kHz, 512-pt DFT, 50% overlap | **约 90-95%** 的 TF bin 非重叠 |
| 32 ms 窗 | 时域分辨率恰好 |
| 增大窗长 | 频率分辨率↑ 但时域稀疏性↓ |

→ [[Multi-Speaker CNN DOA 2018]]
