---
title: GTCRN
type: entity
created: 2026-09-27
updated: 2026-09-27
tags:
  - speech-enhancement
  - single-channel
  - tf-domain
  - complex-ratio-mask
  - ultralight
  - 23.7k-parameters
  - subband
  - erb-filterbank
  - band-merging
  - band-splitting
  - grouped-rnn
  - grnn
  - dual-path-rnn
  - grouped-dprnn
  - grouped-temporal-convolution
  - shufflenet
  - subband-feature-extraction
  - temporal-recurrent-attention
  - dpcrn-backbone
  - paper-claimed-causal
  - unreported-center
  - 16ms-hop
  - latency-ledger-gap
  - macs-not-latency
  - nominal-macs
  - vctk-demand
  - dns3
  - icassp-2024
sources:
  - [[wiki_low_latency/sources/2024/GTCRN 2024]]
related:
  - [[wiki_low_latency/concepts/gtcrn-2024-ultralight-subband-grouped-dprnn]]
  - [[wiki_low_latency/entities/DPCRN]]
  - [[wiki_low_latency/concepts/2107.05429-dual-path-recurrent-context]]
  - [[wiki_low_latency/entities/FastEnhancer]]
  - [[wiki_low_latency/sources/2025/FastEnhancer 2025]]
  - [[wiki_low_latency/entities/RT-Tango]]
  - [[wiki_low_latency/sources/2026/RT-Tango 2026]]
  - [[wiki_low_latency/entities/PSMSE]]
  - [[wiki_low_latency/sources/2026/PSMSE 2026]]
  - [[wiki_low_latency/entities/DeepFilterNet2]]
  - [[wiki_low_latency/entities/PercepNet]]
  - [[wiki_low_latency/entities/DCCRN]]
  - [[wiki_low_latency/entities/D-GRU]]
  - [[wiki_low_latency/entities/Skip-DPCRN]]
  - [[wiki_low_latency/entities/LaCo-SENet]]
  - [[wiki_low_latency/entities/RT-SEMamba]]
  - [[wiki_low_latency/entities/FSB-LSTM]]
  - [[wiki_low_latency/sources/2026/Early Exit Compute-Matched 2026]]
  - [[wiki_low_latency/entities/Early-Exit-Conv-FSENet]]
  - [[wiki_low_latency/concepts/2509.21867-speed-optimized-streaming-design]]
  - [[wiki_low_latency/concepts/2609.29867-compute-matched-dynamic-depth]]
  - [[wiki_low_latency/concepts/2408.12425-dynamic-gated-rnn]]
  - [[wiki_low_latency/concepts/2207.11108-inference-skipping-parallel-rnn]]
  - [[wiki_low_latency/concepts/2304.08707-full-sub-band-modeling]]
  - [[wiki_low_latency/concepts/严格因果与算法延迟]]
  - [[wiki_low_latency/concepts/低时延前端与延迟账本]]
  - [[wiki_low_latency/concepts/低 SNR 人声保留评估]]
  - [[wiki/sources/2026/muNet 2026]]
---

# GTCRN

## 定义

**GTCRN**（Grouped Temporal Convolutional Recurrent Network）是本地论文 [[wiki_low_latency/sources/2024/GTCRN 2024]]（ICASSP 2024，pp. 971–975）提出的**超轻量单通道语音增强模型**，规模为 **23.7 K 参数 / 39.6 MMACs per second**（论文声称值）。

它的骨架是 **DPCRN [3, 16]**，在此基础上做三处"分组式"压缩，再补两个模块把质量找回来：

1. **Band Merging / Band Splitting（BM / BS）**——只在 **2 kHz 以上**按 **ERB 尺度**把频带从 **192 压到 64**，**2 kHz 以下的 65 个低频带原样保留**（因为低频含基频与共振峰，是语音保真的关键）。总特征维数 **192 → 129**；
2. **G-DPRNN**（Grouped DPRNN）——把 **GRNN [18]** 的分组循环与 **DPRNN [7]** 的双路径拼起来：组数固定为 **2**，**intra-frame 用分组双向 GRU**（单帧内、沿频率轴），**inter-frame 用分组单向 GRU**（沿时间轴，论文称这是因果性的支柱）；
3. **GT-Conv**（Grouped Temporal Convolution）——**ShuffleNetV2 [17]** 的 unit（channel split → 两路 → concat → channel shuffle）+ **2D pointwise conv（P-Conv2D）** + **2D 膨胀深度可分离卷积（DD-Conv2D）**，dilation 取 **1 / 2 / 5**、kernel **(3, 3)**。

两个**可选**补偿模块（论文自己提出的部分）：

4. **SFE**（Subband Feature Extraction，§2.4）——沿**频率轴**做 `unfold`（k=3），把相邻子带的关系从"频率维度"搬进"channel 维度"，使后续的 pointwise 卷积可以一次性看到跨子带的信息；
5. **TRA**（Temporal Recurrent Attention，§2.5）——**平方 → 平均池化 → GRU（通道数翻倍）→ FC（恢复通道）→ sigmoid → 沿频率轴复制 → 乘性掩蔽**。它是一个**跨帧有记忆**的能量重标定模块。

输出是 **tanh 约束在 $[-1,1]$ 的复数比率掩蔽（CRM [19]）**的实部与虚部，作用在带噪复数谱上。

> [!note] 这个实体是本库"超轻量"档的**锚点**，而不是"低时延"档的候选
> 本库绝大多数条目（[[wiki_low_latency/entities/LaCo-SENet]]、[[wiki_low_latency/entities/RT-SEMamba]]、[[wiki_low_latency/entities/FSB-LSTM]]）优化的轴是**算法延迟与因果性**（约 2 ms 档、逐层 padding 分配式）。
> **GTCRN 优化的轴是参数量与 MACs**——论文的 motivation 是「SOTA SE 从 several GMACs 到 tens of GMACs，无法部署到耳机/助听器」，**全文没有一个延迟数字**，也没有提算法延迟、RTF、目标硬件、量化。
> 因此它的定位是：**超轻量纵轴上的参照点**。它被库内四篇同时引用（[[wiki_low_latency/sources/2025/FastEnhancer 2025]]、[[wiki_low_latency/sources/2026/RT-Tango 2026]]、[[wiki_low_latency/sources/2026/PSMSE 2026]]、[[wiki/sources/2026/muNet 2026]]）——**锚点数值一错，四条引用链一起偏**（见下方 [!contradiction]）。

> [!important] 论文自己提出的只有两个模块——本页必须把这条边界划清
> 逐项对照：**ERB 频带压缩**不是新想法；**ShuffleNetV2 的 channel split / shuffle** 不是新的；**GRNN 的分组循环**不是新的；**DPRNN 的双路径**不是新的；**时间维注意力**在与它对照的 TA [24] 里已有。
> **本文真正原创的是 SFE（§2.4）与 TRA（§2.5）两个模块**，以及把它们与前述全部部件**组装进 DPCRN 并压到 23.7 K** 的工程。
> **本库记录时不得把 ERB / grouped conv / GT-Conv 读成本文原创。** 这不是贬低——"把已知部件组装到一个新量级"本身就是贡献（Table 1 显示 TRA 有效），但归属必须准确。

## 证据

