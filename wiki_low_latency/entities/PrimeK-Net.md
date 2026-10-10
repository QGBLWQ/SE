---
title: PrimeK-Net
type: entity
paper: "PrimeK-Net: Multi-scale Spectral Learning via Group Prime-Kernel Convolutional Neural Networks for Single Channel Speech Enhancement"
year: 2025
venue: ICASSP 2025
created: 2026-09-27
updated: 2026-09-27
tags:
  - speech-enhancement
  - prime-kernel
  - multi-scale
  - two-stage
  - non-causal
  - GPU
  - model
sources:
  - [[wiki_low_latency/sources/2025/PrimeK-Net 2025]]
related:
  - [[wiki_low_latency/sources/2025/PrimeK-Net 2025]]
  - [[wiki_low_latency/concepts/2502.19906-prime-kernel-multiscale-dense-block]]
  - [[wiki_low_latency/entities/LaCo-SENet]]
  - [[wiki_low_latency/sources/2026/LaCo-SENet 2026]]
---

# PrimeK-Net

## 定义

**PrimeK-Net** 是一个用于单通道语音增强的**两阶段（two-stage, TS）时频域模型**，由 Lin 等（ICASSP 2025）提出。它的核心是两个替换式设计：

1. **GPFCA**（Group Prime-kernel Feed-Forward Channel Attention，组质数核前馈通道注意力）——替换 TS 结构里的 **Conformer**，用线性的通道注意力 + 四组不同**质数核**的深度门控前馈网络；
2. **DSDDB**（Deep Separable Dilated Dense Block，深度可分离空洞密集块）——替换编码/解码器里的 **DDB**，把空洞卷积分解为 depthwise + pointwise。

公开战绩：**VoiceBank+DEMAND 上 PESQ 3.61 / CSIG 4.81 / CBAK 3.98 / COVL 4.35，参数量 1.41 M，FLOPs 44.64 G。**

> [!important] 在本库中的角色：**非因果质量上界**
> PrimeK-Net **不是低时延模型**。它没有因果性声明、没有任何延迟数字、没有 RTF、没有硬件、没有量化、没有流式讨论。
> 它在库中存在的意义是：**它是 [[wiki_low_latency/entities/LaCo-SENet]] 直接沿用的骨干**，因此 LaCo-SENet Table 1 里的「PrimeK-Net 非因果上界 3.61」就是指它。
> ⇒ **库内由此获得一个罕见的配对对照**：同一骨干、同一损失的**非因果上界（3.61）vs 因果 12.5 ms（3.35）** ⇒ **"未来上下文"的价格 ≈ 0.26 PESQ**。
> 详见 [[wiki_low_latency/sources/2025/PrimeK-Net 2025]]。

## 证据

### 一、论文级事实（来自 arXiv:2502.19906 v1）

| 项 | 内容 |
|---|---|
| 全称 | PrimeK-Net: Multi-scale Spectral Learning via Group Prime-Kernel Convolutional Neural Networks for Single Channel Speech Enhancement |
| 作者 | Zizhen Lin（四川大学电子，一作）· Junyu Wang（天津大学智算）· **Ruili Li（东北大学医学，通讯）** · Fei Shen（南理工计算机）· Xi Xuan（**中国香港**城市大学翻译及语言学系） |
| 发表 | **ICASSP 2025**（arXiv Comments 字段逐字：`This paper was accepeted by ICASSP 2025`，原文拼写错误） |
| arXiv | 2502.19906（**v1，2025-02-27**）；类别 `eess.AS` + `cs.SD` |
| DOI（arXiv） | `10.48550/arXiv.2502.19906` |
| DOI（ICASSP 正式版） | **未核验**（无本地正式版 PDF） |
| 页数 | 5 页（正文 4 页 + 参考文献 1 页） |
| 代码 | https://github.com/huaidanquede/PrimeK-Net （论文脚注 1 给出） |
| PDF 元数据 | creator `LaTeX with hyperref` · producer `pdfTeX-1.40.25` · 生成时间 `2025-02-28T01:37:22Z` |

