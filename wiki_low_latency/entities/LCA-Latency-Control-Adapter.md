---
title: LCA (Latency Control Adapter)
type: entity
created: 2026-10-07
updated: 2026-10-07
tags:
  - entity
  - model
  - latency-controllable
  - lookahead
  - adapter
  - dilated-convolution
  - conv-tasnet
  - streaming
  - interspeech-2026
source_paper: "[[wiki_low_latency/sources/2026/Latency Controllable SE 2026]]"
related:
  - [[wiki_low_latency/sources/2026/Latency Controllable SE 2026]]
  - [[wiki_low_latency/concepts/lca-2026-latency-control-adapter]]
  - [[wiki_low_latency/entities/LaCo-SENet]]
  - [[wiki_low_latency/concepts/严格因果与算法延迟]]
  - [[wiki_low_latency/concepts/低时延前端与延迟账本]]
---

# LCA（Latency Control Adapter）

> 一句话定义：一个插在流式增强骨干里的**轻量 adapter 组**，每个 adapter 是一个为特定 lookahead 配置的 **LAM（Lookahead Module）**；推理时按可用延迟预算选一个 adapter，即可**在不重载整个模型的前提下切换算法延迟**。
> 配套概念是 **LAM**：一叠膨胀 1-D 卷积块，每块的因果性由一个二值开关控制 ⇒ 总 lookahead 为 $T_{la}=\sum_i b_i 2^{i-1}$。

- **出处**：Interspeech 2026, pp. 3009-3014, DOI `10.21437/Interspeech.2026-2997`
- **作者**：Hiroshi Sato, Takafumi Moriya, Tsubasa Ochiai, Marc Delcroix（NTT, Inc. Japan）
- **源页**：[[wiki_low_latency/sources/2026/Latency Controllable SE 2026]]
- **无开源代码**（论文未给）

---

## 1. 定义与定位

| 项 | 内容 |
|---|---|
| 类型 | **骨干插件 + 训练范式**（不是完整模型） |
| 输入 / 输出 | 含噪波形 $y\in\mathbb R^T$ → 增强波形 $\hat x$（时域 Conv-TasNet 骨干） |
| 骨干 | 时域 Conv-TasNet（$B=256$, $R=4$, $X=8$, $H=512$, $P=3$） |
| 支持档数 | **7 档**（$T_{la}\in\{0,1,3,7,15,31,63\}$ 帧） |
| 参数共享 | 按 causal / non-causal 两类分别跨 adapter 共享 ⇒ 总参数 $2\cdot M$，**与档数无关** |
| 最小算法延迟 | **5 ms**（超低编码器配置、$T_{la}=0$ 档）；标准配置为 20 ms |
| 是否严格因果 | **只有 $T_{la}=0$ 那一档是**；其余 6 档均引入 lookahead |
| 库内定位 | **"延迟旋钮"演进线的当前终点**（[[wiki_low_latency/entities/LaCo-SENet]] 是训练期版本）；**方法论参照，不是可用基线** |

---

## 2. 组件表

| 组件 | 作用 | 实现 | 关键超参 |
|---|---|---|---|
| **LAM**（Lookahead Module） | 给骨干注入**指定量**的额外 lookahead | 一叠膨胀 1-D 卷积块，每块可 causal 或 non-causal | kernel size 3；dilations $2^0..2^{X-1}$；$X=6$ |
| **因果性开关** $b_i\in\{0,1\}$ | 决定第 $i$ 个块是否非因果 | 单调二值 pattern | $T_{la}=\sum_{i=1}^{X}b_i 2^{i-1}$ |
| **LCA** | 一叠 $K=7$ 个 adapter，每个是一个特定配置的 LAM | 推理时选一个 | 插入位置 $r=4$（separator 之后） |
| **参数共享方案** | 把总参数从 $K\cdot M$ 压到 $2\cdot M$ | 第 $i$ 个 Conv Block 在 causal 块之间共享、在 non-causal 块之间单独共享 | 与 $K$ 无关 |
| **Intra-batch multi-latency training** | 让 7 档共享知识 | 每个 mini-batch 把同一输入过所有 $K$ 个 adapter，损失平均 | $\mathcal L=\frac1K\sum_i(-\mathrm{SNR}(\hat x^{(i)},x))$ |

