---
title: PercepNet - 感知导向的全带实时语音增强
type: source
created: 2026-09-16
updated: 2026-09-16
tags:
  - speech-enhancement
  - perceptual-modeling
  - fullband
  - real-time
  - low-complexity
  - pitch-filtering
  - envelope-postfilter
  - non-causal
  - 48khz
  - algorithmic-latency
  - look-ahead
source_type: paper
year: 2020
authors: Jean-Marc Valin; Umut Isik; Neerad Phansalkar; Ritwik Giri; Karim Helwani; Arvindh Krishnaswamy
venue: arXiv preprint
arxiv: https://arxiv.org/abs/2008.04259
local_pdf: raw/papers/low_latency_causal_se/2008.04259.pdf
related:
  - [[wiki_low_latency/entities/PercepNet]]
  - [[wiki_low_latency/concepts/2008.04259-perceptual-speech-preservation]]
  - [[wiki_low_latency/sources/2023/FSB-LSTM 2023]]
  - [[wiki_low_latency/sources/2023/GCFSnet 2023]]
  - [[wiki/sources/2018/RNNoise 2018]]
  - [[wiki/concepts/Pitch滤波器]]
  - [[wiki/concepts/感知加权损失函数]]
  - [[wiki/concepts/实时与离线语音增强]]
---

~~~yaml
- 论文: [A Perceptually-Motivated Approach for Low-Complexity, Real-Time Enhancement of Fullband Speech](2020)
  ├── 要解决什么问题: 在 48 kHz 全带语音上以很低的 CPU/模型复杂度做实时增强，同时保留人耳更敏感的谱包络和周期性
  ├── 核心方法: 34 个 ERB 感知频带的增益估计 + 基于音高的 comb filtering + envelope postfilter；DNN 只预测感知参数而非所有 STFT bin
  ├── 属于哪个分支: 感知参数化 / 全带实时语音增强 / 低复杂度 DSP-DL 混合；整体为 non-causal look-ahead 系统
  ├── 输入/输出: noisy waveform y(n) → 20 ms Vorbis-window STFT、70 维 band/pitch 特征 → 34 个 gain 与 34 个 pitch-filter strength → enhanced waveform x̂(n)
  ├── 关键trick: 把目标改写为谱包络 + 频率相关 periodic-to-stochastic ratio；让网络学习 pitch filtering strength，并用 envelope postfilter 补偿听感
  ├── 前端/延迟: 48 kHz；20 ms 分析/合成窗、50% overlap、10 ms hop；Figure 1 明示最多 40 ms look-ahead，故不是 strict-causal
  ├── 数据集: 120 h、48 kHz clean speech（>200 speakers、>20 languages）+ 80 h 多种噪声；SNR -5 到 45 dB，含噪声-free 样本；模拟/实测 RIR
  ├── 对比了谁: Noisy、SEGAN、RNNoise (original)、PercepNet 消融、DNS challenge baseline
  ├── 性能上限: VCTK 48 kHz 内测 MOS(P.808)=4.05、PESQ-WB=2.54；DNS challenge overall MOS=3.52
  ├── 参数量: 约 8M weights、8-bit 权重；10 ms frame 约 800 MMACS，5.2% mobile x86 core；40 ms 处理四个内部帧时 4.1%
  ├── 消融关键发现: VCTK 主观 MOS 从 no pitch/no postfilter 的 3.81 提升到完整 PercepNet 的 4.05；PESQ-WB 对 envelope postfilter 的排序相反，说明指标与听感不完全一致
  ├── 遗留问题(你的机会): 40 ms look-ahead、acausal comb taps、无 RTF/p99/deadline/capture-to-playback；无 speech false-suppression、ASR WER、F0/formant/prosody continuity
  └── 跟哪篇像: [[wiki/sources/2018/RNNoise 2018]]、[[wiki_low_latency/sources/2023/FSB-LSTM 2023]]、[[wiki_low_latency/sources/2023/GCFSnet 2023]]、[[wiki/sources/2023/DeepFilterNet 2023]]
~~~

# A Perceptually-Motivated Approach for Low-Complexity, Real-Time Enhancement of Fullband Speech

> Jean-Marc Valin, Umut Isik, Neerad Phansalkar, Ritwik Giri, Karim Helwani, Arvindh Krishnaswamy，Amazon Web Services；arXiv:2008.04259v2，27 Aug 2020。  
> 本页只摄取本地 PDF `raw/papers/low_latency_causal_se/2008.04259.pdf`；venue 未在该本地 PDF 中单独报告。

