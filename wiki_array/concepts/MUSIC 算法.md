---
title: MUSIC 算法
type: concept
created: 2026-06-21
updated: 2026-06-21
tags:
  - doa-estimation
  - subspace-method
  - traditional-method
  - baseline
sources:
  - CNN DOA Estimation with Noise Training 2017
  - Multi-Speaker CNN DOA 2018
  - SSL Survey 2021
related:
  - [[wiki_array/concepts/DOA 波达方向估计]]
  - [[wiki_array/concepts/SRP-PHAT]]
  - [[wiki_array/concepts/GCC-PHAT 广义互相关]]
---

# MUSIC 算法 (MUltiple SIgnal Classification)

## 定义

MUSIC 是由 Schmidt (1986) 提出的**子空间方法**，是 DOA 估计中最经典的高分辨率算法。它利用信号子空间与噪声子空间的正交性来探测声源方向。

## 核心原理

### 协方差矩阵与特征分解

对多通道 STFT 信号 $\mathbf{X}(f,n)$，计算协方差矩阵：

$$\mathbf{R}(f) = \sum_{n=1}^{N} \mathbf{X}(f,n) \mathbf{X}(f,n)^H$$

对 $\mathbf{R}(f)$ 做特征值分解 (EVD)：
- **大特征值**对应的特征向量 → 信号子空间
- **小特征值**对应的特征向量 → 噪声子空间

### MUSIC 伪谱

$$P_{\text{MUSIC}}(\theta) = \frac{1}{\mathbf{a}(\theta)^H \mathbf{E}_n \mathbf{E}_n^H \mathbf{a}(\theta)}$$

- $\mathbf{a}(\theta)$：方向 $\theta$ 的 steering vector
- $\mathbf{E}_n$：噪声子空间的基矩阵
- 当 $\theta$ 对应真实声源方向时，$\mathbf{a}(\theta)$ 与噪声子空间正交 → 分母趋近 0 → $P_{\text{MUSIC}}$ 出现峰值

### 宽带 MUSIC

语音是宽带信号，宽带 MUSIC 对每个频率子带分别计算伪谱，再平均：

$$P_{\text{broadband}}(\theta) = \frac{1}{K} \sum_{k=1}^{K} P_{\text{MUSIC}}(\theta, f_k)$$

## 优缺点

| 优势 | 劣势 |
|---|---|
| 超分辨率（超越衍射极限） | **需要已知声源数**（用于分离信号/噪声子空间） |
| 阵列几何通用 | **对混响敏感**（破坏了空间协方差结构） |
| 数学优雅、可解释性强 | 假设不相关源 |
| | 计算量大（EVD + 全空间搜索） |

## 在 Wiki 论文中的表现

几乎所有摄入论文都将 MUSIC 作为基线对比：

| 论文 | MUSIC 表现 | 结论 |
|---|---|---|
| Chakrabarty 2018 | MAE 13.4°–27.1° | CNN 显著优于 MUSIC |
| Adavanne 2018 | 不如 CRNN | CRNN 在混响下强 50% |
| SSL Survey 2021 | 混响敏感 | DNN 方法普遍超越 |

## 与其他方法的关系

```
子空间方法
  ├── MUSIC (谱峰搜索)
  ├── ESPRIT (旋转不变性, 无需搜索)
  └── Root-MUSIC (多项式求根)
```

- MUSIC → 谱峰搜索，计算量大但精度高
- ESPRIT → 利用阵列结构，无需搜索但精度略低
- 两者都需已知声源数

→ 详见 [[DOA 波达方向估计]]
