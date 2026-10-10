---
title: Early-Exit-Conv-FSENet
type: entity
created: 2026-09-27
updated: 2026-09-27
tags:
  - speech-enhancement
  - single-channel
  - streaming
  - early-exit
  - dynamic-depth
  - conv-fsenet
  - conv-tasnet
  - one-shot-router
  - knee-target
  - monotonicity-regularization
  - int8-quantization
  - npu-deployment
  - stm32n6
  - neural-art
  - cortex-m55
  - measured-latency
  - macs-not-latency
  - accelerator-launch
  - paper-claimed-causal
  - 32ms-window
  - 16ms-hop
sources:
  - [[wiki_low_latency/sources/2026/Early Exit Compute-Matched 2026]]
related:
  - [[wiki_low_latency/concepts/2609.29867-compute-matched-dynamic-depth]]
  - [[wiki_low_latency/entities/D-GRU]]
  - [[wiki_low_latency/entities/Skip-DPCRN]]
  - [[wiki_low_latency/entities/FastEnhancer]]
  - [[wiki_low_latency/entities/LaCo-SENet]]
  - [[wiki_low_latency/entities/RT-Tango]]
  - [[wiki/entities/Conv-TasNet]]
  - [[wiki_low_latency/concepts/2408.12425-dynamic-gated-rnn]]
  - [[wiki_low_latency/concepts/2207.11108-inference-skipping-parallel-rnn]]
  - [[wiki_low_latency/concepts/2509.21867-speed-optimized-streaming-design]]
  - [[wiki_low_latency/concepts/严格因果与算法延迟]]
  - [[wiki_low_latency/concepts/低时延前端与延迟账本]]
  - [[wiki_low_latency/concepts/低 SNR 人声保留评估]]
---

# Early-Exit-Conv-FSENet

## 定义

**Early-Exit Conv-FSENet** 是本地论文 2609.29867 提出的**逐帧深度可变**的因果语音增强模型。它由三部分组成：

1. **骨干**：**Conv-FSENet**（引 [10][21]，派生自 Conv-TasNet [22]）——pointwise-convolutional frontend + $R$ 个 stack（每 stack 含 **3 个因果膨胀深度可分离时间卷积残差块**，Fig. 2）+ mask heads，在 **causal STFT 域做掩蔽**；
2. **exit ladder**：4 个 mask head 分别挂在 frontend 后与每个 stack 后，使**同一份权重**可以按深度"提前交卷"（head 0 = bypass exit，感受野 **1 帧且无记忆**；head 1/2/3 感受野 **15 / 29 / 43 帧**）；
3. **one-shot router**：一个 **16 单元 GRU**，只读 frontend 输出，在**任何 stack 执行之前**输出分类决策 $k(t)\in\{0,\dots,R\}$，随后**只执行 stacks $1..k(t)$，其余完全跳过**。

本页记录的是**架构实体本身**（含配置、状态语义、实测延迟表与证据边界）。

> [!note] 这个实体是"一份权重、多种角色"的典型
> - **角色 A（动态）**：保留 router，逐帧选深度运行；
> - **角色 B（静态）**：把任意一个 exit 单独抽出来当固定深度模型用（论文称为 **repaired static**）；
> - **角色 C（训练脚手架）**：它的存在让"从一次训练里抽出多个静态模型"成为可能——论文最终认为**这才是它最大的价值**（见 [[wiki_low_latency/sources/2026/Early Exit Compute-Matched 2026]] §4.2、§5）。
>
> 值得与 [[wiki_low_latency/entities/D-GRU]] 对照：那篇同样是"一次训练、多档算力"（共享全部参数，只改每步更新的神经元比例 $P$），但它的动机是**让每步算力恒定**；本篇的动机是**让一次训练产出一族可导出的静态图**。

## 证据