> [!warning] PDF 转换质量与阅读说明
> 摄取对象是 `raw/papers/low_latency_causal_se/2008.04259.pdf`（5 页）；已对该文件的五页渲染结果做视觉核对，并复用第 1 页与第 4 页原页资产。
> 原 PDF 共 5 页。Poppler 渲染时报告 No display font for 'Symbol' 与 No display font for 'ArialUnicode'；页面 PNG 仍清晰可读。pypdf 抽取文本存在 fi/fl 连字、上下标/撇号扁平化、希腊字母与部分公式排版丢失等问题，尤其是 Figure 1-4 和 Eq. (1)-(16) 不应只依赖抽取文本。下文公式、图表数字和架构标签均以原 PDF 页面视觉核对为准。

## 1. 他们为什么这么做？（motivation）

### 1.1 任务与对象

论文研究的是**全带（fullband，48 kHz）实时语音增强**。输入是 hands-free microphone 捕获的干净语音、房间响应和环境噪声的混合；目标不是逐采样复原所有细节，而是构造一个在听感上接近干净语音的增强信号。

论文的信号模型为：

$$
y(n)=x(n)\star h(n)+\eta(n). \tag{1}
$$

- $x(n)$：干净语音；
- $h(n)$：说话人到麦克风的 impulse response；
- $\eta(n)$：房间中的加性噪声；
- $y(n)$：观测到的 noisy speech；$\star$ 表示卷积。

论文进一步把干净语音分成局部周期成分与随机成分：

$$
x(n)=p(n)+u(n),\qquad \hat{x}(n)=\hat{p}(n)+\hat{u}(n).
$$

$p(n)$ 是 locally periodic component，$u(n)$ 是 stochastic component；transient（例如 stop）在本文中也归入 stochastic component。PercepNet 试图让 $\hat{x}(n)$ 在感知上接近 $x(n)$，而不是强行精确分离 $u(n)$ 与环境噪声。

### 1.2 为什么要从“重建所有频点”转向“感知参数”

论文指出，许多深度增强器直接在 STFT 域估计 magnitude、IRM 或 complex ratio mask，需要较多 neurons/weights；这既抬高复杂度，也解释了不少方法只覆盖 8/16 kHz。STFT 窗长还存在冲突：

- 长窗具有较好频率分辨率，但可能产生 musical noise 与 reverb-like time smearing；
- 短窗具有较低时间模糊，但难以解析 pitch harmonics 之间的噪声；
- complex mask 或 time-domain processing 可以缓解部分问题，却通常进一步增加复杂度。

PercepNet 的动机是只建模两类对人耳最重要的属性：**spectral envelope** 与 **frequency-dependent periodic-to-stochastic ratio**。论文据此把全带频谱压到符合听觉分辨率的 ERB bands，再把 pitch filtering 和后滤波交给轻量 DSP/DNN 组合。目标是 48 kHz 增强仍能在很小的 CPU 预算下工作。

### 1.3 论文系统总览（PDF 第 1 页）

![[wiki_low_latency/assets/2008.04259/2008.04259-page1-overview-lookahead.png]]

> 图注：原 PDF 第 1 页 Figure 1 与 Figure 2 的页面渲染。Figure 1 明示当前合成窗需要使用最多 $t=40$ ms 的未来样本来生成 $t=0$ 之前的输出；Figure 2 展示 STFT、pitch analysis/filtering、DNN、envelope postfilter、scale bands 和 iSTFT 的管线。该资产是 PDF 原页渲染，不是 AI 重画。

### 1.4 任务、输入输出与目标摘要

| 维度 | PDF 明确内容 |
|---|---|
| 任务 | noisy speech enhancement；包含模拟/实测房间响应，目标保留 early reflections、抑制 late reverberation |
| 采样率 | 训练与主要评测为 48 kHz；DNS challenge 的 16 kHz 数据在 STFT 域内部 upsample/downsample |
| 信号域 | waveform 输入/输出，中间为 STFT 与感知 band 表示 |
| 分析/合成 | 20 ms window、50% overlap、Vorbis window；10 ms internal frame |
| 输入特征 | 34 个 ERB band 的 look-ahead magnitude + 无 look-ahead pitch coherence，加 pitch period 与 pitch correlation，共 70 维 |
| DNN 输出 | 每个 band 一个 $\hat g_b$ 与一个 $\hat r_b$，共 34 gains + 34 pitch-filter strengths |
| 最终输出 | 经 gain、pitch filtering、envelope postfilter、minimum decay、high-pass 后，再由 iSTFT 得到增强波形 |
| 低时延标签 | non_causal；PDF 明示 40 ms look-ahead，不能归入 strict-causal/约 2 ms 合格系统 |

