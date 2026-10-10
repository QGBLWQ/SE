---
title: CMGAN — Conformer + 度量GAN语音增强
type: source
created: 2026-07-06
updated: 2026-07-14
tags:
  - speech-enhancement
  - conformer
  - gan
  - metric-optimization
  - transformer
  - perceptual-loss
source_type: paper
year: 2022
authors: Ruizhe Cao, Sherif Abdulatif, Bin Yang (Universität Stuttgart)
venue: IEEE/ACM TASLP 2022
code: https://github.com/ruizhecao/CMGAN
related:
  - [[wiki/concepts/语音增强评价指标]]
  - [[wiki/concepts/STFT与频谱图]]
  - [[MetricGAN+ 2021]]
  - [[MP-SENet 2023]]
  - [[PHASEN 2020]]
  - [[DCCRN 2020]]
---

```yaml
- 论文: [CMGAN](2022)
  ├── 要解决什么问题: MetricGAN+ 证明了"训练目标对了比架构强了更重要"，但它的 backbone 只是简单 BLSTM——如果把 backbone 也升级到最强，两重增益叠加会怎样？
  ├── 核心方法: Conformer 编码器-解码器替代 CRNN + MetricGAN 感知指标训练 = 首次把 Transformer 级别的骨干和 GAN 指标优化结合
  ├── 属于哪个分支: 语音增强 / Conformer / GAN / 感知指标优化 / 时频域
  ├── 输入/输出: 带噪 STFT 幅度谱 (F×T) → Conformer Encoder-Decoder → 增强幅度 mask → mask × |X| → iSTFT (带噪相位)
  ├── 关键trick: ① Conformer 块 (MHSA + Conv + FFN 三合一) ② MetricGAN 双目标训练 (Metric loss + MSE 正则) ③ 编码器-解码器 skip connections
  ├── 数据集: Voice Bank + DEMAND (PESQ), DNS Challenge (DNSMOS), VCTK (泛化测试)
  ├── 对比了谁: SEGAN, MetricGAN+, DCCRN, PHASEN, FullSubNet, DEMUCS, 多个 CRN 变体
  ├── 性能上限: PESQ=3.41, CSIG=4.47, CBAK=3.91, COVL=3.89 (Voice Bank+DEMAND SOTA at submission)
  ├── 参数量: G ≈ 1.8M (Conformer-based)
  ├── 消融关键发现: Conformer→CRNN: PESQ 3.41→3.25 (–0.16) / 去掉 MetricGAN 仅 MSE: 3.41→3.15 (–0.26) / 4头→8头: 3.35→3.41 (+0.06) → **训练目标贡献 (0.26) > 架构贡献 (0.16)**
  ├── 遗留问题(你的机会): ① 幅度-only, 相位未处理 → 被 MP-SENet 接力的原因 ② 训练成本极高 (GAN交替 + Conformer双重开销) ③ 实时性未验证 ④ Conformer的"卷积+注意力"混合设计 vs 全注意力 vs Mamba — 没有三方消融
  └── 跟哪篇像: [[MetricGAN+ 2021]](训练范式), [[MP-SENet 2023]](继承感知目标, 加相位), [[TF Attention Module 2023]](同年, CRNN+注意力, 不同路线)
```

# CMGAN: Conformer-based Metric GAN for Speech Enhancement

> Ruizhe Cao, Sherif Abdulatif, Bin Yang, IEEE/ACM TASLP 2022

## 1. 动机：他们为什么这么做？

CMGAN 的动机可以浓缩为一个不等式：

```
MetricGAN+ (2021):  好目标 × 弱 backbone  = PESQ 3.15
DCCRN (2020):      弱目标 × 好 backbone  = PESQ 3.01

问题: 好目标 × 好 backbone = ?
```

MetricGAN+ 证明了**训练目标比 backbone 重要**（用最普通的 BLSTM 拿到了 3.15，超越同年所有精心设计的架构）。但这留下了一个自然的问题：**如果我把 backbone 也升级，两重增益能不能叠加？**

