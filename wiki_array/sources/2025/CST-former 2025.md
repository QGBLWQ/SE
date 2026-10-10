---
title: CST-former 2025 — 多维注意力 Transformer 用于 SELD
type: source
created: 2026-06-21
updated: 2026-07-20
tags:
  - seld
  - transformer
  - multidimensional-attention
  - dcase
  - real-scenes
  - lightweight
source_type: paper
year: 2025
authors:
  - Yusun Shul
  - Dayun Choi
  - Jung-Woo Choi
affiliation: KAIST
venue: IEEE/ACM TASLP 2025 (extended from ICASSP 2024)
arxiv: "2504.12870"
code:
related:
  - "[[SELD CRNN 2018]]"
  - "[[DST Attention 2023]]"
  - "[[SELD-Mamba 2024]]"
  - "[[ResNet-Conformer SELD 2025]]"
  - "[[FA-Stateformer 2025]]"
  - "[[wiki/concepts/log-mel 频谱]]"
  - "[[wiki_array/concepts/SELD 声事件定位与检测]]"
  - "[[wiki_array/concepts/ACCDOA]]"
---

```yaml
- 论文: [CST-former](2025)
  ├── 要解决什么问题: 现有 SELD 模型不是太重 (58-85M) 就是注意力只做在时间维——空间(C)和频率(S)维的信息从未被独立建模
  ├── 核心方法: C+S+T 三维独立自注意力 + ULE (局部 T-F patch 嵌入) + CMT Block (卷积局部增强)，总参数量仅 0.39M
  ├── 属于哪个分支: SELD / 轻量 Transformer / 多维注意力分解 / FOA 阵列
  ├── 输入/输出: 7ch log-mel+GCC-PHAT (C=7, T, F=64) → Multi-ACCDOA (SED + DOA)
  ├── 关键trick: ① ULE — 局部 T-F patch 展平成 token，信息量 40× 传统 token ② C+S+T 独立 MHSA — 三个小矩阵替代一个大矩阵 ③ CMT Block (LPU+IRFFN) — 卷积补偿 Transformer 的局部盲区
  ├── 数据集: STARSS22, STARSS23, TAU-NIGENS (DCASE)
  ├── 对比了谁: CRNN baseline, ResNet-Conformer (58M), EINV2 (85M), DST Attention, SELD-Mamba
  ├── 性能上限: SELD Score 相对 2022 baseline ↓22.1% (0.39M 超 85M EINV2)
  ├── 参数量: 0.39M (CRNN baseline 的 65%, ResNet-Conformer 的 1/150)
  ├── 消融关键发现: CMT Block 贡献最大 (+7.7pp) / ULE +1pp over DCA / 三维注意力的 T 和 S 维度贡献小于 C（空间信息是 SELD 核心）
  ├── 遗留问题(你的机会): ① C+S+T 分解 vs FullSubNet 全带+子带——同构的"分治"哲学跨域迁移 ② ULE vs 子带滑动窗口——可学习 patch 替代手工 K=15 ③ 0.39M 的参数效率对增强方向有直接迁移价值 ④ 论文没做三维去掉任何一个的消融（只展示累加，没展示拆解）
  └── 跟哪篇像: [[DST Attention 2023]](前身，S+T 分离注意), [[FullSubNet 2021]](跨域——频率+时间分治，类似哲学), [[CMGAN 2022]](跨域——Conformer 的 MHSA+Conv，类似但不同维度)
```

# CST-former: Channel-Spectro-Temporal Transformer for SELD

> Shul, Choi & Choi, KAIST. ICASSP 2024 → IEEE/ACM TASLP 2025

## 1. 动机：他们为什么这么做？

CST-former 的动机可以概括为三句话：

**① SELD 模型陷入"参数军备竞赛"。** ResNet-Conformer 58M、EINV2 85M——这些模型根本不可能跑在移动设备或边缘节点上。轻量化不是"优化项"而是"能不能用的硬条件"。

