---
title: DeepFilterNet2 — 面向嵌入式全频带音频的实时语音增强
type: source
created: 2026-09-16
updated: 2026-09-16
tags:
  - speech-enhancement
  - full-band
  - deep-filtering
  - low-complexity
  - embedded
  - real-time
  - low-look-ahead
  - multi-target-loss
source_type: paper
year: 2022
authors: H. Schröter; A. Maier; A.N. Escalante-B.; T. Rosenkranz
venue: 未报告（PDF 首页未明确）
paper_id: 2205.05474
arxiv: https://arxiv.org/abs/2205.05474
local_pdf: raw/papers/low_latency_causal_se/2205.05474.pdf
causality: low_look_ahead
algorithmic_latency_ms: 40
sampling_rate: 未报告（论文以 48 kHz full-band 为背景口径）
related:
  - [[wiki_low_latency/entities/DeepFilterNet2]]
  - [[wiki_low_latency/concepts/2205.05474-deep-filtering]]
  - [[wiki_low_latency/index]]
  - [[wiki_low_latency/overview]]
  - [[wiki/sources/2023/DeepFilterNet 2023]]
  - [[wiki_low_latency/sources/2023/FSB-LSTM 2023]]
  - [[wiki_low_latency/sources/2023/GCFSnet 2023]]
  - [[wiki_low_latency/sources/2022/STFT-Domain Very Low Algorithmic Latency 2022]]
  - [[wiki/concepts/STFT与频谱图]]
  - [[wiki/concepts/全带与子带模型]]
  - [[wiki/sources/2020/DCCRN 2020]]
---

~~~yaml
- 论文: [DeepFilterNet2: Towards Real-Time Speech Enhancement on Embedded Devices for Full-Band Audio](2022)
  ├── 要解决什么问题: 在全带语音增强中同时压低 MAC、内存带宽和时间缓冲，使模型能在嵌入式设备上实时运行
  ├── 核心方法: 两阶段 ERB envelope 增益 + 低频复数 deep filtering；统一 encoder、频率分组和轻量化卷积/循环结构
  ├── 属于哪个分支: 全带低复杂度语音增强 / 复数时频处理 / 嵌入式实时部署 / 低 look-ahead
  ├── 输入/输出: x(t) → STFT X(k,f) → ERB 特征与 complex/DF 特征 → 增益和 deep-filter 系数 → Y(k,f) → iSTFT y(t)
  ├── 关键trick: ERB envelope 负责粗频率增益，DF 只重建低频 periodicity；GLinear/PConv 分组、除输入层外 1×3 频率卷积、训练调度、MR loss、数据增强和 post-filter
  ├── 数据集: DNS4 英文部分（500+ h 全带 clean speech、约 150 h noise、150 real + 60,000 simulated HRTFs）；评测 Voicebank+Demand 与 DNS4 blind test
  ├── 对比了谁: Noisy、RNNoise、NSNet2、PercepNet、DCCRN、DCCRN+、S-DCCRN、FullSubNet+、GaGNet、DMF-Net、FRCRN、DeepFilterNet
  ├── 性能上限: Voicebank+Demand 最终 +Post-Filter 为 PESQ=3.03、CSIG=3.72、CBAK=3.37、COVL=3.63、STOI=0.941；DNS4 blind +Post-Filter 为 SIGMOS=4.19、BAKMOS=4.47、OVLMOS=3.90
  ├── 参数量: 2.31 M 参数、0.36 G MACS/s；Core i5-8250U 平均 5 次 RTF=0.04，结论另报 Raspberry Pi 4 RTF=0.42
  ├── 消融关键发现: Simplified DNN 将 RTF 从 0.11 降至 0.04；post-filter 牺牲 Voicebank 的 CSIG/PESQ，却提升 DNS4 的 BAKMOS/OVLMOS，存在明确 SIG-BAK 权衡
  ├── 遗留问题(你的机会): 40 ms 算法时延且有 2-frame look-ahead，不是 strict-causal 2 ms 系统；无 p99、deadline miss、capture-to-playback、峰值 RAM、能耗、状态恢复和人声误抑制证据
  └── 跟哪篇像: [[wiki/sources/2023/DeepFilterNet 2023]]、[[wiki_low_latency/sources/2023/FSB-LSTM 2023]]、[[wiki_low_latency/sources/2023/GCFSnet 2023]]、[[wiki/concepts/全带与子带模型]]
~~~

# DeepFilterNet2: Towards Real-Time Speech Enhancement on Embedded Devices for Full-Band Audio

