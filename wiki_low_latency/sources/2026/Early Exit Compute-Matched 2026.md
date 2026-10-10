---
title: Early Exit Compute-Matched - 算力对齐下逐帧早退的真实价值
type: source
created: 2026-09-27
updated: 2026-09-27
tags:
  - speech-enhancement
  - single-channel
  - streaming
  - early-exit
  - dynamic-depth
  - dynamic-neural-networks
  - conditional-computation
  - compute-matched
  - monotonicity-regularization
  - conv-fsenet
  - conv-tasnet
  - int8-quantization
  - npu-deployment
  - stm32n6
  - neural-art
  - cortex-m55
  - measured-latency
  - macs-not-latency
  - accelerator-launch
  - voicebank-demand
  - paper-claimed-causal
  - 16ms-hop
source_type: paper
year: 2026
authors: Clément Laroche; Riccardo Miccini
venue: arXiv preprint (eess.AS)
venue_status: preprint_only
arxiv: https://arxiv.org/abs/2609.29867
local_pdf: raw/papers/low_latency_causal_se/2609.29867.pdf
evidence_policy: local_pdf_only
related:
  - [[wiki_low_latency/entities/Early-Exit-Conv-FSENet]]
  - [[wiki_low_latency/concepts/2609.29867-compute-matched-dynamic-depth]]
  - [[wiki_low_latency/concepts/严格因果与算法延迟]]
  - [[wiki_low_latency/concepts/低时延前端与延迟账本]]
  - [[wiki_low_latency/concepts/低 SNR 人声保留评估]]
  - [[wiki_low_latency/concepts/2509.21867-speed-optimized-streaming-design]]
  - [[wiki_low_latency/concepts/2408.12425-dynamic-gated-rnn]]
  - [[wiki_low_latency/concepts/2207.11108-inference-skipping-parallel-rnn]]
  - [[wiki_low_latency/entities/FastEnhancer]]
  - [[wiki_low_latency/entities/D-GRU]]
---

~~~yaml
- 论文: [Does per-frame early exit pay? A compute-matched study of dynamic depth for on-device speech enhancement](2026)
  ├── 要解决什么问题: 动态深度（early exit）增强通常只与「自己的其他 exit」比，**很少**与「同一算力下重训的静态模型」比；而代价又只用名义 MACs 报，忽略路由与派发开销。于是无法回答：早退带来的收益到底来自「推理期适应」，还是来自「它训练出了一族更好的静态模型」？——这个问题在语音密集数据集上从未被分离计量过
  ├── 核心方法: 在因果 Conv-FSENet 上装一条 4 级 exit ladder（head 0 只读 frontend 的 bypass exit + head 1/2/3 读 frontend + stacks 1..i），用 16 单元 GRU 的一次性（one-shot）router 在**任何 stack 执行之前**决定本帧跑多深；训练用功率律压缩谱 MSE + deep supervision + 「knee target」路由监督；随后做「**repairing the exits**」——冻结 backbone/frontend/policy，只微调 4×33k 参数的 exit heads，加单调性正则 $\mathcal L_{mono}$ 把「更深反而更差」的帧压掉
  ├── 属于哪个分支: 单通道时频掩蔽增强 / **推理期深度级动态算力** / 端侧 int8 NPU 部署（不是神经元级稀疏、不是宽度剪枝、不是量化感知训练）
  ├── 输入/输出: 输入压缩带噪幅度 $|X|^{0.3}$（与 Conv-FSENet 同口径）；每个 exit head 在带噪复数 STFT 上估一个 sigmoid 幅度掩蔽；输出为增强谱（波形由 iSTFT 恢复，iSTFT 留在 host 上）
  ├── 关键trick: **把 exits 修成单调之后，再去看路由还剩多少价值**——knee target 从「当前 exits」定义，因此不要求质量随深度改善；更深 exit 反而更差时，策略「看起来有用」可能只是在回避有害的深 exit。用 2000 步、只动 4×33k 参数的 heads-only 微调加 $\mathcal L_{mono}$，把这一信号抽掉后再与算力对齐的静态前沿比
  ├── 数据集: 16 kHz **VoiceBank–DEMAND** [27]；训练随机裁 4 s 段 + Remix/BandMask/Shift 增广 [28] + [29] 的谱增广与电平不变性；测试在**全部 824 条**片段上评
  ├── 对比了谁: ① **12 个算力对齐的静态 Conv-FSENet**（TCM 宽度 $H\in\{32,64,96,256\}$ × stack 数 $R\in\{1,2,3\}$，$B=128$ 固定，跨 5.7–41.8 MMAC/s）；② 三对**精确算力对齐的 width–depth 对照**；③ **mono-repaired exits 作为静态模型**（本文最关键的一组对照）；④ 部署层面自比（static / repaired / routed 在 STM32N6 上逐个实测）
  ├── 性能上限: float32 下 routed H=64 在 **8.48 MMAC/s 达 PESQ 2.719**；int8 部署下 **static H=256, R=2 达 2.781 PESQ @ 2.472 ms/frame**；质量最高的一族指标是 PESQ 2.781（int8）
  ├── 参数量: 论文**只报 exit heads 的 4×33k 参数**（用于说明修复期的可训练量），**全模型参数量未报告**
  ├── 消融关键发现: **mono-repair 是全文的分水岭**——修复前 routed 明显优于专用静态前沿（routed H=64：2.719 PESQ @ 8.48 MMAC/s，而同算力静态前沿约 2.60）；修复后 **mono-repaired 前沿几乎与 routed 前沿重合**（共同区间 PESQ 差 < 0.01；三个具体点 8.48 / 12.18 / 20.22 MMAC/s 上分别 +0.009 / −0.001 / +0.007）。即：**逐帧路由不提高给定算力下可达到的最优质量，也不明显降低它**
  ├── 遗留问题(你的机会): ① 论文**自陈局限**——主张只限于语音密集数据集（VoiceBank–DEMAND），长停顿工作负载不在研究范围内，而「router 在稀疏工作负载上是否更有价值」被明确列为**重要的下一步**；② **平均 ms/frame 不是 p99**，全文无 deadline miss / underrun 报告；③ **没有** DNSMOS SIG/BAK、**没有** WER/ASR、**没有**负 SNR 分层、**没有** false-suppression / F0 / prosody；④ 单调性只由 4×33k 参数的 heads 承担，是否足以代表整条 ladder 的单调性未论证；⑤ 论文提到「quantization shifts routed compute by at most 2 %」但**未报告功耗**
  └── 跟哪篇像: [[wiki_low_latency/entities/D-GRU]]（同属"推理期动态算力"，但 D-GRU 跳神经元、**完全没有任何硬件测量**；本篇是它的镜像：真实 MCU 上逐图实测、但省下来的是**延迟而非质量上限**）；[[wiki_low_latency/entities/FastEnhancer]]（同样主张"MACs 不能预测速度"，但机理归因不同，见 §3.7）；[[wiki_low_latency/entities/RT-Tango]]（同为帧级稀疏省算力）
~~~

# Does per-frame early exit pay? A compute-matched study of dynamic depth for on-device speech enhancement

> Clément Laroche⋆; Riccardo Miccini†
> ⋆ GN A/S, Denmark；† Technical University of Denmark, Denmark。
> arXiv:2609.29867v1 [eess.AS]，24 Sep 2026，共 5 页（ICASSP 风格短文，含 cs.LG 与 cs.SD 交叉分类）。
> 基金：EU Horizon Europe，HORIZON-JU-Chips-2024-1-IA，grant agreement No 101194172（NeAIxt）（p.1 脚注）。
> 本页的核心不是复述它的 PESQ，而是把它当成**「动态算力评估方法论」与「真机延迟账本」两个议题的最佳样本**：这是本库第一篇**先做算力对齐、再问动态是否值得**的论文，也是**算力证据最硬**的一篇——它的结论是"动态深度在语音密集集上几乎不值"，但它给出的证据质量远高于结论本身。
> 本页把论文拆成四笔账分别审计：**算力口径（名义 MACs vs 实测 ms/frame）**、**对照是否公平（算力对齐 + 重训静态基线）**、**因果性与延迟**、**人声保留**。

> [!note] 发表状态：**arXiv 预印本，未见同行评审 venue**（2026-09-27 核实，依用户给定信息）
> 依 `evidence_policy: local_pdf_only`，本页只核对了**本地 PDF 能证明的部分**：
> 1. **本地 PDF 无任何 venue 信息**——全文无会议名、无 "Submitted to"、无 "Accepted"、无版权行；页脚/侧栏只有 `arXiv:2609.29867v1 [eess.AS] 24 Sep 2026` 一行（第 1 页左侧竖排），**这是 PDF 里唯一的出处信息**。
> 2. 排版为**典型 ICASSP 系列短文模板**（双栏、Abstract、Index Terms、5 页含 References）。**模板不是录用证据**——本库已就此踩过坑（[[wiki_low_latency/sources/2025/FastEnhancer 2025]]）。
> 3. **本页无法核对 arXiv 元数据**（无网络访问），因此 `venue_status: preprint_only` 与"无 Comments / 无 Journal-ref / 仅 v1"**取自用户给定信息**，本页未独立验证。
> 4. 分类挂 `eess.AS`，用户给定另挂 `cs.LG` 与 `cs.SD`——**PDF 侧栏只印了 `[eess.AS]`**，交叉分类同样来自用户给定信息、未从 PDF 核实。
>
> **本库据此将 `venue` 记为 `arXiv preprint (eess.AS)`，不标任何会议。**

