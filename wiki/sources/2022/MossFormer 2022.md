---
title: MossFormer — 线性注意力语音分离
type: source
created: 2026-07-06
updated: 2026-07-13
tags:
  - speech-separation
  - transformer
  - linear-attention
  - sequence-model
source_type: paper
year: 2022
authors: 待确认
venue: 2022
related:
  - [[SepFormer 2021]]
  - [[Mamba for SE 2024]]
  - [[Conv-TasNet 2019]]
---

```yaml
- 论文: [MossFormer](2022)
  ├── 要解决什么问题: SepFormer 性能强但 Transformer 注意力计算昂贵，需要更高效的长序列分离模型
  ├── 核心方法: 门控卷积 + 线性注意力/Transformer 结构，在保持长程建模能力的同时降低复杂度
  ├── 属于哪个分支: 语音分离 / Transformer / 线性注意力
  ├── 输入/输出: 混合语音波形 → 分离语音波形
  ├── 关键trick: 用更高效的注意力近似替代标准 MHSA，兼顾性能和计算
  ├── 数据集: WSJ0-2mix 等
  ├── 对比了谁: Conv-TasNet, DPRNN, SepFormer
  ├── 性能上限: 旧笔记记录 SI-SNRi≈21.0
  ├── 参数量: 当前笔记未记录
  ├── 消融关键发现: 旧笔记未记录完整数值；线性注意力和门控卷积应是关键模块
  ├── 遗留问题(你的机会): 高效注意力与 Mamba/SSM 谁更适合音频长序列仍开放
  └── 跟哪篇像: [[SepFormer 2021]]、[[Mamba for SE 2024]]
```

# MossFormer: Pushing the Performance Limit Beyond

## 1. 动机：他们为什么这么做？（motivation）

[[SepFormer 2021]] 证明 Transformer 能显著提升语音分离，但标准自注意力在长序列上计算昂贵。语音分离输入很长，直接用标准 Transformer 会带来内存和速度压力。

MossFormer 的动机是保留 Transformer 的长程建模优势，同时降低注意力复杂度，使高性能语音分离更接近可部署。

## 2. 前人局限：之前的人怎么做不了？（limitation → gap）

Conv-TasNet 的 TCN 感受野固定，DPRNN 的 RNN 并行度弱，SepFormer 的标准注意力成本高。三者分别卡在“感受野、并行度、复杂度”上。

MossFormer 填补的 gap 是：用高效注意力和门控机制在性能与复杂度之间取得更好折中。

## 3. 核心 Trick：这个做法关键在哪？

核心可以概括为：

```text
混合波形
  → 可学习编码器
  → MossFormer 分离模块（门控卷积 + 高效/线性注意力）
  → mask
  → 解码器
  → 分离波形
```

关键 trick 是把标准 Transformer 的二次复杂度压力降下来，同时用门控卷积补充局部建模。

## 4. 实验里哪个消融最关键？

旧笔记记录 MossFormer SI-SNRi 约 21.0，超过 SepFormer 约 20.4。需要补齐的消融包括：

- 线性注意力 vs 标准注意力；
- 门控卷积有无；
- 模块层数；
- 参数量和 MACs；
- 与 SepFormer 在同数据集同设置下的公平对比。

## 5. 这个方向还剩什么问题没解决？（future work / limitation）

- 线性注意力近似是否损失细粒度依赖需要更细评估；
- 主要用于分离，迁移到增强要重新考虑噪声建模；
- 与 Mamba/SSM 的长序列效率对比尚未定论；
- 复杂架构的可解释性弱于传统 DSP 或显式分块模型。

## 6. 本论文在库中的位置关联（cross-reference matrix）

| 维度 | 论文 | 关系 |
|---|---|---|
| 前身/基石 | [[SepFormer 2021]] | 继承 Transformer 语音分离路线，并用高效注意力推进 |
| 前身/基石 | [[DPRNN 2020]] | 双路径长序列思想的后续高效注意力版本 |
| 同分支竞品 | [[Mamba for SE 2024]] | 都追求线性复杂度长序列建模；MossFormer 用注意力近似，Mamba 用 SSM |
| 跨分支类比 | [[FA-Stateformer 2025]] | 定位方向也在组合 attention 与 SSM，说明高效长序列是跨音频任务共性 |

## 7. 一句话总结“江湖地位”

```text
2022 | 语音分离 | SepFormer 后的高效注意力推进者 → 将长序列建模从“能做到”推向“更高效”
```
