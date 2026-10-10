---
title: ResNet-Conformer SELD 2025 — DCASE 2024 大模型基线 (EINV2 backbone)
type: source
created: 2026-06-21
updated: 2026-07-02
tags:
  - seld
  - dcase-2024
  - conformer
  - resnet
  - einv2
  - multi-accdoa
  - distance-estimation
  - data-augmentation
source_type: paper
year: 2025 (technical report for DCASE 2024)
authors:
  - Quoc Thinh Vo
  - David K. Han
affiliation: Drexel University
venue: DCASE 2024 Challenge Technical Report
arxiv: "2507.17941"
related:
  - "[[SELD CRNN 2018]]"
  - "[[CST-former 2025]]"
  - "[[EINV2]]"
  - "[[ACCDOA]]"
---

# ResNet-Conformer SELD — EINV2 + Conformer + 数据增强的工程化方案

> Vo & Han, Drexel University, DCASE 2024 Task 3A Technical Report.

```yaml
- 论文: ResNet-Conformer SELD (2024)
  ├── 要解决什么问题: DCASE 2024 新增距离估计(SDE)，需要一套工程化的 EINV2+数据增强方案
  ├── 核心方法: EINV2 backbone + ResNet + Conformer + 多尺度通道注意力 + 多阶段训练 + 大量数据增强
  ├── 属于哪个分支: 大参数量 EINV2 路线（工程方案，不是架构创新）
  ├── 输入/输出: Log-mel(4ch) + 声强向量(3ch) = 7ch / multi-ACCDOA (含距离估计)
  ├── 关键trick: ACS (Audio Channel Swapping) 8倍扩展数据；多阶段训练（合成数据初始化 → 真实数据+增强微调）；MS-CAM 多尺度通道注意力
  ├── 数据集: STARSS23 (dev-train+dev-test) + 合成数据 (AudioSet + TAU-SRIR)
  ├── 对比了谁: DCASE 2024 baseline
  ├── 性能上限: F20°=40.2%, DOA=17.5°, RDE=0.32 (距离估计无明显提升)
  ├── 参数量: 未明确报告 (~50-85M 量级, EINV2+ResNet+Conformer)
  ├── 消融关键发现: 多阶段训练 → +9.9% F-score；ACS+数据增强 → +7.2%；距离估计 RDE 在三个模型中都是 0.32-0.33 → 没进步
  ├── 遗留问题(你的机会): 距离估计 RDE 0.32 和 baseline 一样（完全没改善！这个方向的创新空间最大）；参数量巨大，无法实时部署
  └── 跟哪篇像: EINV2 (Cao 2021, backbone) + CST-former (对标，CST 说"我 0.39M 超过你 58M")
```

## 一、研究任务与对象

| 维度       | 详情                                                                          |
| -------- | --------------------------------------------------------------------------- |
| **任务**   | SELD + **距离估计 (SDE)** — DCASE 2024 Task 3 新增                                |
| **核心问题** | 在 STARSS23 上跑一个工程化的 EINV2+数据增强方案，重点是交付一个可用的参赛系统                             |
| **方法类型** | EINV2 two-branch + ResNet + Conformer + 多尺度通道注意力 + 多阶段训练                    |
| **阵列类型** | FOA (4ch Ambisonics)                                                        |
| **输出格式** | Multi-ACCDOA (含距离估计: a, R, D)  — 3 track × 13 class × (1+3+1) = 156 neurons |
| **数据集**  | STARSS23 + 合成数据 (AudioSet convolves with TAU-SRIR)                          |
| **数据增强** | Random cutout, noise injection, SpecAugment, ACS (8×扩展), random mix         |
| **参数量**  | **未明确报告，估计 50-85M** (EINV2 + ResNet + Conformer)                            |

## 二、整体架构