> [!warning] PDF 转换质量与阅读说明
> 原 PDF 共 5 页，PyMuPDF 文本抽取（`tmp/pdf_extract/2609.29867.txt`）**整体可读**，公式与两张表格的数字基本能辨认，但有七类问题必须看页面渲染图核对，本页已逐条核对：
> 1. **`µ` 与 `ms` 之间的多余逗号是原文的**。正文与表格 caption 中反复出现 `0.640, ms`、`137, µs/MMAC`、`8.48 MMAC/s` 之后的 `1.00 and 0.75, ms`。**第 4 页渲染图确认这些逗号确实印在 PDF 上**（疑似模板/排版产生的英文千位分隔符误用），**不是抽取错误**。本页引用数值时去掉逗号，不视为数值错误。
> 2. **Eq. (3) 与 Eq. (5) 的竖线/范数符号在抽取文本中错位**。Eq. (3) 抽出为 `|S|cej∠S −|bS|cej∠b S`（`ĉ`/`Ŝ` 的帽子被压成 `b`），Eq. (5) 抽出为 `| ˆSj(f, t)|c −|S(f, t)|c`。本页公式已用**第 2 页渲染图**逐条核对，`c=0.3`、`α=0.3`、`λ_ds=1`、`λ_knee=0.1` 四个常数以渲染图为准。
> 3. **Eq. (2) 在抽取文本里被拆成三行且公式编号 `(2)` 被并到第三行末尾**：`Cfe ≈FB, Cstack,i ≈3Hi(2B + 3), Chead,k(t) ≈BF. (2)`。渲染图确认这是**同一个编号 (2) 下的三条并列近似式**。本页按三条并列记录。
> 4. **Table 1 是纯表格，行列归属完整**，抽取无塌陷；本页仍用**第 4 页渲染图**逐格复核了全部 10 行 × 4 列（含 `µs/MMAC` 列）。
> 5. **Table 2 的分节结构与加粗在抽取中丢失**。渲染图确认 Table 2 内有**两个分组标题行**：`Within a fixed ladder` 与 `Across static and dynamic topologies`；且 `ms/frame` 列的部分值**加粗**（`0.930`、`1.668`、`2.684`、`0.751`、`2.762`、`1.364`）。本页 Table 2 以渲染图为准分两段记录。
> 6. **图体（Fig. 1–Fig. 4）在文本抽取中全部丢失**，只留零散标签（`1×1`、`dil. 1/2/4`、`257→128`、`one-shot router (GRU-16)`、Fig. 4 的 `0 0.25 0.5 1 2 4 8 kHz` 与 `0 2 4 6 8 time (s)`）。本页对 Fig. 1/Fig. 2 的描述来自**第 2 页渲染图**，对 Fig. 3/Fig. 4 的描述来自**第 3 页与第 4 页渲染图**。
> 7. **Fig. 3 的图例与刻度在渲染图上偏小**：`# stacks` 的图例是三种**空心圈尺寸**（1 / 2 / 3），`Pareto fronts` 的图例是三种**虚线线型**（dedicated static / mono-repaired / routed）。渲染图足以读出**图例条目的存在与顺序**，但**不足以可靠分辨某一条虚线的具体类别**——本页因此只引用论文的文字结论，不对 Fig. 3 做逐线读数（见 §4.2）。
>
> 论文**未报告**的字段（采样率以外的完整前端锚定、**STFT center**、look-ahead、group delay、warm-up、state reset、算法的 ms 级延迟口径、p50/p95/**p99**、峰值 RAM/SRAM、功耗、deadline miss、underrun/overrun、DNSMOS SIG/BAK、ASR WER、负 SNR 分层、babble/竞争说话人分层、false-suppression、SPP/VAD、F0/formant/prosody、voiced energy、听感 MOS、全套参数量、训练种子数）在本页一律写「未报告」，**不作任何补写**。

## 1. 他们为什么这么做？（motivation）

### 1.1 任务与对象

单通道语音增强，面向「助听器 / 头戴设备 / 耳机」这类**只有共享电池预算**的端侧设备（p.1 Abstract、§1）。论文开篇把部署约束写得很具体（p.1 §1）：

> "device tiers and concurrent workloads ask for different quality/compute operating points; thus, a product needs a **family of models** [3, 4]. Because **microcontroller-class accelerators support only static int8 graphs**, each member of that family is compiled ahead of time. Consequently, a model that chooses its depth at run time is not something mainstream edge toolchains support natively: they lower **one static graph**, leaving the selection policy and the dispatch between separately compiled subgraphs to run **outside the compiled model** [5, 6]."

这段话同时给出了本篇的**技术前提**与**动机**：

- **技术前提**：MCU 级加速器只吃**静态 shape + int8** 图。一个"深度可变"的网络在工具链里**必然被拆成多张图**，由策略在编译器之外做派发（引 [5] 动态网络综述、[6] ST Edge AI Core）。
- **动机**：因此"早退"这个想法在端侧的真实形态**不是一张动态图**，而是**一族静态图 + 一个 host 侧的调度器**。那么它值不值，就必须按这个形态来评估。

### 1.2 论文动机：一个被忽略的对照空白

论文把动机压缩成三句批评（p.1 §1），三句都指向**评测口径**：

> "Dynamic SE is usually compared with **its own exits** [9], while **retrained static models matched for compute are less often used as baselines** [18]. Cost is also usually reported in **nominal MACs, which ignore routing and dispatch overhead** [19]. Finally, extracted static models have **rarely been quantized and carried through to measured accelerator latency**, and output quality has **not been studied frame by frame**."

三句分别对应三个空白：

| # | 空白 | 后果 |
|---|---|---|
| 1 | 动态模型只跟自己的 exits 比，**缺少"同算力、同配方重训"的静态基线** | 无法区分"动态自适应带来的收益"与"这个训练配方本身就产出了更好的模型" |
| 2 | 代价只用**名义 MACs** 报，忽略路由与派发开销 | 名义算力不反映真实部署代价（引 [19] = ShuffleNet V2，即在讲"MACs 不是速度"） |
| 3 | 抽出来的静态模型**很少被量化并一路跑到实测加速器延迟**，且**没有逐帧研究输出质量** | 无法知道整个方法在真实设备上还剩多少 |

论文把 #1 直接写成全文要回答的问题（p.1 §1 末）：

> "This leaves open whether the benefits of early-exit training come from **adapting computation at run-time**, from **improving the static models extracted from the network**, or from **both**."

### 1.3 论文的答案与其自我限定

论文在 §1 就给出了主结论（p.1 §1，注意这一段在引言里，不是结论节）：

> "The main observation is that, once the fixed-depth models are compared fairly, **routing brings little advantage**: indeed, the extracted static models form a competitive quality–compute frontier, which **holds when considering measured latency instead of theoretical MACs**. Our claims are **limited to speech-dense datasets (VoiceBank–DEMAND)**; while arguably more realistic, **workloads with long pauses are outside this study**."

同时给出了四条明确贡献（p.1 §1）：

1. 面向**回归** exit 的 per-frame 单调性正则 + **heads-only 微调**策略；
2. 一个分析，证明**路由的多数 headroom 来自"更深 exit 反而降低质量"的帧**，而修复这些帧**基本消除了这个优势**；
3. 一条**同配方、同评测框架重训的算力对齐静态前沿**，带 seed spread 与对照；
4. 对**每个抽出的固定深度模型**做 int8 量化并给出**实测 STM32N6 延迟**。

> [!note] 这篇论文的定位很特殊：它是"**给某个热门方向泼冷水**"的论文
> 但它的冷水泼得比同类论文**更硬**：不是靠论证，而是靠 ① **算力对齐的重训静态基线**（把对照组补齐）、② **真机 int8 逐图实测**（把代价口径补严）、③ **mono-repair 这个消融**（把"是动态的功劳还是训练的功劳"分离出来）。三条都是本库长期缺乏的评测纪律。详见 §4 与概念页。

## 2. 之前的人怎么做不了？（limitation → gap）

### 2.1 相关工作的两条脉络（p.1 §1）

论文用两段话把前作分成两条线：

| 脉络 | 代表工作（论文引文） | 做法 | 论文的定位 |
|---|---|---|---|
| **动态 SE** | [8] Dynamic NSNet2（MLSP 2023，多个 exits 但**没有 policy**）；[9] Probabilistic early exits（ICLR 2026，per-block 概率判据）；[10]–[13] learned width 与 gating（动态通道剪枝 ICCASSP 2025、adaptive slimming WASPAA 2025、dynamically slimmable ICASSP 2026、dynamic layer gating Interspeech 2025） | 在 backbone 上放多个 exit / 动态改宽度 / 动态门控 | 本篇把它们整体当作"动态"这条线，并指出它们**都缺算力对齐的静态基线** |
| **Train-once-deploy-many** | [3] Once-for-all（ICLR 2020）、[14]–[16]（stochastic depth / layer dropout / universally slimmable）、[4] TODM（ICASSP 2024，on-device ASR）、[17] Subnetwork-to-go（ICASSP 2024，elastic music separation） | 从**一次训练**里抽出多个静态子网 | 论文承认这条线「reportedly matching or surpassing dedicated training」，因此**它的成功恰恰是本文怀疑的根源**：收益也许全在"训练脚手架"上 |

### 2.2 gap：三处"能做但没人做"

论文的 gap 不是"前人的方法做不到"，而是**"前人的对照没做全"**。这是本篇最重要的一点：

| 对照 | 前人做法 | 论文指出 | 为什么至今没做 |
|---|---|---|---|
| **静态基线** | 与自己的 exits 比 | 应为**同配方、同评测框架重训**的算力对齐静态模型（引 [18] 指出这一空白） | 需要训 12 个静态模型 + 3 对 width–depth 对照，成本高，且结果可能不利于自己 |
| **代价口径** | 名义 MACs | 应**在目标加速器上实测**，因为「Cost is also usually reported in nominal MACs, which **ignore routing and dispatch overhead**」（引 [19] ShuffleNet V2） | 需要真实 MCU + 量化 + 工具链，链条长 |
| **质量口径** | 全片段指标 | 应**逐帧看**输出质量 | 需要 per-frame 误差定义（本篇用 Eq. 5 的 $q_j(t)$） |

> [!note] 本篇的 gap 是**方法学 gap**，不是能力 gap——这一点决定了它在本库的角色
> 它不提出更快/更好的网络，而是提出**一套更严的评估规程**：算力对齐 + 同配方重训 + int8 实测 + 逐帧质量。因此它的价值**不依赖于它的结论是否被后来的工作推翻**——即使将来动态深度在某类工作负载上被证明很值，本文那套规程仍然是该被采用的。详见 [[wiki_low_latency/concepts/2609.29867-compute-matched-dynamic-depth]]。

### 2.3 "overthinking"：为什么需要一个专门的修复步骤

论文把动机直接落到一个可观测现象上（p.1 §1）：

> "In this paper, we add a per-frame monotonicity regularization to a causal Conv-TasNet-style network, so that deeper exits are encouraged to improve over shallower ones. **When training on the SE task loss alone, this is not guaranteed: on nearly half of the frames, a deeper exit performs worse than its previous one**, confirming the **"overthinking"** phenomenon observed in early work on early-exiting [7]."

引 [7] 是 Kaya 等 "Shallow-deep networks: Understanding and mitigating network overthinking"（ICML 2019）。**"近一半的帧上更深 exit 更差"** 这个数字是本篇的立论基石——它意味着**knee target 定义的策略天然含有一个"回避坏 exit"的成分**：

> "Because the knee target is defined from the current exits, **it does not require quality to improve with depth**. In practice, a deeper exit can perform worse than the previous one (Sec. 2.2). This creates an **ambiguity** when evaluating routing: **a policy may appear useful simply because it avoids harmful deeper exits, rather than because it assigns less compute to frames that genuinely need less processing**. We therefore repair the exit ladder before assessing the value of dynamic depth."（p.2 §2.3）

这段是全文的逻辑枢纽，也是**本页认为最值得记录的一段**：它把"动态执行的价值"与"更深 = 更好的假设"这一隐含前提拆开了。

## 3. 这个做法核心 trick 是什么？

### 3.1 架构：Early-exit Conv-FSENet（§2.1）

论文的方法由**三块拼装**而成，前两块来自既有工作，第三块（§2.3 的修复）是本文独有的：

| 组件 | 来源 | 在本篇的作用 |
|---|---|---|
| **Backbone：Conv-FSENet** | 引 [10]（同一作者 Miccini 等，ICASSP 2025）+ [21]（ICASSP 2026），派生自 Conv-TasNet [22] | 因果 STFT 域掩蔽网络；提供 frontend + $R$ 个 stack + mask heads |
| **Exit ladder + one-shot router** | 引 [8]（Dynamic NSNet2）等多 exit 思路的延续，但 router 形态是本文的 | 提供"逐帧选深度"的能力 |
| **Repairing the exits（§2.3）** | 与 [20] Jazbec 等（NeurIPS 2023，分类任务的后验单调性强制）对照 | **本文的方法论核心**：先修好 ladder，再评估路由 |

论文对 backbone 的原文描述（p.2 §2.1）：

> "We estimate the speech as $\hat s=\mathcal M(x)$ using **Conv-FSENet** [10, 21], a **causal STFT-domain masking network derived from Conv-TasNet** [22]. The model comprises a **pointwise-convolutional frontend**, $R$ **stacks**, each featuring **3 causal dilated depthwise temporal-convolutional residual blocks** (shown in Fig. 2), and **mask heads**. The frontend maps the compressed noisy magnitude $|X|^{0.3}$ onto a $B$-channel inter-block representation, which is **expanded into $H_i$ channels within each $i$-th block before projecting back to $B$**."

![[wiki_low_latency/assets/2609.29867/2609.29867-page2.png]]

> 图注：原论文第 2 页页面渲染，用于核对 **Fig. 1（exit ladder）+ Fig. 2（residual block）+ Eq. (1)–(7)**。**Fig. 1** 从左到右依次为：$|X|^{0.3}$ → `257→128` 的 `1×1` frontend → `dil. 1/2/4` 的三个 stack；下方四个 `head 0/1/2/3` 分别挂在 frontend 之后与三个 stack 之后（`head 0` 是 bypass exit，只读 frontend）；`one-shot router (GRU-16)` 用**虚线**画在 heads 之下的旁路上——渲染图上虚线的起点位于 **frontend 输出处**、终点指向**各 head 的派发**，这正是正文 "feeds on frontend features **before any stack runs**" 的图形证据。**Fig. 2** 是单个 residual block $B_i$：`B ch.` → `expand B→H_i` → `causal DW conv, k=3, d` → `project H_i→B` → 残差加回 `B ch.`。两张图在本页的架构 ASCII 图（实体页 §架构与状态）中已转写。图片为 PDF 页面复制，不是 AI 重画。

### 3.2 exit ladder 与感受野（§2.1）

论文把 ladder 与感受野写得非常具体（p.2 §2.1）：

> "Mask heads attach **after the frontend (the bypass exit)** and **at each stack**, estimating a **sigmoid-activated magnitude mask on the noisy complex STFT**, such that **exit $i$ evaluates the frontend plus the first $i$ stacks** (Fig. 1). Their **receptive fields are 1, 15, 29 and 43 frames**, while the **bypass exit is memoryless**."

| exit | 读取什么 | 感受野 | 是否有记忆 |
|---|---|---:|---|
| head 0 | frontend 输出 | **1 帧** | **无**（论文明确写 "the bypass exit is memoryless"） |
| head 1 | frontend + stack 1 | **15 帧** | 有（stack 1 的膨胀卷积） |
| head 2 | frontend + stacks 1–2 | **29 帧** | 有 |
| head 3 | frontend + stacks 1–3 | **43 帧** | 有 |

**这组感受野是本文最容易被忽略、但对本库最重要的一条**：head 0 声称 **memoryless**，而 head 1–3 的感受野随深度**线性增长**（1 → 15 → 29 → 43，步长恰好 14 帧）。在 16 ms hop 下，14 帧的增量对应 **224 ms** 的历史跨度——这是**历史窗口（look-back）**，不是 look-ahead。

> [!question] 感受野的"帧"是单向还是双向？论文没有明说
> 论文只给「receptive fields are 1, 15, 29 and 43 frames」和一个 "causal" 的全局声明，**没有说明这 43 帧是全部来自过去（look-back）还是含未来（look-ahead）**。按 `dil. 1/2/4` 的三层膨胀深度可分离卷积（Fig. 2）与 "causal dilated depthwise temporal-convolutional residual blocks" 的用词，**本文的最佳读法是单向、全部为 look-back**：
> $$1 + 2\times(1+2+4)\times 2 = 29 \quad(\text{1 frontend 帧} + \text{2 个 stack} \times \text{每 stack }14\text{ 帧})$$
> 即 $1\to15\to29\to43$ 的步长 14 帧可解释为「每层 3 个残差块，每块取 $k-1=2$ 个历史帧，膨胀率 1/2/4 求和 = 14，且一个 stack 计两份」——**但这个式子是本页的推读，论文没有给出感受野的推导**。若感受野含未来成分，则 look-ahead 会随所选 exit 变化（最深 head 的 look-ahead 最大），这将是本篇因果性的一个**真实缺口**。本页记录为**不确定**（见实体页 [!question]）。

### 3.3 one-shot router：在任何 stack 执行之前就做完决策（§2.1）

这是本篇与多数 early-exit 工作的**结构差异**。原文（p.2 §2.1）：

> "At each **16 ms frame**, a **one-shot policy router** selects an exit **before executing any of the stacks**; this consists of a **16-unit GRU, feeding on the frontend output** and producing a categorical decision $k(t)\in\{0,\dots,R\}$ **before any TCN stack is executed**. **Only stacks up to $k(t)$ are then evaluated. The remaining stacks are skipped entirely.**"

三点值得单独记住：

1. **router 只读 frontend 输出**——不是"读了 intermediate feature 再决定"，因此决策**必须在第一个 stack 之前完成**；
2. router 是一个 **16 单元 GRU**，因此它**自身有跨帧状态**（这一点对 §4.5 的"warm up"和 bit-identical 声明很关键）；
3. **被跳过的 stack 不是"算了不用"，而是"完全跳过"** —— 但"跳过"对状态的语义有后果，见 §4.5。

> [!note] one-shot 是一个很强的约束，也是一个很聪明的工程选择
> 如果 router 要在 stack 之间做决策（如 [9] 的 per-block 判据），那么每次决策都要把中间特征读出到 host，**派发开销会随决策次数增加**。one-shot 把决策压缩成 hosts 上的**一次**分类，代价是 router 只能看到 frontend 特征（深度为 1 的感受野）——**它要在一个很浅的表征上预测"这一帧需要多深"**。这解释了为什么后面 knee target 的训练如此重要：决策信息量与决策精度之间的张力，正是这篇论文所有消融的舞台。

### 3.4 算力公式（Eq. 1–2）

$$
C_{k(t)} = C_{fe} + \sum_{i=1}^{k(t)} C_{stack,i} + C_{head,k(t)}, \tag{1}
$$

$$
C_{fe} \approx FB, \qquad C_{stack,i} \approx 3H_i(2B+3), \qquad C_{head,k(t)} \approx BF. \tag{2}
$$

- $C_{fe}$：frontend 成本，$\approx FB$（$F$ 个频点 × $B$ 个通道）；
- $C_{stack,i}$：第 $i$ 个 stack，$\approx 3H_i(2B+3)$（3 个残差块，每块把 $B$ 扩到 $H_i$ 再投回）；
- $C_{head,k(t)}$：所选用 head，$\approx BF$。

论文对这三条式子的解读（p.2 §2.1）：

> "Selecting an earlier exit therefore **avoids the full cost of every subsequent TCN stack**, while the **frontend and selected mask-head costs remain fixed**."

即：**省下的只有 stack**。frontend（$C_{fe}$）与 head（$C_{head}$）都是"跑不掉的固定成本"。这与 [[wiki_low_latency/entities/D-GRU]] 的成本公式 $(1+2P/100)/3$ 是**同一个记账范式**（都先扣掉"必付项"，再算可省部分），但 D-GRU 省的是 GRU 的 $r/c$ 两门、本篇省的是**整段 stack**。

> [!question] Eq. (1)–(2) 是"近似"且**没有给出单位与口径**
> 三条式子都带 $\approx$，论文**没有说明**它们是 MACs、是乘加次数、还是别的计数；也**没有说明** $k(t)$ 在求和里的写法（$k(t)\in\{0,\dots,R\}$ 时，$k=0$ 的求和为空，只剩 $C_{fe}+C_{head,0}$——这与"bypass exit"的定义自洽）。本页按"analytic MACs"记录，与本篇 §4.2 的 "analytic MMAC" 用词一致，但**论文自身的口径未明**。

### 3.5 训练目标：SE 损失 + deep supervision（Eq. 3–4）

$$
\mathcal L_{SE}(\hat S, S) = \alpha \sum_{l,f} \Big| |S|^c e^{j\angle S} - |\hat S|^c e^{j\angle \hat S} \Big|^2 + (1-\alpha)\sum_{l,f}\Big( |S|^c - |\hat S|^c \Big)^2, \tag{3}
$$

$$
\mathcal L_{enh} = \mathcal L_{SE}(\hat S_k, S) + \frac{\lambda_{ds}}{R+1}\sum_{j=0}^{R}\mathcal L_{SE}(\hat S_j, S), \tag{4}
$$

- $c=0.3$（压缩指数）、$\alpha=0.3$（幅度项与复数项混合权重）；
- $l, f$：时间与频率 bin；$\hat S_k$ 是**路由选中的**输出，$\hat S_j$ 是 exit $j$ 的输出；
- $\lambda_{ds}=1$；
- 论文明确：Eq. (3) 是「the **power-law-compressed spectral MSE** of As in [8, 23], computed on **active-speech-level-normalized spectra**」——即损失在**按语音活跃电平归一化后的谱**上算（引 [23] Braun & Tashev 的损失综述）。

Eq. (4) 是标准的 **deep supervision**（引 [24] Lee 等 Deeply-supervised nets，AISTATS 2015；引 [25] 渐进式增强），含义是**路由选中的 exit 与每一个 exit 都被独立监督**——这是整个方法能"一次训练产出多个可用模型"的基础。

### 3.6 knee target：用"误差曲线拐点"定义路由目标（Eq. 5）

$$
q_j(t) = \frac{1}{F}\sum_{f}\Big( |\hat S_j(f,t)|^c - |S(f,t)|^c \Big)^2, \tag{5}
$$

$$
k(t) = \min\Big\{ j : q_j(t) \le \min_i q_i(t) + \varepsilon \Big\}. \tag{6}
$$

- $q_j(t)$：exit $j$ 在帧 $t$ 的**per-frame 压缩幅度误差**（用同一个压缩指数 $c$ 算，与 Eq. 3 同口径）；
- $k(t)$：**"最便宜的、误差在最优 ε 之内的 exit"**——即 knee 点；
- 论文对该目标的说明（p.2 §2.2）："a **clean-signal knee target**, which identifies the **point of diminishing returns along the exit ladder**."

训练策略（p.2 §2.2）：

> "We train the policy by **cross-entropy against this target**, either **jointly with the full backbone or on a frozen enhancer**. Routing is **discretized by straight-through Gumbel-softmax** [26]."

$$
\mathcal L_{tot} = \mathcal L_{enh} + \lambda_{knee}\mathcal L_{CE} + \mathcal L_{cost}, \tag{7}
$$

- $\lambda_{knee}=0.1$；
- $\mathcal L_{cost}$：「controls the **average routed compute** through the target operating point $\tau$」——即通过一个目标工作点 $\tau$ 来间接控制平均算力。**论文没有给出 $\mathcal L_{cost}$ 的具体形式，也没有给出 $\tau$ 的取值**。

> [!question] $\varepsilon$ 的物理含义**论文全文没有定义**
> Eq. (6) 里的 $\varepsilon$ 是 knee target 唯一的超参，但论文**从未解释它的物理含义或取值**（是 PESQ 当量？是压缩幅度误差？
> 是相对还是绝对？）。正文只在 §2.2 说「within $\varepsilon$ of the best achieved by any exit」，式子里它加在 $\min_i q_i(t)$ 上，**因此量纲应与 $q_j(t)$ 相同**（即压缩幅度谱的 MSE 量纲）。
> 这个记号在 Table 2 里又以 `ε=2·10⁻³` 与 `ε=5·10⁻⁴` 两档出现，但 Table 2 的语境是**部署测量**，与 §2.2 的 knee target 是否同一 $\varepsilon$ **论文未澄清**。本页**不代填**，一律以「未定义」记录。

> [!question] 论文自身的符号冲突：Eq. (7) 的编号与论文里另一个"Eq. 7"重叠
> 本地抽取文本中，`(7)` 出现两次：一处是在 **p.2 §2.3** 的 $\mathcal L_{mono}$ 定义之后（原文作 `(7)`），另一处是 §2.2 的 $\mathcal L_{tot}$ 编号。本页按**第 2 页渲染图**核对：渲染图上 $\mathcal L_{tot}$ 的编号为 **(6)**、$\mathcal L_{mono}$ 的编号为 **(7)**。
> **即：本页把 $\mathcal L_{tot}$ 记为 Eq. (6)、$\mathcal L_{mono}$ 记为 Eq. (7)**，与渲染图一致。用户 brief 中把 $\mathcal L_{tot}$ 称为 "Eq. 6"、$\mathcal L_{mono}$ 称为 "Eq. 7"，**与渲染图核对后一致，无需纠正**；此处记录仅为消除抽取文本里的重复编号歧义。

### 3.7 §2.3 Repairing the exits —— 本文方法论的核心

这是全文最值一读的一节。三步：

**第一步，指认歧义**（原文已在 §2.3 引用，见 §2.3 节）。

**第二步，冻结一切、只动 heads**（p.2 §2.3）：

> "We apply a **monotonicity repair** to the exits themselves. We **freeze the backbone stacks, frontend, and policy**, and **fine-tune only the exit heads (4×33k parameters)** with deep supervision and the following regularizer:"

$$
\mathcal L_{mono} = \frac{1}{TR}\sum_{t=1}^{T}\sum_{j=0}^{R-1}\max\Big(0,\ q_{j+1}(t) - q_j(t)\Big), \tag{8}
$$

> "which **penalizes every frame for which adding depth increases the error**. We fine-tune for **2000 steps** with the Adam optimizer with a **learning rate of $10^{-4}$** and a **regularization weight of 50**."

**第三步，与既有做法划界**（p.2 §2.3）：

> "Rather than **enforcing monotonicity post hoc**, as **Jazbec et al. [20]** do for **classification**, this term **encourages it through a soft constraint during training**."

> [!note] 这一步的意义远超"修个 bug"——它同时做了两件事，而且论文没有把第二件说清楚
> - **明面的一件（论文说了）**：让更深的 exit 不再有害，从而让 knee target 与路由评估变得有意义。
> - **隐含的一件（论文没说，但这是它全部结论的来源）**：一旦阶梯单调，每个 exit 就变成一个**可独立部署的静态模型**。于是"routed 前沿"与"repaired 前沿"成为可直接比较的两条曲线——**这正是把"动态的价值"与"训练的功劳"分离出来的操作手段**。所以 §2.3 不是"预处理"，而是**实验设计本身**。
> 这一点在 §4.2 的结果里被完全兑现：repaired 前沿几乎与 routed 前沿重合，而两者都**高于**从零训练的专用静态前沿。

> [!question] 4×33k 参数是否足以代表整条 ladder 的单调性？
> 论文用「the exit heads (4×33k parameters)」来说明修复是极轻量的（约 132k），这既是优点也是疑点：
> ① 冻结 backbone 意味着**每个 exit 的表示能力被其读取的特征固定**——修复只能在给定特征上调整映射，**无法改变"第 3 个 stack 之后还剩多少可用的信息"**；
> ② 因此 repair 成功只证明了"**在冻结特征的条件下，可以把更深变得更不差**"，**没有**证明"这个 ladder 的本质是单调的"；
> ③ 论文**没有报告 repair 前后的 backbone 是否也被改动过**（正文说冻结，但未报告是否做过其他实验臂），也**没有报告单调性修复的收敛曲线或残余违反率**（$\mathcal L_{mono}$ 最终降到多少）。
> 本库记录为**未验证**：修复的有效性只有"修复后前沿变好"这一间接证据，没有任何直接的逐帧单调性统计。

### 3.8 三块之间的依赖关系（本页的读法）

~~~text
       ┌──────────────────────────────────────────────────────────┐
       │  Conv-FSENet backbone（因果 STFT 域掩蔽）                 │
       │  frontend → stack1 → stack2 → stack3                     │
       └───────┬──────────┬──────────┬──────────┬────────────────┘
               │          │          │          │
            head 0     head 1     head 2     head 3        ← exit ladder
           (bypass)   (RF 15)    (RF 29)    (RF 43)
               ▲          ▲          ▲          ▲
               └──────────┴──────────┴──────────┘
                          │ 派发（host 侧）
                  [ one-shot router：GRU-16 ]
                          ▲
                    只读 frontend 输出（任何 stack 执行之前）

   训练期：  Eq.(3) 压缩谱 MSE ──► 每个 head 独立监督（deep supervision，Eq. 4）
             Eq.(5) knee target ──► router 的 cross-entropy 目标（Eq. 6）
             Eq.(7) L_cost      ──► 平均算力锚到目标工作点 τ

   修复期（§2.3，本文核心）：冻结 backbone / frontend / policy
             只训 head 0..3（4×33k）+ Eq.(8) 单调性正则（2000 步，lr 1e-4，权重 50）

   部署期： 9 张子图（frontend / router / 3×stack / 4×head）→ ONNX → int8 → ST Edge AI Core v4.0
            路由决策与派发都在 Cortex-M55 上；STFT / iSTFT / masking 留在 host
~~~

> [!note] 与 FastEnhancer 的"MACs ≠ 速度"是同一命题、不同机理
> [[wiki_low_latency/sources/2025/FastEnhancer 2025]] 也用"参数量与 MACs 都不变、速度却变差"的消融证明同一件事（BN→LN：Para/MACs 恒为 92K，RTF 0.022→0.028；时间轴 kernel 1→3：SISDR/STOI 一格不动而 Para 翻倍），但它归因于 **算子可融合性与内存操作**。
> 本篇归因于 **accelerator launch 次数与 NPU 利用率**（见 §4.3），并在**真实 MCU** 上量化了这个差异（82–137 µs/MMAC，1.7×）。**两篇的机理不同、层级不同**（FastEnhancer 是 CPU 单线程算子层，本篇是 NPU 图调度层），但结论方向一致。本页认为这是本库应并列记录的一组"**双证据**"。详见概念页命题 ③。

## 4. 实验里哪个消融最关键？

### 4.1 实验设置（§3.1）

| 项目 | 论文设置 |
|---|---|
| 数据 | **16 kHz VoiceBank–DEMAND** [27] |
| 训练切分 | 随机裁 **4 s** 段 |
| 增广 | **Remix / BandMask / Shift** [28] + 谱增广与电平不变性 [29] |
| STFT | **512 样本窗、50 % overlap、$F=257$ bins**（原文：「We compute the STFT using a **512-sample window with 50 % overlap**, yielding $F=257$ bins」） |
| 输入 | 所有模型输入 $|X|^{0.3}$ |
| **静态基线网格** | TCM 宽度 $H\in\{32,64,96,256\}$ × stack 数 $R\in\{1,2,3\}$，**$B=128$ 固定** → **12 个模型，跨 5.7–41.8 MMAC/s**，**bracket 所有 routed 点（6.6–20.2 MMAC/s）** |
| width–depth 对照 | **三对精确算力对齐**的 width–depth 对（检验"同样的算力预算该花在宽度还是深度上"）；**论文未给出这三对的具体配置，只在正文提了一句** |
| 训练 | Adam，lr $10^{-3}$，weight decay $10^{-5}$，**每 epoch 衰减 0.99**，batch **64**，early stopping；静态模型用**同一套配方**，去掉 routing 相关损失 |
| 指标 | **whole-clip SI-SDR** [30] 与 **wideband PESQ** [31]，在**全部 824 条**测试片段上 |
| 动态算力口径 | 「the **realized average MMAC/s over the selected exits**」——即**实际选中的 exit 的平均算力** |
| 修复超参 | 2000 步，Adam，lr $10^{-4}$，正则权重 **50**（§2.3） |

> [!warning] STFT 的三个参数里有两个决定了延迟，而论文只给了三个中的两个半
> 论文只说「**512-sample window with 50 % overlap**」：
> - **窗长** 512 samples = **32 ms** @16 kHz（本页换算）；
> - **hop** = 50 % overlap ⇒ **256 samples = 16 ms**（与本篇反复出现的 "16 ms hop" 自洽）；
> - **$F=257$ bins** —— 注意 **257 = $512/2+1$**，即**单边谱含直流与 Nyquist**。
> - **但 `center` 与否完全没有报告。** 这一点在本库是**一等审计项**（见 [[wiki_low_latency/concepts/严格因果与算法延迟]]）：若 `center=True`，则每一帧的分析窗相对帧锚点**向前后各取 $W/2$**，前端**含 16 ms 的未来样本**，整个系统的算法延迟直接多出 16 ms；若 `center=False`（左对齐），则前端不含未来样本。
> **论文对此完全沉默**——它在 §4.1 部署平台那句 "All networks are causal at a 16 ms hop" 里把 causal 当成既定事实，却**没有报告任何影响因果判定与否的前端锚定参数**。

### 4.2 质量–算力前沿（Fig. 3，float32）——**全文最关键的一组对照**

论文的叙述分两段，第二段是全文的分水岭。

**第一段：对准专用静态基线，路由有明显优势**（p.3 §3.2）

> "Against the dedicated statics, routing gives a **clear advantage over most of the compute range**. For example, the **routed H=64 model reaches 2.719 PESQ at 8.48 MMAC/s**, while the **static frontier is around 2.60 at the same cost**. **The gap becomes smaller as compute increases, but the routed models remain above the dedicated-static frontier.**"

| 对照 | routed H=64 | 专用静态前沿（同算力） | 差值 |
|---|---:|---:|---:|
| @ **8.48 MMAC/s** | PESQ **2.719** | 约 **2.60** | **+0.12 左右** |

**第二段：把每个 exit 修成静态模型后，图景反转**（p.3 §3.2）

> "The picture changes once **each exit is repaired as a static model**. The **mono-repaired frontier almost overlaps the routed one**: at matched compute, their **PESQ differs by less than 0.01** over the common range. For instance, the routed points at **8.48, 12.18, and 20.22 MMAC/s** differ from the **interpolated repaired frontier** by only **+0.009, −0.001, and +0.007 PESQ**, respectively."

| routed 点 (MMAC/s) | 与插值后的 repaired 前沿之差 (PESQ) |
|---|---:|
| **8.48** | **+0.009** |
| **12.18** | **−0.001** |
| **20.22** | **+0.007** |

论文的结论（p.3 §3.2）：

> "The similar routed and repaired frontiers show that **per-frame routing does not raise the best quality attainable at a given compute budget, but importantly it does not noticeably lower it either.**"

**第三段：部署选择因此依工作负载而定**（p.3 §3.2）

> "A repaired static model **fixes one operating point and pays the same cost on every frame**, whereas the routed model **keeps the full exit scaffold and can move between operating points over time**. ... **On dense workloads with little variation, a static deployment is therefore sufficient; on streams with pauses or changing difficulty, routing can reduce average compute while remaining on essentially the same quality–compute frontier. The benefit of dynamic deployment is thus not a higher quality ceiling, but the ability to adapt where compute is spent without sacrificing that ceiling.**"

> [!note] 这三段是本篇的完整论证链，缺一段都会被误读
> - 只读第一段 → 会得出"路由比静态省算力"（**这正是本库其他动态算力论文的常见说法**）；
> - 只读第二段 → 会得出"路由毫无价值"；
> - 三段合读 → 正确结论是"**路由不改善质量上限，只把算力预算的分配权交给运行时**"。
> 本页把这条链记为：**"动态执行的价值不是更高的上限，而是'在不牺牲上限的前提下把算力花在哪里'"**（论文原话：the ability to adapt where compute is spent without sacrificing that ceiling）。这与 [[wiki_low_latency/entities/D-GRU]] 所代表的"动态算力省平均功耗"是**同一类价值的更精确表述**。

> [!warning] Fig. 3 的图例在渲染图上不足以可靠分辨单条曲线——本页不做逐线读数
> 第 3 页渲染图可读出：横轴 **MMAC/s 为对数刻度**，刻度值为 `5 / 7 / 10 / 15 / 20 / 30 / 42`；纵轴 **PESQ 从 2.60 到 2.80**（刻度 `2.60 / 2.65 / 2.70 / 2.75 / 2.80`）；图例分三组——`Model`（static/repaired/routed × H=32/64/96/256，共 12 项）、`# stacks`（三种**空心圈大小**：1 / 2 / 3）、`Pareto fronts`（**三条虚线**：dedicated static / mono-repaired / routed）。
> **但渲染图分辨率下，三条虚线（含各自无标记的 `dedicated static` 虚线）之间的区分、以及某个数据点落在哪一条前沿上，无法可靠读出。** 本页因此**只引用论文给出的三个数值对（+0.009 / −0.001 / +0.007）与 §3.2 的文字结论**，不自行从图上摘取任何数字。凡读者需要确认 Fig. 3 的逐线归属，**必须回原 PDF 高分辨率查看**。

### 4.3 MACs vs 实测延迟（Table 1）——**本节是全文与本库最相关之处**

![[wiki_low_latency/assets/2609.29867/2609.29867-page4.png]]

> 图注：原论文第 4 页页面渲染，用于核对 **Fig. 4 + Table 1 + Table 2 + §4.3 + §4.4 + §5**。**Fig. 4** 是三条纵向对齐的时序图（上：语谱图，纵轴 `0 / 0.25 / 0.5 / 1 / 2 / 4 / 8 kHz`；中：`speech-active` 二值条；下：`exit` 选择序列，纵轴 `0/1/2/3`），横轴 `0–8 s`。**Table 1** 标题为 "Analytic MACs do not price graphs on the STM32N6 NPU. Ten complete int8 single-graph measurements (same board and toolchain)"，四列 `Topology / MMAC/s / ms/frame / µs/MMAC`，共 10 行，**行列归属在渲染图上完整可读，本页已逐格核对**。**Table 2** 标题为 "Measured STM32N6 latency for representative repaired static and routed models"，含**两个分组标题行**（`Within a fixed ladder` / `Across static and dynamic topologies`），四列 `Model / Variant / MMAC/s / int8 PESQ / ms/frame`，`ms/frame` 列部分值**加粗**（`0.930`、`1.668`、`2.684`、`0.751`、`2.762`、`1.364`）。图片为 PDF 页面复制，不是 AI 重画。

**论文的核心观察（p.3 §4.2）**：

> "Hardware latency depends not only on the number of operations, but also on **how they are arranged**. Table 1 shows this clearly on the STM32N6: across **ten measured topologies, execution time per analytic MMAC varies by 1.7×, from 82 to 137 µs/MMAC**. **Depth is particularly costly because each additional stack requires another accelerator launch, while increasing width makes better use of the NPU.**"

**Table 1（10 行 × 4 列，逐格核对渲染图后照抄）**

| Topology | MMAC/s | ms/frame | µs/MMAC |
|---|---:|---:|---:|
| H=32, R=1 | 5.73 | 0.640 | 112 |
| H=64, R=1 | 7.30 | 0.751 | 103 |
| H=32, R=2 | 7.30 | 1.001 | **137** |
| H=96, R=1 | 8.86 | 0.852 | 96 |
| H=64, R=2 | 10.43 | 1.215 | 117 |
| H=96, R=2 | 13.57 | 1.427 | 105 |
| H=256, R=1 | 16.70 | 1.364 | **82** |
| H=96, R=3 | 18.27 | 2.078 | 114 |
| H=256, R=2 | 29.25 | 2.472 | 85 |
| H=256, R=3 | 41.79 | 3.584 | 86 |

论文从这张表读出的三条硬结论（p.3 §4.2）：

| # | 论文原话 | 数据 |
|---|---|---|
| ① | 每解析 MMAC 的执行时间跨 **1.7×** | **82 → 137 µs/MMAC**（$137/82 = 1.671$） |
| ② | 加宽比加深更划算（$H$ 32→256 的 stack 内 MACs 涨 **8×**，实测延迟只涨 **3.1×**） | $256/32=8$；延迟比需用**同 $R$** 的行——$R=1$：$1.364/0.640=2.13$；$R=2$：$2.472/1.001=2.47$；$R=3$：$3.584/2.078=1.72$。**论文给出的 3.1× 与这三个同-$R$ 比值都不吻合**，见下方 [!question] |
| ③ | 相同名义算力可以有不同运行时：$(H{=}32,R{=}2)$ 与 $(H{=}64,R{=}1)$ 的 **MACs 与参数量完全相同**，却是 **1.001 vs 0.751 ms/frame** | 表内两行 MMAC/s **均为 7.30**，延迟 **1.001 vs 0.751**（差 **0.250 ms**，比值 $1.001/0.751=1.333$） |
| ④ | **MAC 甚至给出错误排序**：$(H{=}96,R{=}1)$ 比 $(H{=}32,R{=}2)$ MACs 多 **21 %**，却快 **15 %** | $8.86/7.30 = 1.2137$ → **+21.4 %** ✓；延迟 $1.001 \to 0.852$，$(1.001-0.852)/1.001 = 14.9 \%$ ✓ |
| ⑤ | 因此**不用名义 MACs 估计部署代价**，改为**逐个实测** | 「we therefore do not use nominal MACs to estimate deployment cost, and instead **measure every static, repaired, and routed workload directly on the STM32N6**」 |

论文给出的**机理**（p.3 §4.2）：

> "**Depth is particularly costly because each additional stack requires another accelerator launch, while increasing width makes better use of the NPU.**"

> [!question] 「$H$ 从 32 增到 256，MACs 涨 8×，实测延迟只涨 3.1×」——这个 3.1× **无法由 Table 1 复现**
> 本页用 Table 1 逐对试算（**同 $R$ 才可比**，因为论文这句的语境是"加深很贵、加宽便宜"）：
> | 比较 | $H$ 比 | MACs 比 | 实测延迟比 |
> |---|---:|---:|---:|
> | $R=1$：$H{=}256$ vs $H{=}32$ | $8.00$ | $16.70/5.73 = 2.92$ | $1.364/0.640 = 2.13$ |
> | $R=2$：$H{=}256$ vs $H{=}32$ | $8.00$ | $29.25/7.30 = 4.01$ | $2.472/1.001 = 2.47$ |
> | $R=3$：$H{=}256$ vs $H{=}96$ | $2.67$ | $41.79/18.27 = 2.29$ | $3.584/2.078 = 1.72$ |
>
> **"MACs 涨 8×" 与 Table 1 的任何一对都不一致**（论文说的 8× 应为 **$H$ 通道数之比** $256/32=8$，即**stack 内部的通道宽度比**，而非全模型 MMAC/s 比——全模型 MMAC/s 比在同一 $R$ 下只有 2.9–4.0×，因为 frontend 与 head 是固定成本）。**而 "实测延迟只涨 3.1×" 在 Table 1 中找不到对应的行对**：最接近的是……**没有一对达到 3.1**（最高的同-$R$ 比值是 2.47）。
> 用户 brief 把这一条转述为「H 从 32 增到 256，stack 内 MACs 涨 8×，实测延迟只涨 3.1×」。**本页核对结论：8× 是 stack 内通道比（与 Table 1 的 MMAC/s 列不是同一口径，但论文原文确实说的是 "the MACs within a stack"，所以口径自洽）；3.1× 在 Table 1 中无法定位到具体的行对。** 论文**未说明**这个 3.1× 是哪两个拓扑之比、是否用了 Table 1 之外的数据。本页**照录论文原话并标注无法复现**，不做代填。

> [!note] Table 1 是本库**第一张"真机 int8 逐图实测"表**，比任何名义 MACs 表都硬
> 需要明确它的**证据等级**：这不是仿真、不是估算，是 **10 个完整 int8 单图**在同一块板、同一条工具链上的**端到端 per-frame 执行时间**（含 frontend、含 head）。因此本库把它记为**算力证据的"实测级"**（最高级），而 [[wiki_low_latency/entities/FastEnhancer]] 的 RTF 是**单线程 CPU 吞吐**（不同的量纲）、[[wiki_low_latency/entities/D-GRU]] 的 MACs 是**解析计数**（最低级）。三篇合起来正好构成本库算力证据的三个等级（见概念页"对本库的改进建议"）。

### 4.4 部署平台（§4.1）

| 项目 | 论文设置 |
|---|---|
| 平台 | **STM32N6570-DK** |
| 主机 | **Arm Cortex-M55**（**800 MHz**） |
| 加速器 | **STMicroelectronics Neural-ART** NPU（**1 GHz**） |
| NPU 能力边界 | 「The NPU targets **statically shaped, integer-quantized workloads**, while **unsupported operations and graph orchestration remain on the Cortex-M55**.」 |
| 因果性声明 | 「**All networks are causal at a 16 ms hop.**」 |
| host 侧保留的算子 | 「We keep the **STFT, iSTFT and masking on the host (no NPU FFT)**」 |
| 状态导出 | 「export **ring buffers as explicit state tensors**, making **each graph a pure per-frame stateless function**」 |
| 量化 | ONNX → **post-training int8** [32]，**per-channel scaling + entropy calibration** |
| 编译 | **ST Edge AI Core v4.0** [6]，含 operator rewrites |
| 编译器报告 | 提供 **NPU/host partition 与 memory requirements**（**论文未报告具体数值**） |

> [!note] "ring buffers as explicit state tensors" 是本篇最值得本库借用的工程做法
> 把流式状态**显式化为图输入/输出张量**，于是每张图成为**纯逐帧无状态函数**（"pure per-frame stateless function"）。这一步同时解决三件事：
> ① **可静态编译**（无隐式状态 → 图是纯函数 → 工具链可以一次性 lower）；
> ② **可 int8**（状态张量显式 → 量化范围可标定）；
> ③ **可上 NPU**（NPU 只吃静态 shape）。
> 这与 [[wiki_low_latency/sources/2026/LaCo-SENet 2026]] 用逐层 padding 分配式换取确定延迟、[[wiki_low_latency/sources/2025/FastEnhancer 2025]] 用 BN 融合换取可编译性是**同一类工程动作**：**把"运行时才能确定的东西"提前变成"编译期就能确定的东西"**。详见概念页命题 ⑤。

### 4.5 动态执行与"跳过时的状态"（§4.3）——**本库最值得记录的一节**

**子图切分（p.4 §4.3 Model export）**

> "the dynamic models are deployed as **nine subgraphs** for the **frontend, router, three stacks, and four exit heads**, with the **routing decision and dispatch handled by the host**. Because **different depths share the same frontend and stack graphs**, the full family requires **the same storage of a single ladder rather than several separate models**."

**量化误差（p.4 §4.3）**

> "Quantized outputs remain close to float with the shared compressed-magnitude $|X|^{0.3}$ input: the **repaired family changes by only −0.03 to +0.01 PESQ**, and **quantization shifts routed compute by at most 2 %**."

**State under skipping（p.4 §4.3）——本页认为是全文最重要的一段工程陈述**

> "Each stack maintains its own **ring buffers** for the dilated convolutions. **These buffers are updated only when that stack runs**, so **when a skipped stack resumes, its state reflects the most recent frames processed by that stack rather than the most recent input frames**. This is **far more realistic than common offline evaluation protocols, which compute the routed output as a gated sum, thereby effectively updating each exit even when unused**. Driving the exported graphs on the deployed path costs **−0.005±0.011 PESQ over 824 clips and 0.14 dB SI-SDR**, with **routing decisions bit-identical across arms**. **Neither zero-order hold nor propagating the last computed state to deeper stacks [33] recovers the lost quality.** We therefore **keep skipped-stack states unchanged**, which is already the behavior of the exported graphs and **requires no firmware modification**."

> [!warning] 这一段直接指出**本库（以及绝大多数论文）沿用的评测协议是偏乐观的**
> 常见离线协议把 routed 输出算成 **gated sum**——即"对所有 exit 的输出做门控加权求和"。这种算法的**副作用**是：**即使某个 exit 本帧没被选中，它的状态仍然在更新**。
> 因此在这种协议下评测的"动态模型"，**实际上从未经历过"状态冻结"**，其质量被系统性高估。
> 本篇改为**真的不更新**（跳过就是跳过），代价是 **−0.005±0.011 PESQ / 0.14 dB SI-SDR**。
> **本库口径**：这与 [[wiki_low_latency/concepts/2207.11108-inference-skipping-parallel-rnn]] 讨论的 "peak vs average" 是**同类问题在另一个维度上的表现**——前者关心"算力峰值是否真的降了"，本篇关心"**状态是否真的没更新**"。两条都属于"评测协议本身会制造虚假收益"（见概念页命题 ④）。

**bit-identical 的重要性**：论文声明「routing decisions **bit-identical across arms**」——即"走部署路径的导出图"与"离线参考路径"给出了**完全相同的路由决策序列**。这让 §4.5 的 −0.005 PESQ 差值成为一个**干净的单变量对照**（唯一变量是"状态是否更新"），而不是"决策 + 状态"混合效应。

**零阶保持与状态传播都无效**：

> "Neither **zero-order hold** nor **propagating the last computed state to deeper stacks** [33] **recovers the lost quality**."

引 [33] 是 Elbayad 等 Depth-adaptive transformer（ICLR 2020）。论文试了两种补救方案（保持上一输出 / 把更浅层算出的状态推给更深层），**都没能把丢掉的质量找回来**，因此选择**不补救**——理由很实在：「already the behavior of the exported graphs and **requires no firmware modification**」。

> [!question] 「零阶保持与状态传播都不能恢复」这一结论**只有定性陈述，没有数据**
> 论文没有给出这两种补救方案各自的 PESQ/SI-SDR 数值（哪怕一句"仍差 −0.005"），也没有说明两种方案的实现细节（零阶保持保持的是什么？推给更深的是哪一层的状态？）。
> 本页记录为**未报告**：这是一个**可直接补做的小实验**，且结论对工程实现有直接影响。

### 4.6 端上结果（Table 2，§4.4）——**全文结论的落地证据**

**Table 2（分组结构核对渲染图后照抄）**

| Model | Variant | MMAC/s | int8 PESQ | ms/frame |
|---|---|---:|---:|---:|
| **Within a fixed ladder** |||||
| Static H=64, R=2 | fixed | 10.4 | 2.716 | 1.215 |
| Routed H=64 | $\varepsilon=2\cdot10^{-3}$ | 8.58 | 2.694 | **0.930** |
| Static H=256, R=2 | fixed | 29.3 | 2.781 | 2.472 |
| Routed H=256 | $\varepsilon=2\cdot10^{-3}$ | 20.19 | 2.773 | **1.668** |
| **Across static and dynamic topologies** |||||
| Static H=64, R=1 | fixed | 7.3 | 2.684 | **0.751** |
| Routed H=32 | $\varepsilon=2\cdot10^{-3}$ | 6.34 | 2.639 | 0.769 |
| Routed H=96 | $\varepsilon=2\cdot10^{-3}$ | 10.51 | 2.683 | 1.040 |
| Static H=256, R=1 | fixed | 16.7 | 2.762 | **1.364** |
| Routed H=64 | $\varepsilon=5\cdot10^{-4}$ | 12.29 | 2.724 | 1.473 |

**第一段结论：固定 ladder 内，早退确实省时间**（p.4 §4.4）

> "**Within a fixed ladder, early exit provides a clear reduction in average execution time.** For example, repaired routed H=64 at $\varepsilon=2\cdot10^{-3}$ runs at **0.930 ms/frame**, compared with **1.215 ms** for the corresponding H=64, R=2 static, while PESQ changes **from 2.716 to 2.694**. At H=256, routing reduces latency **from 2.472 to 1.668 ms/frame** while retaining **2.773 versus 2.781 PESQ**. Thus, **when the backbone is fixed, routing can avoid substantial work with little quality loss.**"

| 对照（固定 ladder 内） | ms/frame | PESQ |
|---|---|---|
| Static H=64, R=2 → Routed H=64 | $1.215 \to 0.930$（**省 23.5 %**） | $2.716 \to 2.694$（**−0.022**） |
| Static H=256, R=2 → Routed H=256 | $2.472 \to 1.668$（**省 32.5 %**） | $2.781 \to 2.773$（**−0.008**） |

**第二段结论：一旦允许静态拓扑也变，优势几乎消失**（p.4 §4.4）

> "**The advantage is much smaller once the static topology is also allowed to change.** Several routed points are **matched or dominated** by a different static width/depth choice: **routed H=32 gives 2.639 PESQ at 0.769 ms/frame, while static H=64, R=1 reaches 2.684 at 0.751 ms**; routed H=96 similarly reaches **2.683 at 1.040 ms**. The more quality-oriented routed configurations show the same trend: **routed H=64 with asym4 reaches 2.724 at 1.473 ms, whereas static H=256, R=1 reaches 2.762 at 1.364 ms**. **Dynamic depth therefore mainly provides intermediate operating points within one deployed ladder; it does not create a better latency–quality frontier than architecture-matched statics.**"

| 对照（跨静态与动态拓扑） | Routed | Static | 结论 |
|---|---|---|---|
| 偏低算力 | Routed H=32：PESQ **2.639** @ **0.769 ms** | Static H=64, R=1：PESQ **2.684** @ **0.751 ms** | **static 被支配方反转为支配方**（static 更快 **0.018 ms** 且 PESQ **高 0.045**） |
| 中算力 | Routed H=96：PESQ **2.683** @ **1.040 ms** | ——（论文只给了一个点，未配同算力静态） | 论文原话是 "similarly" |
| 偏质量 | Routed H=64（$\varepsilon=5\cdot10^{-4}$）：PESQ **2.724** @ **1.473 ms** | Static H=256, R=1：PESQ **2.762** @ **1.364 ms** | static **更快 0.109 ms** 且 PESQ **高 0.038** |

论文的最终结论（p.4 §4.4 末）：

> "**Dynamic depth therefore mainly provides intermediate operating points within one deployed ladder; it does not create a better latency–quality frontier than architecture-matched statics.**"

> [!question] `asym4` 在全文**从未定义**
> §4.4 出现「routed H=64 **with asym4** reaches 2.724 at 1.473 ms」——用户 brief 把它对应到 Table 2 的 `Routed H=64 / ε=5·10⁻⁴ / 12.29 / 2.724 / 1.473` 这一行。**本页核对渲染图后确认这个对应是唯一自洽的**（Table 2 中 **只有这一行**的 PESQ 是 2.724、ms/frame 是 1.473，与正文的 "asym4" 句完全对应）。
> **但 `asym4` 这个记号在全文（含 References）没有出现过第二次，也没有任何定义。** 本页**不猜测**它的含义（"asymmetric"？某档配置的简称？），记录为**未定义**。用户 brief 已正确指出这一点。

### 4.7 其他结果与消融

除上述四组外，论文还给出：

| 结果 | 数值 | 出处 |
|---|---|---|
| 修复带来的 PESQ 增益 | **0.04–0.11 PESQ**（同一训练预算下） | §5 结论 |
| 以更少算力匹配最好模型 | 少 **30 %** 算力匹配最好 PESQ，但**代价是 1.0 dB SI-SDR 下降** | §5 结论、Abstract（Abstract 写作 "match the best PESQ at 30 % less compute"） |
| 量化对 repaired family 的影响 | **−0.03 ~ +0.01 PESQ** | §4.3 |
| 量化对 routed 算力的偏移 | **至多 2 %** | §4.3 |
| router 在 host 上的开销 | **26 µs per frame**（Abstract） | Abstract |
| 拆成多张 NPU 图的额外开销 | **+2.2 % latency overhead**（Abstract） | Abstract |
| 部署路径相对离线路径的质量差 | **−0.005±0.011 PESQ**、**0.14 dB SI-SDR**（824 条片段） | §4.3 |
| 「近一半的帧上更深 exit 更差」 | **nearly half of the frames**（无精确比例） | §1 |

> [!question] Abstract 的 "30 % less compute" 与 §5 的措辞不同，且**都没有给出对应的配置对**
> - **Abstract**：「we achieve up to **0.11 higher PESQ for equivalent compute**, and **match the best PESQ at 30 % less compute**」；
> - **§5**：「We could also **match the best model (in terms of PESQ) with 30 % less compute**, although at a **1.0 dB SI-SDR drop**」。
>
> 两处数字一致（30 %），但**论文没有说明这是哪一对模型**（哪个是 "the best model"、哪个是"少 30% 算力的模型"），也没有给出这两个模型的具体 PESQ 与 SI-SDR。
> 本页**不代填**：读者无法从论文数据中复原这条 30 % 主张。**附带的疑点**：§5 说这条匹配"**代价是 1.0 dB SI-SDR 下降**"，与 Abstract 的正面表述（"match the best PESQ"）语气不同——**PESQ 匹配但 SI-SDR 掉 1 dB** 是一个**指标方向不一致**的情形，论文在 §5 里点了出来但未展开。

> [!question] "26 µs per frame" 与 "2.2 % latency overhead" 这两个 Abstract 数字，在正文里**找不到对应的完整语境**
> - **26 µs/frame**：§4.3 只说「since the policy router runs on the dedicated M55 core, we report its contribution from **measured cycle counts at its 800 MHz clock**」——**没有给出 26 µs 这个数**。Abstract 是它唯一的出现处。
> - **+2.2 % latency overhead**：§4.3 只说把 enhancer 拆成独立子图，**没有给出 2.2 % 这个数**。Abstract 是它唯一的出现处。
>
> 两处都是**可复核的量化主张**，但正文未给出测量条件（相对什么基准的 2.2 %？26 µs 是含派发还是仅含 GRU 推理？）。本页记录为**正文未报告细节**。

> [!question] Table 2 缺两组"应有的"行，让"跨拓扑"这一节的对照不完整
> Table 2 的第二个分组标题是 `Across static and dynamic topologies`，其立论是"允许静态拓扑也变时，路由的优势消失"。但表内**缺少与 routed H=96（10.51 MMAC/s, 2.683, 1.040 ms）对应的静态行**——而表内**有** `Static H=64, R=2`（10.4 MMAC/s, 2.716, 1.215 ms），算力几乎相同（**10.4 vs 10.51**）。
> 若把这两行并列：**static H=64,R=2 的 PESQ 高 0.033（2.716 vs 2.683），但 ms/frame 高 0.175（1.215 vs 1.040）** ——即这是一个**真实的 trade-off**（static 更准、routed 更快），而不是支配关系。
> 论文在同一段里只写了「routed H=96 **similarly** reaches 2.683 at 1.040 ms」，**没有把它与表内已有的 `Static H=64, R=2` 对比**。本页认为这处遗漏**弱化了论文"matched or dominated"的措辞**（在这一点上两者是 matched `对价`而非 dominated）。这是本页从渲染图对照后读出的，**论文自身未讨论**。

## 5. 这个方向还剩什么问题没解决？（future work / limitation）

### 5.1 论文自己承认的局限（**写得非常明确，值得表扬**）

1. **数据集局限**（§1 与 §5 各写一次）：
   > "Our claims are **limited to speech-dense datasets (VoiceBank–DEMAND)**; while arguably more realistic, **workloads with long pauses are outside this study**."（§1）
   > "**On speech-dense datasets, however, per-frame depth selection brings little additional benefit.**"（§5）
2. **未来工作明确写成一条**（§5 末）：
   > "**Whether automatic routing becomes more valuable on sparser workloads, where long pauses and cheap bypass opportunities are common, remains an important next step.**"
3. **诚实的代价陈述**：以少 30 % 算力匹配最好 PESQ，**代价是 1.0 dB SI-SDR 下降**（§5）。
4. **状态跳过不能补救**：零阶保持与状态传播**都不能恢复**丢失的质量（§4.3）。

### 5.2 本页读出的隐藏问题（本库关注）

**(a) 延迟账本：厚，但缺 p99。**

本篇的账本**比库内多数论文都厚**——这是它的正面资产：

| 项 | 状态 |
|---|---|
| 真机 per-frame 平均延迟 | **有**（Table 1 十行 ms/frame；Table 2 九行 ms/frame） |
| µs/MMAC 归一化 | **有**（Table 1 第四列，82–137） |
| 量化误差 | **有**（repaired family −0.03~+0.01 PESQ；routed 算力 ≤2 %） |
| 部署路径 vs 离线路径 | **有**（−0.005±0.011 PESQ、0.14 dB SI-SDR） |
| 决策一致性 | **有**（bit-identical across arms） |
| router 自身开销 | **有**（26 µs/frame，但只在 Abstract） |
| 子图切分开销 | **有**（+2.2 %，但只在 Abstract） |
| 平台与频率 | **有**（STM32N6570-DK；Neural-ART 1 GHz；Cortex-M55 800 MHz） |

**但它缺的是**：

- **平均延迟 ≠ p99**。「0.930 ms/frame」是**平均**（论文原文 "measured **per-frame mean** latency"），而实时约束关心的是**最坏帧**。**未报告** p50/p95/**p99**、**未报告** θ 分布；
- **未报告 deadline miss / underrun / overrun**。在 16 ms hop 下，最慢的实测拓扑是 3.584 ms/frame（H=256, R=3），**看似有余量**，但这是平均值，且论文**没有把这个 16 ms 与任一实测 ms/frame 并列讨论过**——**更没有任何一句把"算法延迟"与"每帧执行时间"区分开**；
- **未报告峰值 RAM/SRAM**（虽然说了"compiler reports provide ... memory requirements"，但**数值未给出**）；
- **未报告功耗**——对一个以"shared battery budget"为动机的论文，这是一个显著的缺口；
- **未报告 STFT/iSTFT 在 host 上的耗时**。原文明确 "We keep the STFT, iSTFT and masking on the host"，但**host 侧这些算子的成本没有出现在 Table 1/2 的任何一行里**。因此 Table 1/2 的 ms/frame **不是端到端**的，而是**NPU 图（+ router）**的耗时。这是本页认为**最容易被误读**的一点。

> [!warning] Table 1 / Table 2 的 ms/frame **不是端到端延迟**——本节是本页给本库的最重要提醒
> - 论文自己写清了："We keep the **STFT, iSTFT and masking on the host (no NPU FFT)**"；
> - Table 1 的标题写的是「Ten complete **int8 single-graph** measurements (same board and toolchain)」——**single-graph** 指"整个增强器被 lower 成一张 int8 图"，但**这张图里不含 STFT/iSTFT**（它们留在 host）；
> - 因此 **0.640 ms/frame** 的含义是"**NPU 上那张图的执行时间**"，**不是** capture-to-playback。
>
> 本库口径（[[wiki_low_latency/concepts/严格因果与算法延迟]]）要求「算法延迟 ≠ 计算耗时 ≠ 端到端」，**三者必须分开报**。本篇提供了三者中的**第二项**（计算耗时的平均值），**没有提供第一项**（算法延迟的明确定义与数值），**也没有提供第三项**（端到端）。

**(b) 因果性：只有一句声明，缺全部前端证据。**

论文关于因果性的**全部**表述是（p.3 §4.1）：

> "All networks are **causal at a 16 ms hop**."

以及 §4.1 的两句间接支持：把 STFT/iSTFT 留在 host、把 ring buffer 导出为显式 state tensor（"making each graph a **pure per-frame stateless function**"）。

**缺的**：

- **STFT center 与否未报告**（决定性缺口，见 §4.1 的 warning）；
- **未给逐层 padding / state certificate**（哪一层用什么 padding、padding 是否为零、state 如何跨帧更新）；
- **未给"跳过"对因果性的解释**——这一点其实**反过来是加分项**：因为被跳过的 stack 的状态**不更新**（§4.3），所以任何输出都**只依赖该 stack 最近真正处理过的帧**，**不可能引入未来依赖**。这是一个**结构性**的因果保证，比多数论文的"我们用了因果卷积"更强。**但论文没有把它写成因果性论证**（它是在讲评测协议时顺带提到的）。
- **感受野 1/15/29/43 帧是否含未来成分未说明**（见 §3.2 的 [!question]）。

**(c) 人声保留：指标维度很窄。**

| 本库要求字段 | 本篇报告情况 |
|---|---|
| SI-SDR | **有**（whole-clip SI-SDR [30]，824 条） |
| PESQ | **有**（wideband PESQ [31]，824 条） |
| PESQ 的 narrow-band 版本 | **未报告** |
| STOI / ESTOI | **未报告** |
| DNSMOS **SIG / BAK / OVL** | **全部未报告**（本库特别关注 SIG–BAK trade-off） |
| ASR WER（可懂度） | **未报告** |
| 负 SNR 分层（−10/−5/0/5 dB） | **未报告**。全集层面只有 **Fig. 4 那一条示例语句的 0.46 dB**，**不是分层结果** |
| 噪声类型分层（babble / 竞争说话人 / 瞬态 / 未见噪声） | **未报告** |
| false-suppression | **未报告** |
| SPP / VAD 校准 | **未报告** |
| F0 / formant / prosody continuity | **未报告** |
| voiced energy 保留 | **未报告** |
| 听感 MOS（主观） | **未报告** |

**结论**：本篇的人声保留证据**只有 SI-SDR + PESQ 两个整句指标**。对一个把"人声保留"当一等目标的本库而言，**它的质量主张的证据面是窄的**。特别是 §5 那条「match the best model with 30 % less compute, **although at a 1.0 dB SI-SDR drop**」——**没有 SIG/BAK/WER 的支撑，无法判断这 1 dB 的下降落在"噪声残留"还是"语音损伤"上**。

**(d) 算力证据等级：本库最高，但口径需注明。**

| 维度 | 本篇 |
|---|---|
| 是名义 MACs 还是实测 | **实测**（ms/frame，真机 int8） |
| 测了什么 | **10 个静态拓扑 + 9 个部署模型** |
| 是否量化 | **是**（int8，per-channel + entropy calibration） |
| 是否在同一板/同工具链 | **是**（"same board and toolchain"） |
| 是平均值还是分位数 | **平均**（"per-frame mean latency"） |
| 是否含端到端 | **否**（STFT/iSTFT 留在 host） |
| 是否报功耗 | **否** |
| 是否报内存 | **否**（只说编译器报告有，未给数值） |

**这是本库目前算力证据最完整的一篇**，但它的完整性有两条边界：**平均而非 p99**、**不含 host 侧 STFT/iSTFT**。

**(e) 论文未报告的全模型参数量。**

论文**只报告了 exit heads 的 4×33k 参数**。全模型参数量、每档 $H$ 的参数量、$B=128$ 与 $H_i$ 的具体取值（$H_i$ 是否等于 $H$？论文用了两个记号 $H$ 与 $H_i$）**均未报告**。因此本库**无法**把这个实体放入任何"参数量 vs 性能"的横比。

> [!question] $H$ 与 $H_i$ 是两个记号还是一回事，论文没有澄清
> §2.1 写「expanded into $H_i$ channels **within each $i$-th block**」——下标 $i$ 暗示**每个 block 可以有不同的宽度**；
> 而 §3.1 与 Table 1/2 的所有配置都只用一个 $H$（`H=32/64/96/256`）。
> 因此有两种读法：**(a)** $H_i \equiv H$，所有 stack 同宽，$i$ 只是形式下标；**(b)** 每个 stack 可以不同宽，但论文的实验只用了同宽配置。
> 论文**没有说明**。本页按 (a) 记录（合理默认），但标注为**未澄清**。

**(f) 训练可复现性。**

**已报告**：Adam，lr（主干 $10^{-3}$ / 修复 $10^{-4}$）、weight decay $10^{-5}$、每 epoch 衰减 0.99、batch 64、early stopping、4 s 随机裁、三种增广、修复 2000 步与正则权重 50。
**未报告**：训练总 epoch/步数、**随机种子数与 seed spread**（§1 贡献 3 提到了 "with seed spreads and controls"，**但正文没有任何 seed spread 的数值**）、验证集划分、$B=128$ 的依据、$\mathcal L_{cost}$ 的具体形式与 $\tau$ 的取值、Gumbel-softmax 的温度、$H_i$ 的具体取值。

> [!question] 贡献列表承诺的 "seed spreads" 在正文中没有兑现
> §1 的第 3 条贡献写：「A compute–matched static frontier retrained under the same recipe and evaluation harness, **with seed spreads and controls**」。
> 但正文**没有任何表格或文字给出 seed spread**（无标准差、无 min/max、无多种子均值）。仅 Table 2 caption 与 §3.1 一次都没提种子数。
> **这与 [[wiki_low_latency/sources/2025/FastEnhancer 2025]] 的问题同构**（那篇报了 5 seeds 但不给方差）。对本篇而言**更严重**，因为它的核心结论依赖 0.01–0.05 PESQ 量级的差值（例如 §4.2 的 +0.009 / −0.001 / +0.007），**而这些差值是否落在种子波动之内，本库无法判断**。

### 5.3 与约 2 ms 约束的距离

- **算法延迟**：论文**没有给出任何算法延迟数值**，也没有定义其口径（无 window−hop、无 $W/2$、无推导式）；
- **前沿**：窗口 512 samples = **32 ms**，hop 256 samples = **16 ms**，论文反复以 "16 ms hop" 为因果性锚点；
- **计算结果**：最慢的实测拓扑 3.584 ms/frame、最快的 0.640 ms/frame（**均为 NPU 图的平均执行时间，不含 host 侧 STFT/iSTFT**）。

**本库判定**：即便假设 hop 就是算法延迟下界（16 ms），它也比约 2 ms 目标**高一个量级**；而若 STFT 采用 `center=True`，还要再加 16 ms。**本篇不是约 2 ms 级的系统**，它甚至**没有把自己放进这个量级去讨论**——它的目标场景是助听器/耳机类设备的**per-frame 算力预算**，而非 2 ms 级算法延迟。本页据此把它归入「**端侧动态算力与真机延迟**」议题，而非「约 2 ms 严格因果」议题。

## 6. 本论文在库中的位置关联（cross-reference matrix）

| 关系 | 库中论文/概念 | 关联与差异 |
|---|---|---|
| **同谱系对照（推理期动态算力）** | [[wiki_low_latency/entities/D-GRU]]、[[wiki_low_latency/sources/2024/D-GRU 2024]]、[[wiki_low_latency/concepts/2408.12425-dynamic-gated-rnn]]、[[wiki_low_latency/entities/Skip-DPCRN]]、[[wiki_low_latency/concepts/2207.11108-inference-skipping-parallel-rnn]] | **本库动态算力这条线上的三篇构成一个完整序列**：Skip-DPCRN 跳**整步**（平均省 33 %、峰值只降 15 %，且需并行宿主）→ D-GRU 跳**神经元**且**数量固定**（消除平均/峰值落差，但**只有 MACs、无任何延迟测量**）→ **本篇跳整段 stack，逐帧选深度，并且在真机上实测出"跳了确实快 36 %"**（H=256: 2.472→1.668 ms）**但同时证明"质量上限没变"**。即：**本篇是这条线上第一篇既证明"跳得动"、又证明"跳了不值"的工作**。 |
| **同命题、不同机理（MACs ≠ 速度）** | [[wiki_low_latency/entities/FastEnhancer]]、[[wiki_low_latency/sources/2025/FastEnhancer 2025]]、[[wiki_low_latency/concepts/2509.21867-speed-optimized-streaming-design]] | 两篇都持"名义算力不能预测速度"，但**机理归因不同**：FastEnhancer → **算子可融合性 / 内存操作**（BN 可融合 vs LN 不可，时间轴 kernel 1→3 增缓存）；本篇 → **accelerator launch 次数 / NPU 利用率**（深度每加一层多一次 launch，宽度更能吃满 NPU）。**证据等级也不同**：FastEnhancer 是单线程 Xeon/M1 的 RTF（CPU 吞吐）；本篇是 MCU 上 int8 图的 ms/frame（真机延迟）。两篇合读可得到本库最完整的一组"为什么 MACs 会给出错误排序"。 |
| **同议题（评测协议会制造虚假收益）** | [[wiki_low_latency/concepts/2207.11108-inference-skipping-parallel-rnn]]、[[wiki_low_latency/sources/2022/Skip-DPCRN 2022]] | Skip-DPCRN 的议题是「**平均省 33 %、峰值只降 15 %**」——即"平均值掩盖了峰值"；本篇的议题是「**gated sum 协议让未使用的 exit 也在更新状态**」——即"协议掩盖了跳过"。两条都是**评测口径**问题，可以合成一条一般规则（见概念页命题 ④）。 |
| **最严因果审计尺子** | [[wiki_low_latency/entities/LaCo-SENet]]、[[wiki_low_latency/sources/2026/LaCo-SENet 2026]]、[[wiki_low_latency/concepts/2606.19688-latency-configurable-asymmetric-padding]] | LaCo-SENet 给出逐层 padding 分配式 + 状态选择算子，是本库因果审计的最高标准。用它的尺子量本篇：**STFT center 未报告、逐层 padding 未给、感受野的 look-ahead 属性未说明**——因此本篇的 `paper-claimed-causal` **不能升级为 `strict_causal`**。**但本篇有一个 LaCo-SENet 也没有的结构性保证**：被跳过的 stack 状态不更新 ⇒ 任何输出只依赖该 stack 真正处理过的帧 ⇒ **不可能引入未来依赖**（见 §5.2b）。 |
| **低时延前端账本** | [[wiki_low_latency/concepts/低时延前端与延迟账本]]、[[wiki_low_latency/entities/STFT-Very-Low-Latency-SE]]、[[wiki_low_latency/sources/2022/STFT-Domain Very Low Algorithmic Latency 2022]]、[[wiki_low_latency/concepts/2204.09911-short-asymmetric-stft]] | 本篇给了窗长与 hop（512/50 %），**没给 center**。这些页面提供了"把窗长+hop+center 换算成算法延迟"的账本模板，正是本篇所缺的。 |
| **端侧部署（真机 int8 实测）** | [[wiki_low_latency/entities/RT-SEMamba]]、[[wiki_low_latency/sources/2026/RT-SEMamba 2026]]、[[wiki_low_latency/entities/PSMSE]]、[[wiki_low_latency/sources/2026/PSMSE 2026]] | 本库另有若干端侧/流式记录。**本篇的独特性在于"逐图真机实测 + 量化 + 路由派发"三段全齐**，且明确报告了工具链（ST Edge AI Core v4.0）与开发板型号。 |
| **人声保留缺口** | [[wiki_low_latency/concepts/低 SNR 人声保留评估]]、[[wiki_low_latency/sources/2023/Uncertainty-Aware Speech Enhancement 2023]]、[[wiki_low_latency/sources/2022/Hybrid Continuity Loss 2022]] | 本篇只有 SI-SDR + PESQ，**无 SIG/BAK、无 WER、无负 SNR 分层、无 false-suppression、无 F0/prosody**。这些页面提供本篇缺失的验收字段。 |
| **训练脚手架 / train-once-deploy-many** | [[wiki_low_latency/entities/D-GRU]]（$P$ 扫描产生一族共享参数模型） | **结构同源**：D-GRU 用同一次训练产生多个 $P$ 档位（共享全部参数），本篇用同一次训练产生 4 个深度（共享 backbone，仅 head 不同）。**但两者的动机相反**：D-GRU 要的是"每步算力恒定"，本篇要的是"一次训练产出一族可导出的静态模型"。 |
| **概念页** | [[wiki_low_latency/concepts/2609.29867-compute-matched-dynamic-depth]] | 抽象出"算力对齐是前提""早退的增益可能来自训练脚手架""名义 MACs 会给出错误排序（与 FastEnhancer 机理不同）""评测协议本身会制造虚假收益""显式 state tensor 是可部署前提"五条可复用命题，并提出本库改进建议。 |
| **实体页** | [[wiki_low_latency/entities/Early-Exit-Conv-FSENet]] | 架构、exit ladder、router、Table 1/Table 2 全表、状态与因果性、低时延账本、结果与证据边界。 |

## 7. 一句话总结"江湖地位"

> **2026 | 动态深度 / 端侧部署 / 评测方法学 | 用"4 级 exit ladder + 一次性 GRU-16 router + heads-only 单调性修复"在算力对齐的公平对照下证明：**逐帧早退在语音密集数据集上几乎不提高给定算力下的最优质量**（mono-repaired 前沿与 routed 前沿的 PESQ 差 < 0.01），**但它作为训练脚手架能产出比从零训练的同尺寸模型更 Pareto 高效的静态模型**（同算力下最多 +0.11 PESQ；少 30 % 算力匹配最好 PESQ，代价 1.0 dB SI-SDR）；同时在 STM32N6570-DK 上给出本库第一张**真机 int8 逐图实测**算力表——**10 个拓扑的每 MMAC 执行时间差 1.7×（82–137 µs/MMAC）**，深度贵在"每次 accelerator launch"、宽度更能吃满 NPU，(H=32,R=2) 与 (H=64,R=1) 的名义 MACs 与参数量完全相同却差 0.25 ms/frame，MACs 甚至给出错误排序；并明确指出常见离线评测用 **gated sum** 会让"未使用的 exit 也在更新状态"，本篇改为真的不更新（代价 −0.005±0.011 PESQ）→ 它是**"动态算力"这条线上第一篇既证明跳得动、又证明跳了不值的工作**，把[[wiki_low_latency/entities/D-GRU]]（只有 MACs、无延迟）与[[wiki_low_latency/entities/FastEnhancer]]（有 RTF、无真机延迟）留下的两个缺口同时补上；但它**未报告 STFT center**（因果判定只能停在 `paper-claimed-causal`）、**只报平均 ms/frame 而无 p99**、ms/frame **不含 host 侧 STFT/iSTFT**、承诺的 seed spread 未兑现，且**人声保留只有 SI-SDR + PESQ 两项**。**
> 一句话版：**"早退的价值不在于运行时省了多少，而在于它逼你训出了一族更好的静态模型"** —— 而这句话只有在**算力对齐 + 同配方重训 + 真机实测**三个条件下才成立，这三个条件正是本文真正的贡献。

## 参考资料

- [arXiv:2609.29867](https://arxiv.org/abs/2609.29867)
- 本地原件：`raw/papers/low_latency_causal_se/2609.29867.pdf`
- 本地文本抽取：`tmp/pdf_extract/2609.29867.txt`
- 页面渲染核对：`wiki_low_latency/assets/2609.29867/`（page1–page5，150 dpi）。本页核对方式：**page1**（标题/作者/单位/基金脚注/arXiv 侧栏/Index Terms）、**page2**（Fig. 1、Fig. 2、Eq. 1–7 与 §2.1–§2.3 全文）、**page3**（§3.1 设置、§3.2 前沿叙述、§4.1 平台、§4.2 MACs vs 延迟、Fig. 3 的图例与坐标轴）、**page4**（Fig. 4、Table 1 十行、Table 2 九行与两个分组标题、§4.3–§4.4、§5）、**page5**（References [1]–[33]，用于核对 GTCRN 页码与引文元数据）。
- 本页嵌入 2 张：`2609.29867-page2.png`（Fig. 1 exit ladder + Fig. 2 residual block + Eq. 1–7）、`2609.29867-page4.png`（Fig. 4 + Table 1 + Table 2 + §4.3–§5）。
- 论文内关键引用：[1] Braun 等实时深度抑噪效率；[2] **GTCRN**（Rong 等，ICASSP 2024）；[3] Once-for-all；[4] TODM（on-device ASR）；[5] 动态神经网络综述（Han 等，TPAMI 2022）；[6] **ST Edge AI Core v4.0**；[7] **Kaya 等 Shallow-deep networks（"overthinking"，ICML 2019）**；[8] **Dynamic NSNet2**（Miccini 等，MLSP 2023）；[9] Probabilistic early exits for speech separation（ICLR 2026）；[10] **Scalable SE with dynamic channel pruning**（Miccini 等，ICASSP 2025）；[11] Adaptive slimming（WASPAA 2025）；[12] Dynamically slimmable SE network（ICASSP 2026）；[13] Dynamic layer gating（Interspeech 2025）；[14] Stochastic depth；[15] Layer dropout；[16] Universally slimmable networks；[17] Subnetwork-to-go（elastic music separation）；[18] **Dynamic slimmable networks for efficient speech separation**（arXiv 2507.06179）；[19] **ShuffleNet V2**（MACs 不是速度）；[20] **Jazbec 等 Towards anytime classification（NeurIPS 2023）**；[21] 同一作者的 ICASSP 2026 工作；[22] **Conv-TasNet**（Luo & Mesgarani，TASLP 2019）；[23] Braun & Tashev 损失函数综述（TSP 2021）；[24] Deeply-supervised nets（AISTATS 2015）；[25] Progressive speech enhancement with residual connections（Interspeech 2019）；[26] **Gumbel-Softmax**（Jang 等，ICLR 2017）；[27] **Valentini-Botinhao 等 VoiceBank–DEMAND（ISCA SSW 2016）**；[28] **Défossez 等 Real time SE in the waveform domain（Interspeech 2020）**；[29] Braun & Tashev 数据增广与损失归一化（Speech and Computer 2020）；[30] SI-SDR（Le Roux 等，ICASSP 2019）；[31] **PESQ**（ITU-T P.862，2001）；[32] 神经网络量化白皮书（Nagel 等，arXiv 2106.08295）；[33] **Depth-adaptive transformer**（Elbayad 等，ICLR 2020）。

> [!question] 待核实：引文 [2] GTCRN 的页码与本库其他三篇记录不一致 —— **✅ 已于 2026-09-27 定案**
> **本篇 [2]**（page5 渲染图逐字核对）：
> > X. Rong, T. Sun, X. Zhang, Y. Hu, C. Zhu, and J. Lu, "GTCRN: A speech enhancement model requiring ultralow computational resources," in *Proc. IEEE ICASSP*, 2024, **pp. 10286–10290**.
>
> **本库既有记录**（[[wiki_low_latency/sources/2025/FastEnhancer 2025]] 等页面按 ICASSP 2024 正式卷页引用）：
> > GTCRN（ICASSP 2024），**pp. 971–975**。
>
> **定案（2026-09-27）**：GTCRN 原始 PDF 已由用户提供并补摄（[[wiki_low_latency/sources/2024/GTCRN 2024]]），
> **该 PDF 逐页页脚印刷页码为 p.1→971、p.2→972、p.3→973、p.4→974、p.5→975**，
> 且带版权行 `979-8-3503-4485-1/24/$31.00 ©2024 IEEE` 与 DOI `10.1109/ICASSP48485.2024.10448310`。
> **⇒ 判定 pp. 971–975 正确；本篇 [2] 的 10286–10290 是误著录。**
> 判定依据：**971–975 来自论文自身的一手印刷页码**；10286–10290 来自本篇正文的二手转录（两处页码跨度都是 5 页，因此**不能靠跨度识别**，只能靠一手证据）。
> **本页不静默修正**，原文的 10286–10290 维持原样记录，定案结论并列于此。