| 属性 | 本地 PDF 证据 |
|---|---|
| 任务 | 单通道语音增强；面向「低功耗端侧设备，例如耳机与助听器」（p.1 §1 逐字 `practical deployment in end devices with low power consumption requirements, e.g., earphones and hearing aids`） |
| 发表状态 | **已出版会议论文**：p.1 页脚版权行 `979-8-3503-4485-1/24/$31.00 ©2024 IEEE` + `ICASSP 2024` + DOI `10.1109/ICASSP48485.2024.10448310` + 页码 **971–975** |
| arXiv | **无**（本库多数 low_latency 条目是 arXiv 预印本，**本篇是例外**）⇒ 只能以本地 PDF 的一手证据为准 |
| backbone | 「Using **DPCRN [3, 16]** as the backbone, various strategies are utilized to significantly shrink the model.」；p.1 §1。[3] = DPCRN 原文（Le 等，Interspeech 2021）；[16] = Inference Skipping（Le 等，TASLP 2022，即本库 [[wiki_low_latency/entities/Skip-DPCRN]]）。**两者共享作者 J. Lu** |
| 动机（算力落差） | 「Most SOTA SE models call for **substantial computational resources ranging from several GMACs to tens of GMACs**, making them **infeasible to be deployed on edge devices**」；p.1 §1 |
| 对前人方案的批评 | 「**with the exception of RNNoise, which is compact enough whereas suffers from limited performance**」——**同时否定两端**：PercepNet/DeepFilterNet/DPCRN-CF 仍太大，RNNoise 足够小但性能有限；p.1 §1 |
| ERB 压缩 | 「An **equivalent rectangular bandwidth (ERB) filter bank is used to reduce the redundancy of the input features**」；p.1 §1、§2.1。**只在 2 kHz 以上压**：192 → **64**，加 **65** 个低频带 ⇒ **129** 维 |
| G-DPRNN | grouped convolution [17] + grouped RNN [18]；**组数 = 2**；p.2 §2.2 |
| intra / inter 方向 | 「We use **grouped bidirectional GRU for intra-frame modeling**, and **grouped unidirectional GRU for inter-frame modeling**, **so that the causality of the model can be guaranteed**.」；p.2 §2.2——**全文唯一的因果性表述** |
| GT-Conv | ShuffleNetV2 unit [17]：channel split → 两路 → concat → **channel shuffle**；含 **P-Conv2D**（2D pointwise）与 **DD-Conv2D**（2D 膨胀深度可分离），**dilation 1 / 2 / 5**、**kernel (3, 3)**；p.2 §2.3、Fig. 2 |
| SFE（原创） | **频率轴 `unfold`，k = 3**，把子带关系搬进 channel 维；p.2 §2.4、Fig. 3 |
| TRA（原创） | **Square → Avg Pool → GRU（通道翻倍）→ FC → Sigmoid → 沿频率轴复制 → 乘性掩蔽**；p.2 §2.5、Fig. 4 |
| 输出 | **tanh 约束在 $[-1,1]$ 的 CRM**（实部与虚部）：「These values are interpreted as the real and imaginary parts of the estimated **complex ratio mask (CRM) [19]**」；p.2 §2.6 |
| STFT | **sqrt-Hanning 窗、32 ms、hop 16 ms、FFT 512**；p.3 §3.2 |
| 输入特征 | 带噪谱的**实部、虚部、幅度**在 channel 维拼接；p.2 §2 |
| 损失 | Eq. (1)：$\mathcal L=\alpha\mathcal L_{\text{SISNR}}(\tilde s,s)+(1-\beta)\mathcal L_{\text{mag}}(\tilde S,S)+\beta\left(\mathcal L_{\text{real}}(\tilde S,S)+\mathcal L_{\text{imag}}(\tilde S,S)\right)$，$\alpha=0.01$、$\beta=0.3$；Eq. (2)–(5) 的压缩指数 **0.3**（mag）、单位化指数 **0.7**（real/imag）；p.2–p.3 §2.6 |
| 优化器 | **Adam [23]**，初始 lr **0.001**，验证损失**连续 5 epoch 不降则减半**；p.3 §3.2 |
| batch size | VCTK-DEMAND **4**；DNS3 **16**；p.3 §3.2 |
| DNS3 训练 | 每次 chunk 到 **8 s**，每 epoch 随机取 **40,000** 对；p.3 §3.2 |
| 训练总 epoch | **未报告** |
| 随机种子 / 方差 | **未报告** |
| 参数与算力（声称） | **23.7 K 参数 / 39.6 MMACs per second**，三处一致（Abstract、§3.2、§4）；对应 Table 1 末行 SFE✓+TRA✓（**23.67 K / 39.63 M/s**）——**内部自洽** |
| 消融数据集 | **DNS3 的约 100 小时子集**（Table 1）；p.3 §3.3.1——**不是**全量 720,000 对 |
| VCTK-DEMAND 结果 | **SISNR 18.83 / PESQ 2.87 / STOI 0.940**（Table 2）；p.4 §3.3.2 |
| DNS3 blind 结果 | **P.808 3.44 / BAK 3.90 / SIG 3.00 / OVRL 2.70**（Table 3）；p.4 §3.3.2 |
| 开源代码 | `https://github.com/Xiaobin-Rong/gtcrn`（§3.3.2 正文给出）；**本页未克隆核实**（`evidence_policy: local_pdf_only`） |
| 论文自我定位用词 | `competitive`（Abstract、§4）与 `surpasses ... in terms of SISNR and PESQ`（§3.3.2）——**不是** `state-of-the-art` |
| Limitation / Future work | **全文无此章节**；§4 结论只有 5 句总结，后 3 句是致谢 |

> [!warning] 上表里有一组**"只在用词上诚实、不在数据上诚实"**的反差
> - 好的一面：Abstract/结论用 `competitive` 而非 `SOTA`；
> - 不好的一面：**没有 limitations、没有 future work**，且表 2/3 有大量空格子（RNNoise/PercepNet 的 SISNR/STOI、S-DCCRN 的 MACs 与 BAK/SIG/OVRL）。
> 这是一篇典型的 4 页 ICASSP 短文：**贡献是"一个极小的可用模型"，而不是"一套完整的评估"**。本库记录时必须把这两者分开。

## 架构与状态

![[wiki_low_latency/assets/gtcrn_2024/gtcrn-page2.png]]

> 图注：原论文第 2 页页面渲染，用于核对 **Fig. 1（整体架构）+ Fig. 2（GT-Conv block）+ Fig. 3（SFE）+ Fig. 4（TRA）** 与 §2.1–§2.4 前半。**Fig. 1** 是一条 U 形结构：左侧 **Encoder**、右侧 **Decoder**，顶部标 `BM` / `BS`，中部标 `G-DPRNN`，`SFE` 在 encoder/decoder 之间的旁路上。**注意**：抽取文本把 Fig. 1 的模块名平铺成两行（`BM / Conv / GT-Conv / ... / G-DPRNN / BS / DeConv / ... / SFE`），**无法从文本流判断 skip connection 的连线方式**；渲染图可看出 U 形对称结构与 BM/BS 的位置，但连线细节在 150 dpi 下不足以逐条确认。**Fig. 2** 是 GT-Conv block 框图（`Channel Split` → 两路 → `Concat` → `Channel Shuffle`，含 `P-Conv2D`、`DD-Conv2D`、`BN PReLU`、`SFE`、`TRA`）。**Fig. 3** 是 SFE 的 `Unfold` → `Reshape` 两步示意（标注三个张量尺寸，字体过小，本页未能从渲染图读出字母符号）。**Fig. 4** 是 TRA 的 `Square → Avg Pool → GRU → FC → Sigmoid → ⊗` 流程与 `Aggregation` / `Generation` 两个阶段标注。图片为 PDF 页面复制，不是 AI 重画。

~~~text
┌────────────────────────────── GTCRN（backbone = DPCRN）──────────────────────────────┐
│                                                                                      │
│  带噪波形 ──► STFT（sqrt-Hanning 窗 32 ms / hop 16 ms / FFT 512）                     │
│       │          │                                                                   │
│       │          └──► [ Re, Im, |X| ] 沿 channel 维拼接 ──► 192 带                       │
│       │                          │                                                    │
│       │                     ┌────┴─────┐  2 kHz 以上按 ERB 压 192 → 64                │
│       │                     │   BM     │  2 kHz 以下 65 带【原样保留】                  │
│       │                     └────┬─────┘  ⇒ 【129 维】                                 │
│       │                          │                                                    │
│       │                     ┌────┴─────┐  Encoder：Conv2D（频率轴下采样）              │
│       │                     │  Encoder │                                              │
│       │                     └────┬─────┘                                              │
│       │                          │                                                    │
│       │        ┌─────────────────┴──────────────────┐                                 │
│       │        │            G-DPRNN（组数 = 2）      │                                 │
│       │        │  ┌──────────────────────────────┐  │                                 │
│       │        │  │ intra-frame：分组【双向】GRU  │  │  ← 单帧内、沿频率轴双向            │
│       │        │  │              ↓                │  │    不跨时间帧 ⇒ 不破坏因果         │
│       │        │  │ inter-frame：分组【单向】GRU  │  │  ← 沿时间轴单向                    │
│       │        │  │              ↓                │  │    ★ 论文称此为保证因果性的支柱    │
│       │        │  │  GT-Conv × N                 │  │                                 │
│       │        │  │   ├─ ShuffleNetV2 unit       │  │  channel split → 两路 →          │
│       │        │  │   │   （split/shuffle）      │  │  concat → channel shuffle        │
│       │        │  │   ├─ P-Conv2D   （pointwise）│  │  k=(1,1)                         │
│       │        │  │   └─ DD-Conv2D  （dilated   │  │  k=(3,3)、d=1/2/5                │
│       │        │  │        depthwise separable） │  │                                  │
│       │        │  └──────────────────────────────┘  │                                 │
│       │        └─────────────────┬──────────────────┘                                 │
│       │                          │                                                    │
│       │                     ┌────┴─────┐  ┌──────┐  ┌──────┐  可选（Table 1 的两开关）   │
│       │                     │   SFE    │  │ TRA  │  │ ...  │                          │
│       │                     │unfold k=3│  │见下  │  │      │                          │
│       │                     └────┬─────┘  └──┬───┘  └──┬───┘                          │
│       │                          └───────────┴─────────┘                              │
│       │                          │                                                    │
│       │                     ┌────┴─────┐  Decoder：DeConv2D                           │
│       │                     │  Decoder │                                              │
│       │                     └────┬─────┘                                              │
│       │                          │                                                    │
│       │                     ┌────┴─────┐  BS：64 + 65 → 恢复 192 带                    │
│       │                     │    BS    │                                              │
│       │                     └────┬─────┘                                              │
│       │                          │                                                    │
│       │                          └──► tanh ⇒ CRM ∈ [-1,1]（实部 / 虚部）               │
│       │                                        │                                      │
│       └────────────────────────────────────────┴──► ⊙ 带噪复数谱 ──► iSTFT ──► 波形    │
└──────────────────────────────────────────────────────────────────────────────────────┘

