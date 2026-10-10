---
title: LaCo-SENet
type: entity
created: 2026-09-20
updated: 2026-09-20
tags:
  - speech-enhancement
  - single-channel
  - streaming
  - causal-convolution
  - asymmetric-padding
  - configurable-latency
  - strict-causal
  - paper-claimed-causal
  - 12.5ms-algorithmic-latency
  - onnx-runtime
sources:
  - [[wiki_low_latency/sources/2026/LaCo-SENet 2026]]
related:
  - [[wiki_low_latency/concepts/2606.19688-latency-configurable-asymmetric-padding]]
  - [[wiki_low_latency/concepts/2204.09911-short-asymmetric-stft]]
  - [[wiki_low_latency/concepts/严格因果与算法延迟]]
  - [[wiki_low_latency/concepts/低时延前端与延迟账本]]
  - [[wiki_low_latency/entities/DeepFilterNet2]]
  - [[wiki_low_latency/entities/RT-SEMamba]]
  - [[wiki_low_latency/entities/On-TasNet]]
---

# LaCo-SENet

## 定义

**LaCo-SENet**（Latency-Configurable SE Network）是本地论文 2606.19688 提出的单通道流式语音增强模型。它在 [[wiki_low_latency/entities/PrimeK-Net|PrimeK-Net]] [3] 骨干上把「未来上下文」参数化为一个训练期超参数——padding ratio $r=(r_L,r_R)$——从而用**恒定 1.37M 参数**扫出 12.5–200.0 ms 共 9 个离散时延点。为了让逐层非对称 padding 在 chunk-based streaming 下成立，它引入 **dual-buffer streaming**（state buffer 存过去 + lookahead buffer 在输入级与特征级提供未来）与 **selective state update (SSU)**（只把当前 chunk 帧写入 state），并声称 chunk-wise 输出与 full-sequence 输出**数值完全一致**。

论文口径：16 kHz、VoiceBank+DEMAND、最低算法时延 **12.5 ms**（其中 $W/2=12.5$ ms 是 STFT center delay 下界，不可由 $r$ 消除）。这不是本 Wiki 约 2 ms 目标的已验证系统。

## 证据

