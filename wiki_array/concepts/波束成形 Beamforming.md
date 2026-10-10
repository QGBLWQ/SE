---
title: 波束成形 Beamforming
type: concept
created: 2026-06-21
updated: 2026-06-21
tags:
  - beamforming
  - spatial-filtering
  - doa-estimation
  - source-separation
sources:
  - DBnet Beamforming 2020
related:
  - [[wiki_array/concepts/DOA 波达方向估计]]
  - [[wiki_array/concepts/SRP-PHAT]]
  - [[wiki_array/concepts/GCC-PHAT 广义互相关]]
---

# 波束成形 Beamforming

## 定义

**波束成形 (Beamforming)** 是一种空间滤波技术：将麦克风阵列的各通道信号加权求和，使阵列的灵敏度在目标方向上最大化（主瓣），同时抑制其他方向的信号（旁瓣）。

$$y(t) = \sum_{m=1}^{M} w_m \cdot x_m(t - \tau_m(\theta))$$

- $w_m$：第 $m$ 个麦克风的权重
- $\tau_m(\theta)$：方向 $\theta$ 的 steering delay

## 与 DOA 估计的关系

```
DOA 估计 ──→ 波束成形 ──→ 增强/分离语音
 (where)     (how)        (result)
```

DOA 估计回答"声源在哪"，波束成形回答"如何对准声源并抑制其他方向"。两者通常是**串行关系**——DOA 为波束成形提供 steering direction。

## 主要类型

| 方法 | 原理 | 特点 |
|---|---|---|
| **DAS (Delay-and-Sum)** | 对齐+平均 | 简单但分辨率受限于衍射极限 |
| **MVDR** | 最小化输出功率 + 无失真约束 | 自适应抑制干扰 |
| **GSC** | 固定波束 + 阻塞矩阵 + 自适应消除 | MVDR 的实现形式 |
| **Neural BF** | 神经网络估计波束权重 | 端到端可学习 |

## DBnet：端到端神经波束成形

[[DBnet Beamforming 2020]] 提出的关键创新：

```
传统:  DOA估计模块 → 波束成形模块  (分开优化)
DBnet: DOA层 → 波束层  (端到端联合梯度反向传播)
```

- 不需要 ground truth DOA 标签
- 用分离语音的损失直接驱动 DOA 估计学到最优中间表示
- → DOA 估计从"独立任务"变成"波束成形的中间特征"

## 应用场景

| 应用 | 波束成形的角色 |
|---|---|
| 语音增强 | 对准说话人，抑制环境噪声 |
| 远场 ASR | 前端空间滤波 |
| 视频会议 | 跟踪活跃说话人 |
| 助听器 | 方向性增强 |

→ [[DOA 波达方向估计]]
→ [[DBnet Beamforming 2020]]
