---
title: GCFSnet — 低比特率双耳链路与超低时延多通道语音增强
type: source
created: 2026-09-16
updated: 2026-09-16
tags:
  - speech-enhancement
  - strict-causal
  - ultra-low-latency
  - multichannel
  - binaural
  - hearing-aids
  - beamforming
  - quantization
source_type: paper
year: 2023
authors: Nils L. Westhausen, Bernd T. Meyer
venue: IEEE WASPAA 2023
arxiv: https://arxiv.org/abs/2307.08858
local_pdf: raw/papers/low_latency_causal_se/2307.08858.pdf
related:
  - [[wiki_low_latency/entities/GCFSnet]]
  - [[wiki_low_latency/concepts/低比特率双耳特征链路]]
  - [[wiki_low_latency/index]]
  - [[wiki_low_latency/overview]]
  - [[wiki_array/concepts/波束成形 Beamforming]]
  - [[wiki/entities/RNNoise]]
  - [[wiki/sources/2023/DeepFilterNet 2023]]
---

~~~yaml
- 论文: [Low Bit Rate Binaural Link for Improved Ultra Low-Latency Low-Complexity Multichannel Speech Enhancement in Hearing Aids](2023)
  ├── 要解决什么问题: 双耳助听器想利用跨耳空间信息，但无线传输会带来延迟和低比特率，直接同步麦克风会破坏超低时延
  ├── 核心方法: 两侧各运行一个因果 GCFSnet；当前侧做复数 filter-and-sum 与多帧深度后滤波，跨耳侧只传输延迟且量化的 log-magnitude/IPD 特征
  ├── 属于哪个分支: 多通道/双耳语音增强 / 助听器 / 严格低时延 / 量化感知部署
  ├── 输入/输出: 多麦克风复数 STFT 与 sin/cos IPD → 复数空间滤波器和多帧后滤波器 → 左/右增强语音
  ├── 关键trick: 把延迟跨耳信号限制在特征支路；空间滤波只用当前本侧麦克风；Group Communication + weight sharing + QAT 压缩模型
  ├── 数据集: Libri3Mix min train/dev/test + WHAM!，16 kHz；RAZR 生成约 60k 双耳 BRIR 场景
  ├── 对比了谁: 未处理混合、oracle BLCMV、GCFSnetuni、GCFSnetlowB、GCFSnetbin
  ├── 性能上限: GCFSnetbin 在 8 bit 下 SI-SDR=1.51 dB、HASPI=0.75、MBSTOI=0.59、PESQ=1.23；lowB 在 6 ms/8 bit 为 0.79/0.71/0.56/1.20
  ├── 参数量: 单侧 164k 参数、约 0.36 GMAC/s；权重 8 bit、bias 16 bit、输入/输出 16 bit
  ├── 消融关键发现: 延迟跨耳 IPD 比延迟 log-magnitude 更有用；两者结合最好；超过 6 bit 后多数指标饱和，传输延迟越大收益越小
  ├── 遗留问题(你的机会): 没有真实助听器 capture-to-playback/p99、听障受试者、负 SNR 人声保留或 false-suppression 评估；严格因果依赖尚需逐层审计
  └── 跟哪篇像: [[wiki_low_latency/index]] 中的 2204.09911/2304.08707，以及 [[wiki_array/concepts/波束成形 Beamforming]]、[[wiki/entities/RNNoise]]
~~~

# Low Bit Rate Binaural Link for Improved Ultra Low-Latency Low-Complexity Multichannel Speech Enhancement in Hearing Aids

> Nils L. Westhausen, Bernd T. Meyer，IEEE Workshop on Applications of Signal Processing to Audio and Acoustics (WASPAA), 2023。  
> 随机抽取自本方向 14 篇论文；本笔记只针对 2307.08858，不代表其他论文已完成摄取。

> [!warning] PDF 转换质量与阅读说明
> 原 PDF 共 5 页。页面渲染显示清晰，但 pdftotext 对 Figure 1/2 中的希腊字母、上下标和连线标签有缺失/错位；下文的 Eq. (1)-(3)、架构字段和表格数字均通过原 PDF 页面视觉核对。Figure 1/2 的结构标签仍应以嵌入的原页面截图和原 PDF 为准。

## 1. 他们为什么这么做？（motivation）

### 1.1 任务背景