## 2. 之前的人怎么做不了？（limitation → gap）

### 2.1 既有路线的限制

| 路线 | 能力 | 对本问题的限制 |
|---|---|---|
| spectral subtraction / spectral estimation | 复杂度较低，历史悠久 | 论文指出深度学习方法已在质量上超过它们 |
| STFT magnitude 或 IRM DNN | 可直接估计频谱增强量 | 需要较多神经元和权重；不少系统受限于 8/16 kHz |
| complex ratio mask / time-domain 网络 | 可处理相位或短窗波形信息 | 论文将其描述为进一步增加复杂度的路线 |
| 仅按频点建模 | 频率分辨率高 | 不匹配人耳对谱包络和音调/噪声的感知分辨率，计算量也更大 |
| RNNoise 路线 | 已经提供低复杂度实时增强与 pitch comb filter 基线 | 本文目标是继续提升感知质量，并把 pitch filtering strength 从 heuristic 改为学习 |

### 2.2 从 limitation 到 gap

论文要填的 gap 可以压缩为：

> **怎样在不为每个 STFT bin 预测大规模时频掩蔽的前提下，用人耳相关的频率分辨率和周期性描述，完成 48 kHz fullband enhancement，并把 CPU/内存/带宽开销压到实时可用？**

PercepNet 的回答是把网络输出限制为 34 个 band gains 与 34 个 pitch-filter strengths，再用可解释的 DSP 结构完成频域缩放、周期性重建、包络后滤波和 iSTFT。

### 2.3 严格因果与 latency ledger

| 账本项目 | PDF 明确证据 | 本 Wiki 判定/证据边界 |
|---|---|---|
| 系统标签 | Abstract 与 Figure 1 都写明 40 ms look-ahead | non_causal；不是 strict-causal |
| 采样率 | 48 kHz fullband；同一模型也用于 DNS 的 16 kHz 评测 | 支持 bandwidth-independent claim，不代表低算法延迟 |
| STFT 窗与 hop | 20 ms analysis/synthesis window、50% overlap；即 10 ms frame/hop | 窗长与 overlap 明确；group delay 未单独报告 |
| 最新可读输入样本 | Figure 1 说明为了计算输出直到 $t=0$，使用样本到 $t=40$ ms | 论文级 look-ahead 证据；不是端到端 capture-to-playback |
| DNN 时间上下文 | 1x5 与 1x3 convolution 在时间上对齐，使用最多 $M$ 个未来帧；$M=3$ 以实现含 10 ms overlap 的 40 ms look-ahead | 明确 future observation；整体非因果 |
| DNN 特征 | band magnitude 使用 $Y_b(\ell+M)$；pitch coherence 估计本身使用 full look-ahead | 未来样本进入特征支路；不能称 online-only |
| pitch comb filter | $C_M(z)=\sum_{k=-M}^{M}w_kz^{-kT}$，包含 negative/positive time taps；实际按允许 look-ahead 截断 | 非因果 taps 是第二个独立的 future-context 来源 |
| GRU 状态 | 使用 GRU layers，但 PDF 未给出逐层 state cache、reset 或最后可读样本证书 | 无法据此生成 strict-causal certificate；但即使 GRU 是单向，整机仍非因果 |
| warm-up / state reset | 未报告 | 未报告 |
| I/O buffer、ADC/DAC、capture-to-playback | 未报告 | 未报告 |
| 模型 RTF | 未给出 RTF 数值；只给 CPU core 占用 | RTF: 未报告；CPU 百分比不是 deadline 证明 |
| p50/p95/p99、deadline miss、underrun/overrun | 未报告 | 未报告 |
| 40 ms evaluation batch | 用 40 ms frame size 处理 4 个内部 10 ms frames 以改善 cache efficiency | 这是测量吞吐的 batch 方式，不是 strict-causal 或端到端 latency 证书 |

> [!question] 低时延证据边界
> PercepNet 的“real-time”是 CPU 上的运行效率主张，不是约 2 ms hearing-aid 算法时延主张。PDF 直接支持约 40 ms look-ahead、非因果 comb filtering 和指定 CPU 上的实时运行；它没有提供目标设备的 RTF、deadline 通过率、p99、I/O/ADC/DAC 或 capture-to-playback。

> [!note] 符号复用
> 论文在不同小节复用了 $M$：Eq. (4) 中 $M=5$ 表示 central tap 两侧的 pitch periods；DNN 小节中 $M=3$ 表示用于时间对齐的未来帧数。两者不是同一个超参数。