| 属性 | 本地 PDF 证据 |
|---|---|
| 任务 | 单通道 speech enhancement；16 kHz **VoiceBank–DEMAND** [27]；p.3 §3.1 |
| 骨干来源 | 「Conv-FSENet [10, 21], a **causal STFT-domain masking network derived from Conv-TasNet** [22]」；p.2 §2.1 |
| 骨干结构 | 「a **pointwise-convolutional frontend**, $R$ **stacks**, each featuring **3 causal dilated depthwise temporal-convolutional residual blocks** (Fig. 2), and **mask heads**」；p.2 §2.1 |
| 通道维度 | frontend 把 $|X|^{0.3}$ 映到 **$B$-channel** inter-block 表示；每个 block **内部扩展到 $H_i$ 通道**，再投影回 $B$；p.2 §2.1。**$B=128$ 固定在全部配置**；p.3 §3.1 |
| 输入 | 压缩带噪幅度 **$|X|^{0.3}$**（论文写作 $|X|^{0.3}$，是幅度谱的幂律压缩）；p.2 §2.1、p.3 §3.1 |
| 掩蔽 | 每个 head 在**带噪复数 STFT** 上估一个 **sigmoid-activated magnitude mask**；p.2 §2.1 |
| exit 定义 | head 挂在 **frontend 后（bypass exit）** 与 **每个 stack 后**；「exit $i$ evaluates the **frontend plus the first $i$ stacks**」；p.2 §2.1 |
| 感受野 | **1 / 15 / 29 / 43 帧**；「the **bypass exit is memoryless**」；p.2 §2.1 |
| router | 「a **one-shot policy router** ... consists of a **16-unit GRU, feeding on the frontend output**, producing a categorical decision $k(t)\in\{0,\dots,R\}$ **before any TCN stack is executed**」；p.2 §2.1 |
| 跳过的语义 | 「**Only stacks up to $k(t)$ are then evaluated. The remaining stacks are skipped entirely.**」；p.2 §2.1 |
| 算力公式 | $C_{k(t)}=C_{fe}+\sum_{i=1}^{k(t)}C_{stack,i}+C_{head,k(t)}$（Eq. 1）；$C_{fe}\approx FB$、$C_{stack,i}\approx 3H_i(2B+3)$、$C_{head,k(t)}\approx BF$（Eq. 2）；p.2 §2.1 |
| 增强损失 | 功率律压缩谱 MSE（Eq. 3）：$c=0.3$、$\alpha=0.3$，在 **active-speech-level-normalized** 谱上算；引 [8][23]；p.2 §2.2 |
| deep supervision | $\mathcal L_{enh}=\mathcal L_{SE}(\hat S_k,S)+\frac{\lambda_{ds}}{R+1}\sum_{j=0}^{R}\mathcal L_{SE}(\hat S_j,S)$（Eq. 4），$\lambda_{ds}=1$；引 [24][25]；p.2 §2.2 |
| knee target | per-frame 压缩幅度误差 $q_j(t)=\frac{1}{F}\sum_f(| \hat S_j(f,t)|^c-|S(f,t)|^c)^2$（Eq. 5）；$k(t)=\min\{j: q_j(t)\le\min_i q_i(t)+\varepsilon\}$（Eq. 6）；p.2 §2.2。**$\varepsilon$ 的物理含义论文未定义** |
| 路由训练 | cross-entropy 对抗 knee target；**straight-through Gumbel-softmax** [26] 离散化；「either **jointly with the full backbone or on a frozen enhancer**」；p.2 §2.2 |
| 总损失 | $\mathcal L_{tot}=\mathcal L_{enh}+\lambda_{knee}\mathcal L_{CE}+\mathcal L_{cost}$，$\lambda_{knee}=0.1$；$\mathcal L_{cost}$「controls the average routed compute through the **target operating point $\tau$**」（**形式与 $\tau$ 取值均未报告**）；p.2 §2.2 |
| 单调性修复 | **冻结 backbone stacks、frontend 与 policy**，只微调 **exit heads（4×33k 参数）**；$\mathcal L_{mono}=\frac{1}{TR}\sum_t\sum_{j=0}^{R-1}\max(0,q_{j+1}(t)-q_j(t))$（Eq. 7）；**2000 步**、Adam、lr $10^{-4}$、正则权重 **50**；p.2 §2.3 |
| 与 [20] 的区别 | 「Rather than **enforcing monotonicity post hoc**, as **Jazbec et al. [20]** do for **classification**, this term **encourages it through a soft constraint during training**」；p.2 §2.3 |
| 静态基线网格 | $H\in\{32,64,96,256\}$ × $R\in\{1,2,3\}$，$B=128$ 固定 → 12 个模型，跨 **5.7–41.8 MMAC/s**，bracket 全部 routed 点（**6.6–20.2 MMAC/s**）；p.3 §3.1 |
| 训练配方 | Adam，lr $10^{-3}$，weight decay $10^{-5}$，每 epoch 衰减 **0.99**，batch **64**，early stopping；静态模型同配方去 routing 损失；p.3 §3.1 |
| 数据与增广 | 16 kHz VoiceBank–DEMAND；随机裁 **4 s**；**Remix/BandMask/Shift** [28] + 谱增广与电平不变性 [29]；p.3 §3.1 |
| STFT | **512 样本窗、50 % overlap、$F=257$ bins**；p.3 §3.1。**center / 帧锚定未报告** |
| 指标 | **whole-clip SI-SDR** [30] 与 **wideband PESQ** [31]，**全部 824 条**测试片段；dynamic compute = 「the **realized average MMAC/s over the selected exits**」；p.3 §3.1 |
| 部署平台 | **STM32N6570-DK**：Arm **Cortex-M55** 主机（**800 MHz**）+ ST **Neural-ART** NPU（**1 GHz**）；p.4 §4.1 |
| 量化与编译 | ONNX → **post-training int8** [32]（**per-channel scaling + entropy calibration**）→ **ST Edge AI Core v4.0** [6]；p.4 §4.1 |
| host 侧保留 | 「We keep the **STFT, iSTFT and masking on the host (no NPU FFT)**」；p.4 §4.1 |
| 状态导出 | 「export **ring buffers as explicit state tensors**, making each graph a **pure per-frame stateless function**」；p.4 §4.1 |
| 因果性声明 | 「**All networks are causal at a 16 ms hop.**」；p.4 §4.1（**全文唯一的因果性声明**） |
| 动态部署 | **9 张子图**（frontend、router、3×stack、4×exit head）；「different depths **share the same frontend and stack graphs**」→ 整族只占**一条 ladder 的存储**；p.4 §4.3 |
| 量化误差 | repaired family **−0.03 ~ +0.01 PESQ**；量化使 routed 算力偏移**至多 2 %**；p.4 §4.3 |
| 跳过时的状态 | 「**These buffers are updated only when that stack runs**, so when a skipped stack resumes, its state reflects **the most recent frames processed by that stack rather than the most recent input frames**」；部署路径代价 **−0.005±0.011 PESQ / 0.14 dB SI-SDR**（824 条），**routing decisions bit-identical across arms**；p.4 §4.3 |
| 补救方案与结论 | 「**Neither zero-order hold nor propagating the last computed state to deeper stacks [33] recovers the lost quality.**」→ 保持跳过状态不变（导出图的既有行为，**无需改固件**）；p.4 §4.3 |
| router 开销 | **26 µs/frame**（**仅见于 Abstract**，§4.3 只说是"由 800 MHz 下的 measured cycle counts 换算"）；p.1 Abstract |
| 子图切分开销 | **+2.2 % latency overhead**（**仅见于 Abstract**）；p.1 Abstract |
| 参数量 | **只报告 exit heads 的 4×33k**；**全模型参数量未报告**；p.2 §2.3 |