> [!note] 为什么膨胀是必需的
> 单层 1-D 卷积要引入 $L$ 帧 lookahead 需要 $L$ 的核宽；膨胀卷积用 $X$ 层即可达 $2^X-1$ 帧。
> ⇒ **用对数层数换线性 lookahead**，在长 lookahead 时显著省算力。论文脚注 1 说初步实验确认"等效 lookahead 下膨胀卷积性能更好"。

---

## 3. 延迟-质量前沿表

### 3.1 七档延迟（已独立复核）

| $T_{la}$（帧） | 0 | 1 | 3 | 7 | 15 | 31 | 63 |
|---|---|---|---|---|---|---|---|
| 二进制 pattern $b$ | `000000` | `100000` | `110000` | `111000` | `111100` | `111110` | `111111` |
| 标准 $\tau$（ms，$\tau_{enc}=20$，10 ms/帧） | **20** | 30 | 50 | 90 | 170 | 330 | 650 |
| 超低 $\tau$（ms，$\tau_{enc}=5$，2.5 ms/帧） | **5** | 7.5 | 12.5 | 22.5 | 42.5 | 82.5 | 162.5 |

**复核**：$\tau = \tau_{enc} + T_{la}\cdot L_{shift}/f_s$；标准 $160/16000=10$ ms、超低 $40/16000=2.5$ ms ⇒ 逐项吻合 ✅
**且 pattern 与 $T_{la}$ 一一对应**（$1,1+2,1+2+4,\dots$）⇒ Eq.(5) 的 $2^{i-1}$ 形式正确。

### 3.2 Figure 3 曲线（形状与相对关系，不含具体数值）

| 曲线 | (a) 标准 SDR | (b) 标准 DNSMOS | (c) 超低 SDR |
|---|---|---|---|
| (A-1) causal | 平坦下界（约 16.6 dB） | 平坦下界（约 3.40） | 平坦下界 |
| (A-2) non-causal | **平坦上界（约 17.55 dB）** | **平坦上界（约 3.53）** | 平坦上界 |
| (B-1) 多模型 lookahead | 随延迟单调上升 | 随延迟单调上升 | 随延迟单调上升 |
| (C-2) 单模型 LCA | 随延迟单调上升，**多数点位于 (B-1) 之上或与之重合** | 同 | 同 |

> [!important] 图上最重要的一个观察
> **在最大延迟点（650 ms / 630 ms lookahead），(C-2) 仍未达到 (A-2) 的非因果上界。**
> ⇒ **延迟-质量前沿存在一个无法用 lookahead 弥合的缺口**：把 630 ms 的未来全给模型，仍追不上"从头就看全序列"的模型。
> 这与库内"非因果模型可作质量上界"的用法一致（参见 [[wiki_low_latency/entities/PrimeK-Net]] 作为 LaCo-SENet 的非因果上界）。

> [!question] 数值精度声明
> 上表的"约"值是 150 dpi 渲染图目视读出的**近似**，仅用于描述曲线形状与相对位置。**精确逐点数值需 400–600 dpi 裁单面板重读**，本页不给出具体 dB 以免误引。

### 3.3 正文给出的量化结论

| 对照 | 结论 |
|---|---|
| (C-2) vs (B-1)，标准编码器 | **7 个工作点平均 SDR +0.13 dB** |
| (C-2) vs (B-1)，超低编码器 | **7 个工作点平均 SDR +0.53 dB** |
| (C-2) vs (A-1) causal，超低设置 | **SDR +0.45 dB**（归因于从更大 lookahead 系统蒸馏） |
| 超低 vs 标准（同延迟） | 超低更优（更细的分析窗移 ⇒ 更精确的波形投影），**代价是更多 MACs** |

---

## 4. 成本表（Table 1）

| 系统 | MACs [G/s] | 总参数量 [M] |
|---|---|---|
| (A-1) Causal | 1.31 | 13.3 |
| (B-1) Convolution lookahead（**7 个模型**） | 1.46 | **104.1** |
| (C-1) LCA（**共享** adapter 参数） | 1.46 | **16.5** |
| (C-2) LCA（**不共享**） | 1.46 | **24.5** |

**三条关键性质**：
1. **运行时 MACs 上 (B-1) 与 LCA 完全相同（1.46 G/s）** ⇒ **adapter bank 的成本是"存储"而非"运行时算力"**（推理只执行一条 lookahead 路径）。
2. 加 LAM 相对 causal 的 MACs 代价：**1.31 → 1.46 G/s（+11.5%）**。
3. 支持 7 档的参数成本：多模型 **104.1 M** vs LCA **16.5 / 24.5 M**。

