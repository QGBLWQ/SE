---
title: Ultra-Low Latency Speech Enhancement - A Comprehensive Study
type: source
created: 2026-09-16
updated: 2026-09-16
tags:
  - speech-enhancement
  - low-latency
  - strict-causal-audit
  - noise-suppression
  - speech-preservation
  - real-world-evaluation
  - CRUSE
  - Mamba
  - STFT
  - filterbank
  - benchmark
source_type: paper
year: 2024
authors: Haibin Wu, Sebastian Braun
venue: arXiv preprint (eess.AS)
arxiv: https://arxiv.org/abs/2409.10358
local_pdf: raw/papers/low_latency_causal_se/2409.10358.pdf
related:
  - [[wiki_low_latency/entities/CRUSE-Latency-Study]]
  - [[wiki_low_latency/concepts/2409.10358-ultra-low-latency-benchmark]]
  - [[wiki_low_latency/index]]
  - [[wiki_low_latency/overview]]
  - [[wiki_low_latency/entities/GCFSnet]]
  - [[wiki/sources/2023/DeepFilterNet 2023]]
  - [[wiki/sources/2021/FullSubNet 2021]]
  - [[wiki/sources/2024/Mamba for SE 2024]]
---

~~~yaml
- 论文: [Ultra-Low Latency Speech Enhancement - A Comprehensive Study](2024)
  ├── 要解决什么问题: 在统一数据、模型、损失和评测条件下，公平比较现代 DNN 的低时延语音增强技术，并检查结论能否迁移到真实世界数据
  ├── 核心方法: 以 CRUSE 为固定增强主干，替换分析/合成变换、滤波器组均衡器、未来帧预测和 GRU/Mamba 时序模块，同时做模型容量对照
  ├── 属于哪个分支: 单通道语音增强 / 超低算法时延 / 统一基准与设计空间研究
  ├── 输入/输出: 带噪波形 x(t)=s(t)+n(t) → 分析变换 X → CRUSE fθ → 增强表示或滤波器 → 合成变换 → 增强波形 ŝ(t)
  ├── 关键trick: 控制变量式统一评测；短窗带来的质量损失可由足够的模型容量恢复，而非对称窗、FBE、未来帧预测和 Mamba 并非在所有低时延点都占优
  ├── 数据集: 700 h LibriVox/AVspeech 语音 + 247 h AudioSet/Freesound/内部/彩色稳态噪声；DNS Challenge 第 4、5 盲测集与另建模拟测试集
  ├── 对比了谁: sym/asym/learn-asym、same-compute 模型、Mamba、FBE、mapping/future-predict，以及 original/medium/large CRUSE
  ├── 性能上限: 表 I 中 DNS blind OVR 最高 2.84（F4，10 ms，8.67M/3.28G）；模拟数据 OVR 最高 2.47（C1/F4），PESQ 最高 2.33（F4），siSDR 最高 10.84（C1）
  ├── 参数量: original 0.625M、medium 2.32M、large 8.67M；Mamba 0.642M；MACs 由 230.27M 到 10.95G，Mamba 的 MACs 表中为 -
  ├── 消融关键发现: 强 CRUSE 下 asym 相对 sym 的收益不显著；较大模型可把 3 ms 质量拉回 20 ms 附近；Mamba 在 5 ms 明显退化；未来帧预测在模拟数据有利但 DNS blind 更差
  ├── 遗留问题(你的机会): 采样率、严格因果证书、RTF/p99、硬件端到端 deadline、低 SNR 分层、false-suppression、ASR WER 和人声连续性均未闭环
  └── 跟哪篇像: [[wiki_low_latency/entities/GCFSnet]]、[[wiki/sources/2023/DeepFilterNet 2023]]、[[wiki/sources/2021/FullSubNet 2021]]、[[wiki/sources/2024/Mamba for SE 2024]]
~~~

# Ultra-Low Latency Speech Enhancement - A Comprehensive Study

> Haibin Wu, Sebastian Braun，arXiv:2409.10358v1，eess.AS，2024-09-16。

> [!warning] PDF 转换质量与证据阅读说明
> 原 PDF 共 5 页。文本抽取存在公式下标丢失、换行串接和宽表行列难以可靠分隔的问题，例如第 2 页的 analysis/synthesis 变换符号以及第 4 页 Table I 的长行。Poppler 渲染时提示缺少 Symbol、ArialUnicode 显示字体，但第 1-4 页页面视觉上可读；Eq. (1)-(2) 已按第 2 页页面核对，Figure 1 已按第 3 页核对，Table I/II 已按第 4 页核对。下文的数字只取本地 PDF；没有在 PDF 中给出的采样率、训练超参数、RTF 和硬件时延不作推断。

## 1. 他们为什么这么做？（motivation）

### 1.1 任务与对象

本文研究单通道语音增强（single-channel speech enhancement）。带噪输入和目标写作：

$$
x(t)=s(t)+n(t),
$$

其中 $x(t)$ 是带噪波形，$s(t)$ 是干净目标语音，$n(t)$ 同时包含加入的噪声和混响噪声。系统通过分析变换、增强模型和合成变换，输出 $\hat{s}(t)$，目标是让 $\hat{s}(t)$ 尽可能逼近 $s(t)$。

