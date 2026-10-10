---
title: FastEnhancer - 速度优化的流式神经语音增强
type: source
created: 2026-09-26
updated: 2026-09-26
tags:
  - speech-enhancement
  - single-channel
  - streaming
  - rnnformer
  - dual-path
  - time-rnn-frequency-transformer
  - fusability
  - batch-normalization-fusion
  - rtfspeed-optimization
  - pareto-frontier
  - onnx-runtime
  - paper-claimed-causal
  - 16ms-hop
  - macs-not-latency
source_type: paper
year: 2025
authors: Sunghwan Ahn; Jinmo Han; Beom Jun Woo; Nam Soo Kim
venue: arXiv preprint (eess.AS)
venue_status: preprint_only   # 无会议/期刊；arXiv 无 Comments、无 Journal-ref；仅 v1（2026-09-26 核实）
arxiv: https://arxiv.org/abs/2509.21867
code: https://github.com/aask1357/fastenhancer
docs: https://aask1357.github.io/fastenhancer/
local_pdf: raw/papers/low_latency_causal_se/2509.21867.pdf
evidence_policy: local_pdf_only
related:
  - [[wiki_low_latency/entities/FastEnhancer]]
  - [[wiki_low_latency/concepts/2509.21867-speed-optimized-streaming-design]]
  - [[wiki_low_latency/concepts/严格因果与算法延迟]]
  - [[wiki_low_latency/concepts/低时延前端与延迟账本]]
  - [[wiki_low_latency/concepts/低 SNR 人声保留评估]]
  - [[wiki_low_latency/concepts/2107.05429-dual-path-recurrent-context]]
  - [[wiki_low_latency/entities/DPCRN]]
---

~~~yaml
- 论文: [FastEnhancer: Speed-Optimized Streaming Neural Speech Enhancement](2025)
  ├── 要解决什么问题: 近年前作都在降参数量与 MACs（DPRNN 结构、精细 encoder-decoder、子带分解），但论文观察到这些方法「frequently increase memory operations and architectural complexity, which slows down the actual inference speed」——即 MACs 低 ≠ 实际快；而低 RTF 才是端侧真实诉求
  ├── 核心方法: 精简 encoder-decoder + RNNFormer block（时间轴单向 GRU + 频率轴 MHSA 的 dual-path）；全模型时间轴卷积 kernel=1（避免缓存 k−1 帧）、全模型 BN 并在推理期融合进相邻层；功率压缩复数谱 (c=0.3) + 两通道 mask，Nfft=512，hop H 随档位变化
  ├── 属于哪个分支: 单通道时频掩蔽增强 / 流式低 RTF 架构 / dual-path（但主张「两轴用不同算子」）
  ├── 输入/输出: noisy waveform x → STFT(Nfft=512, hop=H) → 功率压缩 Xc=|X|^0.3·e^{j∠X}（当两通道实张量，保留 Nfft/2 频点）→ 预测两通道 mask M → Ŷc=M⊙Xc → 解压 → 最高频点零填充 → iSTFT 得 ŷ
  ├── 关键trick: 把「延迟/速度」直接当成架构约束来选算子——kernel=1（免缓存）、BN（可融合）、时间 GRU（状态定长、无 KV cache）、频率 MHSA（全局、无需缓存）
  ├── 数据集: VCTK-Demand [14]（Table 2 标题写作 "Voicebank-Demand"，§4 写作 "VT**CK**-Demand"，同一数据集两种写法）；48 kHz 降采样到 16 kHz；训练随机抽 2 s 段
  ├── 对比了谁: GTCRN^a（官方 ckpt）、LiSenNet^b（官方训练代码，**因 input normalization 与 griffin-lim 不可流式**）、LiSenNet^c（去掉前两项后重训，可流式）、FSPEN^d、BSRNN^d（均按 §4 重实现重训）
  ├── 性能上限: FastEnhancer-L：DNSMOS(P.808) 3.53 / SIG 3.44 / BAK 4.04 / OVL 3.16 / SCOREQ 0.239 / SISDR 19.6 / PESQ 3.26 / STOI 0.952 / ESTOI 0.877 / WER 3.1；但 MACs 达 11G，是 GTCRN(40M) 的 275×
  ├── 参数量: 22K(T) / 92K(B) / 195K(S) / 492K(M) / 1105K(L)
  ├── 消融关键发现: ① 时间轴 kernel 1→3：Para 92K→187K、RTF(Xeon) 0.022→0.028，而 SISDR 19.0→19.0、STOI 94.5→94.5 **完全不变**；② BN→LN：**参数量与 MACs 一个没变（92K）**，RTF(Xeon) 0.022→**0.028（+27%）**、RTF(M1) 0.026→0.029（+12%）；③ 频率轴 MHSA→GRU（DPRNN）STOI 相近但 SISDR 明显下降；④ 时间轴 GRU→MHSA（DPT，look-behind 31 帧≈0.5 s）参数更少但需 KV cache，RTF 显著升高
  ├── 遗留问题(你的机会): **通篇没有任何「算法延迟 XX ms」数字**，只报 RTF；STFT 的 center/帧锚定方式未报告；论文称 "frame-by-frame" 但无 group delay / look-ahead / warm-up / state reset / chunk 大小 / batch=1 / 长流稳定性证据；"streaming condition" 未定义；5 seeds 只报均值无方差；RTF 只有单值无 p50/p95/p99；无量化/功耗/峰值内存；无人声保留分层（负 SNR/babble/竞争说话人/false-suppression/SPP/F0/prosody 全未报告）
  └── 跟哪篇像: [[wiki_low_latency/entities/DPCRN]]（同为 TF-domain U-Net + DPRNN，本篇 §2.2 明确点名其为出发点，且本篇要否定的正是"D**PRNN 用在频率轴**"）；[[wiki_low_latency/entities/LaCo-SENet]]（同在单线程 Xeon 上测 RTF，口径同构可比，但 LaCo-SENet 给出逐层延迟分配式而本篇只有 RTF）
~~~

# FastEnhancer: Speed-Optimized Streaming Neural Speech Enhancement

> Sunghwan Ahn; Jinmo Han; Beom Jun Woo; Nam Soo Kim（Seoul National University, Department of Electrical and Computer Engineering and INMC），arXiv:2509.21867v1 [eess.AS]，26 Sep 2025，共 5 页。代码与预训练权重开源：<https://github.com/aask1357/fastenhancer>；文档站：<https://aask1357.github.io/fastenhancer/>。
> 本页的核心不是复述它的指标，而是把它当成**「速度优化方法论」与「延迟账本」两个议题的最佳样本**：它是本库中少数**明确把"实际推理速度"而不是 MACs 当第一目标**的论文，但它**通篇没有给出一个延迟数字**。

> [!note] 发表状态：**arXiv 预印本，未见同行评审 venue**（2026-09-26 核实）
> 核实结果（三项独立证据一致）：
> 1. **本地 PDF 无任何 venue 信息**——无会议名、无 "Submitted to"、无 "Accepted"、无版权行；页脚只有 `arXiv:2509.21867v1 [eess.AS] 26 Sep 2025` 一行；字号与双栏排版是**典型的 ICASSP 系列模板**（摘要区、Index Terms、正文引言均为 ICASSP 段落标题风格），但这只是模板，**不构成录用证据**。
> 2. **arXiv 元数据无 Comments、无 Journal-ref、无 DOI**（仅有 DataCite 分配的 arXiv DOI `10.48550/arXiv.2509.21867`）；只有 **v1** 一个版本，2025-09-26 上传，**无后续更新**（若已录用通常会在 Comments 里补会议名并加 v2）。
> 3. 分类仅 `eess.AS`（未同时挂 `cs.SD`）。
>
> **本库据此将 `venue` 记为 `arXiv preprint (eess.AS)`，不标任何会议。** 需注意：
> - 论文正文**自称 "state-of-the-art"**、使用 **ICASSP 模板**、上传时间（2025-09）落在 **ICASSP 2026** 投稿周期内——这三点容易被误读为"已录用"，**但都不是录用证据**。
> - 本库结论：**不能称其为"A 会论文"**。它是一篇**格式像会议投稿、但尚未见任何同行评审 venue 的预印本**。
> - 同批对照：Tsunoo 2024（arXiv:2412.19248）的 `venue` 记 "ICASSP 2025" 来自**论文正文自述**，属"作者声称"，本库已标为待验证；本篇连作者声称都没有。

