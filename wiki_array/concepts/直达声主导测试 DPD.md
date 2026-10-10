---
title: 直达声主导测试 DPD
type: concept
created: 2026-09-15
updated: 2026-09-15
tags:
  - direct-path
  - reverberation
  - doa-estimation
  - tf-mask
  - drr
sources:
  - Direct-Path Dominance Test 2020
related:
  - [[wiki_array/concepts/DOA 波达方向估计]]
  - [[wiki_array/concepts/SRP-PHAT]]
  - [[wiki_array/concepts/U-Net]]
---

# 直达声主导测试 DPD (Direct-Path Dominance Test)

## 定义

在混响环境中对每个时频单元 (TF bin) 做一个二元判断：**该 bin 是否由直达声主导（direct-path dominated）**。判据是直达路径能量远大于混响与噪声能量之和：

$$|g \cdot s|^2 \gg |r|^2 + |n|^2$$

- $s$：直达声信号；$g$：直达路径增益
- $r$：混响（反射声）分量；$n$：噪声

一个 TF bin 若满足上式，就说它**通过 DPD 测试（DPD=1）**，其相位携带可靠的声源方向信息。

## 为什么对 DOA 重要

混响尾部和反射声会污染 SRP-PHAT / MUSIC 使用的互功率谱，产生**错误峰**。只保留 DPD=1 的 bin 做定位，等价于「只相信未被房间污染的方向观测」，是**学习式可靠观测筛选（reliable observation selection）**的关键先例。

## 与 DRR 的关系

直达混响比 **DRR (Direct-to-Reverberant Ratio)** 是 DPD 判据的连续版度量；DPD 可视为把 DRR 二值化的结果。二者都是混响 DOA 的通用线索。

## 在本库中的实现（2020 论文）

[[Direct-Path Dominance Test 2020]] 用多任务 U-Net 直接估计两个 ideal ratio mask：

- `IRMd*`（只含直达声）→ 即 DPD mask
- `IRMs*`（直达+混响）→ 用作门控，滤除噪声误判 bin

筛出 `IRMDPD > TH` 的 bin 后，再喂 SRP-PHAT / MUSIC 定位。相比传统 Nadiri 2014 靠先验统计假设驱动的 DPD，学习式估计更鲁棒，但依赖直达声标签。

→ [[空间声学图与图复原定位]] · [[DOA 波达方向估计]]