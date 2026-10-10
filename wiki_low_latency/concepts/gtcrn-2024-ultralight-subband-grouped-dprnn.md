---
title: gtcrn-2024 - 超轻量子带分组 DPRNN 的五条可复用命题
type: concept
created: 2026-09-27
updated: 2026-09-27
tags:
  - ultralight
  - subband
  - erb-filterbank
  - band-merging
  - grouped-rnn
  - grouped-dprnn
  - grouped-temporal-convolution
  - shufflenet
  - subband-feature-extraction
  - temporal-recurrent-attention
  - parameter-accounting
  - nominal-macs
  - macs-not-latency
  - paper-claimed-causal
  - unreported-center
  - latency-ledger
  - human-voice-preservation
  - sig-bak-tradeoff
  - baseline-provenance
  - anchor-value-audit
  - ablation-interpretation
sources:
  - [[wiki_low_latency/sources/2024/GTCRN 2024]]
related:
  - [[wiki_low_latency/entities/GTCRN]]
  - [[wiki_low_latency/concepts/2509.21867-speed-optimized-streaming-design]]
  - [[wiki_low_latency/concepts/2609.29867-compute-matched-dynamic-depth]]
  - [[wiki_low_latency/concepts/2207.11108-inference-skipping-parallel-rnn]]
  - [[wiki_low_latency/concepts/2408.12425-dynamic-gated-rnn]]
  - [[wiki_low_latency/concepts/2304.08707-full-sub-band-modeling]]
  - [[wiki_low_latency/concepts/2107.05429-dual-path-recurrent-context]]
  - [[wiki_low_latency/concepts/严格因果与算法延迟]]
  - [[wiki_low_latency/concepts/低时延前端与延迟账本]]
  - [[wiki_low_latency/concepts/低 SNR 人声保留评估]]
  - [[wiki_low_latency/entities/FastEnhancer]]
  - [[wiki_low_latency/entities/PSMSE]]
  - [[wiki_low_latency/entities/RT-Tango]]
  - [[wiki_low_latency/entities/DPCRN]]
  - [[wiki_low_latency/entities/LaCo-SENet]]
  - [[wiki_low_latency/entities/Early-Exit-Conv-FSENet]]
  - [[wiki/sources/2026/muNet 2026]]
---

# gtcrn-2024 - 超轻量子带分组 DPRNN 的五条可复用命题

## 定义

本页从 [[wiki_low_latency/sources/2024/GTCRN 2024]]（ICASSP 2024，pp. 971–975，**23.7 K 参数 / 39.6 MMACs per second**）抽象出**五条可复用的判断规则**。它们不关心 GTCRN 的性能数字本身，而关心**"超轻量"这个档位该怎么记、怎么读、怎么用**。

本页的核心命题是：

> **GTCRN 是本库"超轻量"纵轴的锚点，而它的锚定方式有三个结构性弱点：① 参数量有三套互不相容的库内口径；② 它引用了"MACs 不是速度"的出处（ShuffleNetV2）却全文不报速度；③ 它的因果性是一句声明，而声明只覆盖了七项审计中的一项。**

五条命题：

| # | 命题 | 一句话 |
|---|---|---|
| ① | **锚点数值必须先钉口径** | 被四篇同时引用的锚点，其参数量/算力口径不统一时，四条引用链一起偏 |
| ② | **"分组"是三条正交的压缩轴** | 频带 / 通道 / 循环层三处分组互不重叠，可分别开关与分别审计 |
| ③ | **补偿模块必须用"双坐标"比较** | TRA 的 MACs 代价是 SFE 的 1/9，参数代价是 SFE 的 4.1 倍——单向排序会给出错误结论 |
| ④ | **引用 ShuffleNetV2 的架构论文，尤其应当报告速度** | 这是本库第一条"引用即负有义务"的审计规则 |
| ⑤ | **声明级因果需要一张七项清单来定位缺口在哪** | "用了单向 GRU"只覆盖七项中的一项，其余六项要逐项标"未报告" |

## 命题 ①：被引为锚点的模型，其参数/算力口径必须先钉死

**本库的现实**：GTCRN 被**四篇**同时引用为"超轻量"的参照点：

| 引用者 | 记录值 | 口径 |
|---|---|---|
| [[wiki_low_latency/entities/FastEnhancer]] | **24 K / 40 M MACs**（GTCRN<sup>a</sup>，脚注 `Evaluated using the official checkpoint`） | 四舍五入 + 官方 checkpoint |
| [[wiki/sources/2026/muNet 2026]] | **48 K / 33 MMACs** | **与原文差异最大** |
| [[wiki_low_latency/entities/PSMSE]] | **23.7 K**（区间 `23.7K–79K`） | 直接引用原文 |
| [[wiki_low_latency/entities/RT-Tango]] | 借其 ERB 压缩；记 **48.98 / 197.5 MMAC/s**（16 ms / 4 ms） | **分布式重配口径**，非原文 |

**GTCRN 原文自己的声称**（Abstract、§3.2、§4 三处一致）：**23.7 K 参数 / 39.6 MMACs per second**，且**与 Table 1 末行内部自洽**（23.67 K / 39.63 M/s）。

