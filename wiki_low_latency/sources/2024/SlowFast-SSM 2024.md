---
title: SlowFast-SSM — 双速分支与状态转移调制的超低时延语音增强
type: source
created: 2026-09-16
updated: 2026-09-16
tags:
  - speech-enhancement
  - paper-claimed-causal
  - strict-causal-audit
  - ultra-low-latency
  - state-space-model
  - slow-fast
  - compute-efficient
source_type: paper
year: 2024
publication_year: 2025
authors: Longbiao Cheng, Ashutosh Pandey, Buye Xu, Tobi Delbruck, Vamsi Krishna Ithapu, Shih-Chii Liu
venue: arXiv preprint (eess.AS)
arxiv: https://arxiv.org/abs/2411.02019
local_pdf: raw/papers/low_latency_causal_se/2411.02019.pdf
related:
  - [[wiki_low_latency/entities/SlowFast-SSM]]
  - [[wiki_low_latency/concepts/2411.02019-slowfast-ssm]]
  - [[wiki_low_latency/index]]
  - [[wiki_low_latency/overview]]
  - [[wiki/sources/2021/DPCRN 2021]]
  - [[wiki/sources/2023/DeepFilterNet 2023]]
  - [[wiki/entities/RNNoise]]
  - [[wiki_low_latency/sources/2023/FSB-LSTM 2023]]
  - [[wiki_low_latency/sources/2023/GCFSnet 2023]]
  - [[wiki_low_latency/concepts/2409.10358-ultra-low-latency-benchmark]]
  - [[wiki_low_latency/entities/RT-SEMamba]]
---

~~~yaml
- 论文: [Modulating State Space Model with SlowFast Framework for Compute-Efficient Ultra Low-Latency Speech Enhancement](2024/2025)
  ├── 要解决什么问题: 2 ms 甚至单采样算法延迟会让传统单分支增强器每秒处理十倍甚至更多帧，计算量难以落到端侧
  ├── 核心方法: 低帧率、较重的 Slow 分支分析声学环境；高帧率、轻量的 Fast 分支完成时域增强；Slow 分支调制 Fast 分支的 SSM 状态转移
  ├── 属于哪个分支: 严格低时延 / 时域语音增强 / SSM / 多速率计算复用 / 端侧计算效率
  ├── 输入/输出: 因果时域 noisy speech frames → SlowFast-SSMM → fast enhanced frames → overlap-and-add 语音
  ├── 关键trick: 让慢分支的环境表征跨多个 fast frames 复用，用它生成对角状态转移矩阵和输入门控向量
  ├── 数据集: VoiceBank + DEMAND；28/30 说话人训练，2/30 测试；16 kHz；训练/测试噪声与 SNR 见正文
  ├── 对比了谁: Single-Branch、SlowFast-EC、SlowFast-FiLM、SlowFast-SSMM、RNNoise、DeepFiltering、ULCNetFreq
  ├── 性能上限: 2 ms/δ=1 的 SSMM 为 110 M MAC/s、PESQ-NB/WB=3.30±0.02/2.66±0.02、SI-SNR=18.15±0.02；单采样 62.5 μs/δ=16 为 105 M MAC/s、PESQ-NB/WB=3.12±0.02/2.41±0.03、SI-SNR=16.62±0.08
  ├── 参数量: 论文未给出统一总参数量；2 ms 实验 H=32，单采样实验 H=8；Slow 分支为 1 FC + 4×64-unit GRU + 1 FC
  ├── 消融关键发现: SSMM 比 EC/FiLM 对 reuse factor δ 更鲁棒；δ=3 时 39 M MAC/s 仍基本保持 126 M MAC/s 单分支的增强质量
  ├── 遗留问题(你的机会): 2 ms/62.5 μs 是算法延迟而非端到端 p99；没有目标 SoC deadline、真实远端 Slow 分支链路、丢包抖动、负 SNR 人声保留或听感诊断
  └── 跟哪篇像: [[wiki_low_latency/sources/2022/STFT-Domain Very Low Algorithmic Latency 2022]]、[[wiki_low_latency/sources/2022/DeepFilterNet2 2022]]、[[wiki_low_latency/sources/2020/DCCRN Low-Latency Direction 2020]]、[[wiki_low_latency/concepts/2204.09911-short-asymmetric-stft]]
~~~

# Modulating State Space Model with SlowFast Framework for Compute-Efficient Ultra Low-Latency Speech Enhancement