TRA（§2.5, Fig. 4）——本库最关注的"补偿模块"
   特征 ──► Square ──► Avg Pool（时间轴）──► GRU（通道 ×2）──► FC（恢复通道）
                                                                    │
                                                                 Sigmoid
                                                                    │
                                          沿【频率轴】复制 ──► 乘性掩蔽 ──► 输出
   ★ 含 GRU ⇒ 掩蔽【跨帧有记忆】 ⇒ 与视觉的 SE-Block 同构，但多了时间上的递推

SFE（§2.4, Fig. 3）
   子带特征 X[f, c] ──► 沿【频率轴】unfold (k=3) ──► channel 维拼接
                       "把相邻子带的关系从频率维搬进 channel 维"
   ⇒ 后续 pointwise 卷积一次即可看到跨子带信息
~~~

> [!note] 架构上最值得记住的一点：**"分组"被同时用在三个正交的地方**
> | # | 分组轴 | 具体形式 | 组数 |
> |---|---|---|---|
> | 1 | **频带** | BM/BS 的 ERB 压缩（2 kHz 以上） | 192 → 64 |
> | 2 | **通道** | GT-Conv 的 ShuffleNetV2 channel split / shuffle | 2 路 |
> | 3 | **循环层** | G-DPRNN 的 GRNN 分组 | **2** |
>
> 三处互不重叠、可独立开关（频带压缩是必经路径，通道分组与循环分组是结构常数，SFE/TRA 是可选开关）。**这是本文的叙事核心**：压缩本身不新（ERB、grouped conv、grouped RNN 都是既有工作），**新颖点在于把三种分组组装进同一个 DPCRN 并压到 23.7 K**。
> 值得注意的是 §2.2 的原文措辞是「Grouped convolution [17] and grouped RNN [18] are employed to **decrease the model complexity**」，而 ERB 的作用被独立描述为「**reduce the redundancy of the input features**」——**论文把"提特征冗余"与"降模型复杂度"分开表述**，这个区分在本页的"参数与算力"一节很重要。

> [!important] 一条容易读错的边界：**intra-frame 用双向 GRU，并不破坏因果**
> 论文原文是 `grouped bidirectional GRU for **intra-frame** modeling, and grouped unidirectional GRU for **inter-frame** modeling, so that the causality of the model can be guaranteed`。
> **intra-frame 双向是"单帧内、沿频率轴"的双向**——它不跨时间帧，因此**不引入未来信息**；反向的 look-ahead 只发生在**同一帧的不同频点之间**，而整帧在 STFT 完成后就已经全部可得。
> **因此这条声明在结构上是合理的**（本页判定）。本库不应因为它"用了 bidirectional GRU"就判为非因果——**要判非因果，需要看 inter-frame 的方向与卷积 padding**（见下）。
> 这也解释了论文为什么敢用 `so that` 这个强因果词：**它只对双向/单向这一处讲了因果，而把卷积 padding、STFT center 留白了**（见"低时延账本"）。

## Table 1 消融表速查（7 行 × 8 列，逐格核对 `gtcrn-page4.png`）

**Table 1 标题**：Ablation study results on DNS3 test set.（数据集为**约 100 小时 DNS3 子集**，§3.3.1）

| SFE | TA | TRA | Para. (K) | MACs (M/s) | SISNR | PESQ | STOI |
|---|---|---|---|---|---|---|---|
| - | - | - | - | - | 3.92 | 1.30 | 0.789 |
| ✗ | ✗ | ✗ | 13.35 | 33.91 | 9.87 | 1.87 | 0.834 |
| ✗ | ✓ | ✗ | 14.84 | 34.00 | 10.00 | 1.89 | 0.838 |
| ✗ | ✗ | ✓ | 21.65 | 34.47 | 10.25 | 1.91 | 0.840 |
| ✓ | ✗ | ✗ | 15.37 | 39.07 | 10.10 | 1.90 | 0.838 |
| ✓ | ✓ | ✗ | 16.86 | 39.16 | 10.29 | 1.92 | 0.841 |
| ✓ | ✗ | ✓ | **23.67** | **39.63** | **10.39** | **1.94** | **0.844** |

> [!question] 第 1 行（全 `-`）是什么？——渲染图上**没有行标签**，本页不代填
> 该行 `SFE / TA / TRA / Para. / MACs` 五列全为 `-`，只有 **SISNR 3.92 / PESQ 1.30 / STOI 0.789**。
> 数值特征上它**几乎肯定是未处理的 noisy 混合**：① 参数量与算力列用 `-` 表示"不是模型"；② PESQ 1.30 / STOI 0.789 是典型噪声污染水平；③ DNS3 是**混响 + 噪声**数据，noisy 的 SI-SNR 只有 3.92 dB 属合理范围（对照 VCTK-DEMAND 的 noisy 是 8.45 dB）。
> **但论文只给了 5 个 `-`，没有写 "Noisy"。本页记录为「极可能是 noisy baseline，但论文未标注」。** 同类问题在 Table 2 里不存在（那里明确写了 `Noisy`）。

**三组关键对照（全部写成数值对，差值留给读者）**：

| 对照 | 变的是谁 | Para. (K) | MACs (M/s) | SISNR | PESQ | STOI |
|---|---|---|---|---|---|---|
| **A：TRA vs TA**（✗/✓/✗ → ✗/✗/✓） | TA 换 TRA | 14.84 → 21.65 | 34.00 → 34.47 | 10.00 → 10.25 | 1.89 → 1.91 | 0.838 → 0.840 |
| **B：TRA vs 无注意**（✗/✗/✗ → ✗/✗/✓） | 加 TRA | 13.35 → 21.65 | 33.91 → 34.47 | 9.87 → 10.25 | 1.87 → 1.91 | 0.834 → 0.840 |
| **C：SFE vs 无 SFE**（✗/✗/✗ → ✓/✗/✗） | 加 SFE | 13.35 → 15.37 | 33.91 → 39.07 | 9.87 → 10.10 | 1.87 → 1.90 | 0.834 → 0.838 |

**TRA 与 SFE 的双坐标并列（本页从渲染图重算，论文未提供）**：

| 模块 | MACs 增量 | 参数增量 | SISNR 增量 | PESQ 增量 |
|---|---:|---:|---:|---:|
| **TRA**（✗/✗/✗ → ✗/✗/✓） | 33.91 → 34.47 = **+0.56 M/s** | 13.35 → 21.65 = **+8.30 K** | 9.87 → 10.25 = **+0.38** | 1.87 → 1.91 = **+0.04** |
| **SFE**（✗/✗/✗ → ✓/✗/✗） | 33.91 → 39.07 = **+5.16 M/s** | 13.35 → 15.37 = **+2.02 K** | 9.87 → 10.10 = **+0.23** | 1.87 → 1.90 = **+0.03** |

> [!important] 这张双坐标表是 Table 1 最值得记住的一组数——**它是一个双向 trade-off，不是单向优劣**
> - **MACs 代价**：TRA `+0.56 M/s` vs SFE `+5.16 M/s`（比值 $5.16/0.56 = 9.2$）；
> - **参数代价**：TRA `+8.30 K` vs SFE `+2.02 K`（比值 $8.30/2.02 = 4.1$）；
> - **质量增益**：SISNR 上 TRA `+0.38` vs SFE `+0.23`；PESQ 上 `+0.04` vs `+0.03`。
>
> **即：TRA 用约 1/9 的 MACs 换到更大的 SISNR 增益，但付出了约 4 倍的参数。**
> **论文的措辞是 `our proposed TRA outperforms TA with a very limited increment in computational resources`（只与 TA 比）与 `The advantages of SFE are also evident in Table 1`（未给量化）——论文回避了 TRA vs SFE 的 MACs/参数双坐标对照。** 本页补上这一组。
> **口径提醒**：Table 1 的参数增量是**整表差值**，论文**未明确 `+8.30 K` 是否全部属于 TRA 自身权重**（可能含全连接/归一化的连带变化）。

**TA 是本篇唯一"内部对照"的对照臂，但它几乎是个黑箱**：

> [!question] TA [24] 的结构**全文未描述**
> 论文只写了 `compare our TRA against time-dimension attention (TA) proposed in [24]`（[24] = Zhang 等，ICASSP 2022, pp. 7852–7856），**没有给出** TA 的结构、它与 TRA 的结构差异（池化轴？有没有 GRU？掩蔽维度？）、以及是否用了 [24] 的官方实现。
> Table 1 显示 TA 是"性价比最低"的模块（相对 baseline：MACs `+0.09 M/s`、参数 `+1.49 K`、SISNR `+0.13`、PESQ `+0.02`），但**在不知道 TA 结构的情况下，本库无法判断这个结论是对"时间维注意力"这一类的评价，还是仅对 [24] 这一个具体实现的评价**。
> 记录为**对照臂描述不足**——这是本篇消融设计上的一个真实弱点。