双耳助听器通常由左右两个 behind-the-ear（BTE）设备组成。两侧设备相距约 18 cm，跨耳麦克风信号包含有价值的空间线索；传统的 binaural MVM/LCMV beamforming 可以利用这些线索并尽量保持空间感。

但在互联双耳设备中，跨设备传输同时带来两个硬约束：

1. **传输延迟**：为了把对侧麦克风和本侧信号对齐，传统双耳处理往往需要等待或延迟本侧信号，从而增加整体系统延迟。
2. **链路带宽**：无线链路可能只能传输低比特率信号；量化后的跨耳波形会降低直接使用全部麦克风信号的增强质量。

论文的核心动机不是“把模型做得更大”，而是重新安排信息流：**让当前本侧麦克风承担不等待的空间滤波，让跨耳信息只作为已经延迟的辅助特征进入估计器**。这样可以牺牲一部分跨耳信息的新鲜度，换取低延迟和低复杂度。

### 1.2 论文目标

论文提出 Group-Communication Filter-and-Sum Network（GCFSnet），在左右设备各运行一个多输入单输出（MISO）模型：

~~~text
当前本侧多麦克风 ──→ 复数 filter-and-sum ──→ 多帧深度后滤波 ──→ 本侧增强语音
                         ↑
延迟/量化跨耳特征 ────────┘
~~~

作者声称：在过滤框架保持 2 ms 的情况下，低比特率双耳链路仍可带来收益，且单侧配置在部分指标上可以达到甚至超过高延迟 oracle BLCMV 的结果。

## 2. 之前的人怎么做不了？（limitation → gap）

### 2.1 既有方法的缺口

| 路线 | 能力 | 不能直接满足本题的地方 |
|---|---|---|
| BMVDR/BLCMV | 可以利用双耳空间信息并保持空间线索 | 通常需要同步信号；oracle BLCMV 的块长为 64 ms、shift 为 32 ms |
| 低延迟神经多通道增强 | 可以降低模型延迟 | 许多方法仍依赖较大的频谱模型或未解决双设备带宽 |
| 仅本侧 unilateral enhancement | 不等待跨耳链路，天然易做低延迟 | 丢失两侧间约 18 cm 间距带来的空间信息 |
| 直接传输跨耳波形 | 信息完整 | 传输延迟、量化误差和同步等待会进入处理链路 |

因此本文的 gap 是：**如何在不让跨耳传输延迟进入当前空间滤波路径的前提下，保留一部分延迟双耳信息，并把模型压到助听器 SoC 可承受的规模。**

### 2.2 严格因果与延迟审计

| 项目 | 论文给出的信息 | 本 Wiki 判定 |
|---|---|---|
| 模型因果性 | 摘要明确称 GCFSnet 为 causal；后滤波只使用当前/过去帧 | strict_causal*：论文级证据支持，但未给逐层 certificate |
| 前端 | 16 kHz，过滤框架 frame length 2 ms，shift 1 ms，FFT length 64，Hann；FFT 使用前后等量 zero padding | 约 2 ms 算法前端；等量 zero padding 的样本依赖边界需复现确认 |
| 跨耳输入 | lowB 在训练中随机延迟 4–12 ms，测试使用静态延迟；传输特征是已延迟的 log-magnitude 与 IPD | 没有 future observed samples；这是 stale context，不是 look-ahead |
| 估计器 | causal depthwise-separable convolution、共享 GRU、TAC、tanh 表示 | 结构上支持 streaming；归一化/缓存的逐层细节未完整报告 |
| 多帧后滤波 | Eq. (3) 只汇总 $\widetilde S(t-k,f)$，$k\ge 0$ | 因果；但 K 的计数口径需按实现确认 |
| 算法延迟 | 论文将过滤框架描述为 2 ms，并强调 delayed link 不增加该处理延迟 | 论文没有测 capture-to-playback、ADC/DMA、I/O、DAC 或模型 p99 |
| 计算量 | 单侧约 0.36 GMAC/s，164k 参数 | 理论/模型预算；不等于目标 SoC 的 deadline 通过 |

> [!question] 关键不确定性
> 本文可以标为“论文级 causal、约 2 ms 前端”，但还不能无条件标为“端到端严格 2 ms 已验证”。尤其是 FFT zero padding 的边界、真实设备 buffer、运行时 p99、状态 reset 和长流稳定性，原文没有给出完整证据。

## 3. 这个做法核心 trick 是什么？

### 3.1 Trick A：只让本侧当前信号进入空间滤波

多通道混合信号写为：

