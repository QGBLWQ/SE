---
title: On TasNet - 低时延单说话人语音增强
type: source
created: 2026-09-16
updated: 2026-09-16
tags:
  - speech-enhancement
  - single-speaker
  - low-latency
  - causal
  - waveform-domain
  - tasnet
  - noise-suppression
  - speech-preservation
  - aliasing
source_type: paper
year: 2021
authors: Morten Kolbæk; Zheng-Hua Tan; Søren Holdt Jensen; Jesper Jensen
venue: arXiv preprint
arxiv: https://arxiv.org/abs/2103.14882
local_pdf: raw/papers/low_latency_causal_se/2103.14882.pdf
related:
  - "[[wiki_low_latency/entities/On-TasNet]]"
  - "[[wiki_low_latency/concepts/2103.14882-causal-tasnet]]"
  - "[[wiki/entities/Conv-TasNet]]"
  - "[[wiki/sources/2019/Conv-TasNet 2019]]"
  - "[[wiki/sources/2020/Real Time SE Waveform 2020]]"
  - "[[wiki_low_latency/entities/GCFSnet]]"
  - "[[wiki_low_latency/overview]]"
  - "[[wiki_low_latency/index]]"
---

~~~yaml
- 论文: [On TasNet for Low-Latency Single-Speaker Speech Enhancement](2021)
  ├── 要解决什么问题: 验证 TasNet 在单说话人加性噪声抑制中是否保留分离任务上的优势，并审计短窗/短 hop 的低时延代价
  ├── 核心方法: learned encoder → TCN separator → learned decoder 的端到端波形域管线；比较 gLN/cLN 与非因果/因果卷积
  ├── 属于哪个分支: 单通道波形域语音增强 / 因果 TasNet / 低时延与混叠审计
  ├── 输入/输出: 单麦克风带噪波形 y → 单目标增强波形 x-hat；I=2 时作为两说话人分离验证实现
  ├── 关键trick: 让目标与噪声在 learned inner-domain 中尽量低重叠；保持 2 ms window/1 ms hop；观察 hop 增大后的 aliasing 风险
  ├── 数据集: WSJ0；ssn、竞争女性说话人 wsjf、CHiME3 混合噪声 mix；8 kHz、4 s 信号、训练 SNR 均匀采样于 [-10,10] dB、测试 0 dB
  ├── 对比了谁: 同复杂度约 3.5M 参数的 uNet；TasNet 的 gLN/cLN、非因果/因果变体；2mix/2bal 分离验证
  ├── 性能上限: Table 1 非因果 cLN 在 wsjf 上 STOI=0.97、PESQ=3.33、SI-SDR=16.0 dB；因果 cLN 为 0.95/2.74/12.4，未报告 RTF 或端到端 deadline
  ├── 参数量: TasNet 3.5M；论文还给出 receptive field=15,310 samples，Table 1 同时写 1.53 s，二者在 8 kHz 下不一致
  ├── 消融关键发现: Table 2 中 64 ms/32 ms 明显退化，而 64 ms/1 ms 基本恢复；作者据此将 hop 而非 window 视为关键，并 conjecture aliasing
  ├── 遗留问题(你的机会): 无 MAC/s、FLOPs、RTF、p99、capture-to-playback、warm-up/state reset 或 deadline miss；也没有 false-suppression、SIG/BAK、WER、F0/formant/prosody 语音保留证据
  └── 跟哪篇像: [[wiki/entities/Conv-TasNet]]、[[wiki/sources/2020/Real Time SE Waveform 2020]]、[[wiki/entities/RNNoise]]、[[wiki_low_latency/sources/2023/GCFSnet 2023]]
~~~

# On TasNet for Low-Latency Single-Speaker Speech Enhancement

> Morten Kolbæk, Zheng-Hua Tan, Søren Holdt Jensen, Jesper Jensen。论文 PDF 侧栏日期为 27 Mar 2021；本文以本地 raw/papers/low_latency_causal_se/2103.14882.pdf 为唯一论文证据。

> [!warning] PDF 转换与证据质量
> 本地 PDF 共 5 页。已用 Poppler 从原 PDF 重渲染并视觉核对全部页面：第 1-4 页的方法、架构、Figure 2、Table 1/2 和结论清晰，第 5 页为参考文献。渲染器报告缺少 Symbol 与 ArialUnicode 显示字体，pdfplumber 抽取在第 1 页公式、下标/上标和表格列结构处出现错位，因此公式和表格数字以下均以原 PDF 页面视觉核对为准。论文还存在两项需要保留的内部证据边界：Section 2.1 写 receptive field 为 15,310 samples，而 Table 1 写 1.53 s；PDF 正文将验证集称为 si_tr_s 且给出 1,163 utterances，和训练集名称重复，需复现确认。本文不把作者对 aliasing 的解释升级为已证明的因果机制。

