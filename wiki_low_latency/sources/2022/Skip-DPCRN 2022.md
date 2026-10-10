---
title: Skip-DPCRN - 并行 RNN 上的推理期状态跳过与 VAD 引导算力压缩
type: source
created: 2026-09-22
updated: 2026-09-22
tags:
  - speech-enhancement
  - single-channel
  - streaming
  - dual-path-rnn
  - dpcrn
  - skip-rnn
  - inference-skipping
  - parallel-rnn
  - state-skipping
  - update-rate
  - vad-guided
  - model-compression
  - dynamic-temporal-pruning
  - input-dependent-compute
  - paper-claimed-causal
  - 48ms-total-latency
source_type: paper
year: 2022
authors: Xiaohuai Le; Tong Lei; Kai Chen; Jing Lu
venue: IEEE/ACM TASLP, vol. 30, pp. 2411-2421, 2022
arxiv: https://arxiv.org/abs/2207.11108
local_pdf: raw/papers/low_latency_causal_se/2207.11108.pdf
evidence_policy: local_pdf_only
related:
  - [[wiki_low_latency/entities/Skip-DPCRN]]
  - [[wiki_low_latency/concepts/2207.11108-inference-skipping-parallel-rnn]]
  - [[wiki_low_latency/sources/2021/DPCRN Low-Latency Direction 2021]]
  - [[wiki_low_latency/entities/DPCRN]]
  - [[wiki_low_latency/concepts/2107.05429-dual-path-recurrent-context]]
  - [[wiki_low_latency/concepts/严格因果与算法延迟]]
  - [[wiki_low_latency/concepts/低时延前端与延迟账本]]
---

~~~yaml
- 论文: [Inference skipping for more efficient real-time speech enhancement with parallel RNNs](2022)
  ├── 要解决什么问题: 实时 SE 的算力必须按最坏情况预留，而剪枝/量化/蒸馏都在训练期定型，无法按输入内容动态省算力；把 Skip-RNN 直接搬进 SE 又会因为「RNN 跳步时 mask 也停止更新」产生音频伪影（引文 [20] TinyLSTM 的失败先例）
  ├── 核心方法: 把 Skip-RNN 的二值门控状态更新塞进 DPCRN 的 parallel RNN（intra-frame × T 条 + inter-frame × F_in 条并行），让部分 RNN 跳步时 mask 仍由其余通路继续更新；再用 L_Skip 三种正则诱导跳步、用 γ 缩放式做推理期免重训练的更新率旋钮、用多任务 VAD 分支在纯噪帧单独降 γ
  ├── 属于哪个分支: 单通道时频复数掩蔽增强 / CRN + dual-path / **推理期动态算力压缩**（不是剪枝、不是量化、不是蒸馏、不是结构重设计）
  ├── 输入/输出: 3 通道 X_r / X_i / X_p（复数谱实部、虚部、对数功率谱）→ 5 层 Conv2D encoder（stride 只在频率轴降采样）→ 2 × Skip-DPRNN → 转置卷积 decoder + encoder-decoder skip → 幅度掩蔽 M 与相位掩蔽 Φ（实/虚）→ S̃ = X ⊙ M ⊙ Φ → iSTFT + OLA
  ├── 关键trick: 不新造骨干、不改推理图拓扑，只把「RNN 状态要不要更新」变成一个可学习、可正则、可推理期缩放的二值门；且 GRU 的 output ≡ hidden state，所以状态不更新时后面的 FC 也一起跳过
  ├── 数据集: WSJ0 SI-84（14633 条 ≈25 h，120 说话人；12776/1206/651）+ DNS-3 噪声（60000 条、150 h，DEMAND + Audioset + Freesound）；测试用两个**未见**噪声集 MUSAN 音乐 与 NOISEX92（babble / factory1 / f16），SNR −5/0/5 dB 各 651 条；另有长音频测试集（成对拼接 + 每对间 8 s 静音，325 段）
  ├── 对比了谁: ① 同算力下的 DPCRN-S（直接训练更小模型）与 DPCRN-P（结构化剪枝 + ℓ2 范数正则）；② 自身基线 DPCRN-base；③ 泛化验证用 CRUSE（8.58 M）与 GCRN（7.66 M）
  ├── 性能上限: DPCRN-base NOISEX SDR 9.527 / PESQ 2.688 / STOI 89.13%（1115 M MACs/s）；All-skip α=1×10⁻⁴ → 9.337 / 2.645 / 88.53%，MACs 降到 749.8 M（−32.8%），参数量 0.5286 M → 0.5291 M
  ├── 参数量: DPCRN-base 0.5286 M；Intra-skip 0.5288 M；Inter-skip 0.5288 M；All-skip 0.5291 M（Skip-RNN 只多一个门控 FC，可忽略）
  ├── 消融关键发现: ① 更新率由 α 单调控制（Intra-skip α 从 5×10⁻⁵ 到 3×10⁻⁴，intra 更新率 0.696 → 0.265，MACs 1005 → 849.7 M）；② Intra-skip 在同 α 下更新率更低、但总 MACs 更高，因为 intra RNN 单块算力比 inter RNN 少约 1/4，所以指标反而更好；③ Fig. 5 在**同算力**下 All-skip 大多数点优于 DPCRN-S 与 DPCRN-P，压缩率 >~0.6 时 DPCRN-S 追平；④ Fig. 6 帧级更新率近似高斯分布，**峰值算力只降约 15%**；⑤ 测试集实测更新率**总是略高于**训练时设定的目标更新率（Fig. 5 绿线）
  ├── 遗留问题(你的机会): 48 ms「total latency」= 32 ms 窗 + 16 ms hop，论文未拆成算法/计算/端到端，是 2 ms 目标的 24 倍；MACs 是**测试集平均值**，最坏情况算力只降 15%，恰恰是硬件最不想要的输入相关算力；无 RTF / 目标硬件 / p99 / RAM / 量化 / 功耗；无 per-SNR 分层、无 DNSMOS、无 false-suppression、无 ASR WER、无 F0/prosody；VAD 只报 accuracy 88.2%，未报 recall/precision
  └── 跟哪篇像: [[wiki_low_latency/sources/2021/DPCRN Low-Latency Direction 2021]]（同一作者组的同源基线，本文只是把它的骨干当宿主）、[[wiki_low_latency/sources/2026/RT-Tango 2026]]（同样用「帧级稀疏」省算力，但 RT-Tango 用 FRS 对比过 learned skipping / SkipRNN / TinyLSTM）、[[wiki_low_latency/sources/2024/D-GRU 2024]]（同一问题谱系的反面：D-GRU 批评整步跳过导致每步算力波动）
~~~

# Inference skipping for more efficient real-time speech enhancement with parallel RNNs

> Xiaohuai Le; Tong Lei; Kai Chen; Jing Lu（南京大学近代声学重点实验室 / 声学研究所；NJU-Horizon Intelligent Audio Lab；南京人工智能高等研究院），arXiv:2207.11108v1 [cs.SD]，22 Jul 2022，共 11 页、8 图、4 表。基金：国家自然科学基金 11874219。
> 代码：<https://github.com/Le-Xiaohuai-speech/SKIP-DPCRN>（仓库名即 SKIP-DPCRN，这也是该模型在社区里通常被称作 **Skip-DPCRN** 的原因）；试听样例：<https://github.com/Le-Xiaohuai-speech/SKIP-DPCRN-samples>。
> 本页把论文的 "real-time" 拆成**因果性证据**、**算力口径**与**延迟账本**三笔账分别审计。

> [!warning] PDF 转换质量与阅读说明
> 原 PDF 共 11 页，PyMuPDF 文本抽取（`tmp/pdf_extract/2207.11108.txt`）可读性中等，但有四类问题必须看原 PDF 核对：
> 1. **公式**：抽取把求和号 Σ 与其上下标整体丢弃，导致 Eq. (19)（update rate）、Eq. (23)（L_Skip 第一形式）、Eq. (24)（MSE 目标率版）、Eq. (25)（MAE 版）、Eq. (27)（VAD 平滑）在纯文本里**只剩符号碎片，无法可靠识别**。本页这五条公式全部以**第 4 页与第 5 页渲染图**为准重写；Eq. (10)–(14)（Skip-RNN 机制）与 Eq. (20)（γ 缩放）抽取质量尚可，也已用第 3、4 页渲染图逐条核对。
> 2. **表格**：Table I–IV 在抽取中**列结构完全塌陷**（所有数字连成一串，表头与数据行错位）。本页 Table I 用**第 3 页渲染图**核对，Table II 与 Table III 用**第 6 页渲染图**核对，Table IV 用**第 9 页渲染图**核对。
> 3. **图**：Fig. 1–Fig. 8 的图体在抽取中**完全丢失**，只留 caption；抽取还保留了子图标签 `(a)`–`(f)` 的碎片。本页对 Fig. 3、Fig. 4 的描述来自**第 4 页渲染图**，Fig. 5、Fig. 6 来自**第 7 页渲染图**，Fig. 7 来自**第 8 页渲染图**，Fig. 8 来自**第 9 页渲染图**的实际看图结果。
> 4. **页眉与 DOI 是模板占位符**：每页页眉印的是 `JOURNAL OF LATEX CLASS FILES, VOL. 18, NO. 9, SEPTEMBER 2020`，第 1 页脚注印的 DOI 是 `10.1109/TASLP.2019.2915167`（2019 年的号）。二者都与本文（2022 年投稿、TASLP）不符，是 LaTeX 模板未替换的残留，**不能作为出版信息证据**。见 §4.5 的 [!question]。
>
> 论文未报告的字段（RTF、目标硬件、p50/p95/p99、峰值 RAM/SRAM、量化/定点、功耗、端到端 capture-to-playback、per-SNR 分层、DNSMOS SIG/BAK/OVL、false-suppression、ASR WER、F0/formant/prosody）在本页一律写为「未报告」，不作任何补写。