> [!contradiction] **48 K / 33 无法与原文调和，两条链路一起偏**
> - 参数：**48 K vs 23.7 K** ≈ **2.03×**；MACs：**33 vs 39.6** ≈ **0.83×**——**方向相反**，不可能来自同一模型的同一配置；
> - **高度吻合的线索**：μNet 的 48 K / 33 与"官方 repo 更新后的 **48.2 K / 33.0 MMACs**"几乎完全一致 ⇒ **强烈提示 μNet 引的是官方 repo 的实测值**，而论文的 23.7 K / 39.6 是**设计声称值**；
> - 本页**无法独立核实**（`evidence_policy: local_pdf_only`，无网络、未克隆 repo）。
>
> **可能的解释（均未验证）**：
> | 假设 | 支持 | 反对 |
> |---|---|---|
> | A. 官方实现含论文未计入的参数（BN affine、GRU bias、TRA 的 FC） | 23.7 K 恰等于 Table 1 表内值，**像"按设计算"而非 `sum(p.numel())`** | 2 倍差距偏大 |
> | B. repo 默认配置与论文不同 | —— | MACs 反降说明计算结构变了，与参数翻倍矛盾 |
> | C. MACs 口径不同（per-second vs per-frame；是否含 STFT；hop 假设） | `MMACs per second` 是**时间归一化量**，与 hop 直接相关 | —— |
> | D. μNet 数字另有来源错误 | —— | 48.2/33.0 的高度吻合降低了这个可能 |

**命题形式**：

> **当一个模型被库内多篇引用为锚点时，本库必须先为它建立一张"口径表"**：谁的数是论文声称值、谁的是官方实现实测值、谁的是第三方复现值、谁的是重配口径。**四种口径不可混用于同一条比较轴上。**

**本库的行动规则**（本页建议）：

| 规则 | 做法 |
|---|---|
| **R1 主记录以一手证据为准** | 有本地 PDF 时，**以论文声称值为主记录**，因为它是可核查的一手证据 |
| **R2 并列而非采信** | 差异无法用例差解释时，在 entity 页 `[!contradiction]` **并列全部口径**，不单方面采信 |
| **R3 标注差异方向** | 参数与 MACs 的差异**方向相反**时，说明不是同一配置，**不可用"用四舍五入解释"** |
| **R4 外部转述单列** | μNet 的"GTCRN 需缓冲最多 16 帧中间特征"**不见于 GTCRN 原文**，必须标注为外部转述 |
| **R5 目标：核查代码** | 有网络条件时**优先核查官方 repo 的 `model.py` 与 README**，而不是继续在论文间转述 |

> [!note] 这条命题与本库"超轻量"档的**全部记录**有关
> [[wiki_low_latency/entities/FastEnhancer]]、[[wiki_low_latency/entities/PSMSE]]、[[wiki/sources/2026/muNet 2026]] 都把自己定位在 GTCRN 的附近（更快 / 更大 / 更小），**它们的"相对位置"全部由 GTCRN 的数值决定**。
> 因此 GTCRN 的口径不统一，**不是一个孤立的记录瑕疵，而是这一整个档位的地基问题**。

## 命题 ②："分组"是三条正交的压缩轴——可分别开关、分别审计

GTCRN 把"分组"用在**三个互不重叠**的地方：

| # | 分组轴 | 具体形式 | 组数 / 压缩比 | 可开关？ |
|---|---|---|---|---|
| 1 | **频带** | BM/BS 按 **ERB 尺度**压缩 **2 kHz 以上**的频带 | 192 → 64（低频 65 带保留，总 **129** 维） | 结构必经路径 |
| 2 | **通道** | GT-Conv 的 **ShuffleNetV2 unit**（channel split → 两路 → concat → channel shuffle） | 2 路 | 结构常数 |
| 3 | **循环层** | **G-DPRNN** 的 GRNN 分组（输入与隐状态各切 2 组） | **2** | 结构常数 |
| 4 | **补偿模块** | **SFE**（频率轴 unfold 把子带关系搬进 channel 维）与 **TRA**（时间轴能量重标定） | — | **Table 1 的两个开关** |

**关键观察**：论文原文把 **1 与 2/3 的作用分开表述**——

> 「An **ERB filter bank is used to reduce the redundancy of the input features**. **Grouped convolution [17] and grouped RNN [18] are employed to decrease the model complexity.**」（p.1 §1）

**即：ERB 压的是"特征冗余"，通道/循环分组压的是"模型复杂度"——这是两个不同的会计科目。**

> [!important] 三条轴的正交性带来一个可复用的审计动作：**分轴归因**
> 因为三条轴的作用对象不同（频带维 / channel 维 / 循环层），**它们对参数量、MACs、表示的贡献可以被分轴记账**：
>
> | 轴 | 影响参数量 | 影响 MACs | 影响"频率信息如何被利用" |
> |---|---|---|---|
> | 频带（ERB） | 间接（输入维 257 → 129） | **直接**（所有后续层的输入宽度减半） | 压缩掉高频冗余，保留低频谐波 |
> | 通道（Shuffle） | 直接 | 直接 | — |
> | 循环（GRNN） | 直接（每组参数少 2 倍） | 直接 | — |
> | SFE | **+2.02 K**（Table 1 差值） | **+5.16 M/s** | **把子带关系搬进 channel 维** |
> | TRA | **+8.30 K**（Table 1 差值，归属未报告） | **+0.56 M/s** | **让掩蔽跨帧有记忆** |
>
> **这张表的意义**：当你要把 GTCRN 的某个想法搬到别的模型上时，**你可以只搬一条轴**——这也是 [[wiki_low_latency/entities/RT-Tango]] 实际做的事：它**只借用了第 1 条轴（ERB 压缩）**，其余全部换掉。
> **一个有意思的读法**：GTCRN 最有生命力的部分**不是 G-DPRNN 也不是 GT-Conv，而是那个频带映射表**——因为它足够简单、足够正交，可以被搬到任何时频域模型上。本页建议把 **"ERB 频带压缩"作为一个独立可复用算子**在库内建页（若尚无）。