## 1. 他们为什么这么做？（motivation）

### 1.1 任务与对象

论文的切入点是一个“已有分离架构是否适用于更常见增强任务”的验证问题。TasNet 在多说话人分离上已经取得很高的波形重建性能，但单说话人加性噪声增强在本文之前并不清楚是否同样受益。作者因此把 TasNet 放入 single-channel speech enhancement，并与同等规模、面向增强设计的 uNet 比较。

应用动机包括移动通信设备、助听器、视频会议和语音转写：系统需要从单麦克风混合中提取目标语音，减少背景噪声，同时保留人和机器接收者所需的可懂度。论文没有把“低时延”定义成端到端设备 deadline；它通过短 window/hop 和 causal convolution 变体研究低时延路径。

### 1.2 任务的数学定义

论文在 Section 2 中将单通道混合写为：

$$
x_i \in \mathbb{R}^{L},\qquad v \in \mathbb{R}^{L},\qquad
y=\sum_{i=1}^{I}x_i+v .
$$

- x_i：第 i 个无噪时域语音信号，包含 L 个样本；
- v：加性噪声；
- y：单麦克风观测；
- I：目标语音/说话人数量；
- L：这里是任务定义中的信号段长度，不要和配置中的 encoder L16 混为同一口径。

深度网络的目标是：

$$
\hat{x}_i=f_{\mathrm{DNN}}(y,\theta),
$$

其中 f_DNN 是参数为 theta 的 DNN 估计器。I=1 时就是本文关注的单说话人语音增强；I=2 时用两说话人分离数据验证 TasNet 实现。

| 维度 | PDF 明示内容 |
|---|---|
| 任务 | 单通道、单目标说话人语音增强；附加两说话人分离验证 |
| 输入 | 单麦克风带噪时域波形 y |
| 输出 | I=1 时的增强目标波形 x-hat；I=2 时的两个估计波形 |
| 采样率 | 8 kHz |
| 噪声 | stationary speech-shaped noise（ssn）；竞争女性说话人（wsjf）；mix：ssn、6-speaker babble、street、cafeteria、bus、pedestrian 的串接 |
| 训练/测试 SNR | 训练从 [-10, 10] dB 均匀采样；测试固定为 0 dB |
| 低时延设置 | Table 2 的短设置为 2 ms window / 1 ms hop；causal 配置的论文描述为 latency 由 frame hop 决定，多数实验为 1 ms |

### 1.3 为什么强调噪声类型与人声保留

论文摘要明确说，TasNet 的最大增强收益出现在 speech 这类调制噪声上。wsjf 是最接近“竞争说话人误抑制”压力测试的设置；ssn 则提供较稳定的 stationary 对照；mix 是多种噪声串接的增强设置。这个划分可以检验模型是否只是压低平稳噪声，还是也能在目标语音与干扰说话人重叠时保留目标。

不过，论文的保留证据主要是 STOI、PESQ、SI-SDR 与 learned inner-domain 的 overlap 分析，没有直接测量目标语音的 false-suppression、弱辅音、F0、formant、prosody 或 ASR WER。因而“语音保留”在本文中是由客观指标和表示诊断间接支持，而不是独立闭环的部署指标。

## 2. 之前的人怎么做不了？（limitation → gap）

### 2.1 从多说话人分离到单说话人增强的空白

论文指出，深度学习推动了语音处理进步，但研究注意力更多集中于重叠语音和多说话人分离；自然对话中的单说话人加性噪声增强同样常见，却较少被 TasNet 直接验证。TasNet 已在分离任务中超过 ideal ratio magnitude mask，但“为什么有效”以及这种优势能否迁移到 I=1 增强任务仍未建立。

因此本文的 gap 不是提出新的 separator，而是建立三条证据：

1. 在单说话人增强中，TasNet 是否超过 state-of-the-art uNet；
2. learned inner-domain 是否比传统 STFT 更容易把目标和噪声分开；
3. frame window 与 hop 对低时延性能的影响是否相同。

### 2.2 既有表示与低时延实现的限制

