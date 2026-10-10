---
title: log-mel 频谱 (Log-Mel Spectrogram)
type: concept
created: 2026-07-20
tags:
  - feature-extraction
  - spectrogram
  - mel-scale
  - perception
  - dcase
  - seld
related:
  - [[wiki/concepts/STFT与频谱图]]
  - [[wiki/concepts/Bark尺度与临界频带]]
  - [[wiki_array/concepts/GCC-PHAT 广义互相关]]
  - [[CST-former 2025]]
  - [[SELD-Mamba 2024]]
---

# log-mel 频谱 (Log-Mel Spectrogram)

## 一句话记忆点

> STFT 幅度谱 → 用 Mel 滤波器组（模仿人耳频率分辨率）降维 → 取 log（模仿人耳响度感知）→ 既压缩了数据又保留了感知相关的信息。

---

## 定义

log-mel 频谱是对 STFT 幅度谱做两步后处理得到的特征：

```
原始音频 [T_samples]
    ↓ STFT
复数频谱 [F, T]  (如 F=257 @ 16kHz, 512-FFT)
    ↓ |·|  取幅度
幅度谱 [F, T]
    ↓ × Mel filterbank  (F × M 矩阵, M=64)
Mel 频谱 [M, T]       ← 频率维从 F 压缩到 M
    ↓ log(·)
log-mel 频谱 [M, T]   ← 动态范围压缩
```

### Mel 尺度

人耳对频率的感知是非线性的——低频区分辨率高（能分辨 100 Hz 和 110 Hz），高频区分辨率低（难以分辨 5000 Hz 和 5100 Hz）。Mel 尺度用公式近似这种感知特性：

$$m = 2595 \cdot \log_{10}\left(1 + \frac{f}{700}\right)$$

```
线性频率 (Hz):  0    100   200   500   1000  2000  4000  8000
Mel 尺度:       0    150   283   607   1000  1521  2142  2767
                │─────│─────│──────│─────│─────│─────│─────│
                低频密集采样              高频逐步稀疏
```

Mel 滤波器组由 M 个三角滤波器组成，在 Mel 轴上等间距分布，投影回线性频率后低频密集、高频稀疏。

### 为什么取 log

取 log 做三件事：

| 效果 | 物理含义 | 为什么有用 |
|------|---------|----------|
| **动态范围压缩** | 语音幅度跨越 4-5 个数量级，log 压到 2-3 个 | 网络更容易学习——不需要处理 0.001 和 100 这种跨度 |
| **乘性噪声 → 加性** | log(A×N) = log(A) + log(N) | 卷积噪声在 log 域变成加法，便于线性模型分离 |
| **匹配人耳响度感知** | 人耳响度近似对数感知（dB 标度） | 特征本身就接近"人耳听到的"而非"物理测量的" |

---

## 常见配置

| 配置 | 值 | 场景 |
|------|:---:|------|
| FFT 点数 | 512 (16kHz) / 1024 (48kHz) | 标准 |
| Hop length | 50% overlap (如 256/512) | 标准 |
| Mel 频带数 M | 64 | DCASE SELD 标准 |
| Mel 频带数 M | 80 / 128 | ASR / 通用音频 |
| 频率范围 | 0-8kHz (16kHz 采样) / 0-24kHz (48kHz) | 取决于任务 |
| log 底数 | 自然对数 ln, log10, 或 20·log10 | 等价（差常数因子） |

### DCASE 的 7 通道标准输入

DCASE SELD 任务的 FOA (4ch Ambisonics) 格式使用**7 通道 log-mel + 强度向量**作为标准输入：

```
输入: [7, T, M=64]
  ├── 4 通道 log-mel (FOA 每个通道独立算 STFT → mel → log)
  └── 3 通道强度向量 (Intensity Vectors, 从 FOA 推导)
      ↑ 强度向量 = 声能流方向，编码 DOA 空间线索
```

强度向量就是 log-mel 频谱中每个 T-F bin 的**声能传播方向的归一化向量**——将每个 T-F bin 的空间信息（方向）与其频谱内容绑定，使得一个 Transformer 块可以同时利用该 bin 的内容和位置信息。这和 GCC-PHAT 互补：GCC-PHAT 编码跨通道相位差，强度向量编码瞬时声能流方向。

---

## 与其他频谱特征的对比