> [!warning] 上表里有两类"只在 Abstract 出现"的数字，引用时须注明
> - **26 µs/frame**（router 开销）与 **+2.2 %**（子图切分开销）在正文 §4.3 都**没有给出**，Abstract 是唯一出处；
> - 它们的**测量条件与基准**也未给出（2.2 % 相对什么？26 µs 含不含派发？）。
> 本库记录为**可引用但口径不明**。

## 架构与状态

~~~text
┌─────────────────────────── Early-Exit Conv-FSENet ───────────────────────────┐
│                                                                              │
│   |X|^0.3 ──►┌──────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐          │
│   (compressed │ frontend │──►│ stack 1 │──►│ stack 2 │──►│ stack 3 │          │
│    magnitude) │ 1×1 conv │   │ dil 1/2/4│  │ dil 1/2/4│  │ dil 1/2/4│         │
│   257 bins    │ 257→128  │   │ 3×res.blk│  │ 3×res.blk│  │ 3×res.blk│         │
│               └────┬─────┘   └────┬────┘   └────┬────┘   └────┬────┘          │
│                    │              │              │              │              │
│                    ▼              ▼              ▼              ▼              │
│               ┌────────┐    ┌────────┐    ┌────────┐    ┌────────┐            │
│               │ head 0 │    │ head 1 │    │ head 2 │    │ head 3 │            │
│               │ bypass │    │ RF  15 │    │ RF  29 │    │ RF  43 │            │
│               │ RF 1,  │    │        │    │        │    │        │            │
│               │ 无记忆 │    │        │    │        │    │        │            │
│               └───┬────┘    └───┬────┘    └───┬────┘    └───┬────┘            │
│                   │             │             │             │                 │
│   每帧选一个 ─────┴─────────────┴─────────────┴─────────────┘                 │
│   k(t) ∈ {0,1,2,3}             ▲                                             │
│        ▲                       │ 派发（host 侧，Cortex-M55）                 │
│        │                       │                                             │
│   ┌────┴───────────────────────┴─────┐                                        │
│   │ one-shot router = GRU(16 units)  │◄── 只读 frontend 输出，                  │
│   │ 在任何 stack 执行【之前】出决策  │    在任何 stack 执行之前                  │
│   └──────────────────────────────────┘                                        │
└──────────────────────────────────────────────────────────────────────────────┘

一个 residual block B_i（Fig. 2）
   x_i ──►┌──────────────┐  ┌───────────────────────┐  ┌──────────────┐
   (B ch) │ expand B→H_i │─►│ causal DW conv, k=3, d│─►│ project H_i→B│──┐
          └──────────────┘  └───────────────────────┘  └──────────────┘  │
              ▲                                                          │
              └──────────────────── 残差加 ─────────────────────────────┘
                                                            ──► y_i (B ch)

算力（Eq. 1–2，论文口径，带 ≈）
   C_k(t) = C_fe + Σ_{i=1..k(t)} C_stack,i + C_head,k(t)
   C_fe ≈ F·B          ← 固定，省不掉
   C_stack,i ≈ 3·H_i·(2B+3)   ← 跳过的 stack 才省得掉
   C_head,k(t) ≈ B·F        ← 固定，省不掉

部署切分（p.4 §4.3，共 9 张子图）
   [frontend] [router] [stack1] [stack2] [stack3] [head0] [head1] [head2] [head3]
        └────────── 不同深度共享同一张 frontend / stack 图 ──────────┘
   → 整族只占【一条 ladder 的存储】，而不是多份独立模型
   → 路由决策 + 派发在 Cortex-M55 上；STFT / iSTFT / masking 也在 host
~~~

> [!note] 架构上最值得记住的一点：**router 的输入是"浅表征"，决策却是"要多深"**
> 一个 one-shot、只读 frontend 输出的 16 单元 GRU，要在**看到任何 stack 之前**判断"这一帧需要多深"。它既不能偷看中间特征，也不能分次决策（否则派发开销会随决策次数上升）。
> 这是一个**信息受限的决策问题**：router 只能依赖 frontend（感受野 1 帧）+ 它自身的跨帧状态。这解释了为什么 knee target 的训练如此关键——**router 的准确度上限由 frontend 表征的信息量决定**，而这一点论文没有分析（见"结果与证据边界"）。

> [!note] "感受野 1 → 15 → 29 → 43" 是本篇最容易被跳过、但对本库最重要的一组数
> - **head 0 无记忆**（论文明确写 "memoryless"），意味着 bypass exit 的输出**只依赖当前帧**（外加 router 的 16 单元状态，但 router 不参与掩蔽）；
> - head 1–3 的感受野**每层增加 14 帧**（15, 29, 43），in 16 ms hop ⇒ **每层增加 224 ms 的历史跨度**。
> - 三个 RSS 的增量**恰好相等**（14/14/14），说明三个 stack 的膨胀结构相同（`dil. 1/2/4`，各 3 个残差块）。
> 本页的最佳读法是**全部为 look-back**（见下方 [!question]），若是这样，则"深度"在本篇里同时意味着**更多的历史上下文**，而不只是"更多算力"——这正是早退能省时间又不掉质量的结构原因。

## 配置速查表（Table 1，10 行，逐格核对 page4 渲染图）

