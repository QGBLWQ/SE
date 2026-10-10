---
title: D-GRU
type: entity
created: 2026-09-22
updated: 2026-09-22
tags:
  - speech-enhancement
  - single-channel
  - streaming
  - gru
  - d-gru
  - dg-rnn
  - select-gate
  - dynamic-computation
  - neuron-level-sparsity
  - compute-efficient
  - paper-claimed-causal
  - 20ms-window
  - 10ms-hop
sources:
  - [[wiki_low_latency/sources/2024/D-GRU 2024]]
related:
  - [[wiki_low_latency/concepts/2408.12425-dynamic-gated-rnn]]
  - [[wiki_low_latency/entities/Skip-DPCRN]]
  - [[wiki_low_latency/entities/RT-Tango]]
  - [[wiki_low_latency/entities/DPCRN]]
  - [[wiki_low_latency/entities/SlowFast-SSM]]
  - [[wiki_low_latency/entities/FSB-LSTM]]
  - [[wiki_low_latency/concepts/2207.11108-inference-skipping-parallel-rnn]]
  - [[wiki_low_latency/concepts/严格因果与算法延迟]]
  - [[wiki_low_latency/concepts/低时延前端与延迟账本]]
  - [[wiki_low_latency/concepts/低 SNR 人声保留评估]]
---

# D-GRU

## 定义

**D-GRU**（Dynamic Gated Recurrent Unit）是本地论文 2408.12425 提出的循环单元。它把该文提出的 **DG-RNN** 框架（Dynamic Gated Recurrent Neural Network）的选择性更新策略套到标准 GRU 上：每一步**只更新隐状态中 $z_t$ 值最大的前 $A$ 个神经元**（$A=(P/100)\cdot J$，$P$ 为预设的、跨步恒定的更新百分比），其余神经元**保持上一步的值**，从而在**推理期**把 GRU 的算力压到常规 GRU 的

$$
\frac{1 + 2P/100}{3}
$$

倍。其核心巧思是：**select gate 直接复用 GRU 本来就要计算的 update gate $z_t$，因此不引入任何额外参数**——$P=50$ 时 GRU 层算力为 66.66%（省 33.33%），三个测试骨干的整体算力分别降到 GRU 69% / MPT 75% / DPRNN 71%。

论文口径：16 kHz、320-point FFT、20 ms 帧长、10 ms hop（50% overlap）；三个骨干均被论文称为 **causal**，但**论文没有给出逐层 padding/状态清单，也没有给出任何延迟数字**。本库判定为 `paper-claimed-causal`，且**延迟账本为空**。这不是本 Wiki 约 2 ms 目标的已验证系统。

> [!note] D-GRU 与 DG-RNN 的关系
> **DG-RNN** 是通用框架（select gate 由任意网络 $\mathcal{G}$ 算出，Eq. 1）；**D-GRU** 是该框架的一个具体实现（令 $\mathcal{G}$ 退化为"直接取 $z_t$"，Eq. 7）。本页记录的是 D-GRU 实体；框架层面的抽象见 [[wiki_low_latency/concepts/2408.12425-dynamic-gated-rnn]]。

## 证据

