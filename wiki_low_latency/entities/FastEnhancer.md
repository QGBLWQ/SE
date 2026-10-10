---
title: FastEnhancer
type: entity
created: 2026-09-26
updated: 2026-09-26
tags:
  - speech-enhancement
  - single-channel
  - streaming
  - rnnformer
  - dual-path
  - time-gru-frequency-mhsa
  - power-compression-complex-spectrum
  - batch-normalization-fusion
  - fusability
  - speed-optimized
  - onnx-runtime
  - paper-claimed-causal
  - 16ms-hop
  - macs-not-latency
sources:
  - [[wiki_low_latency/sources/2025/FastEnhancer 2025]]
related:
  - [[wiki_low_latency/concepts/2509.21867-speed-optimized-streaming-design]]
  - [[wiki_low_latency/concepts/严格因果与算法延迟]]
  - [[wiki_low_latency/concepts/低时延前端与延迟账本]]
  - [[wiki_low_latency/concepts/低 SNR 人声保留评估]]
  - [[wiki_low_latency/concepts/2107.05429-dual-path-recurrent-context]]
  - [[wiki_low_latency/entities/DPCRN]]
  - [[wiki_low_latency/entities/PSMSE]]
  - [[wiki_low_latency/entities/LaCo-SENet]]
---

# FastEnhancer

## 定义

**FastEnhancer** 是 Ahn 等 2025 年提出的单通道、16 kHz、**流式**时频域语音增强模型族（5 档：T / B / S / M / L）。它的核心主张是：**在降低参数量与 MACs 之外，必须把"实际推理速度"当作独立的第一目标**——因为近年的轻量化路线（子带分解、精细 encoder-decoder、grouped DPRNN）虽然降下了参数量与 MACs，却因增加了**内存操作与架构复杂度**而**拖慢了实际推理**（论文 §1 / §2.2）。

它的架构答案是一个精简 encoder-decoder + **RNNFormer block**（时间轴**单向 GRU** + 频率轴 **4-head MHSA** 的 dual-path），并且把三个"零算术代价、纯速度代价"的结构选择写进设计原则：**时间轴卷积 kernel 恒为 1**、**全模型用可融合的 BN**、**时间轴不用需 KV cache 的注意力**。

论文口径：Base 档 **92K 参数 / 262M MACs**，在单线程 Intel Xeon Gold 6248R 上 **RTF 0.022**（M1 上 0.026）。论文**没有给出任何算法延迟数字**，本库判定为 `paper-claimed-causal`，且**延迟账本严重不完整**（hop 已知但从未与延迟关联、STFT 帧锚定未报告）。

> [!note] 一句话抓住它
> FastEnhancer 是"**MACs 低 ≠ 跑得快**"这一命题最强的论据集合：它的 MACs 比 GTCRN 高 6.5 倍，RTF 却低 2.7 倍；把 BN 换成 LN（参数量与 MACs 一个没变）就会慢 27%。

## 证据