H. Schröter、A. Maier、A.N. Escalante-B.、T. Rosenkranz，arXiv:2205.05474v1，11 May 2022。以下页码均指本地 PDF raw/papers/low_latency_causal_se/2205.05474.pdf，不使用外部页面作为证据。

> [!warning] PDF 转换质量与阅读说明
> 原 PDF 共 5 页。Poppler pdftoppm 渲染成功且页面布局、Figure 1-3 和 Table 1-2 均可视觉阅读，但首次渲染输出 Syntax Error: No display font for 'Symbol' 与 Syntax Error: No display font for 'ArialUnicode'。pypdf 文本抽取还会产生连字、作者重音符号、上下标和表格小数间空格的丢失或摊平。因此公式、图和表均以原 PDF 渲染页复核；第 2 页和第 4 页的原页面副本嵌入本笔记。
>
> [!question] PDF 中需保留的符号不一致
> 式 (3) 视觉上写作 X_df(k,f_erb)，而 Figure 1 和式 (5) 使用 f_df；式 (5) 的求和项按 PDF 原样写作 X(k-i+l,f)，但其前一句和 Figure 1 说明 deep filtering 作用于 Y_G。式 (8) 的第二个分母项按 PDF 原样为 G'(b,k)，与前一行的 (k,b) 顺序不一致。下文不擅自修正这些记号，并把可确定的工程含义与不确定性分开记录。

## 1. 他们为什么这么做？（motivation）

### 1.1 任务与对象

论文研究**全带语音增强（full-band speech enhancement）**，目标是把含混响和加性噪声的语音混合恢复为更干净的语音，并让系统可以在嵌入式设备上实时运行。论文在引言中把 full-band 音频与 48 kHz 联系起来，但实现细节段没有再次单独给出模型输入采样率，因此本页将“48 kHz”标为全文背景口径，不把它伪装成实现配置字段（第 1 页、第 3 页）。

论文的信号对象是：

$$
x(t)=s(t)*h(t)+n(t). \tag{1}
$$

- $x(t)$：含混响、含噪的观测混合；
- $s(t)$：clean speech；
- $h(t)$：表示混响环境的 room impulse response；
- $n(t)$：加性噪声；
- $*$：时域卷积。

对应的频域写法为：

$$
X(k,f)=S(k,f)\cdot H(k,f)+N(k,f). \tag{2}
$$

- $X(k,f)$：$x(t)$ 的 STFT；好
- $S(k,f)$、$H(k,f)$、$N(k,f)$：相应语音、房间响应和噪声的频域量；
- $k$、$f$：时间帧索引和频率索引。

### 1.2 工程矛盾

论文把嵌入式部署的瓶颈归纳为两类：

1. **频率维和 MAC 增长**：采样率上升通常需要更大的 FFT 窗，带来更多频率 bin，直接增加 multiply-accumulate operations。
2. **实时内存与带宽**：时间卷积或 temporal attention 需要保存较大的时间缓冲；即使可以用 ring buffer 实现，额外内存访问仍可能使 memory bandwidth 成为瓶颈。

已有全带模型可以得到较好的增强质量，但不一定适合嵌入式设备。DeepFilterNet 的出发点是利用语音的**周期成分（periodic component）**和**随机成分（stochastic component）**：第一阶段在压缩 ERB 域增强 speech envelope，第二阶段在复数域用 deep filtering 重建周期性（第 1 页）。

### 1.3 论文目标的可审计版本

| 维度 | PDF 明确内容 | 本 Wiki 记录 |
|---|---|---|
| 任务 | full-band speech enhancement，包含 denoising，并扩展到 dereverberation 与 declipping | 语音增强主任务，附带失真恢复 |
| 信号域 | STFT；第一阶段 ERB 压缩幅度/增益，第二阶段复数 deep filtering | 两阶段时频处理 |
| 部署目标 | embedded devices；摘要报 notebook CPU RTF=0.04，结论报 Raspberry Pi 4 RTF=0.42 | 平均吞吐达到实时口径，但没有 hard deadline 证据 |
| 质量目标 | Voicebank+Demand 的 WB-PESQ、STOI、CSIG/CBAK/COVL；DNS4 blind 的 DNSMOS P.835 | 同时记录语音质量、背景噪声和整体 MOS |
| 算法时延 | 20 ms window、50% overlap、2-frame look-ahead，overall algorithmic delay=40 ms | low_look_ahead，不是 strict-causal 2 ms |

## 2. 之前的人怎么做不了？（limitation → gap）

### 2.1 既有路线与缺口