$$Y(m,t,f)=X_S(m,t,f)+\sum_{i=1}^{I}X_{V_i}(m,t,f)+X_D(m,t,f). \tag{1}$$

- $Y(m,t,f)$：第 $m$ 个麦克风在帧 $t$、频率 $f$ 的复数 STFT；
- $X_S$：目标语音（论文把它描述为 reverberant TF representation of the anechoic target speech）；
- $X_{V_i}$：第 $i$ 个干扰说话人；
- $X_D$：扩散噪声；
- $I$：干扰说话人的数量。

对每一侧，模型只用该侧当前可用的 $M$ 个麦克风估计复数 filter-and-sum 权重：

$$\widetilde S(t,f)=\sum_{m=1}^{M}Y(m,t,f)\,W(m,t,f). \tag{2}$$

其中 $W(m,t,f)$ 是复数滤波器。这个式子的工程含义是：**空间滤波本身不等待跨耳信号**；跨耳信息只改变网络估计出来的 $W$，不会把对侧传输延迟直接变成本侧输出的等待时间。

随后，在每一侧独立使用 causal multi-frame complex post-filter：

$$\widehat S(t,f)=\sum_{k=0}^{K}\widetilde S(t-k,f)\,C(t,k,f). \tag{3}$$

- $C(t,k,f)$：第 $k$ 个历史帧、频率 $f$ 的复数后滤波系数；
- $K$：后滤波历史范围；
- $\widetilde S(t-k,f)$：已经完成空间滤波的当前/历史中间表示。

论文正文说 post-filter of length K，并在配置中写 K=5，但公式索引为 $k=0,\ldots,K$。因此笔记不把它擅自解释成固定的 5 taps，而是保留这一计数歧义。

### 3.2 论文原图：空间滤波 + 后滤波

下图是原论文第 2 页的 Figure 1/2 页面渲染。左图展示两侧独立的 filter estimator、当前本侧 filter-and-sum、延迟跨耳特征和多帧后滤波；右图展示 Group Communication、共享卷积/GRU 和 filter estimation head。

![[wiki_low_latency/assets/2307.08858-page2-architecture.png]]

> 图注：原论文 Figure 1 与 Figure 2。图中虚线点划线表示跨设备麦克风信号在特征计算之前经历 transmission delay；原 PDF 中部分公式/标签在文本抽取中不可可靠识别，故保留页面图作为视觉证据。

### 3.3 Trick B：低比特率跨耳特征，而不是跨耳波形

论文比较三种配置：

| 配置 | 跨耳通信 | 本侧空间滤波 | 特征 |
|---|---|---|---|
| GCFSnetuni | 无 | 仅本侧 2 个麦克风 | 每个本侧通道的 log-magnitude STFT + 本侧 sin/cos IPD |
| GCFSnetlowB | 有延迟、可变低比特率 | 仍仅本侧麦克风 | 在 unilateral 特征上追加延迟跨耳 log-magnitude 与跨耳 sin/cos IPD |
| GCFSnetbin | 无延迟、固定比特率的理想双耳链路 | 使用同步的全部麦克风 | 所有麦克风的 log-magnitude + 参考通道与其他通道的 sin/cos IPD |

IPD（inter-channel phase difference）被表示为 $\sin(\mathrm{IPD})$ 和 $\cos(\mathrm{IPD})$，而不是直接传相位角。这样做有两个好处：

1. sin/cos 表示避免相位 $2\pi$ wrap 的不连续；
2. log 压缩与有界的 sin/cos 值域更适合固定范围量化。

lowB 的关键不是让延迟跨耳信号“追上当前帧”，而是让模型知道它是延迟的，并在训练时随机化传输延迟和比特率。这样模型学习的是“如何使用不完美的空间提示”，而不是假设跨耳信号永远同步。

### 3.4 Trick C：Group Communication + weight sharing + QAT

GCFSnet 的过滤器估计器可以概括为：

~~~text
特征 (t, B)
  → FC 投影到 P=128
  → 切成 G=8 个 group
  → 共享 FC 映射到 U=32
  → 共享 causal depthwise-separable Conv（kernel 5/3）
  → TAC 聚合 group 信息（hidden dimension 2U）
  → 2 层共享 GRU（每层 U units）+ D-Conv skip
  → TAC
  → ungroup + FC
  → 估计实数/复数空间滤波器 W 与后滤波器 C
~~~

模型的关键共享关系：