> Longbiao Cheng, Ashutosh Pandey, Buye Xu, Tobi Delbruck, Vamsi Krishna Ithapu, Shih-Chii Liu。arXiv:2411.02019（v2，2025-01-04）。本地 PDF 未报告正式会议录信息，因此不把 venue 外推为 ICASSP。  
> 本页是 14 篇原件中按新方向摄取的 2411.02019；重点审计超低算法延迟、计算复用和人声质量，不把 2 ms 算法延迟写成端到端延迟。

> [!warning] PDF 转换质量与阅读说明
> 原 PDF 5 页。页面渲染清晰；PDF 文本抽取对 δ、ε、μ、矩阵乘法符号和 Figure 1/2 的标签有缺失或错位。下文的公式、Figure 1、Table I/II 数字已通过页面视觉核对；图中细小符号应以嵌入的原页面渲染图和原 PDF 为准。

## 1. 他们为什么这么做？（motivation）

### 1.1 任务背景

本文研究低算法延迟的单通道时域语音增强：输入是实时到来的 noisy speech，输出是经重叠相加的 enhanced speech。目标场景包括助听器、通信设备和沉浸式 VR；这些场景对 processed speech 的等待时间敏感。

论文抓住了一个容易被忽略的计算事实：当算法延迟从 20 ms 压到 2 ms 时，短 hop 会让每秒需要处理的帧数约增加 10 倍。相邻帧虽然更相似、信息冗余更高，传统单分支网络仍然在每个输入帧上完整执行一次，因此计算量随着低延迟要求一起上升。

### 1.2 论文目标

作者希望在不牺牲增强质量的前提下：

1. 让高频率的实时路径足够轻，匹配 2 ms 算法延迟；
2. 让较重的声学环境分析只低频更新，并跨多个 fast frames 复用；
3. 进一步把同一框架推到单采样级算法延迟，即 16 kHz 下一个样本约 62.5 μs。

本文的目标不是证明某一目标芯片的 capture-to-playback deadline，而是提出一种把“低延迟所需的高帧率”和“环境建模所需的较大上下文”拆开的网络计算组织方式。

## 2. 之前的人怎么做不了？（limitation → gap）

### 2.1 既有低延迟路线的缺口

| 路线 | 能力 | 不能直接满足本题的地方 |
|---|---|---|
| 因果网络 | 减少 look-ahead，能够在线运行 | 仍可能在每个短 hop 上执行完整网络，低延迟时计算量快速上涨 |
| 对称/非对称窗 STFT | 可在质量与算法延迟之间调节 | 更短 hop 带来更多帧；较大分析窗与小合成窗的实现/边界证据需要单独审计 |
| 单分支时域增强器 | 输入输出直接、易于流式化 | 单分支每个 fast frame 都重复计算相似的声学环境表征 |
| 直接使用重型长上下文模型 | 可能保留更多语音/噪声信息 | 在 2 ms 或单采样预算下，重复计算无法接受 |

因此 gap 不是“有没有一个更强的增强 backbone”，而是：**能否让重型环境分析低频运行，让轻型增强状态高频推进，并把两者的接口设计成严格因果、可计算复用的形式。**

### 2.2 严格因果与延迟审计

| 项目 | 论文给出的信息 | 本 Wiki 判定 |
|---|---|---|
| fast branch 的因果性 | Figure 1 和正文要求 Slow 表征 εⱼˢ 不使用当前 fast branch 输入；SSM 状态从前一状态推进到当前输入 | 设计级 strict-causal 证据支持；未提供逐层 certificate |
| 2 ms 配置 | L_F=32 samples、Δ_F=16 samples，16 kHz；输出增强帧长度决定算法延迟 | 32/16 kHz = 2 ms 算法帧；Δ_F=1 ms 是更新 hop，不是额外 look-ahead |
| 单采样配置 | L_F=1、Δ_F=1，16 kHz | 1 sample = 62.5 μs 算法帧口径；不等于端到端播放延迟 |
| slow branch 更新 | Δ_S=δΔ_F；每 δ 个 fast frames 复用同一个 εⱼˢ | 复用的是过去/当前已可用的慢表征；stale context 不等于 future look-ahead |
| OLA | enhanced fast frames 通过 overlap-and-add 得到最终语音 | OLA 边界、缓冲和输出调度未给出可执行的端到端 deadline 证据 |
| 计算量 | 2 ms 的 SSMM δ=3 为 39 M MAC/s；单采样 SSMM 为 105 M MAC/s | 论文级 MAC 预算；没有目标 SoC 实测、p99、SRAM/DMA/音频 I/O 数据 |