> [!warning] PDF 转换质量与阅读说明
> 原 PDF 共 5 页，PyMuPDF 文本抽取（`tmp/pdf_extract/2509.21867.txt`）总体良好（正文与参考文献均可读），但有六类问题必须看渲染图核对，本页已逐条核对：
> 1. **Table 2 的脚注上标归属完全丢失**。抽取文本把四条脚注平铺在末尾，无法判断 a/b/c/d 落在哪一行。**第 4 页渲染图**确认：`GTCRN` 带 `a`、`LiSenNet` 第一行带 `b`、`LiSenNet` 第二行带 `c`、`FSPEN` 与 `BSRNN` 带 `d`。
> 2. **抽取文本把 `FastEnhancer-B` 那一行重复了一次**（文本 567–581 行与 597–611 行内容完全相同）。**第 4 页渲染图**确认 Table 2 实际只有 **5 个 FastEnhancer 行：T / B / S / M / L**（渲染图中的顺序为 B、T、B、S、M、L，其中 B 出现两次属排版重复，本页按去重后的 5 档记录，**不把它当成两个不同配置**）。
> 3. **公式的范数符号被拆散**。Eq. (2)–(5) 的 `∥·∥_2^2` 与 `∥·∥_1` 在抽取文本中断成多行。本页公式已用**第 3 页渲染图**逐条核对：`L_mag=∥|Y_c|−|Ŷ_c|∥_2^2`（只对**幅度**取差）、`L_comp=∥Y_c−Ŷ_c∥_2^2`、`L_con=∥Y_c−STFT_c(ŷ)∥_2^2`、`L_wav=∥y−ŷ∥_1`。
> 4. **功率压缩的相角符号被抽成乱码 `j̸`**。原式为 $X_c=|X|^c\cdot e^{j\angle X}$，$c=0.3$；本页一律用 `\angle X` 正确书写，不沿用抽取文本乱码。
> 5. **Fig. 2（第 3 页）的 8 个子框图与其维度标注在文本中全部散落**。第 3 页渲染图确认子框图标签为 FastEnhancer / Pre Encoder / EncoderBlock / DecoderBlock / Pre RNNFormer / Post RNNFormer / RNNFormer，以及 `H`（hop）在 STFT/iSTFT 标注、`Nfft/8→F` 与 `C1→C2` 的维度变化关系。
> 6. **Fig. 1 与 Fig. 3 的横轴是对数刻度 RTF（0.0125–0.4）**，抽取文本把刻度值与图例平铺，看不出 x 轴方向。第 1 页与第 4 页渲染图确认：**RTF 从左到右递增（x 越左越快）**，Fig. 1 曲线为 FastEnhancer（蓝▲）/ BSRNN（绿▼）/ GTCRN（灰■）/ LiSenNet（橙♦）/ FSPEN（黑×），Fig. 3 为 RNNFormer / DPRNN / DPTransformer（**注意 Fig. 3 的图例只有三条、无第四类**）。
>
> 凡是论文**未报告**的字段（算法延迟、group delay、warm-up、state reset、chunk 大小、look-ahead、p99、峰值 RAM/SRAM、量化、功耗、端到端、负 SNR 分层、babble/竞争说话人、false-suppression、SPP/VAD、F0/formant/prosody、听感 MOS），本页一律写「未报告」，不作任何补写。

## 1. 他们为什么这么做？（motivation）

### 1.1 任务与对象

单通道（monaural）语音增强：从被噪声污染的单通道混合信号中估计干净语音，面向在线会议、智能家居、助听器（p.1 Abstract / §1）。采样率 16 kHz（全部音频从 48 kHz 降采样）。

论文把目标明确写成三条并列属性（p.1 §1）：

- **High quality and intelligibility**：增强语音听起来清晰自然（high quality），且词句容易听懂（high intelligibility）——论文把两者**分开列举**，这一点在本库价值很高；
- **Streaming**：原文「The model can process input spectrograms in a **frame-by-frame** manner.」
- **Fast processing speed**：在资源受限环境下取得低 RTF，并且——**「We consider a single CPU thread as a key benchmark for such environments, as many real-world applications lack dedicated hardware accelerators like GPUs or NPUs.」**（p.1 §1）

第三条是本篇区别于绝大多数低复杂度论文的地方：它明确选择**单 CPU 线程**作为基准场景，而不是 GPU。

### 1.2 论文动机：核心观察

论文的动机不是"再降一点 MACs"，而是对**整条轻量化路线**提出质疑：

> 近年的 DPRNN 结构 [6–8]、精细 encoder–decoder 设计 [9]、子带分解策略 [10–13]「successfully reduce the number of parameters and MAC operations」，**但**「we observe that they frequently increase memory operations and architectural complexity, which slows down the actual inference speed」（p.1 §1，详见 §2.2）。

§2.2 展开了这条观察：DPCRN [7] 与 TRU-Net [8] 引入 TF-domain U-Net + DPRNN；BSRNN [13] 引入 band-split encoder/decoder；FSPEN [10] 引入子带 encoder/decoder + path extension 的时间 RNN；GTCRN [9] 与 LiSenNet [11] 使用子带特征提取、grouped DPRNN 与 channel split-concatenate-shuffle。论文的结论是：

> 「While these methods successfully reduced the number of parameters and MACs, their **increased architectural complexity and memory operations paradoxically led to higher RTFs** (Section 5.1).」（p.2 §2.2）

即：**MACs 与参数量下降，RTF 反而上升。** 这是本篇全部立论的起点，也是本库最需要记录的一条方法论命题（见 §5 与概念页）。

### 1.3 对 DPRNN 的第二条质疑

论文同时对 DPRNN 的**结构假设**提出疑问（p.2 §2.1）：

- DPRNN 原本是波形域语音分离方案 [6]，把序列切成 chunk，在第三维做 intra-chunk RNN、第二维做 inter-chunk RNN；
- 它在 TF 域被广泛采用 [7–12]，做法是**在时间 RNN 与频率 RNN 之间交替**；
- 论文的质疑：**「applying an RNN to the frequency axis assumes that frequency bands have a sequential relationship. This is suboptimal because spectral relationships (e.g. harmonics) exhibit global rather than sequential dependencies.」** 并主张「a model should be capable of handling **all frequency interactions concurrently**」。

对既有的替代尝试，论文也给了评价：把 dual-path 里的 RNN 换成 Mamba / xLSTM [15, 16] 的工作「are designed for non-streaming, large-scale scenarios, and **still impose a sequential relationship on the frequency axis**」；而 DPT [17, 18] 里「a **time-axis transformer is problematic for low-latency streaming**. It requires caching previous key and value frames, demanding additional memory operations. Moreover, to improve speech quality, the number of cache frames should be increased [19], requiring more memory and arithmetic operations.」（p.2 §2.1）

## 2. 之前的人怎么做不了？（limitation → gap）

| 路线 | 代表工作 | 论文指出的问题 |
|---|---|---|
| DPRNN 用在 TF 域 | DPCRN [7]、TRU-Net [8] | 频率轴 RNN 假设频带间有**顺序关系**，而频谱关系（谐波）是**全局**的 |
| 子带分解 + 精细 encoder-decoder | BSRNN [13]、FSPEN [10]、GTCRN [9]、[[wiki_low_latency/entities/LiSenNet\|LiSenNet]] [11] | 降了参数量与 MACs，但**架构复杂度与内存操作上升，RTF 反而更高** |
| Mamba / xLSTM 替换 dual-path RNN | [15, 16] | 面向非流式大规模场景，且**仍然**在频率轴施加顺序关系 |
| Dual-path Transformer (DPT) | [17, 18] + streaming DPT [19] | 时间轴 Transformer 需缓存 KV，缓存帧数越多质量越好 → **内存与算术操作继续增加** |

gap 因此是双重的：**（a）** 现有轻量化路线的"省 MACs"没有转化为"更快"；**（b）** 现有 dual-path 在两条轴上重复使用同一类算子，而两条轴的依赖结构本来就不同。

论文的答案是：**直接以 RTF 为目标做架构选择**（「In contrast to these approaches, we directly aim to minimize the RTF for practical scenarios」，p.2 §2.2），并给出一个**两轴用不同算子**的 block。

### 2.1 三条贡献（p.1–2 §1）

1. 证明**精简 encoder-decoder** 结构（相对于前作的复杂子带设计）能在不牺牲性能的前提下提升处理速度；
2. 提出 **RNNFormer block**——时间轴 RNN（低复杂度时序建模）+ 频率轴 Transformer（捕获跨频带**全局、非顺序**关系）的高效 dual-path block；
3. 在 VCTK-Demand [14] 上评测，取得 SOTA 性能与**所有对比模型中最低的 RTF**，并通过配置多个速度的模型**建立性能-速度的 Pareto 前沿**（Fig. 1）。

