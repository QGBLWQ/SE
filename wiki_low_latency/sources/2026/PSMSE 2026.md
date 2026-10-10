---
title: PSMSE - 并行脉冲 Mamba 轻量流式语音增强（助听器）
type: source
created: 2026-09-20
updated: 2026-09-20
tags:
  - speech-enhancement
  - single-channel
  - spiking-neural-network
  - snn
  - plif
  - mamba
  - ssm
  - streaming
  - strict-causal
  - paper-claimed-causal
  - 30ms-algorithmic-latency
  - hearing-aid
  - edge-deployment
  - aiot
  - low-complexity
  - parallel-branch
  - journal-article
source_type: paper
year: 2026
authors: Junkang Yang; Hiromitsu Nishizaki; Chee Siang Leow; Hongqing Liu; Lu Gan
venue: Internet of Things, 39 (2026) 102046 (Elsevier)
doi: 10.1016/j.iot.2026.102046
local_pdf: raw/papers/low_latency_causal_se/1-s2.0-S2542660526001769-main.pdf
evidence_policy: local_pdf_only
related:
  - [[wiki_low_latency/entities/PSMSE]]
  - [[wiki_low_latency/concepts/S2542660526001769-spiking-mamba-streaming]]
  - [[wiki_low_latency/concepts/严格因果与算法延迟]]
  - [[wiki_low_latency/concepts/低时延前端与延迟账本]]
  - [[wiki_low_latency/concepts/2409.10358-ultra-low-latency-benchmark]]
  - [[wiki_low_latency/concepts/低 SNR 人声保留评估]]
  - [[wiki_low_latency/sources/2026/RT-SEMamba 2026]]
  - [[wiki_low_latency/concepts/2608.12099-mamba-distillation]]
---

~~~yaml
- 论文: [Lightweight streaming speech enhancement for AIoT-enabled wearable hearing aids using parallel spiking mamba](2026)
  ├── 要解决什么问题: 助听器/可穿戴端侧同时满足「流式 + 极轻量 + 可个性化」三重约束；CNN/RNN 感受野贵、Transformer 二次复杂度、SNN 单独用时时序建模弱、Mamba 直接吃 dense 波形又太贵
  ├── 核心方法: PSMSE = 波形域因果 encoder → bottleneck 内 **并行** SMC(Spiking Mamba Convolution) + SMR(Spiking Mamba Recurrent) → decoder 残差；Mamba 直接作用在 spike 表征上，PLIF 神经元可学习膜时间常数，binary convolution 投影 bottleneck
  ├── 属于哪个分支: 单通道时域波形增强 / 脉冲神经网络 SNN / SSM-Mamba / 流式因果 / 助听器端侧
  ├── 输入/输出: noisy waveform y(t)=x(t)+n(t) → Conv1D(k=20,s=10,N=512)+ReLU+channel norm → BinaryConv1D → B=256 bottleneck → 并行 SMC/SMR → Conv1D+Sigmoid 门控 → ConvTranspose1D + 输入残差 → enhanced waveform
  ├── 关键trick: (1) SMC 与 SMR **并行**而非级联（消融证明并行 PESQ 2.85 > 级联 2.81）；(2) Mamba 跑在 sparse spike 表征而非 dense 波形；(3) 用 SNN 替换 ANN 把 MACs 从 0.61 压到 0.11 G/s；(4) spike L1 稀疏正则
  ├── 数据集: 训练 DNS 550 h + CommonVoice 11.0 英语 550 h + VCTK 80 h（经 VAD/DNSMOS 过滤，共约 600 h，SNR 随机 [-5,20] dB）；噪声 DNS + WHAM! + NoiseX92；测试 VoiceBank-DEMAND、DNS 2020 no-reverb、AISHELL-1+IEEE ICME 2024（域偏移）、Clarity 100 条 audiogram
  ├── 对比了谁: DCCRN、DPCRN、TSTNN、DeepFilterNet、FFC-AE-V0/V1、FFC-Unet、CCFNet+、aTENNUate、L-DPSB、HiFi-Stream(-2D)、DEMUCS、HiFi++、NSNet、CA DU-Net、FasNet TAC、TPARN、ADCN、DRC-Net、DeFT-AN；Table 2-4 中标注的基线数值取自原文报告
  ├── 性能上限: 离线 VB-DEMAND PESQ 2.85 / STOI 95.1% / CBAK 3.77(表内最高) / COVL 3.61；流式 PESQ 2.73 / STOI 93.9% / COVL 3.31(表内最高)；DNS PESQ 2.72 / STOI 94.6%；助听器 HASPI 0.90 / HASQI 0.60
  ├── 参数量: 0.26 M 参数；0.11 G/s MACs（离线 VB-DEMAND 口径）；DNS 表为 1.05 G per sample（不同口径）；1 秒输入 FP32 峰值内存 266 MB
  ├── 消融关键发现: 去 SNN → MACs 0.11→0.61 G/s 且 PESQ 掉到 2.75；去 SMR 掉最多(2.85→2.70, STOI 93.2%)；去 SMC → 2.76；去 binary conv → MACs 0.11→0.31 且 PESQ 2.78；去 Mamba → 2.80；Mamba→GRU → 2.81；PLIF→LIF → 2.81；去稀疏损失 → 2.82；并行 vs 级联 2.85 vs 2.81
  ├── 遗留问题(你的机会): 30 ms 算法延迟远超本 wiki 约 2 ms 目标；**Mamba 状态每次调用重置、不跨帧传递**，长流一致性只靠 50% OLA 混合；无真实助听器/DSP/MCU 硬件验证、无 p99/deadline、无量化后精度、无功耗实测、无多通道结果
  └── 跟哪篇像: [[wiki_low_latency/sources/2026/RT-SEMamba 2026]]（同为 Mamba 流式路线）、[[wiki_low_latency/sources/2024/SlowFast-SSM 2024]]（同为低 MAC 状态空间）、[[wiki_low_latency/sources/2023/FSB-LSTM 2023]]（同为低复杂度全带/子带）
~~~

# Lightweight streaming speech enhancement for AIoT-enabled wearable hearing aids using parallel spiking mamba

> Junkang Yang, Hiromitsu Nishizaki, Chee Siang Leow, Hongqing Liu, Lu Gan. *Internet of Things* **39** (2026) 102046，doi:10.1016/j.iot.2026.102046，开放获取 CC BY。Received 3 Apr 2026 / Revised 23 Jun 2026 / Accepted 27 Jul 2026 / Available online 28 Jul 2026。基金：JSPS KAKENHI 23H00493、25H00566。
> 这是本 wiki 第一篇**期刊长文**（21 页，Elsevier），不是 arXiv 短文；frontmatter 因此用 `venue` + `doi` 替代 `arxiv` 字段。本页把论文的 "real-time" 拆成**因果性、算法延迟、MACs/内存、硬件部署**四个独立证据。

