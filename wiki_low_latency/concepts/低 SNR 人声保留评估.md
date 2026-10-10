---
title: 低 SNR 人声保留评估
type: concept
created: 2026-09-16
updated: 2026-09-16
tags:
  - speech-preservation
  - low-snr
  - over-suppression
  - evaluation
---

# 低 SNR 人声保留评估

## 定义

低 SNR 人声保留评估关注增强系统在降噪时是否伤害语音内容，而不只看整体 PESQ、STOI 或 SI-SDR。弱辅音、气声、音节边缘、有声周期和停顿附近最容易被 gain floor 或过抑制损伤。

## 建议指标

- DNSMOS SIG/BAK/OVL 或听感分维度；
- ASR WER/CER、音素/关键词 recall；
- voiced/unvoiced recall、F0 和 formant continuity；
- speech-preservation / false-suppression rate；
- 按 SNR、噪声类型、说话人和音素分层的质量—残留噪声 Pareto；
- 若使用 uncertainty 或 loss weighting，报告 calibration/AUSE 与人声保留的相关性。

## 与本方向的关系

PESQ、STOI、HASPI、SI-SDR 仍然有用，但不能单独证明弱语音未被抑制。所有 2 ms 候选都应把该页作为验收清单，并与 [[wiki_low_latency/concepts/严格因果与算法延迟]] 的 deadline 账本一起报告。

## 关联页面

- [[wiki_low_latency/sources/2021/Noise Suppression Losses 2021]]
- [[wiki_low_latency/sources/2022/Hybrid Continuity Loss 2022]]
- [[wiki_low_latency/sources/2023/Uncertainty-Aware Speech Enhancement 2023]]
- [[wiki_low_latency/sources/2023/GCFSnet 2023]]