**Table 1 标题**：Analytic MACs do not price graphs on the STM32N6 NPU. Ten complete int8 single-graph measurements (same board and toolchain).

| # | Topology | MMAC/s | ms/frame | µs/MMAC |
|---:|---|---:|---:|---:|
| 1 | H=32, R=1 | 5.73 | 0.640 | 112 |
| 2 | H=64, R=1 | 7.30 | 0.751 | 103 |
| 3 | H=32, R=2 | 7.30 | 1.001 | **137** |
| 4 | H=96, R=1 | 8.86 | 0.852 | 96 |
| 5 | H=64, R=2 | 10.43 | 1.215 | 117 |
| 6 | H=96, R=2 | 13.57 | 1.427 | 105 |
| 7 | H=256, R=1 | 16.70 | 1.364 | **82** |
| 8 | H=96, R=3 | 18.27 | 2.078 | 114 |
| 9 | H=256, R=2 | 29.25 | 2.472 | 85 |
| 10 | H=256, R=3 | 41.79 | 3.584 | 86 |

**论文从表中读出的四条**（p.3 §4.2）：

| # | 主张 | 表内数据核对 |
|---|---|---|
| ① | 每 MMAC 执行时间跨 **1.7×**（82–137） | $137/82 = 1.671$ ✓ |
| ② | 相同名义算力可以有不同运行时 | 第 2 行 vs 第 3 行：**MMAC/s 均为 7.30**，延迟 **0.751 vs 1.001**（差 **0.250 ms**，比值 **1.333**）✓ |
| ③ | MACs 给出错误排序 | 第 4 行 $(H{=}96,R{=}1)$ vs 第 3 行 $(H{=}32,R{=}2)$：MACs **$8.86$ vs $7.30$ = +21.4 %**（论文写 21 %）✓；延迟 **$0.852$ vs $1.001$ = 快 $14.9 \%$**（论文写 15 %）✓ |
| ④ | 深度贵在 accelerator launch，宽度更吃满 NPU | 见下方 [!question]（论文给的 "MACs×8 / 延迟×3.1" 无法由本表复现） |

> [!question] 「$H$ 从 32 增到 256，stack 内 MACs 涨 8×，实测延迟只涨 3.1×」——**3.1× 无法在 Table 1 中定位**
> 本页用 Table 1 逐对试算（**同 $R$ 才可比**）：
>
> | 比较（同 $R$） | $H$ 比 | 全模型 MMAC/s 比 | 实测延迟比 |
> |---|---:|---:|---:|
> | $R=1$：$H{=}256$ vs $H{=}32$ | $8.00$ | $16.70/5.73 = 2.92$ | $1.364/0.640 = 2.13$ |
> | $R=2$：$H{=}256$ vs $H{=}32$ | $8.00$ | $29.25/7.30 = 4.01$ | $2.472/1.001 = 2.47$ |
> | $R=3$：$H{=}256$ vs $H{=}96$ | $2.67$ | $41.79/18.27 = 2.29$ | $3.584/2.078 = 1.72$ |
>
> - 「**MACs 涨 8×**」与论文原话一致（原文说的是 "the **MACs within a stack**"，即**stack 内部通道宽度比** $256/32 = 8$；**不是**全模型 MMAC/s 比——后者在同一 $R$ 下只有 2.9–4.0×，因为 frontend($\approx FB$) 与 head($\approx BF$) 是**固定成本**，会稀释增长率）。
> - **「实测延迟只涨 3.1×」在 Table 1 中找不到任何一对能对上**：最大的同-$R$ 延迟比是 **2.47**（$R=2$）。
> - 论文**未说明** 3.1× 是哪两个拓扑之比，也未说明是否用了 Table 1 之外的数据。
> **本页照录论文原话并标注无法复现，不做代填、也不改写这个数字**。

> [!note] Table 1 的正面资产：本库算力证据等级的**最高档**
> - **真机**：STM32N6570-DK（Neural-ART NPU + Cortex-M55）；
> - **int8**：post-training 量化（per-channel scaling + entropy calibration）；
> - **完整图**：标题写 "Ten complete int8 single-graph measurements"——每行是**一整张可部署的图**，不是单个算子的微基准；
> - **同板同工具链**：同一块板、同一条 ST Edge AI Core v4.0；
> - **量纲**：**ms/frame**（时间），而非 MACs。
>
> 因此本库把它记为**「实测级」算力证据**——高于 [[wiki_low_latency/entities/FastEnhancer]] 的单线程 RTF（吞吐量纲）、远高于 [[wiki_low_latency/entities/D-GRU]] 的解析 MACs。
> **但两条边界必须同时记住**：① 是**平均**而非 p99；② **不含 host 侧 STFT/iSTFT**（见"低时延账本"）。

## 结果表（Table 2，9 行，含两个分组，逐格核对 page4 渲染图）

**Table 2 标题**：Measured STM32N6 latency for representative repaired static and routed models.

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

（渲染图上 `ms/frame` 列的**加粗**值为：`0.930`、`1.668`、`2.684`、`0.751`、`2.762`、`1.364`——即两个分组里各自的**较优 ms/frame**。）

**论文对两个分组的结论**（p.4 §4.4）：