> [!question] 关键边界
> 本文可以标为“论文级因果、2 ms 算法帧、单采样算法延迟实验”，但不能无条件标为“端到端严格 2 ms 已验证”。尤其是实际设备 buffer、调度抖动、模型状态 reset、OLA 输出时序和长流稳定性没有被完整测量。

## 3. 这个做法核心 trick 是什么？

### 3.1 Trick A：Slow 分支只低频分析，Fast 分支高频输出

令 fast branch 输入帧序列为

$$
x^F=[x_0^F,\ldots,x_i^F],
$$

令 slow branch 输入帧序列为

$$
x^S=[x_0^S,\ldots,x_j^S].
$$

其中 i、j 分别是 fast/slow 帧索引，N_F、N_S 是两条支路的输入帧数。SlowFast 的两步流程写成：

$$
\epsilon^S=f_{\mathrm{Slow}}(x^S), \tag{1}
$$

$$
\hat{s}=f_{\mathrm{Fast}}(x^F;\epsilon^S). \tag{2}
$$

- ε^S：Slow 分支对噪声与语音声学环境的表征；
- f_Slow：低帧率、相对较重的环境分析函数；
- f_Fast：高帧率、轻量的增强函数；
- \hat{s}：fast branch 输出的增强帧序列，最终经 OLA 合成。

fast branch 使用较短的窗口 L_F 和 hop Δ_F，以满足目标算法延迟；slow branch 使用更大的窗口 L_S 和 hop Δ_S，其中 L_S>L_F、Δ_S>Δ_F。定义 reuse factor：

$$
\delta=\Delta_S//\Delta_F.
$$

同一个 εⱼˢ 被连续 δ 个 fast frames 复用；论文为保持因果性，明确要求 εⱼˢ 不使用当前 fast branch 的输入。这样，slow branch 获得 δ 倍的计算时间，也只需低频运行。

### 3.2 论文原图：双速处理、分帧与 SSM 调制

![[wiki_low_latency/assets/2411.02019/2411.02019-page2-fig1-slowfast-ssmm.png]]

图 1 的关键不是简单地并联两个增强器，而是把“较重的慢速声学分析”和“较轻的快速逐帧增强”放到不同频率上。右侧 SSMM 图把 slow 表征送入 fast SSM 的状态转移和输入门控。

### 3.3 Trick B：用 SSMM 调制 Fast SSM 的状态转移

fast branch 被抽象成一个由 slow branch 动态调制的状态空间模型。论文给出的状态方程和输出方程为：

$$
h_i^F=A_j^S h_{i-1}^F+g_j^S\odot F_{\mathrm{IN}}(x_i^F), \tag{3}
$$

$$
\hat{s}_i=F_{\mathrm{OUT}}(h_i^F). \tag{4}
$$

符号含义：

- h_i^F∈R^H：fast branch 在第 i 个输入帧的隐藏状态，H 是状态维度；
- A_j^S∈R^{H×H}：由第 j 个 slow 表征生成的状态转移矩阵，表达当前声学环境下的状态演化；
- g_j^S∈R^H：输入门控向量，按 slow branch 感知的噪声特性调节 noisy input 的注入；
- F_IN：把时域 noisy frame 映射到 hidden space；
- F_OUT：把 hidden representation 映射回时域增强帧；
- ⊙：逐元素乘法；A_j^S 与 h_{i-1}^F 的乘法是矩阵-向量乘法。

为了降低参数空间，作者把 A_j^S 简化为对角矩阵；F_IN 和 F_OUT 都只使用一个 FC 层。slow branch 通过一个 FC 层生成 [A_j^S,g_j^S]，其元素数量为 2H，因此调制本身的额外开销较小。

### 3.4 Trick C：把慢分支当作可复用的“环境侧信息”

论文还比较了两种替代接口：

| 集成方式 | slow 输出如何进入 fast branch | 解释 |
|---|---|---|
| Embedding Concatenation（EC） | 直接把 εⱼˢ 作为额外 feature 拼接 | 接口直接，但 fast branch 输入维度和计算会增加 |
| Feature-wise Linear Modulation（FiLM） | 由 slow branch 产生 scale/shift 向量 | 对 fast features 做线性调制 |
| SSMM（本文） | slow branch 产生 A_j^S 和 g_j^S，直接调制 SSM 状态推进 | 把慢分支的环境信息放入状态动力学，而非只拼到输入 |