| 路线/配置 | 论文中暴露的限制 | 对本文 gap 的意义 |
|---|---|---|
| 传统 STFT filterbank | 目标和噪声在同一时频系数上的 overlap 可能较高，尤其是竞争说话人与 ssn | 需要检验 learned inner-domain 是否形成更低 overlap 的任务适配表示 |
| TasNet 非因果卷积 + gLN | gLN 使用整个 signal；非因果卷积也需要 future look-ahead | 质量上限高，但不能直接视为严格因果 |
| TasNet 非因果卷积 + cLN | cLN 不消除非因果 convolution 的 look-ahead；存在 kernel-dependent fixed system latency | 可隔离归一化变化与卷积 future context 的影响 |
| TasNet 因果卷积 + cLN | 论文称 essentially causal，质量下降，且竞争说话人噪声下降更明显 | 形成低时延基线，但仍需要逐层 dependency certificate 和设备 deadline 验证 |
| 大 frame hop | separator 按 inner-domain rows 独立卷积，rows 相当于按 hop decimation 的输入版本；无 anti-aliasing filter | Table 2 的退化支持“hop 关键”的现象，但 aliasing 仍是作者 conjecture |

### 2.3 因果性与 future-information 审计

| TasNet 变体 | PDF 证据 | 本 Wiki 标签 |
|---|---|---|
| gLN + non-causal convolution | gLN 使用整个 signal；卷积为 non-causal | non_causal |
| cLN + non-causal convolution | non-causal convolution 需要依赖 kernel length 的 look-ahead，并带来 fixed system latency | non_causal / low_look_ahead |
| cLN + causal convolution | 论文说该配置“essentially causal”，latency 由 frame hop 决定，本文大多数实验为 1 ms | paper_claimed_causal；尚不能升级为 strict_causal |

论文没有逐层列出 padding、卷积缓存、decoder overlap/add 边界、warm-up、state reset、归一化统计的最后可读样本，也没有测量输入输出 buffer。因此，本文最稳妥的结论是：**存在一个论文描述的 causal TasNet 配置，并以 1 ms hop 作为低时延线索；但 PDF 没有给出严格因果证书或端到端 1 ms 证明。**

## 3. 这个做法核心 trick 是什么？

### 3.1 核心不是新增模块，而是 learned inner-domain 的任务迁移

本文沿用 TasNet 的 encoder-separator-decoder 范式，把 I=1 当作增强任务：

~~~text
带噪波形 y
  → learned 1-D convolution encoder
  → inner-domain 表示 w
  → TCN separator 估计逐点 scalar weights
  → learned transposed-convolution decoder
  → 增强波形 x-hat
~~~

![[wiki_low_latency/assets/2103.14882/2103.14882-page2-architecture.png]]

> 图注：原论文 PDF 第 2 页，Figure 1 的 TasNet（左）与 uNet（右）架构原页截图。用途：核对“encoder → separator → decoder”数据流、TasNet 的 TCN separator 与 uNet 的多级卷积/skip connection 对照；该页同时包含 Section 2.1 的实现与 latency 文字证据。

Encoder 和 decoder 都是与 separator 端到端联合学习的线性映射；separator 的 scalar weight 逐点作用于 inner-domain 表示。传统变换增强可把中间域理解为 STFT，再在 STFT 系数上乘权重并 iSTFT；本文的不同点是中间域和重建映射都为任务学习，而不是固定 DFT/iSTFT。

### 3.2 输入、输出与符号化重写

论文 Figure 1 和 Section 2.1 用文字描述 encoder、separator、decoder，没有在本文正文给出完整的编号 encoder/decoder 方程。为方便复现，下面是依据该流程做的符号化整理，**不是额外声称的论文编号公式**：

$$
\mathbf{w}_t=E\!\left(y_{t:t+L_e-1}\right),
\qquad
\mathbf{d}_{i,t}=\mathbf{w}_t\odot\mathbf{m}_{i,t},
\qquad
\hat{x}_i=D\!\left(\{\mathbf{d}_{i,t}\}_t\right).
$$

| 符号 | 含义 | 证据边界 |
|---|---|---|
| E | learned encoder，论文称 fixed (learnt) linear map，工程上以 1-D Conv 实现 | Figure 1 与 Section 2.1 |
| w_t | 第 t 个 input frame 的 inner-domain 表示 | 依据论文流程的符号化记法 |
| m_i,t | separator 给第 i 个输出估计的逐点 scalar weight | 论文正文明确描述为 scalar weight values |
| d_i,t | 加权后的 inner-domain 表示 | w ⊙ m 为流程整理 |
| D | learned decoder，工程上以 transposed convolution 实现 | Figure 1 与 Section 2.1 |
| L_e | encoder frame length 的记号 | 不等同于任务定义的信号段长度 L；具体配置列为 L16 |

### 3.3 TasNet 配置与 uNet 对照

论文采用的 TasNet 配置（沿用其引用的 TasNet notation）为：

