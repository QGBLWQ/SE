---
title: S2542660526001769 - 脉冲神经网络与状态空间模型的并行融合（流式增强）
type: concept
created: 2026-09-20
updated: 2026-09-20
tags:
  - spiking-neural-network
  - snn
  - plif
  - lif
  - mamba
  - ssm
  - parallel-branch
  - event-driven
  - spike-firing-rate
  - macs
  - streaming
  - strict-causal
  - latency-ledger
  - speech-enhancement
sources:
  - [[wiki_low_latency/sources/2026/PSMSE 2026]]
related:
  - [[wiki_low_latency/entities/PSMSE]]
  - [[wiki_low_latency/concepts/2608.12099-mamba-distillation]]
  - [[wiki_low_latency/concepts/2411.02019-slowfast-ssm]]
  - [[wiki_low_latency/concepts/2409.10358-ultra-low-latency-benchmark]]
  - [[wiki_low_latency/concepts/严格因果与算法延迟]]
  - [[wiki_low_latency/concepts/低时延前端与延迟账本]]
  - [[wiki_low_latency/concepts/低 SNR 人声保留评估]]
  - [[wiki_low_latency/concepts/2205.05474-deep-filtering]]
  - [[wiki_array/concepts/Mamba SSM 状态空间模型]]
---

# S2542660526001769 - 脉冲神经网络与状态空间模型的并行融合（流式增强）

## 定义

这里的"并行融合"特指 PSMSE 的组织方式：把两类互补的时序机制放进**同一个 bottleneck 的两个并列分支**——

- **SNN 分支（SMC）**：脉冲神经元提供事件驱动的稀疏表征，解决"序列太密、算力太贵"；
- **SSM 分支（SMR）**：Mamba 的选择性状态空间提供输入相关的近线性长程建模，解决"脉冲网络时序能力弱"。

关键不是"用了 SNN"或"用了 Mamba"，而是三点组合：(1) 两个分支**并行而非级联**；(2) Mamba 的输入是**已经稀疏化的 spike 表征**，不是 dense 波形；(3) 用一个**带可学习阈值的二值卷积（binary convolution）**做瓶颈投影，作为稀疏性的第二根支柱。

它解决的是**每瓦算力**问题（MACs、参数、端侧可行性），**不直接解决算法延迟**。PSMSE 的 30 ms 帧长在 16 kHz 下就是 30 ms 算法延迟，与本 wiki 约 2 ms 的目标差 15×。

## 最小背景

### 脉冲神经元（LIF → PLIF）

LIF 的三阶段（charging / firing / resetting）写作：

$$
U[t]=U[t-1]+\tau\cdot\big(X[t]-(U[t-1]-V_{th})\big),
$$

$$
S[t]=\Theta\big(U[t]-V_{th}\big),\qquad
U'[t]=\big(1-S[t]\big)\cdot U[t]+S[t]\cdot V_{reset},
$$

$U[t]$ 是膜电位，$X[t]$ 是输入，$\tau$ 是 decay factor，$V_{th}$ 是阈值，$V_{reset}$ 是复位值，$\Theta(\cdot)$ 是 Heaviside 阶跃。因为 $\Theta$ 不可导，训练时用 sigmoid 作 surrogate gradient。

**PLIF 相对 LIF 的唯一改动是把 $\tau$ 变成可学习参数**：$\tau=1/(1+e^{-a})$，$a$ 可训练；同层共享 $\tau$、跨层独立。

> [!contradiction] PSMSE 里 $\tau$ 的定义与初值互斥
> 论文写 $\tau=1/(1+e^{-a})\in(0,1)$，又写网络初始化 $\tau=2.0$。若取 $\tau=2.0$，上式展开的泄漏系数 $(1-\tau)=-1$，膜电位更新变成 $U[t]=-U[t-1]+2X[t]+2V_{th}$，是符号翻转的不稳定形式。**"可学习膜时间常数"这一机制在本篇的定量描述因此不可靠**；引用该设计时应只保留"$\tau$ 可学习"这一定性结论，不要复述具体数值。

### 选择性状态空间（Mamba）

$$
\frac{d\mathbf h(t)}{dt}=\mathbf A\mathbf h(t)+\mathbf B\mathbf x(t),\qquad
\mathbf y(t)=\mathbf C\mathbf h(t),
$$

经零阶保持离散化后：

