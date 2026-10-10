---
title: FSB-LSTM - 全带与子带集成的超低算法时延语音增强
type: source
created: 2026-09-16
updated: 2026-09-16
tags:
  - speech-enhancement
  - low-latency
  - algorithmic-latency
  - full-band
  - sub-band
  - lstm
  - complex-tf
  - multichannel
  - hearing-aids
source_type: paper
year: 2023
authors: Zhong-Qiu Wang; Samuele Cornell; Shukjae Choi; Younglo Lee; Byeong-Yeol Kim; Shinji Watanabe
venue: arXiv preprint
arxiv: https://arxiv.org/abs/2304.08707
local_pdf: raw/papers/low_latency_causal_se/2304.08707.pdf
related:
  - [[wiki_low_latency/entities/FSB-LSTM]]
  - [[wiki_low_latency/concepts/2304.08707-full-sub-band-modeling]]
  - [[wiki_low_latency/index]]
  - [[wiki_low_latency/overview]]
  - [[wiki/sources/2021/FullSubNet 2021]]
  - [[wiki/concepts/全带与子带模型]]
  - [[wiki/concepts/STFT与频谱图]]
  - [[wiki_low_latency/entities/GCFSnet]]
---

~~~yaml
- 论文: [Neural Speech Enhancement with Very Low Algorithmic Latency and Complexity via Integrated Full- and Sub-Band Modeling](2023)
  ├── 要解决什么问题: 在噪声-混响环境中做单/多通道 STFT 语音增强，同时把算法延迟、逐帧计算和运行时缓存压到助听器等端侧可接受范围
  ├── 核心方法: FSB-LSTM；每个模块用全带 LSTM 建模所有频率、用共享子带 LSTM 建模下采样频率序列，并通过过完备 T-F 残差高速路反复细化
  ├── 属于哪个分支: 低算法时延 / 低复杂度 / 复数时频映射 / 单通道与多麦克风语音增强
  ├── 输入/输出: P 个麦克风复数 STFT 的 RI 堆叠 [2P×T×F] → 参考麦克风目标 RI 频谱 S_q → iSTFT 波形
  ├── 关键trick: 频率下采样后再递归、full/sub-band 残差相加、全时轴卷积核为 1、用频率 overlap-add 实现低 MAC Deconv2D
  ├── 前端/延迟: 默认 iWS=16 ms、HS=2 ms、oWS=4 ms、256-point DFT 得 129 维复数谱；论文口径算法延迟为 4 ms
  ├── 数据集: WSJCAM0 clean speech + FSD50K 噪声；39,245/2,965/3,260 个训练/验证/测试混合，16 kHz，六麦圆阵仿真
  ├── 关键结果: 6ch FSB-LSTM 为 1.96M 参数、3.37 GMAC/s、SI-SDR=7.8 dB、PESQ=2.61、eSTOI=0.830；2ch/1ch 也优于各自 FB-LSTM 对照
  ├── 关键消融: FSB-LSTM 对 FB-LSTM 的替换实验支持子带块的增益；FB-LSTM 的 HS/oWS 扫描显示 1 ms hop / 2 ms oWS 性能最好但 MAC 约翻倍
  ├── 遗留问题(你的机会): 未报告 RTF、真实硬件 capture-to-playback/p99、deadline miss、能耗、ASR 或 false-suppression；人声保留只有综合指标间接支持
  └── 跟哪篇像: [[wiki/sources/2021/FullSubNet 2021]]、[[wiki/concepts/全带与子带模型]]、[[wiki_low_latency/sources/2023/GCFSnet 2023]]、[[wiki/sources/2023/DeepFilterNet 2023]]
~~~

# Neural Speech Enhancement with Very Low Algorithmic Latency and Complexity via Integrated Full- and Sub-Band Modeling

Zhong-Qiu Wang, Samuele Cornell, Shukjae Choi, Younglo Lee, Byeong-Yeol Kim, Shinji Watanabe，arXiv:2304.08707v1，18 Apr 2023。

> [!warning] PDF 转换质量与阅读说明
> 原 PDF 共 5 页。Poppler 渲染时报告 `No display font for 'Symbol'` 与 `No display font for 'ArialUnicode'`，但第 1-5 页页面图像仍可视觉阅读。pypdf 文本抽取存在连字（如 `ﬂ`）、上下标/撇号和表格小数空格被摊平等问题；第 2-4 页的公式、网络尺寸、表格数值和图中标签均以原页面视觉核对。本笔记不把抽取文本中无法确认的符号或数字当作证据，原图页面截图保留在本页嵌入位置。