| 配置项 | PDF 明示值 | 备注 |
|---|---:|---|
| L | 16 | 配置字符串中的 encoder frame length；Table 2 的短设置为 2 ms window |
| K | 8 | 论文列出但本文没有重新定义该符号，需按引用 [6]/[20] 实现确认 |
| N | 512 | encoder inner-domain 维度/filters 的配置值 |
| X | 8 | 论文列出的 TasNet configuration 符号 |
| R | 3 | 论文列出的 TasNet configuration 符号 |
| B | 128 | bottleneck configuration 值 |
| H | 512 | hidden-channel configuration 值 |
| P | 3 | convolution filter-size configuration 值 |
| 参数量 | 3.5 million | TasNet 与 uNet 设计为相近规模 |
| receptive field | Section 2.1: 15,310 samples；Table 1: 1.53 s | 在 8 kHz 语境下两个 PDF 数字不一致，保留原值，不擅自换算 |

论文给出的 uNet 对照为 filter size 11 samples、receptive field 2,561 samples、3.5 million parameters。其 (inChannel, outChannel, stride) 层序列为：

~~~text
(1,48,1);
(48,48,2) × 2;
(48,96,2);
(96,96,2) × 2;
(96,180,2);
(180,180,2) × 2;
(180,180,1) × 2;
(180,96,1);
(96,96,1) × 2;
(96,48,1);
(48,48,1) × 2;
(48,1,1)
~~~

uNet 使用 parameterized ReLU，并在 encoder 中每三层之后使用 dropout；Table 1 将它列为 non-causal。这个 baseline 使比较尽量聚焦于 representation/separator 设计，而非单纯参数量。

### 3.4 为什么 learned inner-domain 可能有利于人声保留

作者定义 inner-domain overlap：在目标与噪声都对某个 inner-domain coefficient 有显著贡献的系数数量，占总系数数量的比例。overlap 越低，意味着目标和噪声在表示中越可分，理论上可以抑制噪声而较少伤害目标。

Figure 2（PDF 第 3 页）视觉上比较了 TasNet inner-domain（上排）和 STFT filterbank（下排）在 competing speaker、ssn、bus 三种噪声下的 overlap。论文观察到 TasNet 相比 STFT 降低了 overlap，竞争说话人与 ssn 的降幅更明显；bus 的改善较小，作者将其归因于 bus 的低通性质使 STFT 本身已经比较有效。这个结果是**表示层机制证据**，不是 false-suppression 或 F0 保留的直接测量。

### 3.5 hop 作为关键超参数与 aliasing 假说

Table 2 显示，2 ms/1 ms 与 64 ms/1 ms 的性能接近，而 64 ms/32 ms 明显变差。作者的解释链为：

1. separator 使用 convolution，且对 inner-domain 的不同 rows 独立操作；
2. 每个 row 相当于以 hop 为 decimation factor 的输入时域版本；
3. 没有 anti-aliasing filter 时，较大的 hop 可能引入更强 aliasing components；
4. 因而性能下降更可能由 hop 而非 window length 控制。

这条链路是论文明确提出的 conjecture。Table 2 支持“hop 变化与性能同步变化”的现象，但本文没有单独加入 anti-aliasing filter、跨 row separator 或 aliasing energy 的控制实验，所以不能把它写成已完成的因果证明。

### 3.6 论文出现的关键公式与指标边界

本论文明确写出的任务公式是 y = sum_i x_i + v 与 x-hat_i = f_DNN(y,theta)；encoder/decoder 过程主要以 Figure 1 和文字说明呈现。实验报告 STOI、PESQ 和 Scale-Invariant SDR，但 PDF 没有在本文中展开这三个指标的计算公式，也没有报告 DNSMOS SIG/BAK/OVL、ASR WER 或主观 MOS。因此不要把其他 Wiki 页面中的指标公式倒灌为本论文的实验定义；评价指标背景可参阅 [[wiki/concepts/语音增强评价指标]]。

## 4. 实验里哪个消融最关键？

### 4.1 数据、混合与训练

| 项目 | PDF 明示设置 |
|---|---|
| 语料 | WSJ0 |
| 训练语音 | si_tr_s，11,613 utterances，约 44 male + 47 female speakers |
| 验证语音 | PDF 文字写为 si_tr_s，1,163 utterances，5 male + 5 female speakers；名称与训练集重复，需复现确认 |
| 测试语音 | si_et_05 与 si_dt_05，合计 1,857 utterances，10 male + 6 female speakers |
| VAD | 在 clean waveform 上以 25 ms 段分析；移除能量比最大段低超过 40 dB 的段 |
| 信号长度/采样率 | 拼接或截断到 4 s，downsample 到 8 kHz |
| 数据数量 | 训练 20,000 signals，验证 2,000 signals；论文另说明 wsj0-2mix 为 5,000、测试使用 3,000 signals |
| 分离混合 | wsj0-2mix 与新建性别平衡 wsj0-2bal；两语音随机 power ratio 均匀采样于 [-2.5, 2.5] dB；不加入额外噪声 |
| 增强混合 | y=x+v；v 从 ssn、wsjf 或 mix 噪声中取等长随机序列 |
| 目标约束 | 使用 wsjf 时 clean target 只取 male speakers，以避免 uNet 的 label permutation 问题 |
| 优化器 | Adam |
| 学习率 | TasNet 0.001；uNet 0.0001；验证 loss 两个 epoch 未下降时减半 |
| batch | 8 |
| 停止条件 | 验证 loss 五个 epoch 未下降，或 TasNet 100 epochs / uNet 200 epochs 达上限 |