```
FOA 4ch音频 → STFT → 64-bin Log-mel(4ch) + 声强向量(3ch) = 7ch, (C=7, T, F=64)
    │
    ▼
Dual Conv × 4 (分支SED/DOA/SDE)
  SED分支: 只用 log-mel(4ch)          ← 只关心"什么声音"
  DOA分支: log-mel(4ch) + 声强向量(3ch) ← 需要声强信息用于定位
  SDE分支: 只用 log-mel(4ch)          ← 和 SED 一样
    │
Cross-stitch (软连接) ← 三个分支之间交换信息
    │
EINV2 两分支结构 + 共享权重
    │
ResNet Block ← 残差卷积下采样
    │
MS-CAM (多尺度通道注意力) ← 局部+全局通道特征融合
    │
Conformer Block (MHSA + Conv) ← 替代 GRU，8头，4层FFN扩张
    │
MaxPool (防止过拟合)
    │
FC → Multi-ACCDOA output (156 维, 3 track × 13 classes × (激活+xyz+距离))
```

### 与 CST-former 的架构对比

| | ResNet-Conformer | CST-former |
|---|---|---|
| **Backbone** | EINV2 two-branch | Single-branch Transformer |
| **注意力** | MHSA (Conformer 内) | C/S/T 三维独立 MHSA |
| **卷积补偿** | Conformer 内置 Conv 模块 | CMT Block (LPU+IRFFN) |
| **输出** | Multi-ACCDOA (含距离) | Multi-ACCDOA (无距离) |
| **训练** | 多阶段（合成→真实→增强） | 单阶段 |
| **数据增强** | ACS + SpecAugment + mix | 较少（论文重点不是增强） |
| **参数量** | ~50-85M | **0.39M** |
| **优势** | 工程化完整、距离估计 | 轻量、智能架构设计 |

## 三、为什么这么做？（Motivation）

1. **DCASE 2024 新增距离估计**：之前的 ACCDOA 只输出 (x,y,z)，现在还要输出距离 → 输出维度翻倍
2. **EINV2 是已验证的成熟框架**：Cao et al. 2021 的两个分支+软共享设计在 SELD 上表现好 → 不想 reinvent the wheel
3. **数据增强比架构改进更可控**：参赛系统的重点在"怎么把现有模型训练好"，而不是"设计新架构"

## 四、之前的人怎么做不了？（Limitation → Gap）

| 方法 | 能做 | 做不了 |
|------|------|--------|
| EINV2 原版 | SED + DOA | 无距离估计；无 Conformer |
| DCASE 2023 baseline | SED + DOA (single-ACCDOA) | 无距离估计；CRNN backbone |
| CST-former | SED + DOA (multi-ACCDOA) | 无距离估计；不做数据增强 |
| **ResNet-Conformer** | **SED + DOA + SDE；EINV2+Conformer** | **参数巨大；距离估计无改善** |

## 五、核心 trick：不是架构创新，是工程堆叠

这篇论文的"创新"其实是**工程方案**，至少有 4 个 tricks 叠在一起：

### Trick 1: Audio Channel Swapping (ACS) — 数据 8 倍扩展

```
ACS: 交换 4 个 Ambisonics 通道的排列
  因为 Ambisonics 的 4 个通道有方向性（WXYZ）
  交换它们 = 模拟不同的声源方向
  4 个通道有 24 种排列 → 论文用了 8 种
  
  → 训练数据直接 8 倍
  → 成本：0 参数（纯数据增强）
```

### Trick 2: 多阶段训练（合成→真实→增强）

```
Phase 1: 合成数据 (AudioSet+TAU-SRIR) 初始化权重
Phase 2: 真实数据 (STARSS23) + 去增强 微调
Phase 3: 真实数据 + ACS + random mix 最终训练

Model 1 (无多阶段): F=23.1%
Model 2 (合成初始化+无ACS): F=33.0%   ← +9.9%
Proposed (合成初始化+ACS): F=40.2%      ← +7.2% over Model 2

→ 多阶段训练和 ACS 各自贡献显著
```

### Trick 3: MS-CAM (多尺度通道注意力)

```
标准通道注意力 (SE): 全局平均池化 → FC → sigmoid → 逐通道乘回
MS-CAM: 局部(小卷积) + 全局(大池化) → 拼接 → 融合 → 通道权重

→ 同时捕捉局部通道关系（相邻通道 3×3）和全局通道关系（全频率）
→ 作用：SED 和 DOA 分支之间的信息共享更有效
```

### Trick 4: Conformer 替换 GRU

```
EINV2 原版: GRU + MHSA
ResNet-Conformer: Conformer (MHSA + Conv 模块)
→ 和 CST 一样的选择：用卷积补偿注意力对局部细节的丢失
```