## 1. 他们为什么这么做？（motivation）

### 1.1 任务与对象

论文研究的是**噪声-混响条件下的单通道与多通道语音增强**，目标是估计参考麦克风 q 捕获的目标说话人 direct-path signal。论文将单个 N-sample、多麦克风混合写为：

$$
y[n]=s[n]+v[n],\qquad y[n],s[n],v[n]\in\mathbb{R}^{P}.
$$

其中：

- y[n]：P 个麦克风在样本 n 的混合；
- s[n]：目标说话人的 direct-path 信号；
- v[n]：非目标信号，包含噪声和混响成分；
- P：麦克风数；q：输出参考麦克风。

在 STFT 域，论文写为：

$$
Y(t,f)=S(t,f)+V(t,f)\in\mathbb{C}^{P},
$$

Y,S,V 分别是 y,s,v 的 STFT，t 索引 T 个时间帧，f 索引 F 个频率。网络不是预测一个标量掩蔽，而是从所有输入麦克风的复数谱预测目标参考通道 S_q 的实部/虚部。

### 1.2 论文所面对的端侧矛盾

论文指出，取得强增强性能的网络通常包含较多卷积、循环或 self-attention 模块，带来计算、内存和处理时延负担；助听器等产品的计算资源更受限。作者特别强调：在现代边缘设备上，模型存储小于 20 MB 往往已经足够，真正紧张的是**一帧进、一帧出**时的运行时内存、算法复杂度和每帧计算量。

论文引用的 hearing-aid 设计要求通常低于 5 ms，并指出在 50% overlap-add 下 hop size 不能超过约 2.5 ms。于是问题不只是“网络参数少”，而是要让每个小 hop 的网络计算也能在下一次 hop 前结束，并且不需要缓存大量历史帧。

### 1.3 论文目标的可审计版本

| 维度 | PDF 明确内容 |
|---|---|
| 任务 | noisy-reverberant speech enhancement；single- 与 multi-channel |
| 信号域 | STFT complex spectral mapping |
| 输入 | P 个麦克风的 RI 复数谱，堆叠成 2P × T × F |
| 输出 | 参考麦克风 q 的目标 RI 频谱，之后 iSTFT 得到增强波形 |
| 采样率/谱 | 16 kHz；256-point DFT；每帧 129-dimensional complex spectra |
| 默认前端 | iWS=16 ms，HS=2 ms，oWS=4 ms；论文将算法延迟记为 4 ms |
| 设计目标 | 低算法复杂度、低运行时 buffer、低算法延迟，同时维持增强质量 |

## 2. 之前的人怎么做不了？（limitation → gap）

### 2.1 论文列出的既有路线限制

| 路线 | 论文中的能力 | 对本问题的限制 |
|---|---|---|
| 原始 attention | 可看过去帧以捕获长程上下文 | 需要缓存许多过去帧，运行时内存较大，不理想于低复杂度在线增强 |
| Conv2D / UNet 类模型 | 参数数目可控，也能提取 T-F 特征 | 大 kernel、较多输入/输出通道会带来较高计算量 |
| DPRNN、TF-GridNet 等 dual-path | 长序列与子带信息建模能力强 | 计算昂贵；论文特别指出 TF-GridNet 每个频率运行 LSTM，且每帧不能并行处理序列全部步骤 |
| 直接堆叠 LSTM | 能沿帧序列建模 | 直接把 2P × F 输入压到较小隐藏维时，多麦克风的空间信息可能在瓶颈处损失 |
| Conv-TasNet 等时域模型 | 可以用短窗取得低算法延迟 | 编码器后立即形成 bottleneck；高输入维度时可能损失细粒度多通道模式，部分实现还需缓存时间膨胀卷积的历史 |
| 早期低时延 LSTM 研究 | 说明循环网络可以在线工作 | 多在单通道、teleconferencing 条件下研究，允许的延迟可到 40 ms，常用 8/10/16 ms 等较大 hop，不直接覆盖助听器尺度 |

### 2.2 从 limitation 到 gap

