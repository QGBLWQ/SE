---
title: GRAM 2025 — 空间通用音频表示基础模型
type: source
created: 2026-06-21
updated: 2026-06-21
tags:
  - foundation-model
  - spatial-audio
  - self-supervised
  - masked-autoencoder
  - representation-learning
  - seld
source_type: paper
year: 2025
authors:
  - Goksenin Yuksel
  - Marcel van Gerven
  - Kiki van der Heijden
affiliation: Radboud University / Donders Institute
venue: NeurIPS 2025
arxiv: "2506.00934"
related:
  - [[SELD CRNN 2018]]
  - [[wiki_array/concepts/DOA 波达方向估计]]
---

# GRAM — General-purpose Real-world Audio Model

> Yuksel, van Gerven & van der Heijden, 2025. **首个空间音频基础模型**

## 核心贡献

1. **首个带空间信息**的通用音频基础模型（支持双耳和 4ch Ambisonics 格式）
2. 自监督多通道掩码自编码器 (MAE)，少量数据即可超越所有基线
3. 发布 **NatHEAR** 和 **RealSELD** 两个标准化基准

## 架构

```
多通道空间音频 → Multi-Channel Masked Autoencoder
                         ↓
                  空间音频嵌入 (Spatial Embeddings)
                         ↓
            ┌────────────┼────────────┐
            ↓            ↓            ↓
         场景分类    SELD/DOA     T60 估计
```

## 关键数据

| 项目 | 详情 |
|---|---|
| 训练数据 | 85,000 自然声场景仿真 (Soundspace 2.0) |
| 格式 | 双耳 + 4ch FOA Ambisonics |
| 发布 | BRIR + ARIR 全部开源 |

## 基准结果

| 基准 | GRAM vs 基线 |
|---|---|
| HEAR (干净单通道) | 超越所有 SOTA 自监督模型 |
| NatHEAR (含混响噪声) | 大幅超越 |
| RealSELD (真实场景) | 定位性能达有监督模型水平 |


### 6. 本论文在库中的位置关联

| 维度 | 论文 | 关系 |
|------|------|------|
| **前身/基石** | [[SELD CRNN 2018]] | SELD 下游评估时以 SELDnet 为对比基线 |
| **同分支竞品** | [[LAM Self-Supervised DOA 2025]] | 同年 (2025) 自监督：GRAM MAE 预训练 → LAM 声学映射 |
| **跨分支类比** | [[Robotics SSL Review 2025]] | GRAM 可作为机器人 SSL 的预训练 backbone——覆盖综述中"数据稀缺"痛点 |

### 7. 江湖地位

```
2025 | 空间基础模型 | 首个带空间信息的多通道音频基础模型 (NeurIPS 2025)
          → 从"单通道忽略空间"到"多通道空间感知"的转折点
```


---

*标志着音频基础模型从"单通道忽略空间"向"多通道空间感知"的转折。*
