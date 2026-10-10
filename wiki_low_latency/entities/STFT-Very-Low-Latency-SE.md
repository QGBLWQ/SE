---
title: STFT-Very-Low-Latency-SE
aliases:
  - 双窗 STFT 超低算法时延语音增强
  - LSTM-ResUNet low-latency STFT enhancement
type: entity
created: 2026-09-16
updated: 2026-09-16
tags:
  - speech-enhancement
  - low-look-ahead
  - frame-online
  - stft
  - complex-spectral-mapping
  - multichannel
  - beamforming
sources:
  - [[wiki_low_latency/sources/2022/STFT-Domain Very Low Algorithmic Latency 2022]]
related:
  - [[wiki_low_latency/concepts/2204.09911-short-asymmetric-stft]]
  - [[wiki_low_latency/index]]
  - [[wiki_low_latency/entities/GCFSnet]]
  - [[wiki_low_latency/sources/2023/GCFSnet 2023]]
  - [[wiki/sources/2019/Conv-TasNet - Surpassing Ideal TF Masking 2019]]
  - [[wiki/sources/2020/PercepNet 2020]]
  - [[wiki_array/concepts/波束成形 Beamforming]]
---

# STFT-Very-Low-Latency-SE

## 简洁定义

这是论文 2204.09911 提出的一个**低 look-ahead、frame-online 的 STFT 语音增强系统**，不是一个有独立专名的单一网络。它用较长的 analysis window 保留频率分辨率，用较短的 output window 做 iSTFT overlap-add；再把复数谱映射、在线 multi-channel Wiener filter（MCWF）和第二个 DNN 组合起来。论文把该系统的 algorithmic latency 做到 4 ms，并用 future-frame prediction 展示 2 ms 配置。

本实体适合记录“系统级方法”：时延来自 STFT-iSTFT 的窗口/OLA，质量来自复数映射和 beamforming/post-filter，部署可行性则由每帧硬件计算是否赶上 hop 决定。

> [!warning] 证据边界
> 论文的 strong claim 是 4 ms/2 ms algorithmic latency。默认 16 ms analysis window 明确 look ahead 4 ms，因此不能标成 strict sample-causal；论文只假设每帧可在 hop 内完成，没有目标硬件、RTF、p99、deadline miss 或 capture-to-playback 测量。

## 系统管线

~~~text
P-channel Y(t,f) RI
       |
       v
DNN1: LSTM-ResUNet -> target RI S_hat_q^(1)
       |
       +---- Y + S_hat_q^(1) -> online MCWF -> S_hat_q^MCWF
                                      |
                                      v
             DNN2 input = Y + S_hat_q^(1) + S_hat_q^MCWF
                                      |
                                      v
                         DNN2: LSTM-ResUNet
                                      |
                                      v
                       short-window iSTFT + OLA
                                      |
                                      v
                             enhanced s_hat_q
~~~

- DNN1 以多麦克风 mixture 的复数 STFT RI 分量为输入，预测参考麦克风 $q$ 的目标 RI；
- MCWF 在每个频率上在线累积空间统计，输出作为 DNN2 的附加 RI 特征；
- DNN2 同时看 $Y$、DNN1 输出和 MCWF 输出，进行 post-filter / target RI refinement；
- 两个 DNN 与 MCWF 都留在复数 T-F 域，不在中间来回 iSTFT，因此 beamforming 不增加额外的算法窗口时延。

## 关键配置

| 配置项 | PDF 证据 |
|---|---|
| 采样率 | 16 kHz |
| 默认 STFT | input window 16 ms、output window 4 ms、hop 2 ms |
| 默认 DFT | 256-point，129 维复数 STFT |
| 短输出窗 | 每帧 iDFT 后丢弃前 12 ms，只保留最后 4 ms 做 OLA |
| one-frame-ahead | DNN2 预测下一帧；algorithmic latency 从 4 ms 到 2 ms；DNN1 仍预测当前帧 |
| 远期预测 | 两帧 ahead 对应 0 ms，三帧 ahead 对应 -2 ms 的论文记账，但性能明显下降 |
| analysis windows | square-root Hann、Rect、AsqrtHann、Tukey；Tukey 两端各 1 ms taper（16 ms window） |
| DNN backbone | LSTM-ResUNet；3 层 LSTM，每层 300 units；6 个 encoder 下采样块和 6 个 decoder 上采样块 |
| residual block | 每个含 5 个 depthwise-separable 2D convolution；时间 dilation 为 1、2、4、8、16 |
| causal design | convolution/normalization 为 causal/frame-online；时间方向 kernel 为 1x3 或 1x4，residual block 为 causal 2x3 |
| 规模 | 单个 DNN 约 2.3 M 参数；表中六麦 DNN1 为 2.33 M，双 DNN 为 4.67 M |
| 计算量 | ptflops 统计处理 4 s mixture 的总 FLOPs；六麦双 DNN 4 ms 配置为 57.1 G |

