---
title: Uncertainty-Aware Speech Enhancement
type: entity
created: 2026-09-16
updated: 2026-09-16
tags:
  - model
  - speech-enhancement
  - uncertainty
  - aleatoric
  - epistemic
  - speech-preservation
  - non-causal-reference
sources:
  - [[wiki_low_latency/sources/2023/Uncertainty-Aware Speech Enhancement 2023]]
related:
  - [[wiki_low_latency/concepts/2305.08744-uncertainty-aware-suppression]]
  - [[wiki_low_latency/entities/Noise-Suppression-Losses]]
  - [[wiki_low_latency/sources/2020/PercepNet Low-Latency Direction 2020]]
  - [[wiki_low_latency/sources/2023/GCFSnet 2023]]
  - [[wiki_low_latency/index]]
---

# Uncertainty-Aware Speech Enhancement

## 定义

这是一个把数据不确定性（aleatoric）和模型不确定性（epistemic）显式纳入语音增强估计的概率谱方法。网络不仅预测 Wiener filter，还预测 clean-speech posterior variance；AMAP 幅度估计器据此做更保守的抑制。epistemic uncertainty 则通过 MC dropout 或 deep ensembles 的预测 spread 近似。

## 方法管线

~~~text
noisy complex STFT
        ↓
U-Net: Wiener mean + aleatoric variance
        ├─→ Wiener estimate
        └─→ AMAP magnitude estimate
                 ↑
       ensemble / MC-dropout spread
        ↓
enhanced waveform + uncertainty / reliability score
~~~

## 关键配置与证据

| 项目 | 论文证据 |
|---|---|
| 前端 | 16 kHz；32 ms Hann；50% overlap；约 16 ms hop |
| backbone | 6-block 2-D U-Net，instance normalization、skip connections |
| uncertainty | aleatoric variance head；MC dropout / deep ensembles |
| posterior | complex Gaussian clean-speech posterior；AMAP 使用 Rician magnitude 近似 |
| 代表结果 | DE-Aleatoric-AMAP：PESQ 2.83±0.10、ESTOI 0.92±0.01、SI-SDR 17.90±0.78 dB |
| reliability | AUSE：aleatoric 0.110、epistemic 0.094、联合 0.067 |
| 低时延边界 | 未报告 MAC/s、RTF、参数、p99；32 ms window 与 U-Net padding 未证明 strict-causal |

## 研究含义

高 posterior variance 可以降低目标语音被过度衰减的风险，但这不是免费的人声保留保证：噪声也可能被保留。AUSE 只说明 uncertainty 能否排序频谱误差，不等价于 coverage calibration、false-suppression 控制或端侧 deadline 通过。

## 关联页面

- [[wiki_low_latency/sources/2023/Uncertainty-Aware Speech Enhancement 2023]]
- [[wiki_low_latency/concepts/2305.08744-uncertainty-aware-suppression]]
- [[wiki_low_latency/concepts/2111.11606-speech-distortion-losses]]
- [[wiki_low_latency/concepts/2203.16843-continuity-loss]]
- [[wiki_low_latency/sources/2024/SlowFast-SSM 2024]]

> [!warning] 迁移边界
> 该实体是保声/可靠度设计参照，不是约 2 ms strict-causal 部署方案。把 U-Net 或多模型 ensemble 直接搬到端侧前，必须重新测 causal cache、单次/多次 forward 成本、p99 和 selective speech-preservation risk。