两说话人分离实验在计算指标前用真实 source 确定 TasNet 输出的正确 permutation；单说话人增强则直接评估目标输出。论文没有给出训练时的随机种子、硬件、量化设置、部署 runtime 或完整 optimizer state，因此复现仍依赖引用 [6] 和 [20] 的实现细节。

### 4.2 评价指标

- STOI：短时客观可懂度；
- PESQ：感知语音质量；
- SI-SDR：尺度不变信号失真比。

论文报告 noisy 与 processed 两列，并在两说话人分离验证中报告 mean STOI/PESQ/SI-SDR。本文没有 DNSMOS、SIG/BAK/OVL、false-suppression、SPP/VAD calibration、ASR WER、F0/formant/prosody continuity、voiced energy 或听者 MOS；这些缺口对低 SNR 人声保留尤其重要。

### 4.3 Table 1：TasNet/uNet 与因果性结果

![[wiki_low_latency/assets/2103.14882/2103.14882-page4-results.png]]

> 图注：原论文 PDF 第 4 页，Table 1 与 Table 2 原页截图。用途：核对 noisy/processed 的 STOI、PESQ、SI-SDR、Norm、Causal 与 receptive-field 列；页面下半部分同时保留作者对 hop/aliasing 的讨论和结论。

| Test set | Model | # target | RF (s) | Norm | Causal | STOI noisy | STOI processed | PESQ noisy | PESQ processed | SI-SDR noisy | SI-SDR processed |
|---|---|---:|---:|---|:---:|---:|---:|---:|---:|---:|---:|
| 2mix | TasNet | 2 | 1.53 | gLN | N | 0.74 | 0.94 | 1.68 | 2.96 | 0.0 | 14.1 |
| 2mix | TasNet | 2 | 1.53 | cLN | N | 0.74 | 0.93 | 1.68 | 2.93 | 0.0 | 13.0 |
| 2mix | TasNet | 2 | 1.53 | cLN | Y | 0.74 | 0.90 | 1.68 | 2.52 | 0.0 | 10.2 |
| 2bal | TasNet | 2 | 1.53 | gLN | N | 0.70 | 0.94 | 1.50 | 2.84 | 0.0 | 13.4 |
| 2bal | TasNet | 2 | 1.53 | cLN | N | 0.70 | 0.91 | 1.50 | 2.69 | 0.0 | 11.9 |
| 2bal | TasNet | 2 | 1.53 | cLN | Y | 0.70 | 0.89 | 1.50 | 2.29 | 0.0 | 9.4 |
| mix | TasNet | 1 | 1.53 | gLN | N | 0.76 | 0.93 | 1.56 | 2.64 | 0.0 | 12.2 |
| mix | TasNet | 1 | 1.53 | cLN | N | 0.76 | 0.93 | 1.56 | 2.63 | 0.0 | 12.3 |
| mix | TasNet | 1 | 1.53 | cLN | Y | 0.76 | 0.89 | 1.56 | 2.17 | 0.0 | 9.7 |
| mix | uNet | 1 | 0.32 | n/a | N | 0.76 | 0.91 | 1.56 | 2.41 | 0.0 | 11.1 |
| ssn | TasNet | 1 | 1.53 | gLN | N | 0.73 | 0.93 | 1.42 | 2.56 | 0.0 | 11.4 |
| ssn | TasNet | 1 | 1.53 | cLN | N | 0.73 | 0.93 | 1.42 | 2.57 | 0.0 | 11.4 |
| ssn | TasNet | 1 | 1.53 | cLN | Y | 0.73 | 0.89 | 1.42 | 2.11 | 0.0 | 9.1 |
| ssn | uNet | 1 | 0.32 | n/a | N | 0.73 | 0.91 | 1.42 | 2.34 | 0.0 | 10.2 |
| wsjf | TasNet | 1 | 1.53 | gLN | N | 0.71 | 0.96 | 1.53 | 3.19 | 0.1 | 15.2 |
| wsjf | TasNet | 1 | 1.53 | cLN | N | 0.71 | 0.97 | 1.53 | 3.33 | 0.1 | 16.0 |
| wsjf | TasNet | 1 | 1.53 | cLN | Y | 0.71 | 0.95 | 1.53 | 2.74 | 0.1 | 12.4 |
| wsjf | uNet | 1 | 0.32 | n/a | N | 0.71 | 0.95 | 1.53 | 2.81 | 0.1 | 13.4 |