> [!warning] PDF 转换质量与阅读说明
> 原 PDF 共 21 页。`tmp/pdf_extract/S2542660526001769.txt` 的正文文字抽取基本可用，但本文**希腊字母与上下标密集**，抽取文本存在以下已知风险，凡涉及这些位置本页均以**页面渲染图**二次核对：
> - 公式区（Eq. 1–14）中的 $\tau$、$V_{th}$、$V_{reset}$、$\overline{\mathbf A}/\overline{\mathbf B}$、$\Delta$、$\mathbf h_t$ 等符号在纯文本中会丢上下标（例如 `𝐀= exp(Δ𝐀)` 实为 $\overline{\mathbf A}=\exp(\Delta\mathbf A)$）。
> - 表格（Table 1–9）在纯文本中列结构会串行，数字需逐列对齐；Table 2 的 "MACS [G/s]" 与 Table 4 的 "MACs [G]" 是**两种不同口径**，纯文本极易误读。
> - 参考文献 [1]–[71] 混排在正文末尾，不影响正文判读。
>
> 已实际打开并逐项核对的页面渲染图（`wiki_low_latency/assets/S2542660526001769/`）：
> **p.4**（Eq. 4–12，PLIF/LIF 公式）、**p.5**（Fig. 1 SMC/SMR/Mamba 模块图）、**p.6**（Fig. 2 整体架构 + Eq. 13–14 + Mamba 状态重置原句）、**p.7**（Fig. 3 流式框架）、**p.10**（Table 2 离线）、**p.11**（Table 3 流式 + Table 4 DNS + Fig. 6）、**p.17**（Table 8 消融）、**p.18**（Fig. 14 帧长/RTF + 30 ms 延迟与 266 MB 内存原句）、**p.19**（Table 9 发放率）。
> 未逐页核对的图表（Fig. 4/5/7–13、Table 1/5/6/7）只引用正文明确写出的数字，不从图中读数；凡从曲线图读数者（Fig. 10 下游指标、Fig. 14 的 RTF 数值）在本页明确标注为「读图近似」。

## 1. 他们为什么这么做？（motivation）

### 1.1 任务与对象

单通道、16 kHz、时域波形到波形（waveform-to-waveform）的流式语音增强，面向 AIoT 可穿戴助听器。论文开篇给出加性噪声模型：

$$
y(t)=x(t)+n(t),
$$

其中 $y(t)$ 是观测到的含噪语音，$x(t)$ 是干净语音，$n(t)$ 是加性噪声。目标是求最优估计 $\hat x(t)$：

$$
\hat x(t)=\arg\min_{\hat x}\ \mathbb E\big[\mathcal L\big(x(t),\hat x(t)\big)\big],
$$

$\mathcal L(\cdot)$ 是回归损失函数。注意论文把任务定义在**时域波形**上，不走 STFT 复数域；这与本库多数低时延论文（DCCRN/DPCRN/DeepFilterNet2/RT-SEMamba）走时频域不同。

### 1.2 论文动机

论文把助听器约束归纳为三重（Section 2.2）：**极低计算延迟 → 必须严格因果、不能用未来帧**；**毫瓦级功耗预算 → 大 DNN 不可用**；**必须个性化 → 要与听力图/验配公式（NAL-R）对齐**。论文自评「few works currently fully resolve the triple constraints of streaming, lightweight computation, and personalisable enhancement」，这就是它要填的缝。

### 1.3 论文引用的三条现实动机

- 助听器是 AIoT 里典型的 cyber-physical-human system；WHO 数据称全球 5% 以上人口（4.3 亿）需要听力损失康复 [10]。
- 传统 CNN/RNN 要覆盖长程时序必须放大感受野，成本上升；Transformer 对序列长度是 $O(N^2)$，不适合低功耗端侧流式。
- SNN 的事件驱动稀疏性天然匹配 neuromorphic 低功耗硬件，但「SNNs alone often underperform on complex acoustic tasks due to their limited ability to model rich temporal dynamics」；Mamba 长程建模近线性，但「their direct application to streaming audio remains challenging due to the computational burden of processing dense waveform inputs」。

PSMSE 的定位就是把这两条互补的短板互相补上：**用 SNN 的稀疏性解决 Mamba 吃 dense 波形的成本，用 Mamba 的长程建模解决 SNN 时序能力弱**。

## 2. 之前的人怎么做不了？（limitation → gap）

| 路线 | 能力 | 仍然卡在哪里（论文口径） |
|---|---|---|
| 传统 CNN / RNN 时域增强 | 结构简单、可流式 | 要长程上下文就得堆感受野，算力随之上涨 |
| Transformer / CleanUNet2 等 | 全序列依赖建模、SOTA 质量 | $O(N^2)$ 复杂度，「prohibitive for streaming applications」 |
| 超轻量网络 FSPEN / GTCRN / [[wiki_low_latency/entities/LiSenNet\|LiSenNet]] / UL-UNAS | 23.7K–79K 参数 | 「performance tends to degrade due to the limited capacity of their simplified designs」 |
| SNN 路线（spiking transformer [19]、Spiking-FullSubNet [20]、SpikingS4 [21]、DPSNN [22]） | 事件驱动、低功耗 | SNN 单独用时时序建模能力有限；Table 1 中多数在频谱图域 |
| Mamba/SSM 路线（Mamba-SEUNet [23]） | 近线性长序列建模 | 多数是时频域 + 双向 TS-Mamba 块，不是严格因果流式；直接吃 dense waveform 计算负担大 |
| DeepFilterNet 等轻量实时方案 | 端侧可用 | 「compromise noise suppression performance in complex, non-stationary environments」 |
| 传统助听器管线（降噪 → HLC 级联） | 模块可解释 | 「decoupling often leads to suboptimal interaction between modules and accumulated bias」 |

论文归纳的 gap 是**三约束同时满足**：流式 + 极轻量 + 可个性化。三条路线各有一半答案，但没有一篇同时给全。

### 2.1 严格因果与延迟账本

> 依据：Section 4.3 末段（p.6）、Section 4.4 + Fig. 3（p.7）、Section 6.7 末段（p.18）、Section 5.2（p.9）。

| 审计项 | PDF 证据（原文） | 本 Wiki 判定 |
|---|---|---|
| 帧长（frame length） | "input is processed causally using 30-ms frame chunks"（p.6）；"The proposed streaming system uses a frame length of 30 ms"（p.18） | 30 ms = 16 kHz 下 480 samples；**算法延迟下限**，不是 strict-causal 的证明 |
| hop / frame shift | "with a 50% overlap-add strategy"（p.18）；Fig. 3 标注 "Frame Shift" 与 "Computation Latency" | 50% overlap → hop ≈ 15 ms（240 samples）。论文**未显式给出 hop 的样本数**，由 50% OLA 推得 |
| overlap / OLA | 50% overlap-add（p.18） | 合成端需要缓存半帧与前帧尾部叠加；不读取未来样本，但要求**整帧 30 ms 输入先到齐** → `low_look_ahead` |
| look-ahead | "Since the proposed model is strictly causal and does not use future frames, the convolutional lookahead is 0 ms."（p.18） | 论文自述 **0 ms look-ahead**；标为 `paper-claimed-causal`，缺样本级 padding/state certificate |
| Mamba state 传递 | "Explicit Mamba state caching is not used, so the Mamba states are re-initialized on each call and not propagated across consecutive frames."（p.6） | **不跨帧传递**：模型在帧间是"无状态"映射，见下方 `[!contradiction]` |
| 递归状态（SMR / PLIF 膜电位） | Fig. 1 (middle) 画出 `RecurrentLayer` 与 "Get Neuron States"/"Spike" 反馈箭头，说明**帧内**存在循环状态；但论文**未报告**该状态是否跨帧保留、warm-up 几帧、何时 reset | 未报告 → 不能确认跨帧状态连续性；`[!question]` |
| 每帧 MACs | 只给 **0.11 G/s MACs**（每秒音频的乘加量，Table 2）；**未给单次前向/单帧 MAC 数** | 不能直接换算成"每 15 ms 的推理预算"；`[!question]` |
| 峰值内存 | "For a 1-second speech input during inference, the observed peak memory usage is 266 MB."（p.18） | 1 s 输入 **FP32** 观测峰值 266 MB；论文自己声明「does not directly represent the memory requirement of a final hearing-aid deployment」 |
| 端到端 | "the end-to-end algorithmic latency is determined by the frame length, i.e., 30 ms in the default setting."（p.18） | 这是 **algorithmic latency**，不是 capture-to-playback；ADC/DMA、driver buffer、线程调度、DAC/playout、deadline miss、underrun/overrun **全部未报告** |
| 计算耗时 | 只有 Fig. 14 的 RTF–帧长曲线（读图近似：10 ms≈11.8e-3、30 ms≈5.3e-3、100 ms≈2.2e-3） | GPU/训练同环境（2×RTX 3090, Xeon Silver 4314），**不是目标 SoC 的 p50/p95/p99** |