| 属性 | 本地 PDF 证据 |
|---|---|
| 任务 | 单通道 speech enhancement（回归任务，论文强调这一点以区别于 Skip RNN 系列的分类任务）；DNS Challenge 数据集，p.3 §4.1–§4.2 |
| 前端 | 16 kHz；**320-point FFT**；帧长 **20 ms**、overlap **10 ms**（⇒ hop = 160 samples = 10 ms、50% overlap、帧率 100 帧/s）；p.3 §4.2 |
| 骨干 1：GRU | FC + 2 层 GRU + FC；第一层 FC 与两层 GRU 的输出维均为 **320**；末层 FC 输出 **IRM** [20]；**1.34 M**；p.3 §4.1 |
| 骨干 2：MPT | 2 个 MPT block（Multi-Path Transformer [15]），每块含 **4 个 GRU**；输入/输出维 **24 / 48**；输出 **IRM + magnitude deep-filtering 系数** [21]；**0.28 M**；p.3 §4.1 |
| 骨干 3：时频域 DPRNN | 4 个 dual-path block（引文 [11]），每块 **3 个 GRU**；每个 GRU 的输入输出维均 **64**；**直接输出**估计干净语音的**复数谱**；**0.35 M**；p.3 §4.1 |
| 损失 | GRU 与 MPT：增强与目标幅度谱的 **MSE**；DPRNN：幅度 MSE 与复数谱 MSE 的**平均**；p.3 §4.1 |
| select gate（通用） | $g_t=\mathcal{B}(\mathcal{G}(x_t,h_{t-1}))$，$g_t\in\{0,1\}^J$，$J$ = 神经元总数，Eq. (1)，p.2 §2 |
| select gate（D-GRU） | $g^j_t=1$ iff $z^j_t$ 属于 $z_t$ 的 **top-$A$** 最大值，$A=(P/100)\cdot J$，Eq. (7)，p.2 §3.2 |
| 被否掉的替代方案 | 阈值型：$g^j_t=1$ iff $z^j_t>\theta^j$，Eq. (8)。否掉理由：每步更新数不固定 → 算力动态变化 → 硬件仍须按最坏情况预留全部算力；**其性能被明确留作 future work、从未评估**，p.2 §3.2 |
| 隐状态更新 | $h^j_t=z^j_t*c^j_t+(1-z^j_t)*h^j_{t-1}$ if $g^j_t=1$，否则 $h^j_t=h^j_{t-1}$，Eq. (9)，p.2 §3.2 |
| 被跳过的计算 | $g^j_t=0$ 时 $r^j_t$ 与 $c^j_t$ **完全跳过**（Eq. 10–11）；注意 Eq. (10)(11) 中 $h_{t-1}$ 仍是完整向量，被裁剪的是**输出行数**，p.3 §3.2 |
| 成本公式 | $\text{cost(D-GRU)}/\text{cost(GRU)}=(1+2P/100)/3$；$z$ 不能省（top-A 选择需要完整 $z_t$），$r$ 与 $c$ 各只需 $P\%$；$P\in\{100,75,50,25\}$ ⇒ $\{100\%,83.33\%,66.66\%,50\%\}$，p.3 §3.3 与 §4.1 |
| select gate 开销 | top-$A$ 选择复杂度 $O(J)$（引 [19] = Cormen 等《Introduction to Algorithms》，**线性时间选择，不是排序**），论文称其相对 GRU 更新可忽略，p.3 §3.3 |
| 参数量 | GRU 1.34 M / MPT 0.28 M / DPRNN 0.35 M；**D-GRU 不增加参数**——Table 1 中每个骨干的 `Para. (M)` 只列一次、跨全部 $P$ 档位，p.3 Table 1 |
| 算力（MAC/s） | GRU：135.32 → 114.48 (84%) → 93.65 (69%) → 72.83 (53%)；MPT：282.32 → 247.19 (87%) → 212.06 (75%) → 176.96 (62%)；DPRNN：5689.37 → 4876.14 (85%) → 4062.92 (71%) → 3250.19 (57%)（顺序为 $P=100,75,50,25$），p.3 Table 1 |
| 因果性 | 论文原话「three strong causal speech enhancement models」（p.3 §4.1）；**无逐层 padding/state certificate、无 STFT 帧锚定说明、无 DPRNN chunk 长度**，p.3 §4.1 |
| 延迟 | **完全未报告**：无算法延迟、无 RTF、无端到端。论文只报 MACs |
| 统计检验 | Mann-Whitney U [25]（理由：测试数据非正态），**只对 PESQ**；p<0.05 为显著；Table 2，p.4 |

## 架构与状态

~~~text
通用 DG-RNN 更新（Eq. 1–2）
  x_t, h_{t−1}  ──►  G(·) ──► B(·) ──► g_t ∈ {0,1}^J     （每步恰好 A 个 1）
  h^j_t = F^j(x_t, h_{t−1})   if g^j_t = 1     ← 走正常 RNN 更新
  h^j_t = h^j_{t−1}            if g^j_t = 0     ← 保留上一步值

D-GRU 实现（G 退化为「取 z_t」，零额外参数）
  ┌── r_t = σ(W_ir x_t + b_ir + W_hr h_{t−1} + b_hr)      Eq. (3)  ← 只需 P% 行
  ├── z_t = σ(W_iz x_t + b_iz + W_hz h_{t−1} + b_hz)      Eq. (4)  ← 必须全算（要用来选 top-A）
  ├── c_t = tanh(W_ic x_t + b_ic + r_t * (W_hc h_{t−1} + b_hc))  Eq. (5)  ← 只需 P% 行
  └── h_t = z_t * c_t + (1 − z_t) * h_{t−1}                Eq. (6)
                    │
         ┌──────────┴──────────┐
         ▼                     ▼
  top-A(z_t) → g_t        g^j_t = 0 的神经元：r^j_t、c^j_t 全部跳过（Eq. 10–11）
  A = (P/100)·J            h^j_t = h^j_{t−1}
  O(J) 线性时间选择 [19]