论文的 gap 可以压缩为：**怎样用很小的逐帧缓存和可控的 MAC，同时保留多麦克风 T-F 表示中的细粒度空间/谱时模式，并将算法延迟压到 hearing-aid 所需的毫秒量级？** 论文的默认 FSB-LSTM 配置为 4 ms，另用 FB-LSTM 控制实验覆盖 2 ms 的 oWS。

FSB-LSTM 的回答不是立即把所有通道压进一个窄 bottleneck，而是让一个 D-维、过完备的 T-F 表示沿多个模块通过 residual connection 传递；每个块只把频率维下采样到适合 LSTM 的尺度，在 LSTM 处理后再上采样并加回输入。

### 2.3 因果性与 latency ledger

| 账本项目 | PDF 明确证据 | 证据边界/本 Wiki 判定 |
|---|---|---|
| 时间卷积 | 所有卷积在时间轴 kernel size 为 1；作者称因此不必因果卷积地缓存过去帧 | 支持 streaming；仍需实现级核对 padding 与状态，不等于端到端 certificate |
| 循环状态 | 使用多层 unidirectional LSTM；运行时只需缓存过去帧的 hidden/cell states | 论文级 causal LSTM 证据；没有逐层 state reset、边界和最后可读样本的 certificate |
| STFT/iSTFT | 默认 iWS=16 ms、HS=2 ms、oWS=4 ms；论文使用大输入窗和小输出窗的 overlap-add 机制 | 论文口径算法延迟为 4 ms；输入窗、输出窗与硬件调度的端到端关系需复现 |
| 更低 hop 的实验 | Table 2 是 **FB-LSTM（full-band-only 对照）**，测试 HS/oWS 为 8/16、4/8、2/4、1/2 ms | 只能证明 full-band 控制可在 1 ms hop 下工作，不能把 1 ms/2 ms 的指标直接归给 FSB-LSTM |
| 未来上下文 | 论文讨论称减小 HS/oWS 后可利用的 future context（最多到 oWS）变少 | 因而不把整套系统无条件标成 strict causal；更准确是 paper-level low-latency/frame-online |
| 硬件时延 | 论文说硬件时延需要小于 hop size 才能实现实时，并称小 buffer 有利于此 | 没有给硬件平台、wall-clock、deadline miss 或 p50/p95/p99 |
| RTF | 未报告 | 不能从 GMAC/s 推出 RTF；需在目标硬件实测 |
| capture-to-playback | 未报告 | 4 ms 是算法延迟口径，不是完整 ADC/DMA/计算/DAC 端到端数字 |

## 3. 这个做法核心 trick 是什么？

### 3.1 总体数据流

```text
P 个麦克风复数 STFT 的 RI 堆叠 [2P, T, F]
        │
        ├─ Conv2D (time kernel=1, frequency kernel=3) → D 维 T-F embedding
        │
        ├─ B 个 FSB-LSTM modules
        │     ├─ Full-band block：频率下采样 → frame-level LSTM → 上采样 → residual
        │     └─ Sub-band block：频率下采样 → 共享 sub-band LSTM → 上采样 → residual
        │
        ├─ Deconv2D (time kernel=1, frequency kernel=3) → 参考通道目标 RI 频谱
        └─ iSTFT → 增强目标波形
```

![[wiki_low_latency/assets/2304.08707/2304.08707-page2-architecture-table1.png]]

> 图注：原论文第 2 页 Figure 1 与 Table 1 的页面渲染。用途：核对输入 STFT、B × FSB-LSTM 模块、全带/子带块、Deconv2D、iSTFT 的连接关系及符号表；这是论文原页面截图，不是 AI 重画。

### 3.2 先保留过完备 T-F 表示，再让递归块做分工

网络首先把 2P × T × F 的 RI 输入映射为 D × T × F 的 T-F embedding。之后每个 FSB-LSTM module 依次包含一个 full-band block 和一个 sub-band block；两个块都遵循同一结构原则：

1. 在频率维下采样，提取适合循环网络的 discriminative features；
2. 只沿时间帧用 LSTM 建模，避免时间卷积引入过去帧 buffer；
3. 在频率维上采样回原尺寸；
4. 将细化结果加回原始 D × T × F 输入。

这条“information highway”保留了多麦克风输入的细粒度谱时和空间模式；LSTM 不必独自承担从 2P × F 到小隐藏维的全部压缩任务。

