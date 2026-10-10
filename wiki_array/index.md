---
title: 阵列处理 Wiki 内容目录
type: index
created: 2026-06-21
updated: 2026-09-16
tags:
  - index
---

# 声源定位与阵列处理 Wiki

## 综述

- [[语音定位+语音增强/wiki_array/overview|声源定位与阵列处理 Wiki 综述]]

## 实体 (Entities)

- [[DOAnet]] — 首个 CRNN + Ambisonics 多声源 DOA 网络
- [[EINV2]] — 事件独立网络 V2，DCASE SELD 骨干架构

## 概念 (Concepts)

### 基础概念

- [[DOA 波达方向估计]] — 麦克风阵列声源方向估计基础概念
- [[空间混叠 Spatial Aliasing]] — 阵元间距与频率的 DOA 模糊限制

### 传统方法

- [[SRP-PHAT]] — 传统波束扫描 DOA 估计方法
- [[MUSIC 算法]] — 子空间高分辨率 DOA 估计
- [[GCC-PHAT 广义互相关]] — 广义互相关相位变换时延估计

### 阵列与格式

- [[Ambisonics FOA]] — 一阶球谐分解，SELD 核心格式
- [[STFT相位图与相位信息]] — 多通道相位信息的空间编码与端到端学习

### 任务与框架

- [[SELD 声事件定位与检测]] — 联合声事件检测+定位任务
- [[ACCDOA]] — 活动耦合笛卡尔 DOA 统一输出格式

### 关键技术

- [[W-Disjoint Orthogonality]] — 语音 TF 域稀疏性，多声源噪声训练的理论基础
- [[Mamba SSM 状态空间模型]] — 线性复杂度序列建模架构
- [[波束成形 Beamforming]] — DOA 驱动的空间滤波技术

### 空间图与学习式定位

- [[空间声学图与图复原定位]] — 先把阵列信号变成空间图，再学习复原/分割/定位 🆕
- [[U-Net]] — 空间图去噪/复原/分割的共用编解码骨架 🆕
- [[直达声主导测试 DPD]] — 直达声主导 TF bin 筛选，混响 DOA 的可靠观测选择 🆕

## 资料摘要 (Sources)

### 综述与基准

- [[SSL Survey 2021]] — 深度学习 SSL 综述 (156 篇, 2011-2021)
- [[LOCATA Challenge 2019]] — 声源定位与跟踪挑战赛基准
- [[SLoClas Database 2021]] — 联合定位与分类数据库

### CNN 相位图 DOA 估计 (Chakrabarty 系列)

- [[CNN DOA Estimation with Noise Training 2017]] — 单声源奠基作 (WASPAA 2017)
- [[Multi-Speaker CNN DOA 2018]] — 多声源扩展 (IEEE 2019)

### SRP-PHAT / 空间图与图复原

- [[DeepWave Acoustic Imaging 2019]] — 实时声学成像与递归网络基础
- [[Robust Sound Source Tracking SRP-PHAT 3D CNN 2021]] — SRP-PHAT 时序功率图 + 因果 3D CNN 跟踪
- [[SSLIDE 2021]] — 空间 likelihood 图 + 双 decoder 室内定位
- [[Direct-Path Dominance Test 2020]] — U-Net 直达声主导 TF 选择 + SRP-PHAT
- [[Mechanical Fault SSL 2024]] — 强混响多故障 SRP-PHAT 图复原
- [[Beamformed 360 Sound Maps 2025]] — 360° DAS 声学图 + U-Net 分割

### 几何感知 / 球面 DOA

- [[Icosahedral CNN DOA 2023]] — 球面 SRP-PHAT 图 + icosahedral CNN
- [[LAM Self-Supervised DOA 2025]] — 自监督 CSM / 球面声学映射

### CRNN / DOAnet

- [[CRNN DOAnet 2017]] — 首个 CRNN + Ambisonics 多声源 DOA

### 多声源检测与似然编码

- [[Multi-Speaker Detection Likelihood 2017]] — 似然编码 + GCC 子带特征

### 未知声源数 DOA

- [[ISSL 2022]] — 迭代式声源定位 (无阈值)
- [[MIMO-DoAnet 2022]] — 多输出 DOA 网络

### SELD 声事件定位检测

- [[SELD CRNN 2018]] — 奠基性联合 SELD (DCASE 基线)
- [[PILOT Transformer SEL 2021]] — Transformer + 概率输出
- [[DST Attention 2023]] — 分离式 S+T 频率-时间注意力 (DCASE 2023)
- [[SELD-Mamba 2024]] — Mamba SSM + 距离估计 (DCASE 2024)
- [[CST-former 2025]] — 多维注意力 Transformer
- [[ResNet-Conformer SELD 2025]] — EINV2 + Conformer (DCASE 2024 技术报告)