### 3.5 训练损失

所有网络使用：

$$
\mathcal{L}=\lambda_1\mathcal{L}_{\mathrm{SpecMSE}}
+\lambda_2\mathcal{L}_{\mathrm{SISNR}}
+\lambda_3\mathcal{L}_{\mathrm{PESQ}}
+\lambda_4\mathcal{L}_{\mathrm{STOI}}. \tag{5}
$$

- L_SpecMSE：增强语音与目标语音频谱的幅度、实部和虚部之间的均方误差；
- L_SISNR：增强语音与目标语音之间的负 SI-SNR；
- L_PESQ、L_STOI：感知质量与可懂度相关的损失；
- λ₁…λ₄：各项损失的平衡权重。

训练前 200 epochs 只使用 L_SpecMSE；从第 201 个 epoch 起加入完整损失，权重设置为 [λ₁,λ₂,λ₃,λ₄]=[10,0.5,1,5]。

## 4. 实验里哪个消融最关键？

### 4.1 数据与训练设置

| 项目 | 设置 |
|---|---|
| 数据集 | VoiceBank + DEMAND（VBD） |
| 说话人 | 30 人中 28 人训练、2 人测试 |
| 训练噪声/SNR | DEMAND 10 类噪声；SNR 0、5、10、15 dB |
| 测试噪声/SNR | 5 类训练未见噪声；SNR 2.5、7.5、12.5、17.5 dB |
| 采样率 | 16 kHz |
| 2 ms 配置 | L_F=32，Δ_F=16，δ∈{1,2,3,4,5,10}，L_S=2Δ_S，H=32 |
| 单采样配置 | L_F=1，Δ_F=1，Δ_S=16，L_S=32，H=8 |
| Slow branch | 1 FC + 4 个 64-unit GRU + 1 FC |
| 训练 | 230 epochs，batch size 16；每个网络 5 个随机种子 |
| 学习率 | 前 200 epochs 从 1e-3 起，连续两 epochs 不下降时降 10%；后续重置 1e-4，单 epoch 不下降时降 25% |

评价指标包括 PESQ-NB/WB（感知质量）、STOI/ESTOI（可懂度）、HASPI（听障相关可懂度）和 SI-SNR（信噪比改善）；所有指标越高越好。

### 4.2 主结果：δ=3 基本保持质量并显著降算

下表整理 Table I 中的单分支基线和 SSMM 主线。数值为论文报告的均值±标准差；MACs 为 M MAC/s。

| ID/配置 | δ | MACs | PESQ-NB | PESQ-WB | STOI (%) | ESTOI (%) | HASPI (%) | SI-SNR |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Single-Branch | — | 126 | 3.25±0.01 | 2.59±0.03 | 93.14±0.06 | 82.56±0.10 | 98.85±0.12 | 17.79±0.12 |
| SlowFast-SSMM | 1 | 110 | 3.30±0.02 | 2.66±0.02 | 93.38±0.08 | 83.42±0.18 | 99.10±0.07 | 18.15±0.02 |
| SlowFast-SSMM | 2 | 57 | 3.26±0.02 | 2.61±0.02 | 93.18±0.05 | 82.89±0.06 | 98.96±0.07 | 17.89±0.09 |
| SlowFast-SSMM | 3 | 39 | 3.24±0.01 | 2.59±0.02 | 93.10±0.07 | 82.78±0.12 | 98.86±0.03 | 17.86±0.05 |
| SlowFast-SSMM | 4 | 31 | 3.19±0.01 | 2.53±0.01 | 92.90±0.07 | 82.38±0.14 | 98.76±0.05 | 17.74±0.04 |
| SlowFast-SSMM | 5 | 25 | 3.18±0.01 | 2.52±0.02 | 92.75±0.05 | 82.06±0.14 | 98.63±0.02 | 17.66±0.03 |
| SlowFast-SSMM | 10 | 15 | 3.10±0.01 | 2.39±0.01 | 92.36±0.09 | 81.14±0.16 | 98.62±0.12 | 17.08±0.03 |
| Single-Branch（ID 7） | — | 45 | 3.09±0.02 | 2.39±0.03 | 92.72±0.09 | 81.37±0.28 | 97.97±0.08 | 16.91±0.15 |

作者特别比较 ID 0 与 δ=3 的 ID 3.C：39 M MAC/s 相比 126 M MAC/s 约减少 70%，但 PESQ-WB、STOI、HASPI 和 SI-SNR 基本保持。δ=10 可以进一步降到 15 M MAC/s，但质量下降更加明显。