## 输入、输出与目标

论文的物理模型是：

$$
\mathbf{Y}(t,f)=\mathbf{X}(t,f)+\mathbf{V}(t,f)
=\mathbf{S}(t,f)+\mathbf{H}(t,f)+\mathbf{V}(t,f),
\qquad \mathbf{Y},\mathbf{V},\mathbf{X},\mathbf{S},\mathbf{H}\in\mathbb{C}^{P}.
$$

- $\mathbf{Y}$：$P$ 个麦克风的 mixture STFT；
- $\mathbf{V}$：reverberant noise；
- $\mathbf{X}$：reverberant target speech；
- $\mathbf{S}$：目标 direct-path speech；
- $\mathbf{H}$：target 的 non-direct 部分；
- $P$：实验中的 1、2 或 6 个麦克风；
- 目标是参考麦克风 $q$ 的 $S_q$，early reflections 不计入目标。

输入输出关系可写为：

$$
\operatorname{RI}(\mathbf{Y})
\longrightarrow
\widehat S_q^{(1)}
\longrightarrow
\widehat S_q^{\mathrm{MCWF}}
\longrightarrow
\widehat S_q^{(2)}
\xrightarrow{\operatorname{iSTFT}_{\mathrm{short}}}
\widehat s_q.
$$

这里输出不是 mask，而是目标复数 STFT 的 real/imaginary components；最后的 waveform 来自短 output window 的 iSTFT 和 overlap-add。

## 关键公式与符号

### 复数谱映射损失

DNN1 输出：

$$
\widehat S_q^{(1)}
=\widehat R_q^{(1)}+j\widehat I_q^{(1)}.
$$

论文的 RI + magnitude loss：

$$
\mathcal{L}_{\mathrm{RI+Mag}}
=\left\|\widehat R_q^{(1)}-\operatorname{Real}(S_q)\right\|_1
+\left\|\widehat I_q^{(1)}-\operatorname{Imag}(S_q)\right\|_1
+\left\|\sqrt{(\widehat R_q^{(1)})^2+(\widehat I_q^{(1)})^2}-|S_q|\right\|_1.
$$

DNN2 用重合成后的 Wav+Mag loss：

$$
\widehat s_q^{(2)}=\operatorname{iSTFT}\left(\widehat S_q^{(2)}\right),
$$

$$
\mathcal{L}_{\mathrm{Wav+Mag}}
=\left\|\widehat s_q^{(2)}-s_q\right\|_1
+\left\|
\left|\operatorname{STFT}_L(\widehat s_q^{(2)})\right|
-\left|\operatorname{STFT}_L(s_q)\right|
\right\|_1.
$$

实验的 $\operatorname{STFT}_L$ 使用 square-root Hann、32 ms window 和 8 ms hop；这组 loss STFT 参数不应与输入 16 ms STFT 混为一谈。

### 在线 MCWF

给定 DNN1 的目标估计，逐频 MCWF 解：

$$
\min_{\mathbf w(f;q)}
\sum_t\left|\widehat S_q^{(1)}(t,f)
-\mathbf w(f;q)^{\mathrm H}\mathbf Y(t,f)\right|^2,
$$

$$
\widehat{\mathbf w}(f;q)
=\left(\widehat{\boldsymbol\Phi}^{(yy)}(f)\right)^{-1}
\widehat{\boldsymbol\Phi}^{(ys)}(f)\mathbf u_q,
\qquad
\widehat S_q^{\mathrm{MCWF}}(t,f)
=\widehat{\mathbf w}(f;q)^{\mathrm H}\mathbf Y(t,f).
$$

$\mathbf u_q$ 是第 $q$ 个元素为 1 的 one-hot 向量，$\mathrm H$ 为共轭转置。在线时：

$$
\widehat{\boldsymbol\Phi}^{(yy)}(t,f)
=\widehat{\boldsymbol\Phi}^{(yy)}(t-1,f)
+\mathbf Y(t,f)\mathbf Y(t,f)^{\mathrm H},
$$

$$
\widehat{\boldsymbol\Phi}^{(ys)}(t,f)
=\widehat{\boldsymbol\Phi}^{(ys)}(t-1,f)
+\mathbf Y(t,f)\widehat{\mathbf S}^{(1)}(t,f)^{\mathrm H}.
$$

