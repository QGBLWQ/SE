---
title: CRAFT — CRNN+交叉注意力语音增强
type: source
created: 2026-07-06
updated: 2026-07-13
tags:
  - speech-enhancement
  - crnn
  - cross-attention
  - time-frequency-attention
source_type: paper
year: 2022
authors: 待确认
venue: arXiv 2022
related:
  - [[TF Attention Module 2023]]
  - [[CMGAN 2022]]
  - [[CST-former 2025]]
---

```yaml
- 论文: [CRAFT](2022)
  ├── 要解决什么问题: CRNN 语音增强中时间维和频率维依赖通常被卷积/RNN隐式处理，缺少显式的 T-F 交互
  ├── 核心方法: Conv2D 编码器 + 时间/频率交叉注意力 + Bi-LSTM + Conv2D 解码器预测掩码
  ├── 属于哪个分支: 时频域语音增强 / CRNN / attention
  ├── 输入/输出: 带噪幅度谱 → 幅度掩码或增强幅度谱
  ├── 关键trick: 时间维查询频率维、频率维反查时间维，用交叉注意力强化 T-F 依赖
  ├── 数据集: 当前笔记未记录，需回看原文
  ├── 对比了谁: 常规 CRNN、后续可与 T-F Attention 和 Conformer 类方法比较
  ├── 性能上限: 当前笔记未记录完整指标
  ├── 参数量: 当前笔记未记录
  ├── 消融关键发现: 旧笔记未记录数值；可确认交叉注意力是核心模块
  ├── 遗留问题(你的机会): 注意力复杂度、实时性、与 Conformer/FTB/DST 类方法的统一解释
  └── 跟哪篇像: [[TF Attention Module 2023]]、[[CMGAN 2022]]、[[CST-former 2025]]
```

# CRAFT: CRNN with Cross-Attention for Speech Enhancement

> 旧笔记仅保留“CRNN + Cross-Attention”的骨架信息；作者、精确指标和完整实验需回看原文补齐。

## 1. 动机：他们为什么这么做？（motivation）

语音增强的时频谱不是普通图像。时间维包含音素、起止、噪声动态；频率维包含谐波、共振峰和噪声谱形。传统 CRNN 用 CNN 捕获局部时频块，再用 RNN 建模时间序列，但频率维和时间维之间的关系多半是隐式学到的。

CRAFT 的动机是显式增强这种时频交互：让时间维和频率维互相“看见”对方，而不是只靠卷积核局部滑动。

## 2. 前人局限：之前的人怎么做不了？（limitation → gap）

普通 CRNN 的问题是：

- 卷积核只看局部邻域，难以建立长程频率关系；
- Bi-LSTM 主要沿时间建模，对频率维结构处理不足；
- 简单 self-attention 若直接展平成 T×F token，复杂度容易上升；
- 幅度谱增强容易过度平滑，非平稳噪声区域尤其需要自适应关注。

因此 gap 是：如何在不完全抛弃 CRNN 工程稳定性的前提下，加入可解释的时频依赖建模。

## 3. 核心 Trick：这个做法关键在哪？

核心结构可以概括为：

```text
带噪幅度谱
  → Conv2D Encoder
  → Cross-Attention: Time ↔ Frequency
  → Bi-LSTM
  → Conv2D Decoder
  → mask / enhanced magnitude
```

关键不是“加注意力”四个字，而是**交叉注意力的方向性**：时间维表示可以查询频率维上下文，频率维表示也可以反过来查询时间动态。这和 [[PHASEN 2020]] 的 FTB、[[TF Attention Module 2023]] 的时频注意力、[[CST-former 2025]] 的多维注意力存在明显同构关系。

## 4. 实验里哪个消融最关键？

当前旧笔记没有记录原文数值，不能补写不存在的指标。按结构判断，最关键的消融应是：

- 去掉 Cross-Attention，退化为普通 CRNN；
- 只保留时间注意力或只保留频率注意力；
- Cross-Attention 放在 encoder 前/后或 Bi-LSTM 前/后的差异；
- 与 Conformer、T-F Attention 的参数量/性能对比。

> [!question] 待补
> 需要从原文表格补齐 PESQ、STOI、CSIG、CBAK、COVL 等指标以及消融掉点。

## 5. 这个方向还剩什么问题没解决？（future work / limitation）

- 注意力模块是否适合实时因果增强仍需验证；
- 交叉注意力和 Conformer 卷积+MHSA 的边界不清，需要统一比较；
- 如果只处理幅度谱，相位仍由带噪相位继承，质量上限受限；
- 与 [[CMGAN 2022]] 相比，CRAFT 的江湖地位更多是“注意力结构探索”，而非指标压倒性代表。

## 6. 本论文在库中的位置关联（cross-reference matrix）

| 维度 | 论文 | 关系 |
|---|---|---|
| 前身/基石 | [[FullSubNet 2021]] | 都在时频域上增强上下文建模，但 FullSubNet 是全带/子带分治，CRAFT 是 T-F 注意力交互 |
| 同分支竞品 | [[TF Attention Module 2023]] | 都在 CRNN 上加时频注意力；CRAFT 偏交叉注意力，TF Attention 偏可学习注意力模块 |
| 同分支竞品 | [[CMGAN 2022]] | CMGAN 用 Conformer + MetricGAN，在指标与框架完整性上更强 |
| 跨分支类比 | [[CST-former 2025]] | CRAFT 的 T↔F 交叉注意力可看作 CST 三维注意力在增强任务上的二维近亲 |
| 跨分支类比 | [[DST Attention 2023]] | SELD 方向也出现频率/时间分离注意力，说明两个领域独立趋同 |

## 7. 一句话总结“江湖地位”

```text
2022 | 语音增强 | CRNN 中显式加入时频交叉注意力 → 被后续 Conformer/T-F attention 路线覆盖但保留跨域类比价值
```
