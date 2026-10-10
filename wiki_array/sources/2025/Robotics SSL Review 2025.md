---
title: Robotics SSL Review 2025 — 机器人声源定位综述
type: source
created: 2026-06-21
updated: 2026-06-21
tags:
  - survey
  - robotics
  - deep-learning
  - review
source_type: paper
year: 2025
authors:
  - Reza Jalayer
  - Masoud Jalayer
  - Amirali Baniasadi
venue: Applied Sciences 2025
arxiv: "2507.01143"
doi: "10.3390/app15179354"
related:
  - [[wiki_array/concepts/DOA 波达方向估计]]
  - [[SSL Survey 2021]]
---

# A Review on SSL in Robotics: Focusing on Deep Learning Methods

> Jalayer, Jalayer & Baniasadi, 2025. Applied Sciences. 35 页

> [!warning] PDF 转换状态
> MinerU 解析失败（-60010），以下内容来自 WebSearch 获取的摘要。建议手动查看原 PDF 补充细节。

## 核心定位

**首个专门聚焦机器人场景 + 深度学习 SSL 的综述**，填补了现有综述（偏通用 SSL 或非 DL 机器人 SSL）的空白。

## 覆盖内容

| 方面 | 覆盖 |
|---|---|
| 传统方法 | TDOA, Beamforming, SRP, MUSIC |
| DL 方法 | ML, NN, CNN, CRNN, Attention/Transformer |
| 机器人类型 | 人形、地面移动、无人机等 |
| 应用场景 | 社交、搜救、服务、工业 |
| 数据与训练 | 数据集、训练策略 |

## 关键挑战

- 环境鲁棒性（混响、多样化噪声、动态场景）
- 多声源场景
- 计算/功耗约束（嵌入式/移动平台）
- Sim-to-real gap
- 数据稀缺
- 可解释性


### 6. 本论文在库中的位置关联

| 维度 | 论文 | 关系 |
|------|------|------|
| **前身/基石** | [[SSL Survey 2021]] | 互补：SSL Survey 通用 → 本文专攻机器人场景 |
| **跨分支类比** | [[LOCATA Challenge 2019]] | LOCATA 有机器人头部阵列 → 本文综述覆盖了 LOCATA 结果 |
| **跨分支类比** | [[Multi-Speaker Detection Likelihood 2017]] | HRI 场景的早期间接参考——Pepper 机器人 |

### 7. 江湖地位

```
2025 | 综述 | 首篇机器人+深度学习 SSL 综述 → 和 SSL Survey 2021 互补
          → ⚠️ PDF 转换失败，基于 WebSearch 创建
```


---

*与 [[SSL Survey 2021]] 互补——Grumiaux et al. 覆盖通用 SSL，本文专攻机器人场景。*