> [!question] 作者署名里有一个易误读处
> 第 5 作者 Xi Xuan 的机构是 **City University of Hong Kong, Hong Kong SAR, China**。按本库规范应写为 **中国香港城市大学**。
> 通讯作者标记（`*Corresponding author.`）落在 **Ruili Li（Tohoku University，日本）** 上。

### 二、模型规模（三档，论文明确）

| 配置 | 参数量 | FLOPs | PESQ | CSIG | 出处 |
|---|---|---|---|---|---|
| **PrimeK-Net-S**（1 个 GPFCA module） | **0.79 M** | **26.45 G** | 3.53 | 4.76 | Table I（$\mathcal{L}_{\text{old}}$） |
| **PrimeK-Net**（2 个 GPFCA modules，默认） | **1.41 M** | **44.64 G** | **3.57**（$\mathcal{L}_{\text{old}}$）/ **3.61**（$\mathcal{L}_{\text{new}}$） | **4.79 / 4.81** | Table I / Table II |
| PrimeK-Net + DDB（消融替换） | 2.37 M | 未报告 | 3.61（不变） | 4.82 | Table II |

> [!note] 「PrimeK-Net-S 是 1 个 GPFCA module」这个信息**只出现在 Table I 的表题里**
> 论文正文 §II 从未说明默认的 GPFCA 堆叠数。这是**唯一**能推出 "2 个" 的地方（因为 Table III 的 (3,11,23,31) 是四个核 × 分组，与 GPFCA 数量无关）。
> 按库内纪律，此处**只记录推论来源，不当作正文事实**。

### 三、完整结果表

#### Table I —— 同框架同损失的三方对照（$\mathcal{L}_{\text{old}}$）

| Model | PESQ | CSIG | FLOPs | Para. |
|---|---|---|---|---|
| Noisy | 1.97 | 3.35 | — | — |
| MP-SENet [5] | 3.50 | 4.73 | 74.52 G | 2.05 M |
| SE-Mamba [16] | 3.52 | 4.75 | 65.46 G | 2.25 M |
| PrimeK-Net-S | 3.53 | 4.76 | 26.45 G | 0.79 M |
| **PrimeK-Net** | **3.57** | **4.79** | 44.64 G | 1.41 M |

> 表题逐字：「To ensure a fair comparison, the methods listed in this table use the **same loss function** (Without Consistency Loss and with Time Loss).」
> 三模型同用 TS 框架，内部组件分别为 **Conformer / Mamba / GPFCA**，编解码器分别为 **DDB / DDB / DSDDB**。

#### Table II —— 模块消融（默认 $\mathcal{L}_{\text{new}}$，除特别标注）

| Model | PESQ | CSIG | CBAK | COVL | Para. |
|---|---|---|---|---|---|
| **PrimeK-Net** | **3.61** | **4.81** | **3.98** | **4.35** | 1.41 M |
| GPFN → Wide FFN | 3.51 | 4.74 | 3.93 | 4.27 | **1.41 M** |
| DSDDB → DDB | 3.61 | 4.82 | 3.98 | 4.36 | **2.37 M** |
| w/o SCA | 3.42 | 4.70 | 3.82 | 4.16 | 1.34 M |
| w/o CL | 3.59 | 4.79 | 3.95 | 4.32 | 1.41 M |
| w/o CL + w/ TL（= $\mathcal{L}_{\text{old}}$） | 3.57 | 4.79 | 3.97 | 4.30 | 1.41 M |

#### Table III —— 核尺寸消融（**FLOPs 与参数三行完全相同**）

| Kernel Size | 类型 | PESQ | CSIG | FLOPs | Para. |
|---|---|---|---|---|---|
| (17, 17, 17, 17) | 单尺度 | 3.57 | 4.77 | 44.64 G | 1.41 M |
| (5, 15, 21, 27) | 非质数多尺度 | 3.59 | 4.79 | 44.64 G | 1.41 M |
| **(3, 11, 23, 31)** | **质数多尺度** | **3.61** | **4.81** | 44.64 G | 1.41 M |

### 四、参数效率分析（**本页独立计算，论文未做**）

把 Table II 的三行转成"每份参数买到多少 PESQ"：