CMGAN 的回答：**能。** Conformer（从 ASR 借来的最强序列模型）+ MetricGAN 训练 = PESQ 3.41。Conformer 贡献 +0.16，MetricGAN 贡献 +0.26——两者近乎独立叠加。

**比数字更重要的是方法论**：CMGAN 结束了语音增强"修目标还是修架构"的路线之争——答案是"两个都修"。

## 2. 前人局限：之前的人怎么做不了？

**Gap 的本质**：在 CMGAN 之前，"更强的 backbone"和"更好的训练目标"是两条**被不同社区分别推动的独立研究线**，从未在同一篇论文里出现。

| 研究线 | 代表 | 贡献 | 缺什么 |
|--------|------|------|--------|
| **训练目标线** | MetricGAN+ (2021) | D 学 PESQ → G 朝感知方向优化 | backbone 太弱（BLSTM） |
| **架构线（相位）** | DCCRN (2020) | 复数 CRN 保留幅度-相位耦合 | 训练目标仍是 MSE |
| **架构线（注意力）** | Conformer (ASR, 2020) | MHSA+Conv 混合块 | 没被用在 SE，也没配上感知损失 |

为什么之前没人同时做？两个原因：

1. **社区隔阂**：MetricGAN 的训练范式（两个模型交替训练、经验回放、PESQ 标签）在增强社区是小众路线。做 Conformer 的人来自 ASR 社区，不熟悉 MetricGAN；做 MetricGAN 的人用 BLSTM 已经拿到了 SOTA，没有动力换 backbone
2. **训练成本恐惧**：Conformer 本身的训练就比 CRNN 慢，再加上 MetricGAN 的交替训练——两者叠加的训练时间可能是普通 MSE 训练的 5-10 倍。需要足够的算力才敢尝试

CMGAN 的贡献就是**打破了这个隔阂**——证明了更强的 backbone + 更好的训练目标 = 1+1>2。

## 3. 核心 Trick：这个做法关键在哪？

CMGAN 的方法论是"取两个已有组件，证明它们可叠加"。但 Conformer 块本身的设计也需要理解：

### Conformer 块内部

```
输入 (F×T, C=64)
  ↓
 ┌─ LayerNorm → MHSA (8 heads, 64-dim) → Dropout ─┐
 │                                                  ├→ 残差 +
 └────────────────────────────────────────────────┘
  ↓
 ┌─ LayerNorm → ConvModule ─────────────────────────┐
 │   Pointwise(64→128) → GLU → Depthwise(3×3)      │
 │   → BatchNorm → Swish → Pointwise(128→64)        ├→ 残差 +
 └────────────────────────────────────────────────┘
  ↓
 ┌─ LayerNorm → FFN (64→256→64, Swish) ────────────┐
 │                                                  ├→ 残差 +
 └────────────────────────────────────────────────┘
  ↓
输出: 同样形状 (F×T, C=64)
```

**三个子模块的分工**：

| 子模块 | 做什么 | 对应语音增强的什么需求 |
|--------|--------|---------------------|
| **MHSA** (多头自注意力) | 全局交互——每个 T-F bin 可以和**任意距离**的其他 bin 直接通信 | 长程依赖：一个音素跨越 50 帧 → 注意力直接连过去 |
| **ConvModule** (深度可分离卷积) | 局部模式——3×3 核在 T-F 邻域滑动 | 短时谱纹理：谐波间距、共振峰斜率在 3×3 邻域即可识别 |
| **FFN** (前馈网络) | 非线性特征变换 + 维度扩展 | 每个 bin 独立做通道混合 |

### 为什么这种"混合"比单纯的 Transformer 或 CNN 都好？

```
纯 Transformer (如 SepFormer):       纯 CNN (如 Conv-TasNet):
  全局强, 局部弱                       局部强, 全局弱
  "知道第 50 帧和第 200 帧的关系"      "知道 3×3 邻域是谐波峰"
  "但不知道 3×3 邻域是谐波峰"         "但不知道第 50 帧和第 200 帧的关系"

Conformer = 两者取长补短:
  MHSA 负责"跨时刻说话人追踪" (全局)
  Conv 负责"局部谐波/共振峰识别" (局部)
  FFN 负责"对每个 bin 做精细决策"
```