### 4.3 原论文结果图：复用因子和单采样约束

![[wiki_low_latency/assets/2411.02019/2411.02019-page4-table1-table2.png]]

Table II 的单采样实验为：

| 方法 | δ | MACs (M/s) | PESQ-NB | PESQ-WB | STOI (%) | ESTOI (%) | HASPI (%) | SI-SNR |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Noisy | — | — | 2.87 | 1.97 | 92.10 | 78.66 | 97.12 | 8.45 |
| SlowFast-SSMM | 16 | 105 | 3.12±0.02 | 2.41±0.03 | 92.57±0.05 | 81.32±0.17 | 97.80±0.04 | 16.62±0.08 |

论文称该配置实现了单采样级算法延迟；但 105 M MAC/s 仍需要目标设备上的实际 deadline、功耗、内存和 p99 测量才能转化为可部署结论。

### 4.4 最关键消融：EC/FiLM/SSMM 与 reuse factor

在相同的 2 ms 算法延迟设定下，作者比较 EC、FiLM 和 SSMM 三种 slow-fast 接口。关键观察是：

- EC 对 δ 最敏感：从 δ=1 增加到 δ=2 时 PESQ-WB 从 2.45 降到 2.07；
- FiLM 比 EC 稳定，但随着慢表征变旧仍有退化；
- SSMM 在 δ≤3 时只出现轻微退化，并在所有 δ 组整体优于 EC/FiLM；
- 这支持了本文的核心判断：低频环境信息最好调制状态动力学，而不是简单追加到每个 fast frame 的输入。

Table I 中 δ=3 的接口对照如下：

| 方法 | MACs (M/s) | PESQ-NB | PESQ-WB | STOI (%) | ESTOI (%) | HASPI (%) | SI-SNR |
|---|---:|---:|---:|---:|---:|---:|---:|
| SlowFast-EC | 39 | 2.77±0.01 | 2.07±0.01 | 92.01±0.02 | 79.39±0.06 | 96.74±0.09 | 15.69±0.08 |
| SlowFast-FiLM | 39 | 3.15±0.02 | 2.45±0.02 | 92.92±0.03 | 82.20±0.07 | 98.46±0.09 | 17.64±0.02 |
| SlowFast-SSMM | 39 | **3.24±0.01** | **2.59±0.02** | **93.10±0.07** | **82.78±0.12** | **98.86±0.03** | **17.86±0.05** |

### 4.5 与其他实时系统的可比性边界

Table I 还列出 RNNoise（40 M MAC/s，PESQ-WB 2.43，20 ms 算法延迟）、DeepFiltering（233 M MAC/s，PESQ-WB 2.65，8 ms/未统一延迟口径）和 ULCNetFreq（98 M MAC/s，PESQ-WB 2.54，8 ms 算法延迟）。这些行来自不同论文、延迟和评测设置，适合做量级参照，不应当作严格同条件排名。

## 5. 这个方向还剩什么问题没解决？（future work / limitation）

### 5.1 论文明确提出的 future work

论文结尾提出将 SlowFast 应用于需要更严格算法延迟的音频信号处理任务，例如 Active Noise Control（ANC）。

### 5.2 读出来的隐藏问题

1. **算法延迟不等于端到端延迟。** 2 ms 和 62.5 μs 由输出帧长度定义；ADC/DMA、设备 buffer、网络调度、OLA、DAC、OS jitter 和模型 p99 均未测量。
2. **没有真实硬件 deadline。** 论文给出 MAC/s，但没有目标 SoC 的 batch=1 实测、SRAM 峰值、功耗、热约束、最坏帧耗时或长时间运行稳定性。
3. **Slow branch 远程部署仍是可能性。** 作者指出 slow branch 有 δ 倍处理时间，并可考虑放到 remote device；但没有真实链路、时间戳、丢包、抖动或状态同步实验。
4. **人声保留指标仍偏间接。** PESQ、STOI、ESTOI、HASPI 和 SI-SNR 没有直接报告弱辅音、气声、F0/谐波、音节边缘或 false-suppression；测试 SNR 最低为 2.5 dB，也没有负 SNR 人声保留结果。
5. **数据规模和泛化有限。** 实验集中在 VoiceBank + DEMAND；没有真实会议/车载/助听器噪声、真实房间变化、说话人重叠场景或真实听感研究。
6. **SSM 工程证据不完整。** 对角状态转移有利于压缩，但选择性状态更新、定点量化、状态 reset、异常输入和长流数值稳定性未被系统分析。

