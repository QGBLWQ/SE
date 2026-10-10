---
title: DST Attention 2023 — 分离式频谱-时间注意力用于 SELD
type: source
created: 2026-07-01
updated: 2026-07-01
tags:
  - seld
  - attention
  - spectro-temporal
  - dcase
  - transformer
source_type: paper
year: 2023
authors:
  - Yusun Shul
  - Byeong-Yun Ko
  - Jung-Woo Choi
affiliation: KAIST
venue: DCASE 2023 Challenge Technical Report
arxiv: "2306.02591"
related:
  - "[[CST-former 2025]]"
  - "[[SELD CRNN 2018]]"
  - "[[SELD 声事件定位与检测]]"
  - "[[ACCDOA]]"
---

# DST Attention — Divided Spectro-Temporal Attention for SELD

> Shul, Ko & Choi, KAIST. DCASE 2023 Challenge.

```yaml
- 论文: DST Attention (2023)
  ├── 要解决什么问题: SELD模型对特定房间混响过拟合；baseline只有时间注意力，没有频率注意力
  ├── 核心方法: 保留频率维度信息，在CRNN之后分别做S-MHSA(频率)和T-MHSA(时间)独立自注意力
  ├── 属于哪个分支: Transformer + CRNN 混合架构（尺寸注意力方向）
  ├── 输入/输出: Log-mel (4ch) + Intensity Vectors (3ch) = 7ch / ACCDOA & Multi-ACCDOA
  ├── 关键trick: 频率池化层kernel改小保留F'维度；S→T分离注意力顺序
  ├── 数据集: STARSS23 (dev-train), AudioSet+TAU-SRIR合成外部数据
  ├── 对比了谁: DCASE 2023 baseline (CRNN + temporal MHSA)
  ├── 性能上限: SELD score 0.4023 (Submission 1, 有aug+外部数据)
  ├── 参数量: 未明确报告（但baseline ~0.6M，DST稍大）
  ├── 消融关键发现: 频率维度大小F'=16最优；Multi-ACCDOA在无aug+外部数据时更好，但单ACCDOA+aug+外部数据最终更强
  ├── 遗留问题(你的机会): 只分解了S+T，缺少显式的Channel Attention；没有局部patch嵌入(ULE)；后处理增强有限
  └── 跟哪篇像: TimeSformer (视频S+T分解注意力) — DST将其迁移到音频SELD
```

## 一、研究任务与对象

| 维度 | 详情 |
|------|------|
| **任务** | SELD (Sound Event Localization and Detection) |
| **核心问题** | 减少模型对训练房间混响的过拟合 |
| **方法类型** | Divided S+T MHSA + CRNN backbone |
| **阵列类型** | FOA (4ch Ambisonics) |
| **输出格式** | ACCDOA / Multi-ACCDOA |
| **数据集** | STARSS23, 外部数据从 AudioSet + TAU-SRIR 合成 |
| **数据增强** | Frameshift, Time masking, Channel swap, Moderate mix-up |

## 二、整体架构

```
FOA 4ch音频 → STFT → 64-bin Log-mel + Intensity Vectors (7ch, T=250, F=64)
    │
    ▼
ConvBlock Encoder (CRNN风格):
  Conv2D × 3 (通道从7→64)
  频率池化: [2,2,1] 以保留F'=16维频率信息
  时间池化: [5,1,1]
  → 输出: (B=128, M=64, T/5=50, F'=16)
    │
    ▼
DST Attention Blocks × 2:
    │
    ├──→ S-MHSA (频率注意力)
    │      reshape: (B, M, T/5, F') → (B×T/5, F', M)
    │      注意力矩阵: F'×F'
    │      作用: 在同一时间帧内，不同频率bin之间交互
    │
    └──→ T-MHSA (时间注意力)
           reshape: (B, M, T/5, F') → (B×F', T/5, M)
           注意力矩阵: T/5 × T/5
           作用: 在同一频率bin上，不同时间帧之间交互
    │
    ▼
Linear → ACCDOA/Multi-ACCDOA输出 (39/117维)
```

## 三、为什么这么做？（Motivation）

