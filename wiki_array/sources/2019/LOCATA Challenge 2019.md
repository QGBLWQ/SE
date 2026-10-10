---
title: LOCATA Challenge 2019 — 声源定位与跟踪挑战赛
type: source
created: 2026-06-21
updated: 2026-06-21
tags:
  - benchmark
  - challenge
  - localization
  - tracking
  - dataset
source_type: paper
year: 2019
authors:
  - Christine Evers
  - Heinrich W. Löllmann
  - Heinrich Mellmann
  - Alexander Schmidt
  - Hendrik Barfuss
  - Patrick A. Naylor
  - Walter Kellermann
affiliation: Imperial College / FAU Erlangen-Nürnberg
venue: IEEE/ACM TASLP 2020
arxiv: "1909.01008"
related:
  - [[wiki_array/concepts/DOA 波达方向估计]]
---

# LOCATA Challenge — Localization and Tracking Benchmark

> Evers, Löllmann et al., 2019. 声源定位与跟踪的标准化评测框架

## 核心贡献

1. **开放数据集**：4 个麦克风阵列（含移动平台），静态+动态场景
2. **完整标注**：ground truth 位置/方向、VAD 标注、近讲麦克风参考
3. **开源评测框架**：标准化评估指标
4. **参赛算法汇总**：对比分析了所有提交算法的优劣势

## 数据规格

| 阵列 | 类型 | 场景 |
|---|---|---|
| DICIT | 双耳 (人工头) | 静态 |
| Eigenmike | 32ch 球阵列 | 静态+动态 |
| Dummy Array | 12ch 矩形 | 静态 |
| Robot Head | 12ch 类人 | 动态 (机器人头部旋转) |

## 评测任务

1-6 个任务覆盖：单源/多源、静态/动态、已知/未知声源数

## 关键发现

- 没有单一算法在所有任务上最优
- 深度学习方法的参数量远高于传统方法
- 移动声源和未知声源数仍是难点


### 6. 本论文在库中的位置关联

| 维度 | 论文 | 关系 |
|------|------|------|
| **跨分支类比** | [[SLoClas Database 2021]] | 都是基准平台：LOCATA 多阵列通用 → SLoClas 专攻联合定位+分类 |
| **跨分支类比** | [[LAM Self-Supervised DOA 2025]] | LAM 在 LOCATA 上评估——LOCATA 是标准化评测平台 |
| **跨分支类比** | [[SSL Survey 2021]] | LOCATA 是综述中重点引用的基准 |

### 7. 江湖地位

```
2019 | 基准 | 声源定位与跟踪标准化评测 → 与 DCASE 互补——LOCATA 侧重传统vs深度横向对比
```


---

*LOCATA 与 DCASE 互补——LOCATA 侧重传统+深度方法的横向对比，DCASE 侧重 SELD 任务。*