$$
\mathbf h_t=\overline{\mathbf A}\mathbf h_{t-1}+\overline{\mathbf B}\mathbf x_t,\qquad
\mathbf y_t=\mathbf C(\mathbf x_t)\mathbf h_t,
$$

其中 $\mathbf B(\mathbf x)=\mathrm{Linear}_B(\mathbf x)$、$\mathbf C(\mathbf x)=\mathrm{Linear}_C(\mathbf x)$ 就是 Mamba 的 selection mechanism。

**"并行融合"的关键一步**是：$\mathbf x_t$ 在这里不是波形样本，而是上游脉冲层输出的 0/1 spike。稀疏的输入使状态转移的更新本身也变稀疏——这就是论文所说 "the Mamba component operates directly on spike-based representations, significantly reducing sequence complexity compared to raw waveform processing"。

## 三条可复用的设计规则

### 规则 1：并行优于级联（但收益是边际的）

PSMSE 的消融给出了全表唯一"同预算、只换拓扑"的对照：

| 拓扑 | PESQ | STOI | Params | MACs |
|---|---:|---:|---:|---:|
| SMC ∥ SMR（并行） | 2.85 | 95.1 | 0.26 M | 0.11 G/s |
| SMC → SMR（级联） | 2.81 | 95.0 | 0.26 M | 0.11 G/s |

论文的解释是并行「avoiding information bottlenecks or feature loss that may occur in the cascaded structure」：级联会让局部特征先被压缩再进全局分支，造成信息瓶颈。

**但要如实标注收益幅度只有 0.04 PESQ**。并行是"正确方向"，不是"决定性 trick"——这一点在与论文自称的 "main architectural novelty" 对照时容易被夸大。

### 规则 2：让重序列模型吃稀疏表征，而不是吃原始波形

这是省算力的真正来源。消融证据：

| 变体 | MACs [G/s] | PESQ |
|---|---:|---:|
| 原始（SNN + binary conv） | **0.11** | 2.85 |
| w/o SNNs（换回普通 ANN） | **0.61** | 2.75 |
| w/o binary convolution | **0.31** | 2.78 |

两处都是**同一量级或近量级**的变化（5.5× 和 2.8×），且伴随质量下降，说明"稀疏"不是靠牺牲质量换来的装饰，而是结构性的。这也解释了为什么"把 SNN 换成 ANN"会让 PESQ 反而掉——脉冲层不是普通激活函数的替代品，它和下游的稀疏消费逻辑是耦合的。

### 规则 3：帧内递归 + 帧间无状态 = 一种"廉价的因果"

PSMSE 的 SMR 里有 `RecurrentLayer` 和 PLIF 的帧内循环，但论文明确写：

> "Explicit Mamba state caching is not used, so the Mamba states are re-initialized on each call and not propagated across consecutive frames."

于是整个系统在帧间是**无状态映射**：每 30 ms 独立处理一个 chunk，再用 50% overlap-add 拼起来。

这带来一个重要的概念区分——**"因果"与"有状态"是两件独立的事**：

| | 有跨帧状态 | 无跨帧状态 |
|---|---|---|
| 不读未来样本 | 经典流式 RNN/SSM（如 [[wiki_low_latency/entities/RT-SEMamba]]） | **PSMSE**：逐帧无状态 + OLA |
| 读未来样本 | 非因果离线模型 | —（无意义） |

PSMSE 落在右上格：它**合法地满足"不读取未来观测"**，但代价是没有任何长流记忆。可复用的判据是：**审计一个"流式"系统时，必须分别问"是否读未来"和"状态是否跨帧传递"，只答前者不能推出后者。**

这条区分能直接解释 PSMSE 消融里一个看似反常的结果：

| 变体 | PESQ |
|---|---:|
| 原始 | 2.85 |
| w/o Mamba | 2.80 |
| Replace Mamba with GRU | 2.83 |

**Mamba 相对 GRU 只赢 0.02 PESQ，去掉 Mamba 只掉 0.05**。如果 Mamba 真在承担跨帧长程建模，损失不该这么小。合理解释是：默认配置下 30 ms 帧（480 samples）经 kernel 20 / stride 10 编码后帧内只有约 47 个时间步，Mamba 的"长程"根本没有展开的空间——**论文的 SSM 叙事与它的无状态帧配置之间存在未言明的落差**。

## "稀疏性 → MACs"的换算逻辑与三个陷阱

### 换算逻辑

SNN 省算力的标准论证链是：脉冲是 0/1 事件 → 输入为 0 时乘加可跳过 → 有效运算量 ∝ 发放率。PSMSE 用 Table 9 的逐层发放率作为这条链的证据。

