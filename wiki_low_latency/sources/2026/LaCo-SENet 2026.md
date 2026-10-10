---
title: LaCo-SENet - 非对称时间 padding 实现可配置时延流式语音增强
type: source
created: 2026-09-20
updated: 2026-09-20
tags:
  - speech-enhancement
  - single-channel
  - streaming
  - causal-convolution
  - asymmetric-padding
  - configurable-latency
  - strict-causal
  - paper-claimed-causal
  - 12.5ms-algorithmic-latency
  - latency-quality-tradeoff
  - onnx-runtime
source_type: paper
year: 2026
authors: Yunsik Kim; Yoonyoung Chung
venue: arXiv preprint (cs.SD)
arxiv: https://arxiv.org/abs/2606.19688
local_pdf: raw/papers/low_latency_causal_se/2606.19688.pdf
evidence_policy: local_pdf_only
related:
  - [[wiki_low_latency/entities/LaCo-SENet]]
  - [[wiki_low_latency/concepts/2606.19688-latency-configurable-asymmetric-padding]]
  - [[wiki_low_latency/concepts/2204.09911-short-asymmetric-stft]]
  - [[wiki_low_latency/concepts/严格因果与算法延迟]]
  - [[wiki_low_latency/concepts/低时延前端与延迟账本]]
  - [[wiki_low_latency/entities/DeepFilterNet2]]
---

~~~yaml
- 论文: [Latency-Configurable Streaming Speech Enhancement via Asymmetric Temporal Padding](2026)
  ├── 要解决什么问题: 现有流式增强把时延当成「因果 or 非因果」的二元选择，每篇论文锁死在一个时延点上，无法在同一架构与同一参数预算内系统扫描时延-质量权衡
  ├── 核心方法: 固定总 padding Ptot 只改左右分配 (PL, PR)，用单个训练期超参数 r=(rL,rR) 把 1.37M 的 PrimeK-Net 骨干扫出 12.5–200 ms 一整族模型；配 dual-buffer streaming（state buffer + lookahead buffer）和 selective state update (SSU) 保证分块推理与全序列推理等价
  ├── 属于哪个分支: 单通道时频掩蔽增强 / 因果卷积流式 / 时延可配置架构（不是蒸馏、不是 SSM）
  ├── 输入/输出: noisy waveform → STFT 400/100/400 → power-law 压缩 (c=0.3) 的 magnitude+phase 双通道 X∈R^{2×T×F} → encoder/TS Blocks/双 decoder → magnitude mask M̂ 与 enhanced phase Φ̂ → 掩蔽+相位替换 → iSTFT + OLA
  ├── 关键trick: 把「未来上下文」从架构级常量降级为可扫的训练期旋钮；再用 ΠC(x)=x1:C 只把当前 chunk 帧写进 state，避免 lookahead 帧被回放两次
  ├── 数据集: VoiceBank+DEMAND @16 kHz，11,572 训练 / 824 测试语句，10 类噪声 × 四档 SNR
  ├── 对比了谁: RNNoise、GaGNet、DeepFilterNet3 (DFNet3)、aTENNuate 四个「时延可验证」的因果基线；PrimeK-Net 作非因果上界；SEMamba 与 xLSTM-SENet 因 encoder 非因果对称 padding 被判为时延不可确定而排除排名
  ├── 性能上限: 非因果 PrimeK-Net PESQ 3.61（1.41M）；本文对称参考 (rR=0.5) 3.47@200 ms；12.5 ms 全因果点 3.35（同参数预算下保留非因果上界的 93%）
  ├── 参数量: 全部配置恒为 1.37M（唯一例外：PrimeK-Net 参考 1.41M）
  ├── 消融关键发现: 关掉 SSU 后，凡是有 lookahead 的非对称配置 PESQ 全部崩到 noisy 基线 (1.97) 以下——1.86@25 ms、1.45@50 ms、1.39@75 ms，且随 lookahead 增大单调恶化；Ltot=0 时 SSU 是完全的 no-op（Δ=0.00）
  ├── 遗留问题(你的机会): 12.5 ms 里仍有 12.5 ms 是不可消除的 STFT center delay（W/2），不是 2 ms 级前端；C=1 时单线程 Xeon RTF 4.59，要 RTF<1 必须 C≥7–12，此时「算法时延+chunk 缓冲」已升到 ~56–88 ms；无目标 SoC p99 / RAM / 量化 / 功耗 / capture-to-playback / 负 SNR 人声保留 / ASR WER
  └── 跟哪篇像: [[wiki_low_latency/concepts/2204.09911-short-asymmetric-stft]]（把时延预算拆开调节，但拆的是 analysis/synthesis 窗，本文拆的是 conv padding）、[[wiki_low_latency/entities/DeepFilterNet2]]（lookahead 只从输入级进入、所有卷积保持纯因果，本文正是要突破这一限制）
~~~

# Latency-Configurable Streaming Speech Enhancement via Asymmetric Temporal Padding

> Yunsik Kim; Yoonyoung Chung（POSTECH 电子工程系 / Intus Co. Ltd.），arXiv:2606.19688v3 [cs.SD]，18 Aug 2026，共 5 页。代码：<https://github.com/yskim3271/LaCo-SENet>。
> 本页把论文的 "fully causal" 拆成**卷积骨干因果性**与**STFT 前端未来依赖**两笔账分别审计。

> [!warning] PDF 转换质量与阅读说明
> 原 PDF 共 5 页，PyMuPDF 文本抽取（`tmp/pdf_extract/2606.19688.txt`）可读性尚可，但有三类问题必须看原 PDF 核对：
> 1. **公式**：Eq. (2) 的求和下标（`ℓ∈E`、`ℓ∈Db`）与 max 算子、Eq. (4) 的拼接符号 `[s; x; 0]` 在纯文本里被拆散；Eq. (5) 的 $\Pi_C(x)=x_{1:C}$ 下标丢失。本页所有公式已用**第 2 页与第 3 页渲染图**逐条核对。
> 2. **表格**：Table 1 的 `±` 标准差、脚注 †/‡、以及 `Lenc/Ldec` 下标在文本抽取中错位。Table 1 已用**第 3 页渲染图**核对，Table 2 与 Figure 2/3 已用**第 4 页渲染图**核对。
> 3. **图**：Figure 1 的三个子图 (a)/(b)/(c) 在文本中完全丢失，只留下 caption；本页对 Figure 1 的描述全部来自**第 2 页渲染图**的实际看图结果（包括 "Time Stage (Causal)" 与 "Freq Stage (Non-Causal)" 两个方框标签）。
>
> 论文未报告的字段（目标 SoC p99、RAM/SRAM、量化、功耗、capture-to-playback、ASR WER、负 SNR 分层、竞争说话人、VAD/SPP 校准）在本页一律写为「未报告」，不作任何补写。