## 3. 这个做法核心 trick 是什么？

### 3.1 输入输出与信号链路

输入 noisy speech $x$ 先变换为复数谱：

$$
X=\operatorname{STFT}(x),\qquad \text{Nfft}=512,\qquad \text{hop}=H\ (\text{逐档不同}),
$$

功率压缩以模拟人耳的动态压缩特性：

$$
X_c=|X|^c\cdot e^{j\angle X},\qquad c=0.3 .
$$

$X_c$ 被当作**两通道张量**（实部与虚部），频率数为 $\text{Nfft}/2$——论文明确写「for simplicity, **we discard the highest frequency bin**」。模型预测两通道 mask $M$，得到

$$
\hat Y_c=M\odot X_c,\qquad
\hat Y=|\hat Y_c|^{1/c}\cdot e^{j\angle \hat Y_c},
$$

最高频点**零填充**后经 iSTFT 合成 $\hat y=\operatorname{iSTFT}(\hat Y)$，再与目标干净语音 $y$ 比较。

> [!note] 与 DCCRN 的复数谱路线对照
> 本篇走的是「**功率压缩的复数谱 + 两通道 mask**」；[[wiki_low_latency/entities/DCCRN]] 走的是复数比率掩蔽（CRM）路线（见 [[wiki_low_latency/concepts/2008.00264-complex-phase-enhancement]]）。两者都在复数域处理、都让 mask 同时作用于幅度与相位，差别在于**是否先做 $|\cdot|^c$ 压缩**、以及 mask 是加性/乘性的具体形式。本篇的 $c=0.3$ 压缩与 [[wiki_low_latency/entities/LaCo-SENet]] 的 $c=0.3$ 输入口径相同。

### 3.2 Trick ①：卷积——时间轴 kernel 恒为 1

论文对延迟机理的说明是本篇最值得记住的一段（p.2 §3）：

> 「Causal convolutional layers with a time-axis kernel size greater than one **introduce latency**, because they require caching past frames to compute the current output frame. For a time-axis kernel size of $k$, a buffer of $k-1$ past frames is stored and concatenated with the current frame before the convolution operation. The latest $k-1$ frames are then stored in memory for the next computation. **These memory operations significantly increase processing time** (Section 5.2).」

因此：

> 「To ensure minimum latency, FastEnhancer **exclusively uses convolutions with a time-axis kernel size of one**. Throughout this paper, all specified kernel sizes and strides for convolutions refer to the **frequency axis**.」

最后一句是一个极重要的口径声明：**全文提到的所有 kernel size 与 stride 都指频率轴**。所以 Table 2/3 与 Fig. 2 里出现的 `Conv(k)`、`StridedConv(k,s)`、`Tr. Conv(k,s)` 中的 $k,s$ 都是频率轴参数，时间轴的卷积永远是 kernel 1。

> [!warning] 一个容易读错的地方
> 消融里的「Time-axis kernel size 3」并不是改了频率轴 kernel 的值，而是**专门把 encoder/decoder 里那些频率轴 kernel=3 的卷积，在时间轴上从 1 改成 3**（p.4 §5.2 原文：「we modified every convolution whose frequency-axis kernel size is 3 in encoder and decoder blocks, enlarging their **time-axis** kernel size from 1 to 3」）。这是给已经存在的频率轴 3×1 卷积补上时间维的第三格。

### 3.3 Trick ②：归一化——BN 可融合，LN 不能

> 「While both methods introduce negligible number of parameters and MACs, **BN can be converted into a simple multiplication-addition operation and fused into adjacent layers at inference time. In contrast, LN cannot be fused in the same manner, increasing the RTF** (Section 5.2). For this reason, we use BN layers throughout our model and fuse them into neighboring layers at inference time.」（p.2 §3）

这条与 Trick ① 构成同一个论证结构：**参数量与 MACs 完全不变，速度却变差。** §5.2 的消融（Table 3）把它做成了硬证据——见 §4.4。

### 3.4 Trick ③：Encoder/Decoder 与 RNNFormer

**Encoder/Decoder**（p.2–3 §3）：pre-encoder 含一个 strided convolution，把频率分辨率从 $\text{Nfft}/2$ 降到 $\text{Nfft}/8$，同时把通道从 2 增到 $C_1$；随后是 $L$ 个 encoder block。decoder 含 $L$ 个 decoder block，后接 post-decoder 用转置卷积恢复频率分辨率。encoder 与 decoder 之间有 **skip connection**。

**Pre/Post RNNFormer**（p.3 §3）：pre-RNNFormer 由 linear（频率 $\text{Nfft}/8\to F$）+ convolution（通道 $C_1\to C_2$）组成；post-RNNFormer 执行逆运算。关键设计：

> 「The weight of the linear layer in pre-RNNFormer is initialized as a **linear filterbank**, and the weight of the linear layer in post-RNNFormer is initialized as a **linear interpolation**. We empirically found that training these weights offered **no performance benefit** over keeping them fixed. Therefore, we **fixed those weights in all experiments**.」

**RNNFormer**：FastEnhancer 含 $K$ 个 RNNFormer block，每个 block 由两个子 block 组成——**时间轴 GRU block** 与**频率轴 MHSA block**。论文对该混合设计的论证是本篇的第二个核心：

> 「This hybrid design is critical for low-latency and high-performance. For the time axis, a GRU is well-suited for streaming inference with minimal latency, whereas an MHSA requires a key-value caching that increases delay. For the frequency axis, an MHSA is ideal as it **can model global relationships and doesn't require caching**.」（p.3 §3）

结构细节：GRU block = unidirectional GRU → convolution → BN → residual skip connection；MHSA block 结构相同，只把 GRU 换成 **4 heads 的 MHSA**；**第一个 MHSA block 的输入加可学习位置编码**。全模型使用 **weight normalization** [20] 与 **SiLU** 激活 [21]。

> [!note] 这里有一处必须点明的因果性论证
> 论文说频率轴 MHSA「doesn't require caching」——意思是**频率轴注意力只在当前帧内部沿频率轴做**，不跨帧，所以不需要 KV cache。这正是它时间上不看未来的结构依据。但论文**没有**逐层 padding 式，也**没有**说明 STFT 前端的帧锚定方式（见 §5.3）。

### 3.5 配置表（Table 1，5 档）

| Size | H | L | K | C1 | C2 | F |
|---|---|---|---|---|---|---|
| Tiny (T) | 256 | 2 | 2 | 24 | 20 | 16 |
| Base (B) | 256 | 2 | 3 | 48 | 36 | 24 |
| Small (S) | 256 | 3 | 3 | 64 | 48 | 36 |
| Medium (M) | **160** | 3 | 4 | 96 | 72 | 48 |
| Large (L) | **100** | 4 | 5 | 128 | 96 | 64 |

- $H$：hop size（STFT）；$L$：encoder/decoder block 数；$K$：RNNFormer block 数；$C_1,C_2$：通道数；$F$：pre-RNNFormer 降维后的频率数。
- **T/B/S 的 hop = 256，M 为 160，L 为 100。**

> [!warning] 本库推读：hop 是延迟的关键变量，但论文没有把它和延迟联系起来
> 论文给出 $H$ 列后**没有任何一句**把它换算成时间或与延迟挂钩。本库按 16 kHz 自行换算：
> - T/B/S：$256/16000=16.00$ ms
> - M：$160/16000=10.00$ ms
> - L：$100/16000=6.25$ ms
>
> 这三组数字直接决定**帧率与延迟下界**（每帧需要积累一个 hop 的新样本才能推进）。**注意：这是本库推读，不是论文主张。** 论文只把 $H$ 当成一个架构超参，从未讨论其延迟含义。

### 3.6 损失（Eq. 1–5 + §4）

$$
\mathcal L=\lambda_1\mathcal L_{\text{mag}}+\lambda_2\mathcal L_{\text{comp}}+\lambda_3\mathcal L_{\text{con}}+\lambda_4\mathcal L_{\text{wav}}+\lambda_5\mathcal L_{\text{pesq}}, \tag{1}
$$

$$
\lambda_1=0.3,\quad \lambda_2=0.2,\quad \lambda_3=0.3,\quad \lambda_4=0.2,\quad \lambda_5=0.001 .
$$

四个谱/波形项（$Y=\operatorname{STFT}(y)$，$Y_c=|Y|^c\cdot e^{j\angle Y}$）：

$$
\mathcal L_{\text{mag}}=\big\lVert\, |Y_c|-|\hat Y_c|\,\big\rVert_2^2, \tag{2}
$$