**结论**：PSMSE 可以标为「论文级 strict causal、30 ms algorithmic latency、GPU 平均吞吐充足」。**不能**标为本方向约 2 ms 的已验证系统——差距是 15×。更关键的是，"严格因果"在这里是靠**帧间无状态**实现的，而不是靠跨帧状态传递实现的（见 §3.4）。

## 3. 这个做法核心 trick 是什么？

### 3.1 整体管线

~~~text
noisy waveform y(t)   [B, T]
  → Conv1D(kernel L=20, stride=10, channels N=512) → ReLU → channel-wise norm   [N, T]
  → BinaryConv1D (可学习阈值的 1D 卷积)  → bottleneck B = 256
  → Parallel Branch（并行，非级联）
      ├── SMC  (Spiking Mamba Convolution)
      │     SpikeConv1D → Mamba → PLIF Neurons → ReadoutLayer
      └── SMR  (Spiking Mamba Recurrent)
            DenseLayer → 分两支
              支路1: RecurrentLayer(PLIF, 帧内循环, "Get Neuron States" 反馈) → Mamba → PLIF → Readout
              支路2: 直接与支路1输出相加
  → Conv1D → Sigmoid 门控 → 与 encoder 侧 Skip Connection 相乘   [N, T]
  → ConvTranspose1D  +  原始输入残差
  → enhanced waveform
~~~

![[wiki_low_latency/assets/S2542660526001769/S2542660526001769-page6-psmse-overall-architecture.png]]

> 图注：原论文 p.6 **Fig. 2** 页面渲染（PDF 页面复制，非重画）。核对要点：左侧 encoder 为 `Conv1D → ReLU → LayerNorm → BinaryConv1D`（正文写作 "channel-wise normalisation"）；中部红框 **Parallel Branch** 内 SMC 与 SMR 是上下**并列**两个分支；右侧 `Conv1D → Sigmoid` 产生门控并与 Skip Connection 相乘，再经 `ConvTranspose` 输出。图中标注的 `[B,T]`/`[N,T]` 维度可用来核对 bottleneck 与 encoder 通道数。

![[wiki_low_latency/assets/S2542660526001769/S2542660526001769-page5-smc-smr-mamba-modules.png]]

> 图注：原论文 p.5 **Fig. 1** 页面渲染。左 **SMC**：`SpikeConv1D → Mamba → PLIF Neurons → ReadoutLayer`（纯前馈、无循环）。中 **SMR**：`DenseLayer` 后分两支，一支经 `RecurrentLayer`（带 "Get Neuron States"/"Spike" 反馈，即帧内循环）与另一支相加后进 `Mamba → PLIF Neurons → ReadoutLayer`。右 **Mamba**：`LP(Linear Projection) → SiLU(σ) / SSM` 双支路 + `Conv` + 再投影，即标准 Mamba block 结构。注意 SMR 的循环箭头是**模块内部沿帧内时间步**的递归，图上没有画出跨帧的状态传递。

### 3.2 Trick A（论文自认的主贡献）：SMC 与 SMR **并行**，而不是级联

论文把 architectural novelty 明确写成："the parallel integration of SMC and SMR modules for jointly modelling local acoustic features and global temporal dependencies"。SMC 负责**局部**（depthwise 卷积提局部时序 + Mamba），SMR 负责**全局**（帧内循环 + Mamba）。论文的解释是并行「can fuse local features extracted by SMC with global contextual information captured by SMR more effectively, thereby avoiding information bottlenecks or feature loss that may occur in the cascaded structure」。

这条 trick 有直接消融支撑：并行 2.85 vs 级联 2.81（Table 8），且两者参数量/MACs 完全相同（0.26 M / 0.11 G/s）——**这是表里唯一"同预算、只换拓扑"的干净对照**。

### 3.3 Trick B：让 Mamba 跑在 spike 表征上

论文的关键设计句是 "A key innovation is that the Mamba component operates directly on spike-based representations, significantly reducing sequence complexity compared to raw waveform processing." 即 Mamba 的输入不是 dense 波形，而是已经稀疏化的脉冲表征。消融中「把 SNN 换成普通 ANN」使 MACs 从 0.11 涨到 0.61 G/s（5.5×），同时 PESQ 反而掉到 2.75 —— 论文据此认为这是「the mismatch between the ANN's structure and the original framework」。

SSM/Mamba 的状态转移与离散化（Eq. 3–8）：

$$
\frac{d\mathbf h(t)}{dt}=\mathbf A\mathbf h(t)+\mathbf B\mathbf x(t),\qquad
\mathbf y(t)=\mathbf C\mathbf h(t),
$$

$\mathbf h(t)\in\mathbb R^N$ 是隐状态，$\mathbf x(t)\in\mathbb R$ 是输入信号（论文举的例子就是 audio waveform），$\mathbf A$ 是系统演化矩阵。Mamba 的核心改动是把静态 $\mathbf B,\mathbf C$ 变成输入相关的投影：$\mathbf B(\mathbf x)=\mathrm{Linear}_B(\mathbf x)$、$\mathbf C(\mathbf x)=\mathrm{Linear}_C(\mathbf x)$，即 selection mechanism。离散化用零阶保持（ZOH）：

$$
\overline{\mathbf A}=\exp(\Delta\mathbf A),\qquad
\overline{\mathbf B}=(\Delta\mathbf A)^{-1}\big(\exp(\Delta\mathbf A)-\mathbf I\big)\cdot\Delta\mathbf B,
$$

$\Delta$ 是控制离散步长的时间尺度参数。离散形式：

$$
\mathbf h_t=\overline{\mathbf A}\mathbf h_{t-1}+\overline{\mathbf B}\mathbf x_t,\qquad
\mathbf y_t=\mathbf C(\mathbf x_t)\mathbf h_t .
$$

**这里就是本页最需要标注的地方**：上式中的 $\mathbf h_{t-1}\to\mathbf h_t$ 递归只在**单次前向调用内部**成立。论文明确说不做 Mamba state caching，每次调用重新初始化（见 §3.4 的 `[!contradiction]`）。因此这条递归式子描述的是帧内（约 47 个时间步，见下）的状态演化，不是跨 30 ms 帧的长流演化。

### 3.4 Trick C：PLIF 神经元与 spike 事件

LIF 的三阶段（charging / firing / resetting）在论文里写作 Eq. 9–11：

$$
U[t]=U[t-1]+\tau\cdot\big(X[t]-(U[t-1]-V_{th})\big),
$$

$U[t]$ 是膜电位，$X[t]$ 是当前输入，$\tau$ 是控制泄漏率的 decay factor，$V_{th}$ 是阈值。展开后等价于 $U[t]=(1-\tau)U[t-1]+\tau X[t]+\tau V_{th}$，即带阈值的指数泄漏。发放由 Heaviside 阶跃函数给出：

$$
S[t]=\Theta\big(U[t]-V_{th}\big),
$$

复位是硬复位：

$$
U'[t]=\big(1-S[t]\big)\cdot U[t]+S[t]\cdot V_{reset},
$$

