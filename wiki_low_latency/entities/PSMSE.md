---
title: PSMSE
type: entity
created: 2026-09-20
updated: 2026-09-20
tags:
  - speech-enhancement
  - spiking-neural-network
  - snn
  - plif
  - mamba
  - state-space-model
  - strict-causal
  - paper-claimed-causal
  - 30ms-algorithmic-latency
  - streaming
  - hearing-aid
  - edge-deployment
  - low-complexity
  - parallel-branch
sources:
  - [[wiki_low_latency/sources/2026/PSMSE 2026]]
related:
  - [[wiki_low_latency/concepts/S2542660526001769-spiking-mamba-streaming]]
  - [[wiki_low_latency/concepts/严格因果与算法延迟]]
  - [[wiki_low_latency/concepts/低时延前端与延迟账本]]
  - [[wiki_low_latency/concepts/2409.10358-ultra-low-latency-benchmark]]
  - [[wiki_low_latency/concepts/低 SNR 人声保留评估]]
  - [[wiki_low_latency/entities/RT-SEMamba]]
  - [[wiki_low_latency/entities/SlowFast-SSM]]
  - [[wiki_array/concepts/Mamba SSM 状态空间模型]]
---

# PSMSE

## 定义

**PSMSE**（Parallel Spiking Mamba for Speech Enhancement）是 Yang 等 2026 年发表于 *Internet of Things* 的单通道、16 kHz、时域波形到波形流式语音增强模型，面向 AIoT 可穿戴助听器。它的核心是在 bottleneck 里**并行**放两个脉冲模块——**SMC**（Spiking Mamba Convolution，局部时序）与 **SMR**（Spiking Mamba Recurrent，全局上下文）——并让 Mamba 直接作用在稀疏 spike 表征上。

论文报告的规模是 **0.26 M 参数 / 0.11 G/s MACs**（离线 VoiceBank-DEMAND 口径），是本 wiki 目前参数量与 MACs 最低的模型；代价是 **30 ms 算法延迟**（帧长即延迟），远超本 wiki 约 2 ms 的目标。

> [!contradiction] 必须先读的 caveat：Mamba state 不跨帧传递
> 论文 §4.3（p.6）原文："Explicit Mamba state caching is not used, so the Mamba states are re-initialized on each call and not propagated across consecutive frames."
> 也就是说 PSMSE 的"流式"是**逐帧无状态**的：每 30 ms 调用一次网络、每次从零初始化 SSM 状态，靠 50% overlap-add 拼接输出。它满足"不读未来样本"，但**没有跨帧的长流状态记忆**——SSM 递归 $\mathbf h_t=\overline{\mathbf A}\mathbf h_{t-1}+\overline{\mathbf B}\mathbf x_t$ 只在单帧内部（约 47 个时间步）成立。任何"long-range / streaming / causal"的表述都要加这个前置条件。

## 证据