| Layer | Firing Rate |
|---|---:|
| BinaryConv | 0.2427 |
| SpikeConv | 0.1876 |
| Recurrent Layer | 0.1539 |
| Readout（两分支平均） | 0.3466 |

论文的解读是「most neurons remain inactive during inference」，并说明 Readout 偏高（0.3466）是因为它要聚合两条并行分支并把稀疏 spike 转回波形重建特征。

![[wiki_low_latency/assets/S2542660526001769/S2542660526001769-page19-table9-spike-firing-rate.png]]

> 图注：原论文 p.19 页面渲染，含 **Table 9**（逐层 spike 发放率）。论文声明 "Since spike firing rate is only meaningful for event-driven computation, we calculate it only for spiking layers." —— 这句话本身也界定了该指标的适用边界：它只对事件驱动层有意义，不能用来描述 Conv1D/ConvTranspose1D 等密集层。

### 陷阱 1：发放率 ≠ 被跳过的乘加比例

发放率是**逐层神经元被激活的比例**，而 MACs 是**矩阵乘加的规模**。两者之间还隔着：稀疏矩阵在目标硬件上是否真能跳过（GPU/CPU 上稀疏张量通常被 padding 回密集）、跳过的粒度（元素级/通道级/块级）、以及非脉冲层（Conv1D、BinaryConv、ConvTranspose1D、dense）的密集计算是否成为新瓶颈。

**PSMSE 的 0.11 G/s 到底是"理论密集量"还是"已按发放率折算的有效量"，论文没有说明。** 这是阅读任何 SNN 论文时最该追问的一句。

### 陷阱 2：MACs 下降 ≠ 能耗下降

论文在消融里写 "This means that the energy consumption of a regular neural network is several times that of the spiking structure presented in this paper." —— 这是**从 MACs 推断能耗**，不是测量。SNN 的能效优势只在 event-driven / neuromorphic 硬件上才真正兑现；在 RTX 3090 这类 GPU 上跑 SNN，脉冲张量仍是密集张量运算，功耗优势很可能不存在。PSMSE 全文**没有任何功耗或能量测量**。

可复用判据：**"MACs 更低"只能支持"计算规模更小"，要主张"更省电"必须给目标硬件上的实测能量或 pJ/op 折算。**

### 陷阱 3：两个 MACs 口径不能混写

PSMSE 自己就给了两个口径：Table 2 的 **0.11 G/s**（每秒音频的乘加量）与 Table 4 的 **1.05 G**（处理一个样本的总乘加量）。按 0.11 G/s 换算，1.05 G 对应约 9.5 s 音频，而论文又写样本统一为 5 s——**两者无法自洽，论文也未说明是否计入 50% OLA 的重复计算**。

这条与 [[wiki_low_latency/concepts/2409.10358-ultra-low-latency-benchmark]] 的账本原则一致：**复杂度的分母必须写清楚（per second / per frame / per sample / 是否含 OLA 重复），否则跨论文比较没有意义。**

## spike 发放率：一个值得纳入本 wiki 的新指标

本 wiki 现有的延迟账本字段是 window / hop / look-ahead / compute / I/O / deadline / state，**没有"稀疏度"字段**。PSMSE 提示应该补上：

| 建议字段 | 含义 | PSMSE 给出的示例 |
|---|---|---|
| spike firing rate（逐层） | 每层神经元在每个时间步发放的比例 | 0.15–0.35 |
| 有效 MACs 口径 | 理论密集量 vs 按稀疏度折算 | 未区分（缺口） |
| 稀疏跳过的粒度 | 元素/通道/块级，是否被硬件真正跳过 | 未报告（缺口） |
| 目标硬件稀疏支持 | 该硬件是否原生支持事件驱动 | 未验证（缺口） |

它的价值在于：**发放率是"这套 SNN 真的在稀疏工作吗"的直接体检指标**，比"我们用了 SNN"这种定性表述强得多。但要成为可比的效率证据，它必须与"有效 MACs 口径"和"目标硬件稀疏支持"一起报告——PSMSE 只给了第一项。

## 与本库其他概念的边界