**两开关同时打开是否可加？（本页推算）**：

| 组合 | SFE | TRA | SISNR | 相对 baseline（9.87）的增量 |
|---|---|---|---|---|
| baseline | ✗ | ✗ | 9.87 | — |
| 只 SFE | ✓ | ✗ | 10.10 | **+0.23** |
| 只 TRA | ✗ | ✓ | 10.25 | **+0.38** |
| **同时** | ✓ | ✓ | **10.39** | **+0.52** |
| 单独之和 | — | — | — | **+0.61** |

> [!question] SISNR 上呈现**次可加性**（+0.52 < +0.61，差 0.09），PESQ 上**不呈现**（+0.03 + +0.04 = +0.07 vs 实测 +0.07）——论文未讨论
> SFE 把**频率维**的子带关系搬进 channel 维，TRA 沿**时间轴**做能量重标定，**两者作用的轴不同**，按理应当近似可加。
> 一个**可能是**的原因（本页假设，未验证）：在 SFE ✓ 时特征已被重塑，**TRA 的时序池化所统计的"能量"分布已经改变**（channel 语义变了）。论文没有讨论，也没有做交叉验证实验。
> **并且：0.09 的 SISNR 差值在无种子、无方差的情况下，本库无法判断它是否显著。**

## 结果表（Table 2 / Table 3，逐格核对 `gtcrn-page4.png`）

![[wiki_low_latency/assets/gtcrn_2024/gtcrn-page4.png]]

> 图注：原论文第 4 页页面渲染，用于核对 **Fig. 5 + Table 1 + Table 2 + Table 3 + §3.3.1 + §3.3.2 + §4 + §5**。**Fig. 5** 是 2 行 × 4 列的 DNS3 频谱图（纵轴 `0/1/2/5 kHz`、横轴 `0/1/2/3 s`），上标 `(a) Noisy / (b) Enhanced by RNNoise / (c) Enhanced by GTCRN / (d) Clean`，下标 `(e)(f)(g)(h)` 同序。**Table 1** 标题 "Ablation study results on DNS3 test set."，8 列 7 行（第 1 行全 `-`），渲染图上可见 7 行被 **2 条横向分隔线分成 3 段**，与 SFE 列的 `✗✗✗/✓✓✓` 分组吻合。**Table 2** 标题 "Performance on VCTK-DEMAND test set."，6 行。**Table 3** 标题 "Performance on DNS3 blind test set."，4 行，表头双层（`DNSMOS-P.808` 单列 + `DNSMOS-P.835` 下挂 `BAK / SIG / OVRL`）。**RNNoise 行带脚注上标 `1`**，脚注在**本页页脚**：`Metrics are measured with source code provided at https://github.com/xiph/rnnoise/`。图片为 PDF 页面复制，不是 AI 重画。

### Table 2：VCTK-DEMAND test set（6 行）

| 模型 | Para. (M) | MACs (G/s) | SISNR | PESQ | STOI |
|---|---|---|---|---|---|
| Noisy | - | - | 8.45 | 1.97 | 0.921 |
| RNNoise (2018) | 0.06 | 0.04 | - | 2.29 | - |
| PercepNet (2020) | 8.00 | 0.80 | - | 2.73 | - |
| DeepFilterNet (2022) | 1.80 | 0.35 | 16.63 | 2.81 | **0.942** |
| S-DCCRN (2022) | 2.34 | - | - | 2.84 | 0.940 |
| **GTCRN (proposed)** | **0.02** | **0.04** | **18.83** | **2.87** | 0.940 |

> [!warning] Table 2 **不是完整矩阵**——四行有空格子，横比能力被结构性削弱
> | 模型 | Para. | MACs | SISNR | PESQ | STOI |
> |---|---|---|---|---|---|
> | RNNoise | ✓ 0.06 | ✓ 0.04 | **✗ 空** | ✓ 2.29 | **✗ 空** |
> | PercepNet | ✓ 8.00 | ✓ 0.80 | **✗ 空** | ✓ 2.73 | **✗ 空** |
> | DeepFilterNet | ✓ 1.80 | ✓ 0.35 | ✓ 16.63 | ✓ 2.81 | ✓ 0.942 |
> | S-DCCRN | ✓ 2.34 | **✗ 空** | **✗ 空** | ✓ 2.84 | ✓ 0.940 |
>
> **后果**：① RNNoise / PercepNet 无法在 SISNR / STOI 上与 GTCRN 比较——尽管 Abstract 声称 `surpasses RNNoise`，**可比的只有 PESQ 一项**（2.29 vs 2.87）；② S-DCCRN 无法在算力上与 GTCRN 比较，而它是表内唯一 PESQ 接近 GTCRN 的模型（2.84 vs 2.87）；③ §3.3.2 写 `surpasses other baseline models ... in terms of SISNR and PESQ`，但 **SISNR 实际只有 DeepFilterNet 一个可比对象**（16.63 vs 18.83）。
> **本库记录：`surpasses` 的主张在 SISNR 上只有 1 个可比对象；在 STOI 上则不成立**（见下）。

> [!note] 表内最硬的一条事实：**GTCRN 与 RNNoise 的 MACs 完全相同**
> GTCRN **0.02 M 参数 / 0.04 G MACs**；RNNoise **0.06 M 参数 / 0.04 G MACs**。
> 即 **MACs 相同、参数量约为 RNNoise 的 1/3**，而 **PESQ 2.87 vs 2.29**。
> **这是本篇最干净的对照**（同算力量级、同数据集、同指标），也是 Abstract `surpasses RNNoise, a typical lightweight model with similar computational burden` 的支撑。
> **但必须注意口径**：**RNNoise 的数字不是同口径复现的**（见下一条）。

> [!contradiction] **Table 2 的 STOI：GTCRN 0.940 = S-DCCRN 0.940，且低于 DeepFilterNet 0.942**
> 本库口径下必须写清：**GTCRN 在 STOI 上不是表内最高**。
> - GTCRN **0.940**、S-DCCRN **0.940**、DeepFilterNet **0.942**、Noisy **0.921**。
> - ⇒ 论文 §3.3.2 的 `surpasses ... in terms of SISNR and PESQ` 是**精确的**（它只声明了这两项，**没有声明 STOI**）；
> - ⇒ 但本库**不能**把"表内最佳"的读法延伸到 STOI 上，也**不能**把它的 `competitive` 升级为 SOTA（对比集合只有 4 个模型，且有 3 处空格子）。
>
> 另注意 **DeepFilterNet 的算力是 0.35 G/s**，是 GTCRN 的 **8.75 倍**，而 STOI 只高 **0.002**——这个数值对本身是一条有价值的记录（见概念页命题 ③）。

> [!contradiction] **RNNoise 的数字来自它自己的官方 repo，与其他各行口径不同——本篇唯一的脚注就在这里**
> `gtcrn-page4.png` 显示 **Table 3 的 RNNoise 行带脚注上标 `1`**，脚注印在**第 4 页页脚**（逐字）：
> > `1 Metrics are measured with source code provided at https://github.com/xiph/rnnoise/`
>
> **两个问题**：
> 1. **脚注只挂在 Table 3**（渲染图上 Table 3 的 RNNoise 带 `1`），但 **Table 2 也有 RNNoise 行且同样没有标注**——两个表的 RNNoise 数字是否同源、Table 2 是否也是用官方 repo 代码测的，**论文未说明**；
> 2. **口径不同意味着不可直接横比**：用 RNNoise 官方 repo 代码测出的 PESQ 2.29 / P.808 3.15，**与论文自己复现/引用的其他模型不是同一套评估流程**（其他模型显然来自各自论文报告的数字）。
>
> **本页处置**：把这一条作为**引用 Table 2/3 时的一等警示**记录。这与 [[wiki_low_latency/sources/2025/FastEnhancer 2025]] 的"GTCRN^a 用官方 checkpoint、LiSenNet^c 等是作者重实现重训"是**同类问题**（基线来源不统一），但本篇的脚注**只覆盖了 Table 3 的一行**，比 FastEnhancer 的交代更不完整。

### Table 3：DNS3 blind test set（4 行，双层表头）

**表头归属**（`gtcrn-page4.png` 逐格核对）：`DNSMOS-P.808` 是**单列**（2.96 / 3.15 / 3.43 / 3.44），紧邻其右的 `DNSMOS-P.835` 下挂**三个子列 `BAK / SIG / OVRL`**。

| 模型 | Para. (M) | MACs (G/s) | P.808 | BAK | SIG | OVRL |
|---|---|---|---|---|---|---|
| Noisy | - | - | 2.96 | 2.65 | 3.20 | 2.33 |
| RNNoise<sup>1</sup> (2018) | 0.06 | 0.04 | 3.15 | 3.45 | 3.00 | 2.53 |
| S-DCCRN (2022) | 2.34 | - | 3.43 | - | - | - |
| **GTCRN (proposed)** | **0.02** | **0.04** | **3.44** | **3.90** | 3.00 | **2.70** |

