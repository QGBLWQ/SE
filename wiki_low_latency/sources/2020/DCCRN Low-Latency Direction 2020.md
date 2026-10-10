---
title: DCCRN — 深度复数卷积循环网络
type: source
created: 2026-09-16
updated: 2026-09-18
tags:
  - speech-enhancement
  - complex-valued
  - phase-aware
  - CRN
  - semi-causal
  - low-latency
source_type: paper
year: 2020
authors: Yanxin Hu, Yun Liu, Shubo Lv, Mengtao Xing, Shimin Zhang, Yihui Fu, Jian Wu, Bihong Zhang, Lei Xie
venue: INTERSPEECH 2020
arxiv: https://arxiv.org/abs/2008.00264
local_pdf: raw/papers/low_latency_causal_se/2008.00264.pdf
code: https://github.com/huyanxin/DeepComplexCRN
related:
  - [[wiki_low_latency/entities/DCCRN]]
  - [[wiki_low_latency/concepts/2008.00264-complex-phase-enhancement]]
  - [[wiki_low_latency/sources/2021/DPCRN Low-Latency Direction 2021]]
  - [[wiki_low_latency/sources/2022/DeepFilterNet2 2022]]
  - [[wiki/sources/2020/DCCRN 2020]]
---

~~~yaml
- 论文: [DCCRN: Deep Complex Convolution Recurrent Network for Phase-Aware Speech Enhancement](2020)
  ├── 要解决什么问题: 复数 STFT 的实部/虚部包含耦合的幅度与相位信息，普通实值 CRN 将其独立处理；同时 DCUNET 的计算量偏大
  ├── 核心方法: CRN encoder-decoder + complex Conv2d + complex BatchNorm + complex LSTM 变体，直接在复数谱上建模
  ├── 属于哪个分支: 相位感知单通道语音增强 / 复数网络 / 半因果流式增强
  ├── 输入/输出: noisy waveform → complex STFT (real/imag) → CRM 或极坐标 mask → enhanced complex spectrum → waveform
  ├── 关键trick: 用 2×2 实部/虚部耦合结构实现复数卷积，并比较 DCCRN-R/C/E/CL 的目标与复数组件
  ├── 数据集: WSJ0+MUSAN 模拟测试；DNS Challenge 的 simulated 与 blind test；16 kHz
  ├── 对比了谁: LSTM、实值 CRN、DCUNET，以及 DNS Challenge 参赛系统
  ├── 性能上限: WSJ0 平均 PESQ 最高 3.498（DCCRN-CL），DNS 实时赛道最终选择 DCCRN-E，blind-test average MOS 3.42
  ├── 参数量: 约 3.7M；DCCRN-E 单帧处理时间 3.12 ms（Intel i5-8250U，论文报告）
  ├── 消融关键发现: DCCRN 复数组件与同规模实值 CRN 的差异最关键；复数卷积的贡献大于复数 LSTM 的额外收益
  ├── 遗留问题(你的机会): 37.5 ms look-ahead 只满足 DNS 40 ms 规则，远未满足本 Wiki 的约 2 ms strict-causal；混响、过抑制和端侧 p99 仍缺证据
  └── 跟哪篇像: [[wiki_low_latency/sources/2021/DPCRN Low-Latency Direction 2021]]、[[wiki_low_latency/sources/2022/DeepFilterNet2 2022]]、[[wiki_low_latency/sources/2023/FSB-LSTM 2023]]、[[wiki_low_latency/sources/2023/GCFSnet 2023]]
~~~

> [!warning] PDF 转换质量与阅读说明
> 本地原 PDF 共 5 页。正文抽取对复数符号、上下标、公式编号和表格列有轻微错位；Figure 1/2、Eq. (1) 以及 Table 1–3 已用第 2 页和第 4 页页面渲染图视觉核对。下面的数字只在论文对应数据集、track 和配置内成立；PDF 没有提供端到端 p50/p95/p99。

> [!updated] 2026-09-18
> 补充 3.4 节「瓶颈 LSTM」配置（实值 2×256 / complex LSTM 128+128、1024 dense），并在 4.4 账本新增 look-back（过去视野）行。来源为 ar5iv 全文核对，本地 PDF 已加密未直接复核。

## 1. 他们为什么这么做？（motivation）

### 1.1 问题背景

STFT 的输出是复数。若增强器只预测幅度 mask、保留 noisy phase，噪声相位和语音相位的耦合误差会成为质量上限；若把 real/imag 仅堆叠成两个实值通道，网络也不必遵守复数乘法中的交叉关系。