应用动机来自 hearables、助听设备和 VoIP。论文指出，常见 STFT 语音增强使用 20 ms 窗和 10 ms hop；其低时延账本把 20 ms 解释为 10 ms overlap-add 算法延迟加 10 ms buffer 延迟，且不计每帧模型处理时间。对于直接声与处理声可能泄漏混合的 hearables，论文引用的可听阈值小于 5 ms，因此仅凭平均吞吐快还不够。

### 1.2 为什么需要统一比较

作者认为，过去的低时延结果不能直接横比，原因不是只有模型结构不同，还包括任务、训练数据、脚本、损失和评测设置不一致；并且许多工作只在小规模合成数据上测试，方法在真实录音上的优势可能消失。本文的研究目标因此是把低时延技巧放进同一个 CRUSE 主干、同一套训练数据和评测管线中，逐个替换模块。

论文给出的贡献边界是：

1. 在统一框架中比较对称/非对称窗、可学习变换、可训练 filterbank equalizer（FBE）、未来帧预测等五类低时延路线；
2. 在大规模训练数据、DNS Challenge 盲测和模拟测试上使用 DNSMOS、PESQ、STOI、siSDR 等指标；
3. 检查增大模型容量能否补偿缩短窗长造成的质量损失；
4. 在相近参数量下，把 CRUSE 的 GRU 替换为 Mamba，观察状态空间模型在低时延点是否仍然有效。

### 1.3 这不是单一模型刷新榜单

本文的对象是设计空间研究和控制变量基准，不是一个单独命名的部署模型。表 I 中的 F4、C1 等是不同实验设置的行；“性能上限”只能理解为本论文表格内、对应测试协议下的最高记录，不能当作跨数据集的通用 SOTA，也不能替代端侧 deadline 证据。

## 2. 之前的人怎么做不了？（limitation → gap）

### 2.1 既有路线的局限与本文 gap

| 既有路线 | 论文指出的局限 | 本文要补的缺口 |
|---|---|---|
| 非对称分析/合成窗 [5,6] | 既有工作使用较旧的分离架构、只给一个 8 ms 设置、主要在小规模合成数据上测试且缺少同条件比较 | 在现代 CRUSE 和真实世界数据上判断非对称窗是否仍有独立收益 |
| 可学习变换 [7-9] | 既有工作并未聚焦低时延；多为小规模合成或非混响设置，优势迁移到真实/混响条件并不稳定 | 在统一模型和延迟点上比较 fixed STFT 与 learnable analysis/synthesis |
| 深度 filterbank equalizer [10] | 相关工作没有与明显的非对称 STFT 基线直接比较 | 把 FBE 接到相同 CRUSE 管线，单独观察时域自适应滤波的质量/复杂度 |
| 未来帧预测 [11,12] | 缺少同一实际总时延下的“有/无预测”关键基线；既有对照可能只保持窗长相同而改变实际总延迟 | 在同一表中和 filtering-based、mapping-based 系统一起比较 |
| Clarity Challenge [13] | 更偏向完整系统且主要报告可懂度，不能隔离单个处理模块 | 在一个基础管线内替换单模块，同时看质量、可懂度和计算量 |
| 分散的低时延实验 | 训练数据、超参数、脚本和评测不一致；小型合成数据的趋势未必适用于真实录音 | 用统一控制变量做 real-world-relevant 的方法审计 |

因此本文的 gap 是：**在现代 DNN 主干下，低时延技巧的收益究竟来自窗/变换/预测本身，还是来自模型容量、训练管线和数据协议差异？**

### 2.2 严格因果与时延审计

论文明确写出 CRUSE 采用 causal 3x3 deep filters，并把 overlap-add 的算法延迟写为 $L_s-P$。但按本 Wiki 的严格定义，不能仅凭“causal”一词给整个系统颁发 strict-causal 证书：PDF 没有逐层列出 padding、归一化统计、缓存状态、窗口锚点和最新可读样本。

| 审计项 | PDF 明确给出的信息 | 本 Wiki 判定 |
|---|---|---|
| 任务 | 单通道 $x(t)=s(t)+n(t)$ | 不是阵列/双耳方法；人声保留需单独看 SIG/STOI |
| 采样率 | 未报告 | 不能把毫秒可靠换算成样本数；需复现 |
| CRUSE 主干 | 卷积层、4-channel GRU bottleneck、镜像反卷积、conv-skip；使用 causal 3x3 deep filters | 有论文级 causal 证据；strict-causal 逐层 certificate 未给出 |
| 分析/合成 | 段长 $L_a$、$L_s$、帧移 $P$；主干使用 sqrt-Hann | 窗口的绝对采样数和对齐锚点未完整报告 |
| 短窗频率分辨率 | 缩短窗时以 zero-padding 保持 $N$ 不变 | zero-padding 的具体位置/边界和 future dependency 未说明 |
| 非对称窗 | 分析窗由两个不同长度的 half-Hann 拼接，合成窗更短 | 设计目标是降合成时延；右侧样本依赖和 padding 仍需复现 |
| FBE | 对输入 chunk 做 FFT/复数滤波/iFFT，保留最后 $P$ 个样本 | chunk 状态、缓存和边界处理未给出 |
| 未来帧预测 | 用 $X_0,\ldots,X_k$ 预测 $\hat S_{k+1}$ | 论文级 frame-index 证据存在；样本级 strict causality 和 target 对齐未证实 |
| Mamba | 用 Mamba 替换 CRUSE 的 GRU，参数量相近 | 方向、状态初始化和 padding 细节未报告 |