$U'[t]$ 是更新后的膜电位：发脉冲则强制拉到 $V_{reset}$，不发则保留充电阶段的值。因为 Heaviside 不可导，训练时用 sigmoid 作为 surrogate gradient 近似其导数。

PLIF 相对 LIF 的唯一区别是把 $\tau$ 参数化（Eq. 12）：

$$
\tau=\frac{1}{1+e^{-a}},
$$

$a$ 是可学习参数。论文说这样既保证 $\tau\in(0,1)$，又让网络自适应优化膜时间常数；并且**同层神经元共享同一个 $\tau$**（对齐生物学观察），**不同层各自独立**。

网络实际配置：SMC 的 PLIF「膜时间常数、发放阈值、复位值初始化为 $\tau=2.0$、$V_{th}=1.0$、$V_{reset}=0$」。

> [!contradiction] $\tau=2.0$ 与 $\tau=\mathrm{sigmoid}(a)\in(0,1)$ 直接冲突
> Eq. (12) 把 PLIF 的 $\tau$ 定义为 $\tau=1/(1+e^{-a})$，取值范围严格是 $(0,1)$；但 Section 4.3 写网络初始化 $\tau=2.0$。两者不可能同时成立：
> - 若 $\tau$ 真被约束在 $(0,1)$，则初始值应为 0.5 附近的某个数，$\tau=2.0$ 无法由 sigmoid 产生；
> - 若真取 $\tau=2.0$，则 Eq. (9) 展开后的泄漏系数 $(1-\tau)=-1$，膜电位更新退化为 $U[t]=-U[t-1]+2X[t]+2V_{th}$，是**符号翻转的发散形式**，不是稳定泄漏积分。
> 论文没有解释这个不一致（也没有报告训练后学到的 $\tau$ 具体值）。因此本页只能照实记录：**PLIF 的 $\tau$ 初值与 Eq. (12) 的值域互斥**，实际实现细节需看代码或复现才能确定。这不影响"PLIF 优于 LIF"的消融方向（2.81 vs 2.85），但影响对膜电位动力学的定量理解。

脉冲事件被定义为离散 0/1 信号（Eq. 14）：

$$
\mathrm{event}(t)=
\begin{cases}
1 & \text{if membrane potential } V(t)\ge \text{threshold}\\
0 & \text{otherwise}
\end{cases}
$$

论文强调 "These events are sparse, event-driven, discrete signals, analogous to the action potentials emitted by biological neurons."

### 3.5 损失函数：SI-SNR 主项 + 极小的 MSE 与 spike L1 正则

$$
L=0.001\times L_{MSE}+L_{SI\text{-}SNR}+0.001\big(\lVert e_{proj}\rVert_1+\lVert e_{readout}\rVert_1\big),
$$

- $L_{MSE}$：时域均方误差，权重被压到 0.001；
- $L_{SI\text{-}SNR}$：尺度不变信噪比损失，是**主项**（权重 1，论文未写系数）；
- $e_{proj}$：SMC 中 spike 卷积输出的 spike 激活；
- $e_{readout}$：解码层之前的 spike；
- 最后一项是 spike 稀疏性 L1 正则，权重同为 0.001，作用是压制脉冲发放率。

论文没有给出 $L_{SI\text{-}SNR}$ 的展开式，也没有报告训练后 $e_{proj}/e_{readout}$ 的实际 L1 值，因此「稀疏性正则到底把发放率压了多少」无法从现有材料量化（消融只给了"去掉它 PESQ 2.82 vs 2.85"）。

### 3.6 网络超参（Section 4.3 原文）

| 组件 | 配置 |
|---|---|
| encoder | Conv1D，kernel $L=20$、stride $=10$、输出通道 $N=512$；ReLU + channel-wise normalisation |
| bottleneck 投影 | **binary convolution**（带可学习阈值的 1D 卷积），投影到 $B=256$ 维 |
| Mamba | $d_{model}=32$、$d_{state}=16$、$d_{conv}=4$、expand factor $=2$；selective scan 与参数初始化沿用 Mamba 默认实现 [9] |
| PLIF | $\tau=2.0$、$V_{th}=1.0$、$V_{reset}=0$（见 §3.4 的冲突标注） |
| decoder | ConvTranspose1D + 对原始输入波形的 residual connection |
| 流式 | 30 ms 帧 chunk + 50% overlap-add；Mamba state 不缓存、每次调用重置 |

> [!question] bottleneck 维度 $B=256$ 与 Mamba $d_{model}=32$ 之间缺一环
> 论文写 binary convolution 把 encoder 的 512 通道投影到 $B=256$ 维 bottleneck，又写 Mamba 的 $d_{model}=32$。从 256 到 32 的映射（是再降维、分组、还是 8 组 $d_{model}=32$ 并行？）论文**没有说明**，Fig. 1/2 也未标注该维度变换。这会影响对 MACs 预算的独立核算。
> 另外，30 ms 帧（480 samples）经 kernel 20 / stride 10 的 Conv1D 后，帧内时间步约为 $\lfloor(480-20)/10\rfloor+1\approx 47$ 步（未计 padding）。也就是说 Mamba 的"长程建模"在**默认配置下只在约 47 步、即 30 ms 的窗口内**进行。论文未讨论这一点对"long-range sequence modelling"叙事的限制。

### 3.7 个性化模块（Section 4.5）

- 纯音测听得到 250 Hz–8 kHz 的听力阈值 → 1×8 的 audiogram 张量；
- 该张量过 **dense 层**变成与波形特征**同维**的张量（论文举例：帧长 10 ms 时该维度 = 160，即 16 kHz × 0.01 s），然后与含噪输入**concat** 融合成 PSMSE 的输入；「This operation exists in each frame.」
- 参考干净语音先经 **NAL-R + WDRC** 预处理作为目标；
- 用 **PSMSE 输出与 NAL-R+WDRC 模块输出之间的损失**训练整个系统；
- 相关指标 HASPI（可懂度预测）/ HASQI（助听音质）。
- 论文补充：audiogram 之外，车载声学场景的音域特征向量、移动设备的说话人结构等也可用同样方式接入。

## 4. 实验里哪个消融最关键？

### 4.1 数据、训练与评价

- 训练：16 kHz、每帧 0.03 s 上下文、batch 32/GPU × 2 GPU（有效 batch 64）、Adam lr $3\times10^{-4}$ + cosine annealing、$\beta=(0.99,0.999)$、最多 500 epochs、按验证集保留 top-3 checkpoint、PyTorch、2×NVIDIA RTX 3090、单次完整训练约 13 h、CPU 为 Intel Xeon Silver 4314。
- 数据清洗（Algorithm 1）：VAD（SpeechBrain）算 active speech ratio，$r_i<\tau_{vad}=0.5$ 丢弃；再过 DNSMOS，$s_{dnsmos}<\tau_{dnsmos}=3.0$ 丢弃。阈值参考 URGENT challenge [41]。清洗后训练集约 **600 h**，10% 作验证；SNR 为随机整数 $\in[-5,20]$ dB，样本统一 16 kHz / 5 s。
- 噪声源：DNS、WHAM!、NoiseX92。audiogram 来自 Clarity challenge，共 100 条真实助听器用户数据，85% 训练 / 15% 评测，train/test 不重叠。
- 指标：PESQ、STOI、CSIG/CBAK/COVL、参数量、MACs、下游任务（SpkSim / EmoSim / CAcc，用 ESPNet + VERSA + Emo2Vec）、助听器指标 HASPI/HASQI。
- **因果性口径（Section 5.2 关键句）**："The models evaluated in Tables 3, 7, and Fig. 14 are implemented under a causal inference setting, whereas the other comparisons follow a non-causal inference setting." → **Table 3（流式）、Table 7（助听器）、Fig. 14（帧长）是因果推断；Table 2（离线）与 Table 4（DNS）是非因果推断**。这一句是理解本页所有数字的前提。
- 基线口径："the results of the models listed in Tables 2–4 are taken from the metrics reported in their original papers, while the remaining baseline models are retrained using the same training data as PSMSE" → **Table 2–4 的数字不是同条件复现，不能当排行榜**。

