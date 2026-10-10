---
title: DeepFilterNet2
type: entity
created: 2026-09-16
updated: 2026-09-16
tags:
  - model
  - deep-filtering
  - full-band
  - embedded
  - real-time
  - speech-preservation
  - low-look-ahead
  - strict-causal-audit
sources:
  - [[wiki_low_latency/sources/2022/DeepFilterNet2 2022]]
related:
  - [[wiki_low_latency/sources/2022/DeepFilterNet2 2022]]
  - [[wiki_low_latency/concepts/2205.05474-deep-filtering]]
  - [[wiki/sources/2023/DeepFilterNet 2023]]
  - [[wiki_low_latency/entities/PercepNet]]
  - [[wiki_low_latency/sources/2023/FSB-LSTM 2023]]
  - [[wiki_low_latency/sources/2023/GCFSnet 2023]]
causality: low_look_ahead
algorithmic_latency_ms: 40
sampling_rate: 未报告（论文以 48 kHz full-band 为背景口径）
---

# DeepFilterNet2

## 定义

DeepFilterNet2 是面向全带嵌入式实时语音增强的两阶段系统：先用 ERB-domain gains 做粗粒度频率抑制，再用低频 complex deep filter 恢复周期性和相位细节。

## 关键管线

~~~text
waveform → STFT / ERB features → gain estimator + low-frequency deep-filter estimator
        → ERB gains + complex DF coefficients → optional post-filter → iSTFT waveform
~~~

## 低时延审计

论文报告约 0.36 G MACS/s、i5-8250U RTF 0.04、Raspberry Pi 4 RTF 0.42，但原始配置使用 40 ms 算法时延和 2-frame look-ahead。因此它是低复杂度/实时部署参照，不是严格 2 ms causal 方案；capture-to-playback p99、峰值 RAM、能耗和 deadline miss 未报告。

## 质量—保留权衡

post-filter 可以改善 DNS4 的背景噪声与总体 MOS，但会牺牲 VoiceBank+DEMAND 的 PESQ/CSIG。这个 SIG–BAK trade-off 是本方向评估“噪声压制是否误伤人声”的重要参照。

## 输入、输出与架构证据

| 项目 | 论文证据 |
|---|---|
| 输入 | full-band noisy waveform，经 STFT 得到 ERB features 与 low-frequency complex features |
| 第一阶段 | 32-band ERB envelope gain，插值回 STFT 频率轴 |
| 第二阶段 | 5 kHz 以下、order N=5 的 multi-frame complex deep filtering；look-ahead l=2 frames |
| 输出 | enhanced complex STFT，经 iSTFT 输出 waveform |
| 结构优化 | unified encoder、GLinear/频率分组、1×3 temporal kernels、输入层 causal 3×3、grouped PConv |
| 训练目标 | 沿用 L_spec，增加 5/10/20/40 ms multi-resolution spectrogram loss；λ_spec=1e3、λ_MR=5e2 |

原论文 PDF p.2 的 Fig. 1 与 Eq. (3)–(7) 证据集中在：

[[wiki_low_latency/sources/2022/DeepFilterNet2 2022#3. 这个做法核心 trick 是什么？]]

## 精确结果与证据边界

来源页的完整 Table 1/2 位于：

[[wiki_low_latency/sources/2022/DeepFilterNet2 2022#4. 实验里哪个消融最关键？]]

关键行：

| 配置 | Params | MACS | Core i5 RTF | PESQ | STOI |
|---|---:|---:|---:|---:|---:|
| DeepFilterNet | 1.78 M | 0.35 G | 0.11 | 2.81 | 0.942 |
| + Simplified DNN | 2.31 M | 0.36 G | 0.04 | 3.08 | 0.943 |
| + Post-Filter | 2.31 M | 0.36 G | 0.04 | 3.03 | 0.941 |

DNS4 blind test 的 DeepFilterNet2 / +Post-Filter 为 SIGMOS 4.20/4.19、BAKMOS 4.43/4.47、OVLMOS 3.88/3.90。论文另在结论中报告 Raspberry Pi 4 RTF=0.42。

这些结果支持低复杂度平均实时与 SIG–BAK trade-off；未报告目标 SoC 的 p50/p95/p99、deadline miss、capture-to-playback、峰值 RAM、固定点精度、false-suppression、ASR WER、F0/formant/prosody continuity。

## 低时延证据与相关链接

### 证据

- [[wiki_low_latency/sources/2022/DeepFilterNet2 2022#2. 之前的人怎么做不了？（limitation → gap）]]：40 ms、2-frame look-ahead 与 strict-causal 判定。
- [[wiki_low_latency/sources/2022/DeepFilterNet2 2022#5. 这个方向还剩什么问题没解决？（future work / limitation）]]：RTF、deadline、I/O 和部署缺口。
- 本地 PDF：raw/papers/low_latency_causal_se/2205.05474.pdf；重点页 p.2、p.3、p.4。

### 相关链接

- [[wiki_low_latency/concepts/2205.05474-deep-filtering]]：ERB envelope、复数 DF、MR loss 与公式歧义。
- [[wiki/sources/2023/DeepFilterNet 2023]]：同一 DeepFilterNet 工程家族。
- [[wiki_low_latency/sources/2023/FSB-LSTM 2023]]：同分支低复杂度时频路线。
- [[wiki_low_latency/sources/2023/GCFSnet 2023]]：多麦/双耳复数 filter-and-sum；仅作跨分支比较，不表示同一任务。

## PDF 证据

本实体页的唯一证据是 [[wiki_low_latency/sources/2022/DeepFilterNet2 2022]] 所指向的本地 PDF raw/papers/low_latency_causal_se/2205.05474.pdf：

| PDF 页码 | 可核对内容 |
|---|---|
| 第 1 页 | full-band/embedded 动机、信号模型、DeepFilterNet 两阶段背景、摘要 RTF=0.04 |
| 第 2 页 | Figure 1-2、ERB gain 与 DF 流程、式 (3)-(7)、训练调度与 multi-resolution loss |
| 第 3 页 | 数据增强、Unified encoder、grouping、$1\times3$ 频率卷积、PConv、Figure 3、post-filter 和 40 ms 配置 |
| 第 4 页 | Voicebank+Demand Table 1、DNS4 blind Table 2、Core i5-8250U RTF 测量、Raspberry Pi 4 结论 |

可复核的最终结果为：2.31 M 参数、0.36 G MACS/s、Core i5-8250U 平均 5 次 RTF=0.04；Voicebank+Demand 的 '+ Post-Filter' 行为 WB-PESQ=3.03、CSIG=3.72、CBAK=3.37、COVL=3.63、STOI=0.941；DNS4 blind 的 '+ Post-Filter' 行为 SIGMOS=4.19、BAKMOS=4.47、OVLMOS=3.90（第 4 页）。论文结论另报 Raspberry Pi 4 RTF=0.42，但没有 p99、deadline miss 或 capture-to-playback 证据。

## 交叉链接

- [[wiki_low_latency/sources/2022/DeepFilterNet2 2022]]
- [[wiki_low_latency/concepts/2205.05474-deep-filtering]]
- [[wiki/sources/2023/DeepFilterNet 2023]]
- [[wiki/concepts/STFT与频谱图]]
- [[wiki/concepts/全带与子带模型]]
- [[wiki_low_latency/entities/GCFSnet]]