| 分组 | 论文结论 | 表内数据 |
|---|---|---|
| Within a fixed ladder | 「early exit provides a **clear reduction in average execution time**」 | H=64：$1.215 \to 0.930$ ms（**−23.5 %**），PESQ $2.716 \to 2.694$（**−0.022**）；H=256：$2.472 \to 1.668$ ms（**−32.5 %**），PESQ $2.781 \to 2.773$（**−0.008**） |
| Across static and dynamic | 「Several routed points are **matched or dominated** by a different static width/depth choice」；「**it does not create a better latency–quality frontier than architecture-matched statics**」 | Routed H=32：$2.639$ @ $0.769$ ms vs Static H=64,R=1：$2.684$ @ $0.751$ ms → static **更快 0.018 ms 且高 0.045 PESQ**；Routed H=64($\varepsilon{=}5\cdot10^{-4}$)：$2.724$ @ $1.473$ ms vs Static H=256,R=1：$2.762$ @ $1.364$ ms → static **更快 0.109 ms 且高 0.038 PESQ** |

> [!question] 跨拓扑分组**漏了一组本可直接对照的数据**，而且漏掉的这一组**不利于 "dominated" 的措辞**
> Table 2 第一分组里有 **`Static H=64, R=2`：10.4 MMAC/s / 2.716 PESQ / 1.215 ms**；第二分组里有 **`Routed H=96`：10.51 MMAC/s / 2.683 PESQ / 1.040 ms**。两者算力**几乎相同**（10.4 vs 10.51），但分属两个分组，**论文没有并列它们**。
> 若并列：**static 高 0.033 PESQ 但慢 0.175 ms/frame** —— 这是一个**真实的 trade-off（matched 对价）**，**不是支配关系**。
> 论文在同一段只用"**similarly**"带过了 routed H=96（「routed H=96 **similarly** reaches 2.683 at 1.040 ms」），**没有与表内已有行对照**。本页认为这处遗漏**弱化了论文 "matched or dominated" 中 "dominated" 的分量**——在这一点上更准确的说法是"**静态与动态各有胜负**"。此为本页从渲染图对照后读出，**论文自身未讨论**。

> [!question] `ε` 与 `asym4` 两个记号的含义**全文未定义**
> - **$\varepsilon$**：在 §2.2 是 knee target 的容差（Eq. 6 的「within $\varepsilon$ of the best achieved by any exit」），**论文没有解释它的物理含义或量纲**；在 Table 2 里又以 `ε=2·10⁻³` 与 `ε=5·10⁻⁴` 两档出现，**是否与 §2.2 的同一个 $\varepsilon$ 论文未澄清**。
> - **`asym4`**：只出现在 §4.4 的一句「**routed H=64 with asym4** reaches 2.724 at 1.473 ms」，**全文（含 References）再无第二次出现，也无任何定义**。
>   本页核对渲染图后确认：该句**只能对应 Table 2 的 `Routed H=64 / ε=5·10⁻⁴ / 12.29 / 2.724 / 1.473` 这一行**（表中唯有此行的 PESQ 为 2.724、ms/frame 为 1.473）。**但 `asym4` 到底指什么，本页不做任何猜测**
>   （"asymmetric"？某档 $\varepsilon$ 的内部代号？某个配置的简称？）。记录为**未定义**。

## 状态与因果性

| 审计项 | 证据 | 本库判定 |
|---|---|---|
| 采样率 | 16 kHz（p.3 §3.1） | 明确 |
| FFT / 窗长 / hop | **512 样本窗、50 % overlap、$F=257$ bins**（p.3 §3.1） | 明确。窗长 512 samples = **32 ms** @16 kHz（本页换算，论文未直接给）；hop = 256 samples = **16 ms**（与论文反复使用的 "16 ms hop" 自洽）；$F=257=512/2+1$ |
| **STFT center / 帧锚定** | **完全未报告** | `unreported`：若 `center=True`，每帧分析窗相对帧锚点向前后各取 $W/2$，**前端含 16 ms 未来样本**，系统算法延迟直接加 16 ms；若左对齐则不含。**论文对此完全沉默** |
| 因果性（论文声明） | 「**All networks are causal at a 16 ms hop.**」（p.4 §4.1）——**全文唯一一句** | `paper-claimed-causal`：**声明级，无逐层 certificate** |
| 逐层 padding / state certificate | **未给出**。论文只给了结构描述（"causal dilated depthwise temporal-convolutional residual blocks"）与状态导出方式 | `unreported` |
| 感受野的方向性 | 论文给 **1 / 15 / 29 / 43 帧**，但**只给数值不给方向** | `unreported`：**本页按全部为 look-back 读**（见下方 [!question]），但这不是论文的明述 |
| 状态语义（正常运行时） | 每个 stack 维护自己的 **ring buffer** 供膨胀卷积用；head 0 **memoryless** | 状态**跨帧存续**；head 0 无状态 |
| **状态语义（跳过时）** | 「These buffers are **updated only when that stack runs**, so when a skipped stack resumes, its state reflects **the most recent frames processed by that stack rather than the most recent input frames**」（p.4 §4.3） | **本篇对因果性的最强结构性保证**：任何输出**只依赖该 stack 真正处理过的帧** ⇒ **不可能引入未来依赖**。但论文**未把它写成因果性论证** |
| 状态导出的工程形式 | 「export **ring buffers as explicit state tensors**, making each graph a **pure per-frame stateless function**」（p.4 §4.1） | 可静态编译、可 int8、可上 NPU 的前提（见概念页命题 ⑤） |
| 补救方案 | **零阶保持**与**把最后计算的状态传播给更深 stack** [33] **都不能恢复**丢失的质量（p.4 §4.3） | **只有定性陈述，无数据**（未报告两种方案各自的 PESQ/SI-SDR） |
| router 的状态 | **16 单元 GRU**，跨帧维护隐状态；§1 的 Fig. 4 实验里"the faded first repeat **warms the GRU** and is discarded"（p.4 Fig. 4 caption） | router **有状态**，且需要 warm-up（**论文只在 Fig. 4 的实验里体现了这一点，未给 warm-up 时长**） |
| 决策一致性 | 「routing decisions **bit-identical across arms**」（p.4 §4.3） | 部署路径与离线参考路径的**决策序列完全相同** → §4.3 的 −0.005 PESQ 是**干净的单变量对照** |
| 算力 | 名义 MMAC/s（Table 1/2 第三列）+ 真机 ms/frame（第四列） | **实测级**（本库最高）；但为**平均**而非 p99 |