| 属性 | 本地 PDF 证据 |
|---|---|
| 任务 | 单通道 streaming speech enhancement；VoiceBank+DEMAND @16 kHz，11,572 训练 / 824 测试语句，10 类噪声 × 四档 SNR，p.3 §4.1 |
| 输入 | $X\in\mathbb R^{2\times T\times F}$，两通道 = power-law 压缩幅度（$c=0.3$）+ 相位；STFT win/hop/fft = 400/100/400 samples，p.3 §3.3、§3.3.4 |
| 输出 | magnitude mask $\hat M\in\mathbb R^{T\times F}$ 与 enhanced phase $\hat\Phi\in\mathbb R^{T\times F}$，经 masking + phase replacement 重建谱 → iSTFT + OLA，Eq. (6)，p.3 |
| 骨干 | [[wiki_low_latency/entities/PrimeK-Net\|PrimeK-Net]] [3]：encoder $\mathcal E_\theta$ + TS Blocks $\mathcal T_\theta$ + 并行 mask/phase 双 decoder $\mathcal D^M_\theta,\mathcal D^\Phi_\theta$，Eq. (6)，p.3 §3.3 |
| 通道/核配置 | $C_h=64$、DSDDB depth 4、4 个 TS Block（2 time + 2 freq）、time kernels [3,5,7,11]、freq kernels [3,11,23,31]、SCA kernel 11，p.3 §3.3.4 |
| DSDDB | 4 个 depthwise separable conv，dilation (1,2,4,8)，dense connection（每层输入为前面所有层输出的拼接），depthwise 用 `AsymmetricConv2d`，p.3 §3.3.1 |
| TS Block | time branch 重排为 $\mathbb R^{(NF')\times C_h\times T}$，CAB + GPKFFN，**全因果**；freq branch 重排为 $\mathbb R^{(NT)\times C_h\times F'}$，同模块**非因果**（频率轴无时间序），p.3 §3.3.2 |
| 流式改造 | ① InstanceNorm → BatchNorm（chunk-size invariant）；② SCA 的 AdaptiveAvgPool1d → CausalConv1d（depthwise, $K_{\text{sca}}=11$），p.3 §3.3.3 |
| 因果性 | 逐层 padding 分配 Eq. (1)、state 更新 Eq. (4)、选择算子 Eq. (5)；Figure 1(a) 方框标注 "Time Stage (Causal)" / "Freq Stage (Non-Causal)"；$L_{\text{enc}}=L_{\text{dec}}=0$ 时称 fully causal，p.2–3 |
| 时延族 | 9 个配置，$\tau=12.5\text{–}200.0$ ms，$L_{\text{enc}}=L_{\text{dec}}\in\{0,\dots,5\}$ 六个 + 100.0/150.0 ms 两个中间点 + $r_R=0.5$ 对称参考；$\tau=1000((L_{\text{enc}}+L_{\text{dec}})h+W/2)/f_s$，Eq. (3)，p.4 §4.1 |
| 损失 | $\mathcal L=0.9\mathcal L_{\text{mag}}+0.3\mathcal L_{\text{pha}}+0.1\mathcal L_{\text{com}}+0.05\mathcal L_{\text{con}}+0.05\mathcal L_{\text{gan}}$（自称沿用 [[wiki_low_latency/entities/PrimeK-Net\|PrimeK-Net]] [3]，但**其原文未给任何 $\lambda$ 数值** ⇒ 引用链断点，见 source 页 §3.5 的 `[!contradiction]`），p.4 §4.1 |
| 训练 | AdamW，lr $5\times10^{-4}$，$(\beta_1,\beta_2)=(0.8,0.99)$，exp LR decay，batch 8，400K steps，**每配置独立训练**，3 seeds，按 validation PESQ 选点，p.4 §4.1 |
| 最优因果点 | 12.5 ms、1.37M，PESQ 3.35±.02 / STOI .952 / CSIG 4.61 / CBAK 3.71 / COVL 4.05，Table 1，p.3 |
| 运行时 | ONNX Runtime，Intel Xeon Silver 4510 单线程，端到端 steady-state（STFT+model+iSTFT）：RTF 4.59@$C=1$ → 0.30@$C=64$（$L_{\text{tot}}=0$）；RTF<1 需 $C\ge 7\text{–}12$；$C=8$ 因果配置 62.5 ms、RTF 0.77，p.4 §4.2，Figure 3 |

## 架构与状态

~~~text
noisy waveform x[t]
  → STFT (16 kHz, win/hop/fft = 400/100/400), power-law compress c=0.3
  → X ∈ R^{2×T×F}  (compressed magnitude + phase)
  → Eθ : projection to Ch=64 → DSDDB (dilations 1,2,4,8) → freq downsample (stride 1,2)
  → Tθ : 4 × TS Block (2 time + 2 freq)
  │        time branch  : reshape (N·F')×Ch×T  → CAB + GPKFFN   [causal]
  │        freq branch  : reshape (N·T )×Ch×F' → CAB + GPKFFN   [non-causal on freq]
  → DθM (mask)  ┐ parallel
  → DθΦ (phase) ┘ each: DSDDB → transposed conv (restore F)
  → masking + phase replacement → iSTFT + OLA (with OLA tail buffer)
  → enhanced waveform

streaming wrappers
  ├─ state buffer s_k^(ℓ)   : last P_L^(ℓ) frames  (Eq. 4)
  ├─ lookahead buffer        : encoder input extended to C+L_enc ; feature buffer ≥ C+L_dec
  └─ SSU  Π_C(x)=x_{1:C}     : state records current-chunk frames only (Eq. 5)
~~~

Figure 1(a) 中可辨认的模块顺序为：Input Buffer → STFT Context Buffer → Chunk n Audio Samples → Encoder Block → State Buffer (Encoder) → TS Block (Time Stage, Causal) / Freq Stage (Non-Causal) → State Buffer (Time Stage) → Feature Buffer (Wait for Decoder Lookahead) → Mask Decoder Block / Phase Decoder Block → State Buffer (Decoder) → Exit to Magnitude/Phase → Exit to STFT & OLA → OLA Tail Buffer (Tail of Chunk n-1) → Output & Buffer Advance。

## 低时延账本

| 字段 | LaCo-SENet 证据/边界 |
|---|---|
| 采样率、窗、hop | 16 kHz；$W=400$ samples = 25.0 ms；$h=100$ samples = 6.25 ms；fft = 400 |
| 算法时延公式 | $\tau_{\text{ms}}=1000\cdot((L_{\text{enc}}+L_{\text{dec}})\cdot h+W/2)/f_s$，Eq. (3)；$W/2=200$ samples $=12.5$ ms 为**不可消除下界** |
| 时延阶梯 | $\tau=12.5+6.25\,L_{\text{tot}}$ ms；$L_{\text{tot}}\in\{0,2,4,6,8,10,14,22,30\}$（后三项论文只给 100.0/150.0/200.0 ms 三个 τ 值） |
| 时间轴因果 | $r_R=0$ 时 `strict_causal`；$r_R>0$ 时 `low_look_ahead`，上界 $L_{\text{enc}}$/$L_{\text{dec}}$ 帧（Eq. 2） |
| 频率轴 | freq branch 非因果，但只访问**当前帧**的整个频率轴 → 时间维度仍 `strict_causal` |
| 归一化 / SCA | BatchNorm（固定 running stats）+ CausalConv1d SCA → 无未来样本依赖 |
| 起始与状态 | state buffer 首 chunk 冷启动方式、warm-up 帧数、state reset、长流漂移、丢帧/抖动策略**未报告** |
| 运行时 | Xeon Silver 4510 单线程 ONNX Runtime；RTF 4.59@$C=1$、0.30@$C=64$（$L_{\text{tot}}=0$）；RTF<1 需 $C\ge7\text{–}12$ |
| 端到端与 deadline | 只到「algorithmic + chunk buffering」（$C=8$ 因果配置 62.5 ms）；p50/p95/p99、per-hop wall-clock、deadline miss、ADC/DMA、I/O buffer、DAC/playout、underrun/overrun、capture-to-playback 均**未报告** |
| 部署资源 | 目标 SoC、峰值 RAM/SRAM、量化/定点、功耗、编译器/算子差异均**未报告** |

实体判定：**paper-claimed strict temporal causal（有逐层 padding 分配式与状态选择算子支撑，因果证据链为本库最完整）/ 12.5 ms 算法时延（含 12.5 ms STFT center delay 下界）/ 单线程 Xeon 吞吐证据，非端侧 deadline 证据**。

> [!warning] 「12.5 ms」与「实时」不是同一个工作点
> $C=1$ 才能保住 12.5 ms 算法时延，但其单线程 RTF 为 4.59。RTF<1 需 $C\ge7\text{–}12$，chunk 缓冲本身贡献 $6.25\times C$ ms，总时延升至约 56–88 ms（本页按 Eq. (3) 推导；论文只显式给出 $C=8$ 因果配置的 62.5 ms）。跨论文比较时必须说明用的是哪个 $C$。

## 结果与证据边界

- **支持**：在同一 1.37M 参数预算下，12.5→200.0 ms 的 PESQ 单调上升（3.35→3.47）；12.5 ms 全因果点超过所有时延可验证的因果基线（aTENNuate 3.27@46.5 ms、DFNet3 3.17@40 ms、GaGNet 2.94@~10 ms、RNNoise 2.33@10 ms）；SSU 在 $L_{\text{tot}}>0$ 时是必需的（去掉后 PESQ 跌破 noisy 1.97，且随 lookahead 单调恶化）；论文声称分块推理与全序列推理数值等价。
- **不支持**：约 2 ms 级系统已达成；目标端侧 deadline 已通过；端到端 capture-to-playback 已测；低 SNR / 竞争说话人 / 瞬态噪声下的人声保留已证明；运行时动态切换时延（$r$ 是固定的训练期超参数）；跨设备/跨编译器的可移植性。
- **未报告**：目标 SoC p99、RAM/SRAM、量化、功耗、ASR WER、DNSMOS、false-suppression、F0/formant/prosody continuity、SPP/VAD 校准、训练 wall-clock、数据增强、验证集划分、loss 各分项定义、DSDDB 中 kernel 与 dilation 的确切配对。
- **可比性提醒**：Table 1 中 GaGNet/RNNoise 的 $\tau$ 是「from original papers or estimated as (window−hop)/$f_s$」，与本文 Eq. (3) 口径不同；PrimeK-Net 是非因果上界（**已于 2026-09-27 补摄，见 [[wiki_low_latency/entities/PrimeK-Net]]**，3.61/1.41M 逐项对齐；但其算力只有 **44.64 G FLOPs** 一种口径 ⇒ 该行只能用于质量上界，**不能用于效率对比**）；SEMamba/xLSTM-SENet 因 encoder 非因果对称 padding 被排除出因果排名。

## 交叉链接

- 源论文：[[wiki_low_latency/sources/2026/LaCo-SENet 2026]]
- 概念展开：[[wiki_low_latency/concepts/2606.19688-latency-configurable-asymmetric-padding]]
- 非对称前端对照：[[wiki_low_latency/concepts/2204.09911-short-asymmetric-stft]]、[[wiki_low_latency/entities/STFT-Very-Low-Latency-SE]]
- 延迟审计口径：[[wiki_low_latency/concepts/严格因果与算法延迟]]、[[wiki_low_latency/concepts/低时延前端与延迟账本]]
- lookahead 只从输入级进入的对照：[[wiki_low_latency/entities/DeepFilterNet2]]、[[wiki_low_latency/sources/2022/DeepFilterNet2 2022]]
- 同为时延-Pareto 参照：[[wiki_low_latency/sources/2024/Ultra-Low Latency Speech Enhancement Comprehensive Study 2024]]、[[wiki_low_latency/entities/CRUSE-Latency-Study]]
- 因果时域对照：[[wiki_low_latency/entities/On-TasNet]]、[[wiki_low_latency/sources/2021/On TasNet Low-Latency SE 2021]]
- SSM 路线对照：[[wiki_low_latency/entities/RT-SEMamba]]、[[wiki_low_latency/entities/SlowFast-SSM]]
- 人声保留缺口：[[wiki_low_latency/concepts/低 SNR 人声保留评估]]

> [!question] 待验证
> 「chunk-wise 与 full-sequence 输出数值完全一致」是论文的断言（p.4 §4.3），本库未做代码级复现；同时 Table 1（full-sequence, 3.35）与 Table 2（streaming $C=1$, 3.39）在同一配置上存在 +0.04 的 PESQ 差异，疑与 Table 2 的 tail-30-frame 截尾评分协议有关，论文未对齐说明。