DCCRN 的目标是把这两个问题放在同一套轻量的 CRN 骨架里处理：用复数网络直接处理 complex spectrum，同时用 LSTM 建模时间上下文，避免 DCUNET 依靠大量卷积层带来的高计算量。论文面向 DNS Challenge 的实时约束，因此保留了实际部署所需的单帧处理路径和小参数量。

### 1.2 与本 Wiki 方向的关系

DCCRN 是“相位/复数建模”路线的重要历史基线，但它不是本 Wiki 约 2 ms 目标的直接答案。它的 semi-causal decoder 使用未来帧，论文报告的 look-ahead 为 6 个 6.25 ms frame，即 37.5 ms；这满足 DNS Challenge 的 40 ms 规则，却不满足本方向的 strict-causal 约束。

## 2. 之前的人怎么做不了？（limitation → gap）

| 既有路线 | 能做什么 | 还缺什么 |
|---|---|---|
| 幅度-only mask + noisy phase | 训练简单、推理便宜 | 没有直接修正相位，强噪声和瞬态处容易产生残留/伪影 |
| 实值 CRN 处理 [real, imag] 两通道 | 有卷积和循环时序建模 | 实部/虚部被当作普通通道，未显式约束复数乘法耦合 |
| complex CNN / DCUNET | 能在复数谱上恢复相位 | 全卷积深网络计算量较大，长时间上下文和实时部署成本高 |
| 复数组件的零散使用 | 可验证某一个 complex layer | 缺少从 encoder、normalization、recurrent bottleneck 到 decoder 的统一管线 |

因此论文填补的 gap 不是“第一次使用频谱”，而是：在与实值 CRN 接近的参数规模下，把复数运算链路和时序建模整合起来，并用同架构对照判断收益究竟来自复数结构还是模型变大。

## 3. 这个做法核心 trick 是什么？

### 3.1 任务、输入与输出

| 项目 | 论文设置 |
|---|---|
| 任务 | 单通道 supervised speech enhancement / denoising |
| 输入 | noisy waveform $y(t)$，经 Conv-STFT 得到 $Y=Y_r+jY_i$ |
| 频谱 | 512-point complex spectrum；DNS 实时配置的 frame shift 为 100 samples，即 6.25 ms |
| 主干 | 5 个 complex Conv2d encoder block、bottleneck recurrent block、对称 decoder 和 skip connection |
| 输出 | complex mask 或其极坐标表示，得到 $\widehat S$，再经 Conv-iSTFT 生成 enhanced waveform |
| 训练目标 | 论文比较多种 masking target；最终 DNS 模型以 SI-SNR 作为时域训练目标 |

### 3.2 复数卷积：让实部和虚部按同一代数规则流动

令输入 $X=X_r+jX_i$，复数卷积核 $W=W_r+jW_i$，则：

$$
F_{\mathrm{out}}
=(X_r\star W_r-X_i\star W_i)
+j(X_r\star W_i+X_i\star W_r). \tag{1}
$$

$\star$ 是普通实值卷积；实现上需要四路实值卷积，但四路的组合固定为复数乘法的 2×2 结构。这样频率局部模式在 real/imag 之间共享梯度，幅度与相位不再是两个完全独立的特征流。

![[wiki_low_latency/assets/2008.00264/2008.00264-page2-architecture.png]]

图 1（原论文第 2 页页面渲染）：DCCRN 的 complex encoder/decoder、complex LSTM 与 complex module；同一页也核对了复数卷积公式和模块组成。

### 3.3 CRM 与复数模块

对 noisy complex spectrum $Y$ 和 clean complex spectrum $S$，理想 complex ratio mask 为：

$$
\operatorname{CRM}
=\frac{Y_rS_r+Y_iS_i}{Y_r^2+Y_i^2}
+j\frac{Y_rS_i-Y_iS_r}{Y_r^2+Y_i^2}. \tag{2}
$$

预测 $\widehat M$ 后：

$$
\widehat S=Y\odot\widehat M,\qquad
\widehat s=\operatorname{iSTFT}(\widehat S). \tag{3}
$$

论文比较了不同 mask/网络变体：DCCRN-R 对 real/imag 分量分别处理，DCCRN-C 使用复数乘法，DCCRN-E 在极坐标中估计 mask 幅度和相位，DCCRN-CL 进一步加入 complex LSTM。complex BatchNorm 用于复数特征归一化，激活采用 real-valued PReLU。

### 3.4 瓶颈 LSTM：两种时序建模版本

encoder 与 decoder 之间的"循环/RNN"部分就是 LSTM，用来沿时间轴建长程上下文（这也是过去视野无界的来源）。论文有两条 LSTM 路线：