**四项读法（全部写数值对）**：

| 指标 | GTCRN | 最接近的对照 | 差值 |
|---|---|---|---|
| P.808 | **3.44** | S-DCCRN **3.43** | +0.01 |
| BAK（背景噪声抑制） | **3.90** | RNNoise **3.45** | +0.45 |
| **SIG（语音保真）** | **3.00** | **RNNoise 3.00** | **0.00（完全相同）** |
| OVRL（总体） | **2.70** | RNNoise **2.53** | +0.17 |

> [!warning] **SIG 3.00 是 Table 3 里最需要注意的一项：GTCRN 与 RNNoise 的 SIG 完全相同，且两者都低于 Noisy 的 3.20**
> DNSMOS P.835 的 **SIG** 分衡量**语音信号本身的保真度**（是否有语音损伤/失真），是"人声保留"的核心指标；**BAK** 衡量背景噪声抑制。
> - GTCRN **SIG = 3.00**，RNNoise **SIG = 3.00**，Noisy **SIG = 3.20**；
> - 即 **GTCRN 的收益完全来自 BAK（3.90 vs 3.45，+0.45）与 OVRL（2.70 vs 2.53，+0.17），在语音保真上没有任何提升**；
> - 并且**两个增强器都使 SIG 低于未处理信号**（3.00 < 3.20）——这个现象在 DNSMOS 评测里常见（增强引入失真），但论文未提。
>
> 按本库 [[wiki_low_latency/concepts/低 SNR 人声保留评估]] 的规则——「**不能把 BAK 提升而 SIG/可懂度下降描述为无条件改进；需要报告 SIG–BAK trade-off 和失败案例**」——**GTCRN 恰好落在需要报告这个 trade-off 的情形上，但它没有报告**，论文只写 `our model outperforms RNNoise by a wide margin`。

> [!question] Table 3 只有 4 行，S-DCCRN 的 BAK/SIG/OVRL **全空**
> 论文声称 `also surpasses the large-scale S-DCCRN model`，但 **S-DCCRN 只有 P.808 一格数字（3.43）**，GTCRN 的 3.44 比它高 **+0.01**。
> 在 0.01 的量级上、**无种子数、无方差、无置信区间**的情况下，本库**无法判断这个差值是否显著**。论文用了 `surpasses` 这个较强的动词，但支撑只有 0.01。记录为**证据强度不足**。

> [!contradiction] **Fig. 5 的 PESQ/STOI 标注与面板标签错位——这是本库发现的原文（图内）自相矛盾**
> **从 PDF 文本流读出的四个数字**（`gtcrn.txt` 第 2186–2197 行）：`PESQ 1.16 / STOI 0.66`、`PESQ 1.42 / STOI 0.87`、`PESQ 1.28 / STOI 0.73`、`PESQ 1.94 / STOI 0.93`。
> **用 PyMuPDF 提取这四个标注的坐标**（`p.get_text('dict')`，单位 PDF point）：
>
> | 标注 | PESQ | STOI | 块左上角 (x, y) | 所属行 / 列 |
> |---|---|---|---|---|
> | #1 | **1.16** | **0.66** | (255, **69**) | 第 **1** 行（y≈65–135），第 **2** 列 |
> | #2 | **1.42** | **0.87** | (363, **69**) | 第 **1** 行，第 **3** 列 |
> | #3 | **1.28** | **0.73** | (255, **170**) | 第 **2** 行（y≈165–235），第 **2** 列 |
> | #4 | **1.94** | **0.93** | (363, **170**) | 第 **2** 行，第 **3** 列 |
>
> 面板标签（`gtcrn.txt` 第 2174–2185 行）：第 1 行 `(a) Noisy / (b) Enhanced by RNNoise / (c) Enhanced by GTCRN / (d) Clean`；第 2 行 `(e)(f)(g)(h)` 同序。
> **坐标对齐结果（已用 700 dpi 裁剪逐图确认）**：标识 `(b) Enhanced by RNNoise` 的面板其**图内标注**是 **PESQ 1.16 / STOI 0.66**；标识 `(c) Enhanced by GTCRN` 的面板其**图内标注**是 **PESQ 1.42 / STOI 0.87**。
>
> **⇒ 复核结论（2026-09-27 主 agent 用 600 dpi 单面板裁剪二次确认）**：**GTCRN 在两行上都高于 RNNoise** —— 第 1 行 GTCRN **1.42** > RNNoise **1.16**；第 2 行 GTCRN **1.94** > RNNoise **1.28**；STOI 同向（0.87 > 0.66、0.93 > 0.73）。**与正文 §3.3.2 的定性描述及 Table 2 / Table 3 的方向完全一致。**
>
> **⚠️ 本页初稿曾把这两组数读成"RNNoise 更高"，是本页自己的归组错误，现已改正。**
> 教训：Fig. 5 的四个数字在 PDF 文本流里**没有面板标签**（`gtcrn.txt` 把它们与面板标签拆到不同文本块），必须靠坐标 + 裁剪图目视**双重复核**。**以裁剪图目视结果为准。**

**Fig. 5 数值按"渲染图实际标注"照录（只报事实，不做归属修正）**：

| 行 | 列位置 | 面板标签（论文印刷） | 图内实际标注 PESQ | 图内实际标注 STOI |
|---|---|---|---|---|
| 1 | 第 1 列 | (a) Noisy | 无标注 | 无标注 |
| 1 | 第 2 列 | (b) Enhanced by RNNoise | **1.16** | **0.66** |
| 1 | 第 3 列 | (c) Enhanced by GTCRN | **1.42** | **0.87** |
| 1 | 第 4 列 | (d) Clean | 无标注 | 无标注 |
| 2 | 第 1 列 | (e) Noisy | 无标注 | 无标注 |
| 2 | 第 2 列 | (f) Enhanced by RNNoise | **1.28** | **0.73** |
| 2 | 第 3 列 | (g) Enhanced by GTCRN | **1.94** | **0.93** |
| 2 | 第 4 列 | (h) Clean | 无标注 | 无标注 |

> [!note] 这两个样本的绝对数值偏低（PESQ 1.16–1.94），说明它们是**故意挑的困难样本**
> 即便按"GTCRN 更好"的读法（1.42 / 1.94），GTCRN 在这两条样本上的 PESQ 仍**远低于 Table 2 的平均 2.87**。
> **因此 Fig. 5 不能作为"平均性能"的证据**，它只是两个样本，且论文未说明挑选标准。

## 损失函数（Eq. 1–5，逐字核对 `gtcrn-page3.png`）

| 项 | 形式 | 指数 | 权重 |
|---|---|---|---|
| $\mathcal L_{\text{SISNR}}$ | 对数形式的 SI-SNR | — | $\alpha = 0.01$ |
| $\mathcal L_{\text{mag}}$ | MSE on $\left|\tilde S\right|^{0.3}$ 与 $\left|S\right|^{0.3}$ | **0.3（压缩指数）** | $1-\beta$ |
| $\mathcal L_{\text{real}}$ | MSE on $\tilde S_r / \left|\tilde S\right|^{0.7}$ 与 $S_r / \left|S\right|^{0.7}$ | **0.7（单位化指数）** | $\beta$ |
| $\mathcal L_{\text{imag}}$ | MSE on $\tilde S_i / \left|\tilde S\right|^{0.7}$ 与 $S_i / \left|S\right|^{0.7}$ | **0.7（单位化指数）** | $\beta$ |

**总式**（Eq. 1，**论文原式**）：

$$\mathcal L=\alpha\mathcal L_{\text{SISNR}}(\tilde s,s)+(1-\beta)\mathcal L_{\text{mag}}(\tilde S,S)+\beta\left(\mathcal L_{\text{real}}(\tilde S,S)+\mathcal L_{\text{imag}}(\tilde S,S)\right)$$

其中 $\beta = 0.3$。

> [!contradiction] **Eq. (1) 的系数结构与本任务 brief 给出的骨架不同——本页以 PDF 一手证据为准**
> - **brief 给的是**：$\mathcal L = \alpha\mathcal L_{\text{SISNR}} + (1-\alpha)\left[\beta\mathcal L_{\text{mag}} + (1-\beta)\left(\mathcal L_{\text{real}}+\mathcal L_{\text{imag}}\right)\right]$（**外层含 $(1-\alpha)$ 因子**）；
> - **渲染图（700 dpi 裁剪核对）确认论文原式为**：$\alpha\mathcal L_{\text{SISNR}} + (1-\beta)\mathcal L_{\text{mag}} + \beta\left(\mathcal L_{\text{real}}+\mathcal L_{\text{imag}}\right)$（**没有外层 $(1-\alpha)$ 因子**）。
>
> **差异是实质性的**：按论文原式，**谱损失的权重和恒等于 $(1-\beta)+\beta\cdot 2$ 的第一/第三项结构下，且与 $\alpha$ 完全解耦**——即 $\alpha$ 只控制 SISNR 项的相对比重，**不影响谱域三项之间的配比**；而 brief 的骨架里 $\alpha$ 会整体缩放整个谱损失。
> **本页处置**：以论文原式记录，并在概念页的"口径审计"里列为一条**必须看渲染图才能发现的陷阱**（文本抽取把 $\mathcal L$、$\alpha$、$\beta$、下标拆散到 6 行）。

