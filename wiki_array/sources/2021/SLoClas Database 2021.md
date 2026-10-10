---
title: SLoClas 2021 — 声源定位与分类联合数据库
type: source
created: 2026-06-21
updated: 2026-06-21
tags:
  - dataset
  - sound-localization
  - classification
  - benchmark
  - slc
source_type: paper
year: 2021
authors:
  - Xinyuan Qian
  - Bidisha Sharma
  - Amine El Abridi
  - Haizhou Li
affiliation: National University of Singapore
venue: DCASE 2021 Workshop
arxiv: "2108.02539"
related:
  - [[wiki_array/concepts/DOA 波达方向估计]]
---

# SLoClas — Sound Localization and Classification Database

> Qian, Sharma, El Abridi & Li, NUS, 2021

## 核心贡献

发布 **SLoClas 数据库**——一个专为联合声源定位 (DOA) 和声事件分类 (SEC) 设计的大规模数据集。

## 数据规格

| 项目 | 详情 |
|---|---|
| **总时长** | 23.27 小时 |
| **麦克风** | 4 通道阵列 |
| **声源类** | 10 类 (bells, bottles, buzzer, cymbals, horn, metal, particle, phone, ring, whistle) |
| **DOA 范围** | 1°–360°，5° 分辨率 |
| **距离** | 1.5m |
| **噪声** | 6 类户外噪声，4 个 DOA |
| **TSP 信号** | 提供，可用于 RIR 测量 |
| **开放** | 数据库 + 基线代码公开 |

## 基线 SLCnet

- 联合 DOA 分类 + 声事件分类
- 定位准确率 95.21%，分类准确率 80.01%

## 与 DCASE 的区别

DCASE 侧重 SELD（检测+定位+多声源重叠），SLoClas 侧重单声源场景下的联合定位+分类，可作为更纯净的分析基准。


### 6. 本论文在库中的位置关联

| 维度 | 论文 | 关系 |
|------|------|------|
| **跨分支类比** | [[LOCATA Challenge 2019]] | 定位基准平台：SLoClas 联合定位+分类 → LOCATA 纯定位+跟踪 |
| **跨分支类比** | [[SELD CRNN 2018]] | SLoClas 能评估 SELDnet 的 SED+DOA 基线 |

### 7. 江湖地位

```
2021 | 数据集 | 23h 联合定位+分类 → 比 DCASE 更纯净的单声源分析基准
```


---

*为声源定位与分类的联合建模提供了标准化评测平台。*
