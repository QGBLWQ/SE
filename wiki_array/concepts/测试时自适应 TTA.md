---
title: 测试时自适应 TTA
type: concept
created: 2026-09-08
updated: 2026-09-08
tags: [test-time-adaptation, self-training, domain-shift, doa]
sources: [https://doi.org/10.1109/ACCESS.2026.3684240]
related:
  - "[[容错 SSL 诊断引导测试时自适应 2026]]"
  - "[[wiki_array/concepts/DOA 波达方向估计]]"
---

# 测试时自适应（Test-Time Adaptation, TTA）

TTA 在部署流中只用无标签目标数据更新已训练模型，应对噪声、设备故障等分布偏移；它不同于预先拿有标签故障数据做的离线 fine-tune。用于 DOA 时，直接坐标回归往往没有显式的不确定度，输出离散角度 likelihood 的模型可以筛选高置信峰来产生伪标签。[来源：[[容错 SSL 诊断引导测试时自适应 2026]]，PDF §III--IV]

伪标签必须有退出机制：可将高置信局部峰设正标签、确定静音区设负标签、其余中间置信区域 mask 出 loss；动态阈值跟随置信分布。TTA 能恢复仍存的空间线索，不能补回阵列几何已丢失的信息（如四麦阵只余两有效麦）。[来源：[[容错 SSL 诊断引导测试时自适应 2026]]，PDF Eq. (8)--(9), §VI-C]

