---
title: 语音增强与音源分离 Wiki 综述
type: overview
created: 2026-06-05
updated: 2026-06-21
tags:
  - speech-enhancement
  - source-separation
  - deep-learning
  - audio-processing
---

# 语音增强与音源分离 Wiki 综述

## 领域概述

本 Wiki 聚焦于**语音增强 (Speech Enhancement)** 与**音源分离 (Audio Source Separation)** 两大方向，涵盖从传统 DSP 方法到深度学习端到端模型的演进路径。

### 语音增强

目标：从带噪语音中恢复干净语音信号。

| 方法类别 | 代表工作 | 年份 |
|---|---|---|
| 混合 DSP/深度学习 | RNNoise | 2018 |
| 相位感知增强 | PHASEN, DCCRN, DPCRN | 2020-2021 |
| 感知驱动增强 | PercepNet | 2020 |
| 复数域方法 | DCUNET (Retracted), DCCRN | 2019-2020 |

### 音源分离

目标：从混合音频中分离出独立声源（语音、音乐、环境声等）。

| 方法类别 | 代表工作 | 年份 |
|---|---|---|
| 波形域端到端 | Wave-U-Net | 2018 |
| 时域音频分离 | Conv-TasNet | 2019 |
| 双路径 RNN | DPRNN | 2020 |
| Transformer 架构 | SepFormer | 2021 |
| 通用分离网络 | SuDoRM-RF | 2020 |

## 关键概念

- **扩张卷积 (Dilated Convolution)**：扩大感受野而不增加参数
- **感受野 (Receptive Field)**：网络能"看到"的输入上下文范围
- **复数卷积循环网络**：在复数域进行特征学习，保留相位信息
- **双路径处理**：块内 (intra-chunk) + 块间 (inter-chunk) 建模长序列

## 关联 Wiki

- [[语音定位+语音增强/wiki_array/index|声源定位与阵列处理 Wiki]] — DOA 估计、波束成形、空间滤波等前置任务

## 当前收录

- **论文 PDF**：12 篇（`raw/papers/`）
- **转换笔记**：8 篇（`raw/articles/`）
- **入门手册**：1 份（`raw/notes/`）

## 待整理

- [ ] 逐篇论文摄取 → 创建 wiki/sources/ 摘要页
- [ ] 建立概念页：MSD、RDF、扩散系数、结合能 等（如涉及）
- [ ] 建立实体页：关键模型/架构
- [ ] 完善交叉引用和主题页