| 属性 | 本地 PDF 证据 |
|---|---|
| 任务 | 单通道 monaural speech enhancement；面向在线会议、智能家居、助听器；16 kHz（p.1 Abstract / §1） |
| 输入 | noisy speech $x$ → $\operatorname{STFT}$，**Nfft = 512**，hop = $H$；功率压缩 $X_c=|X|^c\cdot e^{j\angle X}$，**$c=0.3$**；当作**两通道张量**（实/虚部），频率数 **Nfft/2 = 256**，**最高频点被丢弃**；p.2 §3 |
| 输出 | 预测两通道 mask $M$ → $\hat Y_c=M\odot X_c$ → 解压 $\hat Y=|\hat Y_c|^{1/c}\cdot e^{j\angle\hat Y_c}$ → **最高频点零填充** → $\hat y=\operatorname{iSTFT}(\hat Y)$；p.2 §3 |
| 卷积约束 | **时间轴 kernel 恒为 1**；论文明确声明「all specified kernel sizes and strides for convolutions refer to the **frequency axis**」；理由：时间轴 kernel $k>1$ 需缓存 $k-1$ 帧，这些内存操作显著增加处理时间；p.2 §3 |
| 归一化 | 全模型 **BN**，推理期**融合进相邻层**；理由：BN 可转成一次乘加、LN 不能融合；p.2 §3 |
| Encoder | pre-encoder：strided conv 把频率分辨率 $\text{Nfft}/2\to\text{Nfft}/8$，通道 $2\to C_1$；随后 $L$ 个 encoder block；p.2 §3 |
| Decoder | $L$ 个 decoder block + post-decoder 转置卷积恢复频率分辨率；encoder-decoder 间有 skip connection；p.2 §3 |
| Pre/Post RNNFormer | pre = linear（频率 $\text{Nfft}/8\to F$）+ conv（$C_1\to C_2$）；post 为逆运算；**pre 的 linear 权初始化成 linear filterbank、post 的初始化成 linear interpolation，且全部实验中固定不动**（论文发现训练它们无收益）；p.3 §3 |
| RNNFormer | $K$ 个 block；每 block = **时间轴单向 GRU block** + **频率轴 4-head MHSA block**；GRU block = unidirectional GRU → conv → BN → residual skip；MHSA block 同构但把 GRU 换成 MHSA；**第一个 MHSA block 输入加可学习位置编码**；p.3 §3 |
| 全局 | weight normalization [20] + SiLU 激活 [21]；p.2 §3 |
| 损失 | $\mathcal L=\lambda_1\mathcal L_{\text{mag}}+\lambda_2\mathcal L_{\text{comp}}+\lambda_3\mathcal L_{\text{con}}+\lambda_4\mathcal L_{\text{wav}}+\lambda_5\mathcal L_{\text{pesq}}$，Eq. (1)；$\lambda=\{0.3,0.2,0.3,0.2,0.001\}$；p.3 §4 |
| $\mathcal L_{\text{mag}}$ | $\lVert\,|Y_c|-|\hat Y_c|\,\rVert_2^2$，Eq. (2)——**只对幅度取差** |
| $\mathcal L_{\text{comp}}$ | $\lVert Y_c-\hat Y_c\rVert_2^2$，Eq. (3)——把两个复数谱当**两通道实值张量**后算 MSE |
| $\mathcal L_{\text{con}}$ | $\lVert Y_c-\operatorname{STFT}_c(\hat y)\rVert_2^2$，Eq. (4)，其中 $\operatorname{STFT}_c(y)=|\operatorname{STFT}(y)|^c\cdot e^{j\angle\operatorname{STFT}(y)}$ |
| $\mathcal L_{\text{wav}}$ | $\lVert y-\hat y\rVert_1$，Eq. (5)——波形域 MAE |
| $\mathcal L_{\text{pesq}}$ | 可微 PESQ [26]；因"只优化 PESQ 会损伤主观质量"[27] 而取**极小权重 0.001**；论文观察加入它也提升了其他客观指标；p.3 §4 |
| 训练数据 | VCTK-Demand [14]，**48 kHz → 16 kHz 降采样**；训练随机抽 **2 秒段**；p.3 §4。**注意 §4 写 "VTCK-Demand"（疑为 VCTK 笔误），Table 2 标题写 "Voicebank-Demand"** |
| 优化 | **AdamP** [28]，initial lr **0.002**，weight decay **0.01**，batch **64**；cosine annealing + **500-step warm-up** [29]；p.3 §4 |
| 种子 | **每档训练 5 个不同随机种子，报平均分**（**未报标准差**）；p.3 §4 |
| 评测栈 | 导出 **ONNXRuntime** [30]；**单线程**；Intel Xeon Gold 6248R + Apple M1（MacBook Air）；「under a streaming condition」；Fig. 1/Fig. 3 的 RTF 在 Xeon 上测；p.3 §4 |
| 指标 | DNSMOS [31] [32]（含 **P.835 的 SIG/BAK/OVL**）、SCOREQ（natural speech, full reference）[33]、SISDR [34]、PESQ（P.862.2 without Corrigendum 2）[35]、STOI [36]、ESTOI [37]、**WER（Whisper-large-v3-turbo）**[38]；p.3 §4 |

## 架构