两种统计在 $t=0$ 全零初始化；逆矩阵用 Woodbury 递推。论文没有采用 recursive averaging，因为假设一个 utterance 内目标和非目标源不移动。

## 低时延与因果性审计

| 维度 | 结论 |
|---|---|
| algorithmic latency | 默认双窗 4 ms；DNN2 one-frame-ahead 2 ms；论文还列出 0 ms 和 -2 ms 的预测实验 |
| look-ahead | 默认 input window 对当前要输出的尾段看前方 4 ms、后方 12 ms |
| latest readable sample | 论文没有单独给出样本索引形式的 latest readable sample；只给出 frame/window 的 4 ms look-ahead 关系 |
| frame-online | 论文明确称 convolution/normalization causal，并按帧更新 LSTM/MCWF |
| strict sample-causal | 默认配置不是 strict sample-causal；4 ms future observation 和 future-target prediction 都不能替代逐样本因果证书 |
| hardware latency | 只假设每帧可在 hop 内完成；无目标硬件测量 |
| latency ledger | algorithmic、hardware、I/O/ADC/DAC、capture-to-playback 必须分开；后 4 项未报告 |
| state/warm-up | 每个 mixture 开头补 $(iWS-HS)$ ms 零样本，MCWF 在 $t=0$ 全零；DNN state reset、warm-up、长流行为未报告 |
| RTF/deadline | 未报告 RTF、p50/p95/p99、deadline miss、underrun/overrun |
| memory/quantization | 未报告峰值 RAM/SRAM、量化精度或定点部署 |

## 代表性证据

| 场景与系统 | latency | #params (M) | FLOPs (G) | SI-SDR (dB) | PESQ | eSTOI (%) |
|---|---:|---:|---:|---:|---:|---:|
| 单麦 DNN1 Wav+Mag, Rect, 1 ahead | 2 ms | 2.32 | 27.8 | 2.5 | 1.85 | 66.6 |
| 单麦 Conv-TasNet Wav+Mag, 2/1 ms | 2 ms | 6.14 | 52.2 | 2.2 | 1.77 | 65.1 |
| 六麦 DNN1 Wav+Mag, Tukey, current | 4 ms | 2.33 | 28.3 | 6.4 | 2.26 | 77.3 |
| 六麦 DNN1+MCWF+DNN2, Tukey, current | 4 ms | 4.67 | 57.1 | 7.9 | 2.70 | 84.0 |
| 六麦 DNN1+MCWF+DNN2, Rect, 1 ahead | 2 ms | 4.67 | 57.1 | 7.1 | 2.50 | 81.0 |
| 六麦 MC-Conv-TasNet Wav+Mag, 2/1 ms | 2 ms | 6.27 | 53.2 | 5.7 | 2.29 | 77.3 |
| 双麦 DNN1+MCWF+DNN2, Rect, 1 ahead | 2 ms | 4.66 | 56.1 | 4.3 | 2.09 | 72.5 |

以上数字来自论文第 10-12 页 Tables I、III、IV；FLOPs 是 4 s mixture 统计值，不能替代端侧实时率。

## 适用范围与限制

- 适合研究“频域分辨率、复数相位、空间滤波和低算法时延”的联合 trade-off；
- 不适合直接宣称 strict-causal 端到端助听器产品，因为没有硬件 p99、I/O、ADC/DAC 和 deadline 证据；
- 训练集过滤人声事件，没有 babble/竞争说话人，因此人声保留和误抑制未被单独验证；
- 训练/测试使用相同阵列几何，MCWF 还假设每个 utterance 内声源不移动；
- 目标是 direct-path，早期反射不计入目标，指标和自然听感之间有定义差异；
- 单 DNN 约 2.3 M，双 DNN 4.66-4.67 M；模型和运行时内存对极小端侧设备仍偏重。

## 与库中页面的关系

- 论文源页：[[wiki_low_latency/sources/2022/STFT-Domain Very Low Algorithmic Latency 2022]]
- 概念页：[[wiki_low_latency/concepts/2204.09911-short-asymmetric-stft]]
- 同方向后续比较：[[wiki_low_latency/entities/GCFSnet]]、[[wiki_low_latency/sources/2023/GCFSnet 2023]]
- 时域对照：[[wiki/sources/2019/Conv-TasNet - Surpassing Ideal TF Masking 2019]]
- 低复杂度混合路线：[[wiki/sources/2020/PercepNet 2020]]、[[wiki/entities/RNNoise]]
- 阵列方法接口：[[wiki_array/concepts/波束成形 Beamforming]]
