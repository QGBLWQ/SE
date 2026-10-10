---
title: SELD CRNN 2018 — 奠基性联合声事件定位与检测的 CRNN
type: source
created: 2026-06-21
updated: 2026-07-02
tags:
  - seld
  - crnn
  - dcase
  - multi-task
  - ambisonics
  - regression
  - foundation
source_type: paper
year: 2018
authors:
  - Sharath Adavanne
  - Archontis Politis
  - Joonas Nikunen
  - Tuomas Virtanen
affiliation: Tampere University
venue: IEEE JSTSP 2019 (extended from DCASE 2018 Workshop)
arxiv: "1807.00129"
related:
  - "[[CRNN DOAnet 2017]]"
  - "[[DST Attention 2023]]"
  - "[[CST-former 2025]]"
  - "[[SELD 声事件定位与检测]]"
---

# SELDnet — 首个用 CRNN 联合做 SED + DOA 的奠基性框架

> Adavanne, Politis, Nikunen & Virtanen, 2018. **D的所有 SELD 研究都跟它比。——这是整个 DCASE SELD 方向的起点。**

```yaml
- 论文: SELDnet (SELD with CRNN) — 2018
  ├── 要解决什么问题: 之前没有人用一套网络同时做"检测声事件"和"定位它们的方向"，两任务分离导致数据关联问题
  ├── 核心方法: CRNN (CNN提取局部特征 + BiGRU建模时序 + 双输出头 SED+DOA)，用一个网络解两个任务
  ├── 属于哪个分支: 联合 SED+DOA 的端到端 DNN（CRNN 路线）
  ├── 输入/输出: 幅度谱+相位谱（无手工特征）/ SED 多标签分类 + DOA 笛卡尔坐标回归
  ├── 关键trick: 相位+幅度各自独立作为输入通道；DOA 用回归而非分类（连续值，不受网格分辨率限制）；Cartesian 坐标优于角度（避免角度环绕不连续）
  ├── 数据集: 7 个（5 FOA + 2 圆阵，消声/混响/真实场景全覆盖）
  ├── 对比了谁: SEDnet, MSEDnet, MUSIC, DOAnet, AZInet, HIRnet（6 个基线）
  ├── 性能上限: ANSYN O2(F=89.0%, DOA=13.8°) → 真实场景 DOA=33.7°（混响严重，性能掉很多）
  ├── 参数量: 0.51M (3×CNN64 + 2×BiGRU128 + FC128)
  ├── 消融关键发现: CRNN > 纯 CNN > 纯 RNN；Cartesian > 角度；DOA 损失权重要比 SED 大 50 倍；模型对未见过的 DOA 值也有效
  ├── 遗留问题(你的机会): 真实场景性能差（DOA 33.7°）；没有距离估计；三声源以上未验证；输出分辨率有限（SED 阈值决定 DOA 的有效性）
  └── 跟哪篇像: DOAnet（同一年，同一个组，CRNN 架构用于纯 DOA）→ SELDnet 是其 SELD 扩展
```

## 一、研究任务与对象

| 维度 | 详情 |
|------|------|
| **任务** | SELD — **首个**联合 SED（多标签检测）+ DOA（回归定位）的 DNN 系统 |
| **核心问题** | 分离做 SED 和 DOA 会产生"数据关联"问题——知道有个声音持续了 2 秒+知道 3 个方向在变，但不知道"哪个方向对应哪个声音" |
| **方法类型** | CRNN：3 层 CNN（局部特征）+ 2 层 BiGRU（时序）+ 双 FC 输出头 |
| **阵列类型** | 通用阵列 — FOA (4ch Ambisonics) + 8ch 圆阵，**不依赖阵列特化特征** |
| **输出格式** | SED: 每帧每类 0/1（多标签 sigmoid）/ DOA: 每类 3D Cartesian (x,y,z) 回归 |
| **数据集** | 7 个数据集 (ANSYN, RESYN, REAL, REALBIG, REALBIGAMB, CANSYN, CRESYN) |
| **参数量** | **0.51M** (3×CNN64 + 2×BiGRU128 + 1×FC128 + 双头) |

## 二、整体架构

```
多通道音频 (C ch, M-point DFT)
    │
    ▼
幅度谱 (C×F×T)  相位谱 (C×F×T)
    │                   │
    └───── 拼接 ────────┘
    │
    ▼
输入: (T, F, 2C)  ← C 个通道 × 2 (幅度+相位)
    │
    ▼
Conv2D × 3 (每层 64 个 3×3×2C 核)
  → 跨通道核 → 学习空间关系（相位差/幅度差）
  → 频率方向 MaxPool (8,8,2) → 最终 F→2
  → 时间方向保留 (T 不变)
  → 输出: (T, 2×64) = (T, 128)
    │
    ▼
Reshape → (T, 128) 序列 → BiGRU × 2 (每层 128 节点)
    │
    ├─────────────────┬─────────────────┐
    ▼                 ▼                 
SED 头              DOA 头
FC(128→N)          FC(128→3N)
sigmoid             tanh
每类: 活跃概率      每类: x, y, z
    │                 │
    └────────┬────────┘
             ▼
SED 输出 > 阈值 0.5 → 该类的 DOA 被选中
```