三个被测试的骨干（论文口径，参数量跨全部 P 档位不变）
  1) GRU     : FC → GRU(320) → GRU(320) → FC → IRM              1.34 M   [串行，无并行通路]
  2) MPT     : 2 × MPT block（每块 4 GRU，in/out 24/48）→ IRM + DF 系数   0.28 M
  3) DPRNN   : 4 × dual-path block（每块 3 GRU，in/out 64）→ 复数谱      0.35 M
~~~

> [!note] 架构上最值得记住的一点：**GRU 骨干是串行的，D-GRU 照样能用**
> Table 1 里的 GRU 骨干是 `FC → GRU → GRU → FC` 的**纯串行**结构，没有多条并行 RNN 通路。[[wiki_low_latency/entities/Skip-DPCRN]] 那条「Skip-RNN 需要 parallel RNN 宿主才不出伪影」的**结构前提**在这里不成立也无需成立——因为 D-GRU 跳的是**神经元**而非**整步**，$h_t$ 始终存在并向后传递。这是两个实体最本质的差别，详见 [[wiki_low_latency/concepts/2408.12425-dynamic-gated-rnn]]。

## 低时延账本

| 字段 | D-GRU 证据/边界 |
|---|---|
| 采样率 | 16 kHz（p.3 §4.2） |
| FFT / 帧长 / hop | 320-point FFT；帧长 20 ms（= 320 samples）；overlap 10 ms（⇒ hop = 160 samples = 10 ms、50% overlap）；帧率 **100 帧/s**（本页由 hop 推得） |
| 频率点数 | $F=161$（**本页按 320-point FFT 推得**，论文未明写） |
| STFT center / padding / 帧锚定 | **未报告**。若 center=True 则前端含 $W/2=10$ ms 未来样本；若左对齐则不含。论文未涉及 |
| 算法延迟 | **未报告**——论文没有给出任何 latency 数字（无 window−hop、无 $W/2$、无推导式） |
| GRU 时间维方向 | 论文级声明 "three strong causal speech enhancement models"；无单向/双向说明，无逐层 state 清单 → `paper-claimed-causal` |
| MPT 因果性 | `unreported`：MPT 内部是否含跨帧注意力/padding 未在 5 页内说明 |
| DPRNN 因果性 | `unreported`：**chunk 长度未报告**；dual-path 通常隐含块级处理，若 intra-chunk 沿时间轴处理整块则存在块级 look-ahead |
| 状态语义 | 跳步是**神经元级**：$h_t$ 每步都存在并向后传递，只有部分分量保持 $h_{t-1}$；时间步链**不断裂**，因此不产生 Skip-RNN 的"输出冻结"伪影 |
| 状态漂移 | 论文承认 "infrequent updates of some neurons might result in inaccurate representations of the current state, **introducing internal noise**"，但**未报告**神经元被选中间隔分布、长期未更新神经元占比、长流性能衰减、state reset、warm-up |
| 算力 | Table 1 报 MAC/s；$P$ 固定 ⇒ **每步算力恒定**（MAC 计数层面，设计保证）；**未报告** p99、per-step wall-clock、峰值 RAM/SRAM |
| 运行时 | **未报告**：无 RTF、无目标硬件、无部署栈（ONNX/TFLite 等） |
| 端到端与 deadline | ADC/DMA、I/O buffer、线程调度、DAC/playout、capture-to-playback、underrun/overrun **全部未报告** → 未验证 |

实体判定：**`paper-claimed-causal`（仅一句集合声明）/ 延迟完全未报告 / 算力为固定 MAC 计数（非输入相关）/ 无任何硬件或 wall-clock 证据**。

> [!warning] 这个实体在本库的特殊性：它是唯一"只有 MACs、没有延迟"的记录
> 本库其他论文至少给出一个（哪怕未拆分的）延迟数字。D-GRU 只报 MAC/s，而 MACs 是**吞吐/能耗**指标，不是延迟指标。因此：
> - **不能**由 hop = 10 ms 反推任何"算法延迟"结论——论文自己也没做这个关联；
> - **不能**把"算力省 33%"读成"延迟降 33%"——top-A 是数据相关算子，会引入 gather/scatter 与不规则内存访问，论文完全没有测量这一点（见 [[wiki_low_latency/sources/2024/D-GRU 2024]] §5 第 6 条）。

## 结果与证据边界