| 模块 | 参数增量 | PESQ 贡献 | 结论 |
|---|---|---|---|
| **SCA**（通道注意力） | **+0.07 M** | **+0.19** | ⭐ 性价比最高：5% 的参数换 0.19 PESQ |
| **GPFN**（vs Wide FFN） | **0 M** | **+0.10** | 零参数代价的改进 |
| **DSDDB**（vs DDB） | **−0.96 M** | 0.00 | 省 68% 参数不损质量 |

⇒ **GPFN 与 DSDDB 都是"零/负参数代价的改进"；SCA 是唯一真正花参数但买到最多质量的地方。**
**这个读法解释了为什么 1.41 M 能打过 2.25 M 的 SE-Mamba**，但**论文自己没有做这个分析**。

### 五、参数量与算力的独立复算（本页验证）

论文声称 DSDDB 的参数量与复杂度**只有 DDB 的 12.7%**（$n=4$、$C=64$、$K=3$）。代入 Eq. (9)(10) 复算：

$$P(\text{DSDDB}) = \sum_{i=1}^{4}iC K^2 + \sum_{i=1}^{4}iC^2 = 10\cdot(64\cdot 9) + 10\cdot 4096 = 5760+40960 = 46720$$
$$P(\text{DDB}) = \sum_{i=1}^{4}iC^2K^2 = 10\cdot 4096\cdot 9 = 368640$$
$$\text{比值} = 46720/368640 = \mathbf{12.67\%} \quad ✅\ \text{与论文的 12.7% 一致}$$

⇒ **论文的 Eq. (9)(10) 与常数取值可独立验证**。Table II 的 `DSDDB→DDB`（1.41M→2.37M，+68%）是这一推导在**参数量维度**上的实证。

> [!warning] FLOPs 维度的 "12.7%" **未被直接实测**
> Table II 只报了 `DSDDB→DDB` 的**参数量**差异（1.41M→2.37M），**没有报 DDB 版的 FLOPs**。
> ⇒ "复杂度只有 12.7%" 只在 Eq. (7)(8) 的**推导**里成立，**表里没有对应数字**。请勿把 12.7% 当作实测值。

## 架构与状态

```text
带噪语音 x
  │
  ├─ STFT：FFT size 400 / window 400 / hop 100   （@16 kHz ⇒ 25 ms 窗 / 6.25 ms hop）
  │
  ├─ Encoder：DSDDB（谱编码）
  │     └─ 每个空洞卷积 = DWC(k) → PWC（深度可分离分解）
  │
  ├─ TS Blocks：GPFCA × N（默认 N=2，来自 Table I 表题）
  │     └─ GPFCA = 通道权重分配层(SCA) + GPFN(组质数核前馈网络)
  │            ├─ SCA(X) = X ⊙ PWC(AAP(X))                     ← 时间轴压成标量
  │            └─ GPGU：chunk 成 4 组 → DFG_i，核 = {3,11,23,31}
  │                   DFG_i(X_i,k_i) = PWC(DWC_k(X_i)) ⊙ DWC_k(X_i)   ← 深度门控
  │                   → CONCAT → PWC 融合
  │
  ├─ Decoder：DSDDB（谱解码）
  │
  └─ 并行的 mask / phase 双路输出（沿用 MP-SENet 的 TS 范式）
        → iSTFT
```

> [!question] 本图的可信边界（重要）
> **原 PDF 第 2 页 Fig. 1（整体架构）的模块标签完全没有进入文本流**——文本抽取里只剩一行图注 `Fig. 1: The overall architecture of the PrimeK-Net.`。
> 因此上面这张图是**依据 §II 正文的模块描述重构的**，**不是从 Fig. 1 还原的**。以下三项**未经图确认**：
> ① TS Blocks 的实际层数与 GPFCA 的堆叠数（正文未给，仅 Table I 表题暗示默认 2 个）；
> ② 并行 mask/phase 双 decoder 的连接方式（论文只说"沿用 MP-SENet 的 TS 范式"，**未在本篇展开**）；
> ③ GPFCA 在时间/频率两阶段中是**共享**还是**各有一套**。
> **需回查 `wiki_low_latency/assets/primek-net_2025/primek-page2.png`。本页不对未确认的连接拓扑做断言。**

### 损失函数（两套，Eq. 11–12）