$$
\mathcal L_{\text{comp}}=\lVert Y_c-\hat Y_c\rVert_2^2, \tag{3}
$$

$$
\mathcal L_{\text{con}}=\lVert Y_c-\operatorname{STFT}_c(\hat y)\rVert_2^2,\qquad \operatorname{STFT}_c(y)=|\operatorname{STFT}(y)|^c\cdot e^{j\angle \operatorname{STFT}(y)}, \tag{4}
$$

$$
\mathcal L_{\text{wav}}=\lVert y-\hat y\rVert_1 . \tag{5}
$$

- $\mathcal L_{\text{mag}}$ **只对幅度取差**（$|Y_c|$ 与 $|\hat Y_c|$ 都是实数非负频谱）；
- $\mathcal L_{\text{comp}}$ 把两个复数谱 $Y_c,\hat Y_c$ 当作**两通道实值张量**后算 MSE（论文原文：「interprets two complex spectrograms $\hat Y_c$ and $Y_c$ as two-channel real-valued tensors, and calculates MSE」）——所以这里的 $\lVert\cdot\rVert_2^2$ 是实张量范数；
- $\mathcal L_{\text{con}}$ 是**一致性损失**：把增强波形重新 STFT + 压缩后，与压缩的干净谱对齐。

第五项 $\mathcal L_{\text{pesq}}$ 是可微 PESQ 损失 [26]。论文给出了**为什么权重取 0.001**：

> 「Optimizing a model solely on the PESQ metric can degrade subjective quality [27]. To prevent this, we use a sufficiently small weighting factor ($\lambda_5=0.001$). We observed that including $\mathcal L_{\text{pesq}}$ improves **not only PESQ but also other objective metrics**.」

引文 [27] 是 de Oliveira 等的 "The PESQetarian: On the relevance of Goodhart's law for speech enhancement"——即"只优化 PESQ 会因 Goodhart 定律失真"。

### 3.7 训练（§4）

- 数据集：VCTK-Demand [14]，**全部音频从 48 kHz 降采样到 16 kHz**；训练时**随机抽 2 秒段**；
- 优化器 **AdamP** [28]，initial lr **0.002**，weight decay **0.01**，batch size **64**；
- **cosine annealing** LR scheduler + **500-step warm-up** [29]；
- **每档模型训练 5 次不同随机种子，报告平均分**（「We trained each model five times with five different random seeds and report the average scores.」）。

> [!question] 5 seeds 只报均值、不报方差
> 论文既然训练了 5 个种子，却**没有报告标准差**。这直接导致 Table 2 中 0.01 量级的差异（例如 FastEnhancer-M 的 P.808 = 3.48 与 S 的 3.49）**无法判断是否显著**——而这个差异恰恰被论文用来论证"少数指标会误导结论"（见 §4.5）。本库记录为「均值可信、显著性不可判定」。

### 3.8 评测口径（§4）

- **导出到 ONNXRuntime** [30]；
- RTF 在**单线程**上测，两个硬件：服务器 CPU **Intel Xeon Gold 6248R**、笔记本 CPU **Apple M1（MacBook Air）**；
- 测试条件：「**under a streaming condition**」；Fig. 1 与 Fig. 3 的 RTF 在 **Xeon** 上测；
- **质量指标**：DNSMOS [31] [32]、SCOREQ（natural speech, full reference mode）[33]、SISDR [34]、PESQ（**P.862.2 without Corrigendum 2**）[35]；
- **可懂度指标**：STOI [36]、ESTOI [37]、WER（用 **Whisper-large-v3-turbo** [38]）。

> [!question] "streaming condition" 没有定义
> 论文只说在 streaming 条件下测 RTF，但**没有定义**这个 streaming 的 **chunk 大小**、**是否有 look-ahead**、**batch 是否为 1**、**是否包含 STFT/iSTFT**。因此这组 RTF 的口径不可完全复现。对比 [[wiki_low_latency/sources/2026/LaCo-SENet 2026]]（明确写 ONNX Runtime、端到端 steady-state、$C=1$ 与 $C\ge7$–$12$ 的完整曲线），本篇的 RTF 口径是明显更粗的。

## 4. 实验里哪个消融最关键？

### 4.1 主结果（Table 2，逐格核对渲染图后照抄）

Table 2 标题在论文里写的是 **"Performance on Voicebank-Demand"**（第 4 页）。

| Model              | Para.(K) | MACs | RTF(Xeon) | RTF(M1)   | P.808    | SIG  | BAK  | OVL  | SCOREQ | SISDR | PESQ | STOI  | ESTOI | WER     |
| ------------------ | -------- | ---- | --------- | --------- | -------- | ---- | ---- | ---- | ------ | ----- | ---- | ----- | ----- | ------- |
| GTCRN^a [9]        | 24       | 40M  | 0.060     | 0.042     | 3.43     | 3.36 | 4.02 | 3.08 | 0.330  | 18.8  | 2.87 | 0.940 | 0.848 | 3.6     |
| LiSenNet^b [11]    | 37       | 56M  | –         | –         | 3.34     | 3.30 | 3.90 | 2.98 | 0.425  | 13.5  | 3.08 | 0.938 | 0.842 | 3.7     |
| LiSenNet^c [11]    | 37       | 56M  | 0.034     | 0.028     | 3.42     | 3.34 | 4.03 | 3.07 | 0.335  | 18.5  | 2.98 | 0.941 | 0.851 | 3.4     |
| FSPEN^d [10]       | 79       | 64M  | 0.046     | 0.038     | 3.40     | 3.33 | 4.00 | 3.05 | 0.324  | 18.4  | 3.00 | 0.942 | 0.850 | 3.6     |
| BSRNN^d [12]       | 334      | 245M | 0.059     | 0.062     | 3.44     | 3.36 | 4.00 | 3.07 | 0.303  | 18.9  | 3.06 | 0.942 | 0.855 | 3.4     |
| **FastEnhancer-T** | 22       | 55M  | **0.012** | **0.013** | 3.42     | 3.34 | 4.01 | 3.06 | 0.334  | 18.6  | 2.99 | 0.940 | 0.850 | 3.6     |
| **FastEnhancer-B** | 92       | 262M | **0.022** | 0.026     | 3.47     | 3.38 | 4.02 | 3.10 | 0.285  | 19.0  | 3.13 | 0.945 | 0.861 | 3.2     |
| **FastEnhancer-S** | 195      | 664M | 0.034     | 0.048     | 3.49     | 3.40 | 4.03 | 3.12 | 0.265  | 19.2  | 3.19 | 0.947 | 0.866 | 3.2     |
| **FastEnhancer-M** | 492      | 2.9G | 0.101     | 0.173     | **3.48** | 3.39 | 4.02 | 3.11 | 0.243  | 19.4  | 3.24 | 0.950 | 0.873 | **2.8** |
| **FastEnhancer-L** | 1105     | 11G  | 0.313     | 0.632     | **3.53** | 3.44 | 4.04 | 3.16 | 0.239  | 19.6  | 3.26 | 0.952 | 0.877 | 3.1     |

**脚注（第 4 页渲染图逐条核对，上标归属明确）**：

- ^a **Evaluated using the official checkpoint.**（→ GTCRN 行）
- ^b **Trained using the official training code. Not streamable because of input normalization and griffin-lim. Thus, RTFs are not reported.**（→ LiSenNet 第一行）
- ^c **To make the model streamable, input normalization and griffin-lim are removed. Trained following the experimental setup in Section 4.**（→ LiSenNet 第二行）
- ^d **Re-implemented and trained following the experimental setup in Section 4 for a fair comparison.**（→ FSPEN 行与 BSRNN 行）