## 1. 他们为什么这么做？（motivation）

### 1.1 任务与对象

单通道流式语音增强：从 noisy waveform $x[t]\in\mathbb R$ 得到增强波形，面向电话、会议、助听器、端侧语音接口。论文把目标区间明确限定在 **10–80 ms**（p.1 §1）：「Within the 10–80 ms regime where most applications operate, quality generally improves with additional lookahead」。

输入表示不是原始复数谱，而是压缩后的双通道实数张量：

$$
X=\big[\ |X_{f,n}|^{c}\ ,\ \angle X_{f,n}\ \big]\in\mathbb R^{2\times T\times F},
$$

其中 $X_{f,n}=\operatorname{STFT}(x[t])$ 是复数谱，$c=0.3$ 是 power-law magnitude compression 指数，$T$ 是帧数、$F$ 是频点数。$\hat M\in\mathbb R^{T\times F}$ 是 magnitude mask、$\hat\Phi\in\mathbb R^{T\times F}$ 是增强相位，最终经「masking + phase replacement」重建谱，再过 iSTFT 与 OLA 输出。

> [!note] 与 RT-SEMamba 的输入口径差异
> [[wiki_low_latency/sources/2026/RT-SEMamba 2026]] 输入的是 uncompressed magnitude/phase 并输出复数谱 $\hat C=\hat M e^{j\hat P}$；LaCo-SENet 先在输入端做 $c=0.3$ 压缩，输出的是 mask + 相位替换。两者都在时频域、都做相位处理，但压缩位置与重建方式不同。

### 1.2 论文动机

论文的核心观察是：**时延被当成架构级的二元选择，而不是可调的设计变量。**

- 现有流式 SE 架构（DSP-DNN hybrid、复数卷积循环、感知深滤波、raw-waveform SSM、Mamba、xLSTM）「each is locked to a single latency point by its design, and none can systematically trade latency for quality within a single architecture and parameter budget」（p.1 §2）。
- 但「质量随 lookahead 提升」在同一区间内是连续的、可测量的（Figure 2）。于是真正缺的不是某个更好的时延点，而是**一个能在同一骨干、同一参数量下扫出整条 Pareto 曲线的机制**。

论文给出的答案是：把「未来上下文」从架构常量降级为一个训练期超参数。

## 2. 之前的人怎么做不了？（limitation → gap）

| 路线                                            | 做法                                                             | 为什么挡住了「可配置时延」                                                  |
| --------------------------------------------- | -------------------------------------------------------------- | -------------------------------------------------------------- |
| DeepFilterNet [7]                             | lookahead 通过一个**全局输入平移**提供，每个卷积仍保持纯因果                          | lookahead 只能在输入边界处固定注入，无法逐层重分配                                 |
| Cached convolution [11]                       | 把 symmetric padding 转成等价的固定输出延迟                                | lookahead 完全由 kernel size 决定，且刻意排除非对称 padding                  |
| FastWaveNet [10] / Denoiser [12]              | 缓存 past activation 替代零左填充                                      | 只解决过去上下文，未处理逐层右 padding 与状态的交互                                 |
| Emformer [13] / Stateful Conformer [14]       | 通过 segment masking / memory policy 给 attention 加 right-context | 面向 attention 架构，且**过去与未来上下文被分开处理**，没有考虑二者在逐层非对称 padding 下的相互作用 |
| 各类流式 SE 骨干（aTENNuate / SEMamba / xLSTM-SENet） | 各自锚定一个时延点                                                      | 架构与训练都锁死，无法在同一参数预算下扫描                                          |

论文的 gap 由此变得很具体：

> 逐层非对称 padding 在数学上只是把 $P_{\text{tot}}$ 重新分配，看起来平凡；但一旦放进 **chunk-based stateful streaming**，每一层 $P_R>0$ 都会把未来帧引入卷积窗，而「朴素地把所有帧缓存进 state」会让这些 lookahead 帧在下一个 chunk 里**再出现一次**（一次来自 state、一次来自新到达输入），输出被逐步污染。这个 state corruption 问题正是前人回避逐层非对称 padding 的真实原因。

论文对既有方法的评价很直接：「Both constraints deliberately preclude per-layer asymmetric padding, avoiding state corruption at the cost of latency flexibility.」（p.1 §2）

### 2.1 严格因果与延迟账本

> 审计口径：本表逐项给出 PDF 证据与本 Wiki 判定。判定三档为 `strict_causal` / `low_look_ahead` / `non_causal`。