$$\mathcal{L}_{\text{old}} = \lambda_1\mathcal{L}_{\text{Metric}} + \lambda_2\mathcal{L}_{\text{Mag}} + \lambda_3\mathcal{L}_{\text{Pha}} + \lambda_4\mathcal{L}_{\text{Com}} + \lambda_5\mathcal{L}_{\text{Time}}$$

$$\mathcal{L}_{\text{new}} = \lambda_1\mathcal{L}_{\text{Metric}} + \lambda_2\mathcal{L}_{\text{Mag}} + \lambda_3\mathcal{L}_{\text{Pha}} + \lambda_4\mathcal{L}_{\text{Com}} + \lambda_6\mathcal{L}_{\text{Con}}$$

| 损失 | 用途 | 与另一套的差异 |
|---|---|---|
| $\mathcal{L}_{\text{old}}$ | **与既有方法公平对比** | 有 Time Loss、无 Consistency Loss |
| $\mathcal{L}_{\text{new}}$ | **论文默认（最佳）** | 去掉 Time Loss、加入 Consistency Loss [24] |

两者的质量差：**PESQ 3.61 vs 3.57 ⇒ $\mathcal{L}_{\text{new}}$ 好 0.04**（Table II 最后两行）。

> [!question] 🔴 **$\lambda$ 权重全部未给出 —— 引用链上的一个真实断点**
> 论文写了 $\lambda_1 \ldots \lambda_6$ 六个符号，**从未给任何具体数值**，只说"沿用 MP-SENet"。
> **但 [[wiki_low_latency/entities/LaCo-SENet]] 写「损失 $\mathcal{L}=0.9\mathcal{L}_{\text{mag}}+0.3\mathcal{L}_{\text{pha}}+0.1\mathcal{L}_{\text{com}}+0.05\mathcal{L}_{\text{con}}+0.05\mathcal{L}_{\text{gan}}$（沿用 PrimeK-Net [3]）」**——**这些具体权重在 PrimeK-Net 原文中不存在。**
> ⇒ 两种可能：**(a)** LaCo-SENet 从 PrimeK-Net 的官方代码仓库读到权重，但文字上归因给了论文；**(b)** 归因不准确。
> **本库处置**：两页**都如实记录、互相标注、不替任何一方补齐**。这也是库内第 14 条（引用即负有义务 / 锚点必须先钉口径）在**非数值类引用**上的一个新样本——**断链不一定是数值矛盾，也可能是上游根本没提供。**

## Table 1 速查（论文表格速查）

### Table I

| Model | PESQ | CSIG | FLOPs | Para. |
|---|---|---|---|---|
| Noisy | 1.97 | 3.35 | — | — |
| MP-SENet [5] | 3.50 | 4.73 | 74.52 G | 2.05 M |
| SE-Mamba [16] | 3.52 | 4.75 | 65.46 G | 2.25 M |
| PrimeK-Net-S $\mathcal{L}_{\text{old}}$ | 3.53 | 4.76 | 26.45 G | 0.79 M |
| PrimeK-Net $\mathcal{L}_{\text{old}}$ | 3.57 | 4.79 | 44.64 G | 1.41 M |

### Table II

| Model | PESQ | CSIG | CBAK | COVL | Para. |
|---|---|---|---|---|---|
| PrimeK-Net | 3.61 | 4.81 | 3.98 | 4.35 | 1.41 M |
| GPFN→Wide FFN | 3.51 | 4.74 | 3.93 | 4.27 | 1.41 M |
| DSDDB→DDB | 3.61 | 4.82 | 3.98 | 4.36 | 2.37 M |
| w/o SCA | 3.42 | 4.70 | 3.82 | 4.16 | 1.34 M |
| w/o CL | 3.59 | 4.79 | 3.95 | 4.32 | 1.41 M |
| w/o CL + w/ TL ($\mathcal{L}_{\text{old}}$) | 3.57 | 4.79 | 3.97 | 4.30 | 1.41 M |

### Table III

