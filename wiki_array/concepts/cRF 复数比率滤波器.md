---
title: cRF 复数比率滤波器
type: concept
created: 2026-06-21
updated: 2026-06-21
tags:
  - filter
  - time-frequency
  - source-separation
  - complex-domain
sources:
  - MIMO-DoAnet 2022
related:
  - [[wiki_array/concepts/STFT相位图与相位信息]]
  - [[wiki_array/concepts/DOA 波达方向估计]]
---

# cRF 复数比率滤波器 (complex-valued Ratio Filter)

## 定义

**cRF** 是在 STFT 域操作的**复数比率滤波器**，用于从多通道混合信号中提取单个声源成分。在 [[MIMO-DoAnet 2022|MIMO-DoAnet]] 中被用于将混合信号分离为独立声源，然后分别做 DOA 估计。

## 数学形式

对于多通道 STFT 信号 $\mathbf{Y}$，cRF 在 TF 域对每个 bin 做复数滤波：

$$\hat{\mathbf{S}}_i(n,k) = \sum_{m=1}^{M} \mathbf{H}_{i,m}(n,k) \cdot \mathbf{Y}_m(n,k)$$

- $\mathbf{H}_{i,m} \in \mathbb{C}$：复数滤波器系数（GRU 估计）
- $\hat{\mathbf{S}}_i$：第 $i$ 个声源的估计
- 同时在幅度和相位上做滤波

## 在 MIMO-DoAnet 中的角色

```
6ch 混合信号 → STFT → 幅度谱 + IPD
                         ↓
                  GRU cRF Estimator
                    ↓          ↓
                 cRF_S (语音)  cRF_N (噪声)
                    ↓          ↓
                 协方差 Φ_S   协方差 Φ_I
                    ↓          ↓
                  各自独立的 SPS Estimator
```

**为什么用 cRF 而非实值掩蔽**：多声源场景下，相位信息对 DOA 估计至关重要，实值掩蔽丢失相位，cRF 保留完整复数信息。

## 与 IRM/IBM 的区别

| 掩蔽类型 | 作用域 | 保留相位？ | 典型用途 |
|---|---|---|---|
| IRM (实值) | 幅度 | ❌ | 语音增强 |
| IBM (二值) | 幅度 | ❌ | 语音分离 |
| **cRF (复数)** | 幅度+相位 | ✅ | **MIMO-DoAnet DOA** |
| cIRM (复数) | 幅度+相位 | ✅ | 语音增强 |

→ [[MIMO-DoAnet 2022]]