## 1. 他们为什么这么做？（motivation）

### 1.1 任务与对象

单通道时频域语音增强，面向「低时延 + 算力受限」的实时部署。论文的输入不是复数谱本身，而是三通道实数张量：

$$
X_r,\ X_i,\ X_p \;\longrightarrow\; \mathbf{X}\in\mathbb R^{T\times F\times C},\qquad C=3,
$$

其中 $X_r,X_i$ 是带噪谱的实部与虚部，$X_p$ 是对数功率谱；$T,F$ 分别是时间与频率维（**论文对这两个符号的定义自相矛盾，见 §4.5 的 [!question]**），$C=3$ 是通道数。带噪谱满足

$$
X(t,f)=S(t,f)+N(t,f), \tag{1}
$$

$S,N$ 分别为干净语音与噪声的复数谱。与 DPCRN [22] 只用 CRM 不同，本文按 PHASEN [26] 的做法**把幅度掩蔽与相位掩蔽分开估计**，输出三通道（幅度掩蔽 $M$ + 相位掩蔽 $\Phi$ 的实部与虚部），最终增强谱为

$$
\widetilde S(t,f)=X(t,f)\odot M(t,f)\odot\Phi(t,f), \tag{3}
$$

$\odot$ 为逐元素乘法。目标掩蔽不直接回归，而是用 signal approximation (SA) [27] 端到端优化，损失就是下面 Eq. (21) 的 complex compressed spectrum MSE。

### 1.2 论文动机

论文的出发点不是"再做一个更强的增强器"，而是**一个算力经济学问题**：实时系统的算力预算必须按最坏情况预留，而当时所有主流的压缩手段都做不到"按输入内容动态省算力"。

- 设计更小的网络 [13]、量化 [14]、剪枝 [15]、知识蒸馏 [17] 全都是**训练期定型**的手段。论文原话：「All these methods are applied at training stage and cannot be utilized to dynamically decrease the computational load according to the characteristics of input data during inference.」（p.1 §I）
- 而带噪语音的能量在时频面上**分布极不均匀**——实际信号里存在大片连续纯噪帧。这些帧本可以少算，却因为架构固定而被一视同仁地算满。
- Skip-RNN [19] 正是为"动态跳步"设计的：它理论上能在推理期省算力。但它在 SE 里的先例 [20]（Fedorov 等的 TinyLSTM）**出了音频伪影**，因为 RNN 跳步时输出掩蔽也停止更新，[20] 用的隐状态指数平滑「cannot effectively alleviate the problem」。

于是本文的核心判断是：

> 伪影不是 Skip-RNN 的固有缺陷，而是**宿主结构**的问题。只要让一部分 RNN 跳步时，掩蔽仍由**其他并行通路**继续更新，伪影就能被规避。

## 2. 之前的人怎么做不了？（limitation → gap）

| 路线 | 做法 | 为什么挡住了"推理期动态省算力" |
|---|---|---|
| 直接设计小网络 [13] | 训练期就锁定容量 | 容量是常数，无法随输入波动 |
| 量化 [14] | 降低权重/算子位宽 | 省的是**每次乘加的成本**，不减少乘加次数；且需重训练/校准 |
| 剪枝 [15], [16] | 移除不重要的权重 | 静态稀疏；论文的 DPCRN-P 还额外暴露了"高压缩率下难微调"的问题 |
| 知识蒸馏 [17], [18] | 大网络监督小网络 | 学生容量固定，同样与输入无关 |
| Skip-RNN [19] 直接用于 SE（引文 [20] TinyLSTM） | RNN 跳步 | **掩蔽也停止更新 → 音频伪影**；隐状态指数平滑缓解无效 |
| 本文 gap | —— | **能不能在不改架构、不改参数量、不重训练的前提下，让算力随输入内容下降，同时不产生伪影？** |

### 2.1 严格因果与延迟账本

> 审计口径：逐项给出 PDF 证据与本 Wiki 判定。判定三档为 `strict_causal` / `low_look_ahead` / `non_causal`；证据不足时标注 `unreported` 并说明缺什么。

| 审计项 | PDF 证据（页码/公式/图表） | 本 Wiki 判定 |
|---|---|---|
| 采样率 | 16 kHz（p.3 §II.B.1） | 明确 |
| 窗 | 32 ms（= 512 samples @16 kHz），sine window，p.5 §III.B | 论文只给"窗长"，未给 center/padding 设置 |
| hop | 16 ms（= 256 samples），50% overlap，p.5 §III.B | 明确；帧率 = 62.5 帧/s |
| FFT | 512，频率维 $F=257$（$512/2+1$，自洽），p.5 §III.B | 明确 |
| 延迟口径 | 「The window length and hop size used in our models are 32 ms and 16 ms respectively, **resulting in a total latency of 48 ms**.」（p.5 §III.B） | **未拆分的"total latency"**：48 = 32 + 16，论文未给推导、未区分算法/计算/端到端。见 §2.2 |
| intra-frame RNN 因果性 | 「The intra-frame RNNs are applied to the $f$-dimension of $\mathbf X_{en}$ to model the spectral patterns in a **single frame**」，形式是 **bi-directional** RNN，每向 $C_{hid}/2$（p.2 §II.B.1，Eq. (4)） | `strict_causal`（**时间维上**）：双向只发生在**单帧内部的频率轴**上，不跨帧读未来观测 |
| inter-frame RNN 因果性 | 「The **unidirectional** RNNs are used to model the time dependence of these sub-features in parallel **to guarantee the causality of the whole model**」（p.3 §II.B.1） | `strict_causal`（论文级声明 + 结构证据：单向 + 在 $F_{in}$ 个子带上并行）。**这是全文唯一的因果性论据** |
| encoder / decoder 卷积 | 5 层 Conv2D，strides $\{(2,1),(2,1),(2,1),(1,1),(1,1)\}$；kernel 从 $(2,5)/(2,3)$ 改为 $(1,5)/(1,3)$（p.3 §II.B.1） | **`unreported`**：论文**从未提到 padding**。若 stride 元组第一项对应频率轴（这是"压缩频率维"唯一自洽的读法），则 kernel 元组的时间轴核长为 5/3，卷积在时间上跨帧——此时 padding 方式（`same` 对称 vs `valid` 左对齐 vs 因果）直接决定是否读未来帧。**缺这一项就无法证明卷积层严格因果** |
| 归一化 | encoder 输入用 batch normalization [28]；DPRNN 块内用 instant layer normalization (iLN) [29]（Eq. (5)(8)） | iLN 的统计量按帧计算、不跨时间（沿用 [[wiki_low_latency/concepts/2107.05429-dual-path-recurrent-context]] 的读法）；但本文**未讨论** BN 的 running statistics 是否冻结 |
| 状态 | RNN hidden state、Skip-RNN 的门概率 $\tilde p_t$ 与二值门 $g_t$（Eq. (11)–(14)）、VAD 分支的 GRU 隐状态（维 32，p.4 §II.B.2） | 设计上支持流式；**warm-up、state reset、长流漂移、丢帧策略全部未报告** |
| 算力 | 基线 1115 M MACs/s（Table I）；Skip 后按 Table III 降到 749.8–1011 M | **输入相关**：所有 MACs 都是**测试集平均**。论文只给了帧级分布（Fig. 6）与"峰值降约 15%"的说法，**没有 worst-case / p99 算力** |
| 端到端 | 论文只到 "total latency of 48 ms" | ADC/DMA、I/O buffer、线程调度、DAC/playout、capture-to-playback、underrun/overrun **全部未报告** → 未验证 |

### 2.2 「48 ms」到底该怎么记账

论文只有一句话给出延迟，没有公式。本页把它拆成可核对的三层：

| 层次 | 数值 | 来源 / 缺口 |
|---|---|---|
| 前端分析延迟（论文口径） | 48 ms | 论文原话 "32 ms window + 16 ms hop → total latency of 48 ms"，**未给推导** |
| 其中窗长项 | 32 ms | $W=512$ samples @16 kHz |
| 其中 hop 项 | 16 ms | $h=256$ samples @16 kHz（50% overlap） |
| 模型计算延迟 | **未报告** | 无 RTF、无 per-frame wall-clock、无硬件 |
| 端到端 capture-to-playback | **未报告** | 无 ADC/DAC、I/O buffer、deadline miss |