| 概念 | 省算力的机制 | 与"并行 SNN+SSM"的关系 |
|---|---|---|
| [[wiki_low_latency/concepts/2608.12099-mamba-distillation]] | 深度蒸馏（8→1/2 层）+ **固定 recurrent SSM state 跨帧传播** | 同为 Mamba 流式路线，但**状态语义相反**：RT-SEMamba 有跨帧状态、PSMSE 没有。两页并读可得到"Mamba 流式"的两种合法语义 |
| [[wiki_low_latency/concepts/2411.02019-slowfast-ssm]] | **多速率复用**：慢支路输出跨多个 fast frame 复用 | 同样压 MAC、同样强调不读未来；但 SlowFast 复用的是"较旧的 stale context"，PSMSE 复用零上下文（无状态）。两条思路正交，可叠加 |
| [[wiki_low_latency/concepts/2205.05474-deep-filtering]] | 用少量 deep filter taps 做复数域精修 | DeepFilterNet2 是 PSMSE 的直接基线（Table 2：1.78 M / 0.35 G/s vs PSMSE 0.26 M / 0.11 G/s），但前者有嵌入式实测、后者没有 |
| [[wiki_low_latency/concepts/低时延前端与延迟账本]] | 把 window/hop/look-ahead/计算/I/O/deadline 分账 | PSMSE 只需在其中增加"帧间状态是否传递"与"稀疏度"两行 |
| [[wiki_low_latency/concepts/低 SNR 人声保留评估]] | 弱辅音/气声/过抑制的独立测量 | PSMSE 完全缺这一维度；Table 5 的 −5 dB babble 下 STOI 63.8% 正好是这类分析的适用场景 |

## 迁移到约 2 ms 的检查清单

若要把"并行 SNN + SSM"搬到本 wiki 的硬约束下，按现有证据需要补做：

1. **先解决帧长**：30 ms 帧必须换成个位数 ms 帧或短窗/非对称前端（参考 [[wiki_low_latency/concepts/2204.09911-short-asymmetric-stft]]）。注意 Fig. 14 显示帧长降到 10 ms 时 RTF 会升到约 30 ms 处的 2× 以上，且论文自己说 10–30 ms 质量还稳——10 ms 是有依据的起点，不是 30 ms。
2. **明确状态语义**：如果保留 Mamba，必须决定是"跨帧缓存 state"（像 RT-SEMamba 那样有持久记忆）还是"逐帧重置"。前者要报告 state reset/warm-up/flush 与长流稳定性，后者要报告帧边界不连续性和 OLA 引入的调制伪影。
3. **修正 PLIF 的 $\tau$**：不能同时使用 $\tau=2.0$ 与 $\tau\in(0,1)$，需先确定真实实现。
4. **把发放率变成可比的效率证据**：同时报告逐层发放率、有效 MACs 口径、稀疏跳过粒度、以及目标硬件是否原生支持事件驱动。
5. **补端侧证据**：量化后精度、峰值 SRAM、功耗、p50/p95/p99、deadline miss、underrun。PSMSE 明确把这些列为 future work。
6. **补人声保留**：false-suppression、SPP/VAD 校准、F0/formant continuity、voiced energy retention，以及按 SNR 分层的 SIG–BAK trade-off。
7. **帧间连续性**：无状态 + OLA 的组合天然缺连续性约束，可直接借用 [[wiki_low_latency/concepts/2203.16843-continuity-loss]] 的思路做跨帧平滑或帧间一致性损失。

## 关联

- 源论文：[[wiki_low_latency/sources/2026/PSMSE 2026]]
- 实体：[[wiki_low_latency/entities/PSMSE]]
- Mamba 流式的另一种语义：[[wiki_low_latency/concepts/2608.12099-mamba-distillation]]、[[wiki_low_latency/entities/RT-SEMamba]]
- 复用式省算力：[[wiki_low_latency/concepts/2411.02019-slowfast-ssm]]
- 延迟与复杂度账本：[[wiki_low_latency/concepts/2409.10358-ultra-low-latency-benchmark]]、[[wiki_low_latency/concepts/低时延前端与延迟账本]]、[[wiki_low_latency/concepts/严格因果与算法延迟]]
- 人声保留：[[wiki_low_latency/concepts/低 SNR 人声保留评估]]、[[wiki_low_latency/concepts/2203.16843-continuity-loss]]
- SSM 背景：[[wiki_array/concepts/Mamba SSM 状态空间模型]]

> [!question] 当前缺口
> PSMSE 证明的是"稀疏脉冲 + 无状态帧处理"能换来极低的 MACs 与参数量；它**没有**证明跨帧长程建模、端侧能效、量化鲁棒性或低 SNR 人声保留。要把它读成本方向的进展，缺的正是这四项。