| 属性 | 本地 PDF 证据 |
|---|---|
| 任务 | 单通道时域语音增强；助听器/AIoT 端侧；16 kHz（p.1, p.8） |
| 加性噪声模型 | $y(t)=x(t)+n(t)$，Eq. (1)，p.2 |
| 输入/输出 | noisy waveform → Conv1D(k=20, s=10, N=512) → ReLU + channel norm → BinaryConv1D → B=256 → 并行 SMC/SMR → Conv1D+Sigmoid 门控（乘 Skip Connection）→ ConvTranspose1D + 输入残差 → enhanced waveform；Fig. 2，p.6 |
| SMC 结构 | `SpikeConv1D → Mamba → PLIF Neurons → ReadoutLayer`；depthwise separable convolution 提局部时序；Fig. 1 (left)，p.5 |
| SMR 结构 | `DenseLayer` → 分两支：一支 `RecurrentLayer`（PLIF、帧内循环，带 "Get Neuron States"/"Spike" 反馈）→ `Mamba → PLIF → Readout`，另一支与之相加；Fig. 1 (middle)，p.5 |
| 并行而非级联 | "a parallel temporal processing module, containing two key components: SMC and SMR"；消融 Cascade 2.81 vs 并行 2.85，p.6 / Table 8，p.17 |
| PLIF 参数 | $\tau=2.0$、$V_{th}=1.0$、$V_{reset}=0$；同层共享 $\tau$、跨层独立；$\tau=1/(1+e^{-a})$ 可学习，Eq. (12)，p.4 / p.6 |
| Mamba 超参 | $d_{model}=32$、$d_{state}=16$、$d_{conv}=4$、expand $=2$；selective scan 与初始化沿用 Mamba 默认实现 [9]，p.6 |
| 损失 | $L=0.001\,L_{MSE}+L_{SI\text{-}SNR}+0.001(\lVert e_{proj}\rVert_1+\lVert e_{readout}\rVert_1)$，Eq. (13)，p.6 |
| 流式 | 30 ms 帧 chunk + 50% overlap-add；**Mamba state 每次调用重置、不跨帧**；conv lookahead 0 ms；端到端算法延迟 = 帧长 = 30 ms，p.6 / p.18 |
| 规模 | 0.26 M 参数；0.11 G/s MACs（Table 2）；DNS 表为 1.05 G per sample（Table 4，**不同口径**）；1 s 输入 FP32 峰值内存 266 MB，p.18 |
| 离线 VB-DEMAND | PESQ 2.85 / STOI 95.1% / CSIG 4.03 / CBAK 3.77 / COVL 3.61（Table 2，**non-causal**） |
| 流式 VB-DEMAND | PESQ 2.73 / STOI 93.9% / CSIG 3.85 / CBAK 3.29 / COVL 3.31（Table 3，**causal**） |
| DNS | PESQ 2.72 / STOI 94.6% / MACs 1.05 G per sample（Table 4，**non-causal**） |
| 助听器 | HASPI 0.90 / HASQI 0.60，端到端，优于 DeepFilterNet+HLC 0.89/0.56（Table 7，causal） |
| 发放率 | BinaryConv 0.2427 / SpikeConv 0.1876 / Recurrent 0.1539 / Readout 0.3466（Table 9，p.19） |

## 架构

~~~text
noisy waveform y(t)                                    [B, T]
  → Conv1D(kernel L=20, stride=10, out_channels N=512)
  → ReLU → channel-wise normalisation                  [N, T]
  → BinaryConv1D（带可学习阈值的 1D 卷积）             → bottleneck B = 256
  → Parallel Branch ─────────────────────────────────────────
      ├── SMC:  SpikeConv1D → Mamba → PLIF → Readout
      └── SMR:  Dense → ┬─ RecurrentLayer(PLIF, 帧内循环) → Mamba → PLIF → Readout
                        └─ (直连分支) ── 相加 ──┘
  ────────────────────────────────────────────────────────────
  → Conv1D → Sigmoid（门控）
  → ⊗ 与 encoder Skip Connection 相乘                   [N, T]
  → ConvTranspose1D + 原始输入残差
  → enhanced waveform
~~~

![[wiki_low_latency/assets/S2542660526001769/S2542660526001769-page6-psmse-overall-architecture.png]]

> 图注：原论文 p.6 Fig. 2 页面渲染（PDF 页面复制）。左侧 encoder、中部红框 Parallel Branch（SMC/SMR 并列）、右侧 Sigmoid 门控 + Skip Connection + ConvTranspose 三处是本模型的关键拓扑。

## 状态与因果性

| 状态对象 | 论文报告 | 本 Wiki 判定 |
|---|---|---|
| Mamba SSM hidden state | **不缓存，每次调用重新初始化，不跨帧传播**（p.6） | 帧间无状态；`non_causal` 不成立，但也不是"持久状态流式" |
| SMR RecurrentLayer / PLIF 膜电位 | Fig. 1 画出帧内循环与 "Get Neuron States" 反馈；**跨帧是否保留未报告** | 未报告，不可假定 |
| Encoder/BinaryConv 的卷积缓存 | 论文未提及 padding 策略与卷积历史缓存 | 未报告 |
| 帧间连续性机制 | 仅 50% overlap-add | `low_look_ahead`：不读未来样本，但需整帧 30 ms 输入先到齐 |
| look-ahead | 论文声称卷积 look-ahead = 0 ms | `paper-claimed-causal`，缺样本级 certificate |
| warm-up / reset / flush | 全部未报告 | 未验证 |