- 卷积模块和 GRU 模块在 group 之间共享；
- 左模型和右模型使用相同架构，并共享这些模块的权重；
- conv 模块负责短期依赖，GRU 模块负责较长期依赖；
- TAC（Transform Average Concatenate）在 group 间交换信息；论文将原 TAC 的 PReLU 改为 tanh，以限制隐表示范围。

量化感知训练（QAT）设置为：

- 权重 8 bit；
- bias 16 bit；
- 层输入/输出 16 bit；
- 线性 fixed-range quantization，范围 $[-1,1]$；
- 通过不量化的 kernel-size-1 D-Conv 实现 quantization equalizer（quantEQ），减小溢出导致的信息损失；
- 所有层使用 tanh，使 latent representation 有界。

这使模型规模达到单侧 164k 参数、约 0.36 GMAC/s。注意这是论文给出的理论计算预算，尚不是某个实际 SoC 上的 p99 deadline 测量。

## 4. 实验里哪个消融最关键？

### 4.1 数据与训练设置

训练/验证/测试基于 Libri3Mix 的 min train 360（146 h）、min dev（11 h）和 min test（11 h），加入 WHAM! 噪声，采样率 16 kHz。由于目标说话人固定在接收器前方且不与干扰源重合，作者没有直接复用带有不同场景假设的既有数据集，而是用 RAZR 生成约 60k 个双耳房间脉冲响应（BRIR）：

- behind-the-ear 助听器 dummy，每侧 3 个麦克风（front/mid/rear）；
- 房间 $RT60$ 从 0.1–0.5 s 采样，房间高度 2.5–4.5 m，面积 12–100 $m^2$；
- 目标说话人方位在正前方 $-12^\circ$ 到 $12^\circ$，距离 0.75–1.5 m；
- 两个干扰说话人和一个扩散噪声源；
- 目标训练参考使用 direct BRIR 部分，包含去混响目标意图。

训练样本在线生成。干扰语音与目标之间的 better-ear SNR 从 $\mathcal N(0,4.1^2)$ dB 采样，噪声从 $\mathcal N(6.2,4.4^2)$ dB 采样；lowB 训练时再随机采样 4–12 ms transmission delay 和 4–16 bit bitrate。

训练配置：

| 项目 | 设置 |
|---|---|
| epochs / batch | 100 / 16 |
| optimizer | Adam，初始 lr $10^{-3}$ |
| 学习率 | 每 2 epochs 乘 0.98；验证集连续 5 epochs 不下降时乘 0.8 |
| gradient clipping | AutoClip，$p=10$ |
| framework | TensorFlow 2.11 |
| 过滤框架 | 2 ms frame、1 ms shift、FFT 64、Hann |
| 模型尺寸 | $P=128,\ U=32,\ G=8,\ K=5$ |
| loss | 等权 compressed spectral MSE（cMSE）+ phase-constrained magnitude loss（PCM） |
| loss 计算 | 重建后用 20 ms window、10 ms shift、FFT 320 |

论文说明 cMSE 和 PCM 等权略优于单独使用任一损失，但没有在本文中展开两者的完整数学定义，只给出参考文献。因此这里不自行补造 cMSE/PCM 公式。

### 4.2 评价指标

论文使用：

- SI-SDR：左右双耳信号取均值；
- PESQ：左右双耳信号取均值；
- better-ear HASPI：按正常听力配置、混合信号缩放到 65 dB SPL；
- MBSTOI：双耳短时客观可懂度。

所有指标的参考是目标语音与 direct BRIR 卷积后的信号。论文**没有**报告本 Wiki 重点关注的 DNSMOS SIG/BAK/OVL、VAD false-suppression、SPP 校准、ASR WER、F0/formant/prosody continuity 或真实听感测试。

### 4.3 主结果：低比特率有收益，但同步双耳仍是上界