~~~text
noisy speech x
  → STFT (Nfft=512, hop=H)                                [B, 2, Nfft/2=256, T]
  → Power Comp  Xc = |X|^0.3 · e^{j∠X}  （当 2 通道实张量）
  ┌───────────────────────────── FastEnhancer ─────────────────────────────┐
  │  Pre Encoder : StridedConv(k, s)                        频率 Nfft/2 → Nfft/8
  │                + BN + SiLU                              通道 2 → C1
  │                                              [B, C1, Nfft/8, T]
  │  EncoderBlock × L : 1x1Conv(C1→C1) + BN + SiLU
  │  ─────────────────────────────────────────────────────────────────────
  │  Pre RNNFormer : Linear(Nfft/8 → F)  ← 权固定为 linear filterbank
  │                + 1x1Conv(C1 → C2) + BN   [B, C2, F, T]
  │  ─────────────────────────────────────────────────────────────────────
  │  RNNFormer × K :
  │     ┌─ Time GRU Block ──┐   ┌─ Frequency MHSA Block ──┐
  │     │  Time GRU         │   │  Frequency MHSA (4 heads)│
  │     │  1x1Conv          │   │  1x1Conv                 │
  │     │  BatchNorm        │   │  BatchNorm               │
  │     │  (+ residual skip)│   │  (+ residual skip, 首块加 PE) │
  │     └───────────────────┘   └──────────────────────────┘
  │      时间轴：递归、无 cache   频率轴：全局、不需 cache
  │  ─────────────────────────────────────────────────────────────────────
  │  Post RNNFormer : Linear(F → Nfft/8)  ← 权固定为 linear interpolation
  │                + 1x1Conv(C2 → C1) + BN
  │  DecoderBlock × L : 1x1Conv(C1→C1) + BN + SiLU
  │  Post Decoder : Tr. Conv(k, s) + BN + SiLU   频率 Nfft/8 → Nfft/2, 通道 C1 → 2
  └─────────────────────────────────────────────────────────────────────────┘
  → 两通道 mask M                                   [B, 2, 256, T]
  → Ŷc = M ⊙ Xc → Power Decomp Ŷ = |Ŷc|^{1/0.3} · e^{j∠Ŷc}
  → 最高频点零填充 → iSTFT (hop=H) → enhanced speech ŷ

  全模型 kernel / stride 均指频率轴；时间轴卷积恒为 kernel 1（无需缓存 k−1 帧）
~~~

![[wiki_low_latency/assets/2509.21867/2509.21867-page3.png]]

> 图注：原论文第 3 页页面渲染。上半为 **Fig. 2**（FastEnhancer 整体架构图，含 FastEnhancer 总览 / Pre Encoder / EncoderBlock / DecoderBlock / Pre RNNFormer / Post RNNFormer / RNNFormer 子框图）；下半左为 **Table 1**（5 档配置），右为 **Eq. (1)–(5)** 与 §4 实验设置正文。图上关键的维度标注为：总览框 `Batch Size = B`、`Channels = C1/C2`、`Frequency = Nfft/8 → F`、`Time Length = T`；STFT/iSTFT 标注 `hop = H`。渲染图同时可核 Eq. (2)–(5) 的范数符号（本页 ASCII 图与公式即据此写定）。

### 配置速查（Table 1）

| Size | H | L | K | C1 | C2 | F | Para.(K) | MACs | RTF(Xeon) | RTF(M1) |
|---|---|---|---|---|---|---|---|---|---|---|
| Tiny (T) | 256 | 2 | 2 | 24 | 20 | 16 | 22 | 55M | 0.012 | 0.013 |
| Base (B) | 256 | 2 | 3 | 48 | 36 | 24 | 92 | 262M | 0.022 | 0.026 |
| Small (S) | 256 | 3 | 3 | 64 | 48 | 36 | 195 | 664M | 0.034 | 0.048 |
| Medium (M) | **160** | 3 | 4 | 96 | 72 | 48 | 492 | 2.9G | 0.101 | 0.173 |
| Large (L) | **100** | 4 | 5 | 128 | 96 | 64 | 1105 | 11G | 0.313 | 0.632 |

- $H$：STFT hop；$L$：encoder/decoder block 数；$K$：RNNFormer block 数；$C_1/C_2$：通道；$F$：pre-RNNFormer 降维后的频率数。
- 后四列（Para./MACs/RTF）来自 Table 2，用于把配置与资源对应起来。
- **注意 $H$ 在 T/B/S 为 256、M 为 160、L 为 100**——这是本库判定延迟的关键线索（见低时延账本）。