### 为什么这个设计是奠基性的？

1. **一个网络同时做两个任务**：CNN 提取的跨通道特征（相位差、幅度差）被 SED 和 DOA 共享 → 隐含的数据关联
2. **DOA 做回归而非分类**：SED 输出做"置信度"，高于阈值时选对应 DOA → 解决了格式统一问题
3. **不依赖阵列特化特征**：只输入原始幅度谱+相位谱，不做 GCC/ILD/ITD → 通用性
4. **Cartesian 坐标优于角度**：角度在 ±180° 不连续，Cartesian (x,y,z) 是连续的

## 三、为什么这么做？（Motivation）

1. **SED 和 DOA 分离做 → 数据关联问题**：一个网络检测到"有人在说话"，另一个网络估计了 3 个方向，你无法知道"哪个人是哪个方向"
2. **之前唯一的 DNN SELD（HIRnet）**只做离散方向分类，10° 分辨率，而且要一个输出节点对一个角度 → 不可扩展
3. **相位谱包含空间信息**（多通道相位差 = DOA 线索），幅度谱包含事件信息（什么频率在响 = 声事件线索），两者分开作为输入通道 → 让 CNN 同时学习

## 四、之前的人怎么做不了？（Limitation → Gap）

| 方法 | 能做 | 不能做 |
|------|------|--------|
| 传统 DOA (MUSIC) | 高精度 DOA（需要声源数） | 对混响敏感；不做声事件检测；需要源数先验 |
| DOAnet (2017) | 多声源 DOA 估计 | 只做 DOA，不做 SED |
| HIRnet (唯一SELD) | SELD（分类方式） | 离散网格 10°，不可扩展；只在圆阵上验证 |
| SEDnet / MSEDnet | 多标签 SED | 只检测，不定位 |
| **SELDnet** | **联合 SED + DOA，连续回归，多阵列通用** | **真实混响场景 DOA 33.7°（仍然很差）；不做距离估计** |

## 五、核心 trick：只有一个 idea 还是叠了十个？

**这篇论文只有一个核心 idea**：把 CRNN（当时 SED 的 SOTA）+ DOA 回归（DOAnet 的思路）合并成一个网络，通过**双输出头 + SED 做 DOA 置信度**来解数据关联。

```
配上一个聪明的工程选择:
  ✓ 幅度+相位分离输入 → 不依赖手工特征 → 阵列通用
  ✓ Cartesian 坐标 → 避免角度环绕
  ✓ 跨通道卷积核 → 学习空间关系

这篇论文没有叠 trick——就是一个干净的 idea + 几个聪明的工程选择。
```

## 六、实验里哪个消融最关键？

### 关键发现 1：CRNN > CNN ≈ RNN

（论文 Fig.3）

```
CRNN (CNN + RNN): 最优
纯 CNN: 参数量大时性能可以但不如 CRNN
纯 RNN: 性能一般

→ 卷积+时序的组合不可替代：CNN 提取局部时频特征，RNN 建模时序依赖
```

### 关键发现 2：Cartesian > 角度

（论文 Fig.6）

```
所有数据集上 (x,y,z) 都优于 (azimuth, elevation)
原因: 角度在 ±180° wrap-around 不连续 → 网络难学
     Cartesian 连续 → smooth loss surface
```

### 关键发现 3：DOA 损失权重要比 SED 大 50 倍

（论文 Fig.5）

```
SED 是 N 类二分类（每个类 0 或 1）
DOA 是 3N 维连续回归
如果把两者的 loss 等权，SED 主导训练 → DOA 学不好
→ DOA 加权 50× = 让网络重视"准确定位"
```

### 关键发现 4：频率 MaxPool [8,8,2] 压缩 F→2

```
三层 CNN 将频率从 F/2 压到 2 维
→ 极端压缩（和 DST 的 F'=2 一样）
→ 所以这篇 baseline 的"频率注意力"根本没法做
→ DST 的 insight "频率池化改小"就是针对这个问题
```

## 七、整体结果

### 模拟数据（有监督，无数据增强）

| 场景 | SED F-score | DOA Error | Frame Recall | 说明 |
|------|:---------:|:--------:|:----------:|------|
| ANSYN O1 (消声,1声源) | 97.7% | 3.4° | 99.4% | 几乎完美 |
| ANSYN O2 (消声,2声源) | 89.0% | 13.8° | 85.6% | 两声源已开始吃力 |
| ANSYN O3 (消声,3声源) | 85.6% | 17.3° | 70.2% | 三声源大幅退化 |
| RESYN O2 (混响,2声源) | 79.6% | 20.2° | 74.9% | 混响显著恶化 |
| REAL O2 (真实IR) | 53.1% | 33.7° | 41.5% | 真实场景性能崩溃 |
| REALBIG (更大数据集) | 61.5% | 31.3° | 45.2% | 更多数据有改善但有限 |