## 3. 这个做法核心 trick 是什么？

### 3.1 Trick A：用 ERB 感知频带代替逐频点输出

论文把 0-20 kHz 表示为 34 个按 human hearing equivalent rectangular bandwidth（ERB）布置的 bands，并施加至少 100 Hz 的最小 band width，避免一个 band 只含一个 DFT bin。对第 $b$ 个 band、帧 $\ell$，论文记该 band 的 complex spectrum 为 $x_b(\ell)$，其 $L_2$-norm 为 $X_b(\ell)$；对应 noisy band 量记为 $Y_b(\ell)$。

从 noisy magnitude 计算理想 band gain：

$$
g_b(\ell)=\frac{X_b(\ell)}{Y_b(\ell)}. \tag{2}
$$

这个 gain 只要求增强 band 的 total energy 接近干净 speech。若语音主要是 stochastic component，能量匹配可能已经足够；若语音高度 periodic，同样能量却可能留下 pitch harmonics 之间的可听噪声，因此还需要 pitch filtering。

### 3.2 Trick B：用音高相关的 comb filter 补足 STFT 频率分辨率

论文用 correlation-based pitch estimator 加 dynamic-programming search 估计 pitch period $T$。简单的两 tap comb filter 为：

$$
C^{(0)}(z)=\frac{1+z^{-T}}{2}. \tag{3}
$$

它在周期性间隔引入 zeros，并把 noisy component 约压低 3 dB。PercepNet 把它扩展到多周期、含非因果 taps 的 filter：

$$
C_M(z)=\sum_{k=-M}^{M}w_k z^{-kT},\qquad
\sum_{k=-M}^{M}w_k=1. \tag{4}
$$

- $T$：估计的 pitch period；
- $M$：central tap 两侧使用的 period 数；
- $w_k$：窗函数权重；论文采用 Hann window，而非最小 $\sigma_w^2$ 的 rectangular window；
- noisy component 的衰减量写为：

$$
\sigma_w^2=\sum_{k=-M}^{M}w_k^2.
$$

论文在 $M=5$ 时按其 dB 口径给出 $\sigma_w=-9$ dB，并在第 2 页 Figure 3 展示 pitch=200 Hz 时提议 filter 与 RNNoise filter 的频响。实际运行时，超过 look-ahead 预算的 $w_k$ taps 会被截断。

这里的 $M$ 仅指 comb filter 的 pitch-period 范围；论文后文 DNN 时间上下文再次使用 $M$，其取值为 $3$，语义不同。

### 3.3 Trick C：让 DNN 学习每个 band 的 pitch-filtering strength

仅使用全强度 comb filter 会在低噪声处过度处理并产生 robotic voice；过滤不足又会留下 roughness。论文因此定义 clean speech 与 periodic component 的 pitch coherence：

$$
q_x\triangleq
\frac{\mathop{\rm Re}\left[p^H x\right]}
{\lVert p\rVert\cdot\lVert x\rVert}. \tag{5}
$$

noisy speech 的 coherence 记为 $q_y$。考虑 $\hat p$ 中 noise 被 $\sigma_w^2$ 衰减，估计周期成分的 coherence 为：

$$
q_{\hat p}=
\frac{q_y}
{\sqrt{(1-\sigma_w^2)q_y^2+\sigma_w^2}}. \tag{6}
$$

定义 pitch filtering strength $r\in[0,1]$，并构造：

$$
z=(1-r)y+r\hat p.
$$

$r=0$ 表示不做 filtering，$r=1$ 表示以 $\hat p$ 替代输入。理想情况是让 $z$ 与 clean speech 的 coherence 相同：

$$
q_z=
\frac{p\cdot\left((1-r)y+r\hat p\right)}
\lVert p\rVert\cdot\lVert(1-r)y+r\hat p\rVert
=q_x. \tag{7}
$$

解得：

$$
r=\frac{\alpha}{1+\alpha}, \tag{8}
$$

$$
\alpha=
\frac{\sqrt{b^2+a(q_x^2-q_y^2)}-b}{a},
\quad
a=q_{\hat p}^2-q_x^2,
\quad
b=q_{\hat p}q_y(1-q_x^2). \tag{9}
$$

当 $q_{\hat p}<q_x$ 时，论文令 $r=1$，并使用 attenuation gain：

$$
g^{(\mathrm{att})}
=\sqrt{\frac{1+n_0-q_x^2}{1+n_0-q_{\hat p}^2}},
\qquad n_0=0.03\ \text{（论文标为 15 dB）}. \tag{10}
$$