**② 注意力全做在时间维，浪费了输入的结构。** FOA 输入是 7ch × T × F 的三维张量——通道编码空间方向，频率编码频谱内容。把三维 flatten 成 1D token 序列再做 attention，等于把"频率变化"和"通道差异"两维的信息混在一起扔给模型自己理。注意力机制的设计没有匹配数据的结构。

**③ 参数效率是"分解"的副产品。** 一个直接在三维 flatten 上做的 MHSA，复杂度是 O((T×F)²)。把三个维度分开做——C-MHSA 管通道间关系、S-MHSA 管频率间关系、T-MHSA 管时间间关系——复杂度变成 O(C² + S² + T²) = O(49 + 4096 + T²)，大幅降低。

```
直接 3D attention:  (T×F)² 个 attention 对
C+S+T 分解 attention: C² + F² + T² 个 attention 对

以 T=200, F=64, C=7:
  直接:  (12800)² ≈ 1.64 亿
  分解:  49 + 4096 + 40000 ≈ 4.4 万
        ↑ 参数减少约 3700 倍
```

这不是"为了省参数而省参数"——分解是更好的**归纳偏置**：通道、频率、时间是三种不同物理含义的维度，强制它们共享同一个注意力矩阵没有道理。

## 2. 前人局限：之前的人怎么做不了？

### Gap 的本质

SELD 社区从 2018 到 2024 年，注意力机制的演进只走了"一条半"路：

```
DCASE 2018-2022:   纯时间维建模 (CRNN, BiGRU)
DCASE 2023:        S+T 分离注意力 (DST)
                  ↑ 只把频率从时间里拆出来了
                  通道(C)维始终被忽略
```

**为什么 C 维被忽略？** 两个原因：

1. **SELD 的 CRNN 基因**：CRNN baseline 的 CNN 前端自动混合了通道，后续 RNN 只管时间。这导致社区形成了"通道融合=CNN 的事"的思维惯性——没人想过 attention 可以也做在通道维上
2. **ULE 是"先有答案再找问题"**：在 ULE 之前，如果直接对 7ch × T × F 的 token 做 channel attention，一个 token 只有 7 维——信息太少，attention 没意义。ULE 把局部 patch (7×P_T×P_F=280 维) 编码成一个 token 后，channel attention 才变得有价值。ULE 是 C-MHSA 的"前置条件"

### 前人方法一览

| 方法                      |    C (空间)    | S (频率) |   T (时间)    |  参数量  | 关键局限                   |
| ----------------------- | :----------: | :----: | :---------: | :---: | ---------------------- |
| CRNN (2018)             |   ❌ CNN 隐式   |   ❌    |   ✅ BiGRU   | 0.60M | 只有时间建模                 |
| PILOT (2021)            |      ❌       |   ❌    |   ✅ MHSA    |  >1M  | Transformer 但只做时间      |
| DST (2023)              |      ❌       | ✅ MHSA |   ✅ MHSA    | 0.30M | 缺通道维——空间信息未被独立建模       |
| ResNet-Conformer (2025) |      ❌       |   ❌    | ✅ Conformer |  58M  | 参数爆炸                   |
| EINV2 (2025)            | ✅ Track-wise |   ❌    |   ✅ MHSA    |  85M  | C 维隐含在 track 结构中，但参数过多 |

**Gap**：没有人同时做 C+S+T 三维独立注意力，也没有人证明分解注意力 = 轻量 + 高性能可以兼得。

## 3. 核心 Trick：这个做法关键在哪？

CST-former 的方法论是"三个维度各自独立做注意力 + 局部 patch 嵌入提供信息量"。不是叠 trick，而是**结构本身的选择就是 trick**。