## 六、消融/实验结果

### 训练策略对比

| Model | F-score | DOA | RDE | 关键变化 |
|-------|:------:|:---:|:---:|------|
| Baseline | 13.1% | 36.9° | 0.33 | DCASE 2024 官方基线 |
| Model 1 | 23.1% | 25.3° | 0.33 | 无多阶段、无增强 |
| Model 2 | 33.0% | 20.7° | 0.32 | + 合成数据初始化 |
| **Proposed** | **40.2%** | **17.5°** | **0.32** | + ACS + 增强 |

### 最关键的发现

```
距离估计 (RDE) 在所有模型中都是 0.32-0.33
→ 完全没有改善！
→ Baseline 已经做到了 RDE=0.33
→ 加了数据增强、多阶段训练、ACS — 还是 0.32

这说明了:
  (a) SDE 任务和架构/数据增强关系不大
  (b) 或者距离估计需要完全不同的特征或训练方式
  (c) 这个方向的创新空间最大 → 你的机会！
```

## 七、和 CST-former 的对比意义

```
为什么 CST 要一直对标 ResNet-Conformer?

  ResNet-Conformer: ~50-85M 参数, F-score ~40%
  CST-former:        0.39M 参数, F-score ~ comparable levels
  
  CST 说: "我参数比你少 150 倍，性能不比你的差"
  但 CST 没做距离估计，而 ResNet-Conformer 做了

→ 如果 CST 要扩展到距离估计:
  需要改输出头（Multi-ACCDOA → add SDE dimension）
  但轻量化 design 在距离估计上可能没有数据增强有效
  → 未解决的 tension
```

## 八、还剩什么问题没解决？

1. **距离估计 RDE=0.32** — 和 baseline 一样，完全没有改善！这是整个 DCASE 2024 最大的开放问题
2. **参数巨大**（~50-85M）— 无法部署到移动设备，CST 对标的就是这个
3. **没有消融掉架构的具体贡献** — MS-CAM 和 Conformer 各自贡献多少？论文没做消融
4. **依赖大量数据增强** — ACS + SpecAugment + random mix + 合成数据 = 四个增强叠加 → 真正的模型能力被增强覆盖了
5. **只在 FOA 上验证** — 其他阵列未测试

## 九、跟哪篇像

**最像**: 
- EINV2 (Cao 2021) — 直接继承 backbone
- CST-former (2025) — 轻量化路线的对标对象
- SELD-Mamba (2024) — 另一个 EINV2 变体（用 Mamba 换 Conformer）


### 6. 本论文在库中的位置关联

| 维度 | 论文 | 关系 |
|------|------|------|
| **前身/基石** | [[SELD CRNN 2018]] | 血统来源——SELD 任务定义和 CRNN 基线 |
| **前身/基石** | [[EINV2]] | 直接继承 EINV2 双分支架构 + cross-stitch |
| **前身/基石** | [[SELD-Mamba 2024]] | 同年 DCASE 2024 的竞品——ResNet-Conformer 也加了 SDE |
| **同分支竞品** | [[CST-former 2025]] | DCASE 2024 轻量方案：ResNet-Conformer 85M → CST 0.39M 但性能翻倍 |
| **同分支竞品** | [[FA-Stateformer 2025]] | 纯 DOA SOTA，FA 精度更高且参数更少 (2.2M) |
| **跨分支类比** | [[DBnet Beamforming 2020]] | 都走"大模型 + 数据增强 + 工程化"路线，不做架构创新 |

### 7. 江湖地位

```
2025 | SELD+SDE | DCASE 2024 工程方案 → EINV2+Conformer+数据增强，85M 参数
          → 距离估计 RDE 无改善——暴露了 SDE 任务的本质困难
          → 被 CST-former(0.39M) 用 1/150 参数超越 → 证明"堆参数"路线已走到尽头
```


---

*ResNet-Conformer 代表了 DCASE 2024 的"大模型工程路线"：拿 EINV2 + Conformer + 堆数据增强 → 交付一套可用的参赛系统。它更像是一份"how to win DCASE"的工程手册，而不是架构创新论文。CST-former 是它的轻量化对标——用 1/150 的参数达到可比性能。两者的竞争代表 SELD 的两条路线：堆资源 vs 巧设计。*