> [!question] 摘要"76%"的口径
> 104.1 → 24.5 M = 降 **76.5%**（≈ 摘要的 76%）；
> 104.1 → 16.5 M = 降 **84.2%**。
> ⇒ 摘要的 76% 对应 **(C-2)**，但摘要未声明。**两数并列，不选边。**

> [!warning] 量纲与规模守卫
> LCA 的 **1.46 G MAC/s = 1460 MMAC/s** 与库内 GTCRN 的 **39.6 MMACs per second** **同分母可直接比**（差约 37 倍）。
> **但参数量 13.3 M vs GTCRN 23.7 K 差约 560 倍** ⇒ **LCA 不是轻量模型，禁止与库内轻量模型同表排名。**
> 且其分母（per second）与 [[wiki_low_latency/entities/PrimeK-Net]] 的 GFLOPs/整句**不同，禁止混比**。

---

## 5. 架构示意（ASCII）

```
   含噪波形 y ∈ R^T
        │
        ▼
   ┌──────────────────────────┐
   │  Encoder（learned 1-D    │   L_len=320 / L_shift=160  ⇒ τ_enc = 20 ms（标准）
   │  filterbank, Conv-TasNet）│   L_len= 80 / L_shift= 40  ⇒ τ_enc =  5 ms（超低）
   └──────────────────────────┘
        │  Z_enc ∈ R^{T'×D}
        ▼
   ┌────────────────────────────────────────────────────────────┐
   │  Separator（R = 4 个块）                                    │
   │   Block 1 → Block 2 → Block 3 → Block 4                     │
   │                                      │                      │
   │                                      ▼  r = 4（separator 之后）│
   │   ┌──────────────────────────────────────────────────────┐ │
   │   │  LCA：K = 7 个 adapter（每个是一个 LAM）              │ │
   │   │                                                      │ │
   │   │   Adapter i  =  6 个膨胀 1-D Conv Block（k=3）        │ │
   │   │     dilations: 2^0 2^1 2^2 2^3 2^4 2^5                │ │
   │   │     每块带二值开关 b_j ∈ {0,1}：                       │ │
   │   │        b_j = 0 ⇒ causal（无右侧上下文）                │ │
   │   │        b_j = 1 ⇒ non-causal（对称上下文）              │ │
   │   │                                                      │ │
   │   │   T_la = Σ_j b_j · 2^(j-1)                            │ │
   │   │                                                      │ │
   │   │   7 个单调 pattern ⇒ T_la ∈ {0,1,3,7,15,31,63}        │ │
   │   │                                                      │ │
   │   │   ★ 参数共享：causal 块之间共享 + non-causal 块之间共享 │ │
   │   │                ⇒ 总参数 2·M，与 K 无关                 │ │
   │   │   ★ 推理时只走一条路径（选中的 adapter）               │ │
   │   └──────────────────────────────────────────────────────┘ │
   └────────────────────────────────────────────────────────────┘
        │  Z_sep
        ▼
   ┌──────────────────────────┐
   │  Decoder（1-D transposed）│
   └──────────────────────────┘
        │
        ▼
   增强波形 x̂

   算法延迟：τ = τ_enc + T_la · L_shift / f_s
```

---

## 6. 低时延账本与因果性审计

### 6.1 延迟账本

| 项 | 标准编码器 | 超低编码器 |
|---|---|---|
| $L_{len}$ / $L_{shift}$ | 320 / 160 样本 | 80 / 40 样本 |
| $f_s$ | 16 kHz | 16 kHz |
| **$\tau_{enc}$** | **20 ms** | **5 ms** |
| $\tau_{sep}$ | $T_{la}\cdot 10$ ms | $T_{la}\cdot 2.5$ ms |
| **$\tau$ 范围** | **20 – 650 ms** | **5 – 162.5 ms** |
| RTF / 硬件 | **未报告** | **未报告** |
| 端到端延迟 | 未报告 | 未报告 |

> [!warning] "Causal" 在这里不等于零延迟
> 论文自己明确说明（§3.2）："**我们称一个系统为 causal，当且仅当 separator 自身不使用未来帧（$T_{la,sep}=0$），尽管 $\tau_{enc}$ 依然存在。**"
> ⇒ Table 1 里的 "(A-1) Causal" 的算法延迟是 **20 ms**，不是 0。这一点极易被误读，必须显式标注。