| 优先级 | Trick | 做什么 | 为什么关键 |
|:---:|------|------|------|
| ⭐⭐⭐ | **C+S+T 三维独立 MHSA** | 三组小注意力矩阵各自负责一个维度的交互 | 分解 = 归纳偏置 = 参数降 3700× + 更易学 |
| ⭐⭐⭐ | **ULE (展开局部嵌入)** | 局部 T-F patch → 展平 → 线性投影 → token | C-MHSA 的前置条件——不给足够信息 C attention 没意义 |
| ⭐⭐ | **CMT Block (LPU+IRFFN)** | 3×3 depthwise conv + 倒残差 FFN | 消融贡献最大 (+7.7pp)——Transformer 缺局部感知，CMT 补上 |
| ⭐ | **T-F Pooling Middle** | 中间层对 T-F 做池化 | 收尾工程优化 |
| ⭐ | **MSULE (多尺度 ULE)** | 多个 patch 尺寸并行 | TASLP 扩展版新增，提升 attribution 不透明 |

### 整体架构

```
FOA 4ch 音频 → STFT
    │
    ├→ 4ch log-mel  (C=4, T, F=64)
    ├→ 3ch 强度向量  (C=3, T, F=64)
    │
    ▼  拼接为 C=7
输入: [7, T, 64]
    │
    ▼  ConvBlock Encoder (可选 Front/Middle/End 位置做 T-F 池化)
    │
    ▼  CST-former Block × N
    │   ┌─────────────────────────────────────────┐
    │   │  ULE: 对每个 (t,f) 位置取本地 patch        │
    │   │    patch = input[:, t:t+P_T, f:f+P_F]    │
    │   │    unfold → Linear → token               │
    │   │                                           │
    │   │  C-MHSA: token 间的通道交互               │
    │   │    (学"4ch log-mel 和 3ch GCC 如何配合")    │
    │   │                                           │
    │   │  S-MHSA: 频率维自注意力                   │
    │   │    (学"65Hz 的嗡嗡声和高频嘶嘶声的关系")     │
    │   │                                           │
    │   │  T-MHSA: 时间维自注意力                   │
    │   │    (学"敲门声的起振→持续→衰减"时间模式)      │
    │   └─────────────────────────────────────────┘
    │
    ▼  CMT Block (LPU + IRFFN)
    │   3×3 depthwise conv → 补偿 Transformer 的局部盲区
    │   倒残差 FFN → 类似 MobileNet 的高效特征变换
    │
    ▼  FC → Multi-ACCDOA
输出: SED (哪个类别) + DOA (哪个方向)
```

### 三个 MHSA 的具体操作（张量形状追踪）

三个 MHSA 操作的维度不同——C-MHSA 做在 ULE 的 patch 内部（趁 C 维还在），S/T-MHSA 做在 token grid 上。下面以具体数字追踪全过程。

**假设**：C=7, T=200, F=64, P_T=10, P_F=4, D=256, n_heads=4, d_head=64。

---

#### 阶段 0：ULE — 为每个 (t, f) 位置生成 token（C 维还未消除）

```
对位置 (t=50, f=30):
  input[:, 50:60, 30:34] → patch [7, 10, 4]
  
  reshape: [7, 10, 4] → [7, 40]   ← 保留 C=7 维，空间展平为 40
               ↑         ↑
             7 个通道   每通道 40 维（=P_T×P_F）
```

此时整个输入变成了 `T×F = 12800` 个这样的 patch，每个形状 `[7, 40]`。

---

#### 阶段 1：C-MHSA — 通道维注意力（在 patch 内部做）

对于**每一个** (t,f) 位置的 patch `[7, 40]`，C-MHSA 把 7 个通道当作 7 个 token 做自注意力：

```
┌──────────────────────────────────────────────────────┐
│  C-MHSA (对单个 (t,f) 位置的 patch)                     │
│                                                       │
│  输入: [7, 40]                                         │
│    token_0 (log-mel ch1):  [40 维 — 该通道在本地 T-F 的信息]
│    token_1 (log-mel ch2):  [40 维]                     │
│    token_2 (log-mel ch3):  [40 维]                     │
│    token_3 (log-mel ch4):  [40 维]                     │
│    token_4 (GCC-PHAT ch1): [40 维 — GCC 的空间信息]     │
│    token_5 (GCC-PHAT ch2): [40 维]                     │
│    token_6 (GCC-PHAT ch3): [40 维]                     │
│                                                       │
│  Linear projections (weights shared across all 12800 patches):
│    Q = [7, 40] × W_Q → [7, 256]  (4 heads × 64)       │
│    K = [7, 40] × W_K → [7, 256]                       │
│    V = [7, 40] × W_V → [7, 256]                       │
│                                                       │
│  Attention:                                            │
│    [7, 7] = softmax(Q·K^T / √64)                      │
│              ↑ 7 个通道两两之间的注意力权重               │
│                                                       │
│  "log-mel ch1 问：我应该关注哪些通道？"                 │
│  → 给 GCC-PHAT ch1 高分（"你的空间信息告诉我方向"）     │
│  → 给 log-mel ch4 中分（"同是幅度信息，互补"）          │
│                                                       │
│  Output: [7, 256] = attention_weights × V             │
│           ↑ 7 个通道各自的"跨通道增强后"的表示            │
└──────────────────────────────────────────────────────┘
```