| 特征 | F 维大小 | 是否保留相位 | 是否感知加权 | 典型场景 |
|------|:---:|:---:|:---:|------|
| **STFT 线性幅度** | 257 | ❌ | ❌ | 语音增强（需要高频率分辨率做精细 mask） |
| **log-mel** | 64 | ❌ | ✅ (Mel) + ✅ (log) | SELD、ASR、音频分类 |
| **MFCC** | 13-40 | ❌ | ✅ (Mel) + ✅ (DCT) | 传统 ASR、说话人识别 |
| **BFCC** (Bark) | 22 | ❌ | ✅ (Bark) | RNNoise（极低参数量） |
| **STFT complex** | 257 | ✅ | ❌ | DCCRN、DPCRN（需要相位做复数 mask） |
| **Raw waveform** | — | ✅ | ❌ | Conv-TasNet（让网络自己学） |

### 增强为什么用线性幅度多，定位为什么用 log-mel 多？

**增强**需要精细的逐频率增益——256 个频率 bin 各一个 mask 值。log-mel 的 64 维太粗糙，一个 mel band 覆盖多个谐波 → 无法精确保留/削除单个谐波。

**定位**不需要逐 bin 精细度——DOA 只需分辨"哪个方向"，64 个 mel band 足够。而且 log-mel 压缩了幅度差异（log 让小声大声接近），帮助网络专注于**频谱形状**（共振峰位置）和**通道间差异**（相位差）而非绝对响度。

---

## 关键属性

### 优点

1. **维数降低**：F=257 → M=64 → 约 4× 压缩 → 减少下游模型参数和计算量
2. **感知对齐**：Mel 频率分辨率 + log 响度压缩 ≈ 人耳处理音频的方式
3. **鲁棒性**：log 压缩减少了对输入音量变化的敏感度
4. **结构化降维**：不同于 pooling 的"无差别压扁"，Mel 滤波器保留了低频优先的结构

### 局限

1. **不可逆**：丢失了相位和精细频率结构 → 无法用 iSTFT 重建波形 → 需配合其他特征或端到端生成
2. **Mel 是固定的**：滤波器组形状和带宽由 Mel 公式决定 → 不像可学习编码器可以任务自适应
3. **log 的非线性不可控**：log(0) 和低幅度区域的噪声放大 → 通常需要加 ε 截断 (log(x+ε), ε=1e-5)
4. **高频信息压缩过多**：8000 Hz 在 Mel 轴上仅有 ~400 mel 的覆盖 → 高频摩擦音（>4kHz）的分辨率远低于低频

---

## Mel vs Bark

Mel 和 Bark 都模仿人耳的频率感知，但来源和参数不同：

| | Mel | Bark |
|---|---|---|
| **来源** | Stevens & Volkmann (1937)，音高匹配实验 | Zwicker (1961)，临界频带理论 |
| **频带数** | 64-128（工程常用） | 22-24（感知理论） |
| **公式** | $m = 2595 \cdot \log_{10}(1+f/700)$ | $z = 13 \cdot \arctan(0.00076f) + 3.5 \cdot \arctan((f/7500)^2)$ |
| **设计理念** | 经验公式，纯数学 | 基于听觉掩蔽效应的生理模型 |
| **低频分辨率** | 较细 | 较粗（Bark 频带在低频更宽） |
| **使用场景** | ASR、SELD、通用音频 | RNNoise、PercepNet、心理声学建模 |

Bark 频带数更少（22 vs 64），因为它严格对应 24 个临界频带——每个频带内掩蔽效应独立。Mel 在工程中被调参（64, 80, 128）是因为不需要严格的心理声学约束。

---

## 在库中的使用

### SELD/DOA 方向（主力特征）

| 论文 | 输入特征 |
|------|---------|
| [[CST-former 2025]] | **7ch log-mel** (4ch FOA + 3ch IV) |
| [[SELD-Mamba 2024]] | **7ch log-mel + IV** |
| [[ResNet-Conformer SELD 2025]] | log-mel + GCC-PHAT + IV |

DCASE 2022-2024 的 7ch log-mel 已是 SELD 方向的事实标准输入。

### 增强/分离方向（偶尔使用）

增强方向主要用 STFT 线性幅度（需要精细频率 mask），log-mel 仅在轻量/实时方案中出现，如 PercepNet 使用 Bark 频带的变体。BFCC（RNNoise）可视为 Bark 域 log-mel 的近亲。

---

## 相关概念

- [[wiki/concepts/STFT与频谱图]] — log-mel 的上游特征
- [[wiki/concepts/Bark尺度与临界频带]] — 另一种感知频率尺度
- [[wiki_array/concepts/GCC-PHAT 广义互相关]] — DCASE 输入中和 log-mel 配对的另一组特征
- [[wiki/concepts/可学习编码器 Learnable Encoder]] — log-mel 的"可学习替代方案"——不做固定滤波，让网络自己学最优基函数