### 4.2 结果表

**Table 2 — 离线（non-causal）VoiceBank-DEMAND**（数字照抄原文 p.10）：

| Models | Year | Para [M] | PESQ | STOI [%] | CSIG | CBAK | COVL | MACS [G/s] |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Noisy | — | — | 1.97 | 79.0 | 3.34 | 2.82 | 2.74 | — |
| DCCRN | 2020 | 3.67 | 2.67 | 93.7 | 3.53 | 2.43 | 3.08 | 24.69 |
| DPCRN | 2021 | 0.67 | 2.51 | 93.5 | 2.94 | 3.25 | 2.70 | 4.81 |
| TSTNN | 2021 | 0.92 | 2.75 | 94.0 | 3.93 | 3.44 | 3.34 | 19.95 |
| DeepFilterNet | 2022 | 1.78 | 2.81 | 94.2 | 4.14 | 3.31 | 3.46 | 0.35 |
| FFC-AE-V0 | 2022 | 0.42 | 2.67 | 86.5 | 4.06 | 3.30 | 3.37 | 4.06 |
| CCFNet+ | 2023 | 0.62 | 3.03 | 95.0 | 4.27 | 3.55 | 3.61 | 1.47 |
| aTENNUate | 2025 | 0.84 | 3.14 | 94.2 | 4.30 | 2.62 | 3.73 | 0.33 |
| L-DPSB | 2025 | 1.16 | 3.00 | 96.0 | 3.96 | 3.75 | 3.52 | 49.90 |
| HiFi-Stream | 2025 | 1.17 | 2.70 | 86.5 | 4.03 | 3.22 | 3.37 | 1.90 |
| HiFi-Stream-2D | 2025 | 0.50 | 2.65 | 86.4 | 4.02 | 3.17 | 3.35 | 1.97 |
| **PSMSE** | **2025** | **0.26** | **2.85** | **95.1** | **4.03** | **3.77** | **3.61** | **0.11** |

论文自评：CBAK 3.77 与 COVL 3.61 是表内最高；STOI 95.1% 仅次于 L-DPSB（96.0%）；PESQ 2.85 低于 aTENNUate（3.14）。**注意 Year 列把 PSMSE 标成 2025，与本文 2026 年出版不符**（原文表格笔误或预印年份）。该表为**非因果（离线）**推断口径。

**Table 3 — 流式（causal）VoiceBank-DEMAND**（数字照抄原文 p.11）：

| Models | PESQ | STOI [%] | CSIG | CBAK | COVL |
|---|---:|---:|---:|---:|---:|
| Noisy | 1.97 | 79.0 | 3.34 | 2.82 | 2.74 |
| DEMUCS | 2.66 | 88.1 | 3.82 | 3.23 | 3.24 |
| FFC-AE-V0 | 2.00 | 78.9 | 3.50 | 2.80 | 2.74 |
| FFC-AE-V1 | 2.42 | 86.0 | 3.90 | 3.21 | 3.17 |
| FFC-Unet | 2.45 | 86.1 | 3.97 | 3.22 | 3.22 |
| HiFi++ | 2.37 | 93.0 | 3.84 | 3.16 | 3.10 |
| HiFi-Stream | 2.30 | 84.5 | 3.67 | 2.86 | 2.98 |
| HiFi-Stream-2D | 2.29 | 84.7 | 3.68 | 2.93 | 2.98 |
| **PSMSE** | **2.73** | **93.9** | **3.85** | **3.29** | **3.31** |

论文自评：PESQ 2.73 为表内最高，超过次优 DEMUCS（2.66）；STOI 93.9% 领先 HiFi++（93.0）；COVL 3.31 与 CBAK 3.29 均为表内最高；唯一让位的是 CSIG，FFC-Unet 3.97 > PSMSE 3.85。

**Table 4 — DNS 测试集**（数字照抄原文 p.11；"MACs here is the total MAC operations processing one sample"）：

| Models | Para [M] | PESQ | STOI [%] | MACs [G] |
|---|---:|---:|---:|---:|
| Noisy | — | 1.38 | 59.0 | — |
| NSNet | 1.3 | 2.18 | — | 7.24 |
| DCCRN | 3.67 | 1.95 | 93.2 | 140.53 |
| DPCRN | 0.67 | 2.16 | 93.3 | 27.61 |
| CA DU-Net | 26.0 | 1.99 | 83.0 | — |
| FasNet TAC | 2.9 | 2.26 | 87.0 | 55.3 |
| TPARN | 3.2 | 2.75 | 92.0 | 71.8 |
| ADCN | 9.3 | 2.84 | 92.0 | 72.8 |
| DRC-Net | 2.6 | 2.79 | 89.0 | 13.9 |
| DeFT-AN | 2.7 | 3.01 | 92.0 | 95.6 |
| **PSMSE** | **0.26** | **2.72** | **94.6** | **1.05** |

![[wiki_low_latency/assets/S2542660526001769/S2542660526001769-page11-table3-4-streaming-dns.png]]

> 图注：原论文 p.11 页面渲染，同页含 **Fig. 6**（参数量–质量三维散点，PSMSE 用圆圈标出）、**Table 3**（流式/causal，VoiceBank-DEMAND）与 **Table 4**（DNS，per-sample MACs）。用于核对 Table 3 与 Table 4 的列头差异——Table 3 无 MACs 列，Table 4 的 MACs 是「per sample」而不是「per second」。

**离线 vs 流式的差异（本页必须讲清）**：

| 口径 | PESQ | STOI | CSIG | CBAK | COVL |
|---|---:|---:|---:|---:|---:|
| Table 2 离线（non-causal） | 2.85 | 95.1 | 4.03 | 3.77 | 3.61 |
| Table 3 流式（causal） | 2.73 | 93.9 | 3.85 | 3.29 | 3.31 |
| 差值 | −0.12 | −1.2 pt | −0.18 | **−0.48** | −0.30 |

**因果化最伤的是 CBAK（−0.48），其次是 COVL（−0.30）**，说明"不能看未来"主要代价落在残留噪声/伪影控制上，而 PESQ 与 STOI 的损失相对温和（−0.12 / −1.2 pt）。这与"因果约束先伤抑噪能力"的直觉一致，是本页最有信息量的一组对照。
> [!note] 该对照的可比性边界
> Table 2 与 Table 3 的**对比模型集合不同**（前者含 DCCRN/DPCRN/TSTNN/CCFNet+/L-DPSB 等，后者含 DEMUCS/FFC 系列/HiFi 系列），因此**两表之间的排名不可跨表比较**。但 **PSMSE 这一行是同一个模型在两种推断口径下的结果**，其差值（尤其 CBAK −0.48）作为"同一模型因果化代价"的估计是有效的。论文本身没有把这两行并排讨论，这一对照是本页的独立整理。

> [!question] Table 2 的 0.11 G/s 与 Table 4 的 1.05 G 无法互推
> Table 4 明说 "MACs here is the total MAC operations processing one sample"。若按 Table 2 的 0.11 G/s 换算，1.05 G ÷ 0.11 G/s ≈ **9.5 s** 音频——但论文在 §5.2 说训练/验证样本统一为 5 s，DNS 测试集也未说明平均时长。两处口径无法自洽，论文也没有说明 1.05 G 是否已包含 50% OLA 的重复计算或 padding。**本页因此不把 0.11 G/s 与 1.05 G 混写**，两者各自保留原表口径。