### 3.3 Full-band block：一次看所有频率

给定输入张量 D × T × F，full-band block 的 Conv2D 使用输入通道 D、输出通道 E、kernel 1 × I、stride 1 × J，只在频率轴做压缩。论文将频率 zero-padding 后的长度定义为：

$$
Q=\left\lceil\frac{F-I}{J}\right\rceil J+I,
$$

Conv2D 的输出为：

$$
E\times T\times\left(\frac{Q-I}{J}+1\right).
$$

把第一和第三维摊平后得到 T × A，其中：

$$
A=E\times\left(\frac{Q-I}{J}+1\right).
$$

接着的顺序是：PReLU → causal global layer normalization（cGLN）→ H-unit LSTM → linear H → A → cGLN/PReLU → reshape → Deconv2D。full-band 的 cGLN 以因果方式基于两个维度计算均值/方差，并用两个 A-维向量沿第一维缩放和移位。Deconv2D 把 E 通道恢复为 D 通道，并将去除 padding 后的结果通过 residual connection 加回 block 输入。

物理/工程含义是：LSTM 的每个时间步骤接收一个包含所有下采样频率位置的 frame-level embedding，因此能同时利用 full-band 的频谱结构；它不是为每个频率各跑一个独立 full-band LSTM。

### 3.4 Sub-band block：保留局部频率分辨率但减少频率数

sub-band block 也从 D × T × F 开始，但用输入通道 D、输出通道 E'、kernel 1 × I'、stride 1 × J' 的 Conv2D 下采样频率。zero-padding 长度为：

$$
Q'=\left\lceil\frac{F-I'}{J'}\right\rceil J'+I',
$$

下采样后的张量为：

$$
E'\times T\times\left(\frac{Q'-I'}{J'}+1\right).
$$