> [!note] 「48 ms」这个口径在同一作者组内是自洽的
> 本库 [[wiki_low_latency/entities/DPCRN]] 记录，原版 DPCRN 报的是 25 ms 窗 + 12.5 ms hop = **37.5 ms "total latency"**。可见同一作者组一贯使用 **total latency = 窗长 + hop** 这一（粗糙的）约定，而不是 `window − hop` 或 `W/2`。
> 也就是说：**48 ms 是"论文口径的 total latency"，不是算法延迟，也不是端到端延迟**，更不能与其他论文按 `W/2` 或 `(W−h)/f_s` 记的账直接横比。本库的处置是把它登记为 `48ms-total-latency`，并注明三项拆分缺失。
> 顺带一个量级判断：**48 ms 是本方向约 2 ms 硬约束的 24 倍**，而且这还是论文最乐观的口径。

**判定结论**：Skip-DPCRN 的因果性证据强度**低于** [[wiki_low_latency/sources/2026/LaCo-SENet 2026]]（后者给出逐层 padding 分配式 + 状态选择算子 + 消融），也**低于** [[wiki_low_latency/sources/2026/RT-SEMamba 2026]]（后者至少说明了 center=False 与时间卷积只做左侧 padding）。本文只有一句 inter-frame RNN 单向的结构声明，**卷积层的 padding、STFT 的 center、归一化统计量、状态生命周期四项全部未报告**。因此本页判定为 `paper-claimed-causal`，**不标 `strict_causal`**。

## 3. 这个做法核心 trick 是什么？

### 3.1 一句话与三个组件

核心 idea 只有一个：**把"RNN 状态要不要更新"变成一个可学习、可正则、可在推理期缩放的二值门；宿主必须是 parallel RNN，这样 mask 才不会被"跳步"拖停。** 围绕它叠了三个工程组件（更新率正则、$\gamma$ 缩放、VAD 引导），但都是同一个 idea 的延伸。

~~~text
                     DPCRN-base（0.5286 M / 1115 M MACs/s）
                            │
              ① Skip-RNN 门控（Eq. 10–14）
                 状态间歇更新，mask 持续更新
                            │
        ┌───────────────────┼────────────────────┐
        ▼                   ▼                    ▼
  ② L_Skip 正则        ③ γ 缩放（Eq. 20）   ④ VAD 引导（Eq. 27）
   Eq.23 压门均值       推理期免重训练调率     纯噪帧 γ=0.4 / 语音帧 γ=1
   Eq.24/25 拉向目标率
        └───────────────────┴────────────────────┘
                            ▼
        算力随输入下降，参数量几乎不变（0.5286 → 0.5291 M）
~~~

![[wiki_low_latency/assets/2207.11108/2207.11108-page4-skiprnn-and-vad-architecture.png]]

> 图注：原论文第 4 页页面渲染。上方 **Fig. 3** 是 Skip-RNN 的三种视图：**(a)** 训练期的完整结构（$\tilde p_t$ 经门 $g_t$、round、累加 $\Delta\tilde p_t$ 后得到 $\tilde p_{t+1}$，下方 $\mathbf S$ 是被门控的状态更新函数，输出 $s_t$）；**(b)** 状态更新过程（$g_t=1$ 时走 $\mathbf S$）；**(c)** 状态跳过过程（$g_t=0$ 时 $\mathbf S$ 被旁路，$\tilde p$ 继续累加）。**虚线是关键**：$\Delta\tilde p_t$ 只依赖上一状态 $s_{t-1}$，状态不变时它是常量，因此 $g_t=0$ 时可以整块跳过计算量最大的 $\mathbf S$。下方 **Fig. 4** 是 DPCRN + Skip-RNN + VAD 的完整架构：encoder 输出分出一支 → 1×1 Conv（压到 1 通道）→ GRU → FC → VAD 概率；右侧标出 2 个 Skip-DPRNN 与 channel 数 3/32/32/32/64/128 的对称 encoder-decoder。图片为 PDF 页面复制，不是 AI 重画。

### 3.2 Trick ①：Skip-RNN 的状态门控（Eq. 10–14）

常规 RNN 的状态更新是每步必算：

$$
\tilde s_t = S(s_{t-1},\,x_t), \tag{10}
$$

$S(\cdot,\cdot)$ 是更新函数，$x_t$ 是 $t$ 时刻输入。Skip-RNN 引入一个状态更新概率 $\tilde p_t$，经 round 映射成二值门 $g_t\in\{0,1\}$：

$$
g_t = \mathrm{round}(\tilde p_t), \tag{11}
$$

$$
s_t = g_t\,\tilde s_t + (1-g_t)\,s_{t-1}. \tag{12}
$$

**Eq. (12) 就是整套方法的全部机制**：$g_t=1$ 就更新，$g_t=0$ 就原样保留上一步状态。概率由上一时刻的隐状态经一个 FC 层算出：

$$
\Delta \tilde p_t = \sigma\!\left(W_p s_{t-1}+b_p\right), \tag{13}
$$

$$
\tilde p_{t+1} = g_t\,\Delta\tilde p_t + (1-g_t)\left(\tilde p_t+\min\!\left(\Delta\tilde p_t,\ 1-\tilde p_t\right)\right). \tag{14}
$$

符号解释：

- $\tilde p_t$：**累积型**更新概率，不是每步重算的瞬时概率；
- $\Delta\tilde p_t\in(0,1)$：本步的概率增量，$\sigma$ 是 Sigmoid，把它限制在 0–1；
- $g_t$：二值门，决定状态更新（1）还是保持（0）；
- Eq. (14) 的两支：**更新时**（$g_t=1$）概率被重置为 $\Delta\tilde p_t$；**跳步时**（$g_t=0$）概率**继续累加** $\Delta\tilde p_t$（并用 $\min(\cdot,1-\tilde p_t)$ 夹住不超过 1），直到 $\tilde p_t$ 足够高、round 后变 1 才再次更新。

**为什么能省算力。** 论文 Fig. 3(c) 用虚线标出了关键点：$\Delta\tilde p_t$ 只依赖 $s_{t-1}$，状态固定时它就是常量，所以 **$g_t=0$ 时 Eq. (10) 这个"计算量最大的更新函数"可以整块跳过**。而 Eq. (13) 那个额外 FC 层的开销「is always negligible」。论文进一步指出一个很实用的性质：

> 「for the structure like GRU, since the output is equal to the hidden state, the FC layers following the RNN can also be skipped when the state is fixed.」

即 **GRU 的 output ≡ hidden state**，所以状态不更新时，紧随其后的 FC（以及 iLN 之后那部分）也可以一起跳——这正是 Table I 里 "Intra/Inter-frame RNN block" 的 MACs 能按 $(1-\text{update rate})$ 线性折算的原因（见 §4.4 的复算）。

### 3.3 Trick ②：更新率的三条正则（Eq. 19, 23–26）

更新率（update rate）定义为二值门的时频平均：

$$
\text{update rate}=\frac{1}{T F_{in}}\sum_t\sum_f g[t,f]. \tag{19}
$$

> [!contradiction] Eq. (19) 的定义与紧随其后的文字解释互相矛盾
> Eq. (19) 算的是 $g[t,f]=1$ 的比例，而由 Eq. (12)，$g=1$ **表示状态被更新**，所以它衡量的是**更新率**。
> 但论文紧接一句写：「The update rate calculates the percentage of the **skipped** states over a period of time.」（p.4 §II.B.2）
> 这句话把 update rate 说成了"被跳过的比例"。按 Eq. (12) 与 Table II/III 的数值方向（α 越大 → 正则越强 → 数值越小 → 论文说"更频繁跳步"），**唯一自洽的读法是 Eq. (19) 衡量更新比例，正文那句话是笔误**。本页所有表格按"更新率"读。

只用 Eq. (21) 训练**得不到高的跳步率**，所以要加正则项。论文给了三个版本：

**版本 A —— 直接压门均值（Eq. 23，最小化）：**

$$
L_{Skip}=\frac{1}{TF_{in}}\sum_i\left(\sum_t\sum_f g_{1;i}[t,f]+\sum_t\sum_f g_{3;i}[t,f]\right), \tag{23}
$$

$g_{1;i},g_{3;i}$ 分别是第 $i$ 个 Skip-DPRNN 模块里 Skip-intra-RNN 与 Skip-inter-RNN 的二值门。它**最小化二值门之和的均值**，等价于直接压更新率。

**版本 B —— 拉向目标更新率（Eq. 24，MSE）：**

$$
L_{Skip}=\sum_i\left[\left(\frac{1}{TF_{in}}\sum_t\sum_f g_{1;i}[t,f]-\mu_{1;i}\right)^2+\left(\frac{1}{TF_{in}}\sum_t\sum_f g_{3;i}[t,f]-\mu_{3;i}\right)^2\right], \tag{24}
$$

$\mu_{1;i},\mu_{3;i}$ 是第 $i$ 个模块里两条 Skip-RNN 的**目标**更新率。这一版让"想要多少更新率"变成一个显式超参数——**这是本页认为对硬件最有价值的一版**，因为它把平均算力从"学出来的"变成"指定的"。

**版本 C —— MAE 版（Eq. 25）：**

$$
L_{Skip}=\sum_i\left(\left|\frac{1}{TF_{in}}\sum_t\sum_f g_{1;i}[t,f]-\mu_{1;i}\right|+\left|\frac{1}{TF_{in}}\sum_t\sum_f g_{3;i}[t,f]-\mu_{3;i}\right|\right). \tag{25}
$$

论文只给了一句理由：「Compare with MSE, MAE can accelerate the convergence.」（p.5）——并且说明在**隐维较大**时（CRUSE/GCRN 的验证）MAE 收敛更快。

**总损失：**

$$
L = L_{SD}+\alpha L_{Skip}, \tag{26}
$$

$\alpha$ 是权重，$\alpha$ 越大跳得越多、更新率越低。

### 3.4 Trick ③：γ 缩放——推理期免重训练的更新率旋钮（Eq. 20）

这是本文最"工程友好"的一条。只要在 $\Delta\tilde p_t$ 上乘一个缩放因子：

$$
\Delta\tilde p_t = \gamma\,\sigma\!\left(W_p s_{t-1}+b_p\right), \tag{20}
$$

$\gamma<1$ 时概率累积变慢、状态更新率下降、省更多算力。论文明确写：

> 「This method can be easily implemented during inference **without retraining**.」（p.4 §II.B.2）

也就是说：**训练一次，推理时可以直接拧 $\gamma$ 换取算力**。这是它相对剪枝/量化/蒸馏（都必须重训练）的核心工程优势。

### 3.5 Trick ④：VAD 引导的差异化 γ

论文观察到一个现象：二值门 $g$ 的亮区分布与带噪谱的**谱包络高度相似**——纯噪帧跳得多，语音帧跳得少。也就是说**模型自己会"偷懒"**。于是把"偷懒"变成显式策略：纯噪帧用更小的 $\gamma$，语音帧保持 $\gamma=1$。

VAD 分支用多任务学习实现（Fig. 4）：encoder 特征 → 1×1 卷积（通道压到 1）→ GRU（隐维 32）→ FC → Sigmoid 得到语音概率，用 BCE 优化。标签由干净语音的能量阈值生成（ideal VAD）。推理期对估计输出做**向低置信度一侧偏置的平滑**：

$$
v(t)=
\begin{cases}
0, & \text{if } \tilde v(t),\tilde v(t-1),\cdots,\tilde v(t-9)=0,\\
1, & \text{otherwise},
\end{cases} \tag{27}
$$

其中 $v(t)$ 是第 $t$ 帧的最终 VAD 判决。论文明确说明这条规则是**用准确率换召回率**：「The smoothing strategy improves the recall ratio of the voice frames at the expense of VAD accuracy.」（p.6 §III.B）——即**只有当连续 10 帧都判 0 才判纯噪**，宁可把噪声帧误判成语音帧（少省算力），也不肯把语音帧误判成噪声帧（误伤人声）。这个偏向与本库「人声保留是一等目标」的取向一致，值得记一笔。

### 3.6 骨干：本文改了什么

| 组件 | 原版 DPCRN [22] | 本文 DPCRN-base | 理由 |
|---|---|---|---|
| RNN 单元 | LSTM | **GRU** [32] | 「yields little performance loss but **saves a quarter of the computational load**」 |
| 卷积核 | $(2,5)$ 与 $(2,3)$ | $(1,5)$ 与 $(1,3)$ | 降复杂度、性能损失不显著 |
| encoder | —— | 5 层 Conv2D，strides $\{(2,1),(2,1),(2,1),(1,1),(1,1)\}$ | 最后两层 stride 保持 $(1,1)$ 是为了给 DPRNN 保留足够频率分辨率，「which we found is important for speech quality」 |
| DPRNN 模块数 | 2 | 2（Skip 版） | —— |
| 隐维 | —— | $C_{hid}=128$（每个 GRU / Bi-GRU） | —— |
| 参数量 | —— | **0.53 M** | —— |

> [!note] 别把这个 0.53 M 的 DPCRN-base 与 DNS-3 的 DPCRN 混为一谈
> 论文自己在 §I 里引用 DPCRN [22] 的 DNS-3 成绩时写的是「**0.8 M** parameters and **3.7 G** MACs」（并顺带说明 Rank-1 是 6.4 M / 6.0 G、Rank-2 是 5.2 M / 52.5 G，其中 Rank-2 的复杂度是**作者自己实现后算的**，因为原论文没给）。
> 但本文的 baseline 是 **0.5286 M / 1115 M MACs/s**——这是同一作者组**按 GRU 化 + 缩小卷积核**重新调过的小版本。本库 [[wiki_low_latency/entities/DPCRN]] 记的也是「约 0.8M 参数」。引用数字时必须写清是哪一版。

### 3.7 算力分布：为什么压缩重点在 DPRNN 模块

Table I（p.3，第 3 页渲染图核对）：

| Operator type | MACs (M) | Parameters (M) |
|---|---:|---:|
| Encoder | 83.71 | 0.042 |
| Intra-frame RNN block × 2 | 360.6 | 0.180 |
| Inter-frame RNN block × 2 | 458.8 | 0.230 |
| Decoder | 212.0 | 0.077 |
| **All** | **1115.1** | **0.529** |

本页按 Table I 复算（论文未给出这两个比例）：DPRNN 模块合计 $360.6+458.8=819.4$ M MACs，占总算力的 **73.5%**；参数量合计 0.410 M，占 **77.5%**。所以"压缩重点放在 DPRNN 模块"是有据的。论文还补了一句方法论理由：卷积层更容易被量化 [14] 压缩，因此本文把火力集中在 RNN 上——**这暗示了 Skip-RNN 与量化是正交、可叠加的**。

## 4. 实验里哪个消融最关键？

### 4.1 数据与评价

| 项目 | 论文设置 |
|---|---|
| 干净语音 | WSJ0 SI-84 [33]，14633 条（约 25 h）、120 说话人；训练 12776 / 验证 1206 / 测试 651 |
| 噪声 | DNS-3 Challenge [24] 噪声集，60000 条、共 150 h，来自 DEMAND [34] + Audioset [35] + Freesound |
| 数据增强 | 干净语音切成 11212 段 8 s；30% 经二阶 IIR 谱增强滤波（系数均匀分布于 $[-3/8,3/8]$，与 [12][13] 一致）；一半音频与 openSLR26/openSLR28 [37] 的 RIR 卷积；SNR 随机取 $-5$ 到 $5$ dB；整体电平按十进对数上的高斯缩放（均值 $-0.5$、方差 1），该缩放因子同时用于 Eq. (21) 的归一化 |
| 测试噪声（**两个未见集**） | ① MUSAN [38] 音乐；② NOISEX92 [39] 的 babble、factory1、f16。SNR $-5/0/5$ dB，每档每集 651 条混合 |
| 长音频测试集 | 测试语音两两拼接，每对之间 8 s 静音；与音乐噪声按 SNR 均匀采样于 $-5$ 到 $5$ dB 混合。共 **3906** 条短音频 + **325** 条长音频 |
| 指标 | SDR [42]、PESQ [43]、STOI [44] |
| 训练 | Adam [41]，batch 16，初始 lr 1e-3；验证损失 10 个 epoch 不降则减半，20 个 epoch 不降则 early stop |
| 剪枝基线配置 | 先用 Eq. (21) + ℓ2 范数正则 [40] 训练，再按幅度剪掉 RNN 与对应 FC 的权重，最后用原损失 Eq. (21) 微调 50 个 epoch |
| 框架/硬件 | TensorFlow；训练用 Nvidia TITAN Xp |

> [!note] 测试集的噪声类型对低时延方向是加分的
> NOISEX92 里的 **babble** 是本库最关心的"竞争说话人/人声噪声"的代理；SNR 下探到 **−5 dB**。这比只测稳态噪声的论文强。
> 但**论文把 −5/0/5 三档合并成一个数报**（Table II 每格只有 1 个值），所以**per-SNR 分层结果完全没有**——无法回答"−5 dB 下 SDR/PESQ 掉多少"。

### 4.2 主结果（Table II，照抄原文数字）

![[wiki_low_latency/assets/2207.11108/2207.11108-page6-table2-table3.png]]

> 图注：原论文第 6 页页面渲染，用于核对 **Table II**（两个测试集上的 SDR/PESQ/STOI 与 update rate，含 Noisy 行）与 **Table III**（各模型的 MACs、参数量与 intra/inter RNN 分项更新率）。注意 Table II 的 Update rate 与 Table III 的分项更新率**聚合口径不同、数值不一致**，见 §4.5 的 [!question]。图片为 PDF 页面复制，不是 AI 重画。

