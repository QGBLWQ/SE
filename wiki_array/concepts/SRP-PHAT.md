---
title: SRP-PHAT 可控响应功率相位变换
type: concept
created: 2026-06-21
updated: 2026-06-21
tags:
  - doa-estimation
  - source-localization
  - traditional-method
  - beamforming
  - phase-transform
sources:
  - CNN DOA Estimation with Noise Training 2017
related:
  - [[wiki_array/concepts/DOA 波达方向估计]]
  - [[wiki_array/concepts/STFT相位图与相位信息]]
---

# SRP-PHAT 可控响应功率相位变换

## 定义

**SRP-PHAT (Steered Response Power with Phase Transform)** 是一种基于波束扫描的传统宽带 DOA 估计方法，由 Brandstein 和 Silverman 于 1997 年提出。它通过对候选 DOA 方向逐一扫描，计算每个方向的波束形成器输出功率，将最大功率对应的方向作为 DOA 估计。

## 数学原理

### 基本形式

SRP-PHAT 在候选方向 $\theta$ 上的输出功率为：

$$P(\theta) = \sum_{m=1}^{M} \sum_{l=1}^{M} \sum_{k} \frac{X_m(k) X_l^*(k)}{|X_m(k) X_l^*(k)|} \cdot e^{j 2\pi f_k (\tau_m(\theta) - \tau_l(\theta))}$$

其中：
- $X_m(k)$：第 $m$ 个麦克风在第 $k$ 个频率 bin 的 STFT 系数
- $\tau_m(\theta)$：方向 $\theta$ 到第 $m$ 个麦克风的理论时延
- PHAT 加权：$\frac{1}{|X_m X_l^*|}$ —— 白化幅度，仅保留相位信息

DOA 估计为：

$$\hat{\theta} = \arg\max_{\theta \in \Theta} P(\theta)$$

### 为什么使用 PHAT 加权

GCC-PHAT（相位变换）的核心思想：
- 直接 GCC：$\sum_k X_m(k) X_l^*(k) e^{j2\pi f_k \tau}$ —— 受信号频谱幅度影响
- GCC-PHAT：$\sum_k \frac{X_m(k) X_l^*(k)}{|X_m(k) X_l^*(k)|} e^{j2\pi f_k \tau}$ —— 仅使用相位信息

**好处**：白化幅度后，所有频率 bin 对互相关的贡献相等，锐化了互相关峰值，提高时延估计精度。

## 在 CNN DOA 论文中作为基线

| 对比维度 | SRP-PHAT | CNN 相位图方法 |
|---|---|---|
| **特征** | 手工 GCC-PHAT | 端到端学习的相位特征 |
| **搜索策略** | 全空间扫描 | 单次前向传播（所有 DOA 并行输出概率） |
| **噪声鲁棒性** | SNR 下降时快速退化 (0dB: 19.1% → 20dB: 43.2%) | 相对稳健 (0dB: 62.3% → 20dB: 90.8%) |
| **混响鲁棒性** | 较差（RT60=0.53s 时仅 21.8%） | 中等（RT60=0.53s 时 54.1%） |
| **阵元位置敏感** | 需要精确阵列几何（3mm 扰动下降 ~5%） | 权重共享带来天然鲁棒性（几乎无下降） |
| **计算** | 搜索空间大时成本高 | 单次前向传播，成本固定 |
| **多麦克风优势** | 麦克风数增加显著提升性能（8 麦接近 CNN） | 麦克风数增加也提升性能，但不如 SRP-PHAT 敏感 |

## SRP-PHAT 的优缺点

### 优势

- **无训练**：不需任何训练数据，直接部署
- **对混响有一定鲁棒性**：相比纯 TDOA 方法
- **可解释性强**：功率图谱可直接展示 DOA 分布
- **多麦克风增益明显**：麦克风数越多，空间选择性越强

### 缺点

- **计算量大**：需要在所有候选方向上扫描（分辨率越高越慢）
- **噪声敏感**：低 SNR 下功率峰值被噪声淹没
- **需要精确阵列几何**：麦克风位置误差导致理论时延与实际不匹配
- **对房间声学变化敏感**

## 与其他方法的关系

```
GCC (广义互相关)
  │
  ├── GCC-PHAT (相位变换白化)
  │     │
  │     └── SRP-PHAT (波束扫描 + GCC-PHAT)
  │           │
  │           └── 与深度学习对比的基线
  │
  └── GCC-NON (其他加权)
```

SRP-PHAT 本质上是将 GCC-PHAT 从**单对麦克风时延估计**推广到**多麦克风波束扫描的空间功率估计**。

## 与本 Wiki 其他概念的关联

- [[DOA 波达方向估计]] — SRP-PHAT 服务的任务
- [[STFT相位图与相位信息]] — CNN 方法用深度学习替代了 SRP-PHAT 中的手工相位处理
- [[CNN DOA Estimation with Noise Training 2017]] — 将 SRP-PHAT 作为基线对比的源文章
