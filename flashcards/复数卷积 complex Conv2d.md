---
title: 复数卷积 complex Conv2d
type: flashcard
created: 2026-09-18
last_reviewed: 2026-10-07
review_count: 2
tags:
  - flashcard
  - wiki_low_latency
  - complex-valued
difficulty: ⭐⭐
related:
  - [[wiki_low_latency/concepts/2008.00264-complex-phase-enhancement]]
---

## 💡 一句话记忆点

> 复数卷积 = 4 个普通实数卷积，按复数乘法 `(Xr⋆Wr−Xi⋆Wi)+j(Xr⋆Wi+Xi⋆Wr)` 的组合规则锁死，让实部/虚部交换信息、共享梯度。

## ❓ 问题

complex Conv2d block 是什么？为什么不能用普通 Conv2d 处理复数谱？

## ✅ 答案

- 普通 Conv2d 每个通道是实数，把 `[实部, 虚部]` 堆成两个通道会被当成无关特征，不遵守复数乘法。
- 复数乘法恒等式 `(a+jb)(c+jd)=(ac−bd)+j(ad+bc)` → 复数卷积用 4 路实卷积固定组合：
  `F_out = (Xr⋆Wr − Xi⋆Wi) + j(Xr⋆Wi + Xi⋆Wr)`
- 一个 complex Conv2d block = complex Conv2d → complex BatchNorm → real PReLU
  - complex BatchNorm：实/虚联合 2×2 协方差白化
  - PReLU：无标准复数激活，对实部、虚部分别施加
- 代价：计算量约为普通卷积的 4 倍。

## 🔍 自测题（下次复习用）

- [ ] 复数卷积的 4 路实卷积分别对应什么？`−` 和交叉项为什么关键？
- [ ] 为什么"堆两个实通道"不能满足复数代数？
- [ ] complex BatchNorm 和两个独立 BatchNorm 的本质区别？