### 5.3 对当前课题的可迁移机会

- 用 SlowFast 的 reuse factor 做“质量—MAC—延迟”三维 Pareto，而不是只报告平均 PESQ；
- 在低 SNR、弱辅音和连续语音上加入 speech-preservation scorecard，包括 DNSMOS SIG/BAK/OVL、误抑制率、ASR WER、F0/共振峰和语音活动边界；
- 让 slow context 带时间戳进入丢包/抖动仿真，区分 stale context 与 look-ahead；
- 在目标 SoC 上报告 p50/p95/p99 帧耗时、峰值 SRAM、功耗和状态恢复。

## 6. 本论文在库中的位置关联（cross-reference matrix）

| 关系 | 库中论文/概念 | 关联与差异 |
|---|---|---|
| 前身/基石 | [[wiki_low_latency/concepts/2204.09911-short-asymmetric-stft]] | 短窗/低算法延迟解决前端时延；SlowFast 进一步把重计算从 fast path 中抽离 |
| 同分支竞品 | [[wiki_low_latency/sources/2023/FSB-LSTM 2023]] | FSB-LSTM 通过 full-/sub-band 建模降低低延迟复杂度；SlowFast 通过多速率复用和 SSM 调制降低重复计算 |
| 同分支竞品 | [[wiki_low_latency/sources/2023/GCFSnet 2023]] | GCFSnet 用本侧当前多麦信号和延迟跨耳特征守住约 2 ms 过滤框架；SlowFast-SSM 是时域单通道多速率计算，二者优化对象不同，数字不可直接横比 |
| 同分支竞品 | [[wiki_low_latency/sources/2021/On TasNet Low-Latency SE 2021]] | On TasNet 直接研究因果时域编码器的低延迟；SlowFast 更强调跨帧的环境表征复用 |
| 时频/相位参照 | [[wiki_low_latency/sources/2020/DCCRN Low-Latency Direction 2020]] | DCCRN 擅长复数谱/相位建模，但原始前端并非 2 ms；SlowFast 的优势是单采样/2 ms 计算组织 |
| 端侧参照 | [[wiki_low_latency/sources/2022/DeepFilterNet2 2022]] | DeepFilterNet2 体现低复杂度深滤波与实时工程；两者均需进一步区分 RTF 与 deadline |
| 人声保留参照 | [[wiki_low_latency/sources/2020/PercepNet Low-Latency Direction 2020]] | PercepNet 用 pitch/包络等显式感知路径保护语音；SlowFast 当前主要依赖客观指标和多任务损失 |
| 极低复杂度参照 | [[wiki/entities/RNNoise]] | RNNoise 的 DSP + 小网络哲学与轻量 Fast path 相近；SlowFast 的核心新增是 slow context 调制状态 |
| 结构类比 | [[wiki_low_latency/entities/RT-SEMamba]] | 两者都关注固定状态和低时延计算；SlowFast 以多速率复用控制重复计算，RT-SEMamba 以蒸馏和 Mamba 深度压缩 |
| 延迟审计概念 | [[wiki_low_latency/concepts/2409.10358-ultra-low-latency-benchmark]] | 2409.10358 说明小窗会推高 MAC/s，并强调需分离算法延迟、计算延迟和端到端证据；与本文互为验证 |

> [!question] 关联不确定性
> 文献中的 RNNoise、DeepFiltering 和 ULCNetFreq 行来自不同训练数据、指标实现和算法延迟口径；本页只把它们当作量级参照。SlowFast 与 RT-SEMamba 的关系是结构类比，不是直接后续工作。

## 7. 一句话总结“江湖地位”

> **SlowFast-SSM 把“低延迟导致高帧率重复计算”转化为“慢速环境表征 + 快速状态推进”的计算组织问题，在 VBD 上用约 39 M MAC/s 保住 2 ms 单分支质量，并把单采样算法延迟推进到 62.5 μs；但它仍是一项算法级效率证据，尚未完成端侧 p99、真实链路和人声保留的部署闭环。**

## 参考资料

1. [arXiv:2411.02019](https://arxiv.org/abs/2411.02019)。
2. 本地原件：raw/papers/low_latency_causal_se/2411.02019.pdf（PDF pp.1–5）。
3. 本 Wiki 中的相关页面：[[wiki_low_latency/index]]、[[wiki_low_latency/overview]]、[[wiki_low_latency/entities/SlowFast-SSM]]。