### 架构上的三个"零算术代价"设计选择

| 选择 | 论文理由 | 代价形式 |
|---|---|---|
| 时间轴卷积 kernel = 1 | kernel $k>1$ 需缓存 $k-1$ 帧，「These memory operations significantly increase processing time」 | 参数量与 MACs 不变，**内存操作与 RTF 变差** |
| 全模型 BN（非 LN） | BN 可融合进相邻层的乘加，LN 不能 | 参数量与 MACs 不变，**算子数与 RTF 变差** |
| 时间轴 GRU（非 MHSA） | MHSA 需 KV cache，且缓存帧数越多质量越好 → 内存与算术操作继续增加 | 参数量反而更少（DPT 参数更少），**RTF 显著更高** |

## 状态与因果性

| 状态对象 | 论文报告 | 本 Wiki 判定 |
|---|---|---|
| 时间轴 GRU 递归状态 | **单向 GRU**，逐 block 存在；论文未描述跨帧如何保存/更新 | `paper-claimed-causal`：结构上只依赖过去，但**无逐层 state certificate** |
| 频率轴 MHSA | 「doesn't require caching」——注意力在**当前帧内部沿频率轴**做 | 时间维度上 `strict_causal`（只访问当前帧的整条频率轴）；非 all-axis unidirectional |
| 时间轴 MHSA（仅 DPT 消融中） | 用 look-behind **31 帧（论文称对应 0.5 s）**，需 KV cache | `low_look_ahead`（有 31 帧历史窗口）；**31 帧 ÷ 0.5 s 反推 2 ms/帧，与 Table 1 的任何 hop 都不符**（见待验证） |
| 卷积 padding / 缓存 | 论文只解释"kernel=1 ⇒ 无需缓存"，**未给逐层 padding 说明** | `unreported`（缺逐层 certificate） |
| STFT 帧锚定 / center | **未报告** | `unreported`：若 center=True 则前端含 $W/2$ 未来样本（本库按 Nfft=512 推得 16 ms） |
| Pre/Post linear 权重 | **固定不动**（初始化为 filterbank / linear interpolation） | 不涉及状态；是"降训练成本"的设计 |
| 流式语义 | 「frame-by-frame manner」处理谱；未定义 chunk 大小、batch、warm-up | `unreported`（流式配置未给出） |
| state reset / flush / 长流漂移 | **未报告** | 未验证 |

> [!note] 它是"缓存型"流式，与 PSMSE 的"逐帧重置"相反
> FastEnhancer 的**时间轴 GRU 状态跨帧传播**（这是"流式"的实质来源），而**频率轴 MHSA 逐帧无状态**（每帧内部独立完成）。作为对照，[[wiki_low_latency/entities/PSMSE]] 是**每帧调用时重新初始化 Mamba state、不跨帧传播**，靠 50% overlap-add 拼接。两者都自称流式，但**状态的存续语义正好相反**——本库在比较"流式"时必须先问清是哪一种。

## 低时延账本

| 字段 | FastEnhancer 证据 / 边界 |
|---|---|
| 采样率 | 16 kHz（48 kHz 降采样，p.3 §4） |
| Nfft / 窗长 | Nfft = 512 ⇒ **窗长 32.0 ms @16 kHz**（**本库按 Nfft 与采样率推得**，论文未换算） |
| hop $H$ | T/B/S = **256** samples；M = **160**；L = **100**（Table 1） |
| hop 换算（**本库推读**） | T/B/S = **16.00 ms**；M = **10.00 ms**；L = **6.25 ms**（$H/16000$）。**论文没有做这个换算，也没有把它与延迟关联** |
| 频率点数 | Nfft/2 = 256，最高频点被丢弃（p.2 §3） |
| STFT center / 帧锚定 / padding | **未报告**。若 center=True，前端另有 $W/2 = 256$ samples $=16$ ms 未来样本（本库推读） |
| look-ahead / group delay | **未报告** |
| 算法延迟（论文口径） | **不存在**——论文通篇无任何延迟数字，无 window−hop、无 $W/2$、无推导式 |
| 延迟下界估计（**本库推读**） | 按 hop 换算为 **6.25–16 ms 量级**；若计入 center 前端再 +16 ms。**故处于"十几毫秒"量级，比约 2 ms 高一个量级或更多** |
| chunk 大小 / batch=1 | **未报告**；RTF 只说 "single thread" + "under a streaming condition" |
| warm-up / state reset / flush | **未报告** |
| 长流稳定性 / 丢帧策略 | **未报告** |
| 计算 | ONNXRuntime [30]，**单线程**，Xeon Gold 6248R（Fig. 1/3 用它）与 Apple M1；RTF 只给**单值** |
| RTF 口径 | 论文称 "under a streaming condition" 但**未定义 chunk 大小与是否有 look-ahead**；**未说明是否含 STFT/iSTFT** 于计时内 |
| p50 / p95 / p99 | **全部未报告** |
| 峰值 RAM / SRAM | **未报告** |
| 量化 | **未报告**（无 INT8/定点结果） |
| 功耗 | **未报告** |
| 端到端 | ADC/DMA、I/O buffer、线程调度、DAC/playout、capture-to-playback、underrun/overrun **全部未报告** |
| deadline | deadline miss、worst-case margin **未报告** |

