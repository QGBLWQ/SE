---
title: "流匹配与 GRPO 后训练"
type: concept
created: 2026-09-08
updated: 2026-09-08
tags:
  - generative-model
  - flow-matching
  - reinforcement-learning
sources:
  - "[[FlowSE-GRPO 2026]]"
related:
  - "[[语音增强评价指标]]"
---

# 流匹配与 GRPO 后训练

流匹配学习从 $x_0\sim\mathcal N(0,I)$ 到目标 $x_1$ 的连续速度 $v=x_1-x_0$，损失为 $\mathbb E\|v-v_\theta(x_t,c,t)\|^2$。确定性 ODE 采样没有同一条件的多样候选；[[FlowSE-GRPO 2026]] 用保持边缘分布的 SDE 加随机噪声，再让 GRPO 在同一条件下比较 $G$ 个样本的相对奖励。其 SE 时间约定下的漂移修正含 $\sigma_t^2/[2(1-t)]$，而非乘 $(1-t)$。

该范式可以直接优化 DNSMOS 等不可微的外部指标，却会出现 reward hacking：某个代理指标上涨不保证语义、声纹或听感都变好。实务上至少要：使用多指标奖励、报告奖励外指标、保留听测和未参与奖励的测试集；也要报告 SDE 噪声与窗口，否则训练稳定性无法判断。
