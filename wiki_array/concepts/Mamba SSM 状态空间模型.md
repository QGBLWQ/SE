---
title: Mamba 状态空间模型
type: concept
created: 2026-06-21
updated: 2026-06-21
tags:
  - state-space-model
  - mamba
  - sequence-modeling
  - architecture
sources:
  - SELD-Mamba 2024
  - FA-Stateformer 2025
  - GRAM Spatial Foundation Model 2025
related:
  - [[wiki_array/concepts/SELD 声事件定位与检测]]
---

# Mamba / SSM 状态空间模型

## 定义

**Mamba** 是一类基于**状态空间模型 (State Space Model, SSM)** 的序列建模架构，核心优势是**线性复杂度 O(N)** 的长程依赖建模能力，避免了 Transformer 自注意力的 O(N²) 瓶颈。

## 数学基础

连续时间 SSM：

$$\mathbf{h}'(t) = \mathbf{A}\mathbf{h}(t) + \mathbf{B}\mathbf{x}(t), \quad \mathbf{y}(t) = \mathbf{C}\mathbf{h}(t)$$

离散化后：

$$\mathbf{h}_k = \bar{\mathbf{A}}\mathbf{h}_{k-1} + \bar{\mathbf{B}}\mathbf{x}_k, \quad \mathbf{y}_k = \mathbf{C}\mathbf{h}_k$$

- $\mathbf{h}$：隐状态 (latent state)
- $\mathbf{A}, \mathbf{B}, \mathbf{C}$：可学习参数
- **选择性 (Selective)**：$\mathbf{B}, \mathbf{C}$ 依赖于输入 $\mathbf{x}$（Mamba 的关键创新）

## 对比：Mamba vs Transformer vs RNN

| | RNN/LSTM | Transformer | Mamba |
|---|---|---|---|
| 复杂度 | O(N) | **O(N²)** | **O(N)** |
| 长程依赖 | 弱 (梯度消失) | **强** | **强** |
| 并行训练 | ❌ (时序) | ✅ | ✅ |
| 推理速度 | 快 | 慢 (KV cache) | 快 |

## Bidirectional Mamba (BMamba)

将两个方向（前向+后向）的 Mamba 组合，类似 BiLSTM/BiGRU：

$$\mathbf{y}_k = \text{concat}(\mathbf{y}_k^{\text{forward}}, \mathbf{y}_k^{\text{backward}})$$

## 在 SSL/SELD 中的应用

| 论文                                     | 使用方式                                      |
| -------------------------------------- | ----------------------------------------- |
| [[SELD-Mamba 2024]]                    | **首个**将 Mamba 用于 SELD：BMamba 替代 Conformer |
| [[FA-Stateformer 2025]]                | BMamba + Self-Attention 协同                |
| [[GRAM Spatial Foundation Model 2025]] | MAE 编码器中的 SSM 组件                          |
| TF-Mamba (引用于 FA-Stateformer)          | 时频双域 Mamba                                |
|                                        |                                           |

## 为什么 Mamba 对 SSL 有吸引力

- 音频序列长（数秒 × 高时频分辨率）→ O(N²) 的 Transformer 昂贵
- 移动声源需要**长程时序建模**→ Mamba 的 O(N) 长程能力天然适合
- DCASE 2024 引入距离估计 → 序列更长 → Mamba 优势更明显

→ [[SELD 声事件定位与检测]]
→ [[SELD-Mamba 2024]]