论文将其视为 ((Q'-I')/J' + 1) 条、每条长度为 T 的时间序列，并用 H'-unit LSTM 逐条细化。这个 LSTM 在所有 sub-band 之间共享，以降低参数量；3D sub-band 张量的 cGLN 以因果方式基于三个维度计算均值/方差，并用两个 E'-维向量沿第一维缩放和移位。随后用 Deconv2D 恢复为 D × T × F，去 padding 后通过 residual connection 加回输入。

与“每个原始频率运行一个子带模块”的高开销路线相比，FSB-LSTM 先把频率数压低；论文的默认设置最终有 26 个 sub-bands，且 sub-band module 的 MAC 约为 full-band module 的两倍。

### 3.5 低 MAC 的 Deconv2D 实现

论文没有直接用典型的“先插入 stride 个零、再做转置卷积”实现 Deconv2D，而是用 linear layer 加上沿频率的 overlap-add。这样可以避免对插入的零做无效乘加；论文报告该实现的 MAC 大约是典型实现的 1/J，其中 J 是 stride。这里的 overlap-add 是频率维操作，不是 iSTFT 的时间 overlap-add。

### 3.6 关键符号与默认配置

| 符号 | 论文含义 | 默认值/备注 |
|---|---|---|
| N | 输入混合的样本数 | 论文未给固定数值 |
| P | 麦克风数 | 6ch、2ch、1ch 三种评测；2ch 使用第 1 和第 4 麦克风，1ch 使用第 1 麦克风 |
| q | 目标参考麦克风 | 训练标签与指标参考为第 1 麦克风的 direct-path target |
| (T,F) | 时间帧数、频率数 | 256-point DFT 得 129 维 complex spectrum |
| D | 每个 T-F unit 的 embedding 维数 | 32 |
| B | FSB-LSTM modules 数 | 3 |
| E,I,J,H | full-band Conv/Deconv 通道、频率 kernel、频率 stride、LSTM hidden units | 8、8、4、256 |
| E',I',J',H' | sub-band Conv/Deconv 通道、频率 kernel、频率 stride、LSTM hidden units | 64、5、5、64 |

### 3.7 输入、输出与损失

Figure 1 的输入是所有麦克风复数 STFT 的 real/imaginary（RI）分量堆叠，形状为 2P × T × F。前端 Conv2D 后，FSB-LSTM 逐块细化 D × T × F embedding；末端 Deconv2D 预测目标参考通道 S_q 的 RI 分量，最后 iSTFT 进行重合成。

损失定义在重合成信号及其 magnitude 上，论文称其为沿用 [3] 的 **Wav+Mag loss**。目标 PDF 没有给出该损失的完整展开式或权重，因此本页只记录名称和作用，**不补造公式，不把 [3] 的外部定义冒充为本论文 PDF 的明示公式**。

## 4. 实验里哪个消融最关键？

### 4.1 数据、训练与评测设置

数据是模拟的 noisy-reverberant 语音增强集：

- 使用 WSJCAM0 的 clean speech split，生成训练/验证/测试混合数分别为 39,245（约 77.7 h）、2,965（约 5.6 h）、3,260（约 8.5 h）；
- FSD50K development set 的 clips 用于训练/验证噪声，evaluation set 用于测试噪声；每个混合最多 7 个 noise clips，其中 1 个长于 10 s 作为 background，其余作为 foreground；
- 六个模拟麦克风均匀排在直径 20 cm 的圆上；每个声源到阵列中心的方向从 [0, 2π) 采样，距离从 [0.75, 2.5] m 采样，混响时间从 [0.2, 1.0] s 采样；
- 每个声源视为 point source，与模拟 room impulse response 卷积后相加；目标 direct-path speech 与 reverberant noise 的 SNR 从 [-8, 3] dB 采样；采样率 16 kHz；
- 2ch 只使用第 1 与第 4 麦克风，1ch 只使用第 1 麦克风；第 1 麦克风的 target direct-path signal 是训练 label 和指标 reference。

论文明确给出的训练可复现信息有限：所有 baseline 使用与 FSB-LSTM 相同的 loss，但目标 PDF 未报告 epoch、batch size、optimizer、learning rate、学习率调度、随机种子、训练硬件或公开代码/commit。因此这些字段均为“未报告/需复现”。

### 4.2 评价指标与证据范围

- **SI-SDR**：scale-invariant signal-to-distortion ratio；
- **PESQ**：使用 `python-pesq (v0.0.2)`，报告 narrow-band MOS-LQO；
- **eSTOI**：extended short-time objective intelligibility；
- **参数量**：以 million（M）报告；
- **计算量**：用 `ptflops` 统计 GMAC/s。

这些指标支持“相对于论文内同条件对照，增强后的整体失真/质量/可懂度更好”的结论；论文没有给主观听感、DNSMOS、noise-only BAK、VAD false-suppression、ASR WER、F0/formant/prosody continuity 或专门的人声保留分数。尤其不能仅凭 SI-SDR/PESQ/eSTOI 宣称弱辅音、气声或音节边缘没有被误抑制。

### 4.3 低时延消融：FB-LSTM 的 hop/oWS 扫描（Table 2）

该表是 6ch **FB-LSTM（只保留 full-band block 的对照）**，iWS 固定为 16 ms；HS 与 oWS 一起减半，保持 overlap-add 的 50% frame-overlap。论文报告 HS 每减半，待处理帧数翻倍，计算量约翻倍。

| 系统 | iWS (ms) | oWS (ms) | HS (ms) | #params (M) | GMAC/s | SI-SDR (dB) | PESQ | eSTOI |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Unprocessed | - | - | - | - | - | -6.2 | 1.44 | 0.411 |
| FB-LSTM (6-layer) | 16 | 16 | 8 | 3.59 | 0.58 | 3.9 | 2.06 | 0.721 |
| FB-LSTM (6-layer) | 16 | 8 | 4 | 3.59 | 1.16 | 5.8 | 2.28 | 0.776 |
| FB-LSTM (6-layer) | 16 | 4 | 2 | 3.59 | 2.33 | 6.8 | 2.37 | 0.795 |
| FB-LSTM (6-layer) | 16 | 2 | 1 | 3.59 | 4.65 | 8.0 | 2.54 | 0.821 |

这个消融把“更小算法延迟”和“更高每秒 MAC”直接放在一起：在 full-band-only 控制中，oWS=2 ms、HS=1 ms 给出最高指标，但 GMAC/s 为 4.65。它是低时延设计的重要证据，却不是 FSB-LSTM 在 2 ms 的直接结果。

### 4.4 主结果：6ch、2ch、1ch

#### Table 3：6ch speech enhancement

| 系统 | #params (M) | GMAC/s | SI-SDR (dB) | PESQ | eSTOI |
|---|---:|---:|---:|---:|---:|
| Unprocessed | - | - | -6.2 | 1.44 | 0.411 |
| FSB-LSTM | 1.96 | 3.37 | **7.8** | **2.61** | **0.830** |
| FB-LSTM (6-layer) | 3.59 | 2.33 | 6.8 | 2.37 | 0.795 |
| FB-LSTM (9-layer) | 5.38 | 3.43 | 7.6 | 2.51 | 0.816 |
| MC-Conv-TasNet | 6.37 | 3.76 | 5.2 | 2.24 | 0.764 |
| LSTM-ResUNet | 2.33 | 3.54 | 6.2 | 2.23 | 0.767 |

#### Table 4：2ch speech enhancement

| 系统 | #params (M) | GMAC/s | SI-SDR (dB) | PESQ | eSTOI |
|---|---:|---:|---:|---:|---:|
| Unprocessed | - | - | -6.2 | 1.44 | 0.411 |
| FSB-LSTM | 1.96 | 3.31 | **4.9** | **2.20** | **0.753** |
| FB-LSTM (6-layer) | 3.59 | 2.27 | 4.2 | 2.07 | 0.729 |
| FB-LSTM (9-layer) | 5.38 | 3.37 | 4.5 | 2.14 | 0.744 |
| MC-Conv-TasNet | 6.19 | 3.68 | 3.6 | 2.00 | 0.711 |
| LSTM-ResUNet | 2.33 | 3.48 | 4.3 | 2.06 | 0.726 |

#### Table 5：1ch speech enhancement

| 系统 | #params (M) | GMAC/s | SI-SDR (dB) | PESQ | eSTOI |
|---|---:|---:|---:|---:|---:|
| Unprocessed | - | - | -6.2 | 1.44 | 0.411 |
| FSB-LSTM | 1.96 | 3.30 | **3.1** | **1.92** | **0.688** |
| FB-LSTM (6-layer) | 3.59 | 2.25 | 2.6 | 1.84 | 0.671 |
| FB-LSTM (9-layer) | 5.38 | 3.35 | 2.5 | 1.83 | 0.667 |
| Conv-TasNet | 6.18 | 3.67 | 2.2 | 1.78 | 0.657 |
| LSTM-ResUNet | 2.32 | 3.47 | 2.8 | 1.90 | 0.682 |

![[wiki_low_latency/assets/2304.08707/2304.08707-page4-results-tables2-5.png]]

> 图注：原论文第 4 页 Table 2、Table 3、Table 4、Table 5 及其相邻正文的页面渲染。用途：核对 hop/oWS 消融、三种通道数下的 SI-SDR/PESQ/eSTOI、参数量和 GMAC/s；该图保留原论文表格版式，不是 AI 重画。

### 4.5 哪个消融最关键？

对论文核心架构而言，最有因果解释力的是把 Figure 1 中的 sub-band module 替换为 full-band module，形成 FB-LSTM，再比较 6-layer 与 9-layer 控制：

- **6ch**：FSB-LSTM 以 1.96M 参数、3.37 GMAC/s 得到 7.8 dB / 2.61 / 0.830；FB-LSTM 6-layer 为 3.59M、2.33 GMAC/s、6.8 / 2.37 / 0.795，9-layer 为 5.38M、3.43 GMAC/s、7.6 / 2.51 / 0.816；
- **2ch**：FSB-LSTM 为 4.9 / 2.20 / 0.753，高于 FB-LSTM 6-layer 的 4.2 / 2.07 / 0.729 和 9-layer 的 4.5 / 2.14 / 0.744；
- **1ch**：FSB-LSTM 为 3.1 / 1.92 / 0.688，高于 FB-LSTM 6-layer 的 2.6 / 1.84 / 0.671 和 9-layer 的 2.5 / 1.83 / 0.667。

因此，PDF 支持的最稳妥结论是：在这套模拟数据和相同指标下，加入 sub-band blocks 能让 FSB-LSTM 在单/双/六通道设置均超过 full-band-only 控制，而且参数量低于两个 FB-LSTM 控制。它不是严格等 GMAC、等参数的单变量消融，所以不能把全部差异归因于 sub-band 机制本身；但跨三种通道设置的方向一致，证据较强。

### 4.6 低时延、噪声抑制、人声保留的证据审计

| 审计目标 | 论文直接支持 | 不能从本文推出 |
|---|---|---|
| 低算法时延 | 默认 FSB-LSTM 配置的算法延迟口径为 4 ms；FB-LSTM 对照可到 HS=1 ms、oWS=2 ms；时间卷积 kernel=1，LSTM 只保留状态 | FSB-LSTM 在 oWS=2 ms 的直接结果、真实硬件 RTF、端到端 p99、deadline 通过率 |
| 噪声抑制 | 在模拟 noisy-reverberant 测试中 SI-SDR、PESQ、eSTOI 均优于未处理和论文内主要 baseline；目标 reference 是 direct-path target | 各噪声类型/频段的抑制曲线、noise-only BAK、强负 SNR 分层、包络噪声或残余混响的独立分数 |
| 人声保留 | SI-SDR、PESQ、eSTOI 的整体改善间接表明目标重建有效；网络输出目标 direct-path RI 谱 | 无 ASR WER、语音失真分解、弱辅音/气声/音节边缘、F0/formant/prosody 连续性、false-suppression 或主观听感证据 |

### 4.7 计算量、运行时缓存与 deadline 证据账本

论文以 GMAC/s 统计模型计算量，以 million（M）报告参数量，并以单精度浮点 streaming setup 估算运行时 buffer。FSB-LSTM 的 buffer 为 46.2 KB；同一段比较中 Conv-TasNet 和 LSTM-ResUNet 的 buffer 分别为 3133.4 KB 和 1815.1 KB。这个结果支持“FSB-LSTM 的状态缓存更小、适合放入较高 cache 层级”的工程判断，但仍属于模型/内存预算。

| 证据层级 | PDF 给出的数字/描述 | 尚不能推出 |
|---|---|---|
| 参数与 MAC | FSB-LSTM 1.96M 参数；GMAC/s 为 3.37（6ch）、3.31（2ch）、3.30（1ch）；FB-LSTM HS=1 ms 时 4.65 GMAC/s | 具体芯片每帧耗时或能耗 |
| streaming buffer | FSB-LSTM 46.2 KB；Conv-TasNet 3133.4 KB；LSTM-ResUNet 1815.1 KB | 实际 cache miss、DMA/I/O 和峰值内存 |
| real-time 条件 | 论文称硬件时延需小于 hop size，且小 buffer/低复杂度有利于实现增强 | 实测 RTF、deadline miss、p99 或 capture-to-playback 通过率 |

## 5. 这个方向还剩什么问题没解决？（future work / limitation）

### 5.1 论文明确提出的 future work

结论段明确提出继续降低 algorithmic latency，并探索 DNN quantization 与 distillation，以进一步减少复杂度，同时保持增强性能。

### 5.2 面向低时延语音增强的 Wiki 审计

1. **4 ms 不是端到端 deadline 证明**：论文给的是 iWS/HS/oWS 机制下的算法延迟；没有 ADC、DMA、输入输出 buffer、实际计算 wall-clock、DAC、underrun 或 p99。
2. **2 ms 证据属于 FB-LSTM 控制**：Table 2 的 HS=1 ms/oWS=2 ms 是 full-band-only 模型，不应写成 FSB-LSTM 已在 2 ms 端到端验证。
3. **strict causality 仍缺逐层证书**：单向 LSTM 与时间 kernel=1 支持因果 streaming，但 zero-padding、cGLN 的在线统计、iSTFT 边界和状态管理没有按最后可读样本逐层列出。
4. **RTF 与 deadline 缺失**：GMAC/s 和 buffer KB 是模型预算，不等于目标芯片上的 RTF<1，更不等于每个 hop 的 p99 deadline 通过。
5. **人声保留没有被单独量化**：没有把噪声抑制和 target speech distortion 分开，也没有 false-suppression 或下游 ASR 结果；因此“增强更强”不应改写成“所有人声细节都保住”。
6. **测试是模拟场景**：论文使用固定六麦圆阵、点源、模拟 room impulse response 和 FSD50K 噪声，尚未给真实助听器/真实房间/真实录音的鲁棒性证据。
7. **训练复现字段不全**：目标 PDF 未报告 optimizer、learning rate、batch、epoch、seed、训练硬件和公开代码版本；Wav+Mag 的展开式也不在本文正文中。
8. **量化/蒸馏只有方向，没有结果**：作者将其列作 future research；本文不能宣称已经完成定点部署或量化 Pareto。

### 5.3 对当前方向的可检验延伸

若将 FSB-LSTM 放入“约 2 ms、strict causal、噪声抑制 + 人声保留”的主线，下一组实验至少应把以下项目分开报告：

- 用同一 FSB-LSTM 在 oWS/HS=4/2 与 2/1 下做真正的端到端流式测试，并报告 p50/p95/p99、deadline miss 和 RTF；
- 以 direct-path target 为参考，增加 speech distortion、VAD false-suppression、ASR/WER 或音素/有声周期连续性指标；
- 做低 SNR 和噪声类型分层，避免只用 pooled SI-SDR/PESQ/eSTOI 代替噪声抑制与人声保留的分解；
- 对 full-only、sub-band-only、FSB residual 和不同频率 stride 做参数/MAC 尽量匹配的单变量消融；
- 在真实多麦/助听器链路上测量输入窗、缓存、硬件调度和状态恢复。

## 6. 本论文在库中的位置关联（cross-reference matrix）

| 关系 | 库中页面 | 关联与差异 |
|---|---|---|
| 同方向低时延、多通道 | [[wiki_low_latency/sources/2023/GCFSnet 2023]] | 两者都面向端侧/助听器量级低时延和多通道增强；FSB-LSTM 预测参考通道复数谱，GCFSnet 做本侧复数 filter-and-sum 与后滤波，前端、链路和延迟口径不同，数字不可直接横比 |
| 同一频率分治母题 | [[wiki/sources/2021/FullSubNet 2021]] | FullSubNet 以 full-band + sub-band 处理单通道幅度/掩蔽；FSB-LSTM 在复数多麦 RI 谱上用下采样、LSTM 和过完备 residual highway，属于同母题的不同实现 |
| 概念基准 | [[wiki/concepts/全带与子带模型]] | 该概念页提供“全带看全局、子带保局部”的频率分工；本页补充 FSB-LSTM 的 26 sub-bands、shared LSTM 和 4 ms 低时延证据 |
| STFT 输入域 | [[wiki/concepts/STFT与频谱图]] | FSB-LSTM 的 (Y=S+V)、RI 堆叠和 256-point DFT 属于该概念页的复数时频建模分支 |
| 低复杂度复数滤波 | [[wiki/sources/2023/DeepFilterNet 2023]] | 都关注低复杂度、复数时频处理和实时增强；DeepFilterNet 走 DSP + deep filtering，FSB-LSTM 走多麦 complex spectral mapping，实验数据/指标不直接可比 |
| 复数 T-F 基线 | [[wiki/sources/2020/DCCRN 2020]] | FSB-LSTM 与 DCCRN 都预测/处理 RI 频谱，但本文用 full/sub-band LSTM 和频率下采样，不能把 DCCRN 的结果迁移为本论文结果 |
| 时间维分治对照 | [[wiki/sources/2021/DPCRN 2021]] | DPCRN 主要在时间维做 dual-path，FSB-LSTM 主要在频率维做 full/sub-band 分工；两者需要同数据、同延迟和同计算预算的公平实验 |
| 本方向目录 | [[wiki_low_latency/index]] | 2304.08707 在目录中登记为 full-/sub-band LSTM；本次只新增本 source/entity/concept/assets，不修改目录 |

## 7. 一句话总结“江湖地位”

~~~text
2023 | 低算法时延时频语音增强 | FSB-LSTM 用过完备 T-F residual highway 把 full-band 与下采样 sub-band LSTM 集成，在 1.96M 参数和 3.30、3.31、3.37 GMAC/s 下取得跨单/双/六通道的强结果，默认算法延迟为 4 ms；但 2 ms 只由 FB-LSTM 控制支撑，真实 RTF/deadline 与人声保留证据仍未闭环。
~~~

### 参考资料

- [arXiv abstract page](https://arxiv.org/abs/2304.08707)
- [Local PDF](../../../raw/papers/low_latency_causal_se/2304.08707.pdf)
- [[wiki_low_latency/entities/FSB-LSTM]]
- [[wiki_low_latency/concepts/2304.08707-full-sub-band-modeling]]
- [[wiki_low_latency/index]]