### 完整架构

```
┌───────────────────────────────────────────────────┐
│                   CMGAN                              │
│                                                      │
│  带噪幅度谱 [F, T]                                    │
│      │                                                │
│  ┌───▼───────────────────────────────────────────┐  │
│  │  Conv2D Encoder × 4:                           │  │
│  │  [257,T,1] → [129,T,16] → [65,T,32]            │  │
│  │  → [33,T,64] → [17,T,64]                       │  │
│  │                                                │  │
│  │  Encoder 的 Conv2D 先做频率降采样                │  │
│  │  同时提取浅层 T-F 特征                           │  │
│  └───┬───────────────────────────────────────────┘  │
│      │ 特征: [17, T, 64]                              │
│  ┌───▼───────────────────────────────────────────┐  │
│  │  Conformer Blocks × 4:                          │  │
│  │  MHSA → ConvModule → FFN → 残差                 │  │
│  │  沿 T 轴展开做 attention, F 轴保留                │  │
│  │  → 全局时序建模 + 局部谱纹理                      │  │
│  └───┬───────────────────────────────────────────┘  │
│      │                                                │
│  ┌───▼───────────────────────────────────────────┐  │
│  │  ConvTranspose2D Decoder × 4:                   │  │
│  │  [17,T,64] → ... → [257,T,1]                    │  │
│  │  + skip connections from Encoder                │  │
│  └───┬───────────────────────────────────────────┘  │
│      │                                                │
│  mask [257, T] → Ŝ_mag = mask ⊙ |X|                   │
│  带噪相位 φ_X → iSTFT → 增强波形                      │
└───────────────────────────────────────────────────┘
```

### 训练：MetricGAN 模式（继承自 MetricGAN+）

和 MetricGAN+ 完全相同的框架——区别只在于 G 从 BLSTM 换成了 Conformer Encoder-Decoder：

$$\mathcal{L}_G = -\gamma \cdot \underbrace{D(G(x), y)}_{\text{Metric loss}} + \underbrace{\text{MSE}(G(x), y)}_{\text{正则}}$$

| 优先级 | Trick | 来源 | 作用 |
|:---:|------|------|------|
| ⭐⭐⭐ | **Conformer backbone** | ASR | 比 BLSTM 更强的全局+局部联合建模 |
| ⭐⭐⭐ | **MetricGAN 训练** | MetricGAN+ | 直接优化 PESQ 而非 MSE |
| ⭐⭐ | **Encoder-Decoder + skip** | U-Net | 多尺度特征保留 |
| ⭐ | **γ 衰减策略** | 自创 | 训练初期多靠 MSE 稳定，后期多靠 Metric loss 冲刺 PESQ |

## 4. 消融分析：哪个设计最敏感？

CMGAN 的消融实验有一个**反直觉的核心发现**：

| 消融项 | PESQ | Δ | 结论 |
|--------|:---:|:---:|------|
| **CMGAN 完整 (Conformer + MetricGAN)** | **3.41** | — | baseline |
| Conformer → CRNN (保留 MetricGAN) | 3.25 | –0.16 | 架构贡献 |
| 去掉 MetricGAN → 纯 MSE (保留 Conformer) | 3.15 | **–0.26** | **目标贡献 > 架构贡献** |
| MetricGAN+ (BLSTM + MetricGAN) | 3.15 | –0.26 | baseline 对比 |
| 4 头 → 8 头 (MHSA heads) | 3.35 | +0.06 | 注意力头数有收益但递减 |
| 不同的 Conformer 块数 | 2 块: 3.30 / 4 块: 3.41 / 6 块: 3.40 | — | 4 块甜点 |

**核心结论：训练目标的贡献（0.26）仍然大于架构的贡献（0.16）。** 这和 MetricGAN+ 论文的发现一致——但 CMGAN 证明了"两者可以叠加"：