> [!question] 0.3 与 0.7 这一对指数的分工论文**没有解释**
> - **0.3** 是**压缩指数**（把幅度谱压到 $|\cdot|^{0.3}$ 再算 MSE）；
> - **0.7** 是**单位化指数**（把实部/虚部按 $|\cdot|^{0.7}$ 归一化后算 MSE）；
> - 两者**恰好和为 1**，且论文对 Eq. (2)–(5) 只有一句 `Each term in the aforementioned formula is calculated as follows`——**没有任何一项的解释**。
>
> 一个**可能是**的设计动机（本页观察，未验证）：$|\tilde S|^{0.7}$ 这个分母使 $\mathcal L_{\text{real/imag}}$ 具有**部分电平不变性**——$\tilde S \to a\tilde S$ 时 $\tilde S_r/|\tilde S|^{0.7} \to a^{0.3}\cdot\tilde S_r/|\tilde S|^{0.7}$，**只残留 $a^{0.3}$ 的依赖**，与 $\mathcal L_{\text{mag}}$ 的压缩指数一致。
> **这个"部分电平不变性"是否是刻意设计、0.7 是否由 0.3 推导而来，论文未说明。**

> [!note] 本库关联：$c = 0.3$ 的功率律压缩是一条**跨论文谱系**
> [[wiki_low_latency/entities/FastEnhancer]]（其损失用 $c = 0.3$ 的功率律压缩）与 [[wiki_low_latency/concepts/2609.29867-compute-matched-dynamic-depth]] 记录的 Conv-FSENet 损失（$|X|^{0.3}$ 压缩、$c = 0.3$）**都属同一谱系**。
> **GTCRN 是这条谱系在库内的早期锚点之一**（2024），且**它是唯一把 0.3 同时用作"压缩指数"与"单位化互补指数"的**。

## 低时延账本

| 字段 | 本篇证据 / 边界 |
|---|---|
| 采样率 | **16 kHz**（§3.1、§3.2） |
| 窗函数 | **sqrt-Hanning**（§3.2） |
| 窗长 | **32 ms**（§3.2；@16 kHz = **512 samples**，换算为本页推得） |
| **hop** | **16 ms**（§3.2；@16 kHz = **256 samples**）——**本篇唯一的时延锚点** |
| FFT 长度 | **512**（§3.2） |
| 频率点数 | **未直接报告**；本页推得 **257 = 512/2 + 1** |
| **STFT center / 帧锚定** | **未报告**——本库一等审计项 |
| **look-ahead** | **未报告** |
| **group delay** | **未报告** |
| **逐层 padding**（Conv / DeConv / P-Conv2D / DD-Conv2D） | **未报告** |
| **算法延迟（论文口径）** | **未报告**——论文**没有这个概念的数值，也没有定义** |
| 算法延迟下界（本页推） | **≈ 16 ms**（若 `center=False` 左对齐）；**≈ 32 ms**（若 `center=True`，需加 $W/2$） |
| 时间轴感受野（本页推） | DD-Conv2D **3 / 5 / 11 帧**（kernel 时间维 3、dilation 1/2/5）；单条链累计 **17 帧**；**论文未给** |
| **RTF** | **未报告** |
| **模型执行时间** | **未报告** |
| **p50 / p95 / p99** | **未报告** |
| **deadline miss / underrun** | **未报告** |
| **目标硬件 / 平台** | **未报告** |
| **是否端到端** | **无法判断**（连 STFT 是否计入 MMACs 都没说） |
| **峰值 RAM / SRAM** | **未报告** |
| **功耗** | **未报告** |
| **量化** | **未报告**（无 int8、无 PTQ、无 QAT） |
| **端侧实测** | **未报告** |
| **warm-up / state reset** | **未报告** |
| **长流稳定性** | **未报告** |
| **batch=1 / chunk 大小** | **未报告**；**DPRNN chunk 长度未报告**（决定 intra/inter 切分边界） |
| **隐层状态的跨帧传递方式** | **未报告**（是否有 ring buffer / state） |
| **GRU 隐层维度** | **未报告** |
| **算力证据的形式** | **只有名义 MMACs（39.6 M/s）**——本库 **L0 级（最低）** |
| 库外可得的速度/可懂度 | **来自第三方复现**：[[wiki_low_latency/entities/FastEnhancer]] 记 GTCRN 的 **RTF 0.060（Xeon）/ 0.042（M1）** 与 **WER 3.6**（用官方 checkpoint 评测）——**GTCRN 原文完全没有这两项** |

> [!warning] 账本判定：GTCRN 的延迟下界**只能由 hop 推得**，且依赖两组未报告的信息
> 按本库 [[wiki_low_latency/concepts/严格因果与算法延迟]] 的口径：
> - **算法延迟下界 ≈ hop = 16 ms**（若采用 `center=False` 的左对齐 STFT）；
> - **若 `center=True`，还要加上 $W/2 = 16$ ms**，即 **约 32 ms**。
>
> **因此 GTCRN 不是约 2 ms 候选**——按最乐观的读法（16 ms hop、左对齐、无 look-ahead），它的算法延迟下界也比 2 ms 目标**高约 8 倍**。
> **但另一半也必须说清**：因为 **`center` 未报告**，本库**既不能判定它 ≥ 16 ms，也不能排除某些实现变体落入更低档**——能确定的只有"hop 是 16 ms，因此**帧率是 62.5 Hz**"。这是一条**"证据不足，双向都不能判定"**的性质，是本页认为最该传给本库的一条判断纪律（详见源页 §5.3）。

> [!note] 但它**可以**被重配到 4 ms hop——库内已有直接证据，且代价被量化了
> [[wiki_low_latency/sources/2026/RT-Tango 2026]] 把**分布式 GTCRN** 用作双耳对照，并在两种帧率下各跑了一次（其 Table 1）：
>
> | 配置 | hop | DNN MACs (MMAC/s) | SI-SDR（左/右） | PESQ（左/右） |
> |---|---:|---:|---|---|
> | GTCRN | **16 ms** | **48.98** | 5.6 / 3.7 | 1.47 / 1.34 |
> | GTCRN | **4 ms** | **197.5** | 6.0 / 4.0 | 1.52 / 1.36 |
>
> - **该架构可被重配到 4 ms hop**（帧率 62.5 → 250 Hz），**不是"被架构锁死在 16 ms"的模型**；
> - **代价是算力 48.98 → 197.5 MMAC/s**（$197.5/48.98 = 4.03$），**与帧率比 250/62.5 = 4.0 几乎完全吻合** ⇒ **GTCRN 的算力几乎正比于帧率**（逐帧计算，无跨帧复用）；
> - **质量反而略升**（SI-SDR 5.6 → 6.0，PESQ 1.47 → 1.52）——帧率提高让时频分辨率与状态更新更细。
>
> **口径提醒**：48.98 / 197.5 是**"每节点分布式 GTCRN"的口径**（4 麦输入、mask 作用于本地参考通道），**与 GTCRN 原文的 39.6 MMACs/s 不是同一配置**（差 1.24×）。**两者不可直接相减**，只能用于说明"该架构可重配到 4 ms"这一质性事实。
> **线性外推（本页推，RT-Tango 未测 2 ms）**：若把 GTCRN 拉到 2 ms hop，按同样比例需约 $197.5 \times (4/2) = 395$ MMAC/s——**这个量级已超出"超轻量"的范畴**（GTCRN 原位 39.6 M/s）。**即：GTCRN 靠"提高帧率"进 2 ms 档，会以牺牲其唯一卖点（超低算力）为代价。**

## 因果性与结构审计

| 审计项 | 证据 | 本库判定 |
|---|---|---|
| 采样率 | 16 kHz（§3.1） | 明确 |
| 窗长 / hop / FFT | 32 ms / 16 ms / 512（§3.2） | 明确 |
| **STFT center / 帧锚定** | **未报告** | **决定性缺口**：若 `center=True` 则前端含 **16 ms 未来样本** |
| **inter-frame 循环方向** | **分组单向 GRU**（论文明确） | **正向**——这是论文的因果性支柱，且理由合理（inter-frame 建模的是"某频点在时间上的依赖"） |
| **intra-frame 循环方向** | **分组双向 GRU**（论文明确） | **本页判定不破坏因果**——它在**单帧内、沿频率轴**双向，**不跨时间帧** |
| **卷积层 padding** | **未报告**（Conv / DeConv / P-Conv2D / DD-Conv2D 全部） | **决定性缺口**：`same` padding 常含未来帧；`causal` padding 不含 |
| **时间轴感受野与缓存需求** | **未给**；本页推得 DD-Conv2D 分别 **3 / 5 / 11 帧**，单条链累计 **17 帧** | 若为因果卷积，需缓存 $(k-1)d$ 帧历史（**2 / 4 / 10 帧**） |
| **隐层状态跨帧传递** | **未报告** | 流式部署的前提缺失 |
| **DPRNN chunk 长度** | **未报告** | 决定 intra/inter 的切分边界与跨帧缓存长度 |
| **accelerator launch / 图的段数** | **不适用**（论文无任何硬件或部署讨论） | 本库结构审计清单的**第 8 项**（[[wiki_low_latency/concepts/2609.29867-compute-matched-dynamic-depth]] 命题 ③）——本篇**完全空白** |
| **因果性声明** | 「grouped unidirectional GRU for inter-frame ... **so that the causality of the model can be guaranteed**」（p.2 §2.2）——**全文唯一一处提 causality** | **`paper-claimed-causal`** |