### 波束成形与端到端

- [[DBnet Beamforming 2020]] — DOA 驱动的端到端波束成形分离

### 自监督与基础模型

- [[LAM Self-Supervised DOA 2025]] — 自监督潜在声学映射
- [[GRAM Spatial Foundation Model 2025]] — 空间音频基础模型
- [[FA-Stateformer 2025]] — Mamba + Self-Attention 协同 DOA

### 视听声源定位

- [[CLIP Audio-Visual SSL 2025]] — CLIP 自监督视听定位

### 综述与基准（补充）

- [[Robotics SSL Review 2025]] ⚠️ — 机器人场景深度学习 SSL 综述 (2025)

### 多任务统一框架

- [[DeepASA 2025]] ⚠️ — 面向对象听觉场景分析 (NeurIPS 2025)

## 主题 (Topics)

*跨实体的综合论述*

> 待添加

## 其他 Wiki

- [[wiki/index|语音增强与音源分离 Wiki]]
- [[wiki_low_latency/index|严格因果超低时延语音增强 Wiki]]

## 操作日志

- [[语音定位+语音增强/wiki_array/log|操作日志]]

---

## 原始资料清单

| # | arXiv ID | 标题 | 年份 | 方向 |
|---|---|---|---|---|
| 1 | 1705.00919 | CNN DOA Estimation with Noise Signals ✅ | 2017 | DOA |
| 2 | 1710.10059 | CRNN DOAnet ✅ | 2017 | DOA |
| 3 | 1711.11565 | Multi-Speaker Detection & Localization ✅ | 2017 | DOA |
| 4 | 1807.00129 | SELD with CRNN ✅ | 2018 | SELD |
| 5 | 1807.11722 | Multi-Speaker CNN DOA ✅ | 2018 | DOA |
| 6 | 1909.01008 | LOCATA Challenge ✅ | 2019 | 基准 |
| 7 | 2010.11566 | DBnet Beamforming ✅ | 2020 | 波束成形 |
| 8 | 2106.03903 | PILOT Transformer SEL ✅ | 2021 | SELD |
| 9 | 2108.02539 | SLoClas Database ✅ | 2021 | 数据库 |
| 10 | 2109.03465 | SSL Survey ✅ | 2021 | 综述 |
| 11 | 2206.12273 | ISSL Iterative ✅ | 2022 | DOA |
| 12 | 2207.07307 | MIMO-DoAnet ✅ | 2022 | DOA |
| 13 | 2408.05057 | SELD-Mamba ✅ | 2024 | SELD |
| 14 | 2306.02591 | DST Attention ✅ | 2023 | SELD |
| 15 | 2504.12870 | CST-former ✅ | 2025 | SELD |
| 16 | 2505.05343 | CLIP Audio-Visual SSL ✅ | 2025 | 视听 |
| 17 | 2506.00934 | GRAM Spatial Foundation ✅ | 2025 | 基础模型 |
| 18 | 2507.07066 | LAM Self-Supervised DOA ✅ | 2025 | DOA |
| 19 | 2507.17941 | ResNet-Conformer SELD ✅ | 2025 | SELD |
| 20 | 2510.25193 | FA-Stateformer ✅ | 2025 | DOA |
| 21 | 2507.01143 | Robotics SSL Review ⚠️ | 2025 | 综述 |
| 22 | 2509.17247 | DeepASA ⚠️ | 2025 | 多任务 |
| 23 | 2006.09006 | Robust Sound Source Tracking | 2021 | DOA/跟踪 |
| 24 | 2010.14420 | SSLIDE | 2021 | DOA/室内 |
| 25 | 2203.16940 | Icosahedral CNN DOA | 2023 | DOA |
| 26 | 2508.00307 | Beamformed 360° Sound Maps | 2025 | DOA/声学图 |
| 27 | — | Direct-Path Dominance Test | 2020 | DOA/直达声 |
| 28 | — | Mechanical Fault SSL | 2024 | DOA/图复原 |
| 29 | — | DeepWave | 2019 | 声学成像 |

> ⚠️ 2 篇 PDF 转换失败，基于 WebSearch 摘要建了精简 source 页，标注 ⚠️ 待手动补充

<!-- frontier-2026-09-08:start -->
## 2026-09-08 前沿论文专题

- [[wiki_array/topics/2026 前沿声源定位五篇比较]]
- [[NeuralMUSIC 2026]]
- [[SFF 多说话人 DOA 2026]]
- [[SARL 空间表征探测基准 2026]]
- [[软体藤蔓机器人分布式声定位 2026]]
- [[容错 SSL 诊断引导测试时自适应 2026]]
<!-- frontier-2026-09-08:end -->