```
MSE baseline (CRNN):              2.86
  + MetricGAN 训练:                3.15  (+0.29)
  + 换 Conformer backbone:         3.41  (+0.26)
  = 总计:                         +0.55 PESQ
```

**论文没有报告但值得追问的消融：**
- Conformer 的 ConvModule 是否是必需的？换成纯 MHSA + FFN 会怎样？（即纯 Transformer 替代 Conformer）
- Conformer vs SepFormer-style Dual-Path Transformer 的对比
- 在更大数据集（DNS 500h）上，目标贡献 vs 架构贡献的比例是否会变化？（数据集增大 → MSE 更强 → 目标贡献缩小？）
- MetricGAN 训练的 γ 衰减策略的消融

## 5. 遗留问题：还剩什么没解决？

### 论文自己承认的局限

1. **幅度-only, 相位未处理**：这是 CMGAN 被 MP-SENet (2023) 超越的直接原因——MP-SENet 加了幅相并行解码，PESQ 3.41→3.50
2. **训练成本极高**：Conformer + GAN 交替训练——两个最耗时的组件叠加。论文未报告训练时间，但估算至少是普通 MSE 训练的 5-10 倍
3. **实时性未验证**：Conformer 的 MHSA 是 O(T²)，离线 OK，实时需要改成因果版本或流式 Conformer

### 读出来的隐藏问题

4. **Conformer 的 MHSA 在短序列上可能浪费**：CMGAN 处理的 Voice Bank 句子通常 <5 秒，T≈200-300 帧。在这个长度下，MHSA 的 O(T²) 完全可承受，但它的全局注意力优势也没有完全发挥——200 帧用 Bi-LSTM 也能很好建模。Conformer 真正的优势场景是 DNS Challenge 的长句（10s+），但 CMGAN 在 DNS 上的评估不够深入
5. **"架构贡献 vs 目标贡献"的结论可能数据集依赖**：Voice Bank+DEMAND 只有 28 个说话人，PESQ 的评估方差较高。在更大、更嘈杂的数据集上，MSE 训练的 Conformer 可能离 MetricGAN 训练的 Conformer 更近——意味着"目标贡献"被高估了
6. **Conformer + MetricGAN 的组合 = 不可复现的高计算门槛**：两个高成本组件叠加 → 只有少数算力充裕的实验室能复现和迭代。这在客观上导致了这条路线在 CMGAN 之后只有一篇主要后继 (MP-SENet)，而 MP-SENet 其实放弃了 GAN 交替训练转用更简单的多级损失
7. **Conformer 的"卷积+注意力"混合设计尚未被 Mamba 挑战**：2024 年 Mamba for SE 证明了 SSM 可以替代 Transformer。但 Conformer 的 ConvModule 和 Mamba 的 SSM 是否互补或冗余？三方消融 (Conformer vs Mamba vs Transformer) 从未做过
8. **CMGAN → MP-SENet 的演化逻辑暗示了一个更深的问题**：MP-SENet 继承了 CMGAN 的感知优化目标（在微调阶段保留 MetricGAN 训练），但主干换了 Transformer + 幅相并行。这意味着 CMGAN 的核心遗产**不是 Conformer，而是证明了"目标+架构可以叠加"的方法论**

### 这些 gap 如何被后续工作填补

| Gap | 填补工作 | 年份 |
|-----|---------|------|
| 幅度-only → 幅相并行 | [[MP-SENet 2023]] 加相位并行解码, PESQ 3.41→3.50 | 2023 |
| Conformer → Mamba | Mamba for SE (2024) 用 SSM 做增强 | 2024 |
| Conformer vs SepFormer | 从未做过——不同任务不同数据集，正面比较困难 | — |

---

## 一、研究任务与对象

| 维度 | 详情 |
|---|---|
| **任务** | 单通道语音增强，指标驱动 (PESQ) 训练 + Conformer backbone |
| **输入** | STFT 幅度谱 (F×T, F=257) |
| **输出** | 增强幅度 mask (sigmoid) → mask × \|X\| → iSTFT (带噪相位) |
| **采样率** | 16 kHz |
| **数据集** | Voice Bank + DEMAND (主), DNS Challenge, VCTK (泛化) |
| **核心指标** | PESQ=3.41, CSIG=4.47, CBAK=3.91, COVL=3.89 |