实体判定：**`paper-claimed-causal`（结构证据较强：kernel=1 + 单向 GRU + 频率轴注意力不需 cache；但无逐层 certificate、无前端帧锚定）/ 论文无算法延迟数字 / 本库推得的延迟下界在十几毫秒量级 / 无 p99、无量化、无功耗、无端到端证据**。**不是 2 ms 级候选**。

> [!warning] RTF 是吞吐指标，不是延迟指标
> 即便 T 档 RTF = 0.012（Xeon 单线程），它说的是"平均处理时间 ≈ 0.012 × 音频时长"，与"每个 hop 必须在 deadline 前算完"是两件事。本篇**没有任何 deadline 证据**。本库口径见 [[wiki_low_latency/concepts/严格因果与算法延迟]]。

## 结果与证据边界

![[wiki_low_latency/assets/2509.21867/2509.21867-page4.png]]

> 图注：原论文第 4 页页面渲染。上方 **Table 2**（主结果，含 a/b/c/d 四条脚注）、中部左 **Table 3**（卷积与归一化消融）、中部右 **Fig. 3**（RTF vs SISDR 与 RTF vs STOI，图例为 RNNFormer / DPRNN / DPTransformer，横轴 RTF 为对数刻度 0.0125–0.4，**越左越快**）。Table 2 在此可核**脚注上标归属**（GTCRN→a、LiSenNet 两行→b/c、FSPEN 与 BSRNN→d）与 **FastEnhancer 只有 5 个档位**（T/B/S/M/L）。

### 主结果（Table 2，逐格核对渲染图后照抄）

| Model | Para.(K) | MACs | RTF(Xeon) | RTF(M1) | P.808 | SIG | BAK | OVL | SCOREQ | SISDR | PESQ | STOI | ESTOI | WER |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| GTCRN^a [9] | 24 | 40M | 0.060 | 0.042 | 3.43 | 3.36 | 4.02 | 3.08 | 0.330 | 18.8 | 2.87 | 0.940 | 0.848 | 3.6 |
| LiSenNet^b [11] | 37 | 56M | – | – | 3.34 | 3.30 | 3.90 | 2.98 | 0.425 | 13.5 | 3.08 | 0.938 | 0.842 | 3.7 |
| LiSenNet^c [11] | 37 | 56M | 0.034 | 0.028 | 3.42 | 3.34 | 4.03 | 3.07 | 0.335 | 18.5 | 2.98 | 0.941 | 0.851 | 3.4 |
| FSPEN^d [10] | 79 | 64M | 0.046 | 0.038 | 3.40 | 3.33 | 4.00 | 3.05 | 0.324 | 18.4 | 3.00 | 0.942 | 0.850 | 3.6 |
| BSRNN^d [12] | 334 | 245M | 0.059 | 0.062 | 3.44 | 3.36 | 4.00 | 3.07 | 0.303 | 18.9 | 3.06 | 0.942 | 0.855 | 3.4 |
| **FastEnhancer-T** | 22 | 55M | **0.012** | **0.013** | 3.42 | 3.34 | 4.01 | 3.06 | 0.334 | 18.6 | 2.99 | 0.940 | 0.850 | 3.6 |
| **FastEnhancer-B** | 92 | 262M | **0.022** | 0.026 | 3.47 | 3.38 | 4.02 | 3.10 | 0.285 | 19.0 | 3.13 | 0.945 | 0.861 | 3.2 |
| **FastEnhancer-S** | 195 | 664M | 0.034 | 0.048 | 3.49 | 3.40 | 4.03 | 3.12 | 0.265 | 19.2 | 3.19 | 0.947 | 0.866 | 3.2 |
| **FastEnhancer-M** | 492 | 2.9G | 0.101 | 0.173 | **3.48** | 3.39 | 4.02 | 3.11 | 0.243 | 19.4 | 3.24 | 0.950 | 0.873 | **2.8** |
| **FastEnhancer-L** | 1105 | 11G | 0.313 | 0.632 | **3.53** | 3.44 | 4.04 | 3.16 | 0.239 | 19.6 | 3.26 | 0.952 | 0.877 | 3.1 |

