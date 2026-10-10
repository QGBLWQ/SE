---
title: SGMSE+ — 基于得分匹配的生成式语音增强
type: source
created: 2026-07-06
updated: 2026-07-13
tags:
  - speech-enhancement
  - diffusion
  - score-based
  - generative
source_type: paper
year: 2023
authors: Julius Richter, Simon Welker, Jean-Marie Lemercier, Timo Gerkmann
venue: IEEE/ACM TASLP 2023
related:
  - [[Conditional Diffusion SE 2022]]
  - [[Investigating Design Space of Diffusion for SE 2023]]
  - [[SELM 2023]]
---

```yaml
- 论文: [SGMSE+](2023)
  ├── 要解决什么问题: 用 score-based diffusion 更稳定地生成干净语音，缓解传统回归增强的过平滑问题
  ├── 核心方法: 条件 score-based generative model，在带噪语音条件下通过反向 SDE 逐步恢复干净 STFT
  ├── 属于哪个分支: 生成式语音增强 / score matching / diffusion
  ├── 输入/输出: 带噪 STFT + 扩散时间步 → 干净语音 STFT / 波形
  ├── 关键trick: 学习条件 score 函数，用反向随机微分方程采样增强语音
  ├── 数据集: VoiceBank+DEMAND, DNS 等
  ├── 对比了谁: 早期扩散 SE、传统 DNN 增强、后续设计空间分析
  ├── 性能上限: 当前笔记未记录完整指标
  ├── 参数量: 当前笔记未记录
  ├── 消融关键发现: 改进 SDE/网络/采样步数是关键；具体数值需回看原文
  ├── 遗留问题(你的机会): 多步采样慢、实时性弱、生成忠实性与感知自然度权衡
  └── 跟哪篇像: [[Conditional Diffusion SE 2022]]、[[Investigating Design Space of Diffusion for SE 2023]]
```

# SGMSE+: Score-Based Generative Speech Enhancement

> Richter et al., Universität Hamburg, IEEE/ACM TASLP 2023。

## 1. 动机：他们为什么这么做？（motivation）

传统增强方法通常学习 noisy→clean 的确定性映射，在强噪声下容易输出“平均化”的语音。扩散和 score-based 模型提供了另一种思路：学习干净语音条件分布的梯度，通过逐步采样恢复语音细节。

SGMSE+ 的动机是将 score-based generative modeling 系统化用于语音增强，并在早期扩散 SE 基础上提升稳定性、质量和采样效率。

## 2. 前人局限：之前的人怎么做不了？（limitation → gap）

[[Conditional Diffusion SE 2022]] 等早期工作证明扩散增强可行，但仍存在：

- 采样步数多，推理慢；
- 噪声调度和 SDE 设计缺少统一经验；
- 对复数 STFT 的建模和网络设计仍不成熟；
- 指标提升与主观听感之间关系不稳定。

SGMSE+ 试图把“扩散能做 SE”推进到“扩散如何做得更强、更稳”。

## 3. 核心 Trick：这个做法关键在哪？

核心是条件 score 建模：

```text
干净语音 x 与带噪语音 y
  → 构造条件 SDE / 扩散过程
  → score network sθ(xt, y, t)
  → 反向 SDE / predictor-corrector sampling
  → 增强语音
```

score network 学的是“当前噪声状态应该朝哪个方向移动才能更像干净语音”，而不是一次性输出 clean。

## 4. 实验里哪个消融最关键？

旧笔记只记录“更大模型 + 更优 SDE + 25 步采样”，没有完整消融数值。关键消融应包括：

- SDE 类型；
- 采样步数 25/50/更多的质量-速度权衡；
- 网络规模；
- 复数谱 vs 幅度谱；
- predictor-corrector 设置。

这些也是 [[Investigating Design Space of Diffusion for SE 2023]] 后续系统分析的重点。

## 5. 这个方向还剩什么问题没解决？（future work / limitation）

- **实时性**：多步采样不适合低延迟端侧增强；
- **可控性**：生成细节是否忠实于原语音仍需约束；
- **评价**：PESQ/STOI 和生成自然度可能不一致；
- **工程稳定性**：采样器和噪声调度对性能敏感。

## 6. 本论文在库中的位置关联（cross-reference matrix）

| 维度 | 论文 | 关系 |
|---|---|---|
| 前身/基石 | [[Conditional Diffusion SE 2022]] | 早期条件扩散 SE，SGMSE+ 进一步系统化 score-based 路线 |
| 后续/扩展 | [[Investigating Design Space of Diffusion for SE 2023]] | 对 SGMSE 类方法做设计空间拆解 |
| 同分支竞品 | [[SELM 2023]] | 都是生成式增强；一个连续扩散，一个离散 token LM |
| 跨分支类比 | [[MetricGAN+ 2021]] | 都试图超越普通 MSE 回归，但 MetricGAN 优化指标，SGMSE+ 学分布 |
| 跨分支类比 | [[DeepASA 2025]] | 都指向生成式/统一式声学场景分析，但任务层次不同 |

## 7. 一句话总结“江湖地位”

```text
2023 | 语音增强 | score-based diffusion SE 代表作 → 把扩散增强从可行性推进到系统生成式路线
```