> [!question] 正文与 Table 5 有一处数字对不上
> §6.3 正文写 "PSMSE achieves the highest PESQ scores of 1.13 and 1.19 under babble noise and factory noise, respectively, significantly outperforming the second-best DEMUCS (1.11 and 1.14)"。但 Table 5 中 DEMUCS 在 factory / −5 dB 的值是 **1.13**，不是 1.14（同列 PSMSE 为 1.19）。差异只有 0.01，不影响结论方向，但属于正文与表格不一致，引用时应以表格为准。

**其余结果（非本 wiki 主战场，仅登记）**：

- Table 5（babble / factory / white × SNR −5/0/5 dB）：PSMSE 在 babble 的 PESQ 为 1.13/1.33/1.75（STOI 63.8/81.9/91.5）；factory 1.19/1.41/1.78（STOI 70.4/84.1/91.6）；white 1.35/1.55/1.93（STOI 80.0/86.7/92.1）。**−5 dB babble 下 PESQ 仅 1.13、STOI 63.8%**——这是本页最诚实的低 SNR 数字，说明该类系统在 babble 低 SNR 下离"人声保留"仍很远。
- Table 6（域偏移：AISHELL-1 汉语 + IEEE ICME 2024 噪声，SNR ∈[−5,20] dB，150 条）：PSMSE PESQ 2.33 / STOI 85.9% / CAcc 82.57%，优于 DeepFilterNet（2.11 / 83.4 / 82.03）；DCCRN、DPCRN 的 CAcc 反而低于 Noisy 基线（76.30 / 79.44 vs 80.24），论文归因于过增强引入非线性失真。
- Table 7（助听器，causal，MBGS 模拟听损 + Clarity audiogram）：HLC-only 的 NAL-R 0.35/0.28、NAL-NL2 0.38/0.25、WDRC 0.41/0.31（HASPI/HASQI）；两阶段 DCCRN+HLC 0.84/0.46、DPCRN+HLC 0.85/0.49、DEMUCS+HLC 0.87/0.53、DeepFilterNet+HLC 0.89/0.56；**PSMSE（End-to-End）0.90/0.60**。论文据此主张端到端联合优化优于"降噪 + HLC 级联"。
- Fig. 10（下游任务，VoiceBank-DEMAND，**读图近似**）：PSMSE CAcc 96.53%、SpkSim 90.01%、EmoSim 99.23%。注意 Noisy 基线 SpkSim 为 90.03%，PSMSE 的 90.01% 与之几乎持平（论文表述为 "nearly matching that of the original speech"），即**在说话人相似度上并未超过不做任何处理**，只是没有像 DPCRN（85.09%）/DEMUCS（86.75%）那样明显退化。

### 4.3 最关键的消融判断

**Table 8 — 架构消融**（照抄原文 p.17；全部为离线口径）：

| Item | PESQ | STOI | #Params | MACS [G/s] |
|---|---:|---:|---:|---:|
| Original Settings | 2.85 | 95.1 | 0.26 | 0.11 |
| Cascade Structure | 2.81 | 95.0 | 0.26 | 0.11 |
| w/o SMC | 2.76 | 94.5 | 0.19 | 0.07 |
| w/o SMR | **2.70** | **93.2** | 0.17 | 0.06 |
| w/o SNNs | 2.75 | 94.5 | 0.26 | **0.61** |
| w/o Mamba | 2.80 | 94.9 | 0.22 | 0.10 |
| Replace Mamba with GRU | 2.83 | 94.6 | 0.25 | 0.10 |
| Replace PLIF with LIF | 2.81 | 94.7 | 0.26 | 0.10 |
| w/o sparsity loss | 2.82 | 94.7 | 0.26 | 0.10 |
| w/o binary convolution | 2.78 | 94.6 | 0.26 | **0.31** |
| w/o Algorithm 1 | 2.79 | 94.8 | 0.26 | 0.11 |

判断（按信息量排序）：

1. **最关键：w/o SNNs（0.11 → 0.61 G/s）**。这是全表唯一的**量级级**效应——把脉冲神经元换回普通 ANN，MACs 涨 5.5× 且 PESQ 同时掉到 2.75。它同时支撑了「SNN 省算力」和「SNN 与这套结构匹配」两个论点，是论文 efficiency 主张的**唯一硬证据**。但要注意：**MACs 降 5.5× 不等于能耗降 5.5×**，论文没有测功耗/能量。
2. **第二关键：w/o SMR（2.85 → 2.70，STOI 93.2%）**。掉点最多，说明全局上下文（帧内循环 + Mamba）是主要贡献者；论文解释为 "the core role of global contextual information"。w/o SMC → 2.76，说明局部细节也不能丢（"relying solely on global information while ignoring local spectral details can compromise the precision of speech reconstruction"）。
3. **结构对照最干净：Cascade Structure（2.81 vs 2.85）**。参数量与 MACs 完全不变、只换拓扑，是"并行优于级联"的直接证据。不过差距只有 0.04 PESQ，属于**边际收益**，论文的 "main architectural novelty" 叙事与实际增益幅度之间存在落差。
4. **binary convolution（0.11 → 0.31 G/s，PESQ 2.78）**：MACs 涨近 3×，说明这个"带可学习阈值的 1D 卷积"是 sparsity 的第二根支柱，与 SNN 并列。
5. **Mamba 的必要性较弱**：w/o Mamba 只掉到 2.80，换成 GRU 只掉到 2.83。也就是说在 30 ms 帧内（约 47 步）序列上，Mamba 相对 GRU 的优势是**边际的**。这与论文 "Mamba provides a more effective long-range sequence-modelling capability" 的措辞相比，证据强度偏弱——很可能正是因为**帧内序列太短、且帧间无状态**，长程建模能力根本没被用上。
6. PLIF vs LIF（2.81）与去掉稀疏损失（2.82）都是小幅掉点，方向正确但强度弱。

**帧长实验（Fig. 14）为什么选 30 ms**（曲线细节见 [[wiki_low_latency/entities/PSMSE]] 中 p.18 页面渲染）：论文给了两条机制解释——(1) RTF 侧，帧长越长单位时间前向次数越少，但 100 ms 后固定开销与"随帧长线性增长的 encoder 单层成本"成为主导，边际收益递减；(2) 质量侧，超过 30 ms 后「a longer frame length results in a significantly reduced update frequency for spiking neurons」，脉冲刷新率下降削弱了对快速变化语音的跟踪能力。**注意论文未报告每个帧长下的绝对推理耗时或 p99，RTF 只是相对趋势。**

### 4.4 发放率（Table 9）——本 wiki 值得单独登记的新指标

| Layer | Firing Rate |
|---|---:|
| BinaryConv | 0.2427 |
| SpikeConv | 0.1876 |
| Recurrent Layer | 0.1539 |
| Readout（两分支平均） | 0.3466 |

论文声明 "Since spike firing rate is only meaningful for event-driven computation, we calculate it only for spiking layers."；并解释 Readout 发放率偏高（0.3466）是因为它要聚合两条并行分支的输出并把稀疏 spike 转回波形重建用的特征（页面渲染见 [[wiki_low_latency/concepts/S2542660526001769-spiking-mamba-streaming]]）。

**但论文没有说明发放率与 MACs 之间的定量关系**——即 0.19 的发放率是否就意味着 19% 的乘加被跳过，以及 0.11 G/s 的 MACs 是"理论密集量"还是"已按发放率折算的有效量"。这是本页最重要的一个未闭合缺口（详见 concept 页）。

## 5. 这个方向还剩什么问题没解决？（future work / limitation）

