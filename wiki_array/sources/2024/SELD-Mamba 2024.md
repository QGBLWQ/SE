---
title: SELD-Mamba 2024 — 选择性状态空间模型用于 SELD
type: source
created: 2026-06-21
updated: 2026-07-02
tags:
  - seld
  - mamba
  - state-space-model
  - dcase-2024
  - distance-estimation
  - einv2
  - linear-complexity
source_type: paper
year: 2024
authors:
  - Da Mu
  - Zhicheng Zhang
  - Haobo Yue
  - Zehao Wang
  - Jin Tang
  - Jianqin Yin
affiliation: Beijing University of Posts and Telecommunications (BUPT)
venue: DCASE 2024 Workshop
arxiv: "2408.05057"
related:
  - "[[SELD CRNN 2018]]"
  - "[[CST-former 2025]]"
  - "[[FA-Stateformer 2025]]"
  - "[[EINV2]]"
  - "[[Mamba SSM 状态空间模型]]"
---

# SELD-Mamba — 首个将 Mamba/SSM 引入 SELD 的工作

> Mu et al., BUPT, 2024. **Mamba 首次应用于 SELD，用 O(N) 复杂度替代 O(N²)。**

```yaml
- 论文: SELD-Mamba (2024)
  ├── 要解决什么问题: Transformer (Conformer) 的 O(N²) 复杂度在长序列 SELD 中不实用；DCASE 2024 新增距离估计
  ├── 核心方法: EINV2 backbone + BMamba（双向 Mamba）替代 Conformer + 两阶段训练（先 SED+DOA，再加 SDE）
  ├── 属于哪个分支: Mamba/SSM 路线的 SELD 先行者（线性复杂度）
  ├── 输入/输出: Log-mel + 声强向量 = 7ch / track-wise (SED概率 + xyz + 距离)
  ├── 关键trick: BMamba (前向+后向 SSM) 替代 MHSA；两阶段训练（SED+DOA 先训练好，再追加 SDE）
  ├── 数据集: DCASE 2024 dev-set (STARSS23为基础, +合成数据), 无数据增强
  ├── 对比了谁: EINV2 原版 (Conformer)
  ├── 性能上限: 和 EINV2 可比，但参数更少；两阶段训练对 SDE 效果显著
  ├── 参数量: 比 EINV2 少（具体数值未报告，估计 < 40M）
  ├── 消融关键发现: BMamba 替代 Conformer → 参数更少+性能可比；两阶段训练优于联合训练
  ├── 遗留问题(你的机会): 没有和 FA-Stateformer 做对比 (两者都是 Mamba 路线但设计不同)；没有数据增强；SDE 仍然有提升空间
  └── 跟哪篇像: EINV2 (backbone) + FA-Stateformer (Mamba 路线但纯 DOA, 不是 SELD)
```

## 一、研究任务与对象

| 维度       | 详情                                                       |
| -------- | -------------------------------------------------------- |
| **任务**   | SELD + **距离估计 (SDE)** — DCASE 2024 Task 3                |
| **核心问题** | 用 Mamba (O(N) 线性复杂度) 替代 Conformer (O(N²) 二次复杂度)          |
| **方法类型** | EINV2 backbone + BMamba 替代 Conformer                     |
| **阵列类型** | FOA (4ch Ambisonics)                                     |
| **输出格式** | Track-wise (3 track, 每 track: SED概率 + 3D Cartesian + 距离) |
| **数据集**  | DCASE 2024 dev-set + 合成数据 (无数据增强)                        |
| **参数量**  | 比 EINV2 少（未精确报告，估计 ~30-40M）                              |

## 二、整体架构

```
FOA 4ch音频 → STFT → 128-bin Log-mel + 声强向量 = 7ch, (C=7, T, F=128)
    │
    ▼
Encoder: 三路 Dual Conv × 4
  SED分支: 只用 log-mel (4ch)         ← 声事件检测
  DOA分支: log-mel + 声强向量 (7ch)    ← 需要声强信息定位
  SDE分支: 只用 log-mel (4ch)         ← 距离估计
    │
  T-F Pooling (前三层) + F Pooling (末层)
  → 输出: (512, T/8, F/16) → 频率平均 → (T/8, 512)
    │
Cross-stitch (软连接) ← 分支间信息交换
    │
Decoder: BMamba × 3 (每 track 一个, 并行)
    │
    每个 BMamba Block:
    ├── Linear_expand (D→2D) + gate
    ├── Conv1D + SiLU
    ├── SSM (选择性扫描)
    ├── 门控输出 ⊗
    └── Linear_project (2D→D)
    │
    前向 Mamba + 后向 Mamba (两个独立 SSM)
    → 融合: 前向输出 + (反向输出 → reverse)
    │
FC → Track-wise 输出 (SED + xyz + 距离)
```