### 2.3 Latency ledger

| 项目 | 论文证据 | 证据边界 |
|---|---|---|
| 分析窗/合成窗 | 一般记作 $L_a,L_s$；Table I 给出 iWin/oWin 为 20、10、6、5、3 ms 等 | 没有采样率和所有配置的样本长度 |
| 帧移/缓冲 | 每段以 $P$ samples frame shift；对 50% overlap 的未来帧预测，论文说总时延只剩 hop-size buffer | 具体每个设置的 $P$ 和输入输出时序未完全展开 |
| overlap-add 算法延迟 | $L_{\mathrm{alg}}=L_s-P$ | 这是算法/重合相加项，不含模型执行时间和 I/O |
| 表 I 的 Latency | sym-20/10/5/3 ms，asym/learn-asym 为 10/5/3 ms，FBE 为 10/5/2.5 ms，G2 为 3 ms | 表中 latency 不是 capture-to-playback 测量 |
| 未来帧预测 | 预测一帧使算法延迟减少一个 hop；50% overlap 时算法延迟为 0，剩 buffer hop | 预测误差和 mapping target 限制仍存在 |
| warm-up / state reset | 未报告 | 不能判断启动、重置和长流边界行为 |
| compute latency | 论文明确说处理每帧的时间不计入介绍中的 latency | 没有 p50/p95/p99、deadline miss、underrun/overrun |
| 端到端链路 | 未报告 ADC/DMA、输入输出 buffer、DAC、目标硬件 | 不能宣称设备端到端小于 5 ms 或 2 ms |

因此本文最稳妥的标签是：**paper-level causal low-latency study；strict_causal 和端到端 deadline 均待复现**。论文的 ms 数字应视为算法/缓冲设计口径，而不是完整设备测量。

## 3. 这个做法核心 trick 是什么？

### 3.1 先固定一个可替换的分析-增强-合成管线

分析阶段把带噪波形分成重叠段。第 $k$ 段 $x_k$ 的长度为 $L_a$，帧移为 $P$ samples。论文的分析变换为：

$$
X_k=(x_k\circ w_a)\cdot W_{\mathrm{fft}}. \tag{1}
$$

符号含义：

- $x_k\in\mathbb{R}^{1\times L_a}$：第 $k$ 个输入波形段；
- $w_a\in\mathbb{R}^{1\times L_a}$：分析窗；
- $\circ$：逐元素乘法；
- $\cdot$：矩阵乘法；
- $W_{\mathrm{fft}}\in\mathbb{R}^{L_a\times N}$：由 $N$ 个长度为 $L_a$ 的分析基函数组成的变换矩阵，可初始化为 Fourier basis；
- $X_k\in\mathbb{R}^{1\times N}$：第 $k$ 段的 $N$ 维表示；
- $N$：保持不变的特征/频率维度；所有段组成 $X\in\mathbb{R}^{N\times K}$，$K$ 为段数。

分析窗与变换矩阵可以合并成一个 1-D convolutional layer。增强模型写为：

$$
\hat{S}=f_\theta(X),
$$

其中 $f_\theta$ 是参数为 $\theta$ 的 DNN，输出可以是增强滤波器，也可以是直接的信号映射；$\hat S$ 是增强表示。不同低时延策略只替换前端、滤波器组或时序模块，保持主干和训练环境尽量一致。

合成阶段，给定增强表示 $\hat S_k$，论文写为：

$$
\hat{s}_k=(\hat{S}_k\cdot W_{\mathrm{ifft}})\circ w_s. \tag{2}
$$

其中：

- $\hat S_k$：第 $k$ 段的增强表示；
- $W_{\mathrm{ifft}}\in\mathbb{R}^{N\times L_s}$：合成基函数矩阵；
- $w_s\in\mathbb{R}^{1\times L_s}$：合成窗；
- $\hat s_k\in\mathbb{R}^{1\times L_s}$：该段重建出的波形；
- 所有重叠段经过 overlap-add 得到 $\hat s(t)$。

论文指出，带窗的 overlap-add 可以作为一个 transpose convolutional layer 实现，并引入：

$$
L_{\mathrm{alg}}=L_s-P,
$$

即合成窗长减去帧移的算法延迟。

### 3.2 CRUSE 主干与输入输出

| 阶段 | 输入/输出 | PDF 明确内容 |
|---|---|---|
| 输入 | 带噪单通道波形 $x(t)$ | $x(t)=s(t)+n(t)$，其中噪声包含加入噪声和混响 |
| 分析 | $x_k\to X_k$，所有段得到 $X$ | 1-D convolution；固定或可学习的变换 |
| 增强 | $X\to\hat S=f_\theta(X)$ | CRUSE：卷积层、4-channel GRU bottleneck、镜像反卷积、conv-skip |
| 过滤 | 当前/历史特征到增强表示或滤波器 | 使用 causal 3x3 deep filters；FBE 另有复数滤波路径 |
| 合成 | $\hat S_k\to\hat s_k\to\hat s(t)$ | inverse transform、windowing、overlap-add |

为了公平比较，论文让模型架构独立于窗口大小；缩短窗口时通过 zero-padding 保持频率维度 $N$ 不变。这里的 zero-padding 是前端设计描述，PDF 没有给出足以完成样本依赖证明的边界细节。

