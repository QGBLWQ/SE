---
title: Multi-Speaker Detection and Localization 2017 — 似然编码多声源检测
type: source
created: 2026-06-21
updated: 2026-06-21
tags:
  - doa-estimation
  - multi-speaker
  - mlp
  - gcc-phat
  - likelihood-coding
  - hri
source_type: paper
year: 2017
authors:
  - Weipeng He
  - Petr Motlicek
  - Jean-Marc Odobez
affiliation: Idiap Research Institute / EPFL
venue: ICRA 2018
arxiv: "1711.11565"
related:
  - [[wiki_array/concepts/DOA 波达方向估计]]
  - [[SSL Survey 2021]]
---

# Deep NN for Multiple Speaker Detection and Localization

> He, Motlicek & Odobez, 2017. 人机交互场景 (HRI) 的实用多声源检测

## 核心贡献

1. **似然编码 (Likelihood-based Coding)**：输出不再用 Softmax 后验概率，而是高斯分布似然向量——天然支持任意数量声源
2. **GCC 子带特征 (GCCFB)**：将 GCC-PHAT 按频带分解，保留频率维度的定位线索
3. **三种架构对比**：MLP、CNN、融合网络
4. **真实机器人场景**：Pepper 机器人录音，含强烈自噪声

## 技术方法

| 维度 | 详情 |
|---|---|
| **输入** | GCC-PHAT (51 delays) + GCCFB (子带 GCC) |
| **架构** | 4 层 MLP / 4 层 CNN |
| **输出** | 似然向量 (360 维，1° 分辨率)，高斯分布编码 |
| **检测** | 峰值检测 (无阈值) |
| **帧长** | 170ms |
| **阵列** | Pepper 机器人 4 麦 |

## 输出编码对比

| 方法 | 编码方式 | 多声源 |
|---|---|---|
| Softmax 后验 | $p(\theta_i\mid\Phi)$ | ❌ 单源 |
| 多标签 Sigmoid | 每类独立二分类 | ✅ (需训练全部组合) |
| **似然编码 (本文)** | 高斯分布叠加 | ✅ 天然支持任意数 |

## 实验

- 真实 Pepper 机器人录音，带 ground truth 标注（数据集公开发布）
- 在 2-3 声源场景下显著优于传统 SRP-PHAT 和 MUSIC
- GCCFB 特征相比纯 GCC-PHAT 在混叠场景下有显著提升

> 同一团队后续工作 (He et al. 2019) 将输入从 GCC 迁移到复数频谱，进一步提升精度。


### 6. 本论文在库中的位置关联

| 维度 | 论文 | 关系 |
|------|------|------|
| **同分支竞品** | [[CNN DOA Estimation with Noise Training 2017]] | 同年 (2017)：GCC+似然编码 → CNN 相位图端到端——手工特征 vs 学特征 |
| **同分支竞品** | [[CRNN DOAnet 2017]] | 同年：似然编码 → SPS 回归——两种不同输出策略 |
| **跨分支类比** | [[ISSL 2022]] | 都解决声源数未知问题：似然编码峰值检测 → 迭代减法+二分类器 |
| **跨分支类比** | [[PILOT Transformer SEL 2021]] | 似然编码 (2017) 和 PILOT 高斯输出 (2021) 都走概率路线——但 PILOT 更数学化 |

### 7. 江湖地位

```
2017 | 纯 DOA | 似然编码 + GCC 子带特征 → 人机交互实用路线
          → 被端到端深度学习方法超越，但似然编码思想和高斯分布输出的 PILOT (2021) 有共鸣
```


---