这些原始数字支持以下限定结论：

1. **非因果 TasNet 与 uNet 的同任务比较**：在 mix、ssn、wsjf 三组增强测试中，Table 1 的非因果 TasNet processed 指标高于 uNet 的对应行；其中 wsjf 的 cLN 非因果行达到 STOI 0.97、PESQ 3.33、SI-SDR 16.0 dB。
2. **cLN 本身不是主要损失来源**：在非因果卷积下，gLN 与 cLN 的差别很小，部分指标相同或略变；这将质量变化更多归因于 convolution 的 future context，而不是单独归因于 cLN。
3. **因果化的代价依赖噪声类型**：mix 的 cLN non-causal 到 cLN causal 为 STOI 0.93→0.89、PESQ 2.63→2.17、SI-SDR 12.3→9.7；ssn 为 0.93→0.89、2.57→2.11、11.4→9.1；wsjf 为 0.97→0.95、3.33→2.74、16.0→12.4。按表中数值相减，竞争说话人场景的 PESQ/SI-SDR 下降更明显。
4. **不要把“TasNet 超过 uNet”泛化到 causal 版本**：Table 1 中 causal TasNet 的 mix/ssn/wsjf processed SI-SDR 分别为 9.7/9.1/12.4 dB，而 uNet 对应为 11.1/10.2/13.4 dB；论文 conclusion 的“consistently outperforms”应理解为论文所比较的整体 TasNet 结果，不能当作严格低时延 causal 优势的证明。

### 4.4 Table 2：最关键的 window/hop 消融

| Test set | Model | # target | Window/hop (ms) | Norm | Causal | STOI noisy | STOI processed | PESQ noisy | PESQ processed | SI-SDR noisy | SI-SDR processed |
|---|---|---:|---:|---|:---:|---:|---:|---:|---:|---:|---:|
| 2bal | TasNet | 2 | 2/1 | gLN | N | 0.70 | 0.93 | 1.50 | 2.66 | 0.0 | 12.4 |
| 2bal | TasNet | 2 | 64/32 | gLN | N | 0.70 | 0.79 | 1.50 | 1.71 | 0.0 | 4.8 |
| 2bal | TasNet | 2 | 64/1 | gLN | N | 0.70 | 0.93 | 1.50 | 2.78 | 0.0 | 12.5 |
| ssn | TasNet | 1 | 2/1 | gLN | N | 0.73 | 0.93 | 1.42 | 2.60 | 0.0 | 11.4 |
| ssn | TasNet | 1 | 64/32 | gLN | N | 0.73 | 0.87 | 1.42 | 2.07 | 0.0 | 8.2 |
| ssn | TasNet | 1 | 64/1 | gLN | N | 0.73 | 0.93 | 1.42 | 2.60 | 0.0 | 11.0 |

关键消融结论是：64/32 比 2/1 明显差，但把 hop 从 32 ms 改回 1 ms 后，64/1 在 2bal 上的 processed STOI/PESQ/SI-SDR 为 0.93/2.78/12.5，在 ssn 上为 0.93/2.60/11.0，基本恢复短窗系统的表现。这个对低时延方向的价值在于：**短 hop 的代价和收益不能由 window length 单独推断；hop 是更敏感的别名/采样控制旋钮。**

### 4.5 内域 overlap 与人声保留的因果性账本

| 观察 | PDF 证据 | 可以支持什么 | 不能支持什么 |
|---|---|---|---|
| TasNet inner-domain 与 STFT overlap | Figure 2，PDF 第 3 页；竞争说话人、ssn 的 overlap 降低更明显 | learned representation 让目标/噪声更可分的机制解释 | 不能直接证明弱语音未被抑制，也不能替代 F0/formant 或 false-suppression |
| wsjf 的非因果指标高 | Table 1：processed STOI/PESQ/SI-SDR 为 0.97/3.33/16.0（cLN non-causal） | 竞争说话人下的总体增强质量较高 | 不等于目标说话人保留率、主观自然度或 causal 可用性 |
| wsjf 因果下降较大 | Table 1：causal 为 0.95/2.74/12.4 | future context 对非平稳干扰的帮助很大 | 不知道下降来自哪一层、padding、状态或训练分布 |
| 低 SNR | 训练 SNR 从 [-10, 10] dB 均匀采样，测试只给 0 dB 汇总 | 有低 SNR 训练覆盖 | 没有按更细 SNR 桶分层结果，无法审计不同低 SNR 下的人声保留 |