| System | Delay (ms) | Bits | SI-SDR (dB) | HASPI | MBSTOI | PESQ |
|---|---:|---:|---:|---:|---:|---:|
| Unprocessed | — | — | -9.20 | 0.17 | 0.38 | 1.06 |
| BLCMV oracle | — | — | -1.52 | 0.67 | 0.60 | 1.11 |
| GCFSnetuni | — | — | -0.11 | 0.66 | 0.53 | 1.18 |
| GCFSnetlowB | 12 | 6 | 0.57 | 0.67 | 0.55 | 1.19 |
| GCFSnetlowB | 12 | 8 | 0.60 | 0.68 | 0.55 | 1.19 |
| GCFSnetlowB | 12 | 16 | 0.60 | 0.68 | 0.55 | 1.19 |
| GCFSnetlowB | 6 | 6 | 0.75 | 0.70 | 0.56 | 1.19 |
| GCFSnetlowB | 6 | 8 | **0.79** | **0.71** | 0.56 | **1.20** |
| GCFSnetlowB | 6 | 16 | 0.77 | 0.71 | 0.56 | 1.20 |
| GCFSnetbin | 0 | 6 | 1.44 | 0.73 | 0.59 | 1.22 |
| GCFSnetbin | 0 | 8 | **1.51** | **0.75** | 0.59 | **1.23** |
| GCFSnetbin | 0 | 16 | 1.45 | 0.75 | 0.59 | 1.23 |

解释：

- 所有 GCFSnet 配置都显著优于未处理混合；
- lowB 相对 unilateral 的最大改善出现在 SI-SDR，6 ms/8 bit 达 0.79 dB；
- GCFSnetuni 在 SI-SDR 和 PESQ 上已经超过这里的 oracle BLCMV，但 BLCMV 使用的是保留更多混响的参考/估计设置，SI-SDR 受混响影响，不能据此宣称神经模型全面超过 oracle；
- MBSTOI 更偏向保留双耳信息，BLCMV 与 GCFSnetbin 在 8/16 bit 下最高；
- GCFSnetlowB 仍低于无延迟同步的 GCFSnetbin，说明延迟双耳特征是有用的补充而不是完整替代。

### 4.4 原论文结果图：传输延迟和比特率的作用

![[wiki_low_latency/assets/2307.08858-page4-results.png]]

> 图注：原论文第 4 页 Figure 3、Table 1 和 Table 2。Figure 3 的红色虚线是 GCFSnetuni 参考线。可直接读出的趋势是：传输延迟上升时收益下降；大于约 6 bit 后多数指标趋于饱和；低 bit + 长延迟时 HASPI/PESQ 可能跌回 unilateral 基线以下。

### 4.5 最有价值的特征消融

Table 2 固定 delay=6 ms、bandwidth=8 bit，比较 lowB 的两类延迟双耳特征：

| GCFSnetlowB 特征 | LogMag | IPD | SI-SDR | HASPI | MBSTOI | PESQ |
|---|:---:|:---:|---:|---:|---:|---:|
| 两者都用 | ✓ | ✓ | **0.78** | **0.71** | 0.56 | **1.20** |
| 只用 IPD |  | ✓ | 0.66 | 0.69 | 0.56 | 1.19 |
| 只用 LogMag | ✓ |  | 0.06 | 0.67 | 0.53 | 1.18 |

最关键的结论是：**延迟 IPD 比延迟 log-magnitude 更能提供有价值的方向信息**，但两者联合仍然最好。对本方向而言，这个结果比“多传几 bit”更有启发性：在固定带宽下，优先保护空间相位结构可能比传输更多幅度细节更划算。

## 5. 这个方向还剩什么问题没解决？（future work / limitation）

### 5.1 论文明确提出的 future work

- 训练和测试加入更动态的声学场景；
- 学习类似 [30] 的 steering；
- 比较延迟双耳特征的其他形式，如 normalized cross-correlation；
- 在听障受试者、真实 BTE 设备和 real-time audio processing 上评估；
- 移植为 fully fixed-point C，在 SmartHeaP 等平台实测；
- 与 openMHA 等开放助听器研究平台集成。

### 5.2 读出来的隐藏问题

1. **2 ms 还不是端到端 deadline 证明**：没有 ADC/DMA、输入/输出 buffer、模型 p50/p95/p99、DAC 或 underrun 记录。
2. **strict-causal certificate 不完整**：论文称 causal，但没有逐层列出 zero padding、状态、边界和归一化的最后可读输入样本。
3. **人声保留没有被单独测量**：没有负 SNR 分层、SIG/BAK、false-suppression、ASR WER、F0/formant 连续性；SI-SDR/HASPI/MBSTOI 不能替代这些指标。
4. **场景先验较强**：目标总在前方 $-12^\circ$ 到 $12^\circ$，这会让“前方 steering”比任意方向更容易；未覆盖移动目标、目标与干扰近角度重合等压力场景。
5. **同步双耳配置是理想上界**：GCFSnetbin 的 0 ms delay 不是无线链路可用配置；lowB 的真实目标应与 GCFSnetuni 做同延迟/同算力的 Pareto 比较。
6. **模型容量与链路设计耦合**：164k/0.36 GMAC/s 是为特定 SoC 容量选择的，不代表在所有设备上最优；没有参数、bitrate、延迟和质量的统一 Pareto 曲线。
7. **没有神经基线**：作者有意只研究 binaural link 效应，因此不能由本文单独判断 GCFSnet 与 DCCRN、DPCRN、DeepFilterNet 或其他增强器的总体优劣。

