---
title: U-Net
type: concept
created: 2026-09-15
updated: 2026-09-15
tags:
  - u-net
  - segmentation
  - image-to-image
  - acoustic-imaging
  - deep-learning-architecture
sources:
  - Direct-Path Dominance Test 2020
  - Mechanical Fault SSL 2024
  - Beamformed 360 Sound Maps 2025
related:
  - [[wiki_array/concepts/波束成形 Beamforming]]
  - [[wiki_array/concepts/SRP-PHAT]]
  - [[wiki_array/concepts/空间声学图与图复原定位]]
---

# U-Net

## 定义

**U-Net**（Ronneberger et al., 2015）是一种编码器—解码器（encoder–decoder）卷积网络，专为**图到图（image-to-image）**的像素级预测任务设计。命名源于其对称的 U 形结构：左侧编码器逐层下采样提取语义上下文，右侧解码器逐层上采样恢复空间分辨率，并通过**跳跃连接（skip connection）**把编码器各层的细粒度特征直接拼接到解码器对应层。

在声源定位 / 阵列处理里，U-Net 被用来把「带噪声 / 带伪峰 / 带旁瓣的空间图」映射为「干净的空间图或 mask」，即**空间图去噪、复原与分割**。

## 为什么适合声学图

| 特性 | 在空间图上的作用 |
|---|---|
| 局部卷积 + 权重共享 | 空间图几何有序，邻域即方向邻域；参数不随图分辨率暴涨 |
| 跳跃连接 | 定位需同时保留「大尺度空间结构」与「细粒度峰值」 |
| 输出与原图同尺寸 | 天然的 mask / clean-map 输出 |
| 参数量可控 | 相比全局 flatten + 全连接，可做轻量化 |

## 在本库中的三处使用

1. [[Direct-Path Dominance Test 2020]]：多任务 U-Net 预测直达声主导 IRM（`IRMd*`）与全语音 IRM（`IRMs*`），再喂 SRP-PHAT/MUSIC 定位。
2. [[Mechanical Fault SSL 2024]]：U-Net 把强混响下的 SRP-PHAT 图复原为 clean source distribution map，再做插值搜索。
3. [[Beamformed 360 Sound Maps 2025]]：Attention U-Net 对 360° DAS 波束图做声源语义分割，再取质心得 DOA。

## 局限（在声学图场景）

- 需要像素级标签（IRM / clean map / 分割 mask）——制作成本高、依赖真值。
- 输出通常仍要后处理（峰值 / 质心 / 连通域 / 插值），不是纯端到端。
- 高分辨率方位—仰角图上的卷积显存开销不可忽略。

→ [[空间声学图与图复原定位]]