**NOISEX（babble / factory1 / f16，SNR −5/0/5 dB 混合）：**

| Model | $\alpha$ | SDR (dB) | PESQ | STOI (%) | Update rate |
|---|---|---:|---:|---:|---:|
| Noisy | — | 0.091 | 1.433 | 74.94 | — |
| DPCRN-base | — | **9.527** | **2.688** | **89.13** | 1.00 |
| Intra-skip | $5\times10^{-5}$ | 9.508 | 2.681 | 88.87 | 0.712 |
| Intra-skip | $1\times10^{-4}$ | 9.448 | 2.670 | 88.86 | 0.482 |
| Intra-skip | $2\times10^{-4}$ | 9.394 | 2.672 | 88.76 | 0.436 |
| Intra-skip | $3\times10^{-4}$ | 9.358 | 2.649 | 88.49 | 0.271 |
| Inter-skip | $5\times10^{-5}$ | 9.409 | 2.666 | 88.67 | 0.765 |
| Inter-skip | $1\times10^{-4}$ | 9.424 | 2.662 | 88.63 | 0.640 |
| Inter-skip | $2\times10^{-4}$ | 9.355 | 2.633 | 88.24 | 0.426 |
| Inter-skip | $3\times10^{-4}$ | 9.355 | 2.640 | 88.30 | 0.359 |
| All-skip | $5\times10^{-5}$ | 9.405 | 2.654 | 88.57 | 0.745 |
| All-skip | $1\times10^{-4}$ | 9.337 | 2.645 | 88.53 | 0.577 |

**MUSAN（音乐噪声）：**

| Model | $\alpha$ | SDR (dB) | PESQ | STOI (%) | Update rate |
|---|---|---:|---:|---:|---:|
| Noisy | — | 0.043 | 2.004 | 80.76 | — |
| DPCRN-base | — | **11.54** | **3.105** | **93.69** | 1.00 |
| Intra-skip | $5\times10^{-5}$ | 11.53 | 3.084 | 93.55 | 0.679 |
| Intra-skip | $1\times10^{-4}$ | 11.48 | 3.076 | 93.54 | 0.456 |
| Intra-skip | $2\times10^{-4}$ | 11.37 | 3.065 | 93.41 | 0.419 |
| Intra-skip | $3\times10^{-4}$ | 11.24 | 3.042 | 93.17 | 0.258 |
| Inter-skip | $5\times10^{-5}$ | 11.45 | 3.068 | 93.38 | 0.709 |
| Inter-skip | $1\times10^{-4}$ | 11.39 | 3.059 | 93.30 | 0.545 |
| Inter-skip | $2\times10^{-4}$ | 11.26 | 3.031 | 93.01 | 0.393 |
| Inter-skip | $3\times10^{-4}$ | 11.27 | 3.024 | 93.02 | 0.328 |
| All-skip | $5\times10^{-5}$ | 11.42 | 3.056 | 93.29 | 0.706 |
| All-skip | $1\times10^{-4}$ | 11.29 | 3.014 | 93.20 | 0.524 |

论文从这两张表读出的四条结论（p.7 §IV.A）：

1. 引入 Skip-RNN **显著省算力、性能退化有限**；
2. 性能与算力**正相关**；
3. $\alpha$ 增大 → 跳步更频繁 → 更新率更低，可以视为一种**动态时间维剪枝**（dynamic temporal pruning）；更新率同时取决于 $\alpha$ 与**推理时的噪声特性**——MUSAN 上所有指标更好而更新率更低，说明模型在更"温和"的噪声下更会偷懒；
4. All-skip 整体略差，但在 $\alpha=1\times10^{-4}$ 时**以更少的 MACs 超过了两个 Inter-skip 模型**。

### 4.3 算力与更新率（Table III，照抄原文数字）

| Models | $\alpha$ | Intra-RNN update rate | Inter-RNN update rate | MACs (M) | Para. (M) |
|---|---|---:|---:|---:|---:|
| DPCRN-base | — | 1.00 | 1.00 | 1115 | 0.5286 |
| Intra-skip | $5\times10^{-5}$ | 0.696 | 1.00 | 1005 | 0.5288 |
| Intra-skip | $1\times10^{-4}$ | 0.469 | 1.00 | 923.6 | 0.5288 |
| Intra-skip | $2\times10^{-4}$ | 0.427 | 1.00 | 908.6 | 0.5288 |
| Intra-skip | $3\times10^{-4}$ | **0.265** | 1.00 | 849.7 | 0.5288 |
| Inter-skip | $5\times10^{-5}$ | 1.00 | 0.737 | 1011 | 0.5288 |
| Inter-skip | $1\times10^{-4}$ | 1.00 | 0.575 | 994.4 | 0.5288 |
| Inter-skip | $2\times10^{-4}$ | 1.00 | 0.410 | 844.2 | 0.5288 |
| Inter-skip | $3\times10^{-4}$ | 1.00 | **0.344** | 814.0 | 0.5288 |
| All-skip | $5\times10^{-5}$ | 0.702 | 0.749 | 892.5 | 0.5291 |
| All-skip | $1\times10^{-4}$ | 0.520 | 0.581 | **749.8** | 0.5291 |

> [!note] 本页复算：Table III 的 MACs 可以用 Table I 精确重建（10 行中 8 行完全吻合）
> 因为 GRU 的 output ≡ hidden state，状态不更新时后续 FC 也一起跳，所以省下的算力应与 RNN 块的 MACs 成**线性**关系：
> $$\text{MACs}=1115.1-360.6\,(1-r_{\text{intra}})-458.8\,(1-r_{\text{inter}}).$$
> 逐行代入 Table III 的更新率：Intra-skip 四行预测 1005.5 / 923.6 / 908.5 / 850.1（表值 1005 / 923.6 / 908.6 / 849.7 ✓）；All-skip 两行预测 892.4 / 749.8（表值 892.5 / 749.8 ✓✓）；Inter-skip 的 $2\times10^{-4}$ 与 $3\times10^{-4}$ 预测 844.4 / 814.1（表值 844.2 / 814.0 ✓）。
> **但 Inter-skip 的前两行对不上**：$5\times10^{-5}$ 预测 994.4（表值 1011），$1\times10^{-4}$ 预测 920.1（表值 994.4）。注意 994.4 恰好是 $r_{\text{inter}}=0.737$ 的预测值——**看起来 Table III 的 Inter-skip MACs 列前两项错位了一行**。详见 §4.5。

论文对 Intra 与 Inter 差异的解释（p.7）：**同 $\alpha$ 下 Intra-skip 的更新率更低、但总 MACs 更高**，因为「the amount of computation of an intra-frame RNN is a quarter fewer than an inter-frame RNN」（按 Table I 复算：$360.6/458.8=0.786$，即约 3/4 ✓）。所以同 $\alpha$ 时 Intra-skip 的**指标反而更好**——它用更少的算力节省换来了更小的质量损失。

### 4.4 最关键的消融：同算力下的三方对比（Fig. 5）

这是本文**最有信息量、也最容易被忽略**的一组对照。

![[wiki_low_latency/assets/2207.11108/2207.11108-page7-fig5-fig6-compression-comparison.png]]

> 图注：原论文第 7 页页面渲染。上方 **Fig. 5** 的三张子图分别是 SDR / PESQ / STOI 随 **MACs（横轴，单位 M）** 的变化：蓝线 DPCRN-S（直接训练更小的模型）、橙线 DPCRN-P（结构化剪枝）、绿线 DPCRN-All-skip（本文）。三条线都扫 5 个压缩率/目标更新率 $\{0.3,0.4,0.5,0.6,0.7\}$，**横轴统一到实际 MACs**，所以这是真正意义上的"同算力比较"。右下 **Fig. 6** 是 DPCRN-All-skip（$\alpha=1\times10^{-4}$）在 NOISEX 与 MUSAN 上**帧级更新率的分布**（小提琴图），用于支撑"峰值算力降约 15%"的说法。图片为 PDF 页面复制，不是 AI 重画。

**实验设置**：用 Eq. (26) + Eq. (24)（$\alpha=1\times10^{-2}$）训练 DPCRN-All-skip，目标更新率分别设为 $\{0.3,0.4,0.5,0.6,0.7\}$。对照的两个模型把 intra/inter RNN 的隐维降到 $\{(48,52),(60,65),(74,77),(86,89),(96,100)\}$，对应压缩率 $\{0.3,0.4,0.5,0.6,0.7\}$，使三者算力可比。

**论文报告的结果与解读（p.7 §IV.B）：**