> [!question] 帧内序列长度与"长程建模"
> 30 ms @ 16 kHz = 480 samples，经 kernel 20 / stride 10 的 Conv1D 后帧内时间步约 $\lfloor(480-20)/10\rfloor+1\approx47$。也就是说默认配置下 Mamba 处理的序列长度只有约 47 步。论文的"long-range sequence-modelling"在帧内窗口的尺度上成立，但**没有跨帧长程**。这与消融中「w/o Mamba 只掉 0.05 PESQ、换成 GRU 只掉 0.02」的结果互相印证。

## 低时延账本

| 字段 | PSMSE 证据 / 边界 |
|---|---|
| 采样率 | 16 kHz |
| 帧长 | 30 ms = 480 samples（默认配置） |
| hop | 50% overlap-add → ≈15 ms = 240 samples（**论文未显式给出样本数**，由 50% OLA 推得） |
| overlap | 50%（论文唯一给出的流式拼接策略） |
| look-ahead | 论文声称 0 ms；未给逐层 padding/state certificate |
| 算法延迟 | 论文口径 = 帧长 = **30 ms**（"the end-to-end algorithmic latency is determined by the frame length"）；未单独报告 group delay |
| 状态 | Mamba state 每次重置；SMR 递归状态跨帧语义未报告；warm-up/reset/flush 未报告 |
| 计算 | 0.11 G/s MACs（离线口径）；Fig. 14 的 RTF–帧长曲线是唯一耗时证据（读图近似 30 ms 处约 5.3×10⁻³） |
| 峰值内存 | 1 s 输入 FP32 观测 266 MB；论文声明不代表最终助听器部署 |
| 量化 | **未做**；INT8/混合精度明确列为 future work |
| 端到端 | ADC/DMA、I/O buffer、线程调度、DAC/playout、capture-to-playback **均未报告** |
| deadline | p50/p95/p99、deadline miss、underrun/overrun **均未报告** |
| 硬件 | 训练/推理环境为 2×RTX 3090 + Xeon Silver 4314；**助听器级 DSP/MCU 未验证** |
| 功耗 | **未测量**；论文用 MACs 下降推断能效（0.11 vs 0.61 G/s），这是推断不是测量 |

实体判定：**paper-level strict causal（帧间无状态口径）/ 30 ms algorithmic latency / 无硬件与 p99 证据**。不能简化为"2 ms 严格因果助听器系统"。

![[wiki_low_latency/assets/S2542660526001769/S2542660526001769-page18-fig14-frame-length-rtf.png]]

> 图注：原论文 p.18 页面渲染。上半为 **Fig. 14**（帧长 10–100 ms 对 PESQ / STOI / RTF 的影响），下半是 §6.7 中"30 ms 帧 + 50% OLA + 0 ms look-ahead + 端到端算法延迟 = 帧长 + 266 MB FP32 峰值内存 + 量化留作 future work"的原文段落，是本实体延迟账本的主要出处。**从曲线读出的近似值**：PESQ 10 ms→30 ms 为 2.76→2.71，之后单调降至 100 ms 的 2.61；STOI 在 10–30 ms 稳定在 93.8–93.9%，之后降到 92.8%；RTF（$\times10^{-3}$）从 10 ms 的 11.8 快速降到 30 ms 的 5.3，再平缓降到 100 ms 的 2.2。30 ms 是"质量已开始下降、但 RTF 收益基本吃完"的拐点。

## 配置速查

| 组件 | 值 |
|---|---|
| encoder | Conv1D kernel 20 / stride 10 / N=512；ReLU + channel-wise norm |
| bottleneck | BinaryConv1D → B=256（带可学习阈值的 1D 卷积） |
| Mamba | $d_{model}=32$、$d_{state}=16$、$d_{conv}=4$、expand 2 |
| PLIF | $\tau=2.0$、$V_{th}=1.0$、$V_{reset}=0$；同层共享 $\tau$ |
| decoder | ConvTranspose1D + 输入残差 |
| 损失 | $0.001 L_{MSE}+L_{SI\text{-}SNR}+0.001(\lVert e_{proj}\rVert_1+\lVert e_{readout}\rVert_1)$ |
| 训练 | Adam lr 3e-4 + cosine、$\beta=(0.99,0.999)$、≤500 epochs、top-3 ckpt、batch 32/GPU × 2、约 13 h |
| 数据 | DNS 550 h + CommonVoice 11.0 英语 550 h + VCTK 80 h（VAD 0.5 / DNSMOS 3.0 过滤）→ 约 600 h，SNR ∈[−5,20] dB |
| 个性化 | 1×8 audiogram → dense → 与波形特征同维（10 ms 帧时 =160）→ concat；目标为 NAL-R + WDRC 预处理的干净语音 |

