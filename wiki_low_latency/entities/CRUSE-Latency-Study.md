---
title: CRUSE-Latency-Study - 统一低时延语音增强评测配置
type: entity
created: 2026-09-16
updated: 2026-09-16
tags:
  - benchmark
  - speech-enhancement
  - low-latency
  - strict-causal-audit
  - CRUSE
  - DNSMOS
  - speech-preservation
sources:
  - [[wiki_low_latency/sources/2024/Ultra-Low Latency Speech Enhancement Comprehensive Study 2024]]
related:
  - [[wiki_low_latency/concepts/2409.10358-ultra-low-latency-benchmark]]
  - [[wiki_low_latency/index]]
  - [[wiki_low_latency/overview]]
  - [[wiki_low_latency/entities/GCFSnet]]
  - [[wiki/sources/2023/DeepFilterNet 2023]]
  - [[wiki/sources/2021/FullSubNet 2021]]
  - [[wiki/sources/2024/Mamba for SE 2024]]
  - [[wiki/concepts/实时与离线语音增强]]
  - [[wiki/concepts/语音增强评价指标]]
---

# CRUSE-Latency-Study

## 定义

CRUSE-Latency-Study 是本库为 2409.10358 建立的“方法/评测实体”页，指论文中以 CRUSE 为固定增强主干、统一训练和测试管线，并替换低时延模块的一组可比较配置。它不是论文官方命名的单一部署模型，也不应把表 I 中的 F4、C1 等实验行误写成一个模型版本。

论文的任务是单通道语音增强：

$$
x(t)=s(t)+n(t)\longrightarrow \hat{s}(t),
$$

其中 $n(t)$ 包含加入的噪声和混响噪声。它更像一个控制变量基准，用来回答“窗、变换、预测、时序模块和模型容量分别如何影响低时延增强”，而不是发布一个端到端硬件系统。

## 基础管线与输入输出

~~~text
带噪单通道波形 x(t)
  → 分段 x_k、分析窗 w_a、变换 W_fft
  → X ∈ R^(N×K)
  → CRUSE f_theta / filtering 或 mapping
  → 增强表示或复数滤波器
  → 合成窗 w_s、inverse transform、overlap-add
  → 增强波形 ŝ(t)
~~~

论文给出的分析与合成变换为：

$$
X_k=(x_k\circ w_a)\cdot W_{\mathrm{fft}},\qquad
\hat{s}_k=(\hat{S}_k\cdot W_{\mathrm{ifft}})\circ w_s.
$$

符号含义：

- $x_k$：长度 $L_a$ 的第 $k$ 个输入段；$w_a$：分析窗；
- $W_{\mathrm{fft}}$：$L_a\times N$ 的分析基函数矩阵；$X_k$：$N$ 维分析表示；
- $\hat S_k$：增强后的段表示；$W_{\mathrm{ifft}}$：$N\times L_s$ 合成基函数矩阵；
- $w_s$：长度 $L_s$ 的合成窗；$\hat s_k$：经 overlap-add 合成的段波形；
- $P$：frame shift；$K$：段数；$\circ$ 是逐元素乘法，$\cdot$ 是矩阵乘法。

论文把 overlap-add 引入的算法延迟写作：

$$
L_{\mathrm{alg}}=L_s-P.
$$

该式不含模型执行时间、输入输出 buffer、ADC/DAC 或设备端到端链路。

## CRUSE backbone

论文描述的 CRUSE 包含一系列卷积层、4-channel GRU bottleneck、镜像反卷积层和 conv-skip connections，并使用 causal 3x3 deep filters。主干使用 sqrt-Hann；为使窗口对照公平，缩短窗口时用 zero-padding 保持频率维度 $N$ 不变。

| 配置项 | PDF 明确内容 |
|---|---|
| 任务 | 单通道语音增强 |
| 输入 | 带噪 waveform，经分析变换得到 $X$ |
| backbone | convolutional recurrent U-Net，4-channel GRU bottleneck，deconvolution，conv-skip |
| filtering | causal 3x3 deep filters |
| 原始规模 | 0.625M parameters；sym-20ms 为 230.27M MACs |
| 3 ms 原始 CRUSE | sym-3ms 为 0.625M、1.54G MACs |
| medium/large | 2.32M / 8.67M parameters；large 3 ms 为 10.95G MACs |
| Mamba 替换 | 0.642M parameters；表中 MACs 为 - |
| 采样率/量化 | 未报告 |