**判定结论**：记为 **`paper-claimed-causal`**。理由：

1. 论文**只有一句声明**，且这句话**只论证了"双向/单向"这一处**，**没有覆盖卷积 padding 与 STFT center**；
2. **逐层 padding certificate 完全未给**（这是因果性的直接判据）；
3. **state certificate 未给**（哪些层有状态、如何跨帧传递）；
4. **STFT 的 center 与否未报告**——决定"前端是否含 16 ms 未来样本"的关键参数；
5. **DPRNN 的 chunk 长度未报告**——决定 intra/inter 的切分边界。

> [!important] 本页的**结构审计（7 项 + accelerator launch）**——按 [[wiki_low_latency/sources/2026/Early Exit Compute-Matched 2026]] 的写法补全
> 7 项中 **#3（STFT center）、#6（卷积 padding）、#7（时间感受野）三项为未报告，且都是决定性的**；第 8 项**不适用**。
> **本页既不能把它升级为 `strict_causal`，也不能判为 `non_causal`。**
> 对照：[[wiki_low_latency/entities/LaCo-SENet]] 有逐层 padding 分配式（本库最严尺子），[[wiki_low_latency/entities/Early-Exit-Conv-FSENet]] 有"跳过即不更新状态"的结构性保证——**GTCRN 两者都没有**。

## 结果与证据边界

- **支持**：
  - **在 RNNoise 的算力量级上把 PESQ 从 2.29 提到 2.87**：MACs **相同（0.04 G/s）**，参数 **0.02 M vs 0.06 M**（Table 2）——**这是本篇最干净的对照**（但注意 RNNoise 数字口径不同，见上）；
  - **TRA 的 MACs 性价比高**：`+0.56 M/s` 换 SISNR `+0.38` / PESQ `+0.04`；对照 **SFE `+5.16 M/s` 换 SISNR `+0.23` / PESQ `+0.03`**（Table 1，双坐标 trade-off：TRA 的参数代价是 SFE 的 4.1 倍）；
  - **VCTK-DEMAND 上 PESQ 2.87 与 SISNR 18.83 为表内最高**（Table 2；但 STOI 0.940 不是最高）；
  - **DNS3 blind 上 P.808 3.44、BAK 3.90、OVRL 2.70 为表内最高**（Table 3）；
  - **模型确实极小**：23.7 K 参数 / 39.6 MMACs per second，比 PercepNet 小 **400 倍**（8.00 M / 0.80 G/s），比 DeepFilterNet 小 **90 倍**（1.80 M / 0.35 G/s）；
  - **ERB 频带压缩是可被复用的算子**：[[wiki_low_latency/entities/RT-Tango]] 直接借用（2 kHz 以上、192 → 64）到双耳场景。
- **不支持**：
  - 任何**低时延**主张——**论文没有延迟数字，也没有这个概念的数值**，全文无 RTF / 无 p99 / 无目标硬件 / 无量化 / 无端侧实测；
  - **约 2 ms 级候选**：hop 就是 **16 ms**，最乐观读法下算法延迟下界也是 2 ms 的 **约 8 倍**；论文**也未声称**低时延；
  - `strict_causal`（**STFT center 未报告、逐层 padding 未给、感受野方向未说明、chunk 长度未给**）；
  - **人声保真（SIG）已提升**——Table 3 的 **SIG = 3.00，与 RNNoise 完全相同，且两者都低于 Noisy 的 3.20**；
  - **STOI 表内最高**——0.940 与 S-DCCRN 持平、**低于 DeepFilterNet 0.942**；
  - **子带路线的 RTF 优势**——论文**无 RTF**，无法回应 [[wiki_low_latency/entities/FastEnhancer]] 的批评（GTCRN RTF 0.060 vs FastEnhancer-B 0.022）；
  - **"越小越好"的容量论证**——[[wiki_low_latency/entities/PSMSE]] 批评这一路线「performance tends to degrade due to the limited capacity of their simplified designs」，**GTCRN 原文无回应数据**；
  - **低 SNR 分层、噪声类型分层、ASR WER、主观 MOS、false-suppression、F0/prosody、混响指标**——**全部未报告**；
  - **表内对比是完整矩阵**——Table 2 有 4 处空格、Table 3 有 6 处空格。
- **未报告**：算法延迟口径与数值、STFT center/帧锚定、look-ahead、group delay、逐层 padding、状态跨帧传递、DPRNN chunk 长度、GRU 隐层维度、SFE 后通道数、skip connection 层对、RTF、模型执行时间、**p50/p95/p99**、deadline miss、目标硬件、峰值 RAM/SRAM、功耗、量化、端侧实测、warm-up、state reset、长流稳定性、batch=1、训练总 epoch/步数、**随机种子与方差**、权重初始化、**DPCRN 的参数量与 MACs**、ASR WER、主观 MOS/MUSHRA、负 SNR 分层、噪声类型分层、false-suppression、SPP/VAD、F0/formant/prosody、voiced energy、混响指标（C50/SRMR/DRR）、eSTOI、CRM 如何与带噪谱相乘、iSTFT 的窗与 hop、OLA 方式、相位是否替换。
- **可比性提醒**：
  - **Table 1 的消融用的是 DNS3 的约 100 小时子集**，而 Table 2/3 主结果的数据量**论文未在同一处说明** ⇒ **Table 1 的绝对数值不可与 Table 2/3 直接横比**；
  - **RNNoise 的数字口径不同**（官方 repo 代码），且**脚注只挂在 Table 3**；
  - **Table 2 的 MACs 单位是 G/s、Table 1 是 M/s**——换算后再比（GTCRN 0.04 G/s = 40 M/s vs Table 1 末行 39.63 M/s，**自洽**）；
  - **Table 2 的 0.02 M 与 Table 1 末行的 23.67 K 是同一个数的两种精度**（0.02 M = 20 K，四舍五入）；
  - **库外引用 GTCRN 的数字必须核对口径**（见下 `[!contradiction]`）。
- **数字口径警示**：
  - **23.7 K / 39.6 M/s 是论文的"设计声称值"**，**不是"官方代码实测值"**（见下）；
  - **hop 16 ms ≠ 算法延迟 16 ms**——前者是帧率，后者需 center/padding 才能定（**未报告**）；
  - **MMACs per second 是时间归一化量**，与 hop 直接相关（RT-Tango 的 4.03× 印证了这一点）；
  - **Table 3 的 SIG 差值 0.00 是本篇最不该被跳过的数字**；
  - **Fig. 5 的四个数字与其面板标签错位**（见上 `[!contradiction]`）。

## 参数量 / 算力的库内三方矛盾

论文在**三处**（Abstract、§3.2、§4 结论）一致声称 **23.7 K parameters and 39.6 MMACs per second**：

> "For the whole model, the number of parameters is **23.7 K** and the computational cost is **39.6 MMACs per second**."（p.3 §3.2 逐字）

**23.7 K 与 39.6 M/s 恰好对应 Table 1 最后一行**（SFE ✓ / TA ✗ / TRA ✓：Para. 23.67 K、MACs 39.63 M/s）——**内部自洽**。