四条脚注（渲染图核对）：

- ^a **Evaluated using the official checkpoint.**
- ^b **Trained using the official training code. Not streamable because of input normalization and griffin-lim. Thus, RTFs are not reported.**
- ^c **To make the model streamable, input normalization and griffin-lim are removed. Trained following the experimental setup in Section 4.**
- ^d **Re-implemented and trained following the experimental setup in Section 4 for a fair comparison.**

### 消融（Table 3 + Fig. 3 + §5.2）

| 消融 | Para.(K) | RTF(Xeon) | RTF(M1) | SISDR | STOI | 论文结论 |
|---|---|---|---|---|---|---|
| **FastEnhancer-B（基线）** | 92 | 0.022 | 0.026 | 19.0 | 94.5 | — |
| 时间轴 kernel 1 → 3 | **187** | 0.028 | 0.037 | **19.0** | **94.5** | 需缓存操作、RTF 显著升高，但**质量与可懂度毫无改善** |
| BN → LN | **92** | **0.028** | **0.029** | 18.9 | 94.5 | **参数量与 MACs 相同**却 RTF 升高；证明 BN + 融合是最有效选择 |
| 频率轴 MHSA → GRU（DPRNN） | — | — | — | **明显下降** | 相近 | 频率建模上 self-attention 优于 recurrent（Fig. 3） |
| 时间轴 GRU → MHSA（DPT，look-behind 31 帧） | **更少** | **显著升高** | — | — | — | 参数更少但因 KV cache 而 RTF 显著升高；时序建模上 recurrent 更适合流式 |

### 支持 / 不支持 / 未报告 / 可比性提醒 / 口径警示

- **支持**：
  1. 在 Table 2 的对比集合内，FastEnhancer 各档取得最低 RTF（T 0.012、B 0.022 为表内最低两者）；
  2. **MACs 高反而更快**：FastEnhancer-B（92K / 262M / RTF 0.022）对 GTCRN（24K / 40M / 0.060）与 FSPEN（79K / 64M / 0.046）——参数量与 MACs 都更高，RTF 反而最低；
  3. **BN→LN 在参数量与 MACs 完全不变下把 RTF 从 0.022 抬到 0.028（Xeon +27%）**，SISDR 19.0→18.9、STOI 不变——本库"可融合性决定速度"的最强单条证据；
  4. **时间轴 kernel 1→3 使 Para. 92K→187K、RTF +27%（Xeon）/+42%（M1），而 SISDR 与 STOI 一格不动**；
  5. DPT 消融中"参数更少但 RTF 更高"（唯一变量是 KV cache）；
  6. 报告了 DNSMOS **SIG/BAK/OVL 三项** + **WER（Whisper-large-v3-turbo）** + **ESTOI** + SCOREQ，是本库**最全的可懂度/保留指标组合之一**；
  7. 论文自己指出 **指标方向会不一致**（M 档 DNSMOS 略降而其他指标全升），并警示「relying on a limited set of objective metrics can lead to misleading conclusions」。
