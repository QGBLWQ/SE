---
title: SepFormer — 纯 Transformer 语音分离
type: source
created: 2026-07-06
updated: 2026-07-13
tags:
  - speech-separation
  - transformer
  - self-attention
  - dual-path
source_type: paper
year: 2021
authors: Cem Subakan, Mirco Ravanelli, Samuele Cornell, Mirco Bronzi, Jianyuan Zhong
venue: ICASSP 2021
related:
  - [[DPRNN 2020]]
  - [[MossFormer 2022]]
  - [[PILOT Transformer SEL 2021]]
---

```yaml
- 论文: [SepFormer](2021)
  ├── 要解决什么问题: DPRNN 的双路径思想有效，但 RNN 并行度和建模能力受限；能否用 Transformer 替代
  ├── 核心方法: 双路径 Transformer；块内 IntraTransformer + 块间 InterTransformer
  ├── 属于哪个分支: 语音分离 / Transformer / 双路径建模
  ├── 输入/输出: 混合波形 → 可学习编码器 → Transformer 分离器 → 分离波形
  ├── 关键trick: 保留 DPRNN 的分块结构，将 RNN 单元换成自注意力模块
  ├── 数据集: WSJ0-2mix, WSJ0-3mix, LibriMix
  ├── 对比了谁: Conv-TasNet, DPRNN
  ├── 性能上限: 旧笔记记录 WSJ0-2mix SI-SNRi=20.4dB, SDRi=20.6dB
  ├── 参数量: 25.7M
  ├── 消融关键发现: 去掉 InterTransformer 17.3；去掉 IntraTransformer 18.1；无位置编码 19.2
  ├── 遗留问题(你的机会): 参数量和计算量较高，后续 MossFormer/Mamba 路线追求高效长序列
  └── 跟哪篇像: [[DPRNN 2020]]、[[MossFormer 2022]]、[[PILOT Transformer SEL 2021]]
```

# SepFormer: Attention Is All You Need in Speech Separation

> Cem Subakan, Mirco Ravanelli, Samuele Cornell, Mirco Bronzi, Jianyuan Zhong, ICASSP 2021。

## 1. 动机：他们为什么这么做？（motivation）

[[DPRNN 2020]] 证明“双路径分块”能高效建模长语音序列，但 RNN 单元仍有顺序处理和表达能力限制。Transformer 在 NLP 中已经证明强大的全局依赖建模能力，SepFormer 的动机是把 Transformer 放进 DPRNN 的双路径框架里。

## 2. 前人局限：之前的人怎么做不了？（limitation → gap）

Conv-TasNet 的 TCN 感受野固定，DPRNN 的 RNN 并行度弱。直接把完整长语音序列送进 Transformer 又太贵。SepFormer 的 gap 是：如何利用 Transformer，同时避免完整序列注意力的二次复杂度爆炸。

## 3. 核心 Trick：这个做法关键在哪？

旧笔记记录结构：

```text
波形 → Conv1D 编码器 → 重叠分块 (L, K, P)
  → IntraTransformer: 块内 token 做 MHSA
  → InterTransformer: 跨块 token 做 MHSA
  → overlap-add
  → Conv1D 解码器 → 分离波形
```

核心 trick 是**双路径 Transformer**：不是对整段语音一次性 self-attention，而是先分块，再分别建模局部和全局。

## 4. 实验里哪个消融最关键？

| 消融项 | SI-SNRi | 分析 |
|---|---:|---|
| SepFormer 完整 | **20.4** | 基线 |
| 去掉 InterTransformer | 17.3 | 块间交互至关重要 |
| 去掉 IntraTransformer | 18.1 | 块内局部建模也重要 |
| 4 头 → 8 头 | 20.0 → 20.4 | 更多头有收益但边际递减 |
| 4 层 → 8 层 | 20.1 → 20.4 | 更深可提升但计算翻倍 |
| 无位置编码 | 19.2 | 位置信息不可或缺 |

最关键：InterTransformer 掉点最大，说明跨块全局关系是分离质量核心。

## 5. 这个方向还剩什么问题没解决？（future work / limitation）

- 参数量 25.7M，计算成本高；
- 标准 Transformer 注意力仍贵；
- 主要适合离线高质量分离；
- 后续 [[MossFormer 2022]] 追求高效注意力，[[Mamba for SE 2024]]/SSM 路线进一步追求线性复杂度。

## 6. 本论文在库中的位置关联（cross-reference matrix）

| 维度 | 论文 | 关系 |
|---|---|---|
| 前身/基石 | [[DPRNN 2020]] | 继承双路径结构，将 RNN 单元替换为 Transformer |
| 前身/基石 | [[Conv-TasNet 2019]] | 继承时域编码器/解码器框架 |
| 后续/扩展 | [[MossFormer 2022]] | 在 SepFormer 后继续降低注意力复杂度 |
| 跨分支类比 | [[PILOT Transformer SEL 2021]] | 定位/SELD 也在 2021 引入 Transformer，说明跨领域同步转向注意力 |
| 跨分支类比 | [[CST-former 2025]] | 都体现多轴/分块 Transformer 对音频张量建模的重要性 |

## 7. 一句话总结“江湖地位”

```text
2021 | 语音分离 | 双路径 Transformer 代表作 → 将 DPRNN 的分块思想推进到注意力时代
```