## 可比较的低时延配置

| 族 | 关键替换 | 论文的延迟/质量解释 |
|---|---|---|
| sym | 对称分析/合成窗 | 20/10/5/3 ms；短窗固定模型时质量下降、MACs 增长 |
| asym | 长分析窗 + 短合成窗 | 保留部分分析频率分辨率；完整 CRUSE 上不稳定优于 sym |
| Learn-asym | 可训练分析/合成 convolution/transposed convolution | 中高时延点更有优势；分析端 ReLU 可改善性能和稳定性 |
| same-compute | 随 hop 缩小卷积滤波器数 | 用近似固定 MACs 换取更小模型，质量明显下降 |
| FBE | 预测复数短 FIR/filterbank，FFT/iFFT，保留最后 $P$ samples | 表中 10/5/2.5 ms；质量低于 overlap-add 路线 |
| future-predict | $X_0,\ldots,X_k\to\hat S_{k+1}$ | 50% overlap 时把算法延迟降为 0、剩 buffer hop；只能用 mapping target |
| Mamba | GRU 替换为 Mamba | 20 ms 尚可，5 ms 明显退化；MACs 未给出 |

## 关键结果证据

表 I 的范围和代表性结果：

| 对照 | 质量/复杂度证据 |
|---|---|
| A1 sym-20ms | DNS blind OVR 2.79；模拟 OVR/PESQ/siSDR 为 2.46/2.22/10.52 |
| A4 sym-3ms | DNS blind OVR 2.74；模拟 OVR/PESQ/siSDR 为 2.36/2.18/9.65；1.54G MACs |
| D3 same-compute-3ms | DNS blind OVR 2.67；模拟 OVR/PESQ/siSDR 为 2.33/2.05/9.03；230.33M MACs |
| F6 large asym-3ms | DNS blind OVR 2.80；模拟 OVR/PESQ/siSDR 为 2.42/2.27/10.34；8.67M、10.95G |
| C1 Learn-asym-10ms | DNS blind OVR 2.83；模拟 OVR/PESQ/siSDR 为 2.47/2.31/10.84 |
| E3 Mamba-5ms | DNS blind OVR 2.63；模拟 OVR/PESQ/siSDR 为 2.33/2.15/9.71 |
| H3 FBE-2.5ms | DNS blind OVR 2.62；模拟 OVR/PESQ/STOI/siSDR 为 2.27/1.89/81.73/7.80 |

完整逐行结果、Table II 和图像证据见 [[wiki_low_latency/sources/2024/Ultra-Low Latency Speech Enhancement Comprehensive Study 2024]]。

## 低时延、人声保留与部署审计

| 维度 | 当前实体页可确认 | 不能由论文推出 |
|---|---|---|
| 因果性 | 论文写 causal 3x3 deep filters | 逐层 strict-causal certificate、padding、归一化、最新可读样本 |
| 算法延迟 | $L_s-P$；表中 Latency 为 20/10/5/3/2.5 ms 等 | 计算 p50/p95/p99、capture-to-playback |
| 计算 | parameters、MACs/sec | RTF、硬件、峰值 RAM/SRAM、功耗、deadline miss |
| 噪声抑制 | DNSMOS BAK/OVR、模拟数据指标 | 按噪声类型和 -10/-5/0/5 dB 分层 |
| 人声保留 | DNSMOS SIG、STOI | false-suppression、SPP/VAD、ASR WER、F0/formant/prosody、voiced energy、人工 MOS |
| 长流部署 | 未报告 | batch=1、warm-up、state reset、underrun/overrun、恢复策略 |

## 关联页面

- 源论文：[[wiki_low_latency/sources/2024/Ultra-Low Latency Speech Enhancement Comprehensive Study 2024]]
- 统一低时延概念：[[wiki_low_latency/concepts/2409.10358-ultra-low-latency-benchmark]]
- 低时延方向：[[wiki_low_latency/index]]、[[wiki_low_latency/overview]]
- 空间/双耳对照：[[wiki_low_latency/entities/GCFSnet]]、[[wiki_low_latency/concepts/低比特率双耳特征链路]]
- 一般实时增强：[[wiki/sources/2023/DeepFilterNet 2023]]、[[wiki/sources/2021/FullSubNet 2021]]
- Mamba 线索：[[wiki/sources/2024/Mamba for SE 2024]]
- 指标与延迟：[[wiki/concepts/语音增强评价指标]]、[[wiki/concepts/实时与离线语音增强]]