**为什么 7 个 token 的 attention 有意义？** 7 个通道各有独特物理含义——4 个 log-mel（Ambisonics 的 4 个指向性分量）编码"各个方向听到的频谱"，3 个 GCC-PHAT 编码"声波到达不同方向的时延差"。C-MHSA 学的是"WGCC 告诉你声音从左边来 → 应该更信任 log-mel 的左通道分量"——这就是空间信息和频谱信息在 attention 中的融合。

**C-MHSA 之后**：7 个通道的输出被聚合成 1 个 token（如平均池化或拼接+线性投影）：

```
[7, 256] → aggregate → [256]  ← 这就是 (t=50, f=30) 的最终 token
```

对所有 T×F 个位置并行做同样的操作（权重共享），得到 token grid：**`[T=200, F=64, D=256]`**。

---

#### 阶段 2：S-MHSA — 频率维自注意力

现在有 `[T, F, D]` 的 token grid。S-MHSA 沿**频率轴**做 attention——每个时间帧独立地让 64 个 mel 频带互相 attend：

```
┌──────────────────────────────────────────────────────┐
│  S-MHSA (对每一帧 t 独立做)                              │
│                                                       │
│  对 t=50 (第 50 帧):                                   │
│    取出该帧所有频率的 token: [F=64, D=256]               │
│                                                       │
│    token_f0  (低频, ~0 Hz):      [256 维]              │
│    token_f1  (次低频, ~31 Hz):   [256 维]              │
│    ...                                                 │
│    token_f63 (高频, ~8 kHz):     [256 维]              │
│                                                       │
│    Q = [64, 256] × W_Q → [64, 256]                    │
│    K = [64, 256] × W_K → [64, 256]                    │
│    V = [64, 256] × W_V → [64, 256]                    │
│                                                       │
│    Attention: [64, 64]                                │
│                                                       │
│  "低频嗡嗡声问：频谱上还有谁？"                          │
│  → 高频嘶嘶声（共同来自同一噪声源）→ 中分               │
│  → 中频共振峰（这是语音的结构）→ 高分                   │
│                                                       │
│  Output: [64, 256]                                    │
│  ↑ 每个频率现在知道自己与整条频谱上其他频率的关系         │
└──────────────────────────────────────────────────────┘
```

对 T=200 帧，每帧独立做一次 S-MHSA（200 次，权重共享），输出仍是 `[T, F, D]`。

**S-MHSA 替代了什么？** 等价于 FullSubNet 全带模型的"降采样+插值"功能——让每个频率 bin 获得全局频谱上下文，但**不需要池化、不损失频率分辨率**。

---

#### 阶段 3：T-MHSA — 时间维自注意力

在 `[T, F, D]` token grid 上，T-MHSA 沿**时间轴**做 attention——每个频率 bin 独立地让 T 个时间帧互相 attend：