| 路线 | 论文承认的优点 | 论文指出或可直接读出的限制 |
|---|---|---|
| STFT + U-Net 类 DNN | 频域建模成熟，能够处理 full-band | 大 FFT 和高频率维带来 MAC、内存带宽和嵌入式负担 |
| PercepNet | 用 triangular ERB filter bank 把 magnitude 压到 32 个 ERB bands | 主要做 real-valued 处理，需要额外 comb-filter 细化 periodic component |
| FRCRN | 把频率 bin 分成 3 个 channel，支持 complex processing/CRM | 论文将其作为高性能参照，Table 1 中计算量为 12.30 G MACS，未报 RTF |
| DMF-Net、GaGNet 等多阶段模型 | 多阶段 coarse-to-fine 处理有潜力 | 复杂度和缓冲开销可能不适合嵌入式；论文特别批评 temporal convolution 的 buffer 需求 |
| TCN / temporal attention | 可以建模时间上下文 | 实时推理要保存 temporal buffer，额外 memory access 可能成为瓶颈 |
| 原 DeepFilterNet | 采用感知启发的 ERB + deep filtering 框架 | 本作需要进一步降低运行时间并提高全带数据、训练和架构效率 |

因此本文的 gap 是：**如何保留全带语音增强和复数周期性重建能力，同时把每秒 MAC、频率处理宽度和实时推理缓冲压到嵌入式预算内。**论文的回答是让 ERB envelope 负责低成本的粗粒度增益，再让只覆盖低频的 deep filter 负责 periodicity；同时从训练调度、数据增强、分组和时间卷积结构一起做系统级优化。

### 2.2 strict-causal 与 latency ledger

| 账本项目 | PDF 证据 | 本 Wiki 判定 |
|---|---|---|
| 采样率 | 引言把 full-band 说明为 48 kHz；3.1 没有再次明确输入采样率 | 未报告（背景提到 48 kHz） |
| STFT window | 20 ms | 明确 |
| overlap / hop | 50% overlap，因此 hop=10 ms | hop 可由 PDF 配置直接计算 |
| DF look-ahead | $l=2$ frames | 明确使用未来上下文 |
| DF order | $N=5$ | 明确 |
| overall algorithmic delay | 论文明确写 40 ms | 算法时延口径，不是端到端播放时延 |
| temporal convolution | 仅输入层使用 causal $3\times3$；其余 convolution/transposed convolution 从 $2\times3$ 改为 $1\times3$，沿频率轴 | 结构上减少历史 buffer，但不能抵消 DF look-ahead |
| future observed samples | 式 (5) 含 $k-i+l$，且 $l=2$ | **非 strict-causal**；应标为 low_look_ahead |
| algorithmic state / warm-up / reset | 未报告 | 未报告 |
| chunk、streaming batch=1 | 未报告；RTF 测量条件也未说明是否为真实 chunk 流 | 未报告 |
| RTF | Core i5-8250U notebook，平均 5 次，Table 1 最终行=0.04；结论另报 Raspberry Pi 4=0.42 | 平均吞吐证据 |
| p50/p95/p99 | 未报告 | 未报告 |
| deadline miss / underrun / overrun | 未报告 | 未报告 |
| ADC/DMA/I/O buffer/DAC | 未报告 | 未报告 |
| 峰值 RAM、SRAM、能耗、量化精度 | 未报告 | 未报告 |

**结论**：DeepFilterNet2 是面向嵌入式的低复杂度、低 look-ahead 系统，但不是本 Wiki 所要求的 strict-causal 约 2 ms 系统。RTF<1 只能说明给定测量条件下平均处理吞吐快于音频时长，不能替代每个 10 ms hop 的 p99 deadline 或完整 capture-to-playback 证明。

## 3. 这个做法核心 trick 是什么？

### 3.1 两阶段信息流

论文的总流程是：