### 6.2 因果性审计（逐项）

| 检查项 | 结论 |
|---|---|
| 是否严格因果？ | **仅 $T_{la}=0$ 一档**（7 档中的 1 档） |
| 其余 6 档的 lookahead | $T_{la}=1,3,7,15,31,63$ 帧 ⇒ $\tau_{sep}=10,30,70,150,310,630$ ms（标准） |
| 是否读取未来输入？ | **$T_{la}>0$ 的档位是**（非因果块有右侧上下文） |
| 是否有全局池化 / 全序列统计量？ | 无（纯卷积 + 逐块因果开关） |
| 是否可与库内严格因果方法排名？ | **不可**。只有 $T_{la}=0$ 档可参与，且其 5 ms 仍超库内 2 ms 目标 2.5 倍 |
| STFT center | **不适用**（时域模型，用 learned filterbank） |

> [!important] 机制可用，档位不可用
> LCA 的**设计思想**（把延迟参数化为可切换模块）对库内有价值；但它的**任何一档配置**都不满足库内约束：
> - $T_{la}=0$ 档：5 ms（超低）或 20 ms（标准），均 > 2 ms；
> - $T_{la}>0$ 档：全部读未来。
> ⇒ **"旋钮的另一端在约束之外"**。借用思想，不借用配置。

---

## 7. 与库内模型对照

| 模型 | 延迟配置方式 | 档数 | 延迟范围 | 参数量 | 运行时 MACs | 与 LCA 的关系 |
|---|---|---|---|---|---|---|
| **LCA（本篇）** | **运行时**选 adapter | **7** | 5–650 ms | 16.5 / 24.5 M | 1.46 G/s（**恒定**） | — |
| [[wiki_low_latency/entities/LaCo-SENet]] | **训练期**固定 padding ratio | 1 / 模型 | 12.5–200 ms | 1.37 M | 未报告 | 同为"延迟可配置"；**LCA 是它的运行时版本** |
| [[wiki_low_latency/entities/RT-SEMamba]] | 层数（8 层 → 蒸馏到 1 层） | 2 | 25 ms（约束） | 未报告 | 未报告 | 档位是"层数"而非"lookahead" |
| [[wiki_low_latency/entities/FastEnhancer]] | 训练期设计（5 档 T–L） | 5 | 未报告 | – | 262 M MACs | 档位是**训练期**设计，非推理期切换 |
| [[wiki_low_latency/entities/RT-Tango]] | 固定 | 1 | **8 ms** | – | – | 与 LCA 构成"低延迟谱系"两端，**可组合** |
| [[wiki_low_latency/entities/DCCRN]] | 固定 | 1 | 37.5 ms | – | – | "延迟是架构副产品"阶段的代表 |

> [!note] 库内"延迟旋钮"三阶段演进
> 1. **延迟是架构副产品**（2020–21）：[[wiki_low_latency/entities/DCCRN]] 37.5 ms / 6 帧 look-ahead
> 2. **延迟是一等目标且可配置**（22–25）：[[wiki_low_latency/entities/STFT-Very-Low-Latency-SE]] 非对称双窗、[[wiki_low_latency/entities/FastEnhancer]] 5 档 T–L、[[wiki_low_latency/entities/LaCo-SENet]] 训练期 padding 旋钮
> 3. **延迟是运行时参数**（2026）：**本篇 LCA**
> ⇒ **LCA 是这条线的当前终点。**

---

## 交叉链接

- 源页：[[wiki_low_latency/sources/2026/Latency Controllable SE 2026]]
- 概念页：[[wiki_low_latency/concepts/lca-2026-latency-control-adapter]]
- 同分支：[[wiki_low_latency/entities/LaCo-SENet]]、[[wiki_low_latency/entities/FastEnhancer]]、[[wiki_low_latency/entities/RT-Tango]]、[[wiki_low_latency/entities/RT-SEMamba]]
- 前端对照：[[wiki_low_latency/entities/STFT-Very-Low-Latency-SE]]、[[wiki_low_latency/concepts/2204.09911-short-asymmetric-stft]]
- 口径：[[wiki_low_latency/concepts/严格因果与算法延迟]]、[[wiki_low_latency/concepts/低时延前端与延迟账本]]、[[wiki_low_latency/concepts/2409.10358-ultra-low-latency-benchmark]]
- 全库判定口径：[[wiki_low_latency/overview]]