| Kernel Size | PESQ | CSIG | FLOPs | Para. |
|---|---|---|---|---|
| (17, 17, 17, 17) | 3.57 | 4.77 | 44.64 G | 1.41 M |
| (5, 15, 21, 27) | 3.59 | 4.79 | 44.64 G | 1.41 M |
| (3, 11, 23, 31) | 3.61 | 4.81 | 44.64 G | 1.41 M |

## 低时延账本

> [!warning] **本模型的低时延账本几乎全空 —— 它本来就不是低时延模型**
> 下表逐项标注，**凡论文未报告的一律写"未报告"，不作补写**。

| 字段 | 论文内容 | 本库判定 |
|---|---|---|
| 采样率 | **正文未明确写出** | `未报告`（VB-DEMAND 惯例为 16 kHz，**属推断**） |
| STFT window | **400 samples** | 若按 16 kHz ⇒ **25 ms** |
| STFT hop | **100 samples** | 若按 16 kHz ⇒ **6.25 ms** |
| FFT size | **400** | 单边谱 $F = 400/2+1 = 201$ |
| 窗函数类型 | **未报告** | `未报告` |
| **STFT center / 帧锚定** | **未报告** | ⭐ **库内一等审计项缺失** ⇒ 算法延迟双向不确定 |
| look-ahead | **未报告** | `未报告`（**"忽略未来"完全没有讨论**） |
| group delay | **未报告** | `未报告` |
| warm-up / state reset | **未报告** | `未报告`（**流式完全未讨论**） |
| chunk / streaming 语义 | **未报告** | `未报告` |
| **算法延迟（ms）** | **未报告** | ❌ **全文无任何延迟数字** |
| 端到端延迟 | **未报告** | `未报告` |
| **FLOPs** | **44.64 G**（Table I）· 26.45 G（S 档） | ⭐ 唯一的算力数字，**解析值** |
| **RTF** | **未报告** | ❌ **无任何实测速度** |
| 目标硬件 | **未报告** | `未报告`（只在缺陷①提到 "memory-constrained edge devices"，**无对应实验**） |
| 量化 | **未报告** | `未报告` |
| 峰值 RAM / 显存 | **未报告**（Fig. 3(b) 只有相对曲线，无数值） | `未报告` |
| p50 / p95 / p99 | **未报告** | `未报告` |
| deadline miss / underrun | **未报告** | `未报告` |
| 功耗 | **未报告** | `未报告` |
| 随机种子数 / 方差 | **未报告** | ❌ 而 Table II/III 的核心增量低至 **0.02 PESQ** |

**算法延迟判定**：**无法判定，且该模型在本库中不具备低时延资格。**
- 唯一的时序锚点是 **hop 100 samples（≈6.25 ms）**；
- **STFT center 未报告** ⇒ 与 [[wiki_low_latency/entities/GTCRN]] 同样陷入「≈25 或 ≈37.5 ms」的**双向不确定**；
- **非因果结构**（两阶段 + 频率轴核长 31 + 未报告的 center）⇒ 按库内第 1 条，**算法延迟判为不可确定**；
- ⇒ **它不是 2 ms 方向候选，也不该出现在任何速度排序中。**

**算力证据等级**：**L0**（仅解析 FLOPs）。按库内第 10 条，**禁止参与速度排序**。
**引用即负有义务**：引用了 NAFNet（效率论证）与 MobileNets（depthwise separable 的效率论证）却**不报任何速度** ⇒ 与 GTCRN 引用 ShuffleNetV2 的情形同构，**标注为"引用即负有义务而未履行"**（库内第 15 条）。

## 因果性与结构审计

### 因果性判定：`未声明`（且实质非因果）

论文**全文没有出现 causal / causality / non-causal / future / streaming / look-ahead 中的任何一个概念**（除"未来工作"的语义）。

| 结构证据 | 含义 |
|---|---|
| **两阶段（TS）结构** | 时间与频率维分别建模；论文**未说明时间阶段是否因果** |
| **GPFN 核长 31 沿频率轴** | 跨 31 个频点的局部结构——频率轴，**不直接引入时间未来依赖** |
| **SCA 的 AAP 把时间轴压成标量** | 用**整条时间序列**的均值 ⇒ **若作用于"整句"，则读取未来**；若按 chunk 内计算则因果 |
| **未报告的 STFT center** | 若 `center=True`，前端即含 $W/2$ 未来样本 |
| **无逐层 padding 证据** | 完全缺失 |