> [!important] 补摄后回看：本篇对 LiSenNet 的两行，是**库内唯一**关于"该模型不可流式"的一手证据
> `LiSenNet 2024`（arXiv:2409.13285）已于 **2026-09-27 完成补摄**，见 [[wiki_low_latency/sources/2024/LiSenNet 2024]] 与 [[wiki_low_latency/entities/LiSenNet]]。对照后的三条结论：
> **① 参数量与 MACs 完全对上**：LiSenNet 原文四处（Abstract / §I / Table I / Table III）一致记为 **37k / 56M**，与本篇 ^b、^c 两行的 `37 / 56M` **无任何差异** ✓。这也是本库**第一个"多份记录完全一致"的超轻量锚点**（与 GTCRN 的三套口径形成鲜明对照）。
> **② 但"有几个版本"对不上**：LiSenNet 原文**只有一个模型**（PESQ 3.07，无流式/非流式之分）；本篇把它拆成 **^b（官方训练代码、不可流式、3.08）** 与 **^c（去掉 input normalization 与 griffin-lim 后重训、可流式、2.98）**。
> ⇒ 最可能的解释：**LiSenNet 原文根本没有"可流式版本"**，^c 是本篇**自行改造并重训**得到的。**L1 目录下的 `^b` 与原文的 3.07 对上（3.08≈3.07），而 `^c` 的 2.98 在原文中不存在** ⇒ **这个"流式化代价"（3.08→2.98，另加 SISDR 13.5→18.5、BAK 3.90→4.03、WER 3.7→3.4 的改善）是本篇独立测量的，不是 LiSenNet 自报的。**
> **③ 原因由本篇独家给出**：LiSenNet 原文**从未**说明 GLA 不可流式，而本篇脚注 ^b 明写「Not streamable because of **input normalization and griffin-lim**」。**这是本库能获得的、关于该模型流式性缺口的唯一一手依据**——LiSenNet 原文对此零说明（详见其 source 页 §5.2 的 `[!question]`）。

> [!contradiction] **FSPEN 的 MACs 在库内有两个不可调和的值——根因就是本篇**
> 本篇记 FSPEN^d [10] 为 **79 / 64M**（并标注 ^d = **Re-implemented and trained**）；而 [[wiki_low_latency/sources/2024/LiSenNet 2024|LiSenNet]] Table I 记 FSPEN [10] 为 **79k / 89M**（转录自 FSPEN 原文）。
> ⇒ **参数量一致（79k）、MACs 差 1.39×**（64M vs 89M），**均不可用舍入解释**。
> **本库判定**：最可能的口径差是 **89M = FSPEN 原文声称值、64M = 本篇重实现后的实测值**；但**两篇都未说明测量条件**（是否含 STFT/iSTFT、batch 是否为 1、chunk 大小），**故不可裁定**。
> ⇒ **按第 14 条"锚点数值先钉口径"规则并列记录、不择一**，并**禁止**把 FSPEN 的 MACs 与任何其他模型的 MACs 放进同一次效率比较。
> **同时注意 FSPEN 的 STOI**：本篇记 **0.942**、LiSenNet 篇也记 **0.942**（表内最高之一），高于 LiSenNet 的 0.939、GTCRN^a 的 0.940、FSPEN 之外的多数基线。
> ⇒ **在 STOI 这一维度上，子带路线的表现并不差**（FastEnhancer 的三档为 0.940/0.945/0.947，其中只有 B、S 明确更高）。**FastEnhancer §2.2 的批评是"RTF 更高"，不是"质量更差"**——引用该段时必须限定批评范围。

> [!note] 渲染图核对结论：抽取文本的两处问题
> 1. **没有重复的 B 配置**。渲染图证实 Table 2 只有 T/B/S/M/L 五个 FastEnhancer 档位；抽取文本（567–581 行与 597–611 行）把 `FastEnhancer-B` 行**重复打印了一次**，属抽取/排版重复。本页按 5 档记录。
> 2. **上标归属只能在渲染图读出**。抽取文本把四条脚注平铺，完全丢失 `a/b/c/d` 落在哪一行；渲染图明确 GTCRN 带 `a`、LiSenNet 两行分别带 `b`/`c`、FSPEN 与 BSRNN 均带 `d`。这一点对基线可比性判定是决定性的（见 §4.3）。

### 4.2 §5.1 的两条关键观察（论文自己写的）

论文在 §5.1 给了两句值得单独引用的话：

> 「In Table 2, FastEnhancer-B outperforms all baseline models on almost every metric. **While having relatively large number of parameters and MACs, its speed-optimized architecture results in the lowest RTFs.**」

对应 Hard Evidence ①：**FastEnhancer-B 的参数量（92K）与 MACs（262M）都高于 GTCRN（24K / 40M）与 FSPEN（79K / 64M），但 RTF 最低（0.022 vs 0.060 / 0.046）。**

> 「As a side observation, compared to FastEnhancer-S, FastEnhancer-M shows **slightly degraded DNSMOS scores despite improved scores on every other metric**. This indicates that **relying on a limited set of objective metrics can lead to misleading conclusions**.」

对应 Hard Evidence ②：**M 档的 P.808 = 3.48 < S 档的 3.49、SIG = 3.39 < 3.40，但 SISDR / PESQ / STOI / ESTOI / WER / SCOREQ / OVL / BAK 全部更好**（仅 BAK 从 4.03 降到 4.02 是同向，OVL 从 3.12 降到 3.11 也是同向——即 P.808、SIG、OVL、BAK 四项 DNSMOS 相关指标在 M 档都略降，而非 DNSMOS 的指标全部更好）。

> [!note] 这一条对本库「人声保留评估」特别有价值
> 它是一份**指标方向不一致**的现成证据：DNSMOS 系（尤其是 SIG 与 P.808）与 SISDR/PESQ 在本例中给出相反信号。本库一贯主张不能只看单一指标判定"人声保留"，篇内这段话正好是论文作者自己的同向佐证。详见 [[wiki_low_latency/concepts/低 SNR 人声保留评估]]。

### 4.3 基线可比性：a/b/c/d 四种来源，**不能混排**

这是本篇最容易误读的地方。四条脚注意味着 Table 2 里的基线**来源不统一**：

| 基线 | 来源 | 是否可流式 | 能否进流式排名 |
|---|---|---|---|
| GTCRN^a | **官方 checkpoint** 直接评测 | 论文未对该行做流式性声明 | 按论文口径参与排名 |
| LiSenNet^b | 官方训练代码训练 | **否**（脚注 b：因 input normalization 与 griffin-lim 而 not streamable） | **不能**（RTF 也因此未报告） |
| LiSenNet^c | 去掉 input normalization 与 griffin-lim 后按 §4 重训 | **是** | 能 |
| FSPEN^d | 按 §4 **重实现重训** | 按论文口径参与排名 | 能 |
| BSRNN^d | 按 §4 **重实现重训** | 按论文口径参与排名 | 能 |

由此产生三条必须写清的读法：

1. **LiSenNet^b 的 SCOREQ 0.425 是表内最高、SISDR 13.5 是表内最低。** 它的 PESQ 3.08 **高于** LiSenNet^c（2.98）与 GTCRN^a（2.87），但**低于** FastEnhancer-B（3.13）。这组"SCOREQ 最高、SISDR 最低"的极端错位，恰恰来自它**不是流式模型**——脚注 b 明写「Not streamable because of input normalization and griffin-lim」，因此**它的数字不能与流式模型并列排名**，其 SCOREQ 0.425 也不例外。
2. **LiSenNet^c 才是可流式版本**，而它相对 ^b 的代价被完整记录下来：**PESQ 3.08 → 2.98、SCOREQ 0.425 → 0.335、SISDR 13.5 → 18.5、BAK 3.90 → 4.03、WER 3.7 → 3.4**。注意方向并不一致：SISDR 与 BAK 反而**变好**，说明"流式化"的影响不是单向退化，而是**改变了误差结构**。这组 a/b/c 三行本身就是"非流式 → 流式"代价的直接教材（见概念页 §4）。
3. **论文对基线来源是坦白的**（脚注写清了官方权重 vs 重训），读者需要自己注意"官方权重"与"作者重训"的数字**不宜直接横比**——重训意味着训练细节、步数、随机性都不完全可控。

> [!note] 教科书级对照：MACs 更高反而更快
> BSRNN^d 的 MACs = 245M，RTF(Xeon) = 0.059；FastEnhancer-B 的 MACs = **262M（更高）**，RTF(Xeon) = **0.022（更低，约 2.7×）**。同一张表内、同一测试条件下，**MACs 高的一方快 2.7 倍**。这是本篇核心论点最干净的一组数据（另一组是下面的 BN→LN 消融）。

### 4.4 最关键的消融：归一化层与卷积 kernel（Table 3）

Table 3 在 FastEnhancer-B 上做两组消融（第 4 页）：

| Ablation | Para.(K) | RTF(Xeon) | RTF(M1) | SISDR | STOI |
|---|---|---|---|---|---|
| **FastEnhancer-B** | 92 | 0.022 | 0.026 | 19.0 | 94.5 |
| Convolution: Time-axis kernel size 3 | 187 | 0.028 | 0.037 | **19.0** | **94.5** |
| Replace BatchNorm to LayerNorm | **92** | **0.028** | **0.029** | 18.9 | 94.5 |

两条消融的论文结论：