- 三条曲线中，绿线（本文）的**实际平均算力总是高于期望值**——即测试集上的实际更新率**总是略高于训练时设定的目标更新率**。论文把这归因于泛化差异，并**没有进一步解释或修正**。这是一个诚实但不完整的自陈。
- 即使有上述偏差，**DPCRN-All-skip 在大多数点上仍优于另外两者**。
- **压缩率 > ~0.6 时，DPCRN-S 追平 DPCRN-All-skip**——也就是说，在轻度压缩区，动态跳步相对"直接训小模型"的优势消失。
- **DPCRN-P 在高压缩率下最差，但随着压缩率下降反而逐渐超过 DPCRN-S**。论文给的解释是：剪枝正则带来显著的权重稀疏性，高压缩率下难以微调。

> [!note] 为什么这组对照比 Table II/III 更关键
> Table II/III 只回答了"跳步之后掉了多少"，**没有回答"省下的算力拿去做别的会不会更好"**。Fig. 5 把横轴统一成实际 MACs，直接与两个最强的替代方案对撞，才是本文主张"superiority over strategies like network pruning or directly training a smaller model"的唯一证据。
> 但要注意它的边界：横轴是 **MACs 平均值**，不是 deadline；三条线的压缩率定义**互不相同**（一个是目标更新率，一个是隐维缩放），所以"同算力"是事后对齐的，不是同一套设计变量。

### 4.5 原文疑点与内部不一致（本页读出的）

> [!question] 疑点 1：$T$ 与 $F$ 到底哪个是时间、哪个是频率？
> 论文写「$T$, $F$ and $C=3$ represent the dimensions of **frequency, time** and channel, respectively」（p.2 §II.B.1），但同一节的 Eq. (4) 又把 $\mathbf X_{in}[t,:,:]$ 称为「the sub-feature at **time** index $t$」。
> 两处直接冲突。从"encoder 用 stride 压缩**频率**维、最后两层 stride 取 $(1,1)$ 以保住频率分辨率"这条描述反推，**stride 元组的第一项应对应频率轴**；若 kernel 元组沿用同一约定，则 kernel $(1,5)/(1,3)$ 的**时间轴核长为 5/3**，卷积在时间上跨帧。
> 由于论文**完全没提 padding**，本页无法判定这些卷积是否读未来帧。这是本文因果性证据链上最大的缺口。

> [!question] 疑点 2：Table III 的 Inter-skip MACs 疑似错位一行
> 见 §4.3 的复算：用 Table I 的模块 MACs 与 Table III 自己的更新率，可以精确重建 10 行中的 8 行；Inter-skip 的 $5\times10^{-5}$（表值 1011）与 $1\times10^{-4}$（表值 994.4）两行对不上，而 994.4 恰是 $r_{\text{inter}}=0.737$ 的预测值。
> 本页**不修改表值**，只记录：这两格与同表其余数字不自洽，引用时应以复算值为准或回查作者代码。

> [!question] 疑点 3：Table II 的 Update rate 与 Table III 的分项更新率无法互相复算
> 论文说 Table II 的更新率是「the average update rate of **all the test sets**」，Table III 是各 RNN 块的更新率。
> 但以 Inter-skip $\alpha=1\times10^{-4}$ 为例：Table II 记 **0.640**，Table III 记 intra 1.00 / inter 0.575。按 MACs 加权平均得 0.762，按算术平均得 0.788，**都不等于 0.640**。All-skip $\alpha=1\times10^{-4}$：Table II 记 0.577，Table III 记 0.520 / 0.581，加权平均 0.554、算术平均 0.551，**也不等于 0.577**。
> 两表的聚合口径未被说明。引用"更新率"时必须写清取自哪张表。

> [!question] 疑点 4：Eq. (21) 的 $c$ 与 $\lambda$ 归因于引文 [21]，但数值与本库记录的 [21] 不一致
> 论文写「the spectrogram compression factor $c$ and the loss weight factor $\lambda$ are respectively set to **0.3 and 0.1** for higher speech quality [21]」。
> 本文的引文 [21] 正是本库 [[wiki_low_latency/sources/2021/Noise Suppression Losses 2021]]（Braun & Gamper, arXiv:2111.11606）。该页记录的 $c=0.3$ **一致**，但该文自己选定的平衡点是 **$\lambda=0.3$**（其 Fig. 4 扫描后选定），并非 0.1。
> 本地 PDF 无法判定这是引用笔误（$\lambda=0.1$ 更可能来自 CRUSE [12] 或 DPCRN [22]），还是 [21] 的不同版本取值不同。**引用时不要把这个 0.1 当作 [21] 的结论。**

> [!question] 疑点 5：出版信息无法从本地 PDF 自证
> 本地 PDF 的页眉是 `JOURNAL OF LATEX CLASS FILES, VOL. 18, NO. 9, SEPTEMBER 2020`（模板占位符），第 1 页脚注 DOI 是 `10.1109/TASLP.2019.2915167`（2019 年的号，且与 arXiv 编号 2207.11108 完全对不上）。
> 因此本页 frontmatter 里的 venue「IEEE/ACM TASLP, vol. 30, pp. 2411-2421, 2022」来自 arXiv 元数据/外部信息，**不是本地 PDF 内可核对的证据**。`evidence_policy: local_pdf_only` 下，这条应视为待验证。

> [!note] 疑点 6：Fig. 6 的画法与文字描述不完全一致
> 正文说帧级算力「is distributed like a **Gaussian** distribution」（p.7 §IV.A），但 Fig. 6 实际画的是**小提琴图**（两个测试集各一个），不是拟合的高斯曲线。另外 "peek" 应为 "peak"。
> 论文未给出该分布的均值/方差/分位数，所以"峰值算力降约 15%"**只能引用为论文说法，无法从图上复算**。

### 4.6 泛化验证（Table IV，照抄原文数字）

![[wiki_low_latency/assets/2207.11108/2207.11108-page8-fig7-binary-gate-vad.png]]

> 图注：原论文第 8 页页面渲染，**Fig. 7** 的六个子图。**(a)** 带噪谱；**(b)** 干净语音的 VAD 标签（二值阶梯）；**(c)** DPCRN-All-skip 增强谱；**(d)** 最后一个 Skip-inter-RNN 的二值门 $g_{3;2}$ 可视化（横轴时间、纵轴并行 RNN 序号，亮=状态更新、暗=跳步）；**(e)** 加 VAD 引导后的增强谱；**(f)** 加 VAD 引导后的门可视化。对比 (d) 与 (f) 可以直观看到：VAD 引导后纯噪段的暗区显著增多（跳得更多），而语音段的亮纹保持不变——这正是 §3.5 的机制在起作用。图片为 PDF 页面复制，不是 AI 重画。

论文把同一策略套到另外两个实时 SE 模型上验证泛化性：

| Model | Params | 帧长 / hop | NOISEX SDR | NOISEX PESQ | NOISEX STOI | NOISEX UR | MUSAN SDR | MUSAN PESQ | MUSAN STOI | MUSAN UR |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Noisy | — | — | 0.091 | 1.433 | 74.94 | — | 0.043 | 2.004 | 80.76 | — |
| CRUSE-base | 8.58 M | 20 / 10 ms | 8.423 | 2.457 | 85.65 | 1.00 | 10.29 | 2.834 | 91.41 | 1.00 |
| CRUSE-skip | 8.58 M | 20 / 10 ms | 8.426 | 2.457 | 85.58 | **0.496** | 10.25 | 2.822 | 91.27 | **0.491** |
| GCRN-base | 7.66 M | 20 / 10 ms | 9.393 | 2.359 | 87.32 | 1.00 | 11.19 | 2.654 | 91.58 | 1.00 |
| GCRN-skip | 7.66 M | 20 / 10 ms | 9.348 | 2.364 | 87.07 | **0.697** | 11.14 | 2.650 | 91.36 | **0.642** |

（UR = update rate。CRUSE 按 [21] 搭建，8 层卷积 + 4 个并行 GRU 子组；GCRN 按 [11] 搭建，但 LSTM 换成 GRU；两者都用 Eq. (26) + **Eq. (25) MAE 正则**训练，因为隐维大时 MAE 收敛更快。）

论文的解读：两个模型在显著更低的更新率下**性能基本持平**，说明 Skip-RNN「can be fused into **any model that use parallel RNN structure**」。至于 **GCRN-skip 的更新率高于 CRUSE-skip**，论文的解释是 GCRN 用了**更少的并行 RNN、更大的隐维**，因而更难优化。

> [!note] 这一句是本篇最需要记住的结论，也是最需要打问号的结论
> 「任何使用 parallel RNN 结构的模型都可以融合 Skip-RNN」是一个**结构条件**，不是普适结论：它要求宿主里存在**多条并行 RNN 通路**，且掩蔽的更新不完全依赖被跳步的那一条。
> 反过来说：**串行 RNN 宿主（例如单条单向 GRU 从头贯到尾的模型）无法直接套用本文的结论**——那正是引文 [20] TinyLSTM 遇到伪影的结构。本页认为这条限制条件应该被显式写进任何引用本文的地方。

### 4.7 长音频与 VAD 引导（Fig. 8）