```
┌──────────────────────────────────────────────────────┐
│  T-MHSA (对每个频率 f 独立做)                            │
│                                                       │
│  对 f=30 (第 30 个 mel 频带):                           │
│    取出该频率所有帧的 token: [T=200, D=256]              │
│                                                       │
│    token_t0   (第 0 帧):    [256 维]                   │
│    token_t1   (第 1 帧):    [256 维]                   │
│    ...                                                 │
│    token_t199 (第 199 帧):  [256 维]                   │
│                                                       │
│    Q = [200, 256] × W_Q → [200, 256]                  │
│    K = [200, 256] × W_K → [200, 256]                  │
│    V = [200, 256] × W_V → [200, 256]                  │
│                                                       │
│    Attention: [200, 200]                              │
│                                                       │
│  "t=80 帧问：在我之前和之后发生了什么？"                 │
│  → t=50-70（敲门声起振）→ 高分                          │
│  → t=150（敲门声已消失）→ 低分                          │
│                                                       │
│  Output: [200, 256]                                   │
│  ↑ 每一帧现在知道自己与整个时间序列中其他帧的关系         │
└──────────────────────────────────────────────────────┘
```

对 F=64 个频带，每个独立做一次 T-MHSA（64 次，权重共享），输出仍是 `[T, F, D]`。

---

#### 总结：三个注意力各自管什么

```
C-MHSA:  attention over C=7  (在 patch 内部, 趁 C 维还在)
          → "log-mel 和 GCC-PHAT 如何配合来推断方向"

S-MHSA:  attention over F=64 (在 token grid 的频率轴上)
          → "这个低频嗡嗡声和高频嘶嘶声来自同一个声源"

T-MHSA:  attention over T=200 (在 token grid 的时间轴上)
          → "敲门声在 t=50 开始, t=80 达到峰值, t=120 结束"
```

**注意**：S-MHSA 和 T-MHSA 的权重是分别独立的——S-MHSA 的 W_Q/W_K/W_V 只用于频率维，T-MHSA 有自己的一套。三组 MHSA 学到的是三种不同物理含义的交互模式。

### ULE — 为什么它是核心创新的前置条件

传统的 token 化：`(7, T, F) → flatten → 每个 (t,f) 位置是一个 7 维 token`。7 维做 attention，太单薄。

ULE 的做法：在每个 (t,f) 位置，切一个 `7 × P_T × P_F` 的 3D patch，展平成 `280` 维，再线性投影到 `256` 维。这个 256 维 token 编码了局部邻域的全部信息——通道关系、时间纹理、频率纹理都在里面。

```
传统 token: [t=50, f=30] → 7 个数（该位置 7 个通道的值）
ULE token:  [t=50, f=30] → 7×10×4=280 个数展平→256 维
                           ↑ 40× 信息量，且来自连续局部区域
```

C-MHSA 只有在这之后才有意义——如果 token 只有 7 维，channel attention 最多能做的是"给 7 个通道排序"，ULE 让 token 变成了"带局部纹理的丰富表示"，channel attention 才能学到复杂的跨通道交互模式。

### CMT Block — 消融贡献最大但论文关注不够

CMT Block 在消融中贡献了 +7.7pp（ULE→CMT 的提升），远超 ULE 自身的贡献（+1.0pp over DCA）。但论文的叙事重心在 ULE 和三维注意力上——因为 CMT 是借来的组件（Guo et al. 2022），ULE 是原创。

这是一个有趣的信号：**Transformer 在 SELD 上最大的痛点不是"注意力维度不够"，而是"局部感知能力不足"**。3×3 depthwise conv 这一个小操作贡献了全模型提升的约 1/3。

## 4. 消融分析：哪个设计最敏感？

### 逐步累加消融（DCASE 2022）

| 配置 | SELD Score↓ | 增量 |
|------|:---:|:---:|
| 2022 Baseline (CRNN, 0.60M) | Reference | — |
| + Temporal MHSA (2023 baseline) | ↓ 6.3% | +6.3 |
| + DST Attention (S+T 分离) | ↓ 9.0% | +2.7 |
| + DCA (Divided Channel Attention) | ↓ 11.1% | +2.1 |
| + **ULE** (Channel Attention with ULE) | ↓ 12.1% | **+1.0** |
| + **CMT Block** (LPU + IRFFN) | ↓ 19.8% | **+7.7** |
| + T-F Pooling Middle (final) | ↓ 22.1% | +2.3 |

### 敏感度排序