- **卷积**：「This necessitated caching operations and significantly increased RTFs, but **no improvement in quality or intelligibility was observed**」（p.4 §5.2）。数据上看：Para. 92→187（翻倍）、RTF(Xeon) 0.022→0.028（+27%）、RTF(M1) 0.026→0.037（**+42%**），而 **SISDR 19.0→19.0、STOI 94.5→94.5 一格不动**。
- **归一化**：「**while this maintained speech quality and intelligibility, it increased RTFs, despite having the same number of parameters and MACs.** This result confirms that using BNs and fusing them into adjacent layers is the most efficient option.」

> [!note] 这是本库最值得引用的一组"零算术代价、纯速度代价"证据
> BN→LN 的替换**不改变参数量、不改变 MACs、几乎不改变质量**（SISDR 19.0→18.9，STOI 不变），但 RTF(Xeon) 从 0.022 涨到 0.028（**+27%**）、RTF(M1) 从 0.026 涨到 0.029（**+12%**）。它唯一排除的解释就是**算术量**——剩下的解释只能是**算子可融合性与内存操作**。这条证据直接支撑概念页第一节的核心命题。注意 M1 上的涨幅（+12%）明显小于 Xeon（+27%），说明这个惩罚**与硬件/算子实现相关**，不是纯算法属性。

### 4.5 另外两组消融（Fig. 3 + §5.2）

![[wiki_low_latency/assets/2509.21867/2509.21867-page4.png]]

> 图注：原论文第 4 页页面渲染（含 Table 2、Table 3、Fig. 3 与 §5–§6 正文）。上方为 Table 2 主结果表与四条脚注（**a/b/c/d 的上标归属在此可核**），中部左为 Table 3 消融表，中部右为 **Fig. 3**（RTF vs SISDR 与 RTF vs STOI 的两张并排折线图）。Fig. 3 的图例为 **RNNFormer / DPRNN / DPTransformer**，横轴 RTF 为**对数刻度** `0.0125 / 0.025 / 0.05 / 0.1 / 0.2 / 0.4`，**越靠左越快**。

**第三组：RNNFormer → DPRNN**（把频率轴 MHSA 换成频率轴 GRU）：

> 「While **STOI scores were similar**, DPRNNs clearly **degraded SISDR** compared to the proposed RNNFormers (Fig. 3). This demonstrates the superiority of self-attention over a recurrent approach for frequency modeling.」（p.4 §5.2）

Fig. 3 渲染图可见：DPRNN 曲线在 SISDR 子图上**整体明显低于** RNNFormer 与 DPTransformer 两条（本页读图：在 RTF 0.0125–0.2 区间低约 0.4–0.6 dB），而在 STOI 子图上三条线接近——与论文"STOI 相近、SISDR 明显下降"的描述一致。

**第四组：RNNFormer → Dual-Path Transformer**（把时间轴 GRU 换成时间轴 MHSA）：

> 「we constructed Dual-Path Transformers by replacing the time-axis GRU blocks with time-axis MHSA blocks with a **look-behind of 31 frames (corresponding to 0.5 seconds)**. Although **DPTs have fewer parameters than RNNFormers**, they require **key-value caching, resulting in significantly increased RTFs**. This result suggests that a recurrent approach is a more efficient choice than self-attention for temporal modeling in a streaming scenario.」（p.4 §5.2）

> [!question] 「31 帧 = 0.5 秒」这个换算反推出的帧长与 Table 1 的 T/B/S 不符
> 1 帧 ÷ 0.5 s = 2 ms/帧 ⇒ 500 帧/s。但按 Table 1 的 T/B/S 档 $H=256$ @16 kHz = 16 ms/帧（62.5 帧/s）、M 档 160 samples = 10 ms（100 帧/s）、L 档 100 samples = 6.25 ms（160 帧/s），**没有任何一档是 2 ms/帧**。论文未说明 DPT 消融用的是哪个 hop，也未说明这 31 帧是按哪一种帧率计的。本页**不猜测**，只记录这个不一致（论文自身未解释）。

> [!note] DPT 消融的论证结构很干净
> 「参数量更少」+「RTF 更高」+ 唯一变量是"是否需要 KV cache"——这与卷积消融（内存操作）、归一化消融（可融合性）构成**同一个论证模板的三次重复**：**参数量与 MACs 都不能预测速度，决定速度的是内存操作与 cache 结构。**

### 4.6 结论（§6）

> 「We made careful architectural choices, including convolutional layers with time-axis kernel size of 1, **normalization layers that can be fused into other layers at inference**, time RNNs, and frequency transformers. Our results demonstrate that FastEnhancer significantly outperforms prior works in terms of speech quality and intelligibility while achieving **the fastest inference speed on a single CPU thread**. This makes our model a highly practical and fast solution for real-world, on-device deployment.」

## 5. 这个方向还剩什么问题没解决？（future work / limitation）

### 5.1 延迟账本：本库必须自己算，且要给"未报告"清单

**论文通篇没有给出任何"算法延迟 XX ms"的表述。** 它只给 RTF 与 hop size。本库逐项补齐：

| 字段 | FastEnhancer 证据 / 边界 |
|---|---|
| 采样率 | 16 kHz（全部音频从 48 kHz 降采样，p.3 §4） |
| Nfft / 窗长 | $\text{Nfft}=512$ ⇒ 窗长 32.0 ms @16 kHz（**本库按 Nfft 与采样率推得**；论文未换算） |
| hop $H$ | T/B/S = 256 samples；M = 160；L = 100（Table 1） |
| hop 换算（**本库推读**） | T/B/S = **16.00 ms**；M = **10.00 ms**；L = **6.25 ms**（$H/16000$，论文**没有**做这个换算，也**没有**把它和延迟关联） |
| STFT center / 帧锚定 / padding | **未报告**。若 center=True，前端额外含 $W/2=$ **16 ms** 未来样本（本库按 $\text{Nfft}/2$ 推得）；论文对此完全沉默 |
| 频率点数 | $\text{Nfft}/2=256$，**最高频点被丢弃**（p.2 §3） |
| look-ahead / group delay | **未报告** |
| warm-up / state reset / flush | **未报告** |
| 长流稳定性 / 丢帧策略 | **未报告** |
| chunk 大小 | **未报告**。论文只在 §3 说模型能 "frame-by-frame manner" 处理谱，没有给流式推理的 chunk 配置 |
| batch=1 证据 | **未报告**（RTF 只说 "single thread" 与 "under a streaming condition"） |
| 算法延迟（论文口径） | **不存在**——论文没有任何延迟数字 |
| 计算 | ONNXRuntime [30]，单线程，Xeon Gold 6248R 与 Apple M1；RTF 只给**单值**，无 p50/p95/p99 |
| 峰值内存 / SRAM | **未报告** |
| 量化 | **未报告**（无 INT8/定点结果） |
| 功耗 | **未报告** |
| 端到端 | ADC/DMA、I/O buffer、线程调度、DAC/playout、capture-to-playback、underrun/overrun **全部未报告** |
| deadline | deadline miss、p99、worst-case margin **全部未报告** |

> [!warning] 延迟下界的量级是"十几毫秒"，不是 2 ms——这是本库推读
> 由 Table 1 的 $H$ 列与 16 kHz 换算，T/B/S 档的帧周期为 16 ms，M 为 10 ms，L 为 6.25 ms。若 STFT 采用 center=True 帧锚定，前端还要再加 $W/2=16$ ms 的未来样本。因此按本库口径，**这个模型的算法延迟下界处于"十几毫秒"量级**——比约 2 ms 目标**高出一个量级或更多**。
> **必须强调：论文没有做出任何这类换算或表述**，以上全部是本库依据 Table 1 的 $H$ 列与 Nfft 的**推读**，且因 center 方式未报告而不能确定为定论。本页不把它写成论文主张。

> [!note] RTF 是吞吐指标，不是延迟指标
> 论文声称在 "streaming condition" 下测 RTF，但**没有定义**这个 streaming 的 chunk 大小与是否有 look-ahead。即便 RTF = 0.012（T 档），它说明的也只是**平均处理时间 ≈ 0.012 × 音频时长**，与"每帧必须在 deadline 前算完"是两件事。本库口径见 [[wiki_low_latency/concepts/严格因果与算法延迟]]：**RTF < 1 只能证明平均吞吐足够，不能替代 deadline 或 p99 证据。**

### 5.2 因果性判定：结构证据较强，但仍缺逐层 certificate

**论文给的是结构级证据**（这比许多论文强）：