## 二、关键结果

| 方法 | PESQ | CSIG | CBAK | COVL | 参数量 |
|------|:----:|:----:|:----:|:----:|:---:|
| Noisy | 1.97 | 3.35 | 2.44 | 2.63 | — |
| SEGAN | 2.16 | 3.14 | 2.61 | 2.43 | — |
| DCCRN | 3.01 | — | — | — | 3.7M |
| MetricGAN+ | 3.15 | 4.14 | 3.42 | 3.53 | 3M |
| FullSubNet | 2.98 | — | — | — | 5.6M |
| **CMGAN** | **3.41** | **4.47** | **3.91** | **3.89** | **~1.8M** |
| *MP-SENet (2023)* | *3.50* | *4.58* | *4.01* | *3.98* | *~4M* |

> CMGAN 的 1.8M 参数拿到 3.41 PESQ——比 DCCRN (3.7M, 3.01) 和 MetricGAN+ (3M, 3.15) 都更高效。Conformer 的参数效率优势明显。

## 三、可复现性

| 项目 | 详情 |
|------|------|
| **代码** | 开源: `github.com/ruizhecao/CMGAN` (PyTorch) |
| **训练** | MetricGAN 交替训练, γ 从 0.01 逐步增加到 1.0 |
| **优化器** | Adam, G: lr=1e-4, D: lr=5e-5 |
| **训练时间** | 未报告（估算 5-10× MSE 训练时间） |
| **窗口** | 32ms Hanning, 50% overlap, 512-FFT |

## 四、本论文在库中的位置关联

| 维度 | 论文 | 关系 |
|------|------|------|
| **前身/基石** | [[MetricGAN+ 2021]] | 完整继承 MetricGAN 训练范式（D 做 PESQ 代理、交替训练 G/D、经验回放） |
| **前身/基石** | Conformer (ASR, 2020) | 借用 Conformer 块的 MHSA+Conv+FFN 三合一设计 |
| **后续/扩展** | [[MP-SENet 2023]] | 继承感知优化目标，但主干换成 Transformer + 幅相并行解码, PESQ 3.41→3.50 |
| **同分支竞品** | [[TF Attention Module 2023]] | 同年，CRNN+注意力，比 CMGAN 更轻量但指标略低 |
| **同分支竞品** | [[CRAFT 2022]] | 同年，CRNN+Cross-Attention，不同路线 |
| **跨分支类比** | [[ResNet-Conformer SELD 2025]] | SELD 也独立用 Conformer——跨领域趋同但 CMGAN 先做了 |

## 五、江湖地位

> **2022 | 语音增强 | "目标+架构"双优路线的奠基者 → PESQ=3.41 (Voice Bank+DEMAND SOTA)** → CMGAN 的核心遗产不是 Conformer 这个具体架构，而是证明了 **MetricGAN 的感知目标 + 强 backbone = 1+1>2**。这个方法论直接影响了 [[MP-SENet 2023]]（保留 Metric 训练、换 Transformer）。在它之前，路线之争是"修目标 vs 修架构"；在它之后，共识变成"两个都修"。
>
> **最被低估的发现**：训练目标贡献 (0.26) 仍然大于架构贡献 (0.16)。在这个意义上，CMGAN 本质上是一篇"用更强架构验证 MetricGAN+ 正确性"的论文——它证明了那篇 INTERSPEECH 短文的核心思想值得被认真对待。
>
> **对标关系**：如果 [[Conv-TasNet 2019]] 在分离方向提出"TCN 替代 LSTM"，[[DCCRN 2020]] 在增强方向提出"复数网络保留相位"，CMGAN 则在训练范式方向提出"Conformer + MetricGAN 双重增益叠加"。这三个是不同维度上的里程碑式证明——架构维度、相位维度、目标维度。