1. **CMT Block** — 最敏感（+7.7pp）。Transformer + 局部卷积 = 1+1>2。这一项的贡献比 ULE + DST + DCA 三项加起来还大
2. **Temporal MHSA** — 高度敏感（+6.3）。从 CRNN 到加时间注意力是第一大步——定位事件的起止边界必须靠时间建模
3. **DCA / ULE** — 低度但必要（合计 +3.1）。ULE 的绝对值不大（+1.0 over DCA），但它是 C-MHSA 能工作的前提
4. **T-F Pooling** — 边际收益（+2.3）。工程收尾

### 论文没有报告但至关重要的消融

- **单独去掉 C / S / T 中的任何一个**：论文只展示了"累加"（逐项加模块），没有做"拆解"（从完整的 CST 中去掉 C）。无法判断三个维度的独立贡献比例——我们只知道累加提升，不知道哪个维度丢不起
- **ULE 的 P_T 和 P_F 敏感度**：P_T=10、P_F=4 是最优吗？如果只用 P_T=5 或 P_F=2 呢？
- **CMT Block 的 LPU vs IRFFN 各自贡献**：+7.7pp 里多少来自 depthwise conv？多少来自倒残差 FFN？
- **S-MHSA 是否需要？** T-MHSA 和 C-MHSA 的贡献已被累加消融覆盖，但 S-MHSA 夹在中间——它可能被 CMT Block 的局部 conv 部分替代（conv 天然有频率局部性）

## 5. 遗留问题：还剩什么没解决？

### 论文自己承认的局限

1. **未做距离估计 (SDE)**：DCASE 2024 新增任务，CST 架构目前不支持距离维
2. **仅限 FOA**：Ambisonics 4ch 格式，未在 ULA/UCA 等其他阵列上测试
3. **域自适应空白**：训练（合成）→ 测试（真实）的 gap 无显式处理
4. **SELD Score 离饱和还很远**：~0.42 vs 理想值 0，约走了 60% 的路

### 读出来的隐藏问题

5. **三维注意力的贡献分解被"累加消融"掩盖**：论文的消融是逐步加模块（基线→+T→+S+T→+C→+ULE→+CMT），无法回答"如果去掉 S-MHSA 会掉多少"。这导致读者无法判断三个维度的真实价值排序
6. **ULE 的设计选择缺少理论支撑**：为什么是 unfold 而不是 3D conv？为什么是 patch 而不是 pixel-wise？论文缺少和 ViT-style patch embedding 的对比
7. **0.39M = 不一定是最优体系**：CMT Block 贡献最大（+7.7pp），说明"轻量不是架构天生的，是 CMT 带来的"。如果换一个更强的局部增强模块（比如 Mamba 的 SSM），参数可能更少且性能更好
8. **C+S+T 分解 = 归纳偏置提升，但通用性待验证**：这个设计假设了 C/S/T 三个维度是近似独立的。在 FOA 上成立（通道 = Ambisonics 编码的空间信息），但在任意阵列几何上是否成立？
9. **对语音增强的直接迁移价值未被讨论**：FullSubNet 的频率分治（全带+子带）和 CST 的 S-MHSA（频率注意力）+ ULE（局部 T-F patch）是高度同构的设计——CST 可以视为 FullSubNet 的"自动分解"版本。这个跨域连接全篇未提
10. **TASLP 版 tricks 叠得太多**：ICASSP 2024 原版只有 ULE + C+S+T + CMT。TASLP 2025 版加了 MSULE、VTM、CTAI——后两个是后处理，提升的归因不透明

### 这些 gap 如何被后续填补

| Gap | 潜在填补方向 | 难度 |
|-----|---------|:---:|
| 三维贡献分解 | 单独去掉 C/S/T 的消融（任何后续工作都可以补） | 低 |
| ULE vs 3D conv vs ViT patch | 消融对比实验 | 低 |
| C+S+T → 增强 | [[全带与子带模型]] + S-MHSA + ULE 的跨域迁移（见本笔记附录） | 中 |
| CMT → Mamba SSM | 局部增强模块的升级消融 | 低 |
| TASLP 版 trick 归因 | 回退到 ICASSP 2024 原版做 clean ablation | 低 |