| 结构证据 | 出处 | 含义 |
|---|---|---|
| 全模型时间轴卷积 kernel = 1 | p.2 §3（并明确声明"全文 kernel/stride 均指频率轴"） | 时间轴上无 $k-1$ 帧缓存需求 |
| 时间轴用**单向** GRU | p.2–3 §3（"a unidirectional GRU"） | 递归状态只依赖过去 |
| 时间轴不用 MHSA | p.2 §2.1、p.3 §3（KV cache 会增加延迟） | 无跨帧 KV cache |
| 频率轴 MHSA「doesn't require caching」 | p.3 §3 | 注意力只在当前帧内沿频率轴做，时间上不看未来 |
| 频率轴无时间顺序 | p.2 §2.1 | 频率轴注意力不引入时间方向的顺序依赖 |

**但它缺的**：

- 没有**逐层 padding / state certificate**（哪一层用什么 padding、padding 是否为零、state 如何在帧间更新，全部未给）；
- 没有说清 **STFT 前端的帧锚定**（center 与否），这直接影响前端是否含未来样本；
- 没有**样本级**的可读性声明（如 LaCo-SENet 的「chunk-wise streaming outputs are numerically identical to full-sequence outputs」）。

**本页判定：`paper-claimed-causal`（结构证据较强，仍缺逐层 certificate 与前端账本）。**

> [!note] 它是"缓存型"流式，与逐帧重置的 PSMSE 正好相反
> 时间轴 GRU 维护**跨帧递归状态**（$h$ 在帧间传播）；频率轴 MHSA **逐帧无状态**（每帧内部独立完成）。这与 [[wiki_low_latency/entities/PSMSE]] 的"每帧重新初始化 Mamba state、帧间无状态"是**两种不同的流式语义**，正好构成本库一组对照。详见 §5.5。

### 5.3 人声保留：指标组合较全，但分层维度空白

**这是本篇的正面资产**（本库应予肯定）：

- 报了 DNSMOS 的 **SIG / BAK / OVL 三项**（多数论文只报 OVL）——SIG 直接关系人声保留；
- 报了 **WER**（用 Whisper-large-v3-turbo）——本库把 ASR WER 列为可懂度的关键字段；
- 报了 **ESTOI**（比 STOI 对调制噪声掩蔽更敏感）；
- 报了 **SCOREQ**（natural speech, full reference mode）——一个较新的全参考质量指标。

以上组合是本库目前**最全的可懂度/保留指标组合之一**。

**但缺**（逐项列入本库验收字段）：

- 负 SNR 分层（−10 / −5 / 0 / 5 dB）**未报告**；
- 噪声类型分层 **未报告**；
- babble / 竞争说话人 **未报告**；
- false-suppression **未报告**；
- SPP / VAD 校准 **未报告**；
- F0 / formant / prosody continuity **未报告**；
- voiced energy 保留 **未报告**；
- 听感 MOS（主观）**未报告**（只有客观指标）。

> [!note] 一个值得本库记录的读法：BAK 几乎不动，SIG 在涨
> 从 T → L，**BAK 从 4.01 到 4.04（非常平）**，而 **SIG 从 3.34 到 3.44（明显上升）**；P.808 从 3.42 到 3.53。说明从 T 到 L 的规模增长，**增益主要来自语音保真度（SIG）与整体质量，而不是更强的噪声抑制（BAK）**。BAK 在 4.01–4.04 之间几乎饱和，暗示这个架构的噪声抑制能力在 T 档就已基本到位，后续增加容量主要花在"把语音保得更准"上。
> 这一点论文**没有讨论**，是本页读出的。它对本库的意义是：如果目标是"低 SNR 下的人声保留"，那么这篇的信号是**正面**的（SIG 随容量单调上升）；但如果目标是"更强的抑噪"，BAK 的天花板提示不要指望靠加容量解决。

### 5.4 论文自身的问题与存疑点

> [!question] 数据集名称在论文内部不一致
> **Table 2 的标题写的是 "Performance on Voicebank-Demand"**（第 4 页），而 **§4 正文写的是 "VTCK-Demand dataset [14]"**（第 3 页，注意是 **VTCK** 而非 VCTK），引文 **[14] 是 Valentini-Botinhao 等的 VoiceBank-DEMAND 论文**（"Investigating RNN-based speech enhancement methods for noise-robust text-to-speech", ISCA Speech Synthesis Workshop 2016）。
> 即：**同一数据集，论文里出现两种写法**（"Voicebank-Demand" / "VTCK-Demand"），且 "VTCK" 疑为 "VCTK" 的笔误。本库**不静默修正**，按原文并列记录此矛盾。另需注意引文 [14] 的标题指向的是 **TTS 的噪声鲁棒性研究**，而 §1 §4 把它当作 VCTK-Demand 数据集引用。

> [!question] Fig. 1 与 FastEnhancer 配置的对应关系未说明
> Fig. 1 只画了 5 个模型（FastEnhancer / BSRNN / GTCRN / LiSenNet / FSPEN），横轴同时出现 0.0125 与 0.4（**跨 32 倍**）。但**FastEnhancer 的哪个配置对应图上哪个点没有说明**——是一个点（T 档？）还是把 5 档都画了？如果只画一个点，那么"Pareto 前沿"的表述就只由单点支撑；如果画了 5 档，图例上应当有区分但论文未说明。本页记录为**图注与图例信息不足以确定**。

> [!question] "state-of-the-art" 的主张范围需要严格限定
> 论文写「achieves state-of-the-art speech quality and intelligibility」，但其对比集合只有 **5 个低复杂度模型**（GTCRN / LiSenNet / FSPEN / BSRNN，加自身），且 **FastEnhancer-M 的 MACs 达 2.9G、L 达 11G**——分别是 GTCRN（40M）的 **72×** 与 **275×**。在这个参数与算力量级上，再与 GTCRN / LiSenNet 比较已不完全公平。
> 论文用 Pareto 前沿的表述（「we establish a new Pareto frontier」，p.2 §1）是**合理**的；但**不能**把它读成"以极小代价击败所有前作"。本库记录为：**在"性能-速度"平面上，FastEnhancer 各档位与前作共同构成一条前沿；L 档的性能是在 275× 于 GTCRN 的算力下取得的。**

> [!question] Pareto 前沿没有形式化定义
> 论文没有给出 Pareto 前沿的数学定义、也没有覆盖度指标（如 hypervolume），只是把点画在 Fig. 1 上。因此"建立新前沿"是一个**定性图注主张**，不是可量化验证的结论。

> [!question] 5 seeds 均值无方差；RTF 无分位数
> 论文明确说「trained each model five times with five different random seeds and report the average scores」，但**没有报告标准差**，因此 0.01 量级的差异（如 M 的 P.808 3.48 vs S 的 3.49）**无法判断显著性**。此外 RTF 只报**单值**，无 p50/p95/p99，无 deadline miss，无 underrun/overrun，无峰值 RAM/SRAM，无功耗，无 INT8 量化结果。

### 5.5 与约 2 ms 约束的距离

**无法从论文数据直接判定**（因为论文没有任何延迟数字），但可以定性说：

- hop 处在 **16 ms（T/B/S）/ 10 ms（M）/ 6.25 ms（L）** 量级；
- STFT 帧锚定（center 与否）**未报告**，若 center=True 则前端另有 16 ms 未来样本；
- 因此**它比约 2 ms 目标高一个量级或更多**（本库推读）。

**本库不能把它列为 2 ms 候选**，但可以把它列为**「速度优化」与「延迟账本」两个方法论议题的最佳样本**——它是"MACs 低 ≠ 快"这一命题最完整的论据集合，同时它的延迟账本空白本身就是一个反面教材。

## 6. 本论文在库中的位置关联（cross-reference matrix）