| 变体 | LSTM 类型 | 配置 |
|---|---|---|
| DCCRN-R / C / E | 实值 LSTM | 2 层 × 256 units |
| DCCRN-CL | complex LSTM | 实部 128 + 虚部 128 units |

最后一级 LSTM 后接 1024-unit dense 层，再进对称 decoder。

**complex LSTM = 4 路实值 LSTM 按复数乘法拼装**（与 complex Conv2d 同一思路）。记两个实值 LSTM 类型为 $\mathrm{LSTM}_r$ 与 $\mathrm{LSTM}_i$：

$$
F_{rr}=\mathrm{LSTM}_r(X_r),\quad F_{ir}=\mathrm{LSTM}_r(X_i),\quad F_{ri}=\mathrm{LSTM}_i(X_r),\quad F_{ii}=\mathrm{LSTM}_i(X_i),
$$

$$
F_{out}=(F_{rr}-F_{ii})+j\,(F_{ri}+F_{ir}).
$$

对照复数乘法 $(a+jb)(c+jd)=(ac-bd)+j(ad+bc)$：实部 $F_{rr}-F_{ii}$ 对应 $ac-bd$，虚部 $F_{ri}+F_{ir}$ 对应 $ad+bc$，因此实/虚谱在逐帧递归内部也交叉耦合。完整推导与记号见 [[wiki_low_latency/concepts/2008.00264-complex-phase-enhancement]]。

**因果性**：LSTM 为单向（causal），hidden/cell state 可累积流开始以来的全部过去帧，属无界软记忆；它本身不读取未来帧，未来 37.5 ms 全部来自 decoder 每层前看 1 帧。

> [!question] 配置待核对
> LSTM 单元数、1024 dense 层，以及"5 个 encoder block vs 论文 channel list 6 项"的出入，均来自 ar5iv 全文核对（本地 PDF 已加密，未直接复核）。复现前建议以作者代码（github huyanxin/DeepComplexCRN）或解锁后 PDF p.3 配置表为准。

## 4. 实验里哪个消融最关键？

### 4.1 WSJ0 模拟实验

论文在 WSJ0+MUSAN 的混合语音上按 0/5/10/15/20 dB 分层评估 PESQ。Table 1 的平均值如下；这些是同一测试协议内的比较，不应与其他数据集的 PESQ 混排：

| 模型 | 参数 (M) | Ave. PESQ |
|---|---:|---:|
| LSTM | 9.6 | 3.326 |
| CRN | 6.1 | 3.329 |
| DCCRN-R | 3.7 | 3.424 |
| DCCRN-C | 3.7 | 3.409 |
| DCCRN-E | 3.7 | 3.433 |
| DCCRN-CL | 3.7 | **3.498** |
| DCUNET | 3.6 | 3.500 |

### 4.2 最关键消融：复数结构 vs 实值结构

最值得保留的结论是“同规模实值 CRN 对照”。在约 3.7M 参数规模下，完整复数路线相对于实值 CRN 的平均 PESQ 提升约 0.15；在 complex 路线内部，加入 complex LSTM 的额外收益小于 complex convolution 带来的收益。这个消融把结论锚定在表示和运算规则，而不是参数量。

| 消融/变体 | Ave. PESQ | 读法 |
|---|---:|---|
| 实值 CRN | 3.329 | 同类 encoder-decoder 的实值参照 |
| DCCRN-R/C/E | 3.424 / 3.409 / 3.433 | 复数目标/坐标选择会影响收益 |
| DCCRN-CL | **3.498** | complex LSTM + 复数主干的最高平均值 |
| DCUNET | 3.500 | 质量相近但运行时计算约为 DCCRN-CL 的 6 倍 |

### 4.3 DNS Challenge：质量不能只看一个 PESQ

![[wiki_low_latency/assets/2008.00264/2008.00264-page4-results.png]]

图 2（原论文第 4 页页面渲染）：WSJ0 PESQ 表、DNS simulated PESQ 表和 blind-test MOS 表；视觉核对了 DCCRN-E、DCCRN-E-Aug、DCCRN-CL 的 track 与 look-ahead 列。

DNS simulated test 的 Table 2 中，DCCRN-E [T1] 的 no-reverb/reverb/average PESQ 为 3.266/3.077/3.171；DCCRN-E-Aug [T2] 为 3.209/3.219/3.214。DCCRN-CL 的平均 PESQ 为 3.181。DNS blind test 中，最终实时 track 选择 DCCRN-E，论文报告 average MOS 3.42、no-reverb MOS 4.00；DCCRN-CL 虽然在模拟 PESQ 上更高，但作者主观听感发现部分片段存在 speech over-suppression。