~~~text
x(t)
  → STFT → X(k,f)
  → ERB Features: X_erb(k,b)
  → Complex/DF Features: X_df(k,f_df)
  → unified encoder F_enc → embedding E(k)
       ├─ ERB decoder → real gains G_erb(k,b)
       │                 → interpolate → G(k,f)
       │                 → Y_G(k,f)=X(k,f)·G(k,f)
       └─ DF decoder → C_df^N(k,i,f_df)
                         → deep filtering on the lower band
                         → Y(k,f')
  → iSTFT → y(t)
~~~

![[wiki_low_latency/assets/2205.05474/2205.05474-page2-fig1.png]]

> 图证据：原 PDF 第 2 页 Figure 1 和 Figure 2。Figure 1 支持 ERB envelope stage、complex periodicity stage、DF coefficients、deep filter、iSTFT 的连接；Figure 2 支持训练调度曲线。此图为 Poppler 对原 PDF 页面渲染的副本，不是 AI 重画。

第一阶段使用压缩 ERB 域降低频率维度，预测 real-valued gain：

$$
\mathcal{E}(k)=\mathcal{F}_{\mathrm{enc}}\left(X_{\mathrm{erb}}(k,b),X_{\mathrm{df}}(k,f_{\mathrm{erb}})\right). \tag{3}
$$

$$
\begin{aligned}
G_{\mathrm{erb}}(k,b)&=\mathcal{F}_{\mathrm{erb-dec}}(\mathcal{E}(k)),\\
G(k,f)&=\operatorname{interp}(G_{\mathrm{erb}}(k,b)),\\
Y_G(k,f)&=X(k,f)\cdot G(k,f).
\end{aligned} \tag{4}
$$

符号含义：

- $X_{\mathrm{erb}}(k,b)$：第 $k$ 帧、第 $b$ 个 ERB band 的特征；
- $X_{\mathrm{df}}$：供 deep-filter 分支使用的 complex feature；
- $\mathcal{E}(k)$：共享 encoder embedding；
- $G_{\mathrm{erb}}$：ERB band 上的实值增益；
- interp：把 ERB band 增益插值到 STFT 频率 bin；
- $Y_G$：第一阶段 gain 后的复数谱。

第二阶段在低频部分预测 $N$ 阶 deep-filter coefficients：

$$
C^N_{\mathrm{df}}(k,i,f_{\mathrm{df}})
=\mathcal{F}_{\mathrm{df-dec}}(\mathcal{E}(k)). \tag{5a}
$$

随后论文按原 PDF 写为：

$$
Y(k,f')
=\sum_{i=0}^{N} C(k,i,f')\cdot X(k-i+l,f). \tag{5}
$$

- $C(k,i,f')$：第 $k$ 帧、深度滤波 tap $i$、输出频率 $f'$ 的系数；
- $N$：滤波阶数，配置为 5；
- $l$：DF look-ahead，配置为 2 frames；
- $f_{\mathrm{df}}$：DF 分支覆盖的低频范围，论文给出上限 $5\ \mathrm{kHz}$；
- $f$、$f'$：输入和输出频率索引。

式 (5) 的前一句说系数“linearly applied to $Y_G$”，Figure 1 也把 $Y_G$ 接入 deep filter；但公式求和项印成 $X$。因此这里能可靠确认的是**两阶段顺序、低频 deep filtering、N=5 和 2-frame look-ahead**，不能把公式里的 $X$ 静默改成 $Y_G$ 后再声称这是 PDF 的逐字公式。

### 3.2 结构优化：把计算和 buffer 从时间轴移开

DeepFilterNet2 保留 convolutional U-Net 总体结构，但做了四类调整（第 3 页 Figure 3 和 Sec. 2.5）：

1. **Unified encoder**：ERB features 与 complex features 的卷积都放入 encoder，拼接后通过 grouped linear（GLinear）和单个 GRU。
2. **Simplified grouping**：不再为每个频率分组建立许多小 linear/GRU layer，而是把 linear layer 沿频率轴分组并用单次矩阵乘法实现；GRU hidden dimension 降至 256。DF decoder 的输出层也分组，利用邻近频率预测 filter coefficients。
3. **Reduction of temporal kernels**：普通 convolution 和 transposed convolution 的 kernel 从 $2\times3$ 改为 $1\times3$，变成只沿频率轴处理；仅输入层保留 causal $3\times3$ temporal context。
4. **Depthwise pathway convolutions**：在 separable convolution 中，参数和 FLOPs 大量集中于 $1\times1$ convolution；对 pathway convolution 使用 grouping（PConv），降低参数量，论文称没有显著损失 SE performance。

Figure 3 的视觉结构包含 ERB encoder/decoder、DF decoder、GLinear、PConv、TConv、$1\times$ GRU、$2\times$ GRU 和 skip/add 路径。图中各层的完整通道数、每一层 hidden size、padding 和 state 更新规则并未在 PDF 文字中完整表格化，故不补造未报告的层级配置。

### 3.3 训练目标：从单一 spectrogram loss 到 multi-target loss

论文沿用 DeepFilterNet 的 spectrogram loss $\mathcal{L}_{\mathrm{spec}}$，并增加 multi-resolution spectrogram loss。增强谱 $Y(k,f)$ 先变回时域，再用 5、10、20、40 ms 多种窗口计算 STFT：

$$
\mathcal{L}_{\mathrm{MR}}
=\sum_i
\left\lVert |Y_i'|^c-|S_i'|^c\right\rVert_2^2
\left\lVert |Y_i'|^c e^{j\varphi_Y}
-|S_i'|^c e^{j\varphi_S}\right\rVert_2^2. \tag{6}
$$

其中：

- $Y_i'=\operatorname{STFT}_i(y)$：预测时域语音 $y$ 的第 $i$ 个 STFT；
- $S_i'$：target speech 的相应 STFT；
- $|\cdot|$：幅度；
- $\varphi_Y,\varphi_S$：预测与 target 的相位；
- $c=0.3$：compression parameter；
- $i$：窗口分辨率索引，窗口集合为 $\{5,10,20,40\}$ ms；
- 两个 $\ell_2^2$ 项在 PDF 中以相邻范数形式相乘，按原式保留。

组合损失为：

$$
\mathcal{L}
=\lambda_{\mathrm{spec}}\mathcal{L}_{\mathrm{spec}}
+\lambda_{\mathrm{MR}}\mathcal{L}_{\mathrm{MR}}. \tag{7}
$$

实现中 $\lambda_{\mathrm{spec}}=1\mathrm{e}3$、$\lambda_{\mathrm{MR}}=5\mathrm{e}2$，使两项处于相同数量级。论文说明相对于原 DeepFilterNet，移除了用于 speech periodicity 的 $\alpha$ loss heuristic；因为作者认为该 heuristic 只是 local speech periodicity 的较差近似（第 2 页、第 3 页）。

### 3.4 Post-filter：用可控的 gain trade-off 换背景噪声

论文采用 Valin 等人提出的 post-filter，对第一阶段预测的 gain 做轻微过抑制，再给较干净的 time-frequency bin 加回一部分 gain：

$$
\begin{aligned}
G'(k,b)&\leftarrow G(k,b)\cdot
\sin\left(\frac{\pi}{2}G(k,b)\right),\\
G(k,b)&\leftarrow
\frac{(1+\beta)\cdot G(k,b)}
{1+\beta+G'(b,k)}.
\end{aligned} \tag{8}
$$

$\beta$ 的具体值在本文 PDF 中未报告。式 (8) 第二行的 G'(b,k) 也按原 PDF 保留，不能确认它是否是 (k,b) 的排版/记号错误。这个模块的效果应当按 SIG 与 BAK 分开读，而不是笼统地说“全面提升”。

## 4. 实验里哪个消融最关键？

### 4.1 数据、训练与推理配置

| 项目 | PDF 配置 |
|---|---|
| 训练数据 | DNS4 英文部分；500+ h full-band clean speech、约 150 h noise、150 real 和 60,000 simulated HRTFs |
| 数据划分 | train/validation/test = 70%/15%/15% |
| Voicebank 约束 | speaker-exclusive split，且与 test set 无 overlap |
| 评测集 | Valentini Voicebank+Demand test set；DNS4 blind test set |
| 优化器 | AdamW |
| 训练轮数 | 100 epochs，按 validation loss 选 best model |
| learning rate | 3 epochs warmup，之后 cosine decay；每 iteration 更新 |
| weight decay | increasing cosine schedule |
| batch schedule | 从 batch size 8 逐步增至 96；Figure 2 展示曲线，精确每个切换点未表格化 |
| STFT/DF | 20 ms window；50% overlap；$l=2$ frames；32 ERB bands；$f_{\mathrm{DF}}=5$ kHz；$N=5$ |
| loss 权重 | $\lambda_{\mathrm{spec}}=1\mathrm{e}3$，$\lambda_{\mathrm{MR}}=5\mathrm{e}2$ |
| 实现/代码 | PDF 说原始 processing loop 在 Rust，训练用 pytorch STFT/ISTFT；给出 DeepFilterNet GitHub 地址，但 commit、编译选项和部署精度未报告 |

数据增强与失真处理被论文有意分开：

- **对 speech 和 noise 都可用的 randomized augmentations**：random 2nd-order filtering、gain changes、用 2nd-order filters 做 equalizer、用于速度/音高变化的 resampling、colored noise（不用于 speech samples）。
- **只作用于 speech mixture creation 的 distortions**：reverberation，通过衰减 room transfer function 让 target 保留较少混响；clipping artifacts，SNR 在 $[20,0]$ dB。
- **target 约束**：clean speech target 不经 distortion transform，DNN 学习重建原始、未失真的 speech。

### 4.2 评价指标

- **Voicebank+Demand**：WB-PESQ、STOI，以及 composite CSIG、CBAK、COVL。Table 1 是 objective results。
- **DNS4 blind**：DNSMOS P.835 的 SIGMOS、BAKMOS、OVLMOS。Table 2 是 blind test 的非侵入式感知客观结果。
- **未报告**：SI-SDR/SI-SNR、eSTOI、ASR WER、VAD false-suppression、noise-only BAK、F0/formant/prosody continuity、主观听感受试者统计、p50/p95/p99 和硬件 deadline miss。

### 4.3 Table 1：Voicebank+Demand 精确结果

原表 RTF 在 notebook Core i5-8250U CPU 上平均 5 次；表中 '-' 在这里统一写为“未报告”。最后一行 '+ Post-Filter' 是完成所列 proposed chain 后的最终行。

| 模型 | Params (M) | MACS (G) | RTF | WB-PESQ | CSIG | CBAK | COVL | STOI |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Noisy | 未报告 | 未报告 | 未报告 | 1.97 | 3.34 | 2.44 | 2.63 | 0.921 |
| RNNoise | 0.06 | 0.04 | 0.03 | 2.33 | 3.40 | 2.51 | 2.84 | 0.922 |
| NSNet2 | 6.17 | 0.43 | 0.02 | 2.47 | 3.23 | 2.99 | 2.90 | 0.903 |
| PercepNet | 8.00 | 0.80 | 未报告 | 2.73 | 未报告 | 未报告 | 未报告 | 未报告 |
| DCCRN | 3.70 | 14.36 | 2.19 | 2.54 | 3.74 | 3.13 | 2.75 | 0.938 |
| DCCRN+ | 3.30 | 未报告 | 未报告 | 2.84 | 未报告 | 未报告 | 未报告 | 未报告 |
| S-DCCRN | 2.34 | 未报告 | 未报告 | 2.84 | 4.03 | 3.43 | 2.97 | 0.940 |
| FullSubNet+ | 8.67 | 30.06 | 0.55 | 2.88 | 3.86 | 3.42 | 3.57 | 0.940 |
| GaGNet | 5.95 | 1.65 | 0.05 | 2.94 | 4.26 | 3.45 | 3.59 | 未报告 |
| DMF-Net | 7.84 | 未报告 | 未报告 | 2.97 | 4.26 | 3.52 | 3.62 | 0.944 |
| FRCRN | 10.27 | 12.30 | 未报告 | 3.21 | 4.23 | 3.64 | 3.73 | 未报告 |
| DeepFilterNet | 1.78 | 0.35 | 0.11 | 2.81 | 4.14 | 3.31 | 3.46 | 0.942 |
| + Scheduling scheme | 1.78 | 0.35 | 0.11 | 2.92 | 4.22 | 3.39 | 3.58 | 0.941 |
| + MR Spec-Loss | 1.78 | 0.35 | 0.11 | 2.98 | 4.20 | 3.41 | 3.60 | 0.942 |
| + Improved Data & Augmentation | 1.78 | 0.35 | 0.11 | 3.04 | 4.30 | 3.38 | 3.67 | 0.942 |
| + Simplified DNN | 2.31 | 0.36 | **0.04** | **3.08** | **4.30** | **3.40** | **3.70** | **0.943** |
| + Post-Filter | 2.31 | 0.36 | **0.04** | 3.03 | 3.72 | 3.37 | 3.63 | 0.941 |

论文正文据此指出：相对 DeepFilterNet baseline，simplified DNN 行的 PESQ 提高 0.27（2.81 → 3.08），RTF 从 0.11 降至 0.04；最终再加 post-filter 后，PESQ 为 3.03。FRCRN 的多数质量指标更高，但其 12.30 G MACS 且未报 RTF；因此本文能支持的是低复杂度 Pareto 位置，不能宣称所有指标全面 SOTA。

![[wiki_low_latency/assets/2205.05474/2205.05474-page4-tables1-2.png]]

> 表证据：原 PDF 第 4 页 Table 1 和 Table 2。页面副本保留了原表列名、脚注和相关工作未报告值的 '-' 记法；本页正文将其解释为“未报告”。

### 4.4 Table 2：DNS4 blind 的精确结果

| 模型 | SIGMOS | BAKMOS | OVLMOS |
|---|---:|---:|---:|
| Noisy | 4.14 | 2.94 | 3.29 |
| RNNoise | 3.88 | 3.69 | 3.38 |
| NSNet2 | 3.87 | 4.21 | 3.59 |
| FullSubNet+ | 4.22 | 4.12 | 3.75 |
| DeepFilterNet | 4.14 | 4.18 | 3.75 |
| DeepFilterNet2 | 4.20 | 4.43 | 3.88 |
| + Post-Filter | 4.19 | **4.47** | **3.90** |

DNS4 表的 post-filter 变化是 SIGMOS 4.20 → 4.19、BAKMOS 4.43 → 4.47、OVLMOS 3.88 → 3.90。它支持“背景噪声和总体 MOS 变好，同时语音 MOS 略降”的 trade-off，而不是无条件提升。

### 4.5 最关键的消融

#### 消融 A：Simplified DNN 的运行时收益

'+ Improved Data & Augmentation' → '+ Simplified DNN'：

- 参数量：1.78 M → 2.31 M，增加 0.53 M；
- MACS：0.35 G → 0.36 G，几乎不变；
- RTF：0.11 → 0.04，下降 0.07，约快 2.75 倍；
- WB-PESQ：3.04 → 3.08；
- STOI：0.942 → 0.943。

这是最有工程价值的消融：参数量略增，却通过分组、GLinear、PConv、GRU hidden reduction 和时间 kernel 简化显著降低实测 CPU RTF。由于所有结构改动被合并在 'Simplified DNN' 一行，PDF 没有逐项 one-factor ablation，不能把这 0.07 的 RTF 下降归给某一个单独模块。

#### 消融 B：Post-filter 的 SIG-BAK 敏感性

在 Voicebank+Demand 上，post-filter 使 PESQ 3.08 → 3.03、CSIG 4.30 → 3.72、CBAK 3.40 → 3.37、COVL 3.70 → 3.63、STOI 0.943 → 0.941；但在 DNS4 blind 上使 BAKMOS 4.43 → 4.47、OVLMOS 3.88 → 3.90，SIGMOS 4.20 → 4.19。它是最需要谨慎解读的设计决定：更强的背景噪声抑制伴随语音质量指标下降。

#### 消融 C：训练与数据增广的累计收益

- scheduling scheme：PESQ 2.81 → 2.92，+0.11；
- MR Spec-Loss：2.92 → 2.98，+0.06；
- Improved Data & Augmentation：2.98 → 3.04，+0.06；CSIG 4.20 → 4.30，但 CBAK 3.41 → 3.38；
- 这些是累积链式结果，不是相互独立的严格单变量实验。

## 5. 这个方向还剩什么问题没解决？（future work / limitation）

### 5.1 论文明确提出的 future work

结论只明确提出把语音增强思想扩展到其他 enhancement，例如校正当前房间环境导致的 lowpass characteristics（第 4 页）。PDF 没有给出更具体的实验路线、期限或硬件验收指标。

### 5.2 低时延 Wiki 读出的限制

1. **算法时延与本方向目标不匹配**：20 ms window、10 ms hop、2-frame look-ahead 对应论文明确的 40 ms overall algorithmic delay；这不是约 2 ms strict-causal front end。
2. **整网不是 strict-causal**：输入层虽然是 causal $3\times3$，但 DF 分支使用 $l=2$ frames 的未来上下文；因此不能把它标成严格因果。
3. **RTF 不是 deadline**：Core i5-8250U 的 0.04 是 5 次平均，Pi 4 的 0.42 只在结论中给出；没有每 hop wall-clock 分布、p99、deadline miss、underrun 或 overrun。
4. **端到端链路未测量**：ADC、DMA、I/O buffer、调度、DAC、capture-to-playback 和 state reset/warm-up 均未报告。
5. **部署细节不闭环**：没有峰值 RAM/SRAM、内存带宽、能耗、量化精度、固定点误差或目标 SoC 的实测。
6. **模型复现字段不完整**：ERB/complex feature 的具体构造、每层通道数、padding、GRU state 管理、post-filter 的 $\beta$ 和沿用的 $\mathcal{L}_{\mathrm{spec}}$ 展开式未在本文 PDF 完整给出。
7. **高频分支的合并细节不足**：DF 只到 $5\ \mathrm{kHz}$，Figure 1 显示完整谱最终进入 iSTFT，但 PDF 没有把 $f>5\ \mathrm{kHz}$ 的增益/直通规则写成独立公式。
8. **人声保留没有单独拆分**：Voicebank composite metrics 和 DNSMOS 支持整体质量/背景噪声变化，但没有低 SNR 分层、false-suppression、ASR WER、F0/formant/prosody continuity 或听障用户评估。
9. **数据外推边界**：训练集包含 real/simulated HRTFs 和大量 full-band speech/noise，但本文没有真实设备 capture-to-playback 或长流故障恢复实验，不能把 RTF 直接外推为产品端到端保证。

### 5.3 计算量、RTF 与 deadline 的证据边界

| 可以从 PDF 说什么 | 不能从 PDF 说什么 |
|---|---|
| 最终 Table 1 行为 2.31 M 参数、0.36 G MACS/s、Core i5-8250U 平均 RTF=0.04 | 不能说目标嵌入式 SoC 的 p99 一定小于 10 ms |
| 结论报告 Raspberry Pi 4 RTF=0.42 | 不能说已测得 capture-to-playback ≤40 ms 或任何 2 ms deadline |
| 论文设计减少 temporal buffer，并称可在嵌入式实时运行 | 不能给出 RAM、SRAM、DMA、能耗、热约束或 underrun 率 |
| $l=2$、20 ms window、50% overlap，论文口径 algorithmic delay=40 ms | 不能把它归类为 strict-causal，也不能把 RTF<1 当成 causal 证明 |
| Table 1/2 支持 objective quality 和 SIG-BAK trade-off | 不能推出人声弱音、辅音、F0 或 ASR 一定未被误抑制 |

## 6. 本论文在库中的位置关联（cross-reference matrix）

| 关系 | 库中页面 | 关联与差异 |
|---|---|---|
| 前身/直接扩展 | [[wiki/sources/2023/DeepFilterNet 2023]] | 目标 PDF 明确说 DeepFilterNet2 扩展 DeepFilterNet 的两阶段 ERB envelope + deep filtering 框架；本作新增训练调度、MR loss、数据/失真增强、简化 DNN 和 post-filter |
| 概念基石 | [[wiki/concepts/STFT与频谱图]] | 式 (1)-(5) 是 STFT 输入、增益谱和复数 deep-filter 输出的实例；该论文的 latency 取决于 STFT window、hop 和 DF look-ahead |
| 频率分治类比 | [[wiki/concepts/全带与子带模型]] | 第一阶段把频率压到 32 ERB bands，第二阶段只在 5 kHz 以下做 complex DF；与显式 full/sub-band 网络同属“压缩频率维后做专门处理”的母题，但不是同一架构 |
| 同分支低时延竞品 | [[wiki_low_latency/sources/2023/FSB-LSTM 2023]] | 两页都关注端侧低复杂度和时频建模；本论文明确为 40 ms look-ahead 系统，库中 FSB-LSTM 的延迟/数据/指标口径不同，不能直接横比 |
| 同分支双耳/多通道参照 | [[wiki_low_latency/sources/2023/GCFSnet 2023]] | GCFSnet 把当前本侧信号放在低时延空间滤波主路径，DeepFilterNet2 是单路全带 ERB+DF；前者强调跨耳通信与空间线索，后者强调 full-band 复数周期性与嵌入式算力 |
| 低算法时延参照 | [[wiki_low_latency/sources/2022/STFT-Domain Very Low Algorithmic Latency 2022]] | 可作为短窗/因果 STFT 方向的对照入口；本论文的 20 ms window + 2-frame look-ahead 不应被当作约 2 ms strict-causal baseline |
| 同表竞品 | [[wiki/sources/2020/DCCRN 2020]]、[[wiki/sources/2021/FullSubNet 2021]] | Table 1 直接列出 DCCRN 和 FullSubNet+；目标 PDF 支持它们的表内数字，但脚注显示部分 RTF/指标来自各自代码或作者，公平比较仍需统一评测协议 |
| 新增实体 | [[wiki_low_latency/entities/DeepFilterNet2]] | 把模型身份、配置、部署证据和未报告字段集中到实体页 |
| 新增概念 | [[wiki_low_latency/concepts/2205.05474-deep-filtering]] | 把 ERB envelope + complex deep filtering、MR loss 和 look-ahead 约束抽象为可复用概念 |

> [!question] 关联证据边界
> 本矩阵只用于库内导航和比较问题定位。DeepFilterNet2 的数字、公式、延迟和部署结论均来自目标 PDF；不同 source 页面的数字没有被混合成同条件排名。

## 7. 一句话总结“江湖地位”

~~~text
2022 | 全带低复杂度嵌入式语音增强 | 用 ERB envelope + 低频复数 deep filtering，并把训练、分组网络和 temporal kernel 优化压到 0.04 CPU RTF、0.42 Raspberry Pi 4 RTF → DeepFilterNet 系列的端侧工程化版本，但 40 ms look-ahead、缺少 hard-deadline/p99 和人声保留证据，使它不是 strict-causal 2 ms 方向的合格终点。
~~~

## 参考资料

- [Local PDF](../../../raw/papers/low_latency_causal_se/2205.05474.pdf)
- [[wiki_low_latency/entities/DeepFilterNet2]]
- [[wiki_low_latency/concepts/2205.05474-deep-filtering]]
- [[wiki_low_latency/overview]]
- [[wiki_low_latency/index]]