### Mamba 层的单步流程（Fig.2）

```
输入 u: (L, D)  ← L帧, D维
  │
  ├──→ Linear_input → û: (L, 2D) → Conv1D → SiLU → x: (L, 2D)
  │
  ├──→ Linear_gate → z: (L, 2D)
  │
  ▼
SSM(x):
  ├──→ Δ = softplus(Linear_Δ(x) + Param_Δ)   ← 选择性扫描 (时间步长)
  ├──→ B = Linear_B(x)                        ← 输入投影
  ├──→ C = Linear_C(x)                        ← 输出投影
  └──→ Discretize(Δ, A, B) → SSM → y_ssm
  │
  ▼
y = σ(SiLU(z)) ⊗ y_ssm      ← 门控
  │
  ▼
Linear_output → ŷ: (L, D)
```

## 三、为什么这么做？（Motivation）

1. **Conformer 复杂度太高**: MHSA 的 O(N²) 在长序列时计算量过大 → Mamba 的 O(N) 是解决方向
2. **Mamba 的选择性机制适合 SELD**: 动态地关注/忽略序列中的信息 = 对重叠声事件的检测有帮助
3. **距离估计需要两阶段训练**: SED+DOA 比 SDE 更难 → 第一阶段打好基础，第二阶段再追加距离

## 四、之前的人怎么做不了？（Limitation → Gap）

| 方法 | 能做 | 不能做 |
|------|------|--------|
| EINV2 (Conformer) | SED + DOA | O(N²) 复杂度；无距离估计 |
| CST-former | SED + DOA (轻量 C/S/T) | 无距离估计；没用 Mamba |
| ResNet-Conformer | SED + DOA + SDE | 参数巨大 (~50-85M) |
| FA-Stateformer | 纯 DOA (Mamba+SA) | 不是 SELD；不做 SED |
| **SELD-Mamba** | **SED+DOA+SDE；O(N)复杂度** | **无消融 BMamba 各组件贡献** |

## 五、核心 trick：两个

### Trick 1: BMamba 替代 Conformer

```
Conformer 的问题:
  MHSA = O(N²) → 长序列很贵
  Conv 模块 → 增加了参数和计算量

BMamba 的优势:
  SSM = O(N) → 长序列线性复杂度
  双向设计 → 前向+后向 → 利用了完整的时序上下文
  门控机制 → 动态选择关注/忽略哪些信息

替换策略:
  保留 EINV2 的 encoder (Dual Conv) → CNN 提取局部特征不变
  替换 decoder: Conformer → BMamba → 线性复杂度序列建模
```

### Trick 2: 两阶段训练

```
为什么需要两阶段?

  SED + DOA:  比较难，需要大量训练
  SDE:        比较容易（因为距离依赖混响和声强衰减模式）
  
  如果三个任务一起训练:
    SED+DOA 还没学好 → SDE 也没法学好
    (因为 SED 的错误会传导到 SDE)

两阶段训练:
  Stage 1: λ_SED=25, λ_DOA=5, λ_SDE=0  ← 集中精力学 SED+DOA
  Stage 2: λ_SED=25, λ_DOA=5, λ_SDE=3  ← 保持 SED+DOA, 再加入 SDE

  效果:
    SED+DOA 打好基础 → SDE 在稳定检测的基础上学距离
```

## 六、实验结果

### 关键对比

```
SELD-Mamba vs EINV2 (Conformer 原版):
  ✓ 参数更少 → 计算更高效
  ✓ 性能可比或更好 → 不牺牲精度换效率

两阶段训练 vs 联合训练:
  ✓ 两阶段对 SDE 任务效果显著更好
  ✓ SED+DOA 指标也更稳定（因为第一阶段集中训练了）
```

### 与 FA-Stateformer 的区别