> [!question] 但正交性有一个**未报告的边界**：三条轴的分界是否在实现上真的干净？
> - **频带轴**：论文未说明 **2 kHz 对应第几个 bin**（本页推得 @16 kHz / FFT 512 时 ≈ bin 64，与 65 个低频带高度接近——**但这是本页算术，论文未给对应关系**）；也未说明 BM 的输入是否就是完整单边谱 257 维（**65 + 192 = 257 是自洽的**，但论文从未写出 257）；
> - **循环轴**：**intra 与 inter 的切分边界（DPRNN chunk 长度）未报告**——若 chunk 长度不等于 1 帧，则"intra-frame 是单帧内"这个前提就需要重新检查（见命题 ⑤）；
> - **通道轴**：GT-Conv 的三处 dilation 为 **1 / 2 / 5**（kernel (3,3)、通道 16），但**时间感受野论文未给**（本页推得 3 / 5 / 11 帧、单链累计 17 帧）。

## 命题 ③：补偿模块的性价比**必须用"双坐标"比较**，单向排序会给出错误结论

![[wiki_low_latency/assets/gtcrn_2024/gtcrn-page4.png]]

> 图注：原论文第 4 页页面渲染，本页用它核对 **Table 1（7 行 × 8 列消融）** 与 **Table 3（DNS3 blind）**。**Table 1** 标题 "Ablation study results on DNS3 test set."，列为 `SFE / TA / TRA / Para.(K) / MACs(M/s) / SISNR / PESQ / STOI`；**渲染图上 7 行被 2 条横向分隔线分成 3 段**（第 1 行独立、第 2–4 行一段、第 5–7 行一段），与 SFE 列的 `✗✗✗/✓✓✓` 分组吻合；勾选标记 `✓/✗` 在文本抽取中列归属易错，**必须看渲染图**。**Table 3** 的表头是双层（`DNSMOS-P.808` 单列 + `DNSMOS-P.835` 下挂 `BAK / SIG / OVRL`），文本抽取把三个子列平铺，**列归属也只能看渲染图**。图片为 PDF 页面复制，不是 AI 重画。

**Table 1 提供了本库难得的一组"同一 baseline 上两个可选模块"的干净对照**（DNS3 约 100 小时子集）：

| 模块 | Para. (K) | MACs (M/s) | SISNR | PESQ | STOI |
|---|---|---|---|---|---|
| baseline（✗/✗/✗） | 13.35 | 33.91 | 9.87 | 1.87 | 0.834 |
| **+ SFE**（✓/✗/✗） | 15.37 | 39.07 | 10.10 | 1.90 | 0.838 |
| **+ TRA**（✗/✗/✓） | 21.65 | 34.47 | 10.25 | 1.91 | 0.840 |
| **+ 两者**（✓/✗/✓） | 23.67 | 39.63 | **10.39** | **1.94** | **0.844** |

**双坐标并列（本页从渲染图重算，论文未提供）**：

| 模块 | MACs 增量 | 参数增量 | SISNR 增量 | PESQ 增量 |
|---|---:|---:|---:|---:|
| **TRA** | 33.91 → 34.47 = **+0.56 M/s** | 13.35 → 21.65 = **+8.30 K** | 9.87 → 10.25 = **+0.38** | 1.87 → 1.91 = **+0.04** |
| **SFE** | 33.91 → 39.07 = **+5.16 M/s** | 13.35 → 15.37 = **+2.02 K** | 9.87 → 10.10 = **+0.23** | 1.87 → 1.90 = **+0.03** |

> [!important] **这是一个双向 trade-off，不是单向优劣**
> - **MACs 方向**：TRA `+0.56` vs SFE `+5.16`（比值 **9.2**）⇒ TRA 便宜一个数量级；
> - **参数方向**：TRA `+8.30` vs SFE `+2.02`（比值 **4.1**）⇒ **SFE 便宜 4 倍**；
> - **质量方向**：SISNR 上 TRA `+0.38` > SFE `+0.23`；PESQ 上 `+0.04` > `+0.03` ⇒ TRA 略优。
>
> **⇒ 只有把"MACs 与参数"两条轴都画出来，"哪个模块更划算"才有确定答案**：若你的预算是 **MACs**（端侧逐帧算力），选 TRA；若你的预算是**参数/存储**（如 ROM 受限），**选 SFE**。
>
> **论文的措辞回避了这一组对照**：它只写 `our proposed TRA outperforms TA with a very limited increment in computational resources`（**只与 TA 比**）与 `The advantages of SFE are also evident in Table 1`（**未给量化**）。**这是本页从渲染图重算后补上的一组数。**

> [!note] 这条命题与库内的"算力不是速度"是**同一逻辑的第三次出现**
> | 页 | 被拆开的两个轴 | 结论 |
> |---|---|---|
> | [[wiki_low_latency/concepts/2509.21867-speed-optimized-streaming-design]] | **MACs vs RTF** | MACs 相同而 RTF 差 27 %（BN→LN） |
> | [[wiki_low_latency/concepts/2609.29867-compute-matched-dynamic-depth]] | **名义 MACs vs 真机 ms/frame** | 同 MACs 同参数量，1.001 vs 0.751 ms/frame |
> | **本页（GTCRN 的 Table 1）** | **MACs vs 参数** | TRA 的 MACs 便宜 9.2×、参数贵 4.1× |
>
> 三次的共同教训：**"代价"是一个向量，不是一个标量。**任何用单轴（无论是 MACs、参数还是 RTF）给出的"性价比"排序，都可能被另一轴反转。

> [!question] 但本条命题有一个**统计显著性上的软肋**
> Table 1 的 SISNR 差值是 `+0.38 / +0.23`，PESQ 差值是 `+0.04 / +0.03`——**在无种子、无方差、无置信区间的情况下，本库无法判断这些差值是否落在训练波动之内**。
> 并且：**两开关同时打开的 SISNR 增量 `+0.52` 小于单独之和 `+0.61`**（差 `0.09`），即存在**次可加性**（PESQ 上则不呈现）。
> 一个可能的原因（本页假设，未验证）：SFE 改变了 channel 的语义，TRA 的时序能量统计所依赖的分布随之改变。**论文未讨论，也未做交叉验证实验。**
> **结论**：双坐标的**方向**是可靠的（成本项是确定的会计数字），但**质量增益的量级**在无方差的情况下不宜过度解读。

