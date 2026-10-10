---
title: SFF 单频滤波
type: concept
created: 2026-09-08
updated: 2026-09-08
tags: [time-frequency, sff, tdoa, doa]
sources: [https://arxiv.org/abs/2606.17258]
related:
  - "[[SFF 多说话人 DOA 2026]]"
  - "[[wiki_array/concepts/GCC-PHAT 广义互相关]]"
---

# SFF（Single Frequency Filtering）

SFF 对每个目标频率将差分语音频移后送入接近单位圆的单极点 IIR 谐振器，得到复输出 $y[k,n]$ 及包络 $e[k,n]$/相位 $\psi[k,n]$。它试图同时保留窄带谐波分辨率和语音激励脉冲的时间分辨率；这一性质只在所述语音、参数和图示下得到比较，不能视为任意信号的时频不确定性突破。[来源：[[SFF 多说话人 DOA 2026]]，PDF §3--4, Eq. (4)--(10)]

在双麦定位中，可对同频 SFF 包络或相位做跨通道相关，再跨频累积并从角度/TDOA 直方图取峰。SFF-PHAT 的相位归一化交叉项与 GCC-PHAT 的思想相近，差别是前者的时频表示由单极点 SFF 得到。[来源：[[SFF 多说话人 DOA 2026]]，PDF §5]