- **不支持**：
  1. 约 2 ms 级算法延迟已达成；
  2. "streaming" 的具体工作点（chunk 大小、是否有 look-ahead、batch=1）已被定义或验证；
  3. deadline / p99 / underrun 已通过；
  4. 长流稳定性、state reset、warm-up 已验证；
  5. 目标端侧硬件（ARM/DSP/NPU）上可实时；
  6. 低 SNR 人声保留已证明；
  7. "以极小代价击败所有前作"——L 档是在 275× 于 GTCRN 的 MACs 下取得的。
- **未报告**：算法延迟（**完全无数字**）、group delay、look-ahead、warm-up、state reset、flush、长流漂移、chunk 大小、batch=1 证据、STFT 帧锚定/center、逐层 padding/state certificate、RTF 的 p50/p95/p99、deadline miss、underrun/overrun、峰值 RAM/SRAM、量化（INT8/定点）、功耗、端到端（ADC/DMA/I/O/DAC/capture-to-playback）、训练 wall-clock/GPU 型号、5 seeds 的标准差、负 SNR 分层（−10/−5/0/5 dB）、噪声类型分层、babble/竞争说话人、未见过噪声、false-suppression、SPP/VAD 校准、F0/formant/prosody continuity、voiced energy 保留、主观听感 MOS。
- **可比性提醒**：
  1. **基线来源不统一**——GTCRN^a 用官方 checkpoint；LiSenNet^b 用官方训练代码（**因 input normalization 与 griffin-lim 不可流式，RTF 未报告**）；LiSenNet^c、FSPEN^d、BSRNN^d 是作者按 §4 **重实现重训**。论文用脚注坦白，但"官方权重"与"作者重训"的数字**不宜直接横比**。
  2. **LiSenNet^b 不能进流式排名**——脚注 b 明说 not streamable，因此它的 SCOREQ 0.425（表内最高）与 SISDR 13.5（表内最低）**不能与流式模型并列解读**。
  3. **LiSenNet^a/b/c 三行本身是"非流式→流式"代价的教材**：可流式化后 PESQ 3.08→2.98、SCOREQ 0.425→0.335、SISDR 13.5→18.5、BAK 3.90→4.03、WER 3.7→3.4——**方向并不一致**，说明流式化改变了误差结构而非单向退化。
  4. **与 LaCo-SENet 的 RTF 口径同构**：都在**单线程 Intel Xeon** 上、都用 ONNXRuntime（LaCo-SENet 是 Xeon **Silver 4510**，本篇是 Xeon **Gold 6248R**）。但 LaCo-SENet 还给出逐层 padding 分配式与算法时延公式，本篇只有 RTF——**用 LaCo-SENet 的尺子量本篇，逐层 certificate 一栏是空的**。
- **口径警示**：
  1. **"参数量/MACs"与"RTF"是两种不同性质的量**——前者是算术量，后者是"算术 + 内存 + 算子实现"的综合结果。本篇的全部核心论证都建立在"两者会背离"上，因此**不能**用 MACs 代替 RTF 排序。
  2. **RTF 是吞吐指标**——不是延迟指标，也不是 deadline 指标。
  3. **5 seeds 只报均值不报方差**，0.01 量级差异的显著性不可判定（M 的 P.808 3.48 vs S 的 3.49 即属此列）。
  4. **数据集名称论文自相矛盾**（"Voicebank-Demand" vs "VTCK-Demand"），见待验证。
  5. **论文口径的 hop 从未与延迟关联**，本页的 16 / 10 / 6.25 ms 换算**全部是本库推读**，须与论文主张严格区分。

## 交叉链接