---

## 6. 本论文在库中的位置关联

| 维度 | 论文 | 关系 |
|------|------|------|
| **前身/基石** | [[DST Attention 2023]] | 直接继承 S+T 分离注意力 → 加 C-MHSA + ULE → 三维独立 |
| **前身/基石** | [[SELD CRNN 2018]] | 血统源头：CNN 前端 + 多任务头保持 CRNN 架构风格 |
| **同分支竞品** | [[SELD-Mamba 2024]] | 同年，CST 用 C+S+T Attention (0.39M) vs Mamba 用 SSM (~30M)——不同路线但都追求轻量 |
| **同分支竞品** | [[ResNet-Conformer SELD 2025]] | 同年 DCASE 2024，CST 0.39M 超 85M EINV2 2 倍——参数量 vs 性能的反直觉对比 |
| **同分支竞品** | [[FA-Stateformer 2025]] | 同年，FA Mamba+SA 协同，精度更高但 CST 的分解范式更简洁 |
| **跨分支类比** | [[FullSubNet 2021]] | **最重要的跨域连接**：FullSubNet 的频率分治 vs CST 的 C+S+T 分解——同为"分而治之"哲学在不同域的实现。See 附录 |
| **跨分支类比** | [[CMGAN 2022]] | Conformer 的 MHSA+Conv 混合 vs CST 的 MHSA+CMT——都是"注意力+卷积局部增强"的组合但维度不同 |

## 7. 江湖地位

> **2025 | SELD | 0.39M C+S+T 三维独立注意力 → 1/150 参数超越 85M EINV2** → CST-former 的核心遗产是证明了**三维分解注意力 = 更好的归纳偏置 + 极致的参数效率**，打破了"高性能=大模型"的假设。ULE 是原创贡献（局部 patch 嵌入→channel attention 获得足够信息量），但消融揭示的最关键组件其实是借来的 CMT Block（+7.7pp）。
>
> **跨域迁移价值**：CST 的 S-MHSA (频率注意力) + ULE (局部 T-F patch) 天然是 [[FullSubNet 2021]] 全带+子带模型的"自动分解版"——频率注意力替代降采样+插值，ULE 替代手工 K=15 窗口。这是增强和定位之间最直接的架构迁移路径之一。
>
> **对标关系**：如果 [[SELD-Mamba 2024]] 代表了"用 SSM 替代 Transformer"的路线，CST-former 代表了"把 Transformer 拆得更聪明"的路线。0.39M vs 30M 的参数对比暗示：2025 年的赢家不一定是 Mamba vs Transformer，而是**谁会做结构分解**。

---

## 附录：CST-former 对语音增强的启发

> Written 2026-07-20. 详细分析见 [[全带与子带模型]] 级联 vs 并行部分。

CST-former 的三维分解注意力与 FullSubNet 的全带+子带分解有高度同构性：

| CST-former | FullSubNet | 启发 |
|---|---|---|
| **S-MHSA**（频率自注意力） | 全带模型（Conv2D 降采样 + LSTM + 插值） | 频率注意力替代降采样——保留 F=257 分辨率的同时拥有全局视野 |
| **ULE**（局部 T-F patch 嵌入） | 子带模型（手工 K=15 滑动窗口） | 可学习 patch 替代固定窗口——不同频率自适应窗口大小 |
| **C-MHSA**（通道注意力） | — (单通道 SE 无此维) | 可退化为特征通道注意力（SENet-style） |
| **CMT Block**（LPU 局部卷积） | — (LSTM 本身有时序局部性) | LPU 可以作为子带 LSTM 的补充或替代 |
| 0.39M | 5.6M | CST 的参数效率多半来自分解——增强也可以"少即是多" |

**最建议的消融实验**：把 FullSubNet 的全带分支（Conv2D→LSTM→插值→concat）替换为 S-MHSA+T-MHSA，子带分支保持不变。最小改动，检验"频率注意力能否替代频率池化"。