## 命题 ④：引用 ShuffleNetV2 的架构论文，尤其应当报告速度

**事实**：GT-Conv 的 unit 直接来自 **ShuffleNetV2 [17]**（Ma 等，ECCV 2018）。而 ShuffleNetV2 正是本库两处反复引用的"**MACs 不是速度**"的原始出处：

- [[wiki_low_latency/concepts/2509.21867-speed-optimized-streaming-design]]（FastEnhancer）用它的结论论证"FLOPs 不能预测速度"；
- [[wiki_low_latency/concepts/2609.29867-compute-matched-dynamic-depth]]（Early Exit）用它在真机 int8 上再次显影（82–137 µs/MMAC，跨 1.7×）。

**而 GTCRN：全文无 RTF、无延迟、无目标硬件、无量化、无 p99——只有名义 MMACs（39.6 M/s）。**

> [!warning] **这是本库第一条"引用即负有义务"的审计规则**
> **规则形式**：
> > **凡在架构设计中引用 ShuffleNetV2（或等价的"MACs 不能预测速度"文献）的论文，本库要求它报告至少一项真实速度测量（RTF 或 ms/frame 或端到端延迟）；若无，则记为"引用即冲突"（citing-while-silent）。**
>
> **理由**：它引用的文献的核心贡献就是"FLOPs 是坏指标"。**引用了这个方法论，就承担了不能用名义 MACs 自证效率的义务。** GTCRN 只报 MACs 而不报速度，**在方法学上是自相矛盾的**——它不是"疏忽"，而是**引了自己反对的尺子当自己的尺子**。
>
> **并且这条冲突是"可被外部兑现"的**：[[wiki_low_latency/entities/FastEnhancer]] 用官方 checkpoint 测出 GTCRN 的 **RTF 0.060（Xeon）/ 0.042（M1）**，对照 FastEnhancer-B 的 **0.022**——**GTCRN 的 MACs 高约 6.5 倍（口外口径），而 RTF 高约 2.7 倍**（这个方向与"MACs 更差"一致，但倍数不同）。**GTCRN 原文没有任何数据可以回应。**

> [!note] 这条规则可以立刻应用到库内其他条目上——但必须先分清"能不能测"
> | 论文 | 引用 ShuffleNetV2 / "MACs≠速度" | 是否报速度 | 本库判定 |
> |---|---|---|---|
> | **GTCRN** | ✓ 直接用作 GT-Conv 的 unit | **✗** | **引用即冲突** |
> | [[wiki_low_latency/entities/FastEnhancer]] | ✓（其中的 BN vs LN 论证） | ✓ RTF（单线程 CPU） | 合规（但无 p99） |
> | [[wiki_low_latency/entities/Early-Exit-Conv-FSENet]] | —— | ✓ 真机 int8 ms/frame | 合规（库内最高档） |
> | [[wiki_low_latency/entities/D-GRU]] | —— | **✗**（只有解析 MACs） | **无速度**（L0） |
>
> **注意区分**：**"没有速度"与"引用了反对名义 MACs 的文献却没有速度"是两种不同的缺陷**。后者更严重，因为它是一个**逻辑上自指的漏洞**。

## 命题 ⑤：声明级因果需要一张七项清单来定位"缺口在哪一项"

GTCRN 关于因果性的**全部**表述（p.2 §2.2 逐字）：

> 「We use **grouped bidirectional GRU for intra-frame modeling**, and **grouped unidirectional GRU for inter-frame modeling**, **so that the causality of the model can be guaranteed**.」

**这是全文唯一一处提 causality。** 这句话**在结构上是合理的**——intra-frame 的双向是**单帧内、沿频率轴**的双向，不跨时间帧，因此不引入未来信息：

~~~text
   时间轴 t ──────────────────────────────────────────►
   ┌────────────┬────────────┬────────────┬────────────┐
   │   帧 t-1    │    帧 t     │   帧 t+1    │   帧 t+2    │
   └────────────┴────────────┴────────────┴────────────┘
                     ▲
                     │
        ┌────────────┴────────────┐
        │   帧 t 内部（频率轴）     │
        │   f=0 ─────────────────► │  intra-frame 双向
        │   f=0 ◄───────────────── │  （同一帧内，不跨时间）
        └─────────────────────────┘
   inter-frame：沿时间轴【单向】 ⇒ 只看 t, t-1, t-2 ...  ✅ 因果

   但【卷积 padding】与【STFT center】是否引入未来样本？
        → 论文完全沉默  ❌
~~~

**问题在于这句话覆盖的范围**。本库的因果性审计需要七项（外加 accelerator launch 共八项，依 [[wiki_low_latency/concepts/2609.29867-compute-matched-dynamic-depth]]）：

| # | 审计项 | GTCRN 的状态 | 影响 |
|---|---|---|---|
| 1 | 采样率 | 16 kHz（§3.1） | 明确 |
| 2 | 窗长 / hop / FFT | **32 ms / 16 ms / 512**（§3.2） | 明确 |
| 3 | **STFT center / 帧锚定** | **未报告** | **决定性**：若 `center=True` 则前端含 **16 ms 未来样本** |
| 4 | **inter-frame 循环方向** | **单向 GRU**（论文明确） | **正向**——★ **这是那句话唯一覆盖的一项** |
| 5 | **intra-frame 循环方向** | **双向 GRU**（论文明确） | **本页判定不破坏因果**——单帧内、沿频率轴 |
| 6 | **卷积层 padding** | **未报告**（全部 Conv / DeConv / P-Conv2D / DD-Conv2D） | **决定性**：`same` padding 常含未来帧 |
| 7 | **时间轴感受野与缓存需求** | **未给**；本页推得 DD-Conv2D **3 / 5 / 11 帧**，单链累计 **17 帧** | 若为因果卷积，需缓存 $(k-1)d$ 帧（**2 / 4 / 10 帧**） |
| 8 | accelerator launch / 图的段数 | **不适用**（无任何硬件或部署讨论） | 本库新增第 8 项，本篇**完全空白** |

