---
title: Ambisonics FOA 一阶环境立体声
type: concept
created: 2026-06-21
updated: 2026-06-21
tags:
  - ambisonics
  - spatial-audio
  - foa
  - hoa
  - array-format
sources:
  - CRNN DOAnet 2017
  - SELD CRNN 2018
  - SSL Survey 2021
related:
  - [[wiki_array/concepts/DOA 波达方向估计]]
  - [[wiki_array/concepts/STFT相位图与相位信息]]
---

# Ambisonics / FOA 一阶环境立体声

## 定义

**Ambisonics** 是一种基于球谐函数 (Spherical Harmonics) 分解的空间音频格式，将任意麦克风阵列的录音转换为**阵列无关**的多通道表示。一阶 Ambisonics (First-Order Ambisonics, FOA) 使用 4 个通道（W, X, Y, Z）。

## FOA 四通道

| 通道 | 球谐分量 | 物理含义 |
|---|---|---|
| **W** | $Y_{00}$ | 全向 (omnidirectional) 声压 |
| **X** | $Y_{1(-1)}$ | 沿 X 轴方向的声压梯度 (前后) |
| **Y** | $Y_{10}$ | 沿 Y 轴方向的声压梯度 (左右) |
| **Z** | $Y_{11}$ | 沿 Z 轴方向的声压梯度 (上下) |

## 数学表示

将方向 $(\phi, \lambda)$ 的声源信号 $s_i$ 编码为 FOA：

$$\mathbf{x}_{\text{FOA}} = \sum_i g_i s_i \cdot [Y_{00}(\phi_i, \lambda_i), Y_{1(-1)}(\phi_i, \lambda_i), Y_{10}(\phi_i, \lambda_i), Y_{11}(\phi_i, \lambda_i)]^T$$

其中 $Y_{nm}$ 是实正交归一化球谐函数，$g_i$ 是距离衰减增益。

## 为什么 Ambisonics 对 SELD 重要

| 特性 | 说明 |
|---|---|
| **阵列无关** | 不同阵列（球阵、圆阵、面阵）可通过线性变换转为相同 FOA 格式 |
| **DOA 在幅度中** | 方向信息主要编码在 X/Y/Z 的**幅度差**中（而非相位差）——与 ULA 的相位信息互补 |
| **3D 定位** | 天然支持方位角+仰角的完整 3D 定位 |
| **DCASE 标准** | 2019-2024 DCASE SELD Task 3 均使用 FOA 格式 |

## HOA (高阶 Ambisonics)

FOA → 二阶 → 三阶 → ... → HOA (Higher-Order Ambisonics)
- 阶数越高 → 空间分辨率越高 → 通道数指数增长
- 一阶 4ch, 二阶 9ch, 三阶 16ch

## 与本 Wiki 论文的关系

| 论文 | Ambisonics 使用 |
|---|---|
| DOAnet (2017) | 首个用 FOA 做 CRNN DOA |
| SELD CRNN (2018) | FOA + 圆阵，奠定 DCASE 基线 |
| 几乎全部 DCASE 系统 | FOA 4ch 幅度+相位谱输入 |
| GRAM (2025) | 双耳 + 4ch FOA 双格式基础模型 |

→ [[DOA 波达方向估计]]
→ [[SELD CRNN 2018]]