正常情形 $q_{\hat p}\ge q_x$ 时，$g^{(\mathrm{att})}=1$。这些含 clean-speech coherence 的公式只在 training target 计算时使用；推理阶段由 DNN 估计每个 band 的参数。

### 3.4 DNN 架构、输入输出与量化

PDF 第 3 页 Figure 4 给出了从 70 维输入 $f$ 计算 34 gains $\hat g_b$ 和 34 strengths $\hat r_b$ 的网络。图中主干/分支可读为：

~~~text
70-dim f
  → FC(128)
  → Conv(1×5, 512)
  → Conv(1×3, 512)
       ├─ 4× GRU(512) → FC(34) → ĝ_b
       └─ GRU(128)    → FC(34) → r̂_b
~~~

输入特征为：

- 每个 ERB band 的两个特征：look-ahead magnitude $Y_b(\ell+M)$ 与 no-look-ahead pitch coherence $q_{y,b}(\ell)$；coherence estimation 本身使用 full look-ahead，共 $34\times2=68$ 维；
- pitch period $T(\ell)$；
- 带 look-ahead 的 pitch correlation estimate；
- 合计 70 维。

输出为：

$$
\hat g_b(\ell)\approx g_b^{(\mathrm{att})}(\ell)g_b(\ell),
\qquad
\hat r_b(\ell)\approx r_b(\ell).
$$

卷积在时间轴上对齐以使用最多 $M=3$ 个未来帧；这与 Figure 1 的 40 ms look-ahead 一致。模型权重被限制在 $\pm\frac12$ 范围并量化为 8-bit integer，用于减少 memory/bandwidth 和利用 vectorization；PDF 没有给出 bias、激活或完整定点部署规格。

### 3.5 Trick D：感知加权 loss，而非普通 band MSE

论文用 $\gamma=0.5$ 的 power-law loudness 近似感知响度。gain loss 为：

$$
\mathcal{L}_g=
\sum_b\left(g_b^\gamma-\hat g_b^\gamma\right)^2
+C_4\sum_b\left(g_b^\gamma-\hat g_b^\gamma\right)^4,
\qquad C_4=10. \tag{11}
$$

第四次方项用来额外惩罚大误差，例如完全误抑制 speech。pitch-filter strength loss 为：

$$
\mathcal{L}_r=
\sum_b
\left((1-r_b)^\gamma-(1-\hat r_b)^\gamma\right)^2. \tag{12}
$$

论文认为 $\hat r_b$ 的误差对最终增强不如 gain 敏感，因此不在 $\mathcal L_r$ 中加第四次方项。作者还说明 Eq. (11) 隐含了 scale-invariance、SNR-invariance、power-law compression 与非线性频率分辨率。

### 3.6 Trick E：envelope postfilter 与最小衰减

为进一步清理 noisy bands，论文把 DNN gain warp 为：

$$
\hat g_b^{(w)}
=\hat g_b\sin\left(\frac{\pi}{2}\hat g_b\right). \tag{13}
$$

clean bands 基本不变，very noisy bands 的增益近似被平方。随后用全局能量补偿：

$$
G=
\sqrt{
\frac{(1+\beta)E_0/E_1}
{1+\beta(E_0/E_1)^2}
},
\qquad \beta=0.02, \tag{14}
$$

其中 $E_0$ 是使用原始 $\hat g_b$ 的增强信号总能量，$E_1$ 是使用 warped gain 后的总能量。论文称 $\beta=0.02$ 对 clean bands 的最大理论增益为 5.5 dB。band energy 为：

$$
\hat X_b=G\hat g_b^{(w)}Y_b. \tag{15}
$$

为避免耳机播放时声音过干，论文再强制一个等效 $T_{60}=100$ ms 的最小能量衰减，并且不允许超过 noisy speech 能量：

$$
\hat X_b^{(r)}(\ell)=
\min\left(
\max\left(\hat X_b(\ell),\delta\hat X_b^{(r)}(\ell-1)\right),
\hat Y_b(\ell)
\right). \tag{16}
$$

最后回到时域后应用 high-pass filter；cutoff 由估计的说话人 pitch 决定，以免削弱 fundamental。

### 3.7 哪一个 idea 最关键？

PercepNet 不是把十个大型模块叠在一起，而是把问题坐标系改成“谱包络 + 周期性 + 感知响度”。其中最关键的结构性 trick 是：

1. 让网络只预测 34-band gain 与 34-band pitch strength；
2. 让 pitch-filtering strength 从启发式变成每 band 的学习量；
3. 用可解释的 postfilter 对 DNN 输出做小幅感知校正。