### 3.3 五类低时延策略

1. **Asymmetric windows**：分析窗由两个不同长度的 half-Hann 窗拼接，合成使用更短的 Hann 窗。核心思路是只缩短决定 overlap-add 时延的合成窗，同时尽量保留分析端频率分辨率。
2. **Learnable analysis/synthesis transforms**：用可训练的 convolution/transposed convolution 实现 Eq. (1) 和 Eq. (2) 的变换。作者还发现，在分析端加入 ReLU 可改善性能和稳定性。表中 Learn-asym 表示可学习的非对称变换。
3. **Trainable filterbank equalizer（FBE）**：最后一个卷积层直接预测 $2M$ 个长度为 $N$ 的滤波器，$2M$ 是因为复数滤波器需要实部和虚部；再用线性映射把长度 $N$ 缩短到 $2P$。滤波后做 iFFT，只保留最后 $P$ 个样本（overlap-discard），所以论文把它的总时延归因于滤波器长度/帧移 $P$。
4. **Future-frame prediction**：用当前可见的 $X_0,X_1,\ldots,X_k$ 预测未来增强表示 $\hat S_{k+1}$。它可把一 hop 的算法时延转成预测问题；但由于 filtering-based target 需要当前帧，本文只能采用 mapping-based target，并预测 complex compressed STFT spectrum。
5. **Mamba**：把 CRUSE 的 GRU 替换为 Mamba。论文强调 Mamba 的选择性状态空间机制和计算效率，但本实验只在表格中给出参数量，Mamba 行的 MACs 为 -，不能由本文确认其低时延计算优势。

### 3.4 关键不是堆技巧，而是做控制变量

本文真正有价值的 trick 是把不同方法放进同一个比较框架：同一 CRUSE 主干、相同窗口点的对照、相同数据和训练策略、同一组 DNSMOS/侵入式指标。这样可以把“窗更短所以变差”“模型更小所以变差”“mapping target 天然受限”等因素分开观察。

模型容量还被作为独立变量：original、medium、large 通过增加卷积滤波器数构造。结果显示，低时延并不是只由前端窗长决定；在固定模型时 hop 越短，单位音频的 MACs 越高，而在 same-compute 设定下被迫缩小模型又会明显损失质量。

## 4. 实验里哪个消融最关键？

### 4.1 数据、训练与评测

| 项目     | 论文明确设置                                                                                   |
| ------ | ---------------------------------------------------------------------------------------- |
| 训练语音   | 700 hour high MOS-rated speech，来自 LibriVox 和 AVspeech                                    |
| 训练噪声   | 247 hour，来自 AudioSet、Freesound、内部噪声源和 1 hour colored stationary noise                    |
| 数据可用性  | 除 65 hour internal noise 外，其余数据在第 2 次 DNS Challenge 中可用                                  |
| 混合方式   | speech/noise on-the-fly mixing；混合与混响策略、loss、training scheme 按文献 [1]                      |
| DNS 测试 | 第 4、5 次 DNS Challenge blind test sets；为增加难度只使用低 signal-to-reverberation 数据部分，共 611 files |
| 模拟测试   | 采用不同语音和噪声语料，按类似训练方式另建                                                                    |
| DNSMOS | 预测 MOS 的 SIG、BAK、OVR 三个分量                                                                |
| 侵入式指标  | PESQ、STOI、siSDR；正文说在 validation set 计算，Table I 将对应列标为 simulated data                     |
| 训练超参数  | 未在本文给出；论文只说遵循 [1]                                                                        |
| 采样率    | 未报告                                                                                      |

> [!question] 评测协议的文字边界
> 第 3 页正文把 PESQ/STOI/siSDR 说成 validation-set 指标，而第 4 页 Table I 把这些列放在 simulated data 下。这里按表格原标签记录，不把它改写成另一个协议；若要复现实验，需要核对作者代码或原始 [1] 管线。

### 4.2 Table I：统一 CRUSE 对照

下表逐行转录原 PDF 第 4 页 Table I。iWin/oWin 是输入/输出窗长；DNS blind set 只列 DNSMOS 的 SIG/BAK/OVR；simulated data 列列出 DNSMOS、PESQ、STOI 和 siSDR。MACs 是论文按处理 1 second audio data 给出的 MAC 数，不是实测 RTF。