|              | SELD-Mamba              | FA-Stateformer             |
| ------------ | ----------------------- | -------------------------- |
| **任务**       | SELD (SED+DOA+SDE)      | 纯 DOA                      |
| **Backbone** | EINV2 (CNN encoder)     | ResNet (深度下采样)             |
| **Mamba 位置** | Decoder (BMamba blocks) | Stateformer 内嵌 (Bi-Mamba+) |
| **自注意力**     | 不用 MHSA (全替换)           | 保留 MHSA（弥补 Mamba 局部不敏感）    |
| **数据增强**     | 无                       | 无                          |
| **短程补偿**     | 无显式机制                   | ShiftConv 时序偏移             |
| **距离估计**     | ✓                       | ✗                          |
| **参数量**      | ~30-40M                 | 2.2M                       |

→ **同一方向（Mamba 做定位）、不同架构设计、不同任务。SELD-Mamba 是大规模方案、FA-Stateformer 是轻量化方案。**

## 七、还剩什么问题没解决？

1. **没有显式局部补偿机制**: FA-Stateformer 用 ShiftConv 弥补 Mamba 的局部不敏感，SELD-Mamba 没有对应的设计 → 可能导致局部快速变化的声源精度不佳
2. **没有数据增强**: 和 DCASE 2024 的其他参赛系统（ResNet-Conformer 用了 4 种增强）相比，SELD-Mamba 在没有增强的情况下评估
3. **BMamba 各组件贡献未消融**: Conv1D 前处理、门控机制、双向设计各自贡献多少？论文没有拆
4. **两阶段训练的权重要靠经验**: λ₁=25, λ₂=5, λ₃=3 是试出来的，没有理论依据
5. **距离估计 (SDE) 仍然有改进空间**: 和 ResNet-Conformer 一样，SDE 是 DCASE 2024 最大的难点

## 八、跟哪篇像

**直接关系**:
- EINV2 (Cao 2021) — backbone，直接继承 encoder + 软连接设计
- FA-Stateformer (2025) — 同是 Mamba 路线，但任务不同 (纯 DOA vs SELD)
- ResNet-Conformer (2025) — 同参加 DCASE 2024，同做 SDE，但设计方案完全不同

**三者的关系**:
```
EINV2 (Conformer, O(N²))
    ├──→ SELD-Mamba (BMamba, O(N))  ← 替换 Conformer 为 Mamba
    └──→ ResNet-Conformer           ← 加强 Conformer + 数据增强
         (Conformer, O(N²), 更多参数)
    
FA-Stateformer (Bi-Mamba+ + SA)     ← 独立 Mamba 路线, 不同任务
```


### 6. 本论文在库中的位置关联

| 维度 | 论文 | 关系 |
|------|------|------|
| **前身/基石** | [[SELD CRNN 2018]] | 继承 SELDnet 的 CNN 前端 + 多任务框架，将 BiGRU 替换为 BMamba |
| **前身/基石** | [[Mamba SSM 状态空间模型]] | Mamba SSM 首次用于 SELD 任务——O(N) 线性复杂度替代 O(N²) 的 Transformer |
| **后续/扩展** | [[FA-Stateformer 2025]] | 改进 BMamba：增加 Bi-Mamba+ + Self-Attention 协同 + FA 时频分离模块 |
| **同分支竞品** | [[DST Attention 2023]] | DCASE 2023，DST 用 S+T Attention → SELD-Mamba 用 BMamba SSM |
| **同分支竞品** | [[CST-former 2025]] | DCASE 2024，SELD-Mamba 重模型 (~30M) → CST 轻量 (0.39M) |
| **同分支竞品** | [[ResNet-Conformer SELD 2025]] | DCASE 2024，SELD-Mamba 和它都加了距离估计 (SDE)——但两者 RDE 均无改善 (~0.32) |
| **跨分支类比** | 无 | Mamba SSM 在音频/语音领域的首次应用之一 |

### 7. 江湖地位

```
2024 | SELD | Mamba SSM 首次用于 SELD + 距离估计 → 被 FA-Stateformer(2025) 的 Bi-Mamba+ + SA 协同超越
          → 核心贡献：证明了 O(N) SSM 在 SELD 上可行，为 Mamba 线开创道路
          → 距离估计 RDE=0.32 和 baseline 一样——DCASE 2024 最大的开放问题
```


---

*SELD-Mamba 是 Mamba/SSM 在 SELD 领域的开篇，证明了用线性复杂度的 SSM 替代二次复杂度的 MHSA 是可行的。它的核心贡献不是"提出新架构"而是"证明了 Mamba 能够在 SELD 上击败 Conformer"。FA-Stateformer 在此基础上又往前走了一步——加了 SA 来弥补 Mamba 的局部不敏感。读这两篇，你就能看到"Mamba 路线在音频定位任务上的快速演进"。*