ERB bands 负责降维和感知对齐，comb filter 负责超越 20 ms STFT 的频率分辨率；两者的组合才是 fullband 低复杂度的核心。

## 4. 实验里哪个消融最关键？

### 4.1 数据、合成与训练设置

论文用 synthetic clean/noise mixtures 训练，SNR 范围为 -5 到 45 dB，另含 noise-free examples：

- clean speech：120 小时、48 kHz，来自多个 public/internal databases，超过 200 speakers、超过 20 languages；
- noise：80 小时、多种 noise types、48 kHz；
- reverb：noisy signal 与 simulated 和 measured room impulse responses 卷积；target 包含 early reflections，因此重点衰减 late reverberation；
- 泛化增强：对 speech 与 noise 各施加不同 random second-order pole-zero filter；对两者施加相同 random spectral tilt；再施加 3-20 kHz random-cutoff low-pass filter，使同一模型覆盖 narrowband 到 fullband。

PDF 没有报告 optimizer、learning rate、batch size、epoch、scheduler、random seed、训练硬件、代码仓库或 commit。这里均记为**未报告**，不从其他来源补齐。

### 4.2 评价协议与指标

论文主要使用两组 crowdsourced P.808 mean opinion score（MOS）测试：

1. **VCTK 内部测试**：48 kHz noisy VCTK test set，824 samples，每个 sample 由 8 listeners 评分，95% confidence interval 为 0.04；PESQ-WB 作为与其他方法比较的参考。
2. **DNS challenge 官方测试**：150 个无混响 synthetic、150 个有混响 synthetic、300 个 real recordings；每个 sample 由 10 listeners 评分，95% confidence interval 为 0.02。16 kHz challenge data 在 STFT 域内部 upsample/downsample，以避免额外 algorithmic delay；同一组模型参数用于 16/48 kHz。

PDF 没有报告 STOI/eSTOI、SI-SDR/SI-SNR、DNSMOS、ASR WER、VAD false-suppression、F0/formant/prosody continuity 或听障受试者测试。因此 MOS/PESQ-WB 只能支撑整体质量与主观听感结论，不能单独证明人声细节无误抑制。

### 4.3 关键消融：pitch filtering 与 envelope postfilter（Table 1，第 4 页）

| Algorithm | PESQ-WB | MOS (P.808) |
|---|---:|---:|
| Noisy | 1.97 | 3.40 |
| SEGAN | 2.16 | 未报告 |
| RNNoise (original) | 2.29 | 3.70 |
| PercepNet (no pitch, no pf) | 2.64 | 3.81 |
| PercepNet (no pf) | 2.73 | 3.91 |
| PercepNet (no pitch) | 2.47 | 3.93 |
| PercepNet | 2.54 | **4.05** |

pf 指 envelope postfilter。按 P.808 主观 MOS 看，完整 PercepNet 高于去掉两者的版本（4.05 vs 3.81），且 pitch filtering 和 postfilter 分别加入后都带来提升。值得保留的反常点是：PESQ-WB 并不跟随该主观排序，完整模型 2.54 低于 no pf 的 2.73；论文明确用此说明 PESQ-WB 对 envelope postfilter 的局限。

### 4.4 外部 blind challenge 结果（Table 2，第 4 页）

| Algorithm | Synthetic w/o reverb | Synthetic w/ reverb | Real record | Overall |
|---|---:|---:|---:|---:|
| Noisy | 3.32 | 2.78 | 2.97 | 3.01 |
| Baseline | 3.49 | 2.64 | 3.00 | 3.03 |
| PercepNet | **3.92** | **3.16** | **3.51** | **3.52** |

相对 challenge baseline，PercepNet 的 overall MOS 为 3.52 vs 3.03；在 synthetic without reverb、synthetic with reverb、real recordings 三列均更高。该表支持“在该 challenge 协议下总体主观质量更好”，不支持“在所有噪声类型、所有硬件和所有低时延预算下都更好”。

### 4.5 结果页与图表证据

![[wiki_low_latency/assets/2008.04259/2008.04259-page4-results-complexity.png]]

> 图注：原 PDF 第 4 页 Table 1、Table 2 及其相邻的实验/复杂度正文。该页用于核对所有 MOS/PESQ-WB 数字、测试样本量/置信区间上下文以及 8M weights、800 MMACS、5.2%/4.1% CPU 结果；这是原 PDF 页面渲染，不是 AI 重画。

### 4.6 复杂度、实时与 deadline 证据边界

