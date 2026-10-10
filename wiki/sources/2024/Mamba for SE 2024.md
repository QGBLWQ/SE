---
title: Mamba for SE — Mamba 状态空间模型用于语音增强
type: source
created: 2026-07-06
updated: 2026-07-13
tags:
  - speech-enhancement
  - mamba
  - ssm
  - sequence-model
source_type: paper
year: 2024
authors: 待确认
venue: 2024
related:
  - [[Mamba SSM 状态空间模型]]
  - [[SELD-Mamba 2024]]
  - [[FA-Stateformer 2025]]
---

```yaml
- 论文: [An Investigation of Incorporating Mamba for Speech Enhancement](2024)
  ├── 要解决什么问题: Transformer/Conformer 能建长程依赖但复杂度高，RNN/TCN 又各有局限；语音增强需要线性复杂度长序列模型
  ├── 核心方法: 将 Mamba/SSM 模块引入语音增强网络，替代或增强原有时序建模模块
  ├── 属于哪个分支: 语音增强 / Mamba / 状态空间模型 / 长序列建模
  ├── 输入/输出: 带噪语音时频特征 → Mamba 序列建模 → 增强语音
  ├── 关键trick: 用选择性状态空间模型以 O(T) 复杂度建模长程语音上下文
  ├── 数据集: 当前笔记未记录
  ├── 对比了谁: RNN/Transformer/Conformer 类增强模型
  ├── 性能上限: 当前笔记未记录完整指标
  ├── 参数量: 当前笔记未记录
  ├── 消融关键发现: 旧笔记仅记录“为什么 Mamba”和消融线索，具体数值需补原文
  ├── 遗留问题(你的机会): Mamba 在 SE 中仍是早期探索，结构位置、双向/因果、频率轴建模都未定型
  └── 跟哪篇像: [[SELD-Mamba 2024]]、[[FA-Stateformer 2025]]、[[MossFormer 2022]]
```

# An Investigation of Incorporating Mamba for Speech Enhancement

## 1. 动机：他们为什么这么做？（motivation）

语音增强需要长程上下文：噪声形态、语音音素、谐波结构都跨越多个帧。RNN 能建序列但并行度弱；Transformer/Conformer 能建全局关系但复杂度高；TCN 高效但感受野固定。

Mamba/SSM 的吸引力在于：以线性复杂度建模长序列，并通过选择性状态更新保留输入相关的动态记忆。因此这篇工作的动机是探索 Mamba 是否能成为语音增强的新一代时序模块。

## 2. 前人局限：之前的人怎么做不了？（limitation → gap）

前人路线的不足：

- CRNN/GRU：长序列依赖强，但并行性和容量有限；
- Transformer/Conformer：能力强，但计算和内存压力大；
- TCN：效率高，但对超长依赖需要很深堆叠；
- Mamba 在语音增强中的最佳放置方式尚不明确。

gap 是：语音增强是否能像 NLP/视觉那样受益于 selective SSM。

## 3. 核心 Trick：这个做法关键在哪？

核心是把增强特征序列送入 Mamba：

```text
带噪语音特征
  → 前端特征提取
  → Mamba / SSM block
  → mask 或谱估计头
  → 增强语音
```

Mamba 的关键不是普通状态空间模型，而是**选择性**：状态更新参数依赖输入，使模型能根据当前语音/噪声内容选择保留或遗忘信息。

## 4. 实验里哪个消融最关键？

当前旧笔记只保存了“为什么 Mamba”和消融线索，没有具体表格。需要补：

- Mamba 替换 RNN/Transformer 的直接对比；
- Mamba 层数；
- 是否双向；
- 放在时间轴、频率轴还是时频展平 token 上；
- 因果版本与非因果版本差异；
- 参数量/RTF。

## 5. 这个方向还剩什么问题没解决？（future work / limitation）

- Mamba 在 SE 中仍未形成像 Conv-TasNet/FullSubNet 那样稳定的范式；
- 对频率轴结构的建模不一定天然适配；
- 因果 Mamba 与非因果 Mamba 的质量差异需明确；
- 与 [[SELD-Mamba 2024]]、[[FA-Stateformer 2025]] 的跨域对比提示：定位领域使用 Mamba 更积极，增强领域还处在早期。

## 6. 本论文在库中的位置关联（cross-reference matrix）

| 维度 | 论文 | 关系 |
|---|---|---|
| 前身/基石 | [[MossFormer 2022]] | 都探索高效长序列建模；MossFormer 用线性注意力，Mamba 用 SSM |
| 同分支竞品 | [[CMGAN 2022]] | CMGAN 用 Conformer，Mamba for SE 试图用线性复杂度 SSM 替代高成本注意力 |
| 跨分支类比 | [[SELD-Mamba 2024]] | SELD 方向也在 2024 引入 Mamba，说明音频长序列建模同步转向 SSM |
| 跨分支类比 | [[FA-Stateformer 2025]] | FA-Stateformer 将 Mamba 与 self-attention 协同，提示 SE 也可探索混合架构 |
| 跨分支类比 | [[Mamba SSM 状态空间模型]] | 共享基础概念页，应保持公式和复杂度解释一致 |

## 7. 一句话总结“江湖地位”

```text
2024 | 语音增强 | Mamba/SSM 进入 SE 的早期探索 → 还未定型，但与 SELD-Mamba 形成跨域同步信号
```
