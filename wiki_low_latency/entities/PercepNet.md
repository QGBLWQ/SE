---
title: PercepNet
type: entity
created: 2026-09-16
updated: 2026-09-16
tags:
  - speech-enhancement
  - fullband
  - perceptual-modeling
  - pitch-filtering
  - low-complexity
  - non-causal
sources:
  - [[wiki_low_latency/sources/2020/PercepNet Low-Latency Direction 2020]]
local_pdf: raw/papers/low_latency_causal_se/2008.04259.pdf
related:
  - [[wiki/sources/2018/RNNoise 2018]]
  - [[wiki/sources/2020/PercepNet 2020]]
  - [[wiki_low_latency/concepts/2008.04259-perceptual-speech-preservation]]
  - [[wiki/concepts/Pitch滤波器]]
  - [[wiki/concepts/感知加权损失函数]]
  - [[wiki_low_latency/sources/2023/FSB-LSTM 2023]]
  - [[wiki_low_latency/sources/2023/GCFSnet 2023]]
---

# PercepNet

## 定义

PercepNet 是 Valin 等人在 2020 年提出的全带语音增强模型。它不直接为每个 STFT bin 预测大规模 mask，而是用 34 个 ERB 感知频带描述谱包络，用 pitch comb filter 恢复周期性，再由轻量 DNN 预测每个 band 的 gain 与 pitch-filter strength，最后经过 envelope postfilter 和 iSTFT 输出增强语音。

它的工程目标是 48 kHz、低 CPU 复杂度的实时增强；按本库严格低时延标准，整体应标为 non_causal，因为 PDF 明示 40 ms look-ahead，且 comb filter 使用含非因果 taps 的 $C_M(z)$。

## 论文内证据

- **PDF 第 1 页**：Figure 1 显示为了生成截至 $t=0$ 的输出，需要读取至 $t=40$ ms；Figure 2 给出 STFT → pitch analysis/filtering → DNN → envelope postfilter → iSTFT 管线。
- **PDF 第 2 页**：34 个 ERB bands、band gain Eq. (2)、多周期 comb filter Eq. (3)-(4)、pitch response Figure 3，以及 coherence/strength Eq. (5)-(10)。
- **PDF 第 3 页**：Figure 4 显示 70 维输入、FC/Conv/GRU 主干与 34 gain/34 strength 输出；Eq. (11)-(12) 为 perceptual loss。
- **PDF 第 4 页**：envelope postfilter Eq. (13)-(16)、VCTK 与 DNS challenge 的 Table 1/2、8M weights/800 MMACS、5.2% 与 4.1% mobile x86 CPU 结果。

## 输入、输出与架构

| 项目 | PercepNet |
|---|---|
| 输入 | noisy waveform $y(n)$；20 ms Vorbis-window STFT，50% overlap，10 ms frame |
| 感知表示 | 34 ERB bands，0-20 kHz，最小 band width 100 Hz |
| DNN 输入 | 68 个 band/pitch-coherence 特征 + pitch period + pitch correlation，共 70 维 |
| DNN 输出 | 34 个 $\hat g_b$ 与 34 个 $\hat r_b$ |
| DSP 后端 | pitch filtering → gain/warped envelope postfilter → minimum decay → high-pass → iSTFT |
| 主要量化 | 权重限制在 $\pm1/2$，8-bit integers |
| 主干配置 | Figure 4 可读为 FC(128) → Conv(1×5,512) → Conv(1×3,512)，增益支路 4×GRU(512)，strength 支路 GRU(128)，各接 FC(34) |

## 结果与复杂度

- VCTK 48 kHz 内测：完整 PercepNet 的 P.808 MOS 为 **4.05**，PESQ-WB 为 **2.54**；RNNoise 为 3.70 / 2.29。
- 关键消融：no pitch/no postfilter 的 MOS 为 3.81；no pf 为 3.91；no pitch 为 3.93；完整 PercepNet 为 4.05。PESQ-WB 对 postfilter 的排序不一致。
- DNS challenge：PercepNet 的 synthetic w/o reverb、synthetic w/ reverb、real record、overall MOS 分别为 **3.92、3.16、3.51、3.52**。
- 复杂度：约 8M weights，10 ms frame 约 800 MMACS；1.8 GHz Intel i7-8565U 上一个 mobile x86 core 占用 5.2%，40 ms 处理四个内部帧时为 4.1%。

## 低时延判定

| 字段 | 证据/判定 |
|---|---|
| causal label | non_causal |
| look-ahead | 40 ms；DNN $M=3$ future frames；band magnitude 使用 $Y_b(\ell+M)$，pitch coherence 特征记为 $q_{y,b}(\ell)$，但其估计使用 full look-ahead |
| comb filter | $k=-M,\ldots,M$；包含 acausal taps，按允许 look-ahead 截断 |
| strict-causal certificate | 未提供 |
| RTF | 未报告；仅有 CPU 百分比 |
| p99/deadline/capture-to-playback | 未报告 |

> [!note] 符号复用
> 论文的 $M$ 在 Eq. (4) 与 DNN 小节中语义不同：前者为 pitch comb filter 两侧的 period 数（$M=5$），后者为 DNN 时间对齐使用的未来帧数（$M=3$）。

## 交叉链接

- 方法前身：[[wiki/sources/2018/RNNoise 2018]]
- 感知保真概念：[[wiki_low_latency/concepts/2008.04259-perceptual-speech-preservation]]
- pitch 相关概念：[[wiki/concepts/Pitch滤波器]]
- 感知 loss：[[wiki/concepts/感知加权损失函数]]
- 低时延对照：[[wiki_low_latency/sources/2023/FSB-LSTM 2023]]、[[wiki_low_latency/sources/2023/GCFSnet 2023]]
- 同文普通域条目：[[wiki/sources/2020/PercepNet 2020]]

> [!warning] 证据边界
> 本实体页的数值和架构均来自 `raw/papers/low_latency_causal_se/2008.04259.pdf` 第 1-4 页的视觉核对。4.1% CPU 只能说明论文测试机上的吞吐结果，不能替代目标硬件上的 RTF、p99 deadline 或端到端时延。