### 5.3 对当前课题的可迁移启示

这篇论文最适合迁移的不是“助听器结构原样照搬”，而是一个信息流原则：

> **低时延主路径只读当前本地观测；可能迟到的辅助信息进入置信度/滤波器估计支路，并在训练时显式模拟迟到、量化和失真。**

在单通道 2 ms 课题中，可以把 IPD 换成 SPP/voicing/uncertainty 置信度；在双麦课题中，可以保留 sin/cos IPD 并测试它对 SIG–BAK trade-off 的影响。但必须重新报告单通道/双通道、负 SNR、人声误抑制和端侧 p99，不能直接把本文的 hearing-aid 结果外推到普通语音通信。

## 6. 本论文在库中的位置关联（cross-reference matrix）

| 关系 | 库中论文/概念 | 关联与差异 |
|---|---|---|
| 前身/基石 | [[wiki_array/concepts/波束成形 Beamforming]] | GCFSnet 的 filter-and-sum 是可学习复数空间滤波；继承波束成形利用空间差异抑噪的基本思想 |
| 前身/基石 | [STFT-Domain Neural Speech Enhancement with Very Low Algorithmic Latency](https://arxiv.org/abs/2204.09911) | 同样把短时频前端、因果/低延迟和增强质量放在一起；GCFSnet 进一步加入双耳链路与链路量化 |
| 前身/基石 | [Ultra-Lightweight Speech Separation Via Group Communication](https://doi.org/10.1109/ICASSP39774.2021.9414561) | 论文直接采用 Group Communication 思路；本作将其放入双耳 filter estimator 并结合 QAT |
| 同分支竞品 | [Neural Speech Enhancement with Very Low Algorithmic Latency and Complexity](https://arxiv.org/abs/2304.08707) | FSB-LSTM 关注 full-/sub-band 时频建模和低延迟；GCFSnet 更强调多麦空间滤波与跨耳链路 |
| 同分支竞品 | [[wiki/sources/2023/DeepFilterNet 2023]] | DeepFilterNet 以低复杂度复数深滤波处理幅相细节；GCFSnet 以多麦复数 filter-and-sum 处理空间线索，二者可形成时频/空间互补 |
| 跨分支类比 | [[wiki/entities/RNNoise]] | RNNoise 的“低复杂度 + DSP 主路径 + 小网络估计器”哲学与 GCFSnet 相似；GCFSnet 将网络估计对象换成复数空间/后滤波器 |
| 后续/扩展 | [[wiki_low_latency/index]] 中的 2411.02019、2608.12099 | 两篇是后续低时延 SSM/Mamba 路线，但不是 GCFSnet 的直接续作；可比较固定状态、量化和多通道空间特征的组合 |
| 跨分支类比 | [[wiki_array/concepts/空间混叠 Spatial Aliasing]] | 多麦空间特征有阵列几何与相位差限制；若迁移到双麦/阵列，应把 IPD 的频率范围和空间混叠作为额外审计项 |

> [!question] 关联不确定性
> 当前新 Wiki 已为本清单的 14 篇论文建立 source/entity/concept 页面；本矩阵中的同条件数字仍不可直接横向排名，真实端到端验证和“被谁超越”的证据需在后续统一实验中补齐。

## 7. 一句话总结“江湖地位”

~~~text
2023 | 助听器多通道低时延语音增强 | 用延迟/量化感知的跨耳特征 + 本侧复数 filter-and-sum 保住 2 ms 过滤框架 → 为“迟到的空间信息如何服务实时增强”提供了一个可部署的系统范式，但真实设备端到端时延和人声保留证据仍未闭环。
~~~

## 参考资料

- [arXiv abstract page](https://arxiv.org/abs/2307.08858)
- [Local PDF](../../../raw/papers/low_latency_causal_se/2307.08858.pdf)
- [[wiki_low_latency/overview]]
- [[wiki_low_latency/concepts/低比特率双耳特征链路]]
