---
title: GCC-PHAT 广义互相关相位变换
type: concept
created: 2026-06-21
updated: 2026-06-21
tags:
  - doa-estimation
  - tdoa
  - cross-correlation
  - feature-engineering
  - traditional-method
sources:
  - Multi-Speaker Detection Likelihood 2017
  - SSL Survey 2021
related:
  - [[wiki_array/concepts/DOA 波达方向估计]]
  - [[wiki_array/concepts/SRP-PHAT]]
  - [[wiki_array/concepts/MUSIC 算法]]
---

# GCC-PHAT 广义互相关相位变换

## 定义

**GCC-PHAT (Generalized Cross-Correlation with Phase Transform)** 是最常用的时延估计 (TDOA) 方法，由 Knapp & Carter (1976) 提出。通过计算两路麦克风信号的互相关，找到最大相关值对应的时延，进而推算 DOA。

## 数学原理

### 基本 GCC

$$r_{1,2}(\tau) = \sum_{f=0}^{F-1} \frac{X_1(f) X_2^*(f)}{|X_1(f) X_2^*(f)|} e^{j 2\pi \frac{f\tau}{N}}$$

- $X_i(f)$：第 $i$ 个麦克风的 $N$ 点 DFT
- $X_1(f) X_2^*(f)$：互功率谱 (CPS)
- PHAT 加权 $\frac{1}{|X_1 X_2^*|}$：**白化幅度**，仅保留相位

### 为什么用 PHAT 加权

| 直接 GCC | GCC-PHAT |
|---|---|
| 受频谱幅度影响 | 仅用相位信息 |
| 互相关峰值宽泛 | 峰值尖锐 |
| 对宽带信号不理想 | 所有频率等权重 |

PHAT 白化的本质是**放弃幅度信息、专注相位（时延）信息**——与 Chakrabarty CNN 只用相位的思路异曲同工。

### 从 TDOA 到 DOA

$$\hat{\tau} = \arg\max_{\tau} r_{1,2}(\tau), \quad \hat{\theta} = \arcsin\left(\frac{c \cdot \hat{\tau}}{d}\right)$$

## GCC-PHAT 作为深度学习输入特征

GCC-PHAT 不仅是传统方法，也是深度学习 SSL 的**重要输入特征**：

| 方法 | 使用方式 |
|---|---|
| Xiao et al. 2015 | 全频带 GCC-PHAT 向量 → MLP |
| He et al. 2017 | **GCCFB**：子带 GCC-PHAT → CNN |
| DCASE 系统 | GCC-PHAT + log-mel 拼接输入 |

### GCCFB (GCC Filter Bank)

将 GCC-PHAT 按频带分解为多个子带，保留**频率维度的定位线索**。相比全频带 GCC，GCCFB 在多声源混叠场景下表现更好。

## 与其他方法的关系

```
TDOA 方法
  ├── GCC (原始)
  ├── GCC-PHAT ★ (最常用)
  ├── GCC-ML (最大似然加权)
  └── GCCFB (子带分解)
         ↓
      SRP-PHAT (多麦克风扩展)
```

→ [[SRP-PHAT]] — GCC-PHAT 的多麦克风波束扫描推广
→ [[MUSIC 算法]] — 不依赖 TDOA 的子空间方法