| 项目 | PDF 精确结果 | 可推出的结论 |
|---|---|---|
| 权重数 | 约 8M weights | 模型不属于极小参数量路线；PDF 未给完整模型文件大小/RAM |
| 权重量化 | 权重限制在 $\pm 1/2$，8-bit integers | 说明考虑 memory/bandwidth/vectorization；未证明完整 fixed-point 部署 |
| 理论复杂度 | 10 ms frame、8M weights 时约 800 MMACS；论文按每个 weight 每 frame/second 一次 MAC 解释 | 可作模型计算预算；不是目标设备 deadline |
| 10 ms frame runtime | 1.8 GHz Intel i7-8565U mobile x86 的一个 CPU core 使用 5.2% | 论文级实时运行证据；没有 RTF 数值 |
| 40 ms frame runtime | 处理 4 个内部 10 ms frames 以改善 cache efficiency；同一输出，CPU 降至同一 core 的 4.1% | 支持该 CPU 上的吞吐优化；不改变 40 ms look-ahead |
| DNS real-time track | 论文称复杂度远低于 challenge 上限，PercepNet 在 real-time track 排名第二 | 只支持 challenge 环境中的运行效率/排名 |
| RTF、p50/p95/p99、deadline miss、功耗 | 未报告 | 不能把 4.1% CPU 或“real-time”改写为端侧 p99 deadline 通过 |

### 4.7 噪声抑制与人声保留的证据审计

| 审计目标 | PDF 直接支持 | 不能从本文推出 |
|---|---|---|
| 噪声抑制 | P.808 MOS 在 VCTK 与 DNS challenge 上优于 noisy/baseline；ERB bands 使算法不能产生 musical noise | 分噪声类型的 BAK/残余噪声曲线、低 SNR 分层、noise-only 指标 |
| 人声保留 | 频带能量、周期性和主观 MOS 改善；gain loss 的四次方项特别惩罚大误差 | false-suppression、弱辅音/气声/音节边缘、F0/formant/prosody continuity、ASR WER |
| 伪影 | 短窗避免 reverb-like smearing；主要可听伪影是 pitch harmonics 之间残留噪声造成的 roughness，尤其是 loud car noise | 不能宣称所有噪声类型均无伪影或所有语音细节均保真 |

## 5. 这个方向还剩什么问题没解决？（future work / limitation）

### 5.1 PDF 直接暴露的限制

1. **40 ms look-ahead 与 acausal comb filter**：PercepNet 的总体延迟远高于约 2 ms hearing-aid 目标；它是 real-time throughput 系统，不是 strict-causal low-latency 系统。
2. **主观质量与 PESQ-WB 不一致**：envelope postfilter 提升 P.808 MOS，却使 PESQ-WB 由 2.73（no pf）降到 2.54（完整 PercepNet）；单一 objective metric 不能代表该设计的听感收益。
3. **仍有残余 roughness**：论文把 loud car noise 下 pitch harmonics 之间的残留噪声列为主要可听伪影。
4. **late reverb 目标选择**：训练 target 保留 early reflections，论文的结果不能被改写成完全 dereverberation。
5. **模型部署细节不全**：PDF 只给 8-bit 权重、8M weights 和 CPU 占用，没有给完整内存、能耗、bias/activation quantization、定点 C、state reset 或长流稳定性。

### 5.2 面向 wiki_low_latency 的隐藏 gap

1. 没有 ADC/DAC、I/O buffer、capture-to-playback、warm-up、underrun/overrun、p50/p95/p99 或 deadline miss。
2. 没有将 look-ahead、STFT 边界、comb-filter 截断、GRU cache 逐层写成 causal certificate；因此只能标 non_causal。
3. 没有按低 SNR 和 babble/竞争说话人/瞬态/未见噪声分层，也没有 SIG-BAK 或 speech-distortion trade-off。
4. 没有 false-suppression、VAD/SPP 校准、ASR WER 或 F0/formant/prosody continuity，无法单独量化“人声保留”。
5. “同一模型覆盖 16/48 kHz”通过 STFT 域 upsample/downsample 与随机低通增强得到，不能外推为在任意采样率、任意设备上都保持同一 latency/quality Pareto。
6. 8M weights 与 800 MMACS 在 mobile x86 上足以完成论文测试，但不是 hearing-aid SoC 的实测；目标硬件、编译器、SIMD 和内存带宽均未给出。

### 5.3 可检验的后续机会

