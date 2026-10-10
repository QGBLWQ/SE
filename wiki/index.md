---
title: Wiki 内容目录
type: index
created: 2026-06-05
updated: 2026-09-16
tags:
  - index
---

# Wiki 内容目录

## 综述

- [[语音定位+语音增强/wiki/overview|语音增强与音源分离 Wiki 综述]]

## 实体 (Entities)

*模型、架构、工具等*

- [[RNNoise]] — Mozilla 开源实时全频带语音增强库 (2018)

## 概念 (Concepts)

*理论、方法、术语等*

- [[理想比率掩蔽 IRM]] — 时频域有监督分离的核心训练目标
- [[Bark尺度与临界频带]] — 基于人耳听觉感知的频率尺度
- [[感知加权损失函数]] — RNNoise 提出的 $\gamma$-指数加权 MSE 损失
- [[谐波]] — 基频整数倍频率分量，浊音的本质频谱结构
- [[Pitch滤波器]] — 频域梳状滤波器，利用谐波结构消除谐波间残余噪声
- [[时序卷积网络 TCN]] — 堆叠扩张卷积块，RNN/LSTM 的卷积替代品 🆕
- [[理想掩蔽 Ideal Mask]] — IBM/IRM/WFM 三种 oracle mask，频域方法的理论上限 🆕
- [[可学习编码器 Learnable Encoder]] — 让网络自己学习"如何把波形变成特征"，替代固定 STFT 🆕
- [[FTB 频时注意力块]] — 频率+时间分离注意力 + 幅度-相位跨模态信息交换 🆕
- [[全带与子带模型]] — 频率维"分而治之"：全带看全局频谱结构，子带做逐 bin 精细增益 🆕
- [[log-mel 频谱]] — STFT 幅度 → Mel 滤波器组 → log 压缩：感知驱动的频谱降维 🆕

## 资料摘要 (Sources)

*每篇源文章对应一个摘要页面。共 26 篇 (2026-07-06 更新)*

- [[CMGAN 2022]]
- [[CRAFT 2022]]
- [[Conditional Diffusion SE 2022]]
- [[Conv-TasNet 2019]]
- [[DCCRN 2020]]
- [[DPCRN 2021]]
- [[DPRNN 2020]]
- [[DeepFilterNet 2023]]
- [[Demucs 2019]]
- [[FullSubNet 2021]]
- [[Investigating Design Space of Diffusion for SE 2023]]
- [[MP-SENet 2023]]
- [[Mamba for SE 2024]]
- [[MetricGAN+ 2021]]
- [[MossFormer 2022]]
- [[PHASEN 2020]]
- [[PercepNet 2020]]
- [[RNNoise 2018]]
- [[Real Time SE Waveform 2020]]
- [[SEGAN 2017]]
- [[SELM 2023]]
- [[SGMSE+ 2023]]
- [[SepFormer 2021]]
- [[SuDoRM-RF 2020]]
- [[TF Attention Module 2023]]
- [[TF-GridNet 2023]]
- [[Wave-U-Net 2018]]

## 主题 (Topics)

*跨实体的综合论述*

> 待添加 — 随摄入量累积后建立

## 综述资料 (Surveys)

- [[deep-learning-speech-enhancement-survey|Deep Learning for Speech Enhancement: A Comprehensive Survey]] 🆕

## 其他 Wiki

- [[语音定位+语音增强/wiki_array/index|声源定位与阵列处理 Wiki]] 🆕
- [[wiki_low_latency/index|严格因果超低时延语音增强 Wiki]] — 约 2 ms 算法延迟、低 SNR 噪声抑制与人声保留

## 操作日志

- [[语音定位+语音增强/wiki/log|操作日志]]

---

## 原始资料清单

### 论文 PDF (`raw/papers/`)

| # | 文件名 | 年份 | 方向 |
|---|---|---|---|
| 1 | ~~Hybrid DSP Deep Learning Approach to Real-Time Full-Band Speech Enhancement~~ ✅ | 2018 | 语音增强 |
| 2 | Wave-U-Net A Multi-Scale Neural Network for End-to-End Audio Source Separation | 2018 | 音源分离 |
| 3 | Conv-TasNet Surpassing Ideal Time-Frequency Magnitude Masking | 2019 | 语音分离 |
| 4 | Phase-Aware Speech Enhancement with Deep Complex U-Net (RETRACTED) | 2019 | 语音增强 |
| 5 | DPRNN Dual-Path RNN for Time-Domain Speech Separation | 2020 | 语音分离 |
| 6 | PHASEN A Phase-and-Harmonics-Aware Speech Enhancement Network | 2020 | 语音增强 |
| 7 | PercepNet A Perceptually-Motivated Approach for Real-Time Enhancement | 2020 | 语音增强 |
| 8 | SepFormer Attention Is All You Need in Speech Separation | 2021 | 语音分离 |
| 9 | DCCRN Deep Complex Convolution Recurrent Network | 2020 | 语音增强 |
| 10 | DPCRN Dual-Path Convolution Recurrent Network | 2021 | 语音增强 |
| 11 | Music Source Separation in the Waveform Domain | 2019 | 音源分离 |
| 12 | SuDoRM-RF Efficient Networks for Universal Audio Source Separation | 2020 | 音源分离 |

### 已转换笔记 (`raw/articles/`)

| # | 文件名 |
|---|---|
| 1 | RNNoise - Hybrid DSP_Deep Learning Speech Enhancement |
| 2 | 2019 - End-to-End Music Source Separation |
| 3 | 2020 - DCCRN Deep Complex Convolution Recurrent Network |
| 4 | 2020 - SuDoRM-RF Efficient Networks |
| 5 | 2021 - DPCRN Dual-Path Convolution Recurrent Network |
| 6 | 复数卷积循环网络 DCCRN |
| 7 | 感受野 Receptive Field |
| 8 | 扩张卷积 Dilated Convolution |
| 9 | 1705.00919 — CNN DOA Estimation with Noise Training → [[wiki_array/index|阵列处理 Wiki]] ✅ |

<!-- frontier-2026-09-08:start -->
## 2026-09-08 前沿论文专题

- [[wiki/topics/2026 语音增强前沿五篇比较]]
- [[U-PAST 2026]]
- [[Balanced Spectral Reconstruction 2026]]
- [[muNet 2026]]
- [[Cloud-Boosted MCSE 2026]]
- [[FlowSE-GRPO 2026]]
<!-- frontier-2026-09-08:end -->