| Row | Model | iWin (ms) | oWin (ms) | Latency (ms) | Model size | MACs | DNS SIG | DNS BAK | DNS OVR | Sim SIG | Sim BAK | Sim OVR | PESQ | STOI (%) | siSDR |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| A1 | sym-20ms | 20 | 20 | 20 | 0.625M | 230.27M | 3.18 | 3.78 | 2.79 | 2.87 | 4.03 | 2.46 | 2.22 | 84.45 | 10.52 |
| A2 | sym-10ms | 10 | 10 | 10 | 0.625M | 460.53M | 3.16 | 3.81 | 2.79 | 2.83 | 4.03 | 2.43 | 2.24 | 84.59 | 10.32 |
| A3 | sym-5ms | 5 | 5 | 5 | 0.625M | 921.06M | 3.12 | 3.77 | 2.74 | 2.78 | 4.02 | 2.38 | 2.21 | 84.46 | 9.94 |
| A4 | sym-3ms | 3 | 3 | 3 | 0.625M | 1.54G | 3.12 | 3.77 | 2.74 | 2.76 | 4.02 | 2.36 | 2.18 | 84.23 | 9.65 |
| B1 | asym-10ms | 20 | 10 | 10 | 0.625M | 460.53M | 3.15 | 3.78 | 2.77 | 2.84 | 4.03 | 2.44 | 2.22 | 84.34 | 10.18 |
| B2 | asym-5ms | 20 | 5 | 5 | 0.625M | 921.06M | 3.13 | 3.77 | 2.75 | 2.81 | 4.03 | 2.41 | 2.16 | 84.20 | 10.06 |
| B3 | asym-3ms | 20 | 3 | 3 | 0.625M | 1.54G | 3.15 | 3.78 | 2.77 | 2.80 | 4.02 | 2.40 | 2.16 | 84.17 | 9.85 |
| C1 | Learn-asym-10ms | 20 | 10 | 10 | 0.625M | 460.53M | 3.23 | 3.78 | 2.83 | 2.88 | 4.03 | 2.47 | 2.31 | 84.88 | 10.84 |
| C2 | Learn-asym-5ms | 20 | 5 | 5 | 0.625M | 921.06M | 3.19 | 3.81 | 2.82 | 2.80 | 4.03 | 2.40 | 2.31 | 85.02 | 10.64 |
| C3 | Learn-asym-3ms | 20 | 3 | 3 | 0.642M | 1.54G | 3.14 | 3.78 | 2.76 | 2.76 | 4.02 | 2.37 | 2.22 | 84.22 | 10.13 |
| D1 | asym-same_compute-10ms | 20 | 10 | 10 | 0.551M | 249.8M | 3.13 | 3.80 | 2.76 | 2.82 | 4.02 | 2.41 | 2.18 | 84.08 | 9.90 |
| D2 | asym-same_compute-5ms | 20 | 5 | 5 | 0.157M | 235.04M | 3.08 | 3.71 | 2.68 | 2.76 | 4.01 | 2.36 | 2.10 | 83.04 | 9.29 |
| D3 | asym-same_compute-3ms | 20 | 3 | 3 | 0.142M | 230.33M | 3.09 | 3.66 | 2.67 | 2.74 | 3.99 | 2.33 | 2.05 | 82.77 | 9.03 |
| E1 | Mamba-20ms | 20 | 20 | 20 | 0.642M | - | 3.19 | 3.80 | 2.81 | 2.87 | 4.03 | 2.46 | 2.27 | 84.59 | 10.61 |
| E2 | Mamba-10ms | 10 | 10 | 10 | 0.642M | - | 3.10 | 3.77 | 2.72 | 2.81 | 4.02 | 2.40 | 2.21 | 83.96 | 10.16 |
| E3 | Mamba-5ms | 5 | 5 | 5 | 0.642M | - | 3.03 | 3.67 | 2.63 | 2.73 | 4.00 | 2.33 | 2.15 | 83.42 | 9.71 |
| F1 | asym-10ms-medium | 20 | 10 | 10 | 2.32M | 1.09G | 3.19 | 3.77 | 2.80 | 2.85 | 4.02 | 2.44 | 2.30 | 84.75 | 10.56 |
| F2 | asym-5ms-medium | 20 | 5 | 5 | 2.32M | 2.20G | 3.16 | 3.80 | 2.78 | 2.84 | 4.03 | 2.43 | 2.19 | 84.15 | 10.07 |
| F3 | asym-3ms-medium | 20 | 3 | 3 | 2.32M | 3.66G | 3.18 | 3.78 | 2.80 | 2.82 | 4.02 | 2.42 | 2.22 | 84.68 | 10.16 |
| F4 | asym-10ms-large | 20 | 10 | 10 | 8.67M | 3.28G | 3.22 | 3.80 | 2.84 | 2.87 | 4.04 | 2.47 | 2.33 | 85.24 | 10.70 |
| F5 | asym-5ms-large | 20 | 5 | 5 | 8.67M | 6.57G | 3.22 | 3.77 | 2.83 | 2.85 | 4.03 | 2.45 | 2.29 | 85.08 | 10.55 |
| F6 | asym-3ms-large | 20 | 3 | 3 | 8.67M | 10.95G | 3.20 | 3.76 | 2.80 | 2.82 | 4.01 | 2.42 | 2.27 | 84.89 | 10.34 |
| G1 | asym-3ms-mapping | 20 | 3 | 3 | 0.625M | 1.54G | 3.10 | 3.74 | 2.70 | 2.70 | 4.01 | 2.28 | 1.91 | 81.85 | 8.19 |
| G2 | asym-6ms-predict | 6 | 6 | 3 | 0.625M | 767.57M | 3.06 | 3.71 | 2.65 | 2.71 | 4.01 | 2.29 | 2.09 | 83.35 | 9.34 |
| H1 | FBE-10ms | - | - | 10 | 0.656M | 256.1M | 3.15 | 3.68 | 2.72 | 2.80 | 3.93 | 2.36 | 2.05 | 82.98 | 8.91 |
| H2 | FBE-5ms | - | - | 5 | 0.644M | 590.6M | 3.11 | 3.65 | 2.68 | 2.75 | 3.93 | 2.32 | 2.00 | 82.90 | 8.60 |
| H3 | FBE-2.5ms | - | - | 2.5 | 0.637M | 1.098G | 3.07 | 3.58 | 2.62 | 2.71 | 3.89 | 2.27 | 1.89 | 81.73 | 7.80 |