⇒ 按库内第 1 条（**只要 encoder 存在非因果对称 padding，算法延迟即判为不可确定**）：**PrimeK-Net 无法判定为因果**，且论文**根本没尝试**让它因果。

### 结构审计清单对照（库内 8 项，见 [[wiki_low_latency/overview]]）

| # | 审计项 | PrimeK-Net 的情况 | 判定 |
|---|---|---|---|
| ① | 时间轴卷积 kernel | **未报告**（论文只给 DFG 的核 $\{3,11,23,31\}$，**未说明是时间轴还是频率轴**）⚠️ | **未知** |
| ② | 归一化层可融合性 | **未报告**（论文未提任何归一化层） | **未知** |
| ③ | 注意力是否需 KV cache | **SCA 非 attention**（AAP+PWC）⇒ 无 KV cache；但 SCA 的时间轴全局池化**本身就需要整段** | ⚠️ **取决于 chunk 语义** |
| ④ | 是否有 global pooling | **有**（AAP） | ⚠️ **危险**：若按整句计算则聚合未来 |
| ⑤ | 是否有数据相关的不规则访问 | **未报告** | **未知** |
| ⑥ | 算力是否固定 | **是**（无动态路由） | ✅ 安全 |
| ⑦ | 是否有全序列统计 | **有**（AAP = adaptive average pooling） | ⚠️ **危险**：跨 chunk size 不一致 |
| ⑧ | accelerator launch / 调度次数 | **未报告** | **未知** |

> [!important] 第 ④⑦ 两项是 PrimeK-Net 最值得警惕的地方
> **SCA 的核心操作是 AAP（把每个通道的时间序列压成一个标量）**。这在图像复原里是无害的（图像没有"因果"概念），**但在流式 SE 里它必须回答一个问题：这个均值是在"整句"上算的，还是在"当前 chunk / 当前帧"上算的？**
> - 若是**整句** ⇒ **非因果，且无法流式**；
> - 若是**当前帧**（即 AAP 退化为对频率轴求均值）⇒ 因果且无状态。
>
> **论文没有回答。** 这个未澄清的歧义恰好落在 PrimeK-Net 最核心的模块上 ⇒ **LaCo-SENet 把这个骨干改造成因果时，一定处理了这个操作**（LaCo-SENet 的 SSU 与 dual-buffer 正是为这类问题设计的），**但 LaCo-SENet 的论文里也没有逐层说明 SCA 的时间语义**。
> ⇒ 这是**库内一个真实的、尚未闭合的因果性缺口**，值得作为后续审计目标。

## 结果与证据边界

| 维度 | 论文给了什么 | 边界 |
|---|---|---|
| 质量 | PESQ 3.61 / CSIG 4.81 / CBAK 3.98 / COVL 4.35 | 只在 **VoiceBank+DEMAND** 一个数据集上；**无负 SNR 分层、无噪声类型分层、无 WER/ASR** |
| 规模 | 1.41 M / 44.64 G FLOPs | 解析值；**FLOPs 量级比库内超轻量锚点 GTCRN（39.6 MMACs/s）高约 3 个数量级** |
| 对照 | Table I 的三方同框架同损失对照 | 未说明是否重训、无种子数；Table I 只有 PESQ 与 CSIG 两列 |
| 消融 | Table II（6 行）+ Table III（3 行） | 两组"参数量/FLOPs 完全不变"的对照设计**很干净**；但效应量低至 0.02 且**无方差** |
| 效率 | 12.7% 的参数量-复杂度推导 | **参数量维度可独立复算（本页已验证 = 12.67%）**；**FLOPs 维度表内无对应数字** |
| 低时延 | 无 | **完全没有** |

### 与库内"人声保留"要求的对照

按 [[wiki_low_latency/concepts/低 SNR 人声保留评估]] 的字段逐项检查：