**论文自己承认的**：

- **只在算法层面评估效率，未在助听器级嵌入式硬件上验证**："the present hardware evaluation should be interpreted as an assessment of algorithmic efficiency rather than a complete validation on hearing-aid-class embedded hardware."
- **量化留作 future work**："Implementing a quantized version and benchmarking it on mobile, DSP, MCU, or hearing-aid-class processors will be investigated in future work."；并明确说"quantizing the spiking and Mamba-based operators while preserving stable enhancement performance remains nontrivial"。
- **266 MB 峰值内存是 FP32 且不代表最终部署**："does not directly represent the memory requirement of a final hearing-aid deployment."
- **未来工作**：在真实硬件（含 neuromorphic 器件）上验证功耗与延迟；扩展到**多通道**与更复杂声学环境。
- 致谢基金：JSPS KAKENHI 23H00493、25H00566。数据可用性声明为 "Data will be made available on request"，**未给出代码或预训练模型链接**。

**读出来的隐藏问题（本 wiki 视角）**：

- **30 ms 算法延迟 vs 约 2 ms 目标 = 15× 差距**。即使论文把 30 ms 说成"low-latency"，它在本 wiki 的硬约束下是不合格系统，只能作为"极低 MACs"方向的参照。
- **Mamba 状态不跨帧传递，与"长程建模"叙事冲突**（见下方 `[!contradiction]`）。这同时削弱了 §4.3 第 5 条对 Mamba 的辩护。
- **帧间无状态 + 50% OLA 是唯一的连续性机制**：这带来两个未报告的风险——(a) 长流下相邻帧输出可能不一致，产生帧率相关的调制/闪烁伪影；(b) 没有 warm-up/flush 语义，起始与结束帧的行为未描述。
- **没有严格意义上的 p99 / deadline 证据**：全文唯一的耗时证据是 Fig. 14 的 RTF 趋势曲线，没有 p50/p95/p99、没有 deadline miss、没有 underrun/overrun、没有 per-hop wall-clock。
- **没有功耗测量**。论文用 MACs 下降推断"能耗低"，但 SNN 的能耗优势只有在 event-driven 硬件上才成立；在 RTX 3090 上跑 SNN 的密集张量运算并不省电。
- **低 SNR 人声保留未系统评估**：没有 false-suppression、SPP/VAD 校准、F0/formant/prosody continuity、voiced energy retention；Table 5 显示 −5 dB babble 下 STOI 只有 63.8%，但论文没有分析这是"残留噪声"还是"语音被误伤"。图 8 的频谱对比只给了定性描述（DPCRN 过抑制、PSMSE 平衡），没有定量。
- **个性化模块的证据很薄**：Table 7 中 PSMSE(0.90/0.60) 对 DeepFilterNet+HLC(0.89/0.56) 的 HASPI 优势只有 0.01；且个性化实验的因果性/延迟口径（30 ms 帧下 audiogram 每帧 concat）与主模型一致，但**没有报告个性化模块带来的参数量/MACs 增量**。
- **单通道**：论文明确把多通道列为 future work，因此双耳/阵列收益完全未验证。

> [!contradiction] "strictly causal" 与 "Mamba states are re-initialized on each call" 的张力
> 原文（p.6, §4.3）："During inference, the input is processed causally using 30-ms frame chunks with 50% overlapping. **Explicit Mamba state caching is not used, so the Mamba states are re-initialized on each call and not propagated across consecutive frames.**"
> 原文（p.18, §6.7）："Since the proposed model is **strictly causal** and does not use future frames, the convolutional lookahead is 0 ms."
> 这两句合起来意味着 PSMSE 的"因果"是**逐帧无状态因果**：
> - 它确实不读未来样本 → 在"不读取未来观测"这一条上成立；
> - 但 Mamba 的 $\mathbf h_t=\overline{\mathbf A}\mathbf h_{t-1}+\overline{\mathbf B}\mathbf x_t$ 递归**在帧边界处被人为截断并重置**，所以跨帧的长流状态记忆为零；
> - 论文 §3.1 用 SSM 的连续时间动力学 + selection mechanism 论证"长程序列建模"，§4.3 又取消了跨帧状态——**"长程"实际只发生在单帧内部（约 47 个时间步）**；
> - 因此"streaming inference"在这里的准确含义是「以 30 ms 为单位重复调用一个无状态映射，再用 50% overlap-add 把结果拼回去」，而不是「一个带持久状态的长流增强器」。
> 后果（论文未讨论）：长流一致性、帧边界不连续、state reset 语义，以及本页 §4.3 第 5 条"w/o Mamba 只掉 0.05 PESQ"这一看似矛盾的结果，都指向同一个解释——**Mamba 在当前配置下并未承担真正的跨帧长程建模**。
> 该 caveat 应作为阅读本篇任何"streaming / long-range / causal"表述时的前置条件。

## 6. 本论文在库中的位置关联（cross-reference matrix）