> [!note] Fig. 8 与 Table IV 的核对资产
> 本页未嵌入 Fig. 8（长音频测试集上 SDR / PESQ / STOI 随 $\gamma$ 的变化，以及语音帧与纯噪帧的平均更新率）与 Table IV 的页面渲染，核对请见 `wiki_low_latency/assets/2207.11108/2207.11108-page9.png`（原论文第 9 页）。图 (a)(b)(c) 的蓝线为理想 VAD、橙线为估计 VAD、绿色虚线为 DPCRN-base；图 (d) 给出不同 $\gamma$ 下两类帧的平均更新率。

设置：DPCRN-All-skip + VAD 估计器联合训练，**目标平均更新率设为 0.5**；只在纯噪帧上施加不同的 $\gamma$。论文报告（p.8 §IV.C）：

- $\gamma<0.3$ 时性能**显著退化**；
- 用**理想** VAD 标签时各指标**并非单调**，且 **$\gamma=0.4$ 时 SDR 就能追平 DPCRN-base**（图 (a) 的绿色虚线）。论文的解释是：**纯噪帧本来就可以被更激进地衰减**，所以在这里多跳几步不会伤 SDR；
- 用**估计** VAD 弱于理想 VAD，但 SDR 与 PESQ 曲线仍显示小 $\gamma$ 的收益；
- 综合最优是 **$\gamma=0.5$**，此时**纯噪段 DPRNN 模块的算力仅为基线的 28%**；
- Fig. 8(d)：**语音帧的更新率随 $\gamma$ 几乎恒定，纯噪帧的更新率与 $\gamma$ 近似线性**——「which allows the model to preserve speech while further reduce the computational load」；
- VAD 估计器在长音频测试集上的**准确率 88.2%**；论文明确声明「the VAD estimator is **not the focus** of this paper and in practice better estimators may lead to higher performance」。

> [!warning] 「28%」是分段条件数，不是整体算力
> 论文写的是「the computational load of the DPRNN modules **at pure noise segments** is only 28% of the baseline」——**限定在纯噪段**。
> 由于语音帧的更新率被刻意保持在基线水平（Fig. 8(d)），整段长音频的**总**算力节省必然远小于 72%。论文没有给出"整段平均省了多少"这个数，也没有给出语音/噪声的时间占比。
> 把 28% 读成"整体省 72%"是**过度解读**。

### 4.8 一个诚实的自陈与一个未解释的观察

- **诚实自陈**：Fig. 5 的绿线——**测试集上实测更新率总是略高于训练时设定的目标更新率**。这意味着 Eq. (24) 的目标率只能作为**下界**，部署时不能直接把它当算力预算。论文没有分析原因（是训练/测试分布差异，还是 round 操作的偏置）。
- **未解释的观察**：MUSAN 上所有指标都优于 NOISEX，而**更新率反而更低**。论文把这解读为"模型在更温和的噪声下更会偷懒"，并用它论证"进一步降算力是可能的"。但这也意味着：**本文报告的 MACs 取决于测试集的噪声难度**，换一个更难的数据集，同一模型的 MACs 会更高。跨论文比较 MACs 时必须固定测试集。

## 5. 这个方向还剩什么问题没解决？（future work / limitation）

**论文自己承认/隐含的：**

1. **VAD 不是重点**：「the VAD estimator is not the focus of this paper」（p.8），只报了一个 accuracy 88.2%，没有报 recall/precision，也没有做更好的估计器。
2. **目标更新率与实际更新率有系统性偏差**（Fig. 5 绿线），论文未解释也未修正。
3. **MAE vs MSE 只给了一句理由**（"accelerate the convergence"），没有收敛曲线或消融数据。
4. 论文**没有 future work 章节**，结论段只是重述贡献。

**本页读出的隐藏问题（本库关注）：**

5. **48 ms 是 2 ms 目标的 24 倍，且未拆分。** 论文只有一句 "resulting in a total latency of 48 ms"，没有算法延迟 / 计算延迟 / 端到端的分账。要放进本库的统一 ledger，必须补 RTF、I/O buffer 与目标硬件测量。
6. **算力是输入相关的，而输入相关的算力恰恰是硬件的敌人。** 本文所有 MACs 都是**测试集平均值**。论文唯一关于尾部的信息是「峰值算力降约 15%」（Fig. 6）——也就是说，**最坏情况下算力几乎没降**（只降 15%）。对于一个需要按最坏情况预留预算的实时系统，"平均省 33%、峰值省 15%"的价值远小于"平均省 33%"这个数字给人的印象。
   - 这一点与本文自己的动机（"实时应用难以部署强大 DNN 因为算力高"）存在张力：如果预算必须按峰值预留，那 Skip-RNN 省下的是**平均功耗/发热**，而不是**最坏情况 deadline**。论文没有讨论这个区分。
7. **没有任何运行时证据。** 未报告：RTF、目标硬件（CPU/ARM/DSP/NPU）、p50/p95/p99、deadline miss、峰值 RAM/SRAM、量化/定点精度、功耗、batch=1 长流稳定性、state reset、warm-up、underrun/overrun。
   - 注意：**算力下降 ≠ 延迟下降**。在未优化的实现里，条件跳步会引入分支预测失败与数据依赖停顿，实际 wall-clock 收益可能远小于 MACs 收益。本文完全没有测量这一点。
8. **人声保留维度基本空白。** 只有 SDR / PESQ / STOI，且三档 SNR 被合并报告。**未报告**：per-SNR 分层（−5/0/5 dB 各一列）、DNSMOS SIG/BAK/OVL、false-suppression、voiced energy 保留、F0/formant/prosody continuity、ASR WER。
   - 唯一与"人声"沾边的证据是 VAD 的 accuracy 88.2%，以及 Eq. (27) 那条**用准确率换召回率**的平滑规则。但论文**没有报告召回率**，而召回率恰恰是它自己声明的设计目标——这是一个可以低成本补上却缺失的关键数字。
   - 一个可见的**风险信号**：PESQ 与 STOI 在激进档（Intra-skip $\alpha=3\times10^{-4}$）分别掉到 2.649 / 88.49，而更新率只有 0.265。质量-算力曲线在低更新率区**开始变陡**（PESQ 从 2.688 → 2.649 掉 0.039，但 SDR 掉 0.169 dB），说明继续压更新率的边际代价在上升。
9. **因果性证据链不完整。** 卷积 padding、STFT center、BN running statistics、状态生命周期四项未报告（详见 §2.1）。本页因此判定为 `paper-claimed-causal`。
10. **训练细节不足以完全复现。** 未报告：训练总步数/epoch 数、GPU 数量、随机种子数、$L_{Skip}$ 的 $\mu$ 取值（只在 Fig. 5 里说目标率是 0.3–0.7，没说训练时具体怎么设）、VAD 分支损失与主损失的加权方式、Eq. (27) 中 10 帧窗口的选择依据。
11. **Table III 疑似错位、Table II/III 聚合口径不明、Eq. (19) 定义与正文矛盾**（§4.5）。复现时这三处需要回查作者代码。

**对当前方向的可迁移启示：**

- **"推理期免重训练调算力"这个性质本身非常有价值**，而且与剪枝/量化/蒸馏正交，可以叠加。但它要真正服务 2 ms 级系统，必须补上**最坏情况算力上界**——例如把 Eq. (24) 的目标率改成"每 N 帧的滑动窗口内更新次数不超过 K"这类**局部约束**，而不是全句平均。
- **"GRU 的 output ≡ hidden state，所以 FC 也能一起跳"是一个可直接复用的工程细节**：任何用 GRU（而非 LSTM）做瓶颈的流式模型，都能把状态跳过扩展到后续 FC。
- **Eq. (27) 的"连续 10 帧全 0 才判噪"偏置策略**是本库可以直接抄的一个小技巧：它把 VAD 的判决偏向"语音侧"，与「人声保留是一等目标」的取向一致。

## 6. 本论文在库中的位置关联（cross-reference matrix）