**判定结论**：记为本库的 **`paper-claimed-causal`**。理由：

1. 论文**只有一句集合声明**（"All networks are causal at a 16 ms hop"），
2. **没有任何逐层 padding / state certificate**，
3. **STFT 的 center 与否未报告**——这是决定"前端是否含 16 ms 未来样本"的关键参数，
4. **感受野 1/15/29/43 帧的方向性未说明**。

> [!note] 但它有一个别的论文没有的结构性保证，这一点应当单独记账
> 因为**被跳过的 stack 的状态不更新**（p.4 §4.3），所以系统的任何输出都只能依赖"该 stack 最近真正处理过的帧"。这是一个**比"我们用了因果卷积"强得多**的保证：即使某个 stack 内部的卷积是非因果的（论文没这么说，但也没排除），**跳过机制本身也不会引入未来依赖**。
> **本页因此把本篇记为"声明级因果 + 跳过机制的结构性保证"。** 这**不足以**升级为 `strict_causal`（center 未报告是硬缺口），但它是本库见过的、对"动态执行下的因果性"最清晰的一次工程交代。

> [!question] 感受野 1/15/29/43 的推导：本页给出一个自洽的读法，但**论文没有给推导**
> 三个 stack 都是 `dil. 1/2/4`（Fig. 1 标注）、每 stack **3 个**残差块（Fig. 2 的 `causal DW conv, k=3, d`）。若全部为**因果（左对齐）卷积**：
> $$\text{每 stack 新增的历史帧} = \sum_{d\in\{1,2,4\}}(k-1)\cdot d = 2 \times (1+2+4) = 14 \text{ 帧}$$
> 从 head 0 的 **1 帧**起，依次 1 → 15 → 29 → 43，**步长恰好 14**。**这与论文给出的四个数完全吻合。**
> **但这个式子是本页的推读。** 论文**既没有给推导，也没有说明感受野是单向还是双向**。若其中含未来成分（例如膨胀卷积对中间帧做了对称 padding），则**最深 head 会带来最多的 look-ahead**，本篇的因果性判定需要降级。本页把它列为**需主 agent 或后续读者回原文/复现代码复核的点**。

## 低时延账本

| 字段 | 本篇证据 / 边界 |
|---|---|
| 采样率 | **16 kHz**（p.3 §3.1） |
| Nfft / 窗长 | **512 样本窗 = 32 ms** @16 kHz（窗长由论文给出，ms 换算为本页推得） |
| hop | **256 samples = 16 ms**（50 % overlap；论文反复以 "16 ms hop" 为准） |
| 频率点数 | **$F=257$ bins**（$=512/2+1$，含直流与 Nyquist） |
| **STFT center / 帧锚定 / padding** | **未报告**（本库一等审计项；若 `center=True` 则前端含 **16 ms** 未来样本） |
| look-ahead / group delay | **未报告** |
| 感受野 | **1 / 15 / 29 / 43 帧**（head 0–3）；**方向性未说明**；head 0 **memoryless** |
| 算法延迟（论文口径） | **未报告**——论文**没有给出任何算法延迟数值，也没有定义其口径**（无 window−hop、无 $W/2$、无推导式） |
| 每帧执行时间（**实测**） | **Table 1**：10 个静态拓扑，**0.640–3.584 ms/frame**；**Table 2**：9 个部署模型，**0.751–2.472 ms/frame**（repaired static）/ **0.769–1.668 ms/frame**（routed） |
| 每 MMAC 执行时间 | **82–137 µs/MMAC**（跨 1.7×；Table 1 第四列） |
| **是否端到端** | **否**。STFT / iSTFT / masking 保留在 host（p.4 §4.1），**这三部分的耗时未出现在 Table 1/2 的任何一行** |
| 是平均值还是分位数 | **平均**（p.4 §4.3 原文 "measured **per-frame mean** latency"）；**p50 / p95 / p99 全部未报告** |
| deadline miss / underrun / overrun | **全部未报告**。最慢实测 3.584 ms/frame 相对 16 ms hop **看似有余量**，但这是平均值，且论文**从未把两者并列讨论** |
| 计算平台 | **STM32N6570-DK**：Arm **Cortex-M55**（**800 MHz**）+ ST **Neural-ART** NPU（**1 GHz**）（p.4 §4.1） |
| 量化 | **int8**，post-training（per-channel scaling + entropy calibration）[32] |
| 编译链 | **ST Edge AI Core v4.0** [6]，含 operator rewrites |
| 量化对质量的影响 | repaired family **−0.03 ~ +0.01 PESQ**（p.4 §4.3） |
| 量化对算力的影响 | routed compute 偏移**至多 2 %**（p.4 §4.3） |
| router 自身开销 | **26 µs/frame**（**仅见于 Abstract**；§4.3 说由 800 MHz 下 measured cycle counts 换算） |
| 子图切分开销 | **+2.2 % latency overhead**（**仅见于 Abstract**） |
| 部署路径 vs 离线路径 | **−0.005±0.011 PESQ / 0.14 dB SI-SDR**（824 条片段）；**routing decisions bit-identical**（p.4 §4.3） |
| 峰值内存 / SRAM | **未报告**（只说 "compiler reports provide ... memory requirements"，**数值未给**） |
| 功耗 | **未报告**（论文的动机是 "shared battery budget"，但无任何功耗数据） |
| 长流稳定性 / state reset / warm-up | **未报告**。唯一相关线索：Fig. 4 的实验把第一次重复用于 "**warms the GRU**" 并丢弃（p.4 Fig. 4 caption）——**暗示 router 有 warm-up 需求，但时长未给** |
| batch=1 / chunk 大小 | **未报告**（但"纯逐帧无状态函数"+ per-frame ms/frame 强烈暗示 batch=1 逐帧） |
| 全模型参数量 | **未报告**（只有 exit heads 的 4×33k） |