| 关系 | 库中论文/概念 | 关联与差异 |
|---|---|---|
| **同分支竞品（最直接）** | [[wiki_low_latency/sources/2026/RT-SEMamba 2026]]、[[wiki_low_latency/entities/RT-SEMamba]] | 两者都是"Mamba + 流式低时延"，但路线几乎相反：RT-SEMamba 走**时频域 + 固定 recurrent SSM state 跨帧传播 + 渐进式 KD**（25 ms 窗、1.05 M 参数、20.56 G/s MACs）；PSMSE 走**时域波形 + 帧间无状态 + SNN 稀疏化**（30 ms 帧、0.26 M 参数、0.11 G/s MACs）。按各自论文报告值，PSMSE 相对 RT-SEMamba 1-layer student 参数少约 4×（0.26 M vs 1.05 M）、MACs 少约 187×（0.11 vs 20.56 G/s，**两者 MACs 统计口径与实现未必一致，仅作量级对照**），代价是延迟口径从 25 ms 变 30 ms 且丢掉了跨帧状态。这是本库里"状态传递 vs 稀疏性"两条省算力路线的正面对照。 |
| 概念延伸 | [[wiki_low_latency/concepts/2608.12099-mamba-distillation]] | 该页展开的是 fixed-state + 蒸馏；本篇提供了**反例**：不做 state caching 也能"流式"，但代价是长程记忆为零。两页并读可得到"Mamba 流式"的两种合法语义。 |
| 同类低 MAC 状态空间 | [[wiki_low_latency/sources/2024/SlowFast-SSM 2024]]、[[wiki_low_latency/concepts/2411.02019-slowfast-ssm]] | SlowFast-SSM 用**多速率复用**降 MAC（慢支路输出跨多个 fast frame 复用，属 stale context 而非未来帧）；PSMSE 用**脉冲稀疏性**降 MAC。两条省算力思路互补，且都强调"不读未来"。 |
| 低复杂度全带建模 | [[wiki_low_latency/sources/2023/FSB-LSTM 2023]]、[[wiki_low_latency/concepts/2304.08707-full-sub-band-modeling]] | FSB-LSTM 通过 full-band/sub-band 集成压低复杂度；PSMSE 通过 spike 稀疏性。两者都在"极低 MACs"象限，可放进同一张复杂度–质量 Pareto。 |
| 低时延前端账本 | [[wiki_low_latency/sources/2022/STFT-Domain Very Low Algorithmic Latency 2022]]、[[wiki_low_latency/concepts/2204.09911-short-asymmetric-stft]] | 该路线用短窗/非对称 STFT 把算法延迟压到个位数 ms；PSMSE 走时域波形、帧长即延迟（30 ms）。**本库约 2 ms 目标下，短窗 STFT 路线目前比 PSMSE 更接近约束。** |
| 因果波形域先驱 | [[wiki_low_latency/sources/2021/On TasNet Low-Latency SE 2021]]、[[wiki_low_latency/entities/On-TasNet]]、[[wiki_low_latency/concepts/2103.14882-causal-tasnet]] | PSMSE 的 encoder(Conv1D)–bottleneck–decoder(ConvTranspose1D) 骨架与 learned-filterbank 时域掩蔽一脉相承，只是把 separator 换成并行 SMC/SMR。可作为"TasNet 骨架 + SNN/SSM"的现代变体来读。 |
| 嵌入式低复杂度参照 | [[wiki_low_latency/sources/2022/DeepFilterNet2 2022]]、[[wiki_low_latency/entities/DeepFilterNet2]]、[[wiki_low_latency/concepts/2205.05474-deep-filtering]] | DeepFilterNet2 是"端侧全带实时"的强参照，也是本篇 Table 2/5/6/7 的直接基线；PSMSE 在 Table 2 用 0.26 M/0.11 G/s 对 1.78 M/0.35 G/s。但 DeepFilterNet2 有嵌入式实测，PSMSE 没有。 |
| 感知/助听器目标 | [[wiki_low_latency/sources/2020/PercepNet Low-Latency Direction 2020]]、[[wiki_low_latency/entities/PercepNet]]、[[wiki_low_latency/concepts/2008.04259-perceptual-speech-preservation]] | PercepNet 用感知动机（谐波/包络/梳状滤波）保人声；PSMSE 用 HASPI/HASQI + NAL-R/WDRC 对齐助听器目标。两者都把"人声可懂度"当一等目标，但 PSMSE 未做 false-suppression 类分析。 |
| 助听器/双耳链路 | [[wiki_low_latency/sources/2023/GCFSnet 2023]]、[[wiki_low_latency/entities/GCFSnet]]、[[wiki_low_latency/concepts/低比特率双耳特征链路]] | GCFSnet 面向双耳助听器链路（多通道 + 量化感知部署）；PSMSE 是**单通道**且未量化。两者可组合成"多通道 + 超低 MAC"的假设，但 PSMSE 明确把多通道留作 future work。 |
| 复数/相位路线对照 | [[wiki_low_latency/sources/2020/DCCRN Low-Latency Direction 2020]]、[[wiki_low_latency/concepts/2008.00264-complex-phase-enhancement]]、[[wiki_low_latency/sources/2021/DPCRN Low-Latency Direction 2021]]、[[wiki_low_latency/concepts/2107.05429-dual-path-recurrent-context]] | DCCRN/DPCRN 是时频复数域 + 循环长上下文，也是本篇 Table 2/4/5/6 的基线；PSMSE 的时域门控（Conv1D+Sigmoid 乘 Skip Connection）在功能上替代了 mask，但完全绕开了相位问题。 |
| 人声保留缺口 | [[wiki_low_latency/concepts/低 SNR 人声保留评估]]、[[wiki_low_latency/concepts/2111.11606-speech-distortion-losses]]、[[wiki_low_latency/entities/Noise-Suppression-Losses]] | PSMSE 只有 PESQ/STOI/CSIG/CBAK/COVL + HASPI/HASQI，**没有** false-suppression、SPP/VAD 校准、F0/formant continuity、DNSMOS 分层或 ASR WER 分层；Table 5 的 −5 dB babble 结果（STOI 63.8%）正需要这类分析。 |
| 过抑制/连续性 | [[wiki_low_latency/concepts/2203.16843-continuity-loss]]、[[wiki_low_latency/entities/Hybrid-Continuity-Loss]] | 由于帧间无状态、仅靠 50% OLA 拼接，PSMSE 在长流下**天然缺少连续性约束**；本篇的稀疏 L1 正则管的是脉冲发放，不是输出连续性。这是可直接迁移的实验缺口。 |
| 延迟审计框架 | [[wiki_low_latency/concepts/严格因果与算法延迟]]、[[wiki_low_latency/concepts/低时延前端与延迟账本]]、[[wiki_low_latency/sources/2024/Ultra-Low Latency Speech Enhancement Comprehensive Study 2024]]、[[wiki_low_latency/concepts/2409.10358-ultra-low-latency-benchmark]] | 用统一账本记录 PSMSE：帧长 30 ms / hop ≈15 ms / look-ahead 0（论文声称）/ 帧间无状态 / 0.11 G/s / 266 MB FP32 / 端到端未验证。 |
| 蒸馏子群参照 | [[wiki_low_latency/concepts/nakaoka21-wave-unet-distillation]]、[[wiki_low_latency/concepts/2309.08144-two-step-distillation]] | PSMSE **不用蒸馏**，而是靠架构替换（ANN→SNN）和稀疏化压 MACs。与本库"蒸馏子群"是**互补的两条轻量化路径**；若两者结合（先稀疏化再蒸馏），是库里尚未出现的组合。 |
| SSM 背景 | [[wiki_array/concepts/Mamba SSM 状态空间模型]] | Eq. (3)–(8) 的连续/离散 SSM 推导可直接复用该概念页。 |
| 原文引用但库中暂无页面 | SpikingS4 [21]、DPSNN [22]、Spiking-FullSubNet [20]、Mamba-SEUNet [23]、GTCRN [16]、LiSenNet [17]、UL-UNAS [18]、FSPEN [15]、CleanUNet2 [14]、aTENNUate [58]、L-DPSB [59]、HiFi-Stream [60] | ⚠️ 疑似关联，需用户确认是否要为 SNN-SE 分支（SpikingS4 / DPSNN / Spiking-FullSubNet）或超轻量分支（GTCRN / LiSenNet / UL-UNAS）建独立页面。**2026-09-27 更新**：GTCRN（第 8 批）与 **LiSenNet（第 10 批）已完成补摄**（见 [[wiki_low_latency/entities/GTCRN]]、[[wiki_low_latency/entities/LiSenNet]]）；**FSPEN [15] 仍缺页**——IEEE 付费墙 + 无 arXiv，需用户提供 PDF；**UL-UNAS [18]、CleanUNet2 [14]、aTENNUate [58]、L-DPSB [59]、HiFi-Stream [60] 及三条 SNN 分支**库中仍无页面 |

## 7. 一句话总结"江湖地位"

> **2026 | 严格因果流式语音增强 | 把 SNN 的事件驱动稀疏性和 Mamba 的近线性长程建模塞进一个"并行 SMC/SMR"架构，做到 0.26 M 参数 + 0.11 G/s MACs 并在流式 VB-DEMAND 拿到 PESQ 2.73，是目前本库中 MACs 与参数量最低的模型 → 但它的"流式"靠的是 30 ms 帧间无状态 + 50% OLA，算法延迟 30 ms（约为本 wiki 目标的 15×），且无任何真实助听器硬件、量化后精度与功耗证据；它是"极低 MACs 方向"的新标杆，不是"约 2 ms 严格因果"的合格系统。**

## 参考资料

- [DOI: 10.1016/j.iot.2026.102046](https://doi.org/10.1016/j.iot.2026.102046)（Internet of Things, 39 (2026) 102046，开放获取 CC BY）
- 本地原件：raw/papers/low_latency_causal_se/1-s2.0-S2542660526001769-main.pdf（21 页）
- 文本抽取：tmp/pdf_extract/S2542660526001769.txt
- 页面渲染：wiki_low_latency/assets/S2542660526001769/（S2542660526001769-page1.png ~ -page21.png；本页嵌入了 p.5 / p.6 / p.10 / p.11 / p.18 / p.19 的重命名副本）
- 论文声称的开源/数据：无代码仓库或预训练模型链接；"Data will be made available on request."