### 4.6 因果性、复杂度与 latency ledger

| 项目 | PDF 明示内容 | 证据边界 |
|---|---|---|
| 采样率 | 8 kHz | 只覆盖窄带；不能外推 16/48 kHz |
| window/hop | Table 2 有 2/1、64/32、64/1 ms | window/hop 消融不是端到端设备测量 |
| causal 变体 | cLN + causal convolutions | 论文称 essentially causal；没有逐层 dependency certificate |
| causal latency 线索 | latency 由 frame hop 决定，多数实验为 1 ms | 不能写成 capture-to-playback ≤1 ms |
| non-causal latency | non-causal convolution 的 look-ahead 依赖 kernel lengths，形成 fixed system latency | 未给出具体 look-ahead 数值或 padding 图 |
| gLN | 使用 entire signal | 明确 non-causal |
| receptive field | Table 1 1.53 s；Section 2.1 15,310 samples | 与算法 latency 不同，且两种 PDF 表述相互不一致 |
| 模型规模 | TasNet 3.5M parameters；uNet 3.5M | 只有参数量；没有 MAC/s、FLOPs、峰值 RAM/SRAM |
| 运行时 | 未报告 CPU/GPU、batch=1、RTF、p50/p95/p99 | 无法判断每个 hop 是否能稳定通过 deadline |
| I/O 与端到端 | 未报告 ADC/DMA、input/output buffer、DAC、capture-to-playback | 不能声称设备级 ultra-low-latency |
| streaming 恢复 | 未报告 warm-up、state reset、长流、underrun/overrun、bypass/recovery | 部署证据缺失 |

因此，“1 ms”在本文中最多是 causal configuration 的 frame-hop / system-latency 线索；“2 ms”是 Table 2 的短 window 配置。论文没有把模型计算时间、I/O buffer、端到端延迟或 deadline miss 纳入实验。

## 5. 这个方向还剩什么问题没解决？（future work / limitation）

### 5.1 论文直接留下的开放点

论文没有单独的 future-work 章节，但 conclusion 和 Section 4.4 明确留下：

1. **aliasing 只是 conjecture**：作者建议让 separator 跨 inner-domain rows 操作，或参考后续允许跨 rows 的 TasNet 改进，以便访问完整 signal 并修正 aliasing；本文没有做 anti-aliasing 或 cross-row 的直接对照。
2. **大 hop 的性能风险**：64/32 在 2bal 与 ssn 上都明显退化，说明低时延不能只看 window size；仍需把 hop、encoder stride、anti-aliasing 和实时计算统一设计。
3. **因果上下文损失**：cLN + causal convolution 在竞争说话人上尤其掉点，说明非平稳噪声的抑制需要 future context 或更强的历史状态建模。
4. **表征解释还不完整**：inner-domain overlap 能解释可分性，但没有给出学习滤波器、频率覆盖、噪声误抑制或波形伪影的细粒度审计。

### 5.2 对低时延/人声保留方向的隐藏缺口

- **严格因果边界**：没有逐层 padding、decoder overlap/add、归一化统计、state 和最新可读样本说明；paper_claimed_causal 不能直接当作 strict_causal。
- **延迟账本不闭环**：没有真实硬件 runtime、RTF、p99、输入输出 buffer、ADC/DAC、deadline miss、underrun/overrun 和恢复策略。
- **人声保留未独立量化**：没有 false-suppression、SIG/BAK/OVL、SPP calibration、ASR WER、F0/formant/prosody continuity、voiced energy 或听感测试。
- **SNR 结果没有分层**：训练覆盖 [-10,10] dB，但测试只报告 0 dB；低 SNR 的关键区间无法逐层比较。
- **窄带与合成数据**：实验 downsample 到 8 kHz，使用 WSJ0 与合成噪声/混合；16 kHz/48 kHz、真实设备、真实房间和未见噪声没有在本文验证。
- **wsjf 目标人群受限**：为避免 uNet 的 permutation 问题，wsjf 只用 male clean target；这使该行不能直接代表任意性别组合的通用增强。
- **复杂度证据不够**：3.5M 参数不是 MAC/s、FLOPs 或峰值内存；相近参数量也不等于相同端侧 deadline 风险。
- **causal TasNet 与 uNet 的比较要谨慎**：uNet 在 Table 1 中是 non-causal；把 causal TasNet 与它直接比较会混入 future-context 差异。

