---
title: On-TasNet - 低时延单说话人语音增强配置
type: entity
created: 2026-09-16
updated: 2026-09-16
tags:
  - speech-enhancement
  - single-speaker
  - waveform-domain
  - tasnet
  - causal
  - low-latency
  - noise-suppression
  - speech-preservation
sources:
  - "[[wiki_low_latency/sources/2021/On TasNet Low-Latency SE 2021]]"
related:
  - "[[wiki_low_latency/concepts/2103.14882-causal-tasnet]]"
  - "[[wiki/entities/Conv-TasNet]]"
  - "[[wiki/sources/2019/Conv-TasNet 2019]]"
  - "[[wiki/sources/2020/Real Time SE Waveform 2020]]"
  - "[[wiki/entities/RNNoise]]"
  - "[[wiki_low_latency/entities/GCFSnet]]"
  - "[[wiki_low_latency/index]]"
---

# On-TasNet

## 简洁定义

On-TasNet 是 2103.14882 对 TasNet 在**单通道、单说话人加性噪声增强**中的低时延配置与行为审计。它沿用 learned encoder - TCN separator - learned decoder，不是另一个带新模块的网络命名；本页把它作为“causal learned-waveform 增强基线”记录。

论文还用 I=2 的两说话人分离实验验证实现。低时延配置由 cLN 与 causal convolution 组成，论文称其为 essentially causal；在本 Wiki 中暂记为 paper_claimed_causal，不等同于已完成的 strict_causal 证明。

## 任务、输入与输出

论文的混合模型为：

$$
y=\sum_{i=1}^{I}x_i+v,\qquad
\hat{x}_i=f_{\mathrm{DNN}}(y,\theta).
$$

- x_i：单麦克风混合中的第 i 个干净目标语音；
- v：加性噪声；
- y：单麦克风带噪时域波形；
- I=1：单说话人语音增强，输出增强目标波形；
- I=2：两说话人分离验证，输出两个估计波形。

TasNet 的流程是：

~~~text
noisy waveform
  → learned 1-D convolution encoder
  → inner-domain representation
  → TCN separator 的逐点 scalar weights
  → learned transposed-convolution decoder
  → enhanced waveform
~~~

对 encoder / separator / decoder 的符号化关系可写为：

$$
\mathbf{w}_t=E\!\left(y_{t:t+L_e-1}\right),\qquad
\mathbf{d}_{i,t}=\mathbf{w}_t\odot\mathbf{m}_{i,t},\qquad
\hat{x}_i=D\!\left(\{\mathbf{d}_{i,t}\}_t\right).
$$

后一个式组是依据论文 Figure 1 与 Section 2.1 做的流程整理，不是论文中编号的完整 encoder/decoder 方程。

## 关键配置与结构

| 项目 | PDF 证据 |
|---|---|
| 采样率 | 8 kHz |
| TasNet configuration | L16, K8, N512, X8, R3, B128, H512, P3 |
| 参数量 | 3.5 million |
| TasNet receptive field | Section 2.1 写 15,310 samples；Table 1 写 1.53 s，原 PDF 两处不一致 |
| 归一化/卷积变体 | non-causal + gLN；non-causal + cLN；causal + cLN |
| 短窗/短 hop 对照 | 2/1 ms、64/32 ms、64/1 ms |
| uNet baseline | 3.5 million parameters、11-sample filter、2,561-sample receptive field、parameterized ReLU、encoder 每三层 dropout |

K=8 由论文配置字符串直接列出，但本文没有重新定义其含义；复现时应以论文引用的 TasNet 实现 [6]/[20] 为准，不在本页臆测。

## 低时延与因果性证据

| 级别 | 证据 | 当前判定 |
|---|---|---|
| gLN + non-causal convolution | gLN 使用整个 signal；卷积需要 future context | non_causal |
| cLN + non-causal convolution | look-ahead 依赖 kernel lengths，形成 fixed system latency | non_causal / low_look_ahead |
| cLN + causal convolution | 论文称 essentially causal；latency 由 frame hop 决定，多数实验为 1 ms | paper_claimed_causal |

论文没有报告 MAC/s、FLOPs、CPU/GPU runtime、RTF、batch=1 p50/p95/p99、输入输出 buffer、ADC/DAC、capture-to-playback、deadline miss、warm-up、state reset、underrun/overrun 或恢复策略。因此参数量和 frame hop 不能单独证明端侧实时 deadline。

## 质量与噪声抑制证据

论文使用 WSJ0，8 kHz、4 s 信号；增强噪声包括 stationary speech-shaped noise（ssn）、竞争女性说话人（wsjf）和由 ssn、6-speaker babble、street、cafeteria、bus、pedestrian 串接的 mix。训练 SNR 为 [-10,10] dB 的均匀采样，测试固定 0 dB。

Table 1 中最强的非因果 wsjf 行为 cLN + non-causal convolution：STOI 0.97、PESQ 3.33、SI-SDR 16.0 dB；同测试条件下 causal cLN 为 0.95、2.74、12.4。这个结果说明竞争说话人对 future context 较敏感，但不是目标人声保留率的直接测量。

人声保留的直接证据仍缺失：没有 false-suppression、DNSMOS SIG/BAK/OVL、ASR WER、F0/formant/prosody continuity、voiced-energy retention 或听者测试。inner-domain overlap 的机制分析与结果表详见 [[wiki_low_latency/sources/2021/On TasNet Low-Latency SE 2021]]。

## 关键消融

Table 2 的 decisive 对照是 hop：

| 条件 | 2bal processed STOI / PESQ / SI-SDR | ssn processed STOI / PESQ / SI-SDR |
|---|---|---|
| 2 ms / 1 ms | 0.93 / 2.66 / 12.4 | 0.93 / 2.60 / 11.4 |
| 64 ms / 32 ms | 0.79 / 1.71 / 4.8 | 0.87 / 2.07 / 8.2 |
| 64 ms / 1 ms | 0.93 / 2.78 / 12.5 | 0.93 / 2.60 / 11.0 |

作者据此认为 hop 比 window length 更关键，并 conjecture 较大 hop 让 row-wise inner-domain convolution 产生更强 aliasing。该机制解释尚没有 anti-aliasing 或 cross-row 的直接消融。

## 相关页面

- 论文证据页：[[wiki_low_latency/sources/2021/On TasNet Low-Latency SE 2021]]
- 概念页：[[wiki_low_latency/concepts/2103.14882-causal-tasnet]]
- 原始架构实体：[[wiki/entities/Conv-TasNet]]
- 可学习编码器：[[wiki/concepts/可学习编码器 Learnable Encoder]]
- TCN：[[wiki/concepts/时序卷积网络 TCN]]
- 低复杂度实时参照：[[wiki/entities/RNNoise]]
- 同一低时延 Wiki：[[wiki_low_latency/index]]