1. **Baseline只有时间注意力**：DCASE 2023 baseline (CRNN + temporal MHSA) 在时序上做了注意力，但它通过频率池化把 F 压到只剩 2 维——频率信息几乎丢光了
2. **TimeSformer 的启发**：视频分类中把 Space 和 Time 的注意力分开做效果很好 → 音频也应该可以把 Frequency 和 Time 分开做
3. **减少过拟合**：不同房间的混响主要影响频率域的 pattern，如果能显式地对频率建模，模型可能对房间变化更鲁棒

## 四、之前的人怎么做不了？（Limitation → Gap）

| 方法                   | 能做               | 做不了                                  |
| -------------------- | ---------------- | ------------------------------------ |
| CRNN baseline        | 时间建模（RNN + MHSA） | 频率池化压到F'=2 → 没有显式频率建模的空间             |
| CRNN + temporal MHSA | 时间注意力            | 同上一频率信息在池化层就丢了                       |
| **DST Attention**    | **分别做S和T的注意力**   | **缺少通道注意力(C-MHSA)；没有局部patch嵌入(ULE)** |
|                      |                  |                                      |

**Gap**：在 SELD 任务中，如何在不堆参数的情况下，让频率和时间的注意力独立发挥作用？

## 五、这个做法核心 trick 是什么？

### 核心：频率维度保留 + S→T 分离注意力

**频率池化调整**是让一切成立的前提。

```
Baseline 的频率池化: [4,2,2] → 64→8→2 → F'=2   ← 频率丢光
DST 的频率池化:     [2,2,1] → 64→16→16 → F'=16  ← 保留了频率信息

从 F'=2 到 F'=16：
  - baseline: 注意力做不了频率方向（只剩2个token，没意义）
  - DST:      S-MHSA在16个频率token之间做注意力 ← 有意义！
```

**S→T 的顺序**（继承 TimeSformer）：
- 先做 S-MHSA：在同一帧内，16个频率 bin 之间交互 → 捕捉谐波结构
- 再做 T-MHSA：同一频率跨时间的交互 → 捕捉时间持续性

### 不是什么 trick？

- 不是 ViT 风格的大 patch embedding（没有 ULE）
- 不是 Conv-Transformer 交错（CMT Block）
- 没有多尺度（MSULE）
- 没有后处理增强（VTM, CTAI）——只有标准 ACCDOA
- **整体非常干净：1 个核心 idea（S+T 分离注意力）+ 1 个工程调整（频率池化改小）+ 数据增强**

## 六、实验里哪个消融最关键？

### 关键发现 1：频率维度大小 F' 的影响

表 4 (无数据增强/无外部数据)：

| F' | SELD Score (Multi-ACCDOA) | 含义 |
|:---:|:---:|------|
| 2 (baseline) | 0.4791 | 无频率注意力，参考值 |
| 8 | 0.4422 | ↓ 7.7% |
| **16** | **0.4345** | **↓ 9.3% ← 最优** |
| 32 | 0.4517 | 开始回升（过拟合？） |
| 64 | 0.4523 | 更差 |

> F'=16 是最优的。太大反而不好。因为频率 token 太多，注意力学不到有意义的关系，且参数增加导致过拟合。

### 关键发现 2：数据增强 + 外部数据的边际贡献

| 条件 | 最佳 SELD Score | 持续提升 |
|------|:---:|:---:|
| 仅 DST（无aug，无外部数据） | 0.4345 | Reference |
| + 数据增强 | 0.4215 | ↓ 3.0% |
| + 外部数据 | 0.4078 | ↓ 3.2% |
| + 700 epoch 训练（Submission 1） | **0.4023** | ↓ 1.4% |

> 数据增强和外部数据各自贡献了 ~3%。效果相当——说明过拟合确实是主要问题，两种方法都能缓解。

### 关键发现 3：Multi-ACCDOA vs Single-ACCDOA

| 条件 | 哪个更好 |
|------|---------|
| 无 aug + 无外部数据 | Multi 更好 (0.4345 vs 0.4423) |
| 有 aug + 外部数据 | **Single 更好** (0.4078 vs 0.4209) |

> 为什么？当没有数据增强时，Multi-ACCDOA 的排列不变学习(PIT)提供了额外的正则化。但当数据增强足够强时，Single-ACCDOA 更简单，训练更稳定。

## 七、整体结果

