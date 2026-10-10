---
title: 操作日志 (阵列处理)
type: log
created: 2026-06-21
updated: 2026-09-15
tags:
  - log
---

## [2026-09-15] rewrite | 8 篇「空间图→定位」source 从精简草稿升级为完整版

按 CLAUDE.md 论文摘要模板（5 维度 + 快速索引卡片 + 关联矩阵 + 江湖地位）重写 8 篇 source 笔记：

- [[Robust Sound Source Tracking SRP-PHAT 3D CNN 2021]] — Cross3D 因果 3D CNN，LOCATA RMSAE 7.96°
- [[SSLIDE 2021]] — 空间 likelihood 图 + 双 decoder（定位/多径缓解），室内 MAE 0.23–0.90 m
- [[Icosahedral CNN DOA 2023]] — 球面等变几何卷积 + soft-argmax，0.29M 参数 <10°
- [[Beamformed 360 Sound Maps 2025]] — DAS 图 + Attention U-Net 分割（v4 标题已改名，见笔记内 note）
- [[LAM Self-Supervised DOA 2025]] — 自监督 CSM 重建，LOCATA LE 13.41°
- [[Direct-Path Dominance Test 2020]] — U-Net 直达声 mask + SRP-PHAT（作者校正为 Hao Wang 等）
- [[Mechanical Fault SSL 2024]] — SRP 图复原 + 插值搜索，≤4 源 >98.5%
- [[DeepWave Acoustic Imaging 2019]] — 算法展开 + 图信号处理（更正：recurrent=层间展开，非时序 RNN）

新建 3 个概念页：[[空间声学图与图复原定位]]、[[U-Net]]、[[直达声主导测试 DPD]]。
交叉链接：8 篇同属「空间图→学习定位」分支，与 SELD / 端到端回归 / 自监督基础模型线互链。

## [2026-09-15] ingest | 补充 SRP-PHAT、空间图与图复原论文

- 下载并校验 8 篇论文 PDF，存入 `raw/articles/`；已有 [[语音定位+语音增强/raw/articles/2507.07066.pdf]]，未覆盖。
- 新建 7 个 source note：
  - [[Robust Sound Source Tracking SRP-PHAT 3D CNN 2021]]
  - [[SSLIDE 2021]]
  - [[Icosahedral CNN DOA 2023]]
  - [[Beamformed 360 Sound Maps 2025]]
  - [[Direct-Path Dominance Test 2020]]
  - [[Mechanical Fault SSL 2024]]
  - [[DeepWave Acoustic Imaging 2019]]
- 更新 [[LAM Self-Supervised DOA 2025]] 的发表信息为 WASPAA 2025 / arXiv 2025。
- 更新 [[语音定位+语音增强/wiki_array/index]]，新增“SRP-PHAT / 空间图与图复原”和“几何感知 / 球面 DOA”索引。

# 操作日志

## [2026-07-13] report | 研一前研究路线评估

- 基于两个 wiki、原始论文转写与 `outputs/chakrabarty_repro/` 的现状，形成 [[../../outputs/reports/研一前语音增强与定位研究路线报告-2026-07-13]]；已按“研一结束或最晚研二上结束完成一篇二区期刊毕业条件”更新为 18 个月倒排。
- 推荐以“真实域泛化的轻量小阵列语音 DOA（物理约束 + 自监督适配）”为研一主线；将空间线索保持的增强—定位联动列为完成主线后的扩展。

## [2026-07-02] 批量重写 | SELD 三篇基石论文

重写了 SELD 领域的 3 篇核心论文笔记，全部按新标准（5 个分析维度 + 快速索引卡片 + 完整架构图 + 消融数据）：

- [[SELD CRNN 2018]] — 从 65 行 → 完整版（~300 行）。新增：完整架构图、消融分析（CRNN > CNN/RNN；Cartesian > 角度；DOA loss 权重 50×；频率池化 [8,8,2]）、7 个数据集的完整结果表、6 个基线对比、8 个遗留问题
- [[ResNet-Conformer SELD 2025]] — 从 60 行 → 完整版（~280 行）。新增：EINV2 two-branch 详细架构、4 个 tricks（ACS、多阶段训练、MS-CAM、Conformer）、训练策略消融（多阶段 +9.9%、ACS +7.2%）、与 CST 的参数/性能对比、**距离估计 RDE=0.32 完全没有改善（关键发现！）**
- [[SELD-Mamba 2024]] — 从 68 行 → 完整版（~250 行）。新增：Mamba 层详细流程图、BMamba 的双向设计、两阶段训练策略（含 loss 权重）、与 FA-Stateformer 和 EINV2 的三向对比、SSM 的完整公式链

核心洞察：三篇覆盖了 SELD 三条路线 —— CRNN 奠基 (0.5M) → EINV2+Conformer 重模型 (~50M) → Mamba 线性复杂度 (~30M)。距离估计 (SDE) 是 DCASE 2024 最大的开放问题——两篇做 SDE 的论文都没改善 RDE。

## [2026-07-01] 单篇摄入 | DST Attention 2023

- 读取: [[raw/articles/2306.02591.pdf]] — "Divided Spectro-Temporal Attention for SELD" (DCASE 2023)
- 创建: [[DST Attention 2023]] — 按新模板格式（5个分析维度 + 快速索引卡片）
- 更新: CLAUDE.md — 追加"论文摘要模板"章节，要求所有 future source 笔记必须包含 5 个分析维度 + 快速索引卡片
- 关联: [[CST-former 2025]] 的直系前身，做对比记录
- 下载: PDF 已存入 raw/articles/