### 与 MUSIC 的对比（消声 vs 混响）

```
ANSYN (消声):
  SELDnet DOA: 13.8° (O2)
  MUSIC DOA:   7.2°   ← MUSIC 更好（源数已知！）

RESYN (混响):
  SELDnet DOA: 20.2°
  MUSIC DOA:   47.1°   ← MUSIC 崩溃！DNN 更鲁棒
```

→ DNN 对混响的鲁棒性远超传统方法，这是在 2018 年就定了的基调。

## 八、还剩什么问题没解决？

1. **真实场景性能很差**：DOA 33.7°，帧召回 41.5% → 离实用差很远
2. **频率维度被压到只剩 2** → 丢失了所有频率结构信息 → DST/CST 后来特地改进了这一点
3. **没有使用 GCC-PHAT 等空间特征** → 完全依赖原始相位谱 → 后续工作（DST/CST）证明加空间特征有很大帮助
4. **没有距离估计（SDE）** → DCASE 2024 新增任务
5. **SED 阈值 0.5 是硬编码的** → 后面被 ACCDOA（连续 DOA 向量，长度=置信度）替代
6. **三声源以上场景基本无法处理** → Frame recall 70%（消声）→ 56%（混响）
7. **模型对训练数据的混响条件敏感** → 没有域自适应

## 九、跟哪篇像

**直接延续**:
- DOAnet → 同一个组，CRNN 用于纯 DOA → SELDnet 是 SELD 扩展
- MSEDnet → 同一个组的 SED baseline → SELDnet 的 SED 分支继承了它

**架构演进链**:
```
SELDnet (2018, CRNN, F→2)
    ↓
DCASE 2022 baseline (CRNN + temporal MHSA)
    ↓
DCASE 2023 baseline (CRNN + GRU + temporal MHSA)
    ↓
DST Attention (2023, 把 F→2 改 F→16, 加 S-MHSA)
    ↓
CST-former (2025, 加 C-MHSA + ULE + CMT)
```


### 6. 本论文在库中的位置关联

| 维度 | 论文 | 关系 |
|------|------|------|
| **前身/基石** | [[CRNN DOAnet 2017]] | 同一实验室（Tampere），DOAnet 提出 CRNN+Ambisonics 做纯 DOA → SELDnet 扩展为 SED+DOA 联合任务 |
| **前身/基石** | [[CNN DOA Estimation with Noise Training 2017]] | 借鉴了 STFT 相位作为输入表示的思想 |
| **后续/扩展** | [[PILOT Transformer SEL 2021]] | 用 Transformer Self-Attention 替换 BiGRU，解决 RNN 的长程依赖瓶颈 |
| **后续/扩展** | [[DST Attention 2023]] | 改小频率池化 (F'=2→16) + 新增 S-MHSA，解决 SELDnet 频率信息丢失问题 |
| **后续/扩展** | [[CST-former 2025]] | 在 DST 基础上加 C-MHSA 和 ULE，三维注意力 0.39M 超越所有大模型 |
| **后续/扩展** | [[SELD-Mamba 2024]] | 用 BMamba 替代 BiGRU，O(N) 复杂度 + 新增距离估计 (SDE) |
| **后续/扩展** | [[ResNet-Conformer SELD 2025]] | 走 EINV2 重模型路线 (85M)，用 Conformer 替代 BiGRU |
| **后续/扩展** | [[FA-Stateformer 2025]] | Bi-Mamba+ + SA 协同，时频分离注意力，当前纯 DOA 精度最优 |
| **同分支竞品** | 无 | 2018 年 SELD 方向唯一的工作——它是定义者 |
| **跨分支类比** | [[Multi-Speaker CNN DOA 2018]] | 同一年，都是 CNN 做 DOA，但 Chakrabarty 用相位图+ULA → SELDnet 用 FOA+幅度+相位+SED |

### 7. 江湖地位

```
2018 | SELD | 奠基任务定义+CRNN基线 → 所有后续 SELD 论文的对比 baseline
          → DCASE 2019-2022 Task 3 标准基线
          → 被 DST(2023)→CST(2025) 注意力线 + SELD-Mamba(2024)→FA-Stateformer(2025) SSM线 持续超越
```


---

*SELDnet 是 SELD 领域的"Hello World"。虽然它 2018 年的性能按现在的标准已经很差了（真实场景 DOA 33.7°），但它奠定了整个领域的技术范式：联合 SED+DOA、CRNN backbone、Cartesian 回归。后续所有工作都在此基础上做加法。理解 SELDnet，才能理解每一篇 SELD 论文的 baseline 是什么、大家在跟什么比。*
