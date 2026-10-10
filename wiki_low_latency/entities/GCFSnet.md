---
title: GCFSnet
type: entity
created: 2026-09-16
updated: 2026-09-16
tags:
  - model
  - multichannel
  - binaural
  - filter-and-sum
  - low-latency
  - quantization
related:
  - [[wiki_low_latency/sources/2023/GCFSnet 2023]]
  - [[wiki_low_latency/concepts/低比特率双耳特征链路]]
  - [[wiki_array/concepts/波束成形 Beamforming]]
---

# GCFSnet

## 概述

GCFSnet（Group-Communication Filter-and-Sum Network）是 Westhausen 与 Meyer 在 2023 年提出的低复杂度、因果、多输入单输出多通道语音增强模型，面向互联双耳助听器。它在每一侧用当前本侧麦克风做复数 filter-and-sum 和 causal multi-frame post-filter，同时可以把已延迟、低比特率的跨耳特征送入滤波器估计器。

## 管线

~~~text
本侧多麦克风 STFT ──┐
                    ├─→ Features → GCFSnet filter estimator
延迟/量化跨耳特征 ───┘                 ├─→ 复数 W：本侧 filter-and-sum
                                      └─→ 复数 C：多帧 causal post-filter
                                                    ↓
                                                  iSTFT
                                                    ↓
                                                 本侧语音
~~~

## 配置与规模

| 项目 | 论文配置 |
|---|---|
| 采样率/前端 | 16 kHz；2 ms frame；1 ms shift；FFT 64；Hann |
| 输入 | log-magnitude STFT、sin/cos IPD；lowB 追加延迟跨耳特征 |
| backbone | group projection → shared DS-Conv → TAC → 2-layer GRU → TAC |
| group 参数 | $P=128,\ U=32,\ G=8$ |
| 后滤波 | 论文配置 $K=5$；公式使用 $k=0,\ldots,K$ |
| 参数/计算 | 164k 参数；约 0.36 GMAC/s/side |
| 量化 | weight 8 bit；bias/input/output 16 bit；range $[-1,1]$ |

## 三种系统

- GCFSnetuni：无跨耳通信，只用本侧两个麦克风。
- GCFSnetlowB：跨耳特征经历已知延迟和 4–16 bit 量化；空间滤波仍只使用本侧当前麦克风。
- GCFSnetbin：无延迟同步双耳链路，作为理想双耳信息上界。

## 关键性质

1. **低时延主路径**：延迟跨耳信号不用于等待对齐，而只作为估计器的辅助提示。
2. **空间信息优先**：特征消融显示延迟 IPD 比延迟 log-magnitude 更能改善 SI-SDR。
3. **共享与量化**：Group Communication、weight sharing 和 QAT 把模型压缩到助听器 SoC 预算。
4. **证据边界**：2 ms 是论文的过滤框架口径；真实硬件端到端延迟、p99 deadline、状态恢复和听障用户评估仍待验证。

*** Add File: E:/work!/语音定位+语音增强/wiki_low_latency/concepts/低比特率双耳特征链路.md
---
title: 低比特率双耳特征链路
type: concept
created: 2026-09-16
updated: 2026-09-16
tags:
  - binaural
  - low-latency
  - multichannel
  - IPD
  - quantization
  - speech-preservation
sources:
  - [[wiki_low_latency/sources/2023/GCFSnet 2023]]
related:
  - [[wiki_array/concepts/波束成形 Beamforming]]
  - [[wiki_low_latency/entities/GCFSnet]]
---

# 低比特率双耳特征链路

## 定义

低比特率双耳特征链路（low-bit-rate binaural feature link）是一个面向双设备实时增强的系统模式：不传输或不等待完整的跨耳波形，而是传输经过延迟和量化的低维声学特征，让本侧模型利用部分空间信息，同时保持本侧当前信号的低延迟主路径。

## 核心分工

~~~text
当前本侧信号 ──→ 空间滤波/增强输出 ──→ 当前输出
       ↑
延迟跨耳特征 ──→ 滤波器估计器（辅助条件）
~~~

这里的延迟跨耳特征是 stale context，不是 future context。它不能让模型看到未来，但可以提供较早时刻的跨耳方位/相位线索。对严格因果系统，必须验证：

- 传输特征是否只依赖过去样本；
- 延迟是否被显式建模且不触发额外等待；
- 量化是否在训练和推理中一致；
- 本侧输出是否可以在跨耳包丢失时 bypass 或恢复。

## GCFSnet 中的特征

GCFSnet 使用跨耳 log-magnitude STFT 与 binaural $\sin(\mathrm{IPD})/\cos(\mathrm{IPD})$。其中 IPD 直接携带方向到达线索，sin/cos 表示避免角度 wrap，log magnitude 则提供跨耳频谱能量信息。

在 delay=6 ms、8 bit 的特征消融中：

| 延迟跨耳特征 | SI-SDR | HASPI | MBSTOI | PESQ |
|---|---:|---:|---:|---:|
| 仅 log-magnitude | 0.06 | 0.67 | 0.53 | 1.18 |
| 仅 IPD | 0.66 | 0.69 | 0.56 | 1.19 |
| log-magnitude + IPD | **0.78** | **0.71** | 0.56 | **1.20** |

## 对本方向的启示

在双麦/多麦 2 ms 语音增强中，低比特率链路可以作为“空间置信度”输入，而不是强行让增强器等待同步全通道波形。下一步应把它与 [[wiki_low_latency/overview|SPP、gain floor、uncertainty 和 SIG–BAK 评估]]结合，并补齐真实设备 p99、包丢失、负 SNR 人声保留和空间线索保真测试。

