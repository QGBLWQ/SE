---
title: RT-SEMamba
type: entity
created: 2026-09-16
updated: 2026-09-20
tags:
  - speech-enhancement
  - mamba
  - state-space-model
  - strict-causal
  - real-time
  - streaming
  - knowledge-distillation
  - complex-stft
sources:
  - [[wiki_low_latency/sources/2026/RT-SEMamba 2026]]
related:
  - [[wiki_low_latency/concepts/2608.12099-mamba-distillation]]
  - [[wiki_array/concepts/Mamba SSM 状态空间模型]]
  - [[wiki_low_latency/concepts/2409.10358-ultra-low-latency-benchmark]]
  - [[wiki/sources/2024/Mamba for SE 2024]]
  - [[wiki_low_latency/sources/2023/FSB-LSTM 2023]]
  - [[wiki_low_latency/sources/2023/GCFSnet 2023]]
---

# RT-SEMamba

## 定义

**RT-SEMamba** 是本地论文 2608.12099 提出的实时单通道语音增强模型。它在复数 STFT 域使用 causal time-frequency Mamba (cTF-Mamba)，沿时间逐帧传播固定大小的 SSM state，并用 8-layer teacher 对 1/2-layer student 做 progressive knowledge distillation。论文报告的是 16 kHz、25 ms algorithmic latency、VCTK-DEMAND；这不是本 Wiki 约 2 ms 目标的已验证系统。

## 证据

| 属性 | 本地 PDF 证据 |
|---|---|
| 任务 | 单通道 noisy speech enhancement；VCTK-DEMAND，p.1、p.3 |
| 输入/输出 | $X(f,\tau)=M(f,\tau)e^{jP(f,\tau)}$；输入 $M,P$，输出 $\widehat M,\widehat P,\widehat C$，再 causal iSTFT，Eq. (2)-(4)，p.2 |
| 架构 | causal dense encoder → Time-Mamba → current-frame Frequency-Mamba → transposed convolution/MLP，重复 cTF-Mamba blocks → causal magnitude/phase decoders → complex/iSTFT，Figure 1，p.2 |
| 因果性 | center=False；时间卷积左侧 $K-1$ padding；Time-Mamba 无 lookahead；Frequency-Mamba 仅当前 frame 内双向，p.2 |
| streaming state | temporal frame buffer、depth-wise conv state buffer、SSM hidden state；1-frame-in/1-frame-out，p.2 |
| KD | magnitude/phase/complex output KD + averaged normalized intermediate feature KD + 10% step ramp-up，Eq. (5)-(12)，p.2-3 |
| 8-layer teacher | 2.74M、47.35 G MAC/s、RTF 0.29；PESQ/CSIG/CBAK/COVL/STOI = 3.32/4.64/3.72/4.08/0.95，p.2-4 |
| 8→1 student | 1.05M、25 ms、RTF 0.11；PESQ/CSIG/CBAK/COVL/STOI = 3.18/4.43/3.68/3.89/0.95，p.3-4 |

## 架构与状态

~~~text
noisy waveform
  → causal STFT (16 kHz, W=400, H=100, center=False)
  → magnitude/phase causal dense encoder
  → time-unidirectional Time-Mamba
  → bidirectional Frequency-Mamba within current frame
  → transposed convolution + MLP, repeated N times
  → causal magnitude/phase decoders
  → complex reconstruction → causal iSTFT → enhanced waveform
~~~

论文给出的基础 SSM 递归是：

$$
\mathbf h_n=\overline{\mathbf A}\mathbf h_{n-1}
+\overline{\mathbf B}\mathbf x_n,\qquad
\mathbf y_n=\mathbf C\mathbf h_n.
$$

$\mathbf h_n$ 是固定大小 recurrent state，$\overline{\mathbf A},\overline{\mathbf B}$ 是离散状态转移矩阵，$\mathbf C$ 是输出投影。固定状态不代表零缓存：论文还要求保存过去 $K-1$ 个 feature frames 和 depth-wise conv 最近 $d_{conv}-1$ 个时间步。

## 低时延账本

| 字段 | RT-SEMamba 证据/边界 |
|---|---|
| 采样率、窗、hop | 16 kHz；$W=400$ samples = 25 ms；$H=100$ samples = 6.25 ms；analysis/synthesis center=False |
| 算法延迟 | 论文口径为 one-window bounded algorithmic latency = 25 ms；未单独报告 group delay |
| 时间因果 | frames $t=1,\ldots,T$ sequentially processed without lookahead；时间卷积右侧不 padding |
| 频率因果 | 当前 frame 内 bidirectional；没有未来 time frame，但不是 all-axis unidirectional |
| 起始与状态 | 缺失 past context 用零填充；warm-up 帧数、state reset、长流稳定性未报告 |
| 运行时 | Table 1 RTF 0.11-0.29，single NVIDIA RTX 5090 GPU，after warm-up |
| 端到端与 deadline | p50/p95/p99、per-hop wall-clock、deadline miss、ADC/DMA、I/O、DAC、underrun/overrun 均未报告 |
| 部署资源 | CPU/SoC、峰值 RAM/SRAM、量化/fixed-point、能耗、编译器均未报告 |

实体判定：**paper-level strict temporal causal / 25 ms algorithmic latency / GPU steady-state RTF only**。不能简化为 2 ms causal SE。

> [!updated] 2026-09-20：判定口径被更严标准挑战
> [[wiki_low_latency/sources/2026/LaCo-SENet 2026]]（arXiv:2606.19688）Table 1 脚注 † 主张「**只要 encoder 存在非因果对称 padding，算法延迟就不可确定，即便模型自称 unidirectional**」，并据此把 SEMamba 排除出因果排名——而本实体正是 SEMamba 的因果化改造。
> 本实体的 `paper-claimed-causal` 判定**保持不变**，但 25 ms **不得**与给出逐层 padding 式的模型（LaCo-SENet 的 Eq. (1)(2)(5)）放在同一可信度层级比较。待代码级逐层 padding/state 审计后才能决定是否升级为 `strict_causal`。详见 source 页「因果性判定口径」小节。

## 结果与证据边界

- 支持：在该 VCTK-DEMAND 协议上，8-layer 质量最高；KD 提高 1/2-layer 质量且不增加 student RTF；时间维可以在线逐帧处理。
- 不支持：约 2 ms 已达成、端侧 deadline 已通过、端到端 capture-to-playback 已测、低 SNR 人声保留/false-suppression 已证明。
- 未报告：完整 $\mathcal L_{task}$ 展开式、epochs/batch/optimizer/lr/seed、component-level KD removal、真实设备、量化、峰值内存和能耗。

## 交叉链接

- 源论文：[[wiki_low_latency/sources/2026/RT-SEMamba 2026]]
- 蒸馏概念：[[wiki_low_latency/concepts/2608.12099-mamba-distillation]]
- Mamba/SSM：[[wiki_array/concepts/Mamba SSM 状态空间模型]]
- 延迟审计：[[wiki_low_latency/concepts/2409.10358-ultra-low-latency-benchmark]]
- Mamba 语音增强前身：[[wiki/sources/2024/Mamba for SE 2024]]
- 低时延对照：[[wiki_low_latency/sources/2023/FSB-LSTM 2023]]、[[wiki_low_latency/sources/2023/GCFSnet 2023]]