### 4.4 延迟与复杂度账本

| 账本项 | 论文证据 | 本 Wiki 判定 |
|---|---|---|
| 因果类型 | encoder 沿时间维补零；decoder 每层 look ahead 1 frame | semi-causal；按本 Wiki 严格定义为 non_causal |
| look-ahead | 6 frames × 6.25 ms = 37.5 ms | 满足 DNS 40 ms 规则，不满足约 2 ms strict-causal |
| look-back（过去视野） | encoder 沿时间维零补（kernel=2、stride=1），约 6 层各回看 1 帧 ≈ 6 帧 × 6.25 ms ≈ 37.5 ms；瓶颈 LSTM 单向，state 还可携带更早全部历史 | 卷积回看为固定有限窗；LSTM 为无界软记忆；二者都不读取未来帧 |
| 单帧计算 | DCCRN-E 约 3.12 ms，Intel i5-8250U、PyTorch/ONNX 参考 | 仅是单机 wall-clock，不是端到端 p99 |
| 参数量 | DCCRN 系列约 3.7M | 轻量，但论文未给绝对 MAC/s、峰值 RAM、量化精度 |
| deadline | 未报告 I/O buffer、ADC/DAC、capture-to-playback、p50/p95/p99 或 deadline miss | 不能由 RTF 或单帧平均时间替代 |

## 5. 这个方向还剩什么问题没解决？（future work / limitation）

1. **前端和 decoder 仍然过长。** 37.5 ms look-ahead 是 DNS 规则下的实时，而不是约 2 ms 的严格因果；要迁移到本方向，需要重新设计短窗 STFT、缓存、decoder 对齐和 overlap-add。
2. **质量指标没有专门证明人声保留。** 论文给出 PESQ、STOI 和 MOS，但没有 false-suppression、低 SNR voiced/unvoiced 分层、F0/formant/prosody continuity 或 ASR WER。
3. **混响鲁棒性不足。** blind test 的 reverb 条件明显低于 no-reverb；额外 RIR 增强只带来有限改善，需把混响与低时延前端联合评估。
4. **complex LSTM 的收益/代价没有被端侧指标完整拆开。** 论文给了参数量和单帧时间，但没有目标 SoC 上的 MAC/s、峰值内存、功耗、量化后质量和长流状态 reset 证据。
5. **复数网络的迁移边界仍开放。** complex Conv/CRM 可作为相位增强或多通道空间滤波的候选模块，但跨通道 IPD 保真、定位误差和增强—定位联动尚未在这篇论文中验证。

## 6. 本论文在库中的位置关联（cross-reference matrix）

| 关系维度 | 关联页面 | 本论文的位置 |
|---|---|---|
| 上游骨架 | [[wiki/entities/Conv-TasNet|Conv-TasNet]]、CRN | 从卷积循环 encoder-decoder 出发，引入复数域操作 |
| 同期相位路线 | [[wiki/sources/2020/PHASEN 2020]] | PHASEN 采用双流交互，DCCRN 采用复数统一；两者代表不同的相位建模哲学 |
| 后续双路径 | [[wiki_low_latency/sources/2021/DPCRN Low-Latency Direction 2021]] | 将复数 CRN 与 DPRNN 的块内/块间长上下文结合 |
| 复数滤波 | [[wiki_low_latency/sources/2022/DeepFilterNet2 2022]] | 从单点 mask 走向多阶深度复数滤波，并面向嵌入式实时 |
| 子带/全带路线 | [[wiki_low_latency/sources/2023/FSB-LSTM 2023]] | 以 full-band/sub-band 协同换取低复杂度与长程频带建模 |
| 本 Wiki 目标对照 | [[wiki_low_latency/sources/2022/STFT-Domain Very Low Algorithmic Latency 2022]]、[[wiki_low_latency/sources/2023/GCFSnet 2023]] | DCCRN 的复数质量路线可借鉴，但 37.5 ms look-ahead 不是 2 ms strict-causal 证据 |

## 7. 一句话总结“江湖地位”

> **DCCRN 是 2020 年把“复数运算”系统化带入轻量语音增强 CRN 的方法基准：约 3.7M 参数、WSJ0 平均 PESQ 最高 3.498，并在 DNS 实时赛道取得有竞争力的主观结果；它证明了 real/imag 的代数耦合有价值，但 37.5 ms look-ahead、混响下的退化、过抑制以及缺少端到端 p99，使它更适合作为相位建模/教师模型参照，而不是本 Wiki 约 2 ms strict-causal 的最终方案。**