**实体判定**：**`paper-claimed-causal`（仅一句集合声明，无逐层 certificate，STFT center 未报告）/ 算力为【真机 int8 实测 ms/frame】（本库最高证据级）/ 延迟账本厚但缺 p99 与端到端 / 人声保留仅 SI-SDR + PESQ。**

> [!warning] 这个实体在本库的特殊性：**账本最厚，但"厚"的地方不是"久经审计"的地方**
> 本库其他论文（[[wiki_low_latency/entities/D-GRU]] 延迟账本为空、[[wiki_low_latency/entities/FastEnhancer]] 只有 RTF 无真机）缺失的是**基本功**；本篇**基本功很足**（真机、int8、µs/MMAC、量化误差、bit-identical、跳过语义），但它缺的是**另一组**东西：
> - **p99 / 最坏帧**（只有平均）；
> - **端到端**（不含 host 侧 STFT/iSTFT）；
> - **算法延迟的明确定义**（论文根本没有这个概念，只有 "16 ms hop"）；
> - **功耗与内存数值**（只有"编译器报告里有"这句话）。
>
> 因此**不能**因为 Table 1 很硬就把它读成"延迟已被完整刻画"。它刻画的是**NPU 图上 per-frame 的平均执行时间**——这是一块**很大但边界明确**的拼图。

## 结果与证据边界

- **支持**：
  - **算力对齐后，逐帧路由不提高质量上限**：mono-repaired 前沿与 routed 前沿在共同区间上 **PESQ 差 < 0.01**（三个具体点 8.48 / 12.18 / 20.22 MMAC/s 上为 **+0.009 / −0.001 / +0.007**）；
  - **早退训练确实产出更好的静态模型**：相对从零训练的专用静态前沿，routed H=64 在 **8.48 MMAC/s 达 PESQ 2.719**，而同算力静态前沿约 **2.60**；同一训练预算下修复带来 **0.04–0.11 PESQ**；**少 30 % 算力可匹配最好 PESQ（代价 1.0 dB SI-SDR）**；
  - **固定 ladder 内早退确实省时间**（真机实测）：H=64 **1.215 → 0.930 ms/frame**（PESQ 2.716 → 2.694）；H=256 **2.472 → 1.668 ms/frame**（PESQ 2.781 → 2.773）；
  - **名义 MACs 不能预测真机速度**：**82–137 µs/MMAC（1.7×）**；$(H{=}32,R{=}2)$ 与 $(H{=}64,R{=}1)$ **MACs 与参数量完全相同**却 **1.001 vs 0.751 ms/frame**；$(H{=}96,R{=}1)$ **MACs 多 21 %** 却**快 15 %**；
  - **量化很稳**：repaired family 只变 **−0.03 ~ +0.01 PESQ**，routed 算力偏移 **≤2 %**；
  - **跳过的语义被诚实处理**：跳过时状态不更新，与离线路径 **bit-identical**，代价 **−0.005±0.011 PESQ**；
  - **router 的算力开销很小**：**26 µs/frame**（Abstract）。
- **不支持**：
  - 约 2 ms 级系统已达成（hop 就是 **16 ms**，比目标高一个量级；论文也未声称）；
  - 动态部署能造出比"架构对齐的静态模型"更好的延迟–质量前沿（论文明确否认：「it does not create a better latency–quality frontier than architecture-matched statics」）；
  - `strict_causal`（**STFT center 未报告、逐层 padding 未给、感受野方向性未说明**）；
  - 实时 deadline 已通过（**只有平均 ms/frame，无 p99、无 deadline miss、无 underrun**）；
  - 端到端延迟已知（**不含 host 侧 STFT/iSTFT**）；
  - 低 SNR 下的人声保留已证明（**只有 SI-SDR + PESQ 两个整句指标**）；
  - 单调性修复已使整条 ladder 单调（**只微调 4×33k 参数的 heads，未报告残余违反率或收敛曲线**）。