- 源论文：[[wiki_low_latency/sources/2025/FastEnhancer 2025]]
- 概念展开：[[wiki_low_latency/concepts/2509.21867-speed-optimized-streaming-design]]
- 前身（被点名并否定的频率轴 RNN）：[[wiki_low_latency/entities/DPCRN]]、[[wiki_low_latency/sources/2021/DPCRN Low-Latency Direction 2021]]、[[wiki_low_latency/concepts/2107.05429-dual-path-recurrent-context]]
- 被挑战的子带路线：[[wiki_low_latency/entities/FSB-LSTM]]、[[wiki_low_latency/sources/2023/FSB-LSTM 2023]]、[[wiki_low_latency/concepts/2304.08707-full-sub-band-modeling]]
- 复数谱路线对照：[[wiki_low_latency/entities/DCCRN]]、[[wiki_low_latency/concepts/2008.00264-complex-phase-enhancement]]
- 嵌入式实时参照：[[wiki_low_latency/entities/DeepFilterNet2]]、[[wiki_low_latency/sources/2022/DeepFilterNet2 2022]]、[[wiki_low_latency/concepts/2205.05474-deep-filtering]]
- 低时延 STFT 前端（hop/窗账本对照）：[[wiki_low_latency/entities/STFT-Very-Low-Latency-SE]]、[[wiki_low_latency/sources/2022/STFT-Domain Very Low Algorithmic Latency 2022]]、[[wiki_low_latency/concepts/2204.09911-short-asymmetric-stft]]
- 感知驱动实时：[[wiki_low_latency/entities/PercepNet]]、[[wiki_low_latency/sources/2020/PercepNet Low-Latency Direction 2020]]
- 最严因果审计尺子（RTF 口径同构）：[[wiki_low_latency/entities/LaCo-SENet]]、[[wiki_low_latency/sources/2026/LaCo-SENet 2026]]、[[wiki_low_latency/concepts/2606.19688-latency-configurable-asymmetric-padding]]
- 状态语义正反对照：[[wiki_low_latency/entities/PSMSE]]、[[wiki_low_latency/sources/2026/PSMSE 2026]]、[[wiki_low_latency/concepts/S2542660526001769-spiking-mamba-streaming]]
- 跨帧固定状态流的另一例：[[wiki_low_latency/entities/RT-SEMamba]]、[[wiki_low_latency/sources/2026/RT-SEMamba 2026]]、[[wiki_low_latency/concepts/2608.12099-mamba-distillation]]
- 动态算力子群（同类论点的另一侧）：[[wiki_low_latency/entities/D-GRU]]、[[wiki_low_latency/concepts/2408.12425-dynamic-gated-rnn]]、[[wiki_low_latency/entities/Skip-DPCRN]]、[[wiki_low_latency/concepts/2207.11108-inference-skipping-parallel-rnn]]
- 统一低时延对照框架：[[wiki_low_latency/entities/CRUSE-Latency-Study]]、[[wiki_low_latency/sources/2024/Ultra-Low Latency Speech Enhancement Comprehensive Study 2024]]
- 非对称 STFT + 复用：[[wiki_low_latency/entities/RT-Tango]]、[[wiki_low_latency/sources/2026/RT-Tango 2026]]
- 延迟审计口径：[[wiki_low_latency/concepts/严格因果与算法延迟]]、[[wiki_low_latency/concepts/低时延前端与延迟账本]]、[[wiki_low_latency/concepts/2409.10358-ultra-low-latency-benchmark]]
- 人声保留缺口：[[wiki_low_latency/concepts/低 SNR 人声保留评估]]
- 顶层页：[[wiki_low_latency/overview]]、[[wiki_low_latency/index]]

> [!question] 待验证
> **(1) 数据集名称自相矛盾**：Table 2 标题 "Performance on **Voicebank-Demand**"，§4 正文 "**VTCK**-Demand dataset [14]"，而 [14] 是 Valentini-Botinhao 的 VoiceBank-DEMAND 论文。同一数据集两种写法（"VTCK" 疑为 "VCTK" 笔误）。本库不静默修正。
> **(2) DPT 消融的帧率与 Table 1 不符**：§5.2 说 look-behind 为「31 frames (corresponding to 0.5 seconds)」⇒ 2 ms/帧（500 帧/s），但 Table 1 的 hop（256/160/100 samples @16 kHz）对应 62.5 / 100 / 160 帧/s，**没有任何一档是 2 ms/帧**。论文未说明该消融用的 hop。
> **(3) Fig. 1 与配置的对应关系未说明**：图上 FastEnhancer 是**一个点还是五个点**未交代；若为单点，则"Pareto 前沿"由单点支撑。
> **(4) 因果性缺逐层 certificate**：无逐层 padding/state 说明、无 STFT 帧锚定（center 与否）说明、无样本级可读性声明。故只能记 `paper-claimed-causal`。
> **(5) RTF 口径不可复现**："streaming condition" 未定义 chunk 大小、是否有 look-ahead、是否含 STFT/iSTFT。