> [!contradiction] **库内三方对 GTCRN 的参数量/算力口径不一致，且都与论文正文不同或需要解释**
> | 来源 | 记录值 | 出处 / 口径 |
> |---|---|---|
> | **GTCRN 原文**（本篇） | **23.7 K 参数 / 39.6 MMACs per second** | Abstract、§3.2、§4；对应 Table 1 的 SFE✓+TRA✓ 行（23.67 K / 39.63 M/s）——**设计声称值** |
> | [[wiki_low_latency/entities/FastEnhancer]]（其 Table 2） | **24 K 参数 / 40 M MACs**（记为 GTCRN<sup>a</sup>，脚注 a = `Evaluated using the official checkpoint`） | **四舍五入 + 官方 checkpoint 评测** |
> | [[wiki/sources/2026/muNet 2026]]（其对比表） | **48 K 参数 / 33 MMACs** | **与原文差异最大** |
> | [[wiki_low_latency/sources/2026/PSMSE 2026]] | **23.7 K**（写作 `23.7K–79K` 区间，与原文一致） | 直接引用原文 |
>
> **(1) 24 K / 40 M 与 23.7 K / 39.6 M 是同一个数的四舍五入** —— 差值仅 `+0.3 K` 与 `+0.4 M/s`（相对误差 1.3 % 与 1.0 %），**不构成矛盾**。FastEnhancer 用官方 checkpoint 评测，而其 checkpoint 的**实际参数量可能与论文声称值略有出入**（论文常按设计值报告，代码实现可能含额外的可学习参数如 BN 的 affine 参数）。
>
> **(2) 48 K / 33 MMACs 与原文的差异无法用例差解释** —— 参数 **48 K vs 23.7 K**（约 **2.03×**），MACs **33 vs 39.6**（约 **0.83×**）。**两者方向相反**（参数翻倍、算力反降），**不可能来自同一模型的同一配置**。
>
> **(3) 一个高度吻合的线索**：[[wiki/sources/2026/muNet 2026]] 的 **48 K / 33** 与"官方 repo（`https://github.com/Xiaobin-Rong/gtcrn`）更新后的 **48.2 K / 33.0 MMACs**"高度吻合 ⇒ **强烈提示 μNet 引用的是官方 repo 的实测值，而不是论文的声称值**。
> **但本页无法独立核实这一点**（`evidence_policy: local_pdf_only`，**无网络访问，也未克隆该 repo**）。
>
> **(4) 因此本库目前的判断是**：**「23.7 K / 39.6」很可能是论文的设计声称值，「48 K / 33」很可能是官方实现的真实规模**——两者差 2 倍的原因论文**从未说明**。
>
> **可能的解释（本页列出，均未验证）**：
> | 假设 | 支持 | 反对 |
> |---|---|---|
> | **A. 官方 repo 含论文未计入的参数**（如 BN 的 affine、GRU 的 bias、TRA 的 FC） | 论文报告 23.7 K 恰好等于 Table 1 的表内值，**可能是"按设计算"而非"按 `sum(p.numel())` 算"** | 2 倍的差距偏大，普通 BN/GRU 参数不至于翻倍 |
> | **B. repo 默认配置与论文不同**（GRU 隐层更大、额外层） | —— | MACs 从 39.6 降到 33 说明**计算结构变了**，与参数翻倍矛盾 |
> | **C. MACs 统计口径不同**（per-second vs per-frame；是否含 STFT；hop 假设） | `MMACs per second` 是**时间归一化**量，与 hop 直接相关；**论文连 STFT 是否计入都没说** | —— |
> | **D. μNet 的数字有其他来源错误** | —— | 48.2 K / 33.0 的高度吻合降低了这个可能 |
>
> **本页的处置（不单方面采信任何一方）**：
> - **以论文原文的 23.7 K / 39.6 MMACs per second 为主记录**（有 PDF 一手证据，且与 Table 1 内部自洽）；
> - **同时并列列出 48 K / 33（μNet 口径）与 24 K / 40（FastEnhancer 口径）**；
> - **明确标注：24 K/40 是四舍五入；48 K/33 无法与原文调和，且与"官方 repo 更新值"高度吻合**；
> - **建议主 agent 把这一条登记入跨页矛盾清单**，并在有网络条件时**直接核查 `https://github.com/Xiaobin-Rong/gtcrn` 的 `model.py` 与 README 的参数量声明**。
>
> **这一条是本页最重要的跨页发现之一**：GTCRN 恰是被 [[wiki_low_latency/entities/FastEnhancer]]、[[wiki/sources/2026/muNet 2026]]、[[wiki_low_latency/entities/PSMSE]]、[[wiki_low_latency/entities/RT-Tango]] **四篇同时引用**为参照的锚点——**锚点的数值错了，四条引用链一起偏**。

## 交叉链接

- 源论文：[[wiki_low_latency/sources/2024/GTCRN 2024]]
- 概念展开：[[wiki_low_latency/concepts/gtcrn-2024-ultralight-subband-grouped-dprnn]]
- 前身/基石（同一课题组谱系）：[[wiki_low_latency/entities/DPCRN]]、[[wiki_low_latency/concepts/2107.05429-dual-path-recurrent-context]]、[[wiki_low_latency/entities/Skip-DPCRN]]、[[wiki_low_latency/sources/2022/Skip-DPCRN 2022]]
- 引用 GTCRN 的四篇：
  - [[wiki_low_latency/entities/FastEnhancer]]、[[wiki_low_latency/sources/2025/FastEnhancer 2025]]（提供 RTF 与 WER；批评子带路线抬高 RTF）
  - [[wiki_low_latency/entities/RT-Tango]]、[[wiki_low_latency/sources/2026/RT-Tango 2026]]（借用 ERB 压缩；测 16 ms 与 4 ms 两个帧率）
  - [[wiki_low_latency/entities/PSMSE]]、[[wiki_low_latency/sources/2026/PSMSE 2026]]（批评容量受限）
  - [[wiki/sources/2026/muNet 2026]]（主要竞品；**48 K / 33 口径的来源**）
- 同分支竞品（子带 / 超轻量）：[[wiki_low_latency/entities/PercepNet]]、[[wiki_low_latency/entities/DeepFilterNet2]]、[[wiki_low_latency/entities/DCCRN]]、[[wiki_low_latency/entities/FSB-LSTM]]、[[wiki_low_latency/concepts/2304.08707-full-sub-band-modeling]]
- 同命题不同机理（MACs ≠ 速度）：[[wiki_low_latency/concepts/2509.21867-speed-optimized-streaming-design]]、[[wiki_low_latency/entities/Early-Exit-Conv-FSENet]]、[[wiki_low_latency/concepts/2609.29867-compute-matched-dynamic-depth]]
- 分组思路的另一端（动态、神经元级）：[[wiki_low_latency/entities/D-GRU]]、[[wiki_low_latency/concepts/2408.12425-dynamic-gated-rnn]]
- 最严因果尺子（对照）：[[wiki_low_latency/entities/LaCo-SENet]]、[[wiki_low_latency/entities/RT-SEMamba]]
- 延迟账本口径：[[wiki_low_latency/concepts/严格因果与算法延迟]]、[[wiki_low_latency/concepts/低时延前端与延迟账本]]
- 人声保留缺口：[[wiki_low_latency/concepts/低 SNR 人声保留评估]]

> [!question] 待验证（本页留给主 agent 与后续读者的清单）
> **(1) 参数量口径矛盾**：原文 **23.7 K / 39.6 MMACs per second**（内部自洽）vs μNet 的 **48 K / 33** vs FastEnhancer 的 **24 K / 40**。**24 K/40 可解释为四舍五入；48 K/33 无法解释**（参数 2.03×、MACs 0.83×，方向相反）。建议**直接核查官方 repo 的 README 与模型定义**。本页无法做（无网络）。
> **(2) STFT center 未报告**——本实体**最关键的一等缺口**。若 `center=True`，前端含 16 ms 未来样本，算法延迟下界从 16 ms 变 32 ms，因果判定需下调。
> **(3) 逐层 padding 未报告**（Conv / DeConv / P-Conv2D / DD-Conv2D 全部）——因果性的直接判据缺失。
> **(4) DD-Conv2D 的时间感受野未给**。本页推得 kernel 时间维 3、dilation 1/2/5 ⇒ 单块 **3/5/11 帧**、单链累计 **17 帧**（若左对齐），**但这是本页的推算，论文未给**；若用 `same` padding 则含未来帧。
> **(5) 参数增量归属未报告**：Table 1 中 `✗/✗/✗ → ✗/✗/✓` 参数从 13.35 K 涨到 21.65 K（**+8.30 K**），而 SFE 只涨 2.02 K。**论文未明确这 8.30 K 是否全部属于 TRA**（可能含全连接/归一化的连带变化）。
> **(6) Fig. 5 的标注归属需坐标复核** —— 初稿曾误判为"标注放反、与正文矛盾"，**经 600 dpi 单面板裁剪二次确认已改正**（GTCRN 1.42/1.94 vs RNNoise 1.16/1.28，与正文一致）。仅作为"文本流丢失面板标签时的复核方法"记录，**不再是论文缺陷**。
> **(7) TA [24] 的结构未描述**：Table 1 的对照臂在本篇内是黑箱。
> **(8) 论文承诺了却未给的数据**：Table 2 的 RNNoise/PercepNet 的 SISNR 与 STOI（空格）、Table 3 的 S-DCCRN 的 BAK/SIG/OVRL（空格）、**DPCRN 本身的参数量（全文未给，"压了多少倍"不可算）**、训练总 epoch 数、随机种子数、GRU 隐层维度、DPRNN chunk 长度、SFE 后通道数、skip connection 层对。
> **(9) 无种子、无方差**：Table 1 / Table 3 有多处 `+0.01` 量级的结论（PESQ 1.89→1.91、P.808 3.43→3.44、两开关次可加性的 0.09 SISNR），**均无法判断显著性**。
> **(10) 页码定案**：本库已用论文自身页脚（971/972/973/974/975）判定 **pp. 971–975 正确**；[[wiki_low_latency/sources/2026/Early Exit Compute-Matched 2026]] 引文 [2] 的 10286–10290 为误著录。**建议在该页的 `[!question]` 上追加定案**（本页不改动该文件）。