> [!contradiction] PLIF 的 $\tau$ 初值与 Eq. (12) 值域互斥
> Eq. (12) 定义 $\tau=1/(1+e^{-a})\in(0,1)$，但 §4.3 写网络初始化 $\tau=2.0$。若 $\tau=2.0$ 成立，Eq. (9) 展开后泄漏系数 $(1-\tau)=-1$，膜电位更新变成符号翻转的不稳定形式。论文未解释，也未报告训练后的 $\tau$ 值。实体的膜动力学因此**不能按论文公式定量复现**。

> [!question] $B=256$ 与 $d_{model}=32$ 之间缺一环
> binary convolution 投影到 256 维 bottleneck，Mamba 的 $d_{model}=32$，两者的映射方式（再降维/分组/并行 8 组？）论文与 Fig. 1/2 均未说明，影响 MACs 的独立核算。

## 结果与证据边界

![[wiki_low_latency/assets/S2542660526001769/S2542660526001769-page10-table2-offline-voicebank.png]]

> 图注：原论文 p.10 **Table 2**（离线 / non-causal，VoiceBank-DEMAND）页面渲染。核对 PSMSE 行的 0.26 M / PESQ 2.85 / STOI 95.1% / CSIG 4.03 / CBAK 3.77 / COVL 3.61 / MACS 0.11 G/s；同表可见 DeepFilterNet（1.78 M / 0.35 G/s）与 L-DPSB（1.16 M / 49.90 G/s）作为复杂度两端的参照。注意表内 Year 列把 PSMSE 标为 2025，与本文 2026 年出版不符。

- **支持**：在 Table 2 的对比集合内，PSMSE 是参数量与 MACs 最低者（0.26 M / 0.11 G/s），且 CBAK（3.77）与 COVL（3.61）为表内最高；流式（causal）口径下 PESQ 2.73 为该表最高；助听器 HASPI/HASQI（0.90/0.60）优于全部所列基线；SNN→ANN 替换使 MACs 涨 5.5×，是稀疏性主张的唯一硬证据。
- **不支持**：约 2 ms 已达成；跨帧状态连续性；长流稳定性；目标 SoC 的 p99/deadline；量化后精度；功耗；多通道；false-suppression / 低 SNR 人声保留。
- **未报告**：单帧/单次前向的 MAC 数；$L_{SI\text{-}SNR}$ 展开式；训练后实际 spike 发放率与损失值；seed/方差；代码与预训练模型；Table 2–4 基线是否同条件复现（论文自述取自原论文报告）。
- **量化缺口**：Table 2 的 0.11 G/s 与 Table 4 的 1.05 G per sample 无法互推（1.05 ÷ 0.11 ≈ 9.5 s，与 5 s 样本约定不符），两处口径不得混写。

## 交叉链接

- 源论文：[[wiki_low_latency/sources/2026/PSMSE 2026]]
- 概念页：[[wiki_low_latency/concepts/S2542660526001769-spiking-mamba-streaming]]
- 延迟审计：[[wiki_low_latency/concepts/严格因果与算法延迟]]、[[wiki_low_latency/concepts/低时延前端与延迟账本]]、[[wiki_low_latency/concepts/2409.10358-ultra-low-latency-benchmark]]
- 人声保留缺口：[[wiki_low_latency/concepts/低 SNR 人声保留评估]]
- 同分支对照：[[wiki_low_latency/entities/RT-SEMamba]]（Mamba + 跨帧固定状态 + KD，25 ms）、[[wiki_low_latency/entities/SlowFast-SSM]]（多速率复用降 MAC）
- SSM 背景：[[wiki_array/concepts/Mamba SSM 状态空间模型]]
- 嵌入式参照：[[wiki_low_latency/entities/DeepFilterNet2]]、[[wiki_low_latency/entities/On-TasNet]]