- **支持**：$P\ge50\%$ 时三个骨干的 PESQ 差异**统计不显著**（Table 2 全部配对 p>0.05），此时 GRU 层算力省 33.33%、整体模型算力降到 GRU 69% / MPT 75% / DPRNN 71%；Table 1 的全部 MAC 数字可由 $(1+2P/100)/3$ **逐行精确重建**（本库独立复算，九行吻合）；**参数量跨全部 $P$ 档位不变**（零额外参数）；在 {−5,0,5} dB 附加集上趋势一致（Figure 2）。
- **不支持**：约 2 ms 级系统已达成；实时 deadline 已通过；算力节省已转化为 wall-clock/功耗收益；每步算力恒定性已被**测量**（只在 MAC 计数层面成立）；长流下状态漂移可控；低 SNR 人声保留已证明；阈值型 select gate 的质量代价已知。
- **未报告**：算法延迟、RTF、目标硬件、p50/p95/p99、峰值 RAM/SRAM、量化/定点、功耗、deadline miss、underrun/overrun、state reset、warm-up、长流稳定性、per-SNR 分层数值（只有 Figure 2 柱状图）、DNSMOS **SIG/BAK** 分项、false-suppression、ASR WER、F0/formant/prosody、SPP/VAD 校准、训练超参（优化器/lr/batch/steps/seeds）、DPRNN chunk 长度、MPT block 内部结构。
- **可比性提醒**：Table 1 的 `noisy` 行是同一批测试数据上的下界（PESQ 1.58）；`All layers` 列的百分比是相对**该骨干自身**的 $P=100$ 基线，**不同骨干之间不可横比**（DPRNN 的 5689 M MAC/s 与 GRU 的 135 M MAC/s 相差 42 倍）。D-GRU 的 MACs 是**固定值**（$P$ 恒定），这一点与 [[wiki_low_latency/entities/Skip-DPCRN]] 的**输入相关平均 MACs** 不同——前者的 MACs 可与固定算力模型横比，后者不能。
- **数字口径警示**：摘要与 §1 写 "50% reduction in GRU computes / computation costs"，但按本文自己的 Eq. (3.3) 与 §5，$P=50$ 的真实节省是 **33.33%**；"50%"指的是**神经元比例**。本库一律采用 33.33%。

## 交叉链接

- 源论文：[[wiki_low_latency/sources/2024/D-GRU 2024]]
- 概念展开：[[wiki_low_latency/concepts/2408.12425-dynamic-gated-rnn]]
- 直接竞品（整步跳过 vs 神经元级跳过）：[[wiki_low_latency/entities/Skip-DPCRN]]、[[wiki_low_latency/sources/2022/Skip-DPCRN 2022]]、[[wiki_low_latency/concepts/2207.11108-inference-skipping-parallel-rnn]]
- 同为帧级稀疏的另一种实现：[[wiki_low_latency/entities/RT-Tango]]、[[wiki_low_latency/sources/2026/RT-Tango 2026]]
- dual-path 家族对照：[[wiki_low_latency/entities/DPCRN]]、[[wiki_low_latency/sources/2021/DPCRN Low-Latency Direction 2021]]、[[wiki_low_latency/concepts/2107.05429-dual-path-recurrent-context]]
- 同为"利用时间冗余降算力"：[[wiki_low_latency/entities/SlowFast-SSM]]、[[wiki_low_latency/sources/2024/SlowFast-SSM 2024]]、[[wiki_low_latency/concepts/2411.02019-slowfast-ssm]]
- 低时延时频掩蔽对照：[[wiki_low_latency/entities/FSB-LSTM]]、[[wiki_low_latency/sources/2023/FSB-LSTM 2023]]
- 因果时域对照：[[wiki_low_latency/entities/On-TasNet]]、[[wiki_low_latency/sources/2021/On TasNet Low-Latency SE 2021]]
- 延迟审计口径：[[wiki_low_latency/concepts/严格因果与算法延迟]]、[[wiki_low_latency/concepts/低时延前端与延迟账本]]
- 最严因果口径（尺子）：[[wiki_low_latency/sources/2026/LaCo-SENet 2026]]、[[wiki_low_latency/entities/LaCo-SENet]]
- 人声保留缺口：[[wiki_low_latency/concepts/低 SNR 人声保留评估]]

> [!question] 待验证
> **(1)** 三个骨干的因果性只有一句集合声明，**无逐层 certificate**；DPRNN 的 chunk 长度未报告，块级 look-ahead 无法排除。
> **(2)** 「每步算力恒定」是 MAC 计数层面的设计保证，**从未被测量**——top-A 稀疏在真实硬件上的 gather/scatter 收益、以及选择算子本身的开销，都未做 wall-clock 测量。
> **(3)** Table 2 的 p 值来自 Mann-Whitney U 检验，而同一批 150 条测试语音在四档 $P$ 上重复使用（**样本是配对的**），未配对检验会降低效力；论文未说明是否做配对处理，也未做多重比较校正。引用 p 值时不宜按精确数值对待。