- **未报告**：STFT center/帧锚定、逐层 padding certificate、look-ahead、group delay、编译期静态算法延迟、**p50/p95/p99**、deadline miss、underrun/overrun、峰值 RAM/SRAM、**功耗**、host 侧 STFT/iSTFT 耗时、长流稳定性、state reset、warm-up 时长、**全模型参数量**、$\mathcal L_{cost}$ 的具体形式与 $\tau$、$\varepsilon$ 的物理含义、`asym4` 的定义、$H_i$ 与 $H$ 的关系、三对 width–depth 精确对照的具体配置、训练总步数、**随机种子与 seed spread**、DNSMOS **SIG/BAK/OVL**、ASR WER、负 SNR 分层（−10/−5/0/5 dB）、噪声类型分层、babble/竞争说话人、false-suppression、SPP/VAD 校准、F0/formant/prosody、voiced energy、听感 MOS。
- **可比性提醒**：
  - Table 1 的 10 行都是**同板同工具链的 int8 完整单图**，**列内可横比**；但它们**不含 STFT/iSTFT**，因此**不能**与含前端的端到端测量（如 [[wiki_low_latency/entities/FastEnhancer]] 的 RTF、[[wiki_low_latency/entities/LaCo-SENet]] 的算法时延）直接比较；
  - Table 2 的 **MMAC/s 列是"实际选中的 exit 的平均值"**（routed 行）或**固定值**（static 行），**这两者口径不同**——routed 的 MMAC/s 是**输入相关的实测平均**，static 的是**设计常数**；
  - Table 2 的 int8 PESQ 是**部署后**的数值，与 §4.2 的 float32 前沿（Fig. 3）**不是同一批数字**（例如 routed H=64 在 float32 下是 2.719 @ 8.48 MMAC/s，在 Table 2 的 int8 下是 2.694 @ 8.58 MMAC/s——**MMAC/s 也略变**，因为量化改变了路由选择）。
- **数字口径警示**：
  - **`µ`/`ms` 前的多余逗号是原文的**（`0.640, ms`、`137, µs/MMAC`），**不是抽取错误**（渲染图已核）；
  - **ms/frame 是平均，不是 p99**；
  - **ms/frame 不含 STFT/iSTFT**；
  - 「$H$ 32→256：MACs ×8 / 延迟 ×3.1」中的 **×8 是 stack 内通道比**（论文原文口径），**×3.1 无法由 Table 1 复现**。

## 交叉链接

- 源论文：[[wiki_low_latency/sources/2026/Early Exit Compute-Matched 2026]]
- 概念展开：[[wiki_low_latency/concepts/2609.29867-compute-matched-dynamic-depth]]
- 同谱系（推理期动态算力）：
  - [[wiki_low_latency/entities/D-GRU]]、[[wiki_low_latency/sources/2024/D-GRU 2024]]、[[wiki_low_latency/concepts/2408.12425-dynamic-gated-rnn]]
  - [[wiki_low_latency/entities/Skip-DPCRN]]、[[wiki_low_latency/sources/2022/Skip-DPCRN 2022]]、[[wiki_low_latency/concepts/2207.11108-inference-skipping-parallel-rnn]]
- 同命题不同机理（MACs ≠ 速度）：[[wiki_low_latency/entities/FastEnhancer]]、[[wiki_low_latency/sources/2025/FastEnhancer 2025]]、[[wiki_low_latency/concepts/2509.21867-speed-optimized-streaming-design]]
- 最严因果尺子：[[wiki_low_latency/entities/LaCo-SENet]]、[[wiki_low_latency/sources/2026/LaCo-SENet 2026]]、[[wiki_low_latency/concepts/2606.19688-latency-configurable-asymmetric-padding]]
- 低时延前端账本：[[wiki_low_latency/concepts/低时延前端与延迟账本]]、[[wiki_low_latency/entities/STFT-Very-Low-Latency-SE]]、[[wiki_low_latency/sources/2022/STFT-Domain Very Low Algorithmic Latency 2022]]、[[wiki_low_latency/concepts/2204.09911-short-asymmetric-stft]]
- 帧级稀疏的另一实现：[[wiki_low_latency/entities/RT-Tango]]、[[wiki_low_latency/sources/2026/RT-Tango 2026]]
- 骨干家族：[[wiki/entities/Conv-TasNet]]、[[wiki_low_latency/entities/DPCRN]]、[[wiki_low_latency/concepts/2107.05429-dual-path-recurrent-context]]
- 因果与延迟口径：[[wiki_low_latency/concepts/严格因果与算法延迟]]
- 人声保留缺口：[[wiki_low_latency/concepts/低 SNR 人声保留评估]]

> [!question] 待验证
> **(1) STFT center 未报告**——这是本实体**最关键的未验证项**。若 `center=True`，前端含 16 ms 未来样本，整篇的因果性判定需要下调；若左对齐则结论成立。论文全文对此沉默。
> **(2) 感受野 1/15/29/43 的方向性未说明**。本页给出一个自洽的 look-back 推导（每 stack 新增 14 帧 = $2\times(1+2+4)$），但**这只是推读**；若含未来成分，最深的 head 3 会有最大的 look-ahead。
> **(3)「$H$ 32→256 的延迟只涨 3.1×」无法由 Table 1 复现**（同-$R$ 最大比值为 2.47）。请复核这是否来自 Table 1 之外的测量、或是否涉及跨 $R$ 的某种比较。
> **(4) `ε` 与 `asym4` 的含义全文未定义**。$\varepsilon$ 在 §2.2 与 Table 2 中是否为同一个量未澄清；`asym4` 只在 §4.4 出现一次。
> **(5) 贡献列表承诺的 "seed spreads" 在正文中没有兑现**——而本篇的核心结论依赖 0.01–0.05 PESQ 量级的差值（+0.009 / −0.001 / +0.007），种子波动是否覆盖这些差值**无法判断**。
> **(6) 单调性修复只用 4×33k 参数的 heads 微调**，且**未报告残余违反率或收敛曲线**——repair 成功只证明了"在冻结特征下可以把更深变得更不差"，未证明"这条 ladder 本质单调"。
> **(7) 零阶保持 / 状态传播两种补救方案"都不能恢复质量"只有定性陈述，无数值**——这是一个可直接补做的小实验。
> **(8) Abstract 的 "26 µs per frame" 与 "+2.2 % latency overhead" 在正文中没有完整语境**（基准、是否含派发均未说明）。
