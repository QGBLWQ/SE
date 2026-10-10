---
title: Bark 尺度与临界频带
type: concept
created: 2026-06-05
updated: 2026-06-05
tags:
  - psychoacoustics
  - frequency-scale
  - bark
  - critical-band
  - speech-enhancement
  - feature-extraction
sources: [RNNoise 2018]
related:
  - [[wiki/concepts/理想比率掩蔽 IRM]]
---

# Bark 尺度与临界频带

## 定义

**Bark 尺度**是一种基于人耳听觉感知的频率尺度，由 Eberhard Zwicker 于 1961 年提出。它将可听频率范围 (0–24 kHz) 映射到约 24 个"临界频带"(critical bands)，每个临界频带对应耳蜗基底膜上约 1.3 mm 的长度。

Bark 尺度的核心思想：**人耳对不同频率的分辨率不是线性的**——低频区分辨率高，高频区分辨率低。

## 频率到 Bark 的映射

常用近似公式 (Traunmüller, 1990)：

$$z(f) = \frac{26.81f}{1960 + f} - 0.53$$

其中 $f$ 为频率 (Hz)，$z$ 为 Bark 号。

| 频率 (Hz) | Bark 号 | 临界带宽 (Hz) |
|---|---|---|
| 100 | 0.9 | ~100 |
| 500 | 4.3 | ~110 |
| 1000 | 7.5 | ~160 |
| 2000 | 12.3 | ~300 |
| 4000 | 17.6 | ~550 |
| 8000 | 21.6 | ~1200 |
| 16000 | 24.0 | ~3400 |

## 与 Mel 尺度的对比

| | Bark 尺度 | Mel 尺度 |
|---|---|---|
| **提出** | Zwicker, 1961 | Stevens, Volkmann & Newman, 1937 |
| **基础** | 临界频带 (听觉滤波器带宽) | 音高感知实验 |
| **频带数** | ~24 (0–24kHz) | 常见 40/80 个滤波器 |
| **低频精度** | 至少 4 个 FFT bin | 滤波器带宽恒定 |
| **应用** | 语音编码 (Opus)、噪声抑制 (RNNoise) | 语音识别、说话人识别 |

## 在 RNNoise 中的使用

RNNoise 使用 22 个 Bark 尺度三角频带替代细粒度的频率 bin，这是其**复杂度的关键技术**：

### 动机

- 48 kHz FFT 产生 960 个频率 bin (20 ms 窗)
- 直接让神经网络预测每个 bin 的增益 → 输出维度太高，参数量爆炸
- 但语音和噪声的**频谱包络** (spectral envelope) 往往是平滑的，不需要每个 bin 精细控制

### 设计

- 22 个三角频带覆盖 0–20 kHz
- 高频遵循 Bark 尺度（带宽随频率增大）
- 低频至少 4 个 FFT bin（保证足够分辨率）
- 三角滤波器：相邻频带之间平滑过渡，$\sum_b w_b(k) = 1$

### 代价与补偿

- **代价**：Bark 频带分辨率不足以抑制 pitch 谐波之间的噪声（谐波间距可能只有几十 Hz）
- **补偿**：增加了一个**频域 pitch 梳状滤波器**，专门处理谐波间噪声，形成"粗+细"两级抑制

## BFCC (Bark-Frequency Cepstral Coefficients)

RNNoise 的输入特征之一就是对 22 个 Bark 频带的对数能量做 DCT 变换：

$$\text{BFCC}[n] = \sum_{b=0}^{21} \log E(b) \cdot \cos\left[\frac{\pi n}{22}\left(b + \frac{1}{2}\right)\right]$$

DCT 的作用：去相关化 (decorrelation)，提高训练数据的条件数 (conditioning)。

## 相关概念

- [[理想比率掩蔽 IRM]] — RNNoise 在 Bark 频带而非频率 bin 上计算 IRM
- [[感知加权损失函数]] — Bark 频带的另一个优势：与感知而非物理频率对应