| 关系 | 库中论文/概念 | 关联与差异 |
|---|---|---|
| **前身/基石（宿主模型）** | [[wiki_low_latency/sources/2021/DPCRN Low-Latency Direction 2021]]、[[wiki_low_latency/entities/DPCRN]]、[[wiki_low_latency/concepts/2107.05429-dual-path-recurrent-context]] | 同一作者组的 DPCRN 本尊。本文不改骨干的**拓扑**，只把它的 parallel RNN 当宿主；同时做了三处收缩（LSTM→GRU、kernel $(2,5)/(2,3)$→$(1,5)/(1,3)$、0.8 M→0.53 M）。**关键差异**：DPCRN 的 intra-chunk 是 BiLSTM、inter-chunk 是单向 LSTM；本文把两者都换成 GRU 并加上门控。注意 DPCRN 报 37.5 ms total latency、本文报 48 ms，是同一口径（窗+hop）下的不同前端配置 |
| **前身/基石（被引进的方法）** | Campos et al., *Skip RNN*（ICLR 2018，本文引文 [19]） | Skip-RNN 的原始出处。库中暂无该页。本文的贡献**不是**提出跳步机制，而是**发现它需要 parallel RNN 宿主才不产生伪影** |
| **前身（失败先例）** | Fedorov et al., *TinyLSTMs*（Interspeech 2020，本文引文 [20]） | 本文明确点名它「One notable drawback … the output mask stops updating when the RNN skips, which results in audio artifacts」。**库中暂无该页**——本库最接近的同类页面是 [[wiki_low_latency/sources/2021/Teacher-Student Wave-U-Net 2021]]，但那是 Nakaoka 等的 Wave-U-Net 蒸馏工作，**与 TinyLSTM 无关**，不能互相替代 |
| **同源方法（数据增强与损失）** | [[wiki_low_latency/sources/2021/Noise Suppression Losses 2021]] | 本文引文 [21] 就是这篇（Braun & Gamper）。本文的 $c=0.3$、IIR 谱增强、RIR 增强、$L_{SD}$ 形式都源自这条线。**但 $\lambda$ 取值不一致**（本文 0.1，该文自选 0.3）——见 §4.5 疑点 4 |
| **同分支竞品（直接对撞）** | [[wiki_low_latency/sources/2024/D-GRU 2024]] | **本轮同时摄取**。D-GRU 在 Related Work 里点名批评 Skip-RNN 系列「整步跳过全部神经元导致**每步算力波动**」，并把本文列为引文 [31]。这是本文主张的正面对立命题：本文用"平均省 33%"论证价值，D-GRU 用"每步算力波动"论证这是缺陷。两条记录必须一起读。⚠️ 该页正在并行摄取，措辞待落地后复核 |
| **同分支竞品（同一思路的另一个实现）** | [[wiki_low_latency/sources/2026/RT-Tango 2026]]、[[wiki_low_latency/entities/RT-Tango]] | RT-Tango 用 FRS（frame-level recursive skipping 一类机制）并**对比了 learned skipping / SkipRNN / TinyLSTM**，与本文的结论可以互证。RT-Tango 是 8 ms 论文级算法延迟、双耳分布式；本文是 48 ms、单通道。两者都把"帧级稀疏"当作省算力的抓手 |
| **同分支竞品（低时延时频掩蔽）** | [[wiki_low_latency/sources/2023/FSB-LSTM 2023]]、[[wiki_low_latency/sources/2022/DeepFilterNet2 2022]]、[[wiki_low_latency/entities/DeepFilterNet2]] | 都是低复杂度时频域增强。DeepFilterNet2 走"复数深滤波 + 嵌入式实时"，本文走"动态跳步"。**可对比的是算力口径**：DeepFilterNet2 报的是固定 MACs，本文报的是**输入相关的平均 MACs**——两者不能直接横比 |
| **同分支竞品（复数谱掩蔽路线）** | [[wiki_low_latency/sources/2020/DCCRN Low-Latency Direction 2020]]、[[wiki_low_latency/entities/DCCRN]] | 都是复数谱掩蔽/复数 CRN。本文按 PHASEN [26] 把幅度与相位掩蔽**分开估计**再相乘（Eq. 3），与 DCCRN/DPCRN 的 CRM 路线是同域不同输出形式 |
| **同分支竞品（统一延迟审计）** | [[wiki_low_latency/sources/2024/Ultra-Low Latency Speech Enhancement Comprehensive Study 2024]]、[[wiki_low_latency/entities/CRUSE-Latency-Study]] | 该研究统一比较超低算法延迟前端与模型规模，而**CRUSE 正是本文的泛化验证宿主之一**（8.58 M / 20 ms 帧 / 10 ms hop）。两条记录合起来可以回答"CRUSE 在 10 ms hop 下能到什么水平" |
| **后续/扩展（最严因果口径）** | [[wiki_low_latency/sources/2026/LaCo-SENet 2026]]、[[wiki_low_latency/entities/LaCo-SENet]] | LaCo-SENet 给出逐层 padding 分配式 + 状态选择算子 + SSU 消融，是本库因果审计的**最高标准**。用它的尺子量本文：本文**卷积 padding 未报告**，因此连"逐层可核验"这一关都过不了。本文的 `paper-claimed-causal` 判定正是按这把尺子给的 |
| **后续/扩展（因果 Mamba + 蒸馏）** | [[wiki_low_latency/sources/2026/RT-SEMamba 2026]]、[[wiki_low_latency/entities/RT-SEMamba]] | RT-SEMamba 用固定 SSM state 解决长流内存，本文用跳步解决平均算力。两者都在"降低每步成本"的同一坐标系里，但一个降的是**状态规模**、一个降的是**状态更新次数** |
| **跨分支类比（两阶段级联的延迟累加）** | [[wiki_low_latency/concepts/2406.07498-two-stage-causal-repair]] | 该页讨论级联阶段的延迟累加；本文是**单阶段**模型，延迟账本简单得多，可作为"单阶段 48 ms"的对照基线 |
| **延迟账本口径** | [[wiki_low_latency/concepts/严格因果与算法延迟]]、[[wiki_low_latency/concepts/低时延前端与延迟账本]] | 本文是这两页的一个**负面样本**：只给一个未拆分的 48 ms，没有算法/计算/端到端的分账，也没有 p99。适合作为"什么算不完整账本"的示例 |
| **缺口对照（人声保留）** | [[wiki_low_latency/concepts/低 SNR 人声保留评估]] | 本文测到了 −5 dB 与 babble（本库少见的覆盖），但**不分层、无 false-suppression、无 ASR WER、无 F0/prosody**，且 VAD 只报 accuracy 不报 recall。是该 scorecard 的"部分覆盖 + 关键缺失"样本 |
| **概念页** | [[wiki_low_latency/concepts/2207.11108-inference-skipping-parallel-rnn]] | 把「推理期状态跳过 + 更新率控制 + VAD 引导」抽象成可复用概念，并论证 parallel RNN 是前提、目标率约束是硬件友好的关键 |
| **实体页** | [[wiki_low_latency/entities/Skip-DPCRN]] | 骨干配置、门控结构、VAD 分支、参数量/MACs、延迟口径与更新率 |

## 7. 一句话总结"江湖地位"

> **2022 | 实时语音增强的推理期算力压缩 | 把 Skip-RNN 从"会出伪影的失败尝试"救回来——关键洞察是伪影来自宿主结构而非跳步本身，只要宿主是 parallel RNN，一部分 RNN 跳步时 mask 仍由其他通路更新，伪影就被规避；在此基础上加了三条更新率正则、一个推理期免重训练的 $\gamma$ 旋钮和一个 VAD 引导的差异化跳步策略，在 DPCRN 上把 MACs 从 1115 降到 749.8 M（−32.8%）而参数量几乎不变（0.5286→0.5291 M），并在同算力下胜过"直接训小模型"与"结构化剪枝"，还在 CRUSE/GCRN 上验证了可迁移性 → 是"动态算力/输入相关算力"这一子方向的开篇标尺，也是 D-GRU 等后续工作"每步算力波动"批评的靶子；但它只报测试集平均 MACs、峰值算力仅降约 15%，48 ms total latency 未拆分且是 2 ms 目标的 24 倍，因果性只有一句 inter-frame 单向的声明，人声保留证据几乎空白。**

## 参考资料

- [arXiv:2207.11108](https://arxiv.org/abs/2207.11108)
- 代码：<https://github.com/Le-Xiaohuai-speech/SKIP-DPCRN>
- 试听样例：<https://github.com/Le-Xiaohuai-speech/SKIP-DPCRN-samples>
- 本地原件：`raw/papers/low_latency_causal_se/2207.11108.pdf`
- 本地文本抽取：`tmp/pdf_extract/2207.11108.txt`
- 页面渲染核对：`wiki_low_latency/assets/2207.11108/`（page1–page11；本页嵌入 4 张：`2207.11108-page4-skiprnn-and-vad-architecture.png`（Fig. 3+Fig. 4）、`2207.11108-page6-table2-table3.png`（Table II+III）、`2207.11108-page7-fig5-fig6-compression-comparison.png`（Fig. 5+Fig. 6）、`2207.11108-page8-fig7-binary-gate-vad.png`（Fig. 7）；另用 page1 核对标题/作者/DOI 占位符、page2 核对 Fig. 1、page3 核对 Fig. 2+Table I、page5 核对 Eq. 21–26、page9 核对 Fig. 8+Table IV）
- 论文内关键引用：[11] GCRN（Tan & Wang）、[12] CRUSE 与 complex compressed spectrum MSE（Braun et al.）、[13] Valin hybrid DSP/DL、[14] 量化、[15] 剪枝、[17] 知识蒸馏、[19] Skip-RNN（Campos et al., ICLR 2018）、[20] TinyLSTMs（Fedorov et al., Interspeech 2020）、[21] Braun & Gamper 损失研究、[22] DPCRN、[23] DPRNN（Luo et al.）、[24] DNS-3 Challenge、[26] PHASEN、[27] signal approximation、[31] FullSubNet、[40] 结构化剪枝（intrinsic sparse structures within LSTM）、[42] SDR、[43] PESQ、[44] STOI
