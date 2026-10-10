---
title: Noise Suppression Losses
type: entity
created: 2026-09-16
updated: 2026-09-16
tags:
  - loss-function
  - speech-enhancement
  - noise-suppression
  - speech-distortion
  - ASR
  - complex-stft
  - low-latency
sources:
  - [[wiki_low_latency/sources/2021/Noise Suppression Losses 2021]]
related:
  - [[wiki_low_latency/concepts/2111.11606-speech-distortion-losses]]
  - [[wiki_low_latency/index]]
  - [[wiki_low_latency/overview]]
  - [[wiki/concepts/感知加权损失函数]]
  - [[wiki/concepts/语音增强评价指标]]
  - [[wiki/sources/2021/MetricGAN+ 2021]]
  - [[wiki/sources/2021/DPCRN 2021]]
  - [[wiki/entities/RNNoise]]
---

# Noise Suppression Losses

## 简洁定义

Noise Suppression Losses 不是一个新的网络 backbone，而是一组用于实时语音增强训练的目标设计，核心实例来自 Braun 与 Gamper 的 2111.11606：在 CRUSE 的端到端复数 STFT 滤波器上，用 compressed complex spectral loss 的 magnitude 项约束语音失真，用 complex 项推动噪声抑制，并把训练损失的 STFT 分辨率与推理前端分离。

## 处理与训练接口

~~~text
推理:
noisy audio -> STFT_P -> compressed complex feature -> CRUSE -> G(k,n) -> iSTFT_P -> enhanced audio

训练 only:
target/enhanced -> STFT_L -> L_SD (+ CD / MOS-WER / embedding terms) -> update CRUSE
~~~

这是“训练目标实体”，不是一个可以脱离论文直接部署的独立模型。论文中 CRUSE 的配置是 4 个 encoder/decoder convolutional layers、通道 [32,64,128,256]、4 个并行 GRU bottleneck 子组和 1x1 skip convolutions；DNN 输出复数滤波器的实部/虚部两通道。

## 关键配置与公式

| 项目 | 2111.11606 中的 PDF 证据 |
|---|---|
| 推理前端 | square-root Hann，20 ms，50% overlap，FFT 320 |
| 训练损失前端 | L_SD^20：20 ms/50%；L_SD^32：32 ms/50%；L_SD^64：64 ms/75% |
| 压缩因子 | c=0.3 |
| 复数/幅度权重 | lambda=0.3 用作后续实验的平衡点；lambda=1 complex only，lambda=0 magnitude only |
| 模型规模 | 8.4M trainable parameters；12.8M MAC/frame |
| CPU 证据 | ONNX runtime 45 ms/s audio，standard laptop CPU；未报告 p50/p95/p99 |

核心损失为：

$$
\mathcal L_{SD}=\frac{1}{\sigma_s^c}\left(
\lambda\sum_{\kappa,\eta}|S^c-\hat S^c|^2
+(1-\lambda)\sum_{\kappa,\eta}\left||S|^c-|\hat S|^c\right|^2
\right),\qquad c=0.3.
$$

其中 S、hat S 是独立 loss STFT 的目标/增强频谱，S^c 是复数压缩谱，sigma_s 是由 VAD 得到的 active speech energy。complex 项同时感知实部/虚部对应的幅度和相位误差；magnitude 项是论文强调的 distortion regularizer。

## 证据结果

在论文 Table 1 中，plain L_SD^64 给出 nSIG=3.79、nBAK=4.28、nOVL=3.54，WER DNS/HQ/meet=30.1/5.9/18.4。相较 L_SD^20 的 3.77/4.23/3.50 与 31.0/5.9/18.7，较长的 loss STFT 在该实验中提升了 nBAK/nOVL 和 DNS WER；但这只是训练损失分辨率效应，不是 64 ms 推理延迟证据。

Table 1 中的 MOS/WER weighting、PANN4 和 wav2vec embedding 没有显著超过强谱损失。尤其要区分：论文的 nSIG/nBAK/nOVL 是无参考 P.835 DNN proxy，不等同于真人听测；论文也没有给严格因果、约 2 ms 算法时延、端到端 capture-to-playback 或 p99 deadline 证据。

## 低时延适配边界

- 可迁移的原则是：让 F_P 决定部署处理开销，让 F_L 在训练期提供更高分辨率监督。
- 不能把 20 ms window 自动写成 20 ms algorithmic latency，也不能把 real-time 自动标为 strict_causal。
- 采样率、centered/right padding、GRU state、look-ahead、warm-up、量化、目标硬件、streaming batch=1、I/O buffer 和长流恢复在该 PDF 中均未完整报告。
- 人声保留仍需单独加入 false-suppression、低 SNR 分层、ASR WER、F0/formant/prosody 和 voiced-energy 评估。

## 关联页面

- [[wiki_low_latency/sources/2021/Noise Suppression Losses 2021]]
- [[wiki_low_latency/concepts/2111.11606-speech-distortion-losses]]
- [[wiki_low_latency/index]]
- [[wiki_low_latency/overview]]
- [[wiki/concepts/感知加权损失函数]]
- [[wiki/concepts/语音增强评价指标]]
- [[wiki/sources/2021/MetricGAN+ 2021]]
- [[wiki/sources/2021/DPCRN 2021]]
- [[wiki/entities/RNNoise]]

> [!warning] 证据边界
> 该实体页描述的是损失设计及其在 CRUSE 中的实例，不应被读成一个已完成严格低时延认证的模型实体。详细的 PDF 页码、公式和 Table 1 全表见 [[wiki_low_latency/sources/2021/Noise Suppression Losses 2021]]。
