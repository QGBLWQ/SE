---
title: FSB-LSTM
type: entity
created: 2026-09-16
updated: 2026-09-16
tags:
  - model
  - speech-enhancement
  - full-band
  - sub-band
  - lstm
  - complex-tf
  - low-latency
  - multichannel
  - hearing-aids
sources:
  - [[wiki_low_latency/sources/2023/FSB-LSTM 2023]]
related:
  - [[wiki_low_latency/concepts/2304.08707-full-sub-band-modeling]]
  - [[wiki/concepts/全带与子带模型]]
  - [[wiki/concepts/STFT与频谱图]]
  - [[wiki/sources/2021/FullSubNet 2021]]
  - [[wiki_low_latency/entities/GCFSnet]]
  - [[wiki_low_latency/index]]
---

# FSB-LSTM

## 简洁定义

FSB-LSTM（full- and sub-band LSTM）是 Wang 等人在 2023 年提出的低算法时延、低复杂度 STFT 域语音增强架构。它接收单/多麦克风复数谱的 real/imaginary（RI）分量，沿多个 residual FSB-LSTM modules 同时做 full-band 与下采样 sub-band 时间建模，输出参考麦克风目标 direct-path 的 RI 频谱，再经 iSTFT 重合成。

它与 [[wiki/sources/2021/FullSubNet 2021]] 共享“全带 + 子带”的频率分工母题，但不是幅度 mask 模型：FSB-LSTM 的目标是多通道 complex spectral mapping。

## 管线

~~~text
P 个麦克风 RI-STFT [2P, T, F]
  → Conv2D (时间 kernel=1、频率 kernel=3)
  → D 维 T-F embedding
  → B × (full-band block → sub-band block)
       每个 block: 频率下采样 → LSTM → 频率上采样 → residual add
  → Deconv2D
  → 参考麦克风 S_q 的 RI 频谱
  → iSTFT → s_hat_q
~~~

## 输入、输出与关键公式

论文将多麦克风混合和 STFT 写为：

$$
y[n]=s[n]+v[n],\qquad y[n],s[n],v[n]\in\mathbb{R}^{P},
$$

$$
Y(t,f)=S(t,f)+V(t,f)\in\mathbb{C}^{P}.
$$

模型输入是所有 P 个麦克风的 RI 堆叠，形状 2P × T × F；输出是参考通道 q 的目标 S_q RI 分量。full-band block 对频率下采样长度使用：

$$
Q=\left\lceil\frac{F-I}{J}\right\rceil J+I,\qquad
A=E\left(\frac{Q-I}{J}+1\right),
$$

其中 E 是 full-band 输出通道，I 是频率 kernel，J 是频率 stride，A 是 flatten 后的 frame embedding 维数。sub-band block 对应：

$$
Q'=\left\lceil\frac{F-I'}{J'}\right\rceil J'+I',
$$

并把 ((Q'-I')/J' + 1) 条频率序列分别沿 T 送入共享的 H'-unit LSTM。论文明确给出的 Wav+Mag loss 名称没有在目标 PDF 中展开，不能在实体页补写外部公式。

## 关键配置与规模

| 项目 | 论文配置/证据 |
|---|---|
| 采样率与谱 | 16 kHz；256-point DFT；129-dimensional complex spectra |
| STFT/iSTFT | iWS=16 ms；HS=2 ms；oWS=4 ms；论文算法延迟口径 4 ms |
| modules | B=3；每个含一个 full-band block 和一个 sub-band block |
| embedding | D=32 |
| full-band | E=8，I=8，J=4，H=256 |
| sub-band | E'=64，I'=5，J'=5，H'=64；默认 26 个 sub-bands |
| 模型量 | 1.96M 参数；表中 GMAC/s 为 3.37（6ch）、3.31（2ch）、3.30（1ch） |
| 运行时缓存 | 论文报告 FSB-LSTM 为 46.2 KB（单精度 streaming buffer 口径） |
| 低时延控制 | FB-LSTM 对照在 HS=1 ms、oWS=2 ms 时为 4.65 GMAC/s；这不是 FSB-LSTM 的 2 ms 结果 |

## 证据与边界

- 时间轴卷积 kernel size 为 1，且使用 unidirectional/causal LSTM；论文说运行时只需缓存过去帧的 hidden/cell states，支持 paper-level streaming/causal 解释。
- 4 ms 是默认 iWS/HS/oWS 机制下的 algorithmic latency，不是测得的端到端 capture-to-playback latency。
- 论文没有报告目标硬件上的 RTF、wall-clock、deadline miss、p99、能耗、真实助听器链路或训练 optimizer/lr/batch/epoch。
- 6ch/2ch/1ch 的 SI-SDR、PESQ、eSTOI 均优于对应 FB-LSTM 控制，但没有 ASR WER、false-suppression 或专门的人声保留指标。

## 关联页面

- 详细 PDF 摄取：[[wiki_low_latency/sources/2023/FSB-LSTM 2023]]
- 本论文方法概念页：[[wiki_low_latency/concepts/2304.08707-full-sub-band-modeling]]
- 全带/子带母题：[[wiki/concepts/全带与子带模型]]
- STFT 输入域：[[wiki/concepts/STFT与频谱图]]
- 同方向低时延多通道对照：[[wiki_low_latency/entities/GCFSnet]]、[[wiki_low_latency/sources/2023/GCFSnet 2023]]
- 目录位置：[[wiki_low_latency/index]]