> [!important] **本页的核心读法：`so that the causality ... can be guaranteed` 这句话的实际覆盖范围是 7 项中的第 4 项——1/7**
> 这不是说论文的声明是错的（第 4 项**确实**成立，且**理由合理**）；而是说：**一声明 ≠ 一认证**。
> **本库判定：`paper-claimed-causal`。既不能升级为 `strict_causal`（#3 / #6 是硬缺口），也不能判为 `non_causal`（#4 是真实的结构保证）。**
>
> **与库内两端的对照**：
> | 论文 | 本库判定 | 它的"额外保证" |
> |---|---|---|
> | [[wiki_low_latency/entities/LaCo-SENet]] | `strict_causal` 方向 | **逐层 padding 分配式**（本库最严尺子） |
> | [[wiki_low_latency/entities/Early-Exit-Conv-FSENet]] | `paper-claimed-causal` + 附加 | **"跳过即不更新状态"的结构性保证**（比"我们用了因果卷积"强） |
> | **GTCRN** | **`paper-claimed-causal`** | **无附加保证**（只有 #4 一项） |

> [!question] 一个可以立刻做的、低成本的改进：**"声明覆盖率"作为一个可记录的量**
> 本页建议本库对每一篇 `paper-claimed-causal` 的论文，**记录它的声明覆盖了八项审计中的哪几项**（例如 GTCRN = {#4}）。
> **理由**：这样"声明级因果"就不是一个二值标签，而是一个**可比较的覆盖度**。两篇都记 `paper-claimed-causal` 的论文，其证据强度可能相差很多——**GTCRN（{#4}）与 Early-Exit Conv-FSENet（{#4 类似的声明} + 跳过状态的结构性保证）不在同一档**。
> **这个字段的取值方式**：列出被声明覆盖的审计项编号 + 明示"其余为未报告"。

> [!note] 与本库"低时延前端"议题的关系：GTCRN 缺的正是那个议题的全部字段
> [[wiki_low_latency/concepts/低时延前端与延迟账本]] 要求的最小账本是：窗长 / hop / **center** / look-ahead / group delay / 算法延迟口径。**GTCRN 只有前三项中的前两项**（窗长、hop），**center 及之后的全部未报告**。
> **因此它的延迟下界只能从 hop 推**：**≈ 16 ms**（`center=False`）或 **≈ 32 ms**（`center=True`，需加 $W/2 = 16$ ms）。
> **这正是本页认为最该传给本库的一条判断纪律**：因为 `center` 未报告，**本库既不能判定它 ≥ 16 ms，也不能排除某些实现变体落入更低档**——能确定的只有"hop 是 16 ms ⇒ 帧率 62.5 Hz"。**这是"证据不足，双向都不能判定"，而不是"已判定为高延迟"。**

**补充证据（库内已有）：该架构确实可被重配到 4 ms**

[[wiki_low_latency/sources/2026/RT-Tango 2026]] 把分布式 GTCRN 在两种帧率下各测一次（其 Table 1）：

| 配置 | hop | DNN MACs (MMAC/s) | SI-SDR（左/右） | PESQ（左/右） |
|---|---:|---:|---|---|
| GTCRN | **16 ms** | **48.98** | 5.6 / 3.7 | 1.47 / 1.34 |
| GTCRN | **4 ms** | **197.5** | 6.0 / 4.0 | 1.52 / 1.36 |

- 算力比 $197.5/48.98 = 4.03$，帧率比 $250/62.5 = 4.0$ ⇒ **算力几乎正比于帧率（逐帧计算、无跨帧复用）**；
- 质量反而略升（SI-SDR 5.6→6.0，PESQ 1.47→1.52）；
- **口径提醒**：这是"每节点分布式 GTCRN"（4 麦输入、mask 作用于本地参考通道），**与原文 39.6 MMACs/s 不可直接相减**（差 1.24×）；
- **线性外推（本页推，RT-Tango 未测 2 ms）**：拉到 2 ms hop 需约 **395 MMAC/s** —— **已超出"超轻量"范畴，会以牺牲其唯一卖点为代价。**

## 附加命题：人声保留的账本——**BAK 涨而 SIG 不涨**是需要报告 trade-off 的情形

**事实（Table 3，DNS3 blind test set）**：

| 模型 | P.808 | BAK | **SIG** | OVRL |
|---|---|---|---|---|
| Noisy | 2.96 | 2.65 | **3.20** | 2.33 |
| RNNoise<sup>1</sup> | 3.15 | 3.45 | **3.00** | 2.53 |
| S-DCCRN | 3.43 | — | — | — |
| **GTCRN** | **3.44** | **3.90** | **3.00** | **2.70** |

> [!warning] **GTCRN 的收益完全来自 BAK（+0.45 vs RNNoise）与 OVRL（+0.17），SIG 上没有任何提升**
> - GTCRN **SIG = 3.00**，RNNoise **SIG = 3.00**——**完全相同**；
> - 且**两者都低于 Noisy 的 3.20** ⇒ **两个增强器都使语音保真低于未处理信号**（DNSMOS 评测里的常见现象：增强引入失真），**论文未提**；
> - 按本库 [[wiki_low_latency/concepts/低 SNR 人声保留评估]] 的规则——「**不能把 BAK 提升而 SIG/可懂度下降描述为无条件改进；需要报告 SIG–BAK trade-off 和失败案例**」——**GTCRN 恰好落在需要报告这个 trade-off 的情形上，但它只写了 `our model outperforms RNNoise by a wide margin`。**

**命题形式**：

> **一个增强器的 DNSMOS 剖面必须逐项读，不能读总分。BAK 涨而 SIG 不动，说明它买到的是"更安静"，不是"更清楚"。**

**与之配套的评测完整性缺口（GTCRN 全部未报告）**：ASR WER、主观 MOS/MUSHRA、负 SNR 分层（−10/−5/0/5 dB）、噪声类型分层（babble / 竞争说话人 / 瞬态）、false-suppression、SPP/VAD 校准、F0/formant/prosody、voiced energy、混响指标（C50/SRMR/DRR；**尽管 DNS3 训练含 RIR 与"保留前 100 ms 反射"的设置**）。

> [!note] 有意思的对照：**这两项恰恰是别人替它补上的**
> [[wiki_low_latency/entities/FastEnhancer]] 用官方 checkpoint 测出 GTCRN 的 **WER 3.6**（有 WER）与 **RTF**（有速度）——**GTCRN 原文两项皆无**。
> 这是一个在本库反复出现的模式：**"锚点自己不给的字段，往往由引用它的人补上"**。因此**库内对锚点的评估，实际上常常建立在第三方复现之上**——这使命题 ① 的口径纪律更加必要。

## 与库内已有条目的关系

### 与 [[wiki_low_latency/concepts/2304.08707-full-sub-band-modeling]]（子带路线）的关系

GTCRN 的 BM/BS 是**"部分子带"**路线：**只在 2 kHz 以上**做 ERB 压缩、低频 65 带原样保留。这与"全子带建模"（每个子带一个独立处理流）是两种不同强度的方案。

**本库已有的三方批评须并读**：

| 批评者 | 批评的维度 | 具体说法 | GTCRN 是否有数据回应 |
|---|---|---|---|
| [[wiki_low_latency/entities/FastEnhancer]] | **RTF** | 子带方案（BSRNN / FSPEN / **GTCRN** / LiSenNet）「increased architectural complexity and memory operations **paradoxically led to higher RTFs**」；GTCRN RTF **0.060** vs FastEnhancer-B **0.022** | **✗ 无 RTF** |
| [[wiki_low_latency/entities/PSMSE]] | **容量** | 超轻量路线「**performance tends to degrade due to the limited capacity of their simplified designs**」 | **✗ 无容量分析** |
| [[wiki_low_latency/entities/LiSenNet]] | **RTF（反证）** | 同为子带方案、同为超轻量档（37k），自报 **RTF 0.028（Xeon E5-2620 v4）**——**低于同表所有非子带基线**（CRN 0.042 / DCCRN 0.184 / FullSubNet 0.386） | **⚠️ 对本路线的批评构成反证**（但硬件不同，见 source 页） |
| GTCRN 自己 | **参数量 / MACs** | 23.7 K / 39.6 M/s（表内最小） | **✓** |

> [!important] 2026-09-27 补摄 LiSenNet 后，这条批评链出现了**第一个反证**
> FastEnhancer §2.2 把 BSRNN / FSPEN / GTCRN / **LiSenNet** 四者一并批评为"RTF 反而更高"。
> 但补摄 [[wiki_low_latency/sources/2024/LiSenNet 2024]] 后可见：**LiSenNet 自报 RTF 0.028**，而 FastEnhancer 自己在 Xeon Gold 6248R 上测其可流式版本 ^c 得 **0.034**——**两者同量级，且都低于同表的非子带基线**。
> ⇒ **"子带 ⇒ RTF 更高"不是一条普适规律**：FastEnhancer 的批评对 **GTCRN**（无 RTF 数据，无法反驳）成立程度不明，对 **LiSenNet** 则**不成立**。
> **这条批评必须按模型逐个验证，不能按路线整批引用。** 详见 [[wiki_low_latency/sources/2024/LiSenNet 2024]] §4.3 与 §6。

> [!note] 这三方合起来给出的图景是：**子带路线在参数与 MACs 上赢，在 RTF 与容量上被质疑。**
> GTCRN 原文**只报告了它赢的那一轴**。这不是造假——4 页短文没有空间——但**本库引用它时不能只引用"23.7 K / PESQ 2.87"，还必须同时记住另外两轴是无回应的**。
> 值得注意的是 **ERB 压缩本身被 [[wiki_low_latency/entities/RT-Tango]] 借走并成功用于双耳场景**——说明"部分子带压缩"这个算子本身是可用的，被批评的是"整个架构的复杂度与 RTF"。

### 与 [[wiki_low_latency/entities/D-GRU]] 的关系（"分组"的两端）

| 维度 | **GTCRN（G-DPRNN）** | **D-GRU** |
|---|---|---|
| 分组的粒度 | **结构化、通道划分**（组数 = 2，固定） | **非结构化、神经元级**（按比例 $P$ 选择） |
| 是否动态 | **静态**（训练后固定） | **动态**（随输入变化） |
| 目的 | **降参数量与 MACs** | **降每步算力** |
| 报告的算力证据 | **名义 MMACs（L0）** | **解析 MACs（L0）** |
| 报告的延迟 | **无** | **无** |

**共同缺口**：**两者都不报告实际延迟。**它们在"分组"这个思路的两端，但**都没有兑现"更省算力 ⇒ 更快"这一步**。这正是 [[wiki_low_latency/concepts/2509.21867-speed-optimized-streaming-design]] 与 [[wiki_low_latency/concepts/2609.29867-compute-matched-dynamic-depth]] 反复显影的那条裂缝。

### 与 [[wiki_low_latency/entities/DPCRN]] / [[wiki_low_latency/entities/Skip-DPCRN]] 的关系（谱系）

GTCRN 明确声明 backbone 是 **DPCRN [3, 16]**，而 **[16] 就是 Inference Skipping（本库 [[wiki_low_latency/entities/Skip-DPCRN]]）**——**两者共享作者 J. Lu**，同属一个课题组的连续工作：

~~~text
   DPCRN (Interspeech 2021)  ──►  Inference Skipping (TASLP 2022)  ──►  GTCRN (ICASSP 2024)
   [3] 双路径卷积循环            [16] 推理期跳过并行 RNN              超轻量分组 DPRNN
   本库 concept 2107.05429      本库 entities/Skip-DPCRN            本库 entities/GTCRN
                                        │                                   │
                                   "跳过省算力"                        "分组省算力"
                                        │                                   │
                                        └────── 共同缺口：都不报真机延迟 ──────┘
~~~

> [!question] 但 GTCRN **没有给出 DPCRN 本身的参数量或 MACs**（Table 2 里没有 DPCRN 行）
> 因此**"压了多少倍"在本篇内不可算**。本库能拿到的间接参照只有 Table 2 的 **S-DCCRN（2.34 M）**，但 S-DCCRN 是 **DCCRN 的扩展（引 [28]）**，**不是 DPCRN**，不能当算力代理。
> 本页记录为**未报告**，不代填。**这是"锚点"的又一处口径空白**（见命题 ①）。

## 对本库的改进建议

### 建议 1：为"锚点模型"建一张**口径表**（命题 ①）

对库内被 ≥ 3 篇引用的模型（GTCRN 是第一个），建立一个字段：**"论文声称值 / 官方实现实测值 / 第三方复现值 / 重配口径"四列**。**理由**：锚点的数值是整条引用链的地基。

### 建议 2：把"**分轴归因**"作为超轻量类论文的**入库必填项**（命题 ②）

要求标出每个压缩手段作用于哪条轴（频带维 / channel 维 / 循环层 / 补偿模块），并分别给出参数量与 MACs 的增量。**理由**：只有分轴记账，某个想法才能被独立搬走（RT-Tango 借 ERB 即是例证）。

### 建议 3：把"**双坐标性价比**"写进消融表的读法（命题 ③）

对消融中"加了模块 X"的结论，**至少同时报 MACs 增量与参数增量**；两者方向相反时**必须并列陈述**，不得只报其中之一。**理由**：GTCRN 的 TRA vs SFE 是标准反例（MACs 差 9.2×、参数反向差 4.1×）。

### 建议 4：新增审计规则"**引用即负有义务**"（命题 ④）

> **凡引用 ShuffleNetV2（或等价"MACs≠速度"文献）的论文，若无任何真实速度测量，记为 `citing-while-silent`。**

**理由**：这是逻辑自指型缺陷，比"单纯缺速度"更严重。**可直接应用于库内已收录条目**（见命题 ④ 表）。

### 建议 5：**"声明覆盖率"作为 `paper-claimed-causal` 的量化字段**（命题 ⑤）

记录该论文的因果性声明**覆盖了八项审计中的哪几项**（GTCRN = {#4}）。**理由**：把二值标签变成可比较的覆盖度，避免"两篇都是声明级"被误读为同一证据强度。

### 建议 6：**DNSMOS 剖面必须逐项读**（附加命题）

对凡报告 DNSMOS P.835 的论文，**强制同时列 BAK 与 SIG**，并在 **BAK 上升而 SIG 未上升**时要求给出 trade-off 讨论与失败案例。**理由**：GTCRN 的 SIG = 3.00 = RNNoise，且两者都低于 Noisy 的 3.20——这个事实**在只看 OVRL 时会被完全掩盖**（OVRL 2.70 vs 2.53 看起来是全面领先）。

## 时延账本与迁移边界

| 项目 | 本篇证据 | 本 Wiki 判定 |
|---|---|---|
| 采样率 / 窗长 / hop / FFT | **16 kHz**；**sqrt-Hanning 窗 32 ms**；**hop 16 ms**；**FFT 512** | 明确（ms 换算与采样点数为本页推得） |
| 频率点数 | **未直接报告**；本页推得 **257 = 512/2+1** | 推读 |
| **STFT center / 帧锚定** | **未报告** | **`unreported`：一等缺口**——若 `center=True` 则前端含 16 ms 未来样本 |
| 逐层 padding certificate | **未给** | **`unreported`（决定性）** |
| 时间感受野 | **未给**；本页推得 DD-Conv2D **3 / 5 / 11 帧**、单链累计 **17 帧** | 推读；方向性亦未说明 |
| 隐层状态跨帧传递 / DPRNN chunk 长度 | **未报告** | 流式部署前提缺失 |
| 因果性 | 「grouped unidirectional GRU for inter-frame ... so that the causality ... can be guaranteed」——**全文唯一一句** | **`paper-claimed-causal`，声明覆盖 {#4} / 7 项** |
| 算法延迟（论文口径） | **未报告**——论文没有这个概念 | `unreported` |
| 算法延迟下界（本页推） | **≈ 16 ms**（`center=False`）；**≈ 32 ms**（`center=True`） | 推读；**双向都不能判定** |
| **RTF / 执行时间 / p50 / p95 / p99** | **全部未报告** | 未验证 |
| **目标硬件 / 量化 / 功耗 / 内存 / 端侧实测** | **全部未报告** | 未验证 |
| 算力证据等级 | **只有名义 MMACs（39.6 M/s）** | **L0（本库最低级）** |
| 库外可得的速度/可懂度 | [[wiki_low_latency/entities/FastEnhancer]] 测出 **RTF 0.060 / 0.042**、**WER 3.6** | **第三方复现，非自报** |
| 4 ms 重配 | [[wiki_low_latency/entities/RT-Tango]]：**48.98 → 197.5 MMAC/s**（4.03×，帧率比 4.0×） | 分布式口径，**不可与 39.6 直接相减** |
| 人声保留 | 只有 **SISNR / PESQ / STOI** + **DNSMOS**（P.808 完整、P.835 仅 2 个模型全） | **SIG 与 RNNoise 相同、低于 Noisy；无 WER / 无主观 MOS / 无分层 / 无 false-suppression / 无 F0** |

**可迁移的部分**：

1. **ERB 频带压缩（2 kHz 以上、192 → 64）这个算子**——已被 [[wiki_low_latency/entities/RT-Tango]] 成功搬到双耳分布式场景，**是本篇最具生命力的部分**；
2. **"分组是三条正交轴"这一分析框架**（频带 / 通道 / 循环层）可直接用于任何"用分组降算力"的架构；
3. **TRA 的"能量 → 池化 → GRU → FC → sigmoid → 乘性掩蔽"结构**（与 SE-Block 同构但**多一个 GRU**）可迁移到任何需要"跨帧有记忆的通道重标定"的位置；
4. **"双坐标比较补偿模块"的读法**可直接复用于任何消融表；
5. **"引用即负有义务"的审计规则**可直接应用于库内全部条目。

**不可迁移 / 需要先解决的部分**：

1. **"23.7 K / 39.6"这个锚点数值不宜继续单方面引用**——库内三方口径不一致（48 K / 33 无法调和），需要先核查官方实现（命题 ①）；
2. **低时延结论完全不可迁移**——本篇**没有任何延迟数据**，连 `center` 都未报告；GTCRN 的算法延迟下界**只能双向不确定地记为"≈16 或 ≈32 ms"**；
3. **"性能对比"不宜作为子带路线的胜利证据**——Table 2 有 4 处空格、Table 3 有 6 处空格、RNNoise 数字口径不同且脚注只挂在 Table 3、**STOI 不是表内最高（0.940 < DeepFilterNet 0.942）**；
4. **Table 1 的消融数字不可与 Table 2/3 横比**——Table 1 用的是 **DNS3 的约 100 小时子集**；
5. **Fig. 5 只有两个困难样本，且 PESQ（1.42 / 1.94）远低于 Table 2 的平均 2.87**，**不能引用 Fig. 5 做任何定量论证**（它只能说明"GTCRN 在这两条样本上谐波结构比 RNNoise 清晰"）——论文未说明这两个样本的挑选标准；
6. **0.01 量级的结论不可采信**（P.808 3.43 → 3.44 的 `surpasses`、PESQ 1.89 → 1.91、两开关次可加性的 0.09 SISNR）——**无种子、无方差**。

## 关联页面

- 源论文：[[wiki_low_latency/sources/2024/GTCRN 2024]]
- 实体页：[[wiki_low_latency/entities/GTCRN]]
- 前身谱系：[[wiki_low_latency/entities/DPCRN]]、[[wiki_low_latency/concepts/2107.05429-dual-path-recurrent-context]]、[[wiki_low_latency/entities/Skip-DPCRN]]、[[wiki_low_latency/concepts/2207.11108-inference-skipping-parallel-rnn]]
- 引用 GTCRN 的四篇：[[wiki_low_latency/entities/FastEnhancer]]、[[wiki_low_latency/entities/RT-Tango]]、[[wiki_low_latency/entities/PSMSE]]、[[wiki/sources/2026/muNet 2026]]
- 同命题不同机理（MACs ≠ 速度）：[[wiki_low_latency/concepts/2509.21867-speed-optimized-streaming-design]]、[[wiki_low_latency/concepts/2609.29867-compute-matched-dynamic-depth]]
- 分组思路另一端：[[wiki_low_latency/entities/D-GRU]]、[[wiki_low_latency/concepts/2408.12425-dynamic-gated-rnn]]
- 子带路线：[[wiki_low_latency/concepts/2304.08707-full-sub-band-modeling]]
- 因果与延迟口径：[[wiki_low_latency/concepts/严格因果与算法延迟]]、[[wiki_low_latency/concepts/低时延前端与延迟账本]]、[[wiki_low_latency/entities/LaCo-SENet]]、[[wiki_low_latency/entities/Early-Exit-Conv-FSENet]]
- 人声保留缺口：[[wiki_low_latency/concepts/低 SNR 人声保留评估]]

> [!question] 当前缺口
> 本页的五条命题都**成立且可复用**，但它们各自的**验证都依赖同一件本页做不到的事**：
> ① **官方实现到底是多少参数**？（命题 ①）——48 K / 33 与 23.7 K / 39.6 差 2 倍，**必须核查 `https://github.com/Xiaobin-Rong/gtcrn`**；
> ② **`center` 是 True 还是 False**？（命题 ⑤）——决定算法延迟下界是 16 ms 还是 32 ms；
> ③ **DD-Conv2D 用的是 `same` 还是 `causal` padding**？——决定 17 帧感受野里有多少是 look-ahead；
> ④ **SFE 后的通道数是多少**？——决定"把子带关系搬进 channel 维"的代价是否真的只有 +2.02 K；
> ⑤ **在 16 ms hop 下，GTCRN 的真机 ms/frame 是多少**？——[[wiki_low_latency/entities/FastEnhancer]] 给的 RTF 是**吞吐量纲**，不是延迟量纲；把 GTCRN 放到 [[wiki_low_latency/concepts/2609.29867-compute-matched-dynamic-depth]] 的 STM32N6 上量一次 ms/frame（**含与不含 host 侧 STFT**各一次），是本库可以独立完成、且**能直接给"超轻量锚点"补上 L3q 证据**的实验；
> ⑥ **把它当作 backbone 的第一次组合实验还没有人做**：GTCRN + [[wiki_low_latency/entities/LaCo-SENet]] 式的因果 padding 分配式 + [[wiki_low_latency/concepts/2204.09911-short-asymmetric-stft]] 的短窗非对称 STFT —— 这是本库记录过但**尚未被实现的组合**。