| 字段 | PrimeK-Net |
|---|---|
| false-suppression | **未报告** |
| SPP / VAD calibration | **未报告** |
| ASR WER | **未报告** |
| F0 / formant / prosody | **未报告** |
| voiced energy | **未报告** |
| 负 SNR 分层 | **未报告**（VB-DEMAND 是 0/5/10/15 dB 的"温和"条件） |
| 竞争说话人 / babble | **未报告** |
| 主观 MOS | **未报告**（用的是 CSIG/CBAK/COVL 这类**客观** MOS 预测器） |

> **注**：CSIG/CBAK/COVL 虽然名字带 MOS，但它们是 **PESQ 家族的客观预测器**，**不是主观听感测试**。这一点在库内需要与真正的 listening test 区分。

## 参数量/算力的三方对照（跨论文）

PrimeK-Net 与 LaCo-SENet 共享骨干，因此库内可以做一个**同骨干跨配置**的对照：

| 配置 | 参数 | 算力 | PESQ | 因果性 | 出处 |
|---|---|---|---|---|---|
| **PrimeK-Net**（非因果） | **1.41 M** | **44.64 G FLOPs** | **3.61** | 非因果 | PrimeK-Net Table I/II |
| LaCo-SENet ($r_R{=}0.5$，200 ms) | 1.37 M | 未报告 | 3.47 | low_look_ahead | LaCo-SENet Table 1 |
| LaCo-SENet（12.5 ms，全因果） | 1.37 M | 未报告 | **3.35** | 可核验因果（SSU） | LaCo-SENet Table 1 |

**本页的计算**：

$$\text{因果化的质量代价} = 3.61 - 3.35 = \mathbf{0.26\ PESQ}\quad(\text{保留上界的 } 3.35/3.61 = \mathbf{92.8\%})$$
$$\text{非因果 → 200 ms 对称参考的代价} = 3.61 - 3.47 = \mathbf{0.14\ PESQ}$$

⇒ **在这个骨干上，"未来上下文"的价格被量化到 0.26 PESQ 以内**。但这仍是**单一种子、无方差**的对照，按库内第 6 条应标注"未经显著性检验"。

> [!contradiction] ⚠️ 一个新出现的口径问题（本页发现）
> PrimeK-Net 报的是 **FLOPs（44.64 G）**，而库内绝大多数论文报的是 **MACs** 或 **MMACs/s**。
> FLOPs 与 MACs 的换算通常是 **1 MAC = 2 FLOPs**（乘 + 加），但也有论文按 1:1 计。
> ⇒ **PrimeK-Net 的"44.64 G"与库内其他论文的算力数字不在同一口径上，禁止直接相比。**
> 这一点在 LaCo-SENet 页也需要标注——LaCo-SENet 的 Table 1 **没有报 PrimeK-Net 的算力列**，所以目前没有产生实际矛盾，但**一旦有人把 44.64 G 拿去和 GTCRN 的 39.6 MMACs/s 比，就会差 3 个数量级**。

## 交叉链接

- [[wiki_low_latency/sources/2025/PrimeK-Net 2025|source 页（完整动机/前后端/消融审计）]]
- [[wiki_low_latency/concepts/2502.19906-prime-kernel-multiscale-dense-block|概念页（质数核多尺度 + 深度可分离空洞密集块）]]
- **后续**：[[wiki_low_latency/entities/LaCo-SENet]] · [[wiki_low_latency/sources/2026/LaCo-SENet 2026]]（直接沿用本骨干与损失）
- **前身**：MP-SENet [5]（损失与 TS 范式）· TSTNN [2]（TS 结构）· NAFNet [19]（GPFCA 模板）· DDB [9]（被 DSDDB 替换）· HIFI-GAN MPD [17]（质数核灵感）
- **同分支竞品**：MP-SENet（Conformer）· SE-Mamba（Mamba）· CMGAN · TridentSE
- **方法论呼应**：[[wiki_low_latency/entities/FastEnhancer]]（同样用"零算术变化的对照"当因果证据，但它的证据是**实测 RTF**，PrimeK-Net 的是**解析 FLOPs** ⇒ 证据等级 L2 vs L0）
- **锚点对照**：[[wiki_low_latency/entities/GTCRN]]（算力轴锚点 vs PrimeK-Net 的质量轴上界角色）
- **判定口径**：[[wiki_low_latency/overview]] 第 1、6、10、14、15、16 条