| 审计项 | PDF 证据（页码/公式/图表） | 本 Wiki 判定 |
|---|---|---|
| STFT window | win/hop/fft = 400/100/400 samples @16 kHz，即 25.0/6.25/25.0 ms（p.3 §3.3.4） | `low_look_ahead`：Eq. (3) 显式把 $W/2=200$ samples $=12.5$ ms 计为 "STFT center delay"，即前端本身需要 12.5 ms 的未来样本 |
| hop | $h=100$ samples = 6.25 ms | 不是完整算法时延，但决定时延梯度的粒度：$\tau=12.5+6.25\,L_{\text{tot}}$ ms |
| encoder 逐层 padding | $P_L=\operatorname{round}(P_{\text{tot}}\cdot r_L)$、$P_R=P_{\text{tot}}-P_L$，Eq. (1)；$L_{\text{enc}}=\sum_{\ell\in E}P_R^{(\ell)}$，Eq. (2) | $r_R=0$ 时 `strict_causal`（无右侧访问）；$r_R>0$ 时 `low_look_ahead`，上界 $L_{\text{enc}}$ 帧 |
| decoder 逐层 padding | $L_{\text{dec}}=\max_{b\in\{\text{mask,phase}\}}\sum_{\ell\in D_b}P_R^{(\ell)}$，Eq. (2) | 与 encoder 同理；注意 mask/phase 双分支**并行**，故取 max 而非求和 |
| 时间轴卷积 | TS Block 的 time branch 重排为 $\mathbb R^{(NF')\times C_h\times T}$，CAB 与 GPKFFN「all employing causal convolutions」（p.3 §3.3.2）；第 2 页 Figure 1(a) 方框标注 "Time Stage (Causal)" | `strict_causal`（论文声明 + 结构证据；无逐层 padding certificate） |
| 频率轴卷积 | freq branch 重排为 $\mathbb R^{(NT)\times C_h\times F'}$，同样模块「non-causally, since the frequency axis carries no temporal ordering」；Figure 1(a) 标注 "Freq Stage (Non-Causal)" | 时间维度上仍 `strict_causal`（只访问当前帧的整个频率轴），但不是 all-axis unidirectional |
| normalization | InstanceNorm → BatchNorm，理由：InstanceNorm 统计量依赖全序列长度、跨 chunk size 不一致；BatchNorm 用固定 running statistics、chunk-size invariant（p.3 §3.3.3） | `strict_causal`（不引入未来样本；用训练期 running stats） |
| channel attention (SCA) | AdaptiveAvgPool1d (global) → CausalConv1d (depthwise, $K_{\text{sca}}=11$)；理由：「Global pooling aggregates future frames, violating causality」 | `strict_causal`（这是论文自己识别并修掉的**唯一一处显式未来泄漏点**） |
| state | state buffer $s_k^{(\ell)}$ 存最近 $P_L^{(\ell)}$ 帧，Eq. (4)；feature buffer 要求 `buffered frames ≥ C+L_dec`，Eq. (2) 之后；SSU 用 $\Pi_C(x)=x_{1:C}$ 限制写入范围，Eq. (5) | `strict_causal` 设计；但 warm-up 帧数、state reset、长流漂移、丢帧策略**未报告** |
| compute | ONNX Runtime，Intel Xeon Silver 4510 **单线程**，端到端 steady-state（STFT+model+iSTFT）：$C=1$ 时 RTF 4.59 → $C=64$ 时 0.30（$L_{\text{tot}}=0$）；RTF<1 需 $C\ge 7\text{–}12$；$C=8$ 因果配置 RTF 0.77（p.4 §4.2，Figure 3） | 只是**吞吐**证据，不是目标硬件 p99 / deadline miss 证据；且 $C=1$ 时 RTF 4.59 说明 12.5 ms 那个点在该 CPU 上**并不实时** |
| end-to-end | 论文只给「algorithmic plus chunk buffering」：$C=8$ 因果配置 62.5 ms（= 12.5 + 8×6.25，本页按 Eq. (3) 复算一致） | ADC/DMA、I/O、driver buffer、DAC/playout、capture-to-playback、underrun/overrun **未报告** → 未验证 |

**判定结论**：LaCo-SENet 是本库目前**因果性证据链最完整的一篇**——它不是靠"论文自称 causal"，而是给出了逐层 padding 分配式、状态更新式、选择算子，以及一句极强的经验断言：「chunk-wise streaming outputs are numerically identical to full-sequence outputs across all configurations」（p.4 §4.3）。

但必须同时记住两点：**(a)** 它的 "fully causal" 只覆盖卷积骨干（$L_{\text{enc}}=L_{\text{dec}}=0$），前端仍保留 $W/2=12.5$ ms 的 STFT center delay，因此**下界是 12.5 ms，不是 0 ms**；**(b)** 12.5 ms 那个点在报告硬件上 RTF 4.59，真正能实时的 $C$ 会把总时延推高到 56–88 ms 量级。

## 3. 这个做法核心 trick 是什么？

### 3.1 三个机制，一个旋钮

~~~text
                     r = (rL, rR)  ← 唯一训练期超参数（全部非对称卷积层共享）
                            │
        ┌───────────────────┼────────────────────────┐
        ▼                   ▼                        ▼
 ① 非对称时间 padding   ② dual-buffer streaming   ③ selective state update
    固定 Ptot，只改分配      state buffer（过去）      ΠC(x) = x1:C
    感受野/参数量不变        + lookahead buffer（未来）  只把当前 chunk 帧写进 state
        │                   │                        │
        └───────────────────┴────────────────────────┘
                            ▼
              chunk-wise 输出 ≡ full-sequence 输出
~~~

![[wiki_low_latency/assets/2606.19688/2606.19688-page2-dual-buffer-architecture.png]]

> 图注：原论文第 2 页 Figure 1 页面渲染。**(a)** dual-buffer streaming 架构：STFT context buffer 在输入级给 encoder lookahead，feature buffer 在 decoder 级提供未来，state buffer 保留过去；注意方框上明确标了 "Time Stage (Causal)" 与 "Freq Stage (Non-Causal)"，以及右下的 "OLA Tail Buffer (Tail of Chunk n-1)" 与 "Output & Buffer Advance"。**(b)** 训练期用非对称 padding $(P_L,P_R)$ 重分配过去/未来上下文而保持感受野。**(c)** chunk size = 1 的流式推理：selective state update 阻止 lookahead 帧污染卷积 state。图片为 PDF 页面复制，不是 AI 重画。

### 3.2 Trick ①：padding 分配式（时延旋钮）

设标准对称卷积的单侧 padding 为 $P$，则总 padding 固定为 $P_{\text{tot}}=2P$。定义 padding ratio：

$$
r=(r_L,r_R),\qquad r_L+r_R=1,
$$

时间轴 padding 分配为：

$$
P_L=\operatorname{round}(P_{\text{tot}}\cdot r_L),\qquad P_R=P_{\text{tot}}-P_L. \tag{1}
$$

符号解释：

- $P_{\text{tot}}$：一层卷积在时间轴上可用的总 padding 预算，由 kernel size 决定并**在整个训练与推理过程中固定**；
- $r_L,r_R$：过去/未来分配比例，$r_R=0$ 即纯因果（无右侧访问），$r_R=0.5$ 即退化为标准对称 padding；
- $P_L,P_R$：实际的左侧（过去）与右侧（未来）padding 帧数；
- $r$ **是所有非对称卷积层共享的、固定的训练期超参数**——论文明确写「it is not adapted to SNR, input content, or runtime conditions」。它不随输入变化，所以不是一个"动态时延"机制，而是一个"训练时选点时延"机制。

关键不变性：因为 $P_{\text{tot}}$ 固定，**感受野大小、参数量、架构拓扑都不变**，变的只是「过去/未来访问比」。论文原话：「Only the ratio of past-to-future access changes, enabling quantized latency configuration.」频率轴 padding 保持对称，只有时间轴接受非对称切分。

> [!note] 为什么这是"量化"而不是"连续"的时延
> $P_R$ 必须是整数帧，逐层累加后 $L_{\text{tot}}=L_{\text{enc}}+L_{\text{dec}}$ 是整数。代入 Eq. (3) 可得时延只能取
> $$\tau=12.5+6.25\,L_{\text{tot}}\ \text{ms},$$
> 即以 hop（6.25 ms）为步长的离散阶梯。论文扫出的 9 个配置正好对应 $L_{\text{tot}}\in\{0,2,4,6,8,10\}$（$L_{\text{enc}}=L_{\text{dec}}\in\{0,\dots,5\}$ 六个）、$\{14,22\}$（论文只写 100.0/150.0 ms 两个中间点）与 $\{30\}$（对称参考）。100/150 ms 对应 $L_{\text{enc}}=L_{\text{dec}}=7/11$ 是**本页按 Eq. (3) 的推导**，论文原文没有点明这两个整数。

### 3.3 Trick ②：dual-buffer streaming（把全序列计算精确重切成 chunk）

输入谱按 $C$ 帧一个 chunk 处理，$k$ 为 chunk 序号。累计右侧 padding 决定算法时延：

$$
L_{\text{enc}}=\sum_{\ell\in E}P_R^{(\ell)},\qquad
L_{\text{dec}}=\max_{b\in\mathcal B}\sum_{\ell\in D_b}P_R^{(\ell)},\qquad
\mathcal B=\{\text{mask},\text{phase}\}, \tag{2}
$$

$$
\tau_{\text{ms}}=1000\cdot\frac{(L_{\text{enc}}+L_{\text{dec}})\cdot h+W/2}{f_s}. \tag{3}
$$

符号解释：

- $E$：encoder 中带非对称时间 padding 的卷积层集合；$D_b$：decoder 分支 $b$ 中同类层的集合；
- $h$：hop size（100 samples）；$W$：STFT window（400 samples）；$f_s$：采样率（16 kHz）；
- $(L_{\text{enc}}+L_{\text{dec}})\cdot h$：把累计 lookahead 帧数换算成样本数——**每一帧 lookahead 只花一个 hop**，不是一整个 window；
- $W/2$：STFT center delay，**与 $r$ 无关的常数项**，这就是 12.5 ms 下界的来源；
- decoder 用 $\max$ 而非求和：mask 与 phase 解码器**并行**运行，lookahead 取分支最大而不是相加。

**Challenge 1 — state buffer（过去上下文）。** chunk 边界上，卷积的左 padding 若填零就与全序列处理不一致。每层缓存最近 $P_L^{(\ell)}$ 帧：

$$
\tilde x_k^{(\ell)}=\big[\,s_{k-1}^{(\ell)};\ x_k^{(\ell)};\ \mathbf 0\,\big],\qquad
s_k^{(\ell)}\leftarrow\text{last }P_L^{(\ell)}\text{ frames of }x_k^{(\ell)}. \tag{4}
$$

$\tilde x_k^{(\ell)}$ 是喂给卷积的拼接输入（过去的真实激活 + 当前 chunk + 右侧零填充），$s_k^{(\ell)}$ 是本层在 chunk $k$ 结束时保存的状态。

**Challenge 2 — lookahead buffer（未来上下文）。** 分两级注入未来：

- **输入级（encoder）**：当 $L_{\text{enc}}>0$，encoder 输入被扩展到 $C+L_{\text{enc}}$ 帧，使每个 encoder 卷积访问**真实未来帧**而不是零；
- **特征级（decoder）**：当 $L_{\text{dec}}>0$，encoder 输出特征被累积进 feature buffer，只有 `buffered frames ≥ C+L_dec` 时才触发 decoder；decoder 收到的是扩展后的特征序列，**只输出当前 chunk 对应的那部分**，其余帧作为未来上下文。因为被输出区域与零右填充边界之间至少隔着 $L_{\text{dec}}$ 帧 lookahead，所有输出都用真实未来上下文算出来。

**Challenge 3 — selective state update（本篇真正的技术贡献）。** 当 state buffer 与 lookahead buffer 同时工作时，若 state 记录**全部**帧（含追加的 lookahead），这些帧会在后续 chunk 里出现两次（一次来自 state、一次作为新输入），输出被逐步扭曲。论文用选择算子

$$
\Pi_C(x)=x_{1:C}
$$

只保留当前 chunk 帧，于是状态更新变成：

$$
s_k^{(\ell)}\leftarrow\text{last }P_L^{(\ell)}\text{ frames of }\Pi_C\big(x_{k,\text{ext}}^{(\ell)}\big). \tag{5}
$$

即使处理的是含 $C$ 个当前帧加 lookahead 的扩展输入 $x_{k,\text{ext}}$，state 也只依赖当前 chunk 帧。**lookahead 帧参与前向计算，但永不写入 state。**

### 3.4 Trick ③（工程侧）：两处流式化改造

| 改造 | 原设计 | 问题 | 替换为 |
|---|---|---|---|
| normalization | InstanceNorm | 统计量依赖全序列长度，跨 chunk size 不一致 | BatchNorm（固定 running statistics，chunk-size invariant） |
| channel attention (SCA) | AdaptiveAvgPool1d（global） | 全局池化聚合未来帧，**违反因果性** | CausalConv1d（depthwise，$K_{\text{sca}}=11$） |

这两处是"论文自己承认原来会破坏因果性、必须改"的地方，也是复现时最容易漏掉的地方。

### 3.5 骨干与损失

骨干沿用 PrimeK-Net [3]（[[wiki_low_latency/entities/PrimeK-Net]]）的分解方式：

$$
H=\mathcal T_\theta\big(\mathcal E_\theta(X)\big),\qquad
\hat M=\mathcal D_\theta^{M}(H),\qquad
\hat\Phi=\mathcal D_\theta^{\Phi}(H). \tag{6}
$$

$X$ 先投影到 $C_h$ 通道，过 encoder 的 DSDDB（dense dilated depthwise block，四个 depthwise separable conv，dilation 1/2/4/8，dense connection），沿频率下采样（stride $(1,2)$）得到 $H\in\mathbb R^{C_h\times T\times F'}$（$F'=\lceil F/2\rceil$）；每个 decoder 先过 DSDDB 再用转置卷积恢复频率分辨率。DSDDB 中的 depthwise 卷积使用 `AsymmetricConv2d`，使同一个 $r$ 贯穿整个网络。

损失完全沿用 PrimeK-Net [3]（[[wiki_low_latency/entities/PrimeK-Net]]）：

$$
\mathcal L=0.9\,\mathcal L_{\text{mag}}+0.3\,\mathcal L_{\text{pha}}+0.1\,\mathcal L_{\text{com}}
+0.05\,\mathcal L_{\text{con}}+0.05\,\mathcal L_{\text{gan}},
$$

分别加权 magnitude、phase、complex、consistency 与 MetricGAN [17] metric 项。论文**没有在本页展开每一项的具体形式**，因此本 Wiki 不补写未给出的定义。

> [!contradiction] 「沿用 PrimeK-Net」的五个权重系数在原文中不存在
> 本页给出的 $0.9/0.3/0.1/0.05/0.05$ 标注为"沿用 PrimeK-Net [3]"，但**补摄 PrimeK-Net 原文（arXiv:2502.19906）后确认：该文全文未给出任何 $\lambda$ 数值**，只定义了两个损失函数 $\mathcal L_{old}$（Eq. 11）与 $\mathcal L_{new}$（Eq. 12）的形式，未做加权组合，也未给权重表。
> ⇒ 这五个系数**不可能来自 PrimeK-Net 的原文**。可能是：① 来自官方代码实现（未写进论文）；② 来自 PrimeK-Net 的后续版本；③ 是 LaCo-SENet 自行设定但误标为"沿用"。
> **本库不判定哪一方正确，按双方原文并列记录**，并标注为**引用链断点**——与 [[wiki_low_latency/overview#跨论文判定口径（2026-09-20 确立）|第 14 条"锚点数值必须先钉死口径"]]同源。任何后续复现工作若照抄这五个系数，应知道其**一手依据缺失**。

训练：AdamW（lr $=5\times10^{-4}$，$(\beta_1,\beta_2)=(0.8,0.99)$）+ exponential LR decay，batch size 8，400K steps；**每个时延配置独立训练**，三个随机种子，按 validation PESQ 选最优 checkpoint，报 mean ± s.d.。

> [!note] 「独立训练」是理解本文代价的关键
> 时延族不是一次训练后调推理参数得到的，而是**每个点单独训练一个模型**（每个点 400K steps × 3 seeds）。因此"1.37M 参数扫出整族模型"说的是**参数量**恒定，而不是训练成本恒定。论文没有报告总训练开销。

## 4. 实验里哪个消融最关键？

### 4.1 数据与评价

VoiceBank+DEMAND @16 kHz，11,572 训练 / 824 测试语句，10 类噪声 × 四档 SNR（论文只写 "four SNR levels"，**未给出具体 dB 值**）。评价用 PESQ (wideband)、STOI、CSIG、CBAK、COVL，在**全长度测试语句上用 full-sequence inference** 计算；流式等价性单独在 §4.3 验证。

![[wiki_low_latency/assets/2606.19688/2606.19688-page3-table1-comparison.png]]

> 图注：原论文第 3 页 Table 1 渲染（VoiceBank+DEMAND 主对比表）。用于核对各基线的 $\tau$/Params/PESQ/STOI/CSIG/CBAK/COVL，以及 †（自称 unidirectional 但 encoder 用非因果对称 padding，算法时延不可确定）与 ‡（对称 padding 上界，排除出因果排名）两个脚注。

### 4.2 主结果（Table 1，照抄原文数字）

| Model | Year | $\tau$ (ms) | Params | PESQ | STOI | CSIG | CBAK | COVL |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| Noisy | — | — | — | 1.97 | .921 | 3.35 | 2.44 | 2.63 |
| RNNoise [5] | 2018 | 10 | 0.06M | 2.33 | .922 | 3.40 | 2.51 | 2.84 |
| GaGNet [15] | 2022 | ~10 | 5.94M | 2.94 | — | 4.26 | 3.45 | 3.59 |
| DFNet3 [7] | 2023 | 40 | 2.13M | 3.17 | .944 | 4.34 | 3.61 | 3.77 |
| aTENNuate [4] | 2025 | 46.5 | 0.84M | 3.27 | — | 4.57 | 2.85 | 3.96 |
| xLSTM-SENet† [9] | 2025 | — | ~2.2M | 3.26 | .950 | 4.57 | 3.79 | 4.00 |
| SEMamba† [8] | 2024 | — | 1.41M | 3.29 | .950 | — | — | — |
| **LaCo-SENet** ($L_{\text{enc}}=0,L_{\text{dec}}=0$) | 2026 | **12.5** | 1.37M | **3.35**±.02 | **.952**±.000 | **4.61**±.01 | **3.71**±.01 | **4.05**±.02 |
| LaCo-SENet ($L_{\text{enc}}=1,L_{\text{dec}}=1$) | | 25.0 | | 3.36±.01 | .953±.000 | 4.62±.01 | 3.72±.02 | 4.07±.01 |
| LaCo-SENet ($L_{\text{enc}}=3,L_{\text{dec}}=3$) | | 50.0 | | 3.40±.02 | .953±.001 | 4.63±.02 | 3.72±.01 | 4.09±.02 |
| LaCo-SENet ($L_{\text{enc}}=5,L_{\text{dec}}=5$) | | 75.0 | | 3.43±.01 | .954±.001 | 4.66±.02 | 3.78±.00 | 4.12±.02 |
| LaCo-SENet‡ ($L_{\text{enc}}=15,L_{\text{dec}}=15$) | | 200.0 | | 3.47±.02 | .957±.001 | 4.69±.01 | 3.79±.03 | 4.17±.02 |
| PrimeK-Net [3]（非因果上界） | 2025 | — | 1.41M | 3.61 | — | 4.81 | 3.98 | 4.35 |

> [!note] 该行的口径已由补摄核验（2026-09-27）
> PrimeK-Net 的 **3.61 / 4.81 / 3.98 / 4.35** 与参数量 **1.41M** 已与本页数据逐项对齐（见 [[wiki_low_latency/sources/2025/PrimeK-Net 2025]] §4.2）。但注意**本篇 Table 1 未列 PrimeK-Net 的算力**，而 PrimeK-Net 只有 **44.64 G FLOPs** 一种口径（库内唯一 FLOPs 量纲）——所以该行**不能用于"效率"对比**，只能用于"质量上界"。
> 另：PrimeK-Net 的 STOI 在原文中未报告（此处亦为 "—"），其评价集为 VoiceBank+DEMAND，与本篇相同，故该上界是**同数据同前端**的紧上界。

论文给出的读法：

- 12.5 ms 全因果点 PESQ 3.35，**超过所有因果基线**，包括 46.5 ms 的 aTENNuate（3.27）；
- PESQ 从 12.5 ms 的 3.35 升到 75.0 ms 的 3.43，**主要增益集中在 25–75 ms**，之后收益递减；
- 对称参考再花 125 ms 只换来 +0.04（3.47 @200.0 ms）；
- 流式配置保留非因果 PrimeK-Net（3.61）的 **93–95%** 质量，参数量相当（1.37M vs 1.41M）。

> [!contradiction] SEMamba 与 xLSTM-SENet 的因果性判定冲突
> Table 1 脚注 †：「Labeled unidirectional, but encoder convolutions use non-causal symmetric padding; algorithmic latency not deterministically computable.」论文据此把 **SEMamba（PESQ 3.29）与 xLSTM-SENet（3.26）排除出因果排名**，尽管二者论文自称 unidirectional。
> 这与本库 [[wiki_low_latency/sources/2026/RT-SEMamba 2026]] 的处境直接相关：RT-SEMamba 同样基于 SEMamba 系因果化改造，其 25 ms 结论建立在"论文自称 causal"之上。LaCo-SENet 的审计口径更严——**只要 encoder 存在非因果对称 padding，算法时延就不可确定，即便模型自称 unidirectional**。本库应沿用这一更严口径：把「自称单向」与「逐层可核验的因果」分开记账。

> [!question] Table 1 与 Table 2 的 PESQ 口径不一致
> Table 1 是 full-sequence inference，12.5 ms 配置为 **3.35**；Table 2 是 $C=1$ 的 streaming PESQ，同一配置为 **3.39**。而论文同时声称「chunk-wise streaming outputs are numerically identical to full-sequence outputs across all configurations」。两处相差约 +0.04~+0.05（各配置均如此）。
> 最可能的解释是 Table 2 的 caption 写了「tail 30 frames trimmed to exclude end-of-utterance OLA boundary artifacts」——即**评分协议不同**（截尾后打分），而非输出不同。但论文**没有把这两个数字对齐说明**，读者容易误读成流式比全序列更好。复现时应统一评分协议。

### 4.3 最关键的消融：SSU（Table 2）

![[wiki_low_latency/assets/2606.19688/2606.19688-page4-pesq-latency-rtf-ablation.png]]

> 图注：原论文第 4 页渲染。左上 Figure 2（PESQ vs algorithmic latency，实心圆点连线的 LaCo-SENet 覆盖 12.5–200.0 ms，空心标记为对比模型）；右上 Figure 3（steady-state streaming RTF vs chunk size $C$，三条曲线对应 $L_{\text{enc}}+L_{\text{dec}}\in\{0,10,30\}$，虚线为 RTF=1）；下方 Table 2（SSU 消融）。

Table 2 在 **streaming inference、$C=1$** 下对比启用/禁用 SSU（$L_{\text{tot}}=L_{\text{enc}}+L_{\text{dec}}$，tail 30 帧截尾，3 seeds）：

| $L_{\text{enc}}+L_{\text{dec}}$ | $\tau$ (ms) | w/ SSU | w/o SSU | $\Delta$PESQ |
|---:|---:|---:|---:|---:|
| 0 | 12.5 | 3.39±.01 | 3.39±.01 | 0.00 |
| 2 | 25.0 | 3.41±.01 | 1.86±.31 | **−1.56** |
| 6 | 50.0 | 3.45±.01 | 1.45±.14 | **−2.00** |
| 10 | 75.0 | 3.48±.01 | 1.39±.01 | **−2.09** |
| 30 | 200.0 | 3.52±.02 | 2.04±.06 | −1.48 |

论文的解读：

- 所有非对称配置（$L_{\text{tot}}=2\text{–}10$）禁用 SSU 后，PESQ **跌破 noisy 基线 1.97**，且**随 lookahead 增大单调恶化**（−1.56 → −2.09）；
- 对称参考（$L_{\text{tot}}=30$，$r_R=0.5$）跌幅较小（−1.48），因为左右等分把 state buffer 减半，降低了污染程度；
- 结论：「SSU is thus essential whenever asymmetric padding introduces lookahead.」
- 并且在 $L_{\text{tot}}=0$ 时 SSU 是完全的 no-op（$\Delta=0.00$）——**没有 lookahead 就没有可泄漏的帧**，这与机制解释完全自洽。

> [!note] 这是本篇最有信息量的消融
> 它不只是"去掉一个模块掉点"，而是**证明了这个机制的必要性边界**：污染量随 lookahead 单调增长，说明 bug 的模式与理论预测一致（lookahead 帧被回放两次），而不是随机退化。同时 $L_{\text{tot}}=0$ 处的零差异构成了一个干净的对照组。

### 4.4 流式吞吐（Figure 3）

ONNX Runtime，Intel Xeon Silver 4510 **单线程**，端到端 steady-state（STFT + model + iSTFT）：

- $L_{\text{tot}}=0$：$C=1$ 时 RTF **4.59** → $C=64$ 时 **0.30**；
- 大 lookahead 的惩罚随 $C$ 增大收窄：$C=1$ 时 2.10×，到 $C=64$ 约 1.0×（此时各配置 RTF ≈0.23–0.30）；
- **实时（RTF<1）需要 $C\ge 7\text{–}12$**；
- $C=8$ 因果配置：总时延（algorithmic + chunk buffering）**62.5 ms**，RTF **0.77**。

> [!warning] 「12.5 ms」与「RTF<1」不是同一个工作点
> $C=1$ 是唯一能保住 12.5 ms 算法时延的 chunk size，但它的单线程 RTF 是 4.59。要 RTF<1 必须放大 $C$，而 chunk 缓冲本身要付出 $6.25\times C$ ms。按 Eq. (3) 与本页推导，$C\ge7\text{–}12$ 对应的总时延约为 **56–88 ms**；论文只显式给出 $C=8$ 因果配置的 62.5 ms。
> 也就是说：**本篇报出的 12.5 ms 是算法时延，不是实时工作点的端到端时延。**论文没有给出每个配置的精确 $C$ 阈值。

## 5. 这个方向还剩什么问题没解决？（future work / limitation）

**论文自己承认/隐含的：**

1. $r$ 是固定的训练期超参数，「not adapted to SNR, input content, or runtime conditions」——**运行时不可切换时延**。换时延点必须换模型（每点独立训练 400K steps × 3 seeds），没有"一个模型多时延档位"的方案，也没有动态时延自适应。
2. 论文把区间定位在 **10–80 ms**，没有主张进入个位数毫秒区间；12.5 ms 下界来自 $W/2$，与 padding ratio 无关，**当前架构无法突破**。

**本页读出的隐藏问题（本库关注）：**

3. **12.5 ms 不是 2 ms。** $W/2=200$ samples 的 STFT center delay 是硬下界，且 Eq. (3) 把它计入时延——这意味着前端本身需要 12.5 ms 未来样本。按本 Wiki 约 2 ms 的硬约束，LaCo-SENet 最优点仍超出 6 倍以上。
4. **实时工作点 = 高时延。** $C=1$ 单线程 RTF 4.59；RTF<1 需 $C\ge7\text{–}12$，总时延升至 ~56–88 ms 量级。论文没有报告把 $C$ 降到 1 的实时方案（更快的核、量化、多线程、定点）。
5. **硬件口径单一且非端侧。** 只有 Intel Xeon Silver 4510 单线程 ONNX Runtime。**未报告**：目标 SoC（ARM/DSP/NPU）、p50/p95/p99、deadline miss、峰值 RAM/SRAM、量化/定点精度、功耗、编译器/算子实现差异、RTF 的 batch=1 长流稳定性。
6. **端到端完全缺失。** ADC/DMA、I/O buffer、线程调度、DAC/playout、capture-to-playback、underrun/overrun 全部**未报告**。论文的 62.5 ms 只到"algorithmic + chunk buffering"。
7. **人声保留维度完全空白。** 只有 PESQ/STOI/CSIG/CBAK/COVL。**未报告**：负 SNR 分层（−10/−5/0/5 dB 的逐档结果）、babble/竞争说话人、瞬态噪声、未见噪声、false-suppression、SPP/VAD 校准、F0/formant/prosody continuity、voiced energy 保留、DNSMOS SIG/BAK/OVL、ASR WER。
   - 一个可见的**预警信号**：12.5 ms 配置的 CBAK（3.71）与 200 ms 配置（3.79）差距不大，但 aTENNuate 的 CBAK 只有 2.85 而 CSIG 高达 4.57——说明 CBAK/CSIG 在不同模型间的权衡结构差异很大，本库不能只看 PESQ 判优劣。
8. **训练细节不足以完全复现。** 未报告：总训练步的 wall-clock/GPU 型号与数量、数据增强、验证集划分、loss 各分项的具体定义（论文说"follows PrimeK-Net"，需查原文）、seed 选择对 $\pm$ 的影响、DSDDB 四个卷积的 kernel 与 dilation 的确切配对方式。
9. **等价性声明不可独立验证。** 「numerically identical」是论文的断言，本页没有代码级复现或第三方验证；且与 Table 1/Table 2 的 PESQ 差异并存（见 §4.2 的 [!question]）。
10. **基线可比性受限。** Table 1 里 GaGNet 标 "~10 ms"、RNNoise 标 10 ms，论文说明时延值「from original papers or estimated as (window−hop)/fs」——估算口径与本文的 Eq. (3) 口径**不是同一把尺子**。PrimeK-Net 是非因果上界，不能计入因果排名。

**对当前方向的可迁移启示：**

- 「把未来上下文变成训练期旋钮」这个思路本身对 2 ms 目标是有价值的——但它需要先解决"固定 $W/2$ 下界"：换成短窗/非对称窗前端（参见 [[wiki_low_latency/concepts/2204.09911-short-asymmetric-stft]]）后，padding ratio 才能成为真正的主旋钮。
- SSU 的「选择算子」是一个**通用补丁**：任何"既缓存过去状态、又显式缓冲未来帧"的流式系统都会遇到重复回放问题，本库其他做 lookahead 的因果模型应逐一体检这一项。

## 6. 本论文在库中的位置关联（cross-reference matrix）

| 关系 | 库中论文/概念 | 关联与差异 |
|---|---|---|
| **前身/基石** | [[wiki_low_latency/sources/2025/PrimeK-Net 2025]]、[[wiki_low_latency/entities/PrimeK-Net]]（ICASSP 2025，[3]） | LaCo-SENet 直接沿用 PrimeK-Net 骨干（1.37M vs 1.41M）与同一套损失；PrimeK-Net 是非因果的，LaCo-SENet 的贡献就是把它的**未来访问**参数化。**已于 2026-09-27 完成补摄**——PrimeK-Net 的 SCA 用 `AdaptiveAvgPool1d`（时间作用域原文未定义，疑为全局）正是本篇 §3.4 用 depthwise `CausalConv1d`($K_\text{sca}=11$) 改造的点；**两篇 STFT 参数完全一致（400/400/100 @16 kHz）**，可确证骨干同源。**注意本页两个 caveat**：① PrimeK-Net 报 **44.64 G FLOPs**（库内唯一 FLOPs 量纲），与其 1.41M 参数属不同口径，禁与其他篇的 MACs 混比；② 本篇写"损失完全沿用 PrimeK-Net"并给出 $0.9/0.3/0.1/0.05/0.05$，但 **PrimeK-Net 原文未给任何 $\lambda$ 数值** ⇒ 引用链断点，不判定谁对 |
| **前身/基石** | [[wiki_low_latency/sources/2022/STFT-Domain Very Low Algorithmic Latency 2022]]、[[wiki_low_latency/concepts/2204.09911-short-asymmetric-stft]] | 那篇把「频率分辨率预算」与「输出时延预算」拆开（analysis window 长、synthesis window 短）；本篇拆的是 **conv padding 的左右分配**。两者都在做「非对称」，但作用轴不同，是同一思想的两个正交实现 |
| **前身/基石（被明确对照）** | [[wiki_low_latency/entities/DeepFilterNet2]]、[[wiki_low_latency/sources/2022/DeepFilterNet2 2022]] | 论文点名 DeepFilterNet「supplies lookahead through a global input shift while keeping every convolution purely causal」——lookahead 只能在输入边界注入。**本篇正是要突破这个限制**，代价是必须引入 SSU。DFNet3（3.17@40 ms）在 Table 1 中被本篇以更低时延（3.35@12.5 ms）超过 |
| **同分支竞品（时延-质量 Pareto）** | [[wiki_low_latency/sources/2024/Ultra-Low Latency Speech Enhancement Comprehensive Study 2024]]、[[wiki_low_latency/entities/CRUSE-Latency-Study]] | 该研究建立统一的前端/模型对照框架；本篇提供了同一架构内的**9 点 Pareto 曲线**，正好是那种统一比较最需要的素材，但口径（Eq. (3) 计入 $W/2$）需对齐 |
| **同分支竞品（因果时域）** | [[wiki_low_latency/entities/On-TasNet]]、[[wiki_low_latency/sources/2021/On TasNet Low-Latency SE 2021]]、[[wiki_low_latency/concepts/2103.14882-causal-tasnet]] | 因果 learned-filterbank 路线，同样关心因果性与低时延；本篇是时频掩蔽路线，两者可做「时域 vs 时频」的因果账本对照 |
| **同分支竞品（Mamba/SSM）** | [[wiki_low_latency/sources/2026/RT-SEMamba 2026]]、[[wiki_low_latency/entities/RT-SEMamba]]、[[wiki_low_latency/sources/2024/SlowFast-SSM 2024]]、[[wiki_low_latency/entities/SlowFast-SSM]] | RT-SEMamba 25 ms、SlowFast-SSM 低 MAC；本篇 12.5 ms 且**给出逐层 padding 分配式**。**关键冲突**：本篇把 SEMamba 判为"时延不可确定"（Table 1 脚注 †），而 RT-SEMamba 的因果性正建立在 SEMamba 系改造上——两条记录必须一起读 |
| **同分支竞品（时频掩蔽/低复杂度）** | [[wiki_low_latency/sources/2023/FSB-LSTM 2023]]、[[wiki_low_latency/entities/FSB-LSTM]]、[[wiki_low_latency/sources/2021/DPCRN Low-Latency Direction 2021]]、[[wiki_low_latency/sources/2020/DCCRN Low-Latency Direction 2020]] | 都是时频域因果/低时延增强；本篇的 magnitude mask + phase replacement 输出形式与 DCCRN/DPCRN 的复数谱路线可对比 |
| **跨分支类比（把"上下文预算"当旋钮）** | [[wiki_low_latency/concepts/2409.10358-ultra-low-latency-benchmark]]、[[wiki_low_latency/concepts/低时延前端与延迟账本]]、[[wiki_low_latency/concepts/严格因果与算法延迟]] | 本篇是这三个账本概念页的**最佳正向样本**：给出了可复算的 Eq. (3) 与逐层 padding 分配；同时暴露了"算法时延 ≠ 实时工作点"的经典陷阱 |
| **缺口对照（人声保留）** | [[wiki_low_latency/concepts/低 SNR 人声保留评估]]、[[wiki_low_latency/sources/2023/Uncertainty-Aware Speech Enhancement 2023]]、[[wiki_low_latency/entities/Uncertainty-Aware-SE]]、[[wiki_low_latency/sources/2022/Hybrid Continuity Loss 2022]] | 本篇完全没有人声保留/过抑制/低 SNR 分层证据；这些页面提供了本篇缺失的验收字段 |
| **概念页** | [[wiki_low_latency/concepts/2606.19688-latency-configurable-asymmetric-padding]] | 展开 padding 分配式、双缓冲与 SSU 的可复用推导 |
| **实体页** | [[wiki_low_latency/entities/LaCo-SENet]] | 架构配置、时延族、RTF 与部署口径 |

## 7. 一句话总结"江湖地位"

> **2026 | 严格因果超低时延 SE | 把"未来上下文"从架构常量降级为训练期旋钮（非对称 padding）+ 用 SSU 修复由此产生的 state corruption，在 1.37M 固定预算下扫出 12.5–200 ms 整条 Pareto 曲线，12.5 ms 全因果 PESQ 3.35 超过 46.5 ms 的 aTENNuate 3.27 → 是"时延可配置"这一子方向的开篇标尺，同时以最严的因果审计口径把 SEMamba/xLSTM-SENet 排除出排名；但 12.5 ms 中仍有 12.5 ms 不可消除的 STFT center delay，且真正实时的 chunk size 会把总时延推回 62.5 ms 量级——距离约 2 ms 目标仍有量级差距。**

## 参考资料

- [arXiv:2606.19688](https://arxiv.org/abs/2606.19688)
- 代码：<https://github.com/yskim3271/LaCo-SENet>
- 本地原件：`raw/papers/low_latency_causal_se/2606.19688.pdf`
- 本地文本抽取：`tmp/pdf_extract/2606.19688.txt`
- 页面渲染核对：`wiki_low_latency/assets/2606.19688/`（page1–page5；本页嵌入 page2 架构图、page3 Table 1、page4 Figure 2/3 + Table 2）
- 论文内关键引用：PrimeK-Net [3]（ICASSP 2025）、aTENNuate [4]（Interspeech 2025）、RNNoise [5]、DCCRN [6]、DeepFilterNet [7]、SEMamba [8]（SLT 2024）、xLSTM-SENet [9]（Interspeech 2025）、FastWaveNet [10]、cached convolution [11]、Denoiser [12]、Emformer [13]、Stateful Conformer [14]、GaGNet [15]、VoiceBank+DEMAND [16]、MetricGAN [17]、CSIG/CBAK/COVL [18]