## [2026-07-01] 重写 | FA-Stateformer 2025

- 重写: [[FA-Stateformer 2025]] — 从 72 行简化版 → 完整版（按新模板：5个分析维度 + 快速索引卡片 + 完整消融数据）
- 新增内容: 完整架构图、FA模块时频分支的公式、4个消融实验的详细分析、计算效率对比表、与5个baseline的完整对比、SNR/RT60鲁棒性分析
- 核心发现: FA模块频域注意力 > 时域注意力；ShiftConv15 > Conv31；SEConformer参数降40%不降性能

## [2026-06-21] ingest-batch | 批量摄入 18 篇声源定位论文

### Batch 1: 基础（续作 + 综述）
- [[Multi-Speaker CNN DOA 2018]] — Chakrabarty 多声源扩展 (IEEE 2019)
- [[SSL Survey 2021]] — 深度学习 SSL 综述 (156 篇)

### Batch 2: 核心 DOA 估计 (6 篇)
- [[CRNN DOAnet 2017]] — 首个 CRNN+Ambisonics 多声源 DOA
- [[Multi-Speaker Detection Likelihood 2017]] — 似然编码多声源检测
- [[ISSL 2022]] — 迭代式声源定位（无阈值）
- [[MIMO-DoAnet 2022]] — 多输出 DOA 网络
- [[LAM Self-Supervised DOA 2025]] — 自监督潜在声学映射
- [[FA-Stateformer 2025]] — Mamba+Self-Attention 协同 DOA

### Batch 3: SELD 声事件定位检测 (6 篇)
- [[SELD CRNN 2018]] — 奠基性联合 SELD（DCASE 基线）
- [[PILOT Transformer SEL 2021]] — Transformer + 概率输出
- [[SLoClas Database 2021]] — 联合定位+分类数据库
- [[SELD-Mamba 2024]] — Mamba SSM + 距离估计
- [[CST-former 2025]] — 三维注意力 Transformer
- [[ResNet-Conformer SELD 2025]] — DCASE 2024 技术报告

### Batch 4: 波束成形/基础模型/基准 (4 篇)
- [[DBnet Beamforming 2020]] — DOA 驱动的端到端波束成形
- [[CLIP Audio-Visual SSL 2025]] — CLIP 自监督视听定位
- [[GRAM Spatial Foundation Model 2025]] — 空间音频基础模型
- [[LOCATA Challenge 2019]] — 定位跟踪挑战赛

### 更新
- 更新 [[语音定位+语音增强/wiki_array/index]] — 完整 19 篇目录 + 原始资料清单
- 更新 [[语音定位+语音增强/wiki_array/overview]] — 5 方向分类 + 架构演进时间线
- 更新 [[语音定位+语音增强/wiki_array/log]] — 本条目

> ⚠️ 2 篇转换失败 (2507.01143 SSL in Robotics review, 2509.17247 DeepASA)，待后续重试

## [2026-06-21] init | 阵列处理 Wiki 初始化

- 从主 Wiki (`wiki/`) 中分离出声源定位/阵列处理方向，建立独立 `wiki_array/`
- 创建骨架：`overview.md`, `index.md`, `log.md`
- 更新 `CLAUDE.md` 添加 `wiki_array/` 目录说明和领域特化规则

## [2026-06-21] concepts | 补齐概念和实体页面

- 创建 9 个概念页：
  - [[MUSIC 算法]] — 子空间高分辨率 DOA
  - [[GCC-PHAT 广义互相关]] — 时延估计基础
  - [[Ambisonics FOA]] — 球谐空间音频格式
  - [[SELD 声事件定位与检测]] — 联合检测+定位
  - [[ACCDOA]] — 统一输出格式
  - [[W-Disjoint Orthogonality]] — TF 稀疏性
  - [[Mamba SSM 状态空间模型]] — 线性复杂度序列建模
  - [[波束成形 Beamforming]] — DOA 驱动空间滤波
  - [[空间混叠 Spatial Aliasing]] — 阵列基本限制
- 创建 2 个实体页：
  - [[DOAnet]] — 首个 CRNN DOA 网络
  - [[EINV2]] — SELD 骨干架构
- 更新 [[语音定位+语音增强/wiki_array/index]], [[语音定位+语音增强/wiki_array/overview]]

## [2026-06-21] concepts-2 | 补齐 8 个概念 + 2 篇补充论文

- 新增 6 个概念页：[[cRF 复数比率滤波器]], [[SPS 空间伪谱]], [[ESPRIT 算法]], [[TDOA 到达时延差]], [[MVDR 最小方差无失真响应]], [[DAMAS 解卷积声源映射]]
- 2 篇 PDF 转换失败论文基于 WebSearch 建立精简 source 页：
  - [[Robotics SSL Review 2025]] ⚠️ (机器人 SSL 综述, Applied Sciences 2025)
  - [[DeepASA 2025]] ⚠️ (面向对象听觉场景分析, NeurIPS 2025)
- 更新 [[语音定位+语音增强/wiki_array/index]], [[语音定位+语音增强/wiki_array/overview]], 所有计数刷新

<!-- frontier-2026-09-08:start -->
## [2026-09-08] ingest | 声源定位前沿论文五篇

- 收录 5 篇 2026 前沿论文及中文技术笔记；全文位于 [[outputs/reports/2026-09-08-frontier/README|论文包]]。
<!-- frontier-2026-09-08:end -->