| 对比项 | Baseline | DST (Submission 1) | 提升 |
|-------|:-------:|:------------------:|:---:|
| SELD Score | 0.4791 | **0.4023** | **↓ 16%** |
| Error Rate | 0.570 | 0.495 | ↓ 13% |
| F-score | 29.90 | 42.68 | ↑ 43% |
| Loc. Error | 22.00° | 16.70° | ↓ 24% |
| Loc. Recall | 47.70 | 55.19 | ↑ 16% |

## 八、从 DST 到 CST-former 的改进对比

```
DST (DCASE 2023)                  →    CST-former (TASLP 2025)
──────────────────                     ────────────────────

只分解 S + T                      →    分解 C + S + T（加了通道注意力）

直接 flatten (7ch混入patch)        →    ULE（局部展开嵌入，保留通道结构）

标准 FFN                          →    CMT Block (LPU + IRFFN) → +7.7%

单尺度频率池化                     →    MSULE（多尺度并行窗口）

无后处理                           →    VTM + CTAI（向量阈值 + 聚类增强）

参数量 ~0.4-0.6M                  →    ~0.39M（基本持平）

SELD Score 0.4023                 →    SELD Score ~0.35-0.38（进一步↓22% vs baseline）

↓ 核心问题的继承：DST 证明 S+T 分离注意力比纯时间注意力好
  CST-former 在此基础上问：那再加个 C（通道）呢？
  → 实验回答：值得！Channel Attention 是最不能丢的维度
```

## 九、还剩什么问题没解决？（Future Work / Limitation）

1. **还是没有 Channel Attention**: 7 通道的麦克风信息在 ConvBlock 中被卷积混合，没有独立的通道间注意力 → CST-former 后来补上了
2. **频率维度 F' 的选择是经验性的**: F'=16 最优是通过实验穷举找到的，缺乏理论解释
3. **过拟合仍然存在**: 即使加了 4 种数据增强 + 外部数据，SELD score 0.4023 离完美还很远
4. **只在 FOA 上验证**: 其他阵列格式（MIC, ULA）未测试
5. **没有距离估计**: DCASE 2024 新增的 SDE（Sound Distance Estimation）未涉及
6. **模型复杂度较低但不是唯一焦点**: 参数量未报告，不像 CST-former 那样把"极致轻量"作为目标

## 十、跟哪篇像

**最像**: TimeSformer (Bertasius et al. 2021) — S+T 分离注意力的原始出处，DST 是从视频迁移到 SELD 的第一篇

**架构血统**:
- 前端 CRNN → DCASE baseline (Adavanne 2023)
- S+T 分离注意力 → TimeSformer + DASformer
- 输出格式 → ACCDOA / Multi-ACCDOA (Shimada 2021/2022)


### 6. 本论文在库中的位置关联

| 维度 | 论文 | 关系 |
|------|------|------|
| **前身/基石** | [[SELD CRNN 2018]] | 直接改进 SELDnet：保留 CRNN 前端，改频率池化 [8,8,2]→[2,2,1] + 新增 S+T 注意力 |
| **前身/基石** | [[CRNN DOAnet 2017]] | CRNN 前端设计的血统来源 |
| **后续/扩展** | [[CST-former 2025]] | 在 S+T 基础上增加 C-MHSA + ULE → 从二维→三维注意力，性能再提升 13% |
| **同分支竞品** | [[SELD-Mamba 2024]] | 同年（DCASE 2023/2024），DST 用 S+T Attention → SELD-Mamba 用 BMamba SSM |
| **同分支竞品** | [[ResNet-Conformer SELD 2025]] | 同年 DCASE 2024，DST 轻量 (0.3M) → ResNet-Conformer 重模型 (85M) |
| **跨分支类比** | [[FA-Stateformer 2025]] | 都是时频分离建模：DST 用 S-MHSA+T-MHSA → FA 用时频分离注意力+SSM |

### 7. 江湖地位

```
2023 | SELD | 频率保留+分离注意力 → 证明了"F'=16+S-MHSA 远比 F'=2+BiGRU 强"
          → 直接催生了 CST-former (2025) 的三维注意力
          → S+T 分离结构成为后续所有 SELD 架构的标准组件
```


---

*DST Attention 是 CST-former 的"直系前身"，两者出自同一团队（KAIST Choi 组）。它干净地验证了一个假设：把频率和时间注意力分开，比只做时间注意力好得多。CST-former 在这条路上又加了一个维度（C），从而达到了更极致的性能。*