### 5.3 可复用的研究机会

本论文最适合迁移的原则是：**在 learned waveform pipeline 中，把 hop/aliasing、future context 和目标语音保留作为同一组约束审计，而不是只追求一个平均 PESQ。** 后续复现应至少补齐：

1. 8/16 kHz 的明确 encoder stride、window、hop、padding、state 和最新可读输入样本；
2. batch=1 流式 p50/p95/p99、RTF、峰值内存、deadline miss 与长流 reset；
3. -10/-5/0/5 dB、竞争说话人、babble、瞬态和未见噪声分层；
4. false-suppression、语音可懂度/质量 trade-off，以及 F0、formant、prosody 或 ASR 结果；
5. anti-aliasing、跨 row separator、gain floor 或保守抑制机制的独立消融。

## 6. 本论文在库中的位置关联（cross-reference matrix）

| 关系 | 库中页面 | 关联、继承与边界 |
|---|---|---|
| 前身/基石 | [[wiki/entities/Conv-TasNet]]；[[wiki/sources/2019/Conv-TasNet 2019]] | 本文不是另造 TasNet，而是把 learned encoder + TCN + learned decoder 从多说话人分离迁移到 I=1 增强，并在低 hop 条件下重新审计 |
| 前身/方法背景 | [[wiki/sources/2020/Real Time SE Waveform 2020]] | 同属波形域实时增强线索；现有笔记只记录“Conv-TasNet 实时化”方向，不能替代本论文的 Table 1/2 证据 |
| 同分支竞品 | [[wiki/entities/RNNoise]] | RNNoise 代表小 GRU + DSP/STFT 的极低复杂度路线；本文代表 learned waveform inner-domain 路线；两篇没有同条件表格，不能直接横比 |
| 同分支竞品 | [[wiki/sources/2020/PercepNet 2020]]；[[wiki/sources/2020/DCCRN 2020]] | 分别代表感知驱动的实时增强与复数频域增强；本文未直接比较，关联仅用于方法路线定位 |
| 后续/扩展 | [[wiki/sources/2020/DPRNN 2020]] | 本文引用的后续方向允许 separator 跨 inner-domain rows 访问更完整 signal；可视为对固定 row-wise separator/aliasing 假说的直接架构回应 |
| 后续/同任务低时延 | [[wiki/sources/2021/DPCRN 2021]] | 双路径 CRN 关注单通道增强中的长上下文与复杂度；不是本文的直接续作，需按各自采样率、延迟和数据协议比较 |
| 低时延系统类比 | [[wiki_low_latency/sources/2023/GCFSnet 2023]]；[[wiki_low_latency/concepts/低比特率双耳特征链路]] | 两者都把低时延约束与质量一起看；GCFSnet 是多通道/双耳、延迟链路特征，On TasNet 是单通道 learned waveform，不能互换结果 |
| 跨分支概念类比 | [[wiki_array/concepts/空间混叠 Spatial Aliasing]] | 两者都使用 aliasing 词汇，但本文讨论的是 inner-domain rows 的时间 decimation/卷积别名，不是阵列空间混叠；仅作术语对照 |
| 跨分支概念类比 | [[wiki_array/concepts/波束成形 Beamforming]] | 均体现“表示/滤波器决定目标与干扰可分性”的思想，但 On TasNet 没有多麦空间滤波；该关联为 ⚠️ 疑似关联，需用户确认 |
| 库内导航 | [[wiki_low_latency/overview]]；[[wiki_low_latency/index]] | 本页应作为“causal learned-filterbank / hop aliasing / 单通道增强”分支的证据页；index、overview 和 log 未在本任务中修改，待主 agent 处理 |

## 7. 一句话总结“江湖地位”

> **2021 | 单通道低时延语音增强 | 把 TasNet 的 learned inner-domain + TCN 体系验证到单说话人噪声抑制，并用 window/hop 消融指出 1 ms hop 比 window length 更关键、且可能受 aliasing 控制 → 成为 causal learned-waveform 增强的实证基线，但真实设备 deadline、RTF 和人声保留证据仍未闭环。**

### 参考资料

- [arXiv abstract page](https://arxiv.org/abs/2103.14882)
- [Local PDF](../../../raw/papers/low_latency_causal_se/2103.14882.pdf)
- [[wiki_low_latency/entities/On-TasNet]]
- [[wiki_low_latency/concepts/2103.14882-causal-tasnet]]
- [[wiki/entities/Conv-TasNet]]
- [[wiki/concepts/可学习编码器 Learnable Encoder]]
- [[wiki/concepts/时序卷积网络 TCN]]
- [[wiki/concepts/语音增强评价指标]]