- 固定 PercepNet 的感知 band/periodicity 表示，逐步减少 look-ahead，分别测试 comb taps、pitch feature 和 DNN temporal context 对质量的影响；
- 在单独的 strict-causal 版本中去掉 future magnitude 与 acausal taps，报告算法延迟、RTF、p50/p95/p99 和每个 hop 的 deadline miss；
- 将 P.808 MOS 与 SIG/BAK/OVL、VAD false-suppression、ASR WER、F0/formant/prosody continuity、低 SNR 分层一起报告；
- 对 8-bit weights、activation/bias quantization、蒸馏和目标 SoC 做统一 Pareto，而不是只报告 x86 CPU 百分比；
- 以 loud car、babble、竞争说话人和未见噪声为压力集，定位 pitch-harmonic roughness 与人声误抑制的失败样例。

## 6. 本论文在库中的位置关联（cross-reference matrix）

| 关系 | 库中页面 | 关联与差异 |
|---|---|---|
| 前身/基石 | [[wiki/sources/2018/RNNoise 2018]]、[[wiki/entities/RNNoise]] | 本地 PDF 第 1 页明确说 PercepNet improves on RNNoise，并在 Table 1 直接比较；PercepNet 延续低复杂度 DSP-DL 估计器，但把 band gain、感知 pitch filtering 和 envelope postfilter 组织得更明确 |
| 同文跨域条目 | [[wiki/sources/2020/PercepNet 2020]] | 同一论文的普通语音增强条目；本页补充 40 ms look-ahead、non-causal 审计、RTF/deadline 证据边界，避免把“real-time”当作 strict-causal |
| 同分支低时延对照 | [[wiki_low_latency/sources/2023/FSB-LSTM 2023]] | FSB-LSTM 以复数 STFT mapping 和 full/sub-band LSTM 处理单/多通道增强；与 PercepNet 的 40 ms look-ahead 不同，实验数据/指标也不可直接横比 |
| 同分支多通道/双耳对照 | [[wiki_low_latency/sources/2023/GCFSnet 2023]] | GCFSnet 将当前本侧多麦空间滤波与延迟跨耳特征结合；PercepNet 是单麦感知 band/DSP 路线，关注点和 causal ledger 不同 |
| 低复杂度时频竞品 | [[wiki/sources/2023/DeepFilterNet 2023]] | 都把低复杂度、复数/频域处理与实时部署放在目标中；PercepNet 的输出是 ERB band gains/periodicity，而非 deep filter，数字不能直接比较 |
| 频带分治类比 | [[wiki/sources/2021/FullSubNet 2021]]、[[wiki/concepts/全带与子带模型]] | PercepNet 的 34 ERB bands 是感知分辨率，不是 FullSubNet 的 full/sub-band neural decomposition；可作为“频率降维/局部结构保留”类比，但不是直接继承关系 |
| 概念链接：周期性 | [[wiki/concepts/Pitch滤波器]] | Eq. (3)-(10) 将 pitch period、coherence、comb filter 与 band strength 组合为可学习的周期性恢复支路 |
| 概念链接：损失 | [[wiki/concepts/感知加权损失函数]] | Eq. (11)-(12) 的 $\gamma=0.5$ power-law、L2+L4 gain loss 和 strength loss 是感知加权训练的具体实例 |
| 概念链接：前端/实时 | [[wiki/concepts/STFT与频谱图]]、[[wiki/concepts/实时与离线语音增强]] | 本文同时说明 20 ms STFT、50% overlap、40 ms future context 和 CPU throughput；可用于区分算法 look-ahead、RTF 与 deadline |

> [!question] 关联不确定性
> 本矩阵只用于本地 Wiki 导航。除本论文行内数字外，其他论文的数字、严格因果结论和“被超越”关系应以各自 source 页为准；不同数据集、采样率、参考目标和指标不应直接排序。

## 7. 一句话总结“江湖地位”

~~~text
2020 | 全带感知参数化实时语音增强 | 用 ERB 谱包络 + 周期性建模、可学习 pitch filtering 和 envelope postfilter，把 48 kHz 增强压到移动 x86 单核 4.1% → 继承 RNNoise 的低复杂度 DSP-DL 范式并成为感知建模基线；但 40 ms look-ahead 与 acausal taps 使它不属于严格约 2 ms 分支，后续低时延论文需补齐 RTF/deadline 与人声保留证据。
~~~

### 参考资料

- [Local PDF](../../../raw/papers/low_latency_causal_se/2008.04259.pdf)
- [[wiki_low_latency/entities/PercepNet]]
- [[wiki_low_latency/concepts/2008.04259-perceptual-speech-preservation]]
- [[wiki_low_latency/sources/2023/FSB-LSTM 2023]]
- [[wiki_low_latency/sources/2023/GCFSnet 2023]]