| 关系 | 库中论文/概念 | 关联与差异 |
|---|---|---|
| **前身/基石（被明确点名）** | [[wiki_low_latency/entities/DPCRN]]、[[wiki_low_latency/sources/2021/DPCRN Low-Latency Direction 2021]]、[[wiki_low_latency/concepts/2107.05429-dual-path-recurrent-context]] | 论文 §2.2 点名 DPCRN [7] 与 TRU-Net [8] 引入 TF-domain U-Net + DPRNN，是其出发点；而本篇要否定的正是 **DPRNN 用在频率轴**这件事（§2.1）。即：**同一血脉的下一代，但砍掉了频率轴 RNN** |
| **同分支竞品（被挑战的子带路线）** | [[wiki_low_latency/entities/FSB-LSTM]]、[[wiki_low_latency/sources/2023/FSB-LSTM 2023]]、[[wiki_low_latency/concepts/2304.08707-full-sub-band-modeling]] | **直接冲突**：sub-band / full-band 集成建模的立论是"分频带建模更高效"；本篇 §2.2 明确批评子带方案（BSRNN/FSPEN/GTCRN/LiSenNet）「increased architectural complexity and memory operations paradoxically led to higher RTFs」，并主张简单的 encoder-decoder 就够。两条路线需要并读 |
| **同分支竞品（复数谱/相位）** | [[wiki_low_latency/entities/DCCRN]]、[[wiki_low_latency/concepts/2008.00264-complex-phase-enhancement]] | 本篇是「功率压缩复数谱 + 两通道 mask」；DCCRN 是 CRM 路线。都在复数域处理，但压缩方式与输出形式不同 |
| **同分支竞品（嵌入式实时）** | [[wiki_low_latency/entities/DeepFilterNet2]]、[[wiki_low_latency/sources/2022/DeepFilterNet2 2022]]、[[wiki_low_latency/concepts/2205.05474-deep-filtering]] | 嵌入式实时低复杂度参照；DeepFilterNet 系在文献 [7] 中被本篇列为 DPRNN 家族的一部分（经 DPCRN 脉络） |
| **同分支竞品（低时延 STFT 前端）** | [[wiki_low_latency/entities/STFT-Very-Low-Latency-SE]]、[[wiki_low_latency/sources/2022/STFT-Domain Very Low Algorithmic Latency 2022]]、[[wiki_low_latency/concepts/2204.09911-short-asymmetric-stft]] | 本篇的 hop 换算（256 / 160 / 100 samples）应与之对照：那篇把时延预算拆在 analysis/synthesis 窗上，本篇则**完全没有做时延换算**。两篇构成"有前端账本 vs 无前端账本"的对照 |
| **同分支竞品（感知驱动实时）** | [[wiki_low_latency/entities/PercepNet]]、[[wiki_low_latency/sources/2020/PercepNet Low-Latency Direction 2020]] | 同属低复杂度实时增强；本篇的 SIG/BAK/OVL + WER + ESTOI 组合比典型的单指标报告更全 |
| **最严因果审计尺子（口径同构）** | [[wiki_low_latency/entities/LaCo-SENet]]、[[wiki_low_latency/sources/2026/LaCo-SENet 2026]]、[[wiki_low_latency/concepts/2606.19688-latency-configurable-asymmetric-padding]] | **RTF 口径同构**：两者都在**单线程 Intel Xeon** 上测（LaCo-SENet 是 Xeon **Silver 4510**，本篇是 Xeon **Gold 6248R**），都用 ONNXRuntime。但 LaCo-SENet 给出逐层 padding 分配式与算法时延公式，本篇只有 RTF。**量本篇的因果性必须用 LaCo-SENet 的尺子**：逐层 certificate 一栏本篇是空的 |
| **状态语义正反对照** | [[wiki_low_latency/entities/PSMSE]]、[[wiki_low_latency/sources/2026/PSMSE 2026]]、[[wiki_low_latency/concepts/S2542660526001769-spiking-mamba-streaming]] | **两种流式语义**：PSMSE **逐帧重置**（Mamba state 不跨帧）；本篇 **GRU 状态跨帧传播 + 频率轴逐帧无状态**。同是"流式"，状态存续语义正好相反 |
| **跨帧固定状态流的另一例** | [[wiki_low_latency/entities/RT-SEMamba]]、[[wiki_low_latency/sources/2026/RT-SEMamba 2026]]、[[wiki_low_latency/concepts/2608.12099-mamba-distillation]] | 同属"跨帧维护固定状态"的流式路线，可与本篇的跨帧 GRU 状态并读 |
| **动态算力子群（同一类论点的另一侧）** | [[wiki_low_latency/entities/D-GRU]]、[[wiki_low_latency/concepts/2408.12425-dynamic-gated-rnn]]、[[wiki_low_latency/entities/Skip-DPCRN]]、[[wiki_low_latency/concepts/2207.11108-inference-skipping-parallel-rnn]] | D-GRU 论文批评 Skip RNN「每步算力波动不适合硬件实时约束」，与本篇「结构可融合性决定实际速度」是**同一类论点的不同侧面**：都主张"名义算力/平均算力不决定实时性"，都指向"可预测性/可融合性" |
| **统一低时延对照框架** | [[wiki_low_latency/entities/CRUSE-Latency-Study]]、[[wiki_low_latency/sources/2024/Ultra-Low Latency Speech Enhancement Comprehensive Study 2024]] | 该研究建立统一的前端/模型对照框架，本篇的 5 档 Pareto 点是很好的素材，但需要它的 $H$ 列与 Nfft 才能把点放到统一的延迟轴上 |
| **非对称 STFT + 复用** | [[wiki_low_latency/entities/RT-Tango]]、[[wiki_low_latency/sources/2026/RT-Tango 2026]] | 同属速度/算力优化路线；RT-Tango 用固定间隔复用 mask，本篇用免缓存算子选择 |
| **缺口对照（延迟账本为空）** | [[wiki_low_latency/sources/2024/Tsunoo Causal SSL Semantic 2024]]、[[wiki_low_latency/entities/Tsunoo-Causal-SSL-SE]] | 上一篇同样"延迟账本为空"；本篇至少给了 RTF 与 hop（虽未换算），可作对照 |
| **概念页** | [[wiki_low_latency/concepts/2509.21867-speed-optimized-streaming-design]] | 展开"MACs/RTF ≠ 延迟""可融合性是一等约束""两轴选不同算子""非流式→流式代价"四条可复用命题 |
| **实体页** | [[wiki_low_latency/entities/FastEnhancer]] | 架构配置、状态与因果性、低时延账本、结果与证据边界 |
| **顶层页** | [[wiki_low_latency/overview]]、[[wiki_low_latency/index]] | 本页为 overview 的"平均算力 ≠ 可用算力"条目提供最完整的一组证据 |

## 7. 一句话总结"江湖地位"

> **2025 | 流式语音增强 / 速度优化 | 用"精简 encoder-decoder + RNNFormer（时间 GRU + 频率 MHSA）"证明「降 MACs 的轻量化路线反而拖慢实际推理」，并以两组硬消融——时间轴 kernel 1→3 使 Para. 翻倍而 SISDR/STOI 一格不动、BN→LN 在参数量与 MACs 完全不变下把 RTF 抬高 27%——给出本库关于"可融合性与内存操作决定速度"的最强证据；FastEnhancer-B 以 92K/262M 的资源取得 0.022 的最低 RTF（MACs 比 GTCRN 高 6.5× 而快 2.7×）→ 是"性能-速度 Pareto 前沿"子方向的标尺与"MACs ≠ 速度"命题的教科书样本；但它**通篇没有任何算法延迟数字**、STFT 帧锚定未报告、hop 从未与延迟关联，按本库口径其延迟下界在"十几毫秒"量级（推读），距约 2 ms 目标尚有一个量级以上。**

## 参考资料

- [arXiv:2509.21867](https://arxiv.org/abs/2509.21867)
- 代码与预训练权重：<https://github.com/aask1357/fastenhancer>
- 文档站：<https://aask1357.github.io/fastenhancer/>
- 本地原件：`raw/papers/low_latency_causal_se/2509.21867.pdf`
- 本地文本抽取：`tmp/pdf_extract/2509.21867.txt`
- 页面渲染核对：`wiki_low_latency/assets/2509.21867/`（page1–page5；本页嵌入 page4 用于核对 Table 2/3 与 Fig. 3，另核对了 page1 的 Fig. 1 与 page3 的 Fig. 2/Table 1/Eq. 1–5）
- 论文内关键引用：[1] 谱减 Boll 1979；[6] DPRNN；[7] DPCRN；[8] TRU-Net；[9] GTCRN（ICASSP 2024）；[10] FSPEN（ICASSP 2024）；[11] LiSenNet（ICASSP 2025）；[12] BSRNN；[13] band-split RNN；[14] Valentini-Botinhao 等 VoiceBank-DEMAND（ISCA SSW 2016）；[15] Mamba for SE；[16] xLSTM-SENet；[17] [18] Dual-path Transformer；[19] streaming DPT；[20] weight normalization；[21] GELU/SiLU；[22] BatchNorm；[23] LayerNorm；[24] GRU；[25] MHSA；[26] torch-pesq；[27] PESQetarian；[28] AdamP；[29] cosine annealing + warm-up；[30] ONNXRuntime；[31] [32] DNSMOS / DNSMOS P.835；[33] SCOREQ；[34] SISDR；[35] PESQ P.862.2；[36] STOI；[37] ESTOI；[38] Whisper-large-v3-turbo