### 4.3 Table II：弱模型上的非对称窗消融

Table II 固定增强主干为 U-Net（去掉 CRUSE 的 GRU bottleneck），只比较对称窗与输入窗 20 ms、输出窗更短的非对称窗：

| iWin (ms) | oWin (ms) | SIG | BAK | OVR |
|---:|---:|---:|---:|---:|
| 20 | 20 | 2.80 | 3.74 | 2.47 |
| 10 | 10 | 2.71 | 3.61 | 2.35 |
| 20 | 10 | 2.72 | 3.64 | 2.38 |
| 5 | 5 | 2.59 | 3.54 | 2.24 |
| 20 | 5 | 2.66 | 3.57 | 2.30 |
| 3 | 3 | 2.49 | 3.53 | 2.16 |
| 20 | 3 | 2.62 | 3.52 | 2.25 |

在弱 U-Net 上，20/10、20/5、20/3 的 OVR 分别高于同输出窗的 10/10、5/5、3/3；但在完整 CRUSE 上，论文认为非对称窗与对称窗差异不显著或略差。这是本文最关键的“容量与前端 trick 交互”证据。

### 4.4 原论文 Figure 1：质量与 MACs 随时延变化

![[wiki_low_latency/assets/2409.10358/2409.10358-page3-figure1.png]]

> 图注：原论文第 3 页 Figure 1，左图是不同低时延方法/模型大小的 DNSMOS OVR 与总时延，右图是 MACs/sec 与总时延。用途：视觉核对论文对“固定模型缩短 hop 会提高单位时间计算量、增大模型可补偿质量损失”的趋势描述。

### 4.5 哪个消融最关键：按因果问题拆开看

#### A. 非对称窗不是强 CRUSE 的通用增益

完整 CRUSE 的对称窗从 20 ms 缩到 10 ms，DNS blind OVR 仍为 2.79；到 5/3 ms 降为 2.74。相同输出窗下，asym-10ms/asym-5ms/asym-3ms 的 DNS blind OVR 为 2.77/2.75/2.77，没有显示稳定优于 sym。论文由此推测，强 CRUSE 能补偿短对称分析窗的损失；弱 U-Net 才更明显受益于非对称输入窗。

#### B. 模型容量能恢复短窗损失，但代价清楚

原始 asym-3ms（B3）为 0.625M、1.54G，模拟数据 OVR/PESQ/siSDR 为 2.40/2.16/9.85；large asym-3ms（F6）为 8.67M、10.95G，模拟数据为 2.42/2.27/10.34。论文进一步把 F6 与 20 ms 原始模型 A1 视为质量接近：DNS blind OVR 为 2.80 对 2.79，模拟 OVR 为 2.42 对 2.46。也就是说“3 ms 达到 20 ms 附近”是以更大的模型和更高 MACs 为代价，不是免费前端 trick。

same-compute 对照更能说明这一点：D3 在 3 ms 下把模型缩到 0.142M、230.33M MACs，DNS blind OVR/模拟 OVR/PESQ/siSDR 为 2.67/2.33/2.05/9.03，明显低于大容量行。低时延设计必须同时报告窗口、模型容量和 MACs。

#### C. Mamba 的低时延行为与“线性复杂度”宣传不等价

Mamba-20ms（E1）的 DNS blind OVR 为 2.81、模拟 OVR/PESQ/siSDR 为 2.46/2.27/10.61；到 Mamba-5ms（E3）下降为 2.63、2.33/2.15/9.71。论文结论是 Mamba 在标准 20 ms 表现不错，但缩短时延后明显退化。由于表 I 的 Mamba MACs 是 -，本文没有给出足够证据证明它在该设置下更省算。

#### D. FBE 在同一研究框架中质量落后

FBE-2.5ms（H3）的模型为 0.637M、1.098G，DNS blind OVR/模拟 OVR/PESQ/STOI/siSDR 为 2.62/2.27/1.89/81.73/7.80。论文概括 FBE overlap-save 版本显著低于 overlap-add 路线；它的低延迟实现不能仅凭较低的同延迟复杂度被判为更好。

#### E. 未来帧预测的收益被 mapping target 限制

在 G1/G2 对照中，G2 预测模型相对 G1：

| 设置 | DNS blind OVR | 模拟 OVR | PESQ | STOI (%) | siSDR |
|---|---:|---:|---:|---:|---:|
| G1 asym-3ms-mapping | 2.70 | 2.28 | 1.91 | 81.85 | 8.19 |
| G2 asym-6ms-predict | 2.65 | 2.29 | 2.09 | 83.35 | 9.34 |

G2 在模拟数据上略好，但在 DNS blind 上更差；而 A4/B3 的 filtering-based 模型在两类测试上都超过 G1/G2。论文将原因归于未来帧预测只能使用 mapping target，mapping 成为瓶颈，并指出该技巧在模拟训练数据上可能拟合得更好、对真实 DNS 数据泛化较差。

#### F. 学习前端在中高时延更有说服力，低时延不稳定

Learn-asym-10ms（C1）在 DNS blind 的 OVR 为 2.83、模拟 OVR/PESQ/siSDR 为 2.47/2.31/10.84；在 3 ms 的 C3 则为 2.76、2.37/2.22/10.13。作者结论认为 learnable transform 整体优于 fixed symmetric/asymmetric 选项，但表中 3 ms 各行差距变小，不能把该结论外推成所有严格 2 ms 条件都稳定获益。

### 4.6 质量、人声保留与噪声抑制证据边界

本文确实报告了 DNSMOS SIG（signal quality）、BAK（background quality）、OVR（overall quality）以及 simulated data 上的 STOI；这些是低时延质量/可懂度的有用证据。比如 original CRUSE 的 DNS blind SIG/BAK/OVR 从 A1 的 3.18/3.78/2.79 到 A4 的 3.12/3.77/2.74，缩短到 3 ms 时信号质量和总体质量都有下降。

但下列人声保留和低 SNR 证据在 PDF 中没有出现：

- 没有按 -10/-5/0/5 dB 或噪声类型分层；
- 没有 babble、竞争说话人、瞬态噪声和未见噪声的单独结果；
- 没有 false-suppression、SPP/VAD calibration、ASR WER、F0/formant/prosody continuity 或 voiced-energy 保留；
- 没有真实听者 MOS/A-B 听测；DNSMOS 是预测 MOS，不是本文新增的人工听测；
- 没有把 SIG-BAK trade-off 画成按 SNR/噪声类别分层的曲线。

因此本文能支持的是“统一条件下的低时延方法质量/可懂度比较”，不能支持“低 SNR 下人声保留已被充分验证”或“某方法无条件降低过抑制”。

### 4.7 计算量与 RTF/deadline 证据

论文报告的是模型参数量和处理 1 second audio data 的 MACs。代表性范围如下：

| 配置 | 模型 size | MACs | 论文中可支持的结论 |
|---|---:|---:|---|
| A1 sym-20ms | 0.625M | 230.27M | 原始 CRUSE 20 ms 质量/计算基线 |
| A4 sym-3ms | 0.625M | 1.54G | 同一模型缩短窗后单位时间 MACs 增长 |
| D3 same-compute 3ms | 0.142M | 230.33M | 保持计算预算时压小模型，质量明显损失 |
| F4 large 10ms | 8.67M | 3.28G | 更大容量可提高质量，但代价是模型和 MACs |
| F6 large 3ms | 8.67M | 10.95G | 质量接近 20 ms 原始模型，但计算远高于 A1 |
| H3 FBE-2.5ms | 0.637M | 1.098G | FBE 的表内预算与质量记录 |
| E1-E3 Mamba | 0.642M | - | MACs 未报告 |

RTF、CPU/GPU/SoC、峰值 RAM/SRAM、量化精度、batch=1 实测、p50/p95/p99、deadline miss、underrun/overrun、warm-up 和 long-stream stability 均未报告。故 MACs 小于某预算不能被改写成“端到端实时通过”。

![[wiki_low_latency/assets/2409.10358/2409.10358-page4-tables.png]]

> 图注：原论文第 4 页 Table I 与 Table II 的高分辨率页面渲染。用途：视觉核对全部结果行、模型大小/MACs、DNSMOS SIG/BAK/OVR 与 simulated-data PESQ/STOI/siSDR；表格列结构不以文本抽取结果为准。

## 5. 这个方向还剩什么问题没解决？（future work / limitation）

### 5.1 论文明确说了什么

论文没有单列 future-work 章节，结论主要总结了统一实验得到的观察：强模型下非对称窗优势不明显；Mamba 在标准时延尚可但低时延下降；learnable windows 整体较强；future-frame prediction 在相同时延下没有确定优势且受 mapping target 限制；增大模型可恢复短窗损失。因而，下面列出的“未解决问题”分为 PDF 明确缺失和本 Wiki 审计出的复现缺口，不把后者冒充作者已经承诺的 future work。

### 5.2 低时延系统仍缺的硬证据

| 未决项 | 本文状态 | 需要补的证据 |
|---|---|---|
| 采样率与样本级时序 | 未报告 | 给出 sample rate、帧锚点、每个窗的可读样本范围 |
| strict causality | 只明确写 causal 3x3 deep filters | 逐层检查右侧 padding、zero-padding、归一化、GRU/Mamba 状态和 FBE cache |
| 算法 vs 端到端时延 | 有 $L_s-P$ 和表中 latency | 测 ADC/DMA、input/output buffer、模型 p99、DAC 及 capture-to-playback |
| 运行时可靠性 | 未报告 RTF/硬件 | 流式 batch=1、p50/p95/p99、deadline miss、underrun/overrun、state reset、warm-up、长流 |
| 模型容量/功耗 | 只有参数量和 MACs | 目标芯片上的 SRAM/RAM、功耗、量化和热稳定性 |
| 人声保留 | SIG、STOI 等总指标 | 负 SNR 分层、false-suppression、SPP/VAD、ASR WER、F0/formant/prosody、voiced energy 和听测 |
| 噪声泛化 | 有真实来源的 DNS blind set，但无类别分层 | babble、竞争说话人、瞬态、混响、未见噪声的分层失败案例 |
| Mamba 计算优势 | 参数量相近，MACs 为 - | 同一实现、同一硬件、同一 batch 下的 MAC/RTF/p99 对照 |
| future prediction 因果解释 | mapping 与 filtering 混在方法差异中 | 固定 target type、同延迟、同模型容量，单独隔离预测本身的作用 |
| 指标协议一致性 | 正文写 validation，表头写 simulated data | 发布脚本、split、参考信号和指标计算位置 |

### 5.3 对当前低时延课题的机会

本文给出的可复用原则是：先固定一个小型 causal 主干，再分别扫描窗/hop、模型容量和目标形式；每个质量结论都要伴随 SIG-BAK、可懂度、MACs 和端侧时延账本。对本库的 2 ms 方向，最直接的补实验是：

1. 在明确采样率的 16 kHz、batch=1 流式设置下，做样本依赖 certificate；
2. 以 A1/A4/F6/D3 的思想构造质量-容量-MACs Pareto 曲线；
3. 加入 -10/-5/0/5 dB、babble/竞争说话人/瞬态/未见噪声分层；
4. 同时报告 DNSMOS SIG/BAK/OVR、STOI/eSTOI、siSDR、ASR WER、false-suppression 和 voiced-energy；
5. 在真实目标硬件测 compute p99、deadline miss 和 recovery/bypass。

这些是从本文证据缺口推导出的研究机会，不是本文已经验证的结果。

## 6. 本论文在库中的位置关联（cross-reference matrix）

| 关系 | 库中页面/论文 | 关联与边界 |
|---|---|---|
| 前身/基石 | [[wiki_low_latency/index]] 中的 CRUSE 参考文献 [1] | 本文把 CRUSE 作为统一 backbone；本地 index 只说明论文池位置，不能替代 [1] 原文的训练细节 |
| 前身/基石 | [STFT-Domain Neural Speech Enhancement with Very Low Algorithmic Latency](https://arxiv.org/abs/2204.09911) | 本文参考文献 [12]；同样关心短 STFT/未来帧与低算法延迟，本文补上统一现代 DNN 和真实 DNS blind 对照 |
| 同分支竞品 | [Integrated Full- and Sub-Band Modeling](https://arxiv.org/abs/2304.08707) | 低时延 full-/sub-band 路线；当前库中主要通过 index 记录，尚无同协议 source 页，数字不可直接横比 |
| 同分支竞品 | [[wiki_low_latency/entities/GCFSnet]] | GCFSnet 是 2023 双耳/多麦、复数 filter-and-sum 与延迟跨耳特征；本文是单通道统一 benchmark，二者分别覆盖空间信息与前端/容量控制 |
| 同分支竞品 | [[wiki/sources/2023/DeepFilterNet 2023]] | 都关注低复杂度、因果/深度滤波与实时增强；数据、采样率、指标和 latency 口径不同，不能把旧笔记数字与本文表 I 合并 |
| 同分支竞品 | [[wiki/sources/2021/FullSubNet 2021]] | 因果频域建模和实时部署是共同关切；本文提供更细的窗、模型容量和 FBE/future-predict 控制变量 |
| 后续/扩展线索 | [[wiki/sources/2024/Mamba for SE 2024]] | 两者都把 Mamba 放入语音增强；本文专门给出 20/10/5 ms 的低时延退化证据，但 Mamba MACs 未报告，不能据此宣称全面超越 |
| 跨分支类比 | [[wiki_low_latency/concepts/低比特率双耳特征链路]] | GCFSnet 的迟到空间特征与本文的“算法延迟不等于链路/计算时延”可互相校验；一个是多通道信息流，一个是单通道前端基准 |
| 跨分支类比 | [[wiki/concepts/实时与离线语音增强]] | 提供 algorithmic latency 与 real-time 的通用区分；本文的 $L_s-P$ 可作为该账本的论文实例 |
| 评价接口 | [[wiki/concepts/语音增强评价指标]] | 本文实际使用 DNSMOS、PESQ、STOI、siSDR；人声保留所需的 WER、false-suppression、F0/formant 等仍未加入论文评测 |

> [!question] 关联不确定性
> 本矩阵的论文关系来自本地已有 Wiki、wiki_low_latency/index 和 2409.10358 PDF 的参考文献；库中尚未为所有低时延候选论文建立 source 页面。除本文表 I/II 外，不把其他页面或研究地图中的摘要当作本论文数字证据。

## 7. 一句话总结“江湖地位”

~~~text
2024 | 单通道超低时延语音增强 | 用统一 CRUSE、真实世界 DNS 评测和模型容量对照证明“低时延质量的关键不只在窗技巧，容量与目标形式同样决定结果” → 成为低时延方法比较的系统审计基线，但尚未闭合 strict-causal、端到端 deadline 和低 SNR 人声保留证据。
~~~

### 参考资料

- [arXiv abstract page](https://arxiv.org/abs/2409.10358)
- [Local PDF](../../../raw/papers/low_latency_causal_se/2409.10358.pdf)
- 论文参考文献 [1]：Towards efficient models for real-time deep noise suppression，ICASSP 2021（本文 CRUSE backbone 来源）。
- 论文参考文献 [5,6]：非对称分析/合成窗的低时延方法。
- 论文参考文献 [10]：Low-latency monaural speech enhancement with deep filterbank equalizer。
- 论文参考文献 [11,12]：future-frame prediction 与 STFT-domain very-low-algorithmic-latency speech enhancement。
- 论文参考文献 [22]：Mamba: Linear-time sequence modeling with selective state spaces